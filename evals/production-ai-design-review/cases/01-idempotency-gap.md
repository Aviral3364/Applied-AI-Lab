# Case 01 — Refund agent (synthetic)

> Fictional system for evaluation only. Any resemblance to a real system is coincidental.

## Purpose

A customer-support agent resolves refund requests for an online store.
It is deployed to production behind the support chat widget.

## Components

- **Planner:** a hosted LLM receives the chat transcript and the order record, then proposes tool calls.
- **Tools:**
  - `get_order(order_id)` — read-only lookup in the orders database.
  - `issue_refund(order_id, amount_cents)` — calls the payment provider's `POST /refunds` endpoint.
- **Executor worker:** consumes proposed tool calls from a queue and invokes the tool.

## Executor retry contract

- Each tool call has a 5 second client timeout.
- On timeout or HTTP 5xx, the worker retries the same call up to 3 times with 1 second fixed backoff.
- `issue_refund` sends `{order_id, amount_cents}` only.
  No idempotency key or request identifier is sent, and the worker does not query existing refunds before retrying.
- The payment provider documentation (excerpt supplied) states: "A request that times out may still have been processed."

## Authorization

- The executor uses one service credential with refund permission for all stores.
- Refunds above 500.00 require supervisor approval; the approval is checked by the executor against the exact `order_id` and `amount_cents` before calling `issue_refund`.

## Not present

No persistent memory, no code execution, no MCP connectors, no other agents.

## Tests supplied

- Unit tests for `get_order` parsing.
- No tests for retry behaviour.
