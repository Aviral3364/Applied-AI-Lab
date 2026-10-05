# Staff-level review method

## Inventory and scope

Identify task boundaries, allowed data/resources, irreversible actions, tenancy, credentials and delegation, model/tool versions, state stores, queues, deployment controls and operational budgets.
Name known capabilities, absent capabilities and unknown capabilities separately.
A description of an intention is not evidence of its enforcement.
Scale review depth to available evidence; offer a preliminary review rather than demanding all artifacts up front.

Inspect trust boundaries: external text → context, context → action proposal, proposal → executor, executor → external service, persisted memory → future runs, and agent → agent.
Trace a high-impact action and a realistic failure path end to end before recommending components.

## Classify evidence

| Label | Required basis |
| --- | --- |
| Confirmed defect | Direct artifact evidence demonstrating the defect within specified scope, or an authorized observed failure. Code evidence may establish a code defect without proving deployed exploitation. |
| Plausible risk | A concrete path and impact conditional on explicit, unresolved assumptions. It is not a confirmed vulnerability. |
| Evidence gap | The relevant behaviour/control cannot be determined from supplied artifacts. Explain what evidence would resolve it. |
| Validated control | Evidence supports this control within a stated boundary; distinguish code inspection from a successful test and production observation. |

Use file/section/config/test identifiers that actually exist.
Summarize evidence without copying secrets.
Never claim tests ran merely because a test file exists.
A model-generated explanation or chain of thought is not an authoritative execution log or proof of causal reasoning.

## Severity and priority

Severity is impact **if the mechanism occurs**, scoped to affected data, action and blast radius.
Confidence is strength of evidence; likelihood is a reasoned exposure judgment, usually unknown without operational data.
Do not manufacture numerical likelihoods.

- **Critical:** credible broad/high-impact compromise or irreversible loss with severe exposure; justify actual assets and reachable authority.
- **High:** significant unauthorized access/action, material state corruption or sustained service loss with meaningful blast radius.
- **Medium:** bounded integrity, quality, privacy, availability or recovery impairment.
- **Low:** limited impact or defence-in-depth improvement.
- **Unknown:** missing facts prevent impact assessment. Use this instead of inflating an evidence gap to Critical.

Context can change these judgments.
Explain preconditions and existing mitigations.
An open question is not automatically a release blocker.
Mark a recommended blocker only when a credible material mechanism or explicitly required control justifies it.
Proposed severity does not become an industry-standard score.

Prioritize urgent containment, pre-release fixes, scheduled improvements and investigation actions according to impact, exposure, dependencies and effort.
No arbitrary scoring formula.
Keep proposed owner roles and timelines distinct from assignments agreed by the team.

## Action quality

An action must state the component, concrete change/investigation, protected invariant, acceptance test, trade-off, control failure behaviour and residual risk.
Link it to evidence and a finding.

Examples of reasoning to apply when relevant:

- Authorization and exact-action approval must be independently checked at execution; prompt refusals do not provide access control.
  An approval cannot silently authorize changed parameters or replayed actions.
- A schema-valid tool call can still target the wrong resource or violate business constraints.
  Validate semantics and state preconditions too.
- A timeout may follow a committed side effect.
  Reconcile before retrying when outcomes are ambiguous; establish idempotency scope, key lifetime and duplicate behaviour.
  No unsupported exactly-once guarantee across independent tools.
- Bound retries, queues, fan-out, run length and spend.
  Cancellation cannot necessarily undo a committed action; define draining/reconciliation separately.
- Compensating actions are not atomic rollback and may fail. State the irreversible steps and recovery ownership.
- Memory, retrieval and caches need provenance, isolation and permission-change handling where applicable.
  Redaction and integrity checks alone do not prove trustworthiness.
- Prompt filtering/model guardrails are fallible.
  Layer containment and test bypass/overblocking.
  Decide fail-closed versus degraded behaviour by operation risk; never fall back into a more privileged path.

These are review prompts, not findings to emit for every system.
A proven existing control may resolve the concern; do not prescribe replacing it without a demonstrated reason.

## Verification and verdict

Tests should exercise a failure mechanism, its enforcement boundary and resulting state.
Include controlled negative cases, mid-operation failure, permission change and recovery where relevant.
Collect real tool execution/state evidence, not only final natural-language answers.
Measure stochastic behaviour with repeated controlled trials and report sample sizes and uncertainty; no failures observed does not establish impossibility.

Use fault injection only in an explicitly authorized isolated environment.
Do not suggest replaying writes on production to prove idempotency.
Shadow evaluation must suppress actual side effects and protect sensitive data.
Verify recovery procedures as well as prevention.

Record coverage as reviewed, unknown or not applicable with supporting reasons.
Unreviewed surfaces remain unknown.
Summarize existing controls, blockers, open questions and residual risks without a blanket certification.
Missing evidence may justify **requires validation** or **insufficient evidence**, not an invented defect.
