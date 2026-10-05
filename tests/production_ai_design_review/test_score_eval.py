"""Eval definitions are well-formed and the offline scorer grades correctly."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "production-ai-design-review"
EVALS = REPO / "evals" / "production-ai-design-review"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scorer = _load("score_eval", EVALS / "score_eval.py")
tools = _load("review_tools_for_evals", SKILL / "scripts" / "review_tools.py")


class EvalDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((EVALS / "evals.json").read_text(encoding="utf-8"))
        self.domains = {d["id"] for d in tools.load_catalog()["domains"]}

    def test_skill_name_matches(self):
        self.assertEqual(SKILL.name, self.data["skill_name"])

    def test_ids_unique_and_files_exist(self):
        ids = [case["id"] for case in self.data["evals"]]
        self.assertEqual(len(ids), len(set(ids)))
        for case in self.data["evals"]:
            for name in case["files"]:
                self.assertTrue((EVALS / name).is_file(), name)

    def test_grading_uses_valid_vocabulary(self):
        for case in self.data["evals"]:
            grading = case["grading"]
            with self.subTest(eval=case["id"]):
                for rule in grading.get("must_find", []):
                    self.assertIn(rule["domain"], self.domains)
                    self.assertLessEqual(set(rule["classification_in"]), tools.KINDS)
                    self.assertIn(rule.get("min_severity", "unknown"), tools.SEVERITIES)
                for rule in grading.get("must_not_claim", []):
                    self.assertTrue(rule)
                    if "domain" in rule:
                        self.assertIn(rule["domain"], self.domains)
                    if "classification" in rule:
                        self.assertIn(rule["classification"], tools.KINDS)
                if "max_severity" in grading:
                    self.assertIn(grading["max_severity"], tools.SEVERITIES)
                self.assertTrue(grading["allowed_verdicts"])
                self.assertLessEqual(set(grading["allowed_verdicts"]), tools.VERDICTS)

    def test_restraint_case_exists(self):
        self.assertTrue(any(not c["grading"]["must_find"] and "max_severity" in c["grading"] for c in self.data["evals"]))


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((SKILL / "assets/example-review.json").read_text(encoding="utf-8"))

    def test_matching_review_passes(self):
        result = scorer.score(scorer.load_eval(1), self.review, tools)
        self.assertTrue(result["passed"], result)

    def test_fabricated_finding_and_verdict_fail_restraint_case(self):
        result = scorer.score(scorer.load_eval(3), self.review, tools)
        self.assertFalse(result["passed"])
        self.assertIn("F-01", result["fabricated"])
        self.assertFalse(result["verdict_ok"])

    def test_missing_expected_finding_fails(self):
        result = scorer.score(scorer.load_eval(2), self.review, tools)
        self.assertFalse(result["passed"])
        self.assertEqual({"guardrails", "authorization"}, {r["domain"] for r in result["missed"]})

    def test_under_severity_counts_as_missed(self):
        review = copy.deepcopy(self.review)
        retries = next(f for f in review["findings"] if f["domain"] == "retries")
        retries["severity"] = "low"
        result = scorer.score(scorer.load_eval(1), review, tools)
        self.assertEqual(["retries"], [r["domain"] for r in result["missed"]])

    def test_invalid_review_cannot_pass(self):
        review = copy.deepcopy(self.review)
        review["findings"][0]["domain"] = "invented"
        result = scorer.score(scorer.load_eval(1), review, tools)
        self.assertFalse(result["passed"])
        self.assertTrue(result["validation_errors"])

    def test_lookup_by_name(self):
        self.assertEqual(3, scorer.load_eval("well-controlled")["id"])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.json"
            path.write_text(json.dumps(self.review))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(0, scorer.main(["1", str(path)]))
                self.assertEqual(1, scorer.main(["3", str(path)]))
                self.assertEqual(2, scorer.main(["99", str(path)]))


if __name__ == "__main__":
    unittest.main()
