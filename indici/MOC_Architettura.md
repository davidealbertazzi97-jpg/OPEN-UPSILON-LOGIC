---
type: architecture
status: active
priority: high
tags: [moc, architettura, entrypoint]
---
# MOC Architettura

This Map of Content (MOC) defines the entry topology and rules of Vault Upsilon. Coding agents must use this node to orient themselves and find other indices and modules.

## Structural Design
Vault Upsilon is built as an agentic memory model. Instead of scanning directories (which wastes valuable context tokens), agents must follow wikilinks to jump between nodes.

```mermaid
graph TD
    README[README.md] --> MOC_Arch[indici/MOC_Architettura.md]
    MOC_Arch --> MOC_Proj[indici/MOC_Progetti.md]
    MOC_Arch --> MOC_Cant[indici/MOC_Cantieri.md]
    MOC_Arch --> MOC_Prot[indici/MOC_Protocolli.md]
    MOC_Arch --> MOC_Sess[indici/MOC_Sessioni.md]
    
    MOC_Proj --> Proj[progetti/]
    MOC_Cant --> Cant[CANTIERI/]
    MOC_Prot --> Prot[scoperte e processi/]
    MOC_Sess --> Sess[sessioni/]
```

## Folder Descriptions
- **`indici/`**: Contain the MOCs. They map the entire memory space semantically.
- **`progetti/`**: Houses long-lived, stable, or system project definitions.
- **`CANTIERI/`**: Contains active worksites where multiple agents iterate in parallel.
- **`sessioni/`**: Contains chronological session notes serving as workspace handoffs.
- **`scoperte e processi/`**: Registry of execution protocols (recipes and procedures).
- **`informazioni generali/`**: Stable knowledge base & agent configurations (contiene [[Integrazione_Agenti]]).
- **`dump/`**: Unstructured temp notes and logs.
- **`scripts/`**: Tooling for validation, token optimization, and orchestration.

## Core Rules for Agents
1. **Never Orphan a Node**: Every created node must have at least one incoming or outgoing `[[WikiLink]]` to/from a relevant MOC or project node.
2. **Mandatory Handoff**: Every significant block of work must conclude with a session note in `sessioni/` linking to the active project.
3. **Commit often**: Keep the workspace clean and commit changes to git before concluding a session.
4. **Token Management**: Run `python3 scripts/token_optimizer.py` before starting a session to keep context sizes low.

---
[[MOC_Progetti]] | [[MOC_Cantieri]] | [[MOC_Protocolli]] | [[MOC_Sessioni]]
