#!/usr/bin/env python3
"""Score an exported review JSON against an eval's structural expectations.

Offline, standard library only. Validates the review with the skill's own validator
first, then checks must-find recall, must-not-claim violations (fabrication guard),
maximum severity and verdict. It does not grade prose quality or factual accuracy.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SKILL = REPO / "skills" / "production-ai-design-review"
SEVERITY_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def load_validator():
    spec = importlib.util.spec_from_file_location("review_tools", SKILL / "scripts" / "review_tools.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_eval(eval_id, evals_path=HERE / "evals.json"):
    data = json.loads(Path(evals_path).read_text(encoding="utf-8"))
    for case in data["evals"]:
        if case["id"] == eval_id or case.get("name") == str(eval_id):
            return case
    raise ValueError(f"unknown eval {eval_id}")


def _matches(finding, rule):
    return all(finding.get(key) == value for key, value in rule.items())


def score(case, review, validator=None):
    """Return a result dict; result['passed'] is the overall outcome."""
    validator = validator or load_validator()
    grading = case["grading"]
    errors = validator.validate_report(review)
    result = {"eval": case["id"], "validation_errors": errors, "missed": [], "fabricated": [],
              "over_severity": [], "verdict_ok": None, "passed": False}
    if errors:
        return result
    findings = review["findings"]
    for rule in grading.get("must_find", []):
        minimum = SEVERITY_RANK[rule.get("min_severity", "unknown")]
        hit = any(f["domain"] == rule["domain"] and f["classification"] in rule["classification_in"]
                  and SEVERITY_RANK[f["severity"]] >= minimum for f in findings)
        if not hit:
            result["missed"].append(rule)
    for rule in grading.get("must_not_claim", []):
        result["fabricated"].extend(f["id"] for f in findings if _matches(f, rule))
    if "max_severity" in grading:
        ceiling = SEVERITY_RANK[grading["max_severity"]]
        result["over_severity"] = [f["id"] for f in findings if SEVERITY_RANK[f["severity"]] > ceiling]
    result["verdict_ok"] = review["verdict"] in grading.get("allowed_verdicts", [review["verdict"]])
    result["passed"] = not (result["missed"] or result["fabricated"] or result["over_severity"]) and result["verdict_ok"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eval_id", help="numeric id or name from evals.json")
    parser.add_argument("review", type=Path, help="review JSON exported by the skill")
    parser.add_argument("--evals", type=Path, default=HERE / "evals.json")
    args = parser.parse_args(argv)
    try:
        eval_id = int(args.eval_id) if args.eval_id.isdigit() else args.eval_id
        result = score(load_eval(eval_id, args.evals), json.loads(args.review.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
