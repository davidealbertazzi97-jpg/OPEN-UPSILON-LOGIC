# Vault Omega

Vault Omega is an open-source, pre-structured Obsidian vault boilerplate designed specifically for agentic software workflows and coding assistants (e.g., Claude, Cursor, Codex, Antigravity, etc.). 

It introduces a structured cognitive layout for shared memory, logical guardrails, token-saving context summaries, and a built-in local swarm orchestrator to coordinate multiple agents seamlessly without context bloat.

## Features
- **Cognitive Obsidian Layout**: Standardized directory structure representing index maps (MOCs), project trackers, worksites (Cantieri), session handoffs, processes/protocols, and a general knowledge base.
- **Prolog-Style Declarative Guardrails**: A Python-based rule engine (`scripts/vault_guardrails.py`) that scans the vault, checks consistency constraints (e.g., active projects requiring a next step, session notes requiring handoff details), and reports warnings/conflicts.
- **Token Optimization**: A state compiler script (`scripts/token_optimizer.py`) that builds a compact markdown summary of the entire vault's active state (keeping it under 4000 tokens) to prevent coding agents from parsing the whole vault and wasting resources.
- **Local Swarm Orchestration**: A portable orchestration script (`scripts/swarm_orchestrator.py`) that enables main agents to spawn and coordinate specialized subordinate agents (Gemini, Goose, OpenCode, Codex, GitHub Copilot, Cursor) inside isolated project spaces.

---

## Directory Structure

```text
├── .gitignore
├── LICENSE
├── README.md
├── indici/                   # Maps of Content (MOCs) serving as entry points
│   ├── MOC_Architettura.md   # Structural blueprint of the vault
│   ├── MOC_Cantieri.md       # Registry of active worksites
│   ├── MOC_Progetti.md       # Long-term stable/system projects index
│   ├── MOC_Protocolli.md     # Registry of execution protocols
│   └── MOC_Sessioni.md       # Chronological log of session notes
├── progetti/                 # Stable and long-lived system projects
├── CANTIERI/                 # Active worksites where agents collaborate
│   ├── README.md             # Guidelines for worksite isolation
│   └── Template_Cantiere.md  # Template for initiating new worksites
├── sessioni/                 # Handoff files capturing progress and next steps
├── scoperte e processi/      # Reusable execution protocols and guides
├── informazioni generali/    # Stable knowledge base & agent configurations
├── dump/                     # Unstructured temporary notes and logs
└── scripts/                  # Automation, validation, and optimization scripts
    ├── vault_guardrails.py   # Python validator for logical checks
    ├── token_optimizer.py    # Compiler for context summaries
    └── swarm_orchestrator.py # Multi-agent dispatcher and logger
```

---

## Getting Started

### 1. Initial Onboarding
Coding agents entering this vault should read the root file `README.md` first and follow the entry path defined in `indici/MOC_Architettura.md`.

### 2. Running Guardrails
Validate the vault's consistency and rules integrity:
```bash
python3 scripts/vault_guardrails.py
```
For strict checking (fails with exit code 1 on conflict findings):
```bash
python3 scripts/vault_guardrails.py --strict
```

### 3. Compiling Token-Optimized Context
Before invoking any large LLM coding agent, generate a minimized context summary of the vault:
```bash
python3 scripts/token_optimizer.py
```
This writes a compact summary to `scripts/context_summary.md` which you can include in agent system prompts. It typically uses under 1000 tokens instead of the 4000+ tokens required to parse the whole directory tree.

### 4. Spawning Swarm Agents
Use the orchestrator to recommend, dispatch, and review tasks handled by local sub-agents:
```bash
# Recommend the best agent for a given task
python3 scripts/swarm_orchestrator.py recommend --task "Fix visual issues on React dashboard"

# Dispatch a task to a specialized agent
python3 scripts/swarm_orchestrator.py dispatch --agent gemini --project /path/to/repo --task "Refactor styling"
```

---

## License

This project is dual-licensed under the **Apache License 2.0** and the **MIT License**, permitting commercial use, modification, and distribution. See the `LICENSE` file for details.
