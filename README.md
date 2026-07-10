# Vault Omega & Playground
> **Experimental Sandbox for Agnostic Multi-Agent Swarms & Logic-Grounded Cognitive Memory**

---

## 👁️ Visione & Origine del Progetto

**Vault Omega** è un progetto sperimentale nato dal desiderio di fondere la **logica pura della programmazione logica dichiarativa (Prolog-style)** con la potenza predittiva dei **modelli linguistici statistici (LLM)**. 

I moderni agenti di coding (come Claude Code, Cursor, Codex, Antigravity) operano su basi statistiche, il che li rende inclini all'allucinazione, alla deriva del contesto e a consumi esponenziali di token. Vault Omega introduce un'infrastruttura **agnostica, auto-espandibile e deterministica** per governare la memoria collettiva dello sciame e consentire la collaborazione parallela di più agenti autonomi, eliminando la dipendenza da un singolo IDE o provider proprietario.

```text
       ┌────────────────────────────────────────────────────────┐
       │                 Statistical LLM Agents                 │
       │          (Claude Code, Cursor, Codex, Gemini)          │
       └───────────────────────────┬────────────────────────────┘
                                   │  Uses & Modifies
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             Vault Omega Cognitive Layout               │
       │    (Structured Markdown Notes: MOCs, Cantieri, Logs)   │
       └───────────────────────────┬────────────────────────────┘
                                   │  Evaluated By
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │               Deterministic Logic Layer                │
       │   - vault_guardrails.py (Rules & Conflict Checker)     │
       │   - token_optimizer.py  (Aggregator & Token Saver)     │
       └────────────────────────────────────────────────────────┘
```

---

## 🚀 Obiettivi Fondamentali

1. **Riduzione Drastica delle Allucinazioni**: Sostituzione delle euristiche statistiche con controlli logici deterministici. Un agente non può dichiarare un compito completato se non soddisfa il contratto strutturale del vault.
2. **Risparmio del Contesto (Token Saving)**: Riduzione fino al 95% dei token sprecati in letture esplorative, grazie alla compilazione dinamica dello stato in un singolo file compresso (`context_summary.md`).
3. **Collaborazione Multi-Agente in Parallelo**: Uno script orchestratore portabile in grado di raccomandare e instradare sotto-task a slot agenti specializzati (`gemini`, `goose`, `opencode`, `codex`, `copilot`, `cursor`).
4. **Indipendenza da IDE e Provider (Agnostico)**: Un'infrastruttura decentralizzata che gira in locale sulla macchina del developer, accessibile sia da filesystem che via API REST o protocollo MCP.
5. **Autonomia Logica e Auto-Espansione (Self-Expanding Mind)**: Gli agenti stessi possono scrivere nuovi protocolli e modificare i file di verifica logica Python per introdurre nuove regole che si applicheranno a tutti i futuri agenti dello sciame.

---

## 📁 Architettura & Struttura del Vault

Il vault è strutturato come un grafo cognitivo basato su **WikiLinks (`[[Link]]`)** e diviso in compartimenti specifici:

```text
├── .gitignore
├── LICENSE                   # Licenza Apache 2.0 / MIT
├── README.md                 # Questo documento di onboarding
├── context_summary.md        # Sommario compresso compilato (~150 token)
├── indici/                   # Mappe dei Contenuti (MOC) per la navigazione semantica
│   ├── MOC_Architettura.md   # Grafo e topology del vault
│   ├── MOC_Cantieri.md       # Tracciatore dei progetti in sviluppo attivo
│   ├── MOC_Progetti.md       # Indice dei progetti stabili di sistema
│   ├── MOC_Protocolli.md     # Indice delle guide e dei processi
│   └── MOC_Sessioni.md       # Indice cronologico dei log di sessione
├── progetti/                 # Schede descrittive dei progetti stabili
├── CANTIERI/                 # Cartelle di lavoro attivo ad alta iterazione
│   ├── README.md             # Regole per l'isolamento dei cantieri
│   └── Template_Cantiere.md  # Modello per avviare un nuovo cantiere
├── sessioni/                 # Log di handoff che descrivono stato finale e prossimi passi
├── scoperte e processi/      # Guide operative e protocolli riutilizzabili
├── informazioni generali/    # KB stabile (es: Integrazione_Agenti.md)
├── dump/                     # Note temporanee, log e scratchpad (ignorati da Git)
└── scripts/                  # Motori logici e di orchestrazione
    ├── agents.json           # Configurazione CLI degli agenti dello sciame
    ├── vault_guardrails.py   # Validatore Prolog-style in Python
    ├── token_optimizer.py    # Compilatore dello stato della memoria
    └── swarm_orchestrator.py # Interfaccia di dispatching multi-agente
```

---

## ⚙️ I Tre Pilastri Logici

### 1. Il Validatore Logico (`vault_guardrails.py`)
Funge da motore di inferenza Prolog-style. Mappa le note markdown come predicati logici (es: `cantiere(id, status)`, `session(id, project)`) e verifica che le regole di coerenza siano soddisfatte:
- **Nessuna nota orfana**: Qualsiasi file markdown (fuori da sessioni e dump) deve essere linkato da almeno un MOC.
- **Contratto del Cantiere**: Ogni file in `CANTIERI/` deve avere frontmatter `type: project` e contenere le intestazioni standard (`## Obiettivo`, `## Perimetro`, `## Lane`, `## Prossimi passi`).
- **Contratto di Handoff**: Ogni sessione recente deve specificare dove deve guardare l'agente successivo.

Esecuzione:
```bash
python3 scripts/vault_guardrails.py --strict
```

### 2. Il Risparmio dei Token (`token_optimizer.py`)
Legge ricorsivamente il vault, filtra le parti non essenziali ed aggrega le informazioni attive in un singolo blocco di testo compresso (`context_summary.md`).
- **Il calcolo matematico**: Un agente che scansiona 10 note del vault per orientarsi consuma circa **4000+ token**. Leggendo solo il `context_summary.md` l'agente ottiene lo stesso allineamento in soli **150 token** (risparmio del 95%).

Esecuzione:
```bash
python3 scripts/token_optimizer.py
```

### 3. L'Orchestratore dello Sciame (`swarm_orchestrator.py`)
Fornisce una CLI portabile per consentire ad un agente capofila (es: Codex) di coordinare ed avviare altri agenti in parallelo all'interno di workspace isolati:
- **Raccomandazione**: Suggerisce l'agente migliore per un determinato task analizzando parole chiave (es: `gemini` per la UI, `codex` per refactoring backend).
- **Dispatch**: Avvia l'agente delegato in background, cattura lo standard output in un log file e ne valida la conformità strutturale alla chiusura.

Esecuzione:
```bash
# Raccomanda un agente
python3 scripts/swarm_orchestrator.py recommend --task "Fix dashboard styling"

# Avvia una corsa
python3 scripts/swarm_orchestrator.py dispatch --agent gemini --project /path/to/project --task "Improve CSS styling"
```

---

## 🖥️ La Web UI: Omega Playground

Il modulo **Omega Playground** è un'interfaccia web di cantiere interamente **open-source e dependency-free** situata in **`playground/`**. 

```text
+-----------------------------------------------------------------------------+
|                            Omega Playground Web UI                          |
+----------------------+------------------------------+-----------------------+
|  [Sidebar]           |  [Markdown Editor]           |  [D3 WikiLink Graph]  |
|  - indici/           |                              |                       |
|  - progetti/         |  Edit note contents          |  Visualizes floating  |
|  - CANTIERI/         |  & write double-click        |  nodes. Click to      |
|  - sessioni/         |  [[WikiLinks]]               |  navigate notes.      |
|                      +------------------------------+-----------------------+
|                      |  [Markdown Preview]          |  [Agent Swarm Panel]  |
|                      |                              |  - Recommend agent    |
|                      |  Live HTML rendering         |  - Dispatch worker    |
|                      |  with clickable WikiLinks    |  - Real-time terminal |
+----------------------+------------------------------+-----------------------+
```

### Caratteristiche
- **Graph Viewer D3.js**: Un grafico interattivo a forze che mappa le connessioni tra le note del vault in tempo reale. Cliccando su un nodo si apre la nota corrispondente.
- **Markdown Editor & Preview**: Editor side-by-side che trasforma i WikiLink `[[WikiLink]]` in collegamenti ipertestuali cliccabili nel pannello di preview.
- **Swarm Runner Terminal**: Pannello grafico per testare la prontezza degli agenti locali, richiedere raccomandazioni ed eseguire dispatch monitorando l'output in un terminale retro-glowing con scorrimento automatico.
- **Zero Install**: Il server (`server.js`) utilizza solo librerie standard di Node.js/Bun. Nessun pacchetto esterno da installare.

Avvio:
```bash
node playground/server.js
```
Quindi apri nel browser l'indirizzo **`http://localhost:8080`**.

---

## 📜 Licenza & Conformità Open Source

Il progetto Vault Omega è rilasciato sotto la **Licenza Apache 2.0** e la **Licenza MIT**. È utilizzabile liberamente, modificabile e distribuibile sia per scopi privati che commerciali.

### Riferimenti di terze parti (Licenze Rispettate):
Tutti i componenti esterni utilizzati dal playground sono open-source e pienamente conformi alle rispettive licenze d'uso:
1. **D3.js** (Visualizzazione Grafico): Rilasciata sotto **Licenza ISC** (estremamente permissiva e compatibile con Apache/MIT).
2. **Marked.js** (Parser Markdown): Rilasciata sotto **Licenza MIT** (pienamente compatibile).
3. **Python 3** (Esecuzione Motori Logici): Rilasciata sotto **Python Software Foundation License** (compatibile con Apache/MIT).
4. **Node.js / Bun** (Runtime Server): Rilasciate sotto licenze permissive MIT/BSD (pienamente compatibili).

Nessun codice proprietario o closed-source (compresi i sorgenti commerciali di Obsidian) è presente in questo repository.
