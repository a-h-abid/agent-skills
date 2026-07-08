from __future__ import annotations

import importlib.util
import io
import json
import socket
import unittest
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "abd-jira-cloud" / "scripts" / "jira.py"
SPEC = importlib.util.spec_from_file_location("abd_jira_cloud_jira", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
jira = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(jira)


class ConfigurationTests(unittest.TestCase):
    def test_accepts_and_canonicalizes_jira_cloud_base_url(self) -> None:
        self.assertEqual(
            jira.validate_base_url("https://Example.atlassian.net/"),
            "https://example.atlassian.net",
        )
        self.assertEqual(
            jira.validate_base_url("https://example.atlassian.net:443"),
            "https://example.atlassian.net",
        )

    def test_rejects_unsafe_base_urls(self) -> None:
        values = (
            "http://example.atlassian.net",
            "https://atlassian.net",
            "https://.atlassian.net",
            "https://foo..atlassian.net",
            "https://example.atlassian.net.evil.test",
            "https://user:token@example.atlassian.net",
            "https://example.atlassian.net/jira",
            "https://example.atlassian.net?x=1",
            "https://example.atlassian.net#fragment",
            "https://example.atlassian.net:8443",
        )
        for value in values:
            with self.subTest(value=value), self.assertRaises(jira.JiraError):
                jira.validate_base_url(value)

    def test_live_config_requires_all_values_but_dry_run_only_needs_url(self) -> None:
        dry = jira.Config({"JIRA_BASE_URL": "https://example.atlassian.net"})
        dry.require(live=False)
        with self.assertRaisesRegex(jira.JiraError, "JIRA_EMAIL, JIRA_API_TOKEN"):
            dry.require(live=True)

    def test_path_values_are_encoded_as_one_segment(self) -> None:
        self.assertEqual(jira.path_segment("ABC/1?x=2", "issue"), "ABC%2F1%3Fx%3D2")
        self.assertEqual(jira.issue_path("ABC/1"), "/rest/api/3/issue/ABC%2F1")
        with self.assertRaises(jira.JiraError):
            jira.path_segment("bad\nkey", "issue")

    def test_transition_dry_run_rejects_invalid_base_url_before_emitting_preview(self) -> None:
        cfg = jira.Config(
            {
                "JIRA_BASE_URL": "https://.atlassian.net",
                "JIRA_EMAIL": "user@example.com",
                "JIRA_API_TOKEN": "token",
            }
        )
        args = SimpleNamespace(
            key="ABC-1",
            to="Done",
            id=None,
            resolution=None,
            comment=None,
            dry_run=True,
        )
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            with self.assertRaisesRegex(
                jira.JiraError, r"JIRA_BASE_URL must be an HTTPS \*\.atlassian\.net"
            ):
                jira.cmd_transition(args, cfg)
        self.assertEqual(stdout.getvalue(), "")


class FieldParsingTests(unittest.TestCase):
    def test_parses_json_and_plain_string_values(self) -> None:
        self.assertEqual(
            jira.parse_kv_json(['priority={"name":"High"}', "summary=Hello"]),
            {"priority": {"name": "High"}, "summary": "Hello"},
        )

    def test_rejects_missing_or_empty_field_names(self) -> None:
        for value in ("summary", "=value"):
            with self.subTest(value=value), self.assertRaises(jira.JiraError):
                jira.parse_kv_json([value])


class FakeResponse:
    def __init__(self, body=b"", status=200):
        self.body = body
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return self.body


class TransportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = jira.Config(
            {
                "JIRA_BASE_URL": "https://example.atlassian.net",
                "JIRA_EMAIL": "person@example.com",
                "JIRA_API_TOKEN": "SENTINEL_API_TOKEN",
            }
        )

    def test_dry_run_redacts_token_and_emits_one_json_value(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            result = jira.request("GET", "/rest/api/3/myself", self.cfg, dry_run=True)
        document = json.loads(output.getvalue())
        self.assertIsNone(result)
        self.assertEqual(document["headers"]["Authorization"], "Basic <redacted>")
        self.assertNotIn("SENTINEL_API_TOKEN", output.getvalue())

    def test_live_request_uses_timeout_and_parses_json(self) -> None:
        with mock.patch.object(
            jira.HTTP_OPENER, "open", return_value=FakeResponse(b'{"ok":true}')
        ) as opened:
            self.assertEqual(jira.request("GET", "/rest/api/3/myself", self.cfg), {"ok": True})
        self.assertEqual(opened.call_args.kwargs["timeout"], 30)

    def test_empty_success_returns_empty_object(self) -> None:
        with mock.patch.object(jira.HTTP_OPENER, "open", return_value=FakeResponse()):
            self.assertEqual(jira.request("PUT", "/rest/api/3/issue/ABC-1", self.cfg), {})

    def test_http_error_is_bounded_redacted_and_reports_retry_after(self) -> None:
        body = ("SENTINEL_API_TOKEN" + "x" * (jira.ERROR_BODY_LIMIT + 10)).encode()
        error = urllib.error.HTTPError(
            "https://example.atlassian.net/rest/api/3/search/jql",
            429,
            "Too Many Requests",
            {"Retry-After": "7"},
            io.BytesIO(body),
        )
        with mock.patch.object(jira.HTTP_OPENER, "open", side_effect=error):
            with self.assertRaises(jira.JiraError) as raised:
                jira.request("POST", "/rest/api/3/search/jql", self.cfg)
        message = str(raised.exception)
        self.assertIn("Retry-After: 7", message)
        self.assertIn("[truncated]", message)
        self.assertNotIn("SENTINEL_API_TOKEN", message)

    def test_timeout_and_malformed_json_become_jira_errors(self) -> None:
        for effect in (
            socket.timeout("slow"),
            urllib.error.URLError("dns failure"),
            FakeResponse(b"not-json"),
        ):
            with self.subTest(effect=type(effect).__name__):
                context = (
                    mock.patch.object(jira.HTTP_OPENER, "open", side_effect=effect)
                    if isinstance(effect, Exception)
                    else mock.patch.object(jira.HTTP_OPENER, "open", return_value=effect)
                )
                with context, self.assertRaises(jira.JiraError):
                    jira.request("GET", "/rest/api/3/myself", self.cfg)

    def test_redirect_policy_rejects_cross_origin_and_downgrade(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        for destination in (
            "https://evil.test/steal",
            "http://example.atlassian.net/steal",
        ):
            with self.subTest(destination=destination), self.assertRaises(jira.JiraError):
                handler.redirect_request(request, None, 302, "Found", {}, destination)

    def test_redirect_policy_allows_same_origin_https(self) -> None:
        handler = jira.SameOriginRedirectHandler()
        request = urllib.request.Request("https://example.atlassian.net/rest/api/3/myself")
        redirected = handler.redirect_request(
            request, None, 302, "Found", {}, "/rest/api/3/myself?moved=1"
        )
        self.assertEqual(
            redirected.full_url,
            "https://example.atlassian.net/rest/api/3/myself?moved=1",
        )


if __name__ == "__main__":
    unittest.main()
