# Production AI Design Review

A portable agent skill for reviewing production AI architectures, workflows, design documents and code. It connects reliability and security findings to concrete mitigations and verification tests.

## What it reviews

The question bank covers 19 domains: task success, planning, retrieval, prompt injection, authorization, tool contracts, execution containment, guardrails, retries, state consistency, capacity, cost, memory, privacy, supply chain, MCP, multi-agent delegation, evaluations/releases and operations.

The reviewer selects relevant domains from the system's capabilities. It separates confirmed defects, plausible risks, evidence gaps and validated controls rather than turning every checklist question into a finding.

## Use the skill

Copy this repository's skill files into a `production-ai-design-review` directory in the skill location supported by your agent client. Consult that client's official installation instructions. The entry point is [SKILL.md](SKILL.md); references and scripts must remain alongside it.

Example request:

> Use production-ai-design-review to review this architecture. Identify evidence-grounded reliability and security risks, then propose prioritized mitigation actions and verification tests. Distinguish observed defects from missing evidence.

Supply the design or code you want reviewed, its intended tasks and action capabilities, and any relevant tests or configuration. Remove secrets and customer identifiers. Missing evidence does not prevent a preliminary review, but limits its conclusions.

## What you receive

- A scoped assessment with evidence and severity rationale.
- Mitigation or investigation actions with owner roles and enforcement locations.
- Trade-offs, failure behaviour, recovery requirements and residual risks.
- Observable acceptance tests, clearly separated from tests actually executed.
- Coverage, assumptions and official sources supporting external technical claims.

External verification uses official first-party documentation or official standards/security publications. A source describing a risk does not prove the reviewed system contains it. The [source policy](references/source-policy.md) explains provenance, version checks and offline limitations.

## Offline helpers

Python 3.10+ standard library only. No installation, credentials, external API calls or execution of the reviewed system is required.

```bash
# Select questions for a system that retrieves documents and changes state.
python3 scripts/review_tools.py questions --capability retrieval --capability writes

# Validate the synthetic example's report structure.
python3 scripts/review_tools.py validate examples/example-review.json

# Render an exported report. Existing output files are not overwritten.
python3 scripts/review_tools.py render examples/example-review.json --output example-review.md

# Run the helper test suite.
python3 -m unittest discover -s tests -v
```

Available capability flags: `retrieval`, `tools`, `writes`, `memory`, `code-execution`, `mcp`, `multi-agent`. The tool does not discover capabilities; unspecified capabilities remain a review question.

See the [report format](references/report-format.md) and [fictional example](examples/example-review.json). The helper validates structural consistency and evidence/action/test linkage, not the truth of a report, publisher ownership or production safety.

## Review boundaries

The skill is a review workflow, not an automated vulnerability scanner or production-readiness certification. It cannot guarantee exhaustive coverage, zero failures or immunity to prompt injection. Live fault injection, transactions, deployments and data changes require separate authorization. Proposed mitigations become validated controls only after appropriate evidence is collected.

Public references and example verification dates are historical snapshots. Refresh version-sensitive claims using official sources during each applicable review.
