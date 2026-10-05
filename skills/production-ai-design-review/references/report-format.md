# Structured report format (version 1)

Use UTF-8 JSON.
Scripts use Python 3.10+ without dependencies.
Field names/enums below are the public contract.
Unknown extra fields are retained by the renderer inside records; required fields must still be present.
Do not insert credentials, customer identifiers or raw sensitive context.

## Top level

- `schema_version`: integer `1`.
- `system`, `scope`, `summary`: nonempty strings. State review boundary and decision reasoning.
- `reviewed_at`: ISO calendar date, not future. Use the actual review date.
- `verdict`: `requires_mitigation`, `requires_validation`, `insufficient_evidence`, or `no_blocker_observed` (only within stated scope).
  The verdict must be consistent with the findings: `requires_mitigation` needs at least one `confirmed_defect` or `plausible_risk`;
  `requires_validation` and `insufficient_evidence` need at least one finding or a coverage entry marked `unknown`;
  `no_blocker_observed` cannot coexist with critical/high findings.
- `assumptions`, `limitations`: arrays of strings, empty when none.
- `artifacts`, `sources`, `findings`, `action_items`, `tests`, `validated_controls`, `coverage`: arrays of objects.
  Coverage must have at least one item; the other arrays may be empty for an appropriately scoped review.

## Records

IDs are nonempty unique strings within their record collection.
References must resolve and finding/action/test links must be bidirectional.
Use human-readable IDs such as F-01, A-01 and T-01.

**Artifact:** `id`, `label`, `version`, `basis` strings.
Version may explicitly be `not specified`.
Basis explains whether supplied design, inspected code, test output or observation.
An artifact describes evidence actually available, not a desired future document.

**Evidence entry:** `artifact_id`, `location`, `observation` strings.
Location may be a section or actual line identifier; do not invent line numbers.
Evidence is required for confirmed defects, validated controls, and claimed passed/failed tests.

**Source:** `id`, `publisher`, `url`, `claim`, `version`, `authority`, `status`, `verified_at`.
URL must be HTTPS without embedded credentials.
Authority is `official_primary` or `unverified`; status is `verified` or `unverified`.
Verified sources require official-primary authority and an actual ISO verification date.
Unverified sources use null `verified_at`; do not use them as confirmed support.
A verified flag is the reviewer's documented assertion, not a script's certification.
Source ownership and exact claim support require manual verification under source-policy.md.

**Finding:**

- `id`, `title`, `domain`, `mechanism`, `impact`, `severity_rationale`, `likelihood_rationale`: nonempty strings.
- `domain`: a domain `id` from [risk-catalog.json](risk-catalog.json), or `custom:<name>` for a system-specific concern outside the catalog.
- `classification`: `confirmed_defect`, `plausible_risk`, `evidence_gap`.
- `severity`: `critical`, `high`, `medium`, `low`, `unknown`.
- `confidence`: `low`, `medium`, `high`.
- `evidence`: evidence-entry array. Confirmed defects need at least one direct artifact.
- `assumptions`, `missing_evidence`: string arrays. Plausible risks need assumptions; gaps name missing evidence.
- `source_ids`: source references, empty when the claim is supported solely by system artifacts/explicit engineering reasoning.
- `action_ids`: at least one action reference.

**Action:**

- `id`, `owner_role`, `component`, `change`, `rationale`, `tradeoffs`, `failure_behavior`, `recovery`, `residual_risk`: nonempty strings.
  Recovery may explicitly explain why no state-changing recovery is applicable.
- `priority`: `contain_now`, `before_release`, `scheduled`, `investigate`.
- `kind`: `containment`, `mitigation`, `investigation`.
- `finding_ids`, `test_ids`: nonempty reference arrays.
- `source_ids`, `depends_on`: reference arrays, possibly empty. Dependencies must not be circular.

**Test:** `id`, `setup`, `stimulus`, `expected`, `collect` strings; `action_ids` nonempty references; `status` in `proposed`, `not_run`, `passed`, `failed`; `result_evidence` evidence-entry array.
Proposed/unrun tests have no result evidence.
A code file alone cannot support a claim that its tests passed.

**Validated control:** `id`, `description`, `boundary` strings; `basis` in `artifact_inspection`, `test_observation`, `production_observation`; nonempty `evidence` array.
Validation is limited to this evidence and boundary.

**Coverage:** `domain` (catalog ID or `custom:<name>`, unique), `reason` strings; `status` in `reviewed`, `unknown`, `not_applicable`.
Unknown is not equivalent to reviewed-safe; exclusions need capability-specific reasons.

## Usage

The synthetic [example](../assets/example-review.json) shows a complete report with a mitigation, investigation action and proposed tests.
It is an example of formatting, not a benchmark or universal architecture recommendation.

`validate` checks record structure/linkage, evidence requirements and some contradictory claims.
`render` performs the same check, escapes Markdown content and writes the report without overwriting.
Neither tool inspects the target system, browses sources, assigns risks or guarantees report accuracy.
Fix validation errors rather than deleting substantive findings to pass the helper.
