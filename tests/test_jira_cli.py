from __future__ import annotations

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
