---
type: protocol
status: active
tags: [protocol, logic, guardrails, anti-hallucination]
---
# Protocol Logical Guardrails

Protocol for using declarative logic rules to prevent drift and hallucinations of coding agents within the Upsilon vault.

## Objective of Declarative Logic
Instead of letting the LLM generate unconstrained actions, the vault incorporates deterministic logical checks. The checks standardize the operational state and reduce costs by translating the markdown graph into evaluable predicates:
1. **Facts**: Properties extracted from YAML frontmatter or conventional markers. Examples:
   - `worksite(worksite_id, status)`
   - `session(session_id, date, project_id)`
   - `owner(worksite_id, owner_name)`
2. **Consistency Rules**: Logical conditions to satisfy to declare the vault consistent. Examples:
   - An active project must have at least one recent work session.
   - Every created note must be referenced by at least one MOC (no orphan notes).
   - Every recent work session must include explicit headings for handoffs.

## Control Layer (`vault_guardrails.py`)
The script `scripts/vault_guardrails.py` implements this rules engine in Python:
- Parses markdown files to extract structured data (Facts).
- Evaluates logical rules for completeness and consistency.
- Returns structured results:
  - `ok`: Compliant state.
  - `warning`: Non-blocking issue (e.g. legacy handoff style).
  - `conflict`: Blocking contract violation (e.g. worksite not indexed in MOC).

## How to Mitigate Hallucinations
- Agents must run `python3 scripts/vault_guardrails.py` at the end of their session.
- Logical errors are raised explicitly, forcing the agent to correct its own nodes before declaring completion.

---
[[MOC_Protocols]] | [[MOC_Architecture]]
