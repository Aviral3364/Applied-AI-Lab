# Applied AI Lab

A home for AI agent code, reusable skills, experiments and tools for building dependable AI systems.

## Available now

- [Production AI Design Review](docs/production-ai-design-review.md): an evidence-grounded review skill for production AI/LLM and agent systems, covering reliability, security, guardrails and operations, with mitigation actions and verification tests.

## Repository layout

```text
skills/<skill-name>/   Shippable skills only (SKILL.md, scripts/, references/, assets/, agents/)
docs/                  Human-facing guides, one per skill
tests/                 Unit tests and Agent Skills spec conformance checks for every skill
evals/<skill-name>/    Behavioural eval cases and offline scorers
tools/                 Repository maintenance scripts (doc lint, source reachability)
```

Skills follow the [Agent Skills specification](https://agentskills.io/specification).
Tests, evals and docs are kept out of skill directories so that copying a skill ships only what an agent loads; `tests/test_skill_conformance.py` enforces this in CI.

## Development

```bash
python3 -m unittest discover -s tests -t . -v
python3 tools/lint_docs.py
```

## License

[Apache-2.0](LICENSE). See [CHANGELOG.md](CHANGELOG.md) for release notes.
