# Evals: production-ai-design-review

Behavioural checks for the skill.
These files are development material and are deliberately **not** part of the shipped skill directory.

| ID | Case | What it checks |
| --- | --- | --- |
| 1 | [01-idempotency-gap](cases/01-idempotency-gap.md) | Finds ambiguous-commit retries; no fabricated MCP/memory/sandbox/multi-agent defects |
| 2 | [02-approval-param-drift](cases/02-approval-param-drift.md) | Finds session-wide approval not bound to exact actions; excessive authority |
| 3 | [03-well-controlled](cases/03-well-controlled.md) | Restraint: no critical/high defects or write-path findings for a controlled read-only system |

Definitions and grading rules: [evals.json](evals.json) (same top-level shape as Anthropic skill-creator's `evals/evals.json`, plus a structured `grading` block).

## Run

1. Install the skill in your agent client (see the [guide](../../docs/production-ai-design-review.md#install)).
2. For each eval, give the agent the `prompt` and the case file, and save the exported JSON to a git-ignored workspace:
   `production-ai-design-review-workspace/iteration-1/eval-<id>/review.json`.
3. Score:

```bash
python3 evals/production-ai-design-review/score_eval.py 1 production-ai-design-review-workspace/iteration-1/eval-1/review.json
```

Exit code `0` = pass, `1` = expectation failed, `2` = usage/input error.
Output lists validation errors, missed expectations, fabricated findings, over-severity findings and verdict match.

## Limits

Scoring is structural: it checks domains, classifications, severities and verdicts, not the quality or truth of the prose.
Model behaviour is stochastic; run each case several times and report pass counts and sample size rather than a single result.
Read failures alongside the full review before changing the skill.
