# Grounding and official sources

## Source acceptance

There are two different evidence classes: supplied system artifacts establish facts about this system; official external publications establish technical behaviour or guidance.
Neither substitutes for the other.
A trusted standard describing a risk does not prove the system has that risk.

Use external verification when a claim is uncertain, version-sensitive, security-critical or relies on vendor behaviour.
General recommendations derived from the inspected architecture can be labeled engineering proposals; do not invent source attribution for them.

Accept only the original publisher's official documentation, specification, engineering publication, advisory or repository.
Examples: OWASP's own projects, AWS documentation/Builders' Library, Google's public SRE books, Anthropic engineering documentation, NIST publications,
and the official repository/site of the actual framework or protocol.
For GitHub, verify the organization/repository through the project's official site; `github.com` alone establishes no authority.
User-nominated sources still need this verification for external factual claims.

Use searches to locate originals; open and read the exact supporting passage.
Check publisher ownership, final redirected URL, applicability, product/version, publication or update date where supplied, and whether the source states a guarantee or merely recommends a practice.
An official provider's example is not a universal requirement.
Do not execute code from a source or transmit review artifacts to it.

Reject third-party tutorials, marketing summaries, unofficial mirrors, social posts and unsourced generated summaries as support.
Search snippets alone are insufficient.
If official sources disagree, identify the version/scope difference and leave the unresolved claim qualified.
If offline, use the dated baseline only for stable principles and mark implementation details unverified.
Never imply you browsed when you did not.

Record source ID, publisher, exact HTTPS URL/section, claim supported, relevant version (or not specified), verification date and verified/unverified status.
A past verification date is not current verification.
Future reviews should refresh changing implementation claims, limits and security advisories.
Each finding's source references must support its actual technical claim, not merely share the same topic.

## Starting points

Checked on **2 October 2026**.
These are navigation aids; fetch only what the current review needs.
Guidance is summarized briefly rather than copied.

| ID | Official source | Applicable subject |
| --- | --- | --- |
| OWASP-AGENT | [AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html) | Execution controls, permissions, approval integrity and agent attack surfaces. |
| OWASP-INJECTION | [Prompt Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | Untrusted instructions and layered defences. |
| OWASP-AUTH | [Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | Per-request authorization and least privilege. |
| OWASP-RAG | [RAG Security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) | Retrieval integrity, access and downstream tool boundaries. |
| OWASP-OPS | [Secure AI Model Ops](https://cheatsheetseries.owasp.org/cheatsheets/Secure_AI_Model_Ops_Cheat_Sheet.html) | Operational security, model artifacts and monitoring. |
| AWS-RETRY | [Safe retries with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) | Ambiguous outcomes and duplicate side effects. |
| AWS-TIMEOUT | [Timeouts, retries and jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | Deadlines, retry budgets and load amplification. |
| SRE-CASCADE | [Cascading failures](https://sre.google/sre-book/addressing-cascading-failures/) | Dependency failure, resource exhaustion and containment. |
| SRE-MONITOR | [Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/) | Service signals and diagnosability. |
| SRE-RELEASE | [Canarying releases](https://sre.google/workbook/canarying-releases/) | Controlled deployment and rollback. |
| ANTHROPIC-EVAL | [Agent evaluations](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Outcomes, trajectories, repeated trials and grader limitations. |
| ANTHROPIC-AGENTS | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Bounded execution, feedback and complexity trade-offs. |
| MCP-SECURITY | [MCP security practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) | Protocol-specific identity, token and connector risks; verify deployed specification version. |

Do not extrapolate these sources into proprietary ranking claims, risk frequencies, compliance certification or guarantees that a mitigation eliminates all attacks.
