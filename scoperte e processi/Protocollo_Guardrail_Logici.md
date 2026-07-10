---
type: protocol
status: active
tags: [protocollo, logica, guardrails, antiallucinazione]
---
# Protocollo Guardrail Logici

Protocollo per l'utilizzo di regole logiche declarative atte a prevenire derive e allucinazioni degli agenti di coding nel vault Obsidian.

## Obiettivo della Logica Dichiarativa
Invece di lasciare che l'LLM crei risposte non vincolate, il vault incorpora controlli logici deterministici. I controlli logici standardizzano lo stato operativo e riducono i costi (token) traducendo il grafo delle note Obsidian in predicati valutabili:
1. **Fatti (Facts)**: Proprietà estratte dal frontmatter YAML o da marcatori convenzionali. Esempi:
   - `cantiere(cantiere_id, status)`
   - `session(session_id, date, project_id)`
   - `owner(cantiere_id, owner_name)`
2. **Regole di Coerenza (Rules)**: Condizioni logiche da soddisfare per considerare il vault "consistente". Esempi:
   - Un progetto attivo deve avere almeno una sessione di lavoro recente.
   - Ogni nota operativa creata deve essere referenziata da almeno un MOC (nessuna nota orfana).
   - Ogni sessione di lavoro recente deve includere intestazioni esplicite per l'handoff.

## Layer di Controllo (`vault_guardrails.py`)
Lo script `scripts/vault_guardrails.py` implementa questo motore di regole in Python:
- Analizza i file markdown estrudendo i dati strutturati (Facts).
- Valuta le regole logiche di completezza e coerenza.
- Ritorna esiti strutturati:
  - `ok`: Tutto conforme.
  - `warning`: Problema non bloccante (es: stile di handoff deprecato).
  - `conflict`: Violazione bloccante del contratto (es: cantiere non indicizzato nel MOC).

## Come Mitigare le Allucinazioni
- Gli agenti devono eseguire `python3 scripts/vault_guardrails.py` a fine sessione.
- Gli errori logici vengono sollevati esplicitamente, forzando l'agente a correggere i propri nodi prima di dichiarare la fine del lavoro.

---
[[MOC_Protocolli]] | [[MOC_Architettura]]
