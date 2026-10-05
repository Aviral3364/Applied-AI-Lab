# Changelog

All notable changes to skills in this repository.
Skill versions are recorded in each `SKILL.md` under `metadata.version`.

## production-ai-design-review

### 1.1.0 — 2026-10-05

#### Changed

- Restructured to the [Agent Skills specification](https://agentskills.io/specification) layout.
  The skill directory now ships runtime content only: `SKILL.md`, `scripts/`, `references/`, `assets/`, `agents/`.
- Moved the example report from `examples/` to `assets/example-review.json`.
- Moved tests to `tests/`, the human guide to `docs/`, and added evals under `evals/`.
- Clarified scope: production AI/LLM and agent systems, not general non-AI service architecture.
- Added `license`, `compatibility` and `metadata` frontmatter fields.
- Reflowed Markdown to one sentence per line (rendered output unchanged).

#### Validator (report schema v1)

> [!WARNING]
> These rules can reject reports that passed in 1.0.0.

- `finding.domain` and `coverage.domain` must be a risk-catalog ID or `custom:<name>`.
- `requires_mitigation` requires at least one `confirmed_defect` or `plausible_risk` finding.
- `requires_validation` and `insufficient_evidence` require a finding or a coverage entry marked `unknown`.
- Error messages name the record ID (or index when the ID is missing) for every collection.

#### Added

- Apache-2.0 license.
- Offline eval harness with three synthetic cases, including a restraint case that guards against fabricated findings.
- CI: Agent Skills conformance test, doc line-length lint, SHA-pinned actions, Dependabot, and a monthly source reachability check.

### 1.0.0 — 2026-10-05

- Initial public release.
