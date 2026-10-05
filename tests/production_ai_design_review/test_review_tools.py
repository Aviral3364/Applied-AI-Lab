"""Meaningful report integrity and CLI tests using a synthetic design, offline."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "skills" / "production-ai-design-review"
spec = importlib.util.spec_from_file_location("review_tools", ROOT / "scripts/review_tools.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((ROOT / "assets/example-review.json").read_text())

    def rejected(self, fragment):
        errors = tools.validate_report(self.report)
        self.assertTrue(any(fragment in message for message in errors), errors)

    def test_complete_example_is_valid(self):
        self.assertEqual([], tools.validate_report(self.report))

    def test_confirmed_defect_needs_direct_evidence(self):
        self.report["findings"][0]["evidence"] = []
        self.rejected("direct artifact evidence")

    def test_external_guidance_cannot_replace_system_evidence(self):
        self.report["artifacts"] = []
        self.rejected("unknown artifacts ID")

    def test_gap_must_name_missing_evidence(self):
        self.report["findings"][1]["missing_evidence"] = []
        self.rejected("must name missing evidence")

    def test_plausible_risk_requires_assumptions(self):
        self.report["findings"][0]["classification"] = "plausible_risk"
        self.rejected("requires explicit assumptions")

    def test_findings_require_action(self):
        self.report["findings"][0]["action_ids"] = []
        self.rejected("needs at least 1")

    def test_actions_require_verification(self):
        self.report["action_items"][0]["test_ids"] = []
        self.rejected("needs at least 1")

    def test_bidirectional_links_required(self):
        self.report["tests"][0]["action_ids"] = ["A-02"]
        self.rejected("must link back")

    def test_cannot_claim_unrun_test_passed(self):
        self.report["tests"][0]["status"] = "passed"
        self.rejected("direct artifact evidence")

    def test_unverified_source_not_confirmed_support(self):
        self.report["sources"][0].update(status="unverified", verified_at=None)
        self.rejected("confirmed external support must be verified")

    def test_verified_source_requires_official_authority(self):
        self.report["sources"][0]["authority"] = "unverified"
        self.rejected("must be official_primary")

    def test_credentials_in_source_urls_rejected(self):
        self.report["sources"][0]["url"] = "https://secret@example.com/docs"
        self.rejected("without embedded credentials")

    def test_duplicate_ids_rejected(self):
        self.report["findings"].append(copy.deepcopy(self.report["findings"][0]))
        self.rejected("duplicate ID")

    def test_unresolved_high_finding_contradicts_verdict(self):
        self.report["verdict"] = "no_blocker_observed"
        self.report["findings"][0]["severity"] = "high"
        self.rejected("contradict")

    def test_malformed_fields_return_errors_not_crash(self):
        for collection, field in (("findings", "classification"), ("findings", "severity"), ("tests", "status")):
            with self.subTest(collection=collection, field=field):
                malformed = copy.deepcopy(self.report)
                malformed[collection][0][field] = {"unexpected": True}
                self.assertTrue(tools.validate_report(malformed))

    def test_capability_selection_avoids_irrelevant_write_risks(self):
        read = {d["id"] for d in tools.select_domains(["retrieval"])}
        self.assertIn("retrieval", read)
        self.assertNotIn("retries", read)
        write = {d["id"] for d in tools.select_domains(["writes"])}
        self.assertTrue({"retries", "state", "tools"} <= write)
        self.assertNotIn("mcp", write)

    def test_unknown_capability_not_silently_ignored(self):
        with self.assertRaises(ValueError):
            tools.select_domains(["imaginary-capability"])

    def test_renderer_preserves_mitigation_and_residual_risk(self):
        content = tools.render_report(self.report)
        for action in self.report["action_items"]:
            self.assertIn(action["change"], content)
            self.assertIn(action["residual_risk"], content)
        self.assertIn("requires\\_mitigation", content)

    def test_renderer_escapes_untrusted_markup(self):
        self.report["summary"] = "<script>alert(1)</script> [click](https://example.org)"
        rendered = tools.render_report(self.report)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("[click]", rendered)

    def test_cli_renders_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "review.json"
            output = Path(directory) / "review.md"
            report.write_text(json.dumps(self.report))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(0, tools.main(["render", str(report), "--output", str(output)]))
                first = output.read_text()
                self.assertEqual(1, tools.main(["render", str(report), "--output", str(output)]))
            self.assertEqual(first, output.read_text())

    def test_invalid_report_does_not_write_output(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "review.json"
            output = Path(directory) / "review.md"
            report.write_text("[]")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(1, tools.main(["render", str(report), "--output", str(output)]))
            self.assertFalse(output.exists())

    def test_dependency_cycle_rejected(self):
        self.report["action_items"][0]["depends_on"] = ["A-02"]
        self.report["action_items"][1]["depends_on"] = ["A-01"]
        self.rejected("dependency cycle")

    def test_acyclic_dependencies_accepted(self):
        self.report["action_items"][0]["depends_on"] = ["A-02"]
        self.assertEqual([], tools.validate_report(self.report))

    def test_future_or_malformed_verification_date_rejected(self):
        self.report["sources"][0]["verified_at"] = "2999-01-01"
        self.rejected("cannot be in the future")
        self.report["sources"][0]["verified_at"] = "20261002"
        self.rejected("ISO date")

    def test_no_findings_is_not_automatic_failure(self):
        self.report.update(findings=[], action_items=[], tests=[], verdict="no_blocker_observed")
        self.assertEqual([], tools.validate_report(self.report))

    def test_catalog_source_ids_resolve_to_official_registry(self):
        catalog = json.loads((ROOT / "references/risk-catalog.json").read_text())
        policy = (ROOT / "references/source-policy.md").read_text()
        for domain in catalog["domains"]:
            for source in domain["source_ids"]:
                self.assertIn("| " + source + " |", policy)


if __name__ == "__main__":
    unittest.main()
