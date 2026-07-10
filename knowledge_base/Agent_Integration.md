---
type: documentation
status: active
tags: [onboarding, integration, api, mcp]
---
# Agent Integration (Collective Mind Integration)

This document explains how you, as a programming agent, can connect to this vault and use it as a shared brain and collective memory for the swarm.

## 1. Direct Filesystem Access (Standard Mode)
If you were launched with read/write access to the vault folder:
1. **Read State (Token Saving)**: As a first step, do not scan the entire filesystem. Read only the `context_summary.md` file located at the root of the vault. This file summarizes the current status of worksites, recent sessions, and next steps in under 200 tokens.
2. **Update Notes**: Save your progress by writing chronological notes in `sessions/` (with prefix `Session_YYYY-MM-DD_<WorksiteSlug>_...`) and update the worksite status in `worksites/`.
3. **Verify Guardrails**: Before concluding your turn, run the logic validator to ensure you have not violated the vault's structural constraints:
   ```bash
   python3 scripts/vault_guardrails.py --strict
   ```

## 2. REST API Access (Playground Server)
If you have enabled a tool to make HTTP requests (e.g. curl, fetch, or MCP), you can interact with the collective mind via the local server running at `http://localhost:8080`:

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/files` | `GET` | Returns the tree of all markdown files in the vault. |
| `/api/file?path=<rel_path>` | `GET` | Reads the markdown content of a specific note. |
| `/api/file?path=<rel_path>` | `POST` | Writes/Saves the content of a note (send body in plain text). |
| `/api/optimize` | `GET` | Compiles and returns the updated `context_summary.md` summary. |
| `/api/guardrails` | `GET` | Runs the validator and returns the JSON report of conflicts/warnings. |
| `/api/swarm/recommend?task=<task>` | `GET` | Returns recommendations for the best agents suited for the task. |
| `/api/swarm/dispatch` | `POST` | Starts a delegated agent (e.g. gemini, codex) in the background. |

## 3. MCP Integration (Model Context Protocol)
You can configure this playground server as an MCP server in your client (e.g. Claude Desktop or Cursor) to give your agent native tools for reading, writing, and validating the collective memory.

---
[[MOC_Architecture]] | [[Protocol_Swarm_Orchestration]]
