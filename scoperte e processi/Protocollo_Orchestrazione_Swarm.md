---
type: protocol
status: active
tags: [protocollo, swarm, orchestrazione]
---
# Protocollo Orchestrazione Swarm

Questo protocollo descrive come l'agente orchestratore coordina gli agenti delegati (lane esterne) per eseguire compiti delimitati all'interno dei cantieri attivi.

## Principio della Delega
L'agente principale agisce da orchestratore, mantenendo la visione strategica, la revisione severa del codice e la sintesi finale, delegando le attività esecutive a slot agenti dedicati:
- **`gemini`**: Specializzato in rifinitura visiva, UX, testi e seconda opinione frontend.
- **`goose`**: Utilizzato per diagnostica di sistema, operazioni a basso livello ed esperimenti isolati.
- **`opencode`**: Utilizzato per esplorazione, scrittura di documentazione ed esecuzione di smoke test.
- **`codex`**: Specializzato in modifiche strutturali rigorose, refactoring di backend e refactoring di sicurezza.
- **`copilot`**: Integrato nei flussi di lavoro nativi di GitHub (Issue, PR, push).
- **`cursor`**: Utilizzato come corsia alternativa per la programmazione interattiva e la risoluzione di problemi IDE.

## Flusso di Lavoro Swarm
1. **Pianificazione e Selezione**: L'orchestratore analizza il task e richiede una raccomandazione:
   ```bash
   python3 scripts/swarm_orchestrator.py recommend --task "Scrivere test di integrazione per endpoint di login"
   ```
2. **Dispatch**: Avvio del worker dedicato sul repo del cantiere in modalità background o foreground:
   ```bash
   python3 scripts/swarm_orchestrator.py dispatch --agent codex --project /home/user/my-project --task "Scrivere test di login"
   ```
3. **Esecuzione e Log**: Il worker esegue l'agente in sandbox/host, indirizzando i log su `agent.log` all'interno della directory della corsa (`runs/run-YYYYMMDD-.../`).
4. **Validazione e Chiusura**: Prima di completare il task, l'agente delegato DEVE effettuare un self-review (rileggere le modifiche, correggere difetti evidenti) e stampare un `FINAL REPORT`.
5. **Takeover**: L'orchestratore esegue la review, controlla i guardrail della memoria e acquisisce il lavoro eseguito.

---
[[MOC_Protocolli]] | [[MOC_Cantieri]]
