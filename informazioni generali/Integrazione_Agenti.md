---
type: documentation
status: active
tags: [onboarding, integrazione, api, mcp]
---
# Integrazione Agenti (Collective Mind Integration)

Questo documento spiega come tu, in quanto agente di programmazione, puoi connetterti a questo vault e utilizzarlo come cervello condiviso e memoria collettiva dello sciame.

## 1. Accesso Diretto tramite Filesystem (Modalità Standard)
Se sei stato lanciato con accesso in lettura/scrittura alla cartella del vault:
1. **Lettura Stato (Token Saving)**: Come primo passo, non scansionare l'intero filesystem. Leggi esclusivamente il file `context_summary.md` situato nella root del vault. Questo file riassume lo stato attuale dei cantieri, delle sessioni recenti e dei prossimi passi in meno di 200 token.
2. **Aggiornamento Note**: Salva il tuo progresso scrivendo note cronologiche in `sessioni/` (con prefisso `Sessione_YYYY-MM-DD_<CantiereSlug>_...`) e aggiorna lo stato dei cantieri in `CANTIERI/`.
3. **Verifica Guardrail**: Prima di concludere il tuo turno, esegui il validatore logico per assicurarti di non aver violato i vincoli strutturali del vault:
   ```bash
   python3 scripts/vault_guardrails.py --strict
   ```

## 2. Accesso tramite API REST (Server Playground)
Se hai abilitato uno strumento per effettuare richieste HTTP (es. curl, fetch o MCP), puoi interagire con la mente collettiva tramite il server locale attivo su `http://localhost:8080`:

| Endpoint | Metodo | Descrizione |
| --- | --- | --- |
| `/api/files` | `GET` | Ritorna l'albero di tutti i file markdown del vault. |
| `/api/file?path=<rel_path>` | `GET` | Legge il contenuto markdown di una specifica nota. |
| `/api/file?path=<rel_path>` | `POST` | Scrive/Salva il contenuto di una nota (invia il corpo in plain text). |
| `/api/optimize` | `GET` | Compila e restituisce il sommario aggiornato `context_summary.md`. |
| `/api/guardrails` | `GET` | Esegue il validatore e ritorna il report JSON dei conflitti/warning. |
| `/api/swarm/recommend?task=<task>` | `GET` | Ritorna le raccomandazioni degli agenti più indicati per il task. |
| `/api/swarm/dispatch` | `POST` | Avvia un agente delegato (es: gemini, codex) in background. |

## 3. Integrazione MCP (Model Context Protocol)
Puoi configurare questo server playground come server MCP all'interno del tuo client (es. Claude Desktop o Cursor) per dare all'agente strumenti nativi di lettura, scrittura e validazione della mente collettiva.

---
[[MOC_Architettura]] | [[Protocollo_Orchestrazione_Swarm]]
