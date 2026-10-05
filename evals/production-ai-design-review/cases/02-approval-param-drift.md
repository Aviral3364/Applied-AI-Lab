# Case 02 — Infrastructure scaling agent (synthetic)

> Fictional system for evaluation only. Any resemblance to a real system is coincidental.

## Purpose

An operations agent helps on-call engineers adjust Kubernetes deployments during incidents.
It runs in production with access to three clusters.

## Components

- **Planner:** an LLM reads the incident channel and proposes actions.
- **Tools:**
  - `get_deployment(cluster, name)` — read-only.
  - `scale_deployment(cluster, name, replicas)` — write.
  - `restart_deployment(cluster, name)` — write.
- **Approval flow:** before any write, the agent posts a natural-language summary ("Scale checkout to more replicas in prod-eu") to the incident channel with an Approve button.

## Approval implementation (excerpt supplied)

```python
def on_approve(session_id, user):
    if user in ONCALL_GROUP:
        sessions[session_id].approved = True   # no expiry

def execute(session_id, tool_call):
    if tool_call.is_write and not sessions[session_id].approved:
        raise PermissionError("approval required")
    return tools[tool_call.name](**tool_call.args)
```

- The approval message shows only the summary text, not the exact tool arguments.
- After approval, the planner may continue planning and issue further write calls in the same session.

## Authorization

- The executor uses a single Kubernetes service account bound to `cluster-admin` on all three clusters.

## Not present

No retrieval index, no persistent memory, no MCP, no other agents.

## Tests supplied

- One test that `execute` raises `PermissionError` when `approved` is False.
