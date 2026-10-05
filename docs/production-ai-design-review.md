# Production AI Design Review

A portable [Agent Skill](https://agentskills.io/specification) for reviewing production AI/LLM and agent architectures, workflows, design documents and code.
It connects reliability and security findings to concrete mitigations and verification tests.

- Skill: [`skills/production-ai-design-review/`](../skills/production-ai-design-review/) (entry point: [SKILL.md](../skills/production-ai-design-review/SKILL.md))
- License: [Apache-2.0](../LICENSE)
- Changes: [CHANGELOG.md](../CHANGELOG.md)

## Who it is for

Use it for design or readiness reviews of systems where a model plans, retrieves, calls tools, writes state or delegates to other agents.

It is **not** a general architecture review for non-AI services.
Several domains (`capacity`, `privacy`, `eval-release`, `operations`) apply equally to the services supporting an AI system,
and are reviewed where they affect the AI system's behaviour, authority or recovery.

## What it reviews

The question bank covers 19 domains: task success, planning, retrieval, prompt injection, authorization, tool contracts, execution containment, guardrails,
retries, state consistency, capacity, cost, memory, privacy, supply chain, MCP, multi-agent delegation, evaluations/releases and operations.

The reviewer selects relevant domains from the system's capabilities.
It separates confirmed defects, plausible risks, evidence gaps and validated controls rather than turning every checklist question into a finding.

## Install

Copy the whole skill directory (not only `SKILL.md`; `scripts/`, `references/`, `assets/` and `agents/` must stay alongside it) into a skill location supported by your client.

| Client | Personal (all projects) | Project (commit to repo) | Official docs |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/skills/production-ai-design-review/` | `.claude/skills/production-ai-design-review/` | [Skills](https://docs.anthropic.com/en/docs/claude-code/skills) |
| OpenAI Codex | `$HOME/.agents/skills/production-ai-design-review/` | `.agents/skills/production-ai-design-review/` | [Skills](https://developers.openai.com/codex/skills) |

Locations verified against the linked official docs on 2026-10-05; consult them for other clients and for changes.

```bash
git clone https://github.com/Aviral3364/Applied-AI-Lab.git
cp -R Applied-AI-Lab/skills/production-ai-design-review ~/.claude/skills/
```

`agents/openai.yaml` is optional Codex/ChatGPT UI metadata; other clients ignore it.

## Use the skill

Example request:

> Use production-ai-design-review to review this architecture.
> Identify evidence-grounded reliability and security risks, then propose prioritized mitigation actions and verification tests.
> Distinguish observed defects from missing evidence.

Supply the design or code you want reviewed, its intended tasks and action capabilities, and any relevant tests or configuration.
Remove secrets and customer identifiers.
Missing evidence does not prevent a preliminary review, but limits its conclusions.

## What you receive

- A scoped assessment with evidence and severity rationale.
- Mitigation or investigation actions with owner roles and enforcement locations.
- Trade-offs, failure behaviour, recovery requirements and residual risks.
- Observable acceptance tests, clearly separated from tests actually executed.
- Coverage, assumptions and official sources supporting external technical claims.

External verification uses official first-party documentation or official standards/security publications.
A source describing a risk does not prove the reviewed system contains it.
The [source policy](../skills/production-ai-design-review/references/source-policy.md) explains provenance, version checks and offline limitations.

## Offline helpers

Python 3.10+ standard library only.
No installation, credentials, external API calls or execution of the reviewed system is required.
Run from the installed skill directory:

```bash
# Select questions for a system that retrieves documents and changes state.
python3 scripts/review_tools.py questions --capability retrieval --capability writes

# Validate the synthetic example's report structure.
python3 scripts/review_tools.py validate assets/example-review.json

# Render an exported report. Existing output files are not overwritten.
python3 scripts/review_tools.py render assets/example-review.json --output example-review.md
```

Available capability flags: `retrieval`, `tools`, `writes`, `memory`, `code-execution`, `mcp`, `multi-agent`.
The tool does not discover capabilities; unspecified capabilities remain a review question.

`validate` checks structure, evidence/action/test linkage, catalog domains (or `custom:<name>`) and verdict consistency.
It does not check the truth of a report, publisher ownership or production safety.
See the [report format](../skills/production-ai-design-review/references/report-format.md) and [fictional example](../skills/production-ai-design-review/assets/example-review.json).

## Development

Tests and evals live outside the skill so that only runtime content ships.

```bash
python3 -m unittest discover -s tests -t . -v     # unit + skill conformance tests
python3 tools/lint_docs.py                        # prose line-length check
```

Evals: see [evals/production-ai-design-review](../evals/production-ai-design-review/README.md).

## Review boundaries

The skill is a review workflow, not an automated vulnerability scanner or production-readiness certification.
It cannot guarantee exhaustive coverage, zero failures or immunity to prompt injection.
Live fault injection, transactions, deployments and data changes require separate authorization.
Proposed mitigations become validated controls only after appropriate evidence is collected.

Public references and example verification dates are historical snapshots.
Refresh version-sensitive claims using official sources during each applicable review.
