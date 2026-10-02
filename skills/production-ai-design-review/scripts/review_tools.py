#!/usr/bin/env python3
"""Offline review helpers. Structural validation is not factual verification."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"confirmed_defect", "plausible_risk", "evidence_gap"}
SEVERITIES = {"critical", "high", "medium", "low", "unknown"}
VERDICTS = {"requires_mitigation", "requires_validation", "insufficient_evidence", "no_blocker_observed"}


def validate_report(report):
    """Return all structural errors, including linkage and evidence contradictions."""
    errors = []

    def fail(path, message):
        errors.append(f"{path}: {message}")

    def obj(value, path):
        if not isinstance(value, dict):
            fail(path, "must be an object")
            return {}
        return value

    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            fail(path, "must be a nonempty string")

    def texts(value, path, minimum=0):
        if not isinstance(value, list):
            fail(path, "must be an array")
            return []
        if len(value) < minimum:
            fail(path, f"needs at least {minimum} item(s)")
        for i, item in enumerate(value):
            text(item, f"{path}[{i}]")
        return [item for item in value if isinstance(item, str)]

    def enum(value, options, path):
        if not isinstance(value, str) or value not in options:
            fail(path, f"must be one of {', '.join(sorted(options))}")

    def records(key):
        value = report.get(key)
        if not isinstance(value, list):
            fail(key, "must be an array")
            return []
        return [obj(item, f"{key}[{i}]") for i, item in enumerate(value)]

    def indexed(items, key):
        result = {}
        for i, item in enumerate(items):
            ident = item.get("id")
            text(ident, f"{key}[{i}].id")
            if isinstance(ident, str) and ident.strip():
                if ident in result:
                    fail(key, f"duplicate ID {ident}")
                result[ident] = item
        return result

    def iso_date(value, path):
        try:
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError()
            parsed = date.fromisoformat(value)
            if parsed > date.today():
                fail(path, "cannot be in the future")
        except ValueError:
            fail(path, "must be an ISO date YYYY-MM-DD")

    if not isinstance(report, dict):
        return ["report: must be an object"]
    if type(report.get("schema_version")) is not int or report["schema_version"] != 1:
        fail("schema_version", "must be integer 1")
    for field in ("system", "scope", "summary"):
        text(report.get(field), field)
    iso_date(report.get("reviewed_at"), "reviewed_at")
    enum(report.get("verdict"), VERDICTS, "verdict")
    for field in ("assumptions", "limitations"):
        texts(report.get(field), field)
    artifacts = records("artifacts")
    sources = records("sources")
    findings = records("findings")
    actions = records("action_items")
    tests = records("tests")
    controls = records("validated_controls")
    coverage = records("coverage")
    groups = {key: indexed(items, key) for key, items in (
        ("artifacts", artifacts), ("sources", sources), ("findings", findings),
        ("action_items", actions), ("tests", tests), ("validated_controls", controls))}

    def links(value, target, path, minimum=0):
        refs = texts(value, path, minimum)
        for ref in refs:
            if ref not in groups[target]:
                fail(path, f"unknown {target} ID {ref}")
        return refs

    def evidence(value, path, minimum=0):
        if not isinstance(value, list):
            fail(path, "must be an array")
            return []
        if len(value) < minimum:
            fail(path, "needs direct artifact evidence")
        for i, entry in enumerate(value):
            entry = obj(entry, f"{path}[{i}]")
            links([entry.get("artifact_id")], "artifacts", f"{path}[{i}].artifact_id", 1)
            for field in ("location", "observation"):
                text(entry.get(field), f"{path}[{i}].{field}")
        return value

    for item in artifacts:
        for field in ("label", "version", "basis"):
            text(item.get(field), f"artifact.{field}")
    for item in sources:
        ident = item.get("id", "?")
        for field in ("publisher", "claim", "version"):
            text(item.get(field), f"source.{ident}.{field}")
        enum(item.get("status"), {"verified", "unverified"}, f"source.{ident}.status")
        enum(item.get("authority"), {"official_primary", "unverified"}, f"source.{ident}.authority")
        url = item.get("url")
        try:
            parts = urlsplit(url) if isinstance(url, str) else None
            if not parts or parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
                raise ValueError()
        except ValueError:
            fail(f"source.{ident}.url", "must be an HTTPS URL without embedded credentials")
        if item.get("status") == "verified":
            if item.get("authority") != "official_primary":
                fail(f"source.{ident}", "verified external evidence must be official_primary")
            iso_date(item.get("verified_at"), f"source.{ident}.verified_at")
        elif item.get("verified_at") is not None:
            fail(f"source.{ident}.verified_at", "must be null when unverified")

    for item in findings:
        ident = item.get("id", "?")
        kind = item.get("classification")
        enum(kind, KINDS, f"finding.{ident}.classification")
        enum(item.get("severity"), SEVERITIES, f"finding.{ident}.severity")
        enum(item.get("confidence"), {"low", "medium", "high"}, f"finding.{ident}.confidence")
        for field in ("title", "domain", "mechanism", "impact", "severity_rationale", "likelihood_rationale"):
            text(item.get(field), f"finding.{ident}.{field}")
        evidence(item.get("evidence"), f"finding.{ident}.evidence", 1 if kind == "confirmed_defect" else 0)
        assumptions = texts(item.get("assumptions"), f"finding.{ident}.assumptions")
        missing = texts(item.get("missing_evidence"), f"finding.{ident}.missing_evidence")
        if kind == "plausible_risk" and not assumptions:
            fail(f"finding.{ident}", "plausible risk requires explicit assumptions")
        if kind == "evidence_gap" and not missing:
            fail(f"finding.{ident}", "evidence gap must name missing evidence")
        refs = links(item.get("source_ids"), "sources", f"finding.{ident}.source_ids")
        if kind == "confirmed_defect":
            for ref in refs:
                if groups["sources"].get(ref, {}).get("status") != "verified":
                    fail(f"finding.{ident}", "confirmed external support must be verified")
        action_refs = links(item.get("action_ids"), "action_items", f"finding.{ident}.action_ids", 1)
        for ref in action_refs:
            linked = groups["action_items"].get(ref, {}).get("finding_ids", [])
            if not isinstance(linked, list) or ident not in linked:
                fail(f"finding.{ident}", f"action {ref} must link back to finding")

    for item in actions:
        ident = item.get("id", "?")
        enum(item.get("priority"), {"contain_now", "before_release", "scheduled", "investigate"}, f"action.{ident}.priority")
        enum(item.get("kind"), {"containment", "mitigation", "investigation"}, f"action.{ident}.kind")
        for field in ("owner_role", "component", "change", "rationale", "tradeoffs", "failure_behavior", "recovery", "residual_risk"):
            text(item.get(field), f"action.{ident}.{field}")
        refs = links(item.get("finding_ids"), "findings", f"action.{ident}.finding_ids", 1)
        links(item.get("source_ids"), "sources", f"action.{ident}.source_ids")
        links(item.get("depends_on"), "action_items", f"action.{ident}.depends_on")
        if isinstance(item.get("depends_on"), list) and ident in item["depends_on"]:
            fail(f"action.{ident}", "cannot depend on itself")
        test_refs = links(item.get("test_ids"), "tests", f"action.{ident}.test_ids", 1)
        for ref in refs:
            linked = groups["findings"].get(ref, {}).get("action_ids", [])
            if not isinstance(linked, list) or ident not in linked:
                fail(f"action.{ident}", f"finding {ref} must link back to action")
        for ref in test_refs:
            linked = groups["tests"].get(ref, {}).get("action_ids", [])
            if not isinstance(linked, list) or ident not in linked:
                fail(f"action.{ident}", f"test {ref} must link back to action")

    for item in tests:
        ident = item.get("id", "?")
        enum(item.get("status"), {"proposed", "passed", "failed", "not_run"}, f"test.{ident}.status")
        for field in ("setup", "stimulus", "expected", "collect"):
            text(item.get(field), f"test.{ident}.{field}")
        refs = links(item.get("action_ids"), "action_items", f"test.{ident}.action_ids", 1)
        evidence(item.get("result_evidence"), f"test.{ident}.result_evidence", 1 if item.get("status") in ("passed", "failed") else 0)
        if item.get("status") in ("proposed", "not_run") and item.get("result_evidence"):
            fail(f"test.{ident}", "unrun tests cannot have claimed result evidence")
        for ref in refs:
            linked = groups["action_items"].get(ref, {}).get("test_ids", [])
            if not isinstance(linked, list) or ident not in linked:
                fail(f"test.{ident}", f"action {ref} must link back to test")

    for item in controls:
        for field in ("description", "boundary"):
            text(item.get(field), f"control.{field}")
        enum(item.get("basis"), {"artifact_inspection", "test_observation", "production_observation"}, "control.basis")
        evidence(item.get("evidence"), "control.evidence", 1)
    seen_domains = set()
    for item in coverage:
        domain = item.get("domain")
        text(domain, "coverage.domain")
        enum(item.get("status"), {"reviewed", "unknown", "not_applicable"}, "coverage.status")
        text(item.get("reason"), "coverage.reason")
        if isinstance(domain, str):
            if domain in seen_domains:
                fail("coverage", f"duplicate domain {domain}")
            seen_domains.add(domain)
    if not coverage:
        fail("coverage", "must describe reviewed/unknown/excluded scope")
    remaining = {
        ident: {ref for ref in item.get("depends_on", []) if isinstance(ref, str) and ref in groups["action_items"]}
        for ident, item in groups["action_items"].items()
        if isinstance(item.get("depends_on"), list)
    }
    while remaining:
        ready = {ident for ident, refs in remaining.items() if not refs}
        if not ready:
            fail("action_items", "dependency cycle among " + ", ".join(sorted(remaining)))
            break
        remaining = {ident: refs - ready for ident, refs in remaining.items() if ident not in ready}
    if report.get("verdict") == "no_blocker_observed":
        if any(f.get("severity") in ("critical", "high") for f in findings):
            fail("verdict", "unresolved high/critical findings contradict no_blocker_observed")
    return errors


def render_report(report):
    """Render all report content as escaped Markdown after validation."""
    errors = validate_report(report)
    if errors:
        raise ValueError("\n".join(errors))

    def esc(value):
        result = str(value).replace("\r", " ").replace("\n", " ")
        for char in ("\\", "`", "*", "_", "[", "]", "<", ">", "|", "#"):
            result = result.replace(char, "\\" + char)
        return result

    lines = [f"# Production AI review: {esc(report['system'])}", "",
             f"**Verdict:** {esc(report['verdict'])}. **Reviewed:** {report['reviewed_at']}", "",
             esc(report["summary"]), "", f"**Scope:** {esc(report['scope'])}", ""]
    labels = {"findings": "Findings", "action_items": "Action plan", "tests": "Verification tests",
              "validated_controls": "Validated controls", "coverage": "Coverage", "artifacts": "Artifacts", "sources": "Sources"}

    def emit(value, indent=0):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, (list, dict)):
                    lines.append(" " * indent + f"- **{esc(key)}:**")
                    emit(child, indent + 2)
                else:
                    lines.append(" " * indent + f"- **{esc(key)}:** {esc(child)}")
        elif isinstance(value, list):
            if not value:
                lines.append(" " * indent + "- None recorded.")
            for child in value:
                if isinstance(child, dict):
                    lines.append(" " * indent + "- Record:")
                    emit(child, indent + 2)
                else:
                    lines.append(" " * indent + "- " + esc(child))

    for key in ("assumptions", "limitations", *labels):
        lines.extend(["## " + labels.get(key, key.title()), ""])
        emit(report[key])
        lines.append("")
    lines.extend(["Structural validation does not verify factual claims, publisher authority or system safety.", ""])
    return "\n".join(lines)


def select_domains(capabilities):
    catalog = json.loads((ROOT / "references/risk-catalog.json").read_text(encoding="utf-8"))
    selected = set(capabilities)
    unknown = selected - set(catalog["capabilities"])
    if unknown:
        raise ValueError("Unknown capabilities: " + ", ".join(sorted(unknown)))
    if selected & {"writes", "mcp", "code-execution", "multi-agent"}:
        selected.add("tools")
    return [d for d in catalog["domains"] if "always" in d["applies_to"] or selected.intersection(d["applies_to"])]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    question = sub.add_parser("questions", help="Print a capability-specific question bank; does not discover capabilities")
    question.add_argument("--capability", action="append", default=[])
    for name in ("validate", "render"):
        cmd = sub.add_parser(name)
        cmd.add_argument("report", type=Path)
        if name == "render":
            cmd.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "questions":
            print("Question bank only. Unknown capabilities require separate evidence review.\n")
            for domain in select_domains(args.capability):
                print(f"{domain['id']}: {domain['title']}")
                for question in domain["questions"]:
                    print("- " + question)
                print()
            return 0
        report = json.loads(args.report.read_text(encoding="utf-8"))
        errors = validate_report(report)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        if args.command == "render":
            content = render_report(report)
            with args.output.open("x", encoding="utf-8") as output:
                output.write(content)
            print(f"Wrote {args.output}")
        else:
            print("Structure and references valid; factual/source verification remains the reviewer's responsibility.")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
