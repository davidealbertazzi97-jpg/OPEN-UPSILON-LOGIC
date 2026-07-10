# Vault Omega & Playground
> **Experimental Sandbox for Agnostic Multi-Agent Swarms & Logic-Grounded Cognitive Memory**

---

## 👁️ Vision & Origin of the Project

**Vault Omega** is an experimental project born from the desire to merge **pure logic programming (Prolog-style)** with the predictive power of **statistical Large Language Models (LLMs)**.

Modern coding agents (such as Claude Code, Cursor, Codex, Antigravity) operate on statistical probabilities, making them prone to hallucinations, context drift, and exponential token consumption. Vault Omega introduces an **agnostic, self-expanding, and deterministic** infrastructure to govern the swarm's collective memory and enable parallel collaboration of multiple autonomous agents, eliminating dependency on a single proprietary IDE or environment.

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

## 🚀 Core Goals

1. **Drastic Reduction of Hallucinations**: Replacing statistical heuristics with deterministic logical checks. An agent cannot declare a task completed unless it satisfies the structural contract of the vault.
2. **Context Savings (Token Optimizer)**: Reducing up to 95% of tokens wasted in exploratory file scans, thanks to the dynamic compilation of the active state into a single compressed file (`context_summary.md`).
3. **Parallel Multi-Agent Collaboration**: A portable orchestrator script capable of recommending and routing sub-tasks to specialized agent slots (`gemini`, `goose`, `opencode`, `codex`, `copilot`, `cursor`).
4. **IDE & Provider Agnostic**: A decentralized infrastructure running locally on the developer's machine, accessible via filesystem, REST API, or MCP (Model Context Protocol).
5. **Autonomous Logical Self-Expansion**: Agents themselves can write new protocols and modify Python validation scripts to introduce new rules that apply to all future swarm runs.

---

## 📁 Archive & Vault Structure

The vault is structured as a cognitive graph based on **WikiLinks (`[[Link]]`)** and divided into specific compartments:

```text
├── .gitignore
├── LICENSE                   # Apache 2.0 / MIT License
├── README.md                 # This bilingual documentation
├── context_summary.md        # Compiled token-saving state summary (~150 tokens)
├── indici/                   # Maps of Content (MOC) for semantic navigation
│   ├── MOC_Architettura.md   # Grafo and topology of the vault
│   ├── MOC_Cantieri.md       # Active worksites registry
│   ├── MOC_Progetti.md       # Long-term stable/system projects index
│   ├── MOC_Protocolli.md     # Guides and execution protocols registry
│   └── MOC_Sessioni.md       # Chronological session handoff logs index
├── progetti/                 # stable system projects notes
├── CANTIERI/                 # Active high-iteration worksites
│   ├── README.md             # Worksite sandbox isolation guidelines
│   └── Template_Cantiere.md  # Template for initiating a new worksite
├── sessioni/                 # Chronological handoff notes
├── scoperte e processi/      # Reusable execution protocols and guides
├── informazioni generali/    # Stable knowledge base (e.g. Integrazione_Agenti.md)
├── dump/                     # Unstructured temporary logs and notes (Git ignored)
└── scripts/                  # Logical verification & swarm orchestrator scripts
    ├── agents.json           # Swarm agents CLI command configuration
    ├── vault_guardrails.py   # Prolog-style validator in Python
    ├── token_optimizer.py    # Cognitive state compiler and token saver
    └── swarm_orchestrator.py # Multi-agent dispatching CLI interface
```

---

## ⚙️ The Three Logical Pillars

### 1. Logical Validator (`vault_guardrails.py`)
Acts as a Prolog-style inference engine. It maps markdown files as logical predicates (e.g., `cantiere(id, status)`, `session(id, project)`) and runs consistency checks:
- **No Orphan Nodes**: Every markdown file (except session logs and dumps) must be linked by at least one MOC.
- **Worksite Contract**: Every file in `CANTIERI/` must have frontmatter `type: project`, status, and standard headings (`## Obiettivo`, `## Perimetro`, `## Lane`, `## Prossimi passi`).
- **Handoff Contract**: Every recent session must specify where the next agent should look.

Run it:
```bash
python3 scripts/vault_guardrails.py --strict
```

### 2. Token Saving (`token_optimizer.py`)
Recursively scans the vault, filters out non-essential info, and compiles the active state into a single compressed markdown block (`context_summary.md`).
- **The Math**: An agent scanning 10 vault notes to align consumes about **4000+ tokens**. Reading only `context_summary.md` yields the same alignment in just **150 tokens** (95% savings).

Run it:
```bash
python3 scripts/token_optimizer.py
```

### 3. Swarm Orchestrator (`swarm_orchestrator.py`)
Provides a portable CLI to allow a lead agent (e.g. Codex) to coordinate and launch other agents in parallel in isolated workspaces:
- **Recommendation**: Suggests the best agent for a task by parsing keywords (e.g., `gemini` for UI/UX, `codex` for backend/security).
- **Dispatch**: Spawns the worker agent in the background, captures stdout to a log file, and runs guardrails upon completion.

Run it:
```bash
# Get agent recommendation
python3 scripts/swarm_orchestrator.py recommend --task "Fix styling bugs"

# Dispatch task to agent
python3 scripts/swarm_orchestrator.py dispatch --agent gemini --project /path/to/project --task "Improve CSS styling"
```

---

## 🖥️ Web UI: Omega Playground

The **Omega Playground** is a **dependency-free, open-source** local web application located in `playground/`.

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

### Features
- **D3.js Graph Visualizer**: Interactive force-directed link graph showing connections between notes. Clicking a node opens it in the editor.
- **Markdown Editor & Preview**: Side-by-side editor converting `[[WikiLinks]]` into clickable navigation nodes in the preview pane.
- **Swarm Runner Terminal**: Control center to test agent readiness, request recommendations, dispatch workers, and stream console output in real-time.
- **Zero Install**: The server (`server.js`) uses only standard Node.js/Bun modules. No external packages to install.

Run it:
```bash
node playground/server.js
```
Then navigate to **`http://localhost:8080`**.

---

## 🔧 Quick Installation & Agent Automation

### Manual Installation (All Platforms)
To run the playground server locally:
```bash
# 1. Clone the repository
git clone https://github.com/davidealbertazzi97-jpg/OPEN-OMEGA-LOGIC.git

# 2. Enter the folder
cd OPEN-OMEGA-LOGIC

# 3. Launch the server
node playground/server.js
```
The dashboard is now running at `http://localhost:8080`.

### 🤖 Plug-and-Play Agent Automation Prompt (Cross-Platform)
Copy and paste this single prompt block directly into your AI coding agent (e.g. Claude Code, Cursor Agent, Aider, Codex) to let it automatically install, configure, and persist the playground server across reboots on **Linux, macOS, and Windows**:

````markdown
You are an autonomous AI coding agent. Your goal is to install, configure, and set up the Open-Omega-Logic playground vault on this host, ensuring it runs persistently on every system reboot.

Follow these step-by-step instructions:

1. **Clone the Repository**:
   Clone the repository to a dedicated directory in the user's home directory:
   ```bash
   git clone https://github.com/davidealbertazzi97-jpg/OPEN-OMEGA-LOGIC.git ~/OPEN-OMEGA-LOGIC
   ```

2. **Verify Prerequisites**:
   Check if Node.js (or Bun) and Python 3 are installed on the host. Locate the absolute path of `node` (using `which node` on Unix, or `where node` on Windows).

3. **Initialize the Vault State**:
   Enter the directory and compile the initial vault state:
   ```bash
   cd ~/OPEN-OMEGA-LOGIC
   python3 scripts/token_optimizer.py
   ```

4. **Ensure Cross-Platform Reboot Persistence**:
   Depending on the detected host Operating System, set up automatic persistence:

   - **On Linux**:
     Create `~/.config/systemd/user/omega-playground.service`:
     ```ini
     [Unit]
     Description=Omega Playground Server Daemon
     After=network.target

     [Service]
     ExecStart=<NODE_PATH> <REPO_PATH>/playground/server.js
     Restart=always
     Environment=PORT=8080
     WorkingDirectory=<REPO_PATH>

     [Install]
     WantedBy=default.target
     ```
     Enable and start the service:
     ```bash
     systemctl --user daemon-reload
     systemctl --user enable omega-playground.service
     systemctl --user start omega-playground.service
     ```

   - **On macOS**:
     Create `~/Library/LaunchAgents/com.omega.playground.plist`:
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
     <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>com.omega.playground</string>
         <key>ProgramArguments</key>
         <array>
             <string><NODE_PATH></string>
             <string><REPO_PATH>/playground/server.js</string>
         </array>
         <key>RunAtLoad</key>
         <true/>
         <key>KeepAlive</key>
         <true/>
         <key>WorkingDirectory</key>
         <string><REPO_PATH></string>
     </dict>
     </plist>
     ```
     Load the agent:
     ```bash
     launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.omega.playground.plist
     ```

   - **On Windows**:
     Create a silent startup script `omega-startup.vbs` in the Windows Startup Folder (`shell:startup`):
     ```vbs
     Set WshShell = CreateObject("WScript.Shell")
     WshShell.Run "node """ & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\OPEN-OMEGA-LOGIC\playground\server.js""", 0, False
     ```

5. **Validate Server**:
   Query `http://localhost:8080/api/files` to confirm that the server is up and listening. Report back to the user with the service status.
````

---

## 📜 License & Third-Party Compliance

The project is dual-licensed under the **Apache License 2.0** and the **MIT License**. It is free to use, modify, and distribute for both private and commercial purposes.

### Third-Party Software (Licenses Respected):
- **D3.js** (Graph visualization): **ISC License** (compatible with Apache/MIT).
- **Marked.js** (Markdown parser): **MIT License** (compatible).
- **Python 3** (Logic Engines): **PSF License** (compatible).
- **Node.js / Bun** (Runtime server): **MIT/BSD Licenses** (compatible).

No proprietary or closed-source code (including commercial Obsidian sources) is included in this repository.

---
---

# Vault Omega & Playground (Italiano)
> **Sandbox Sperimentale per Swarm Multi-Agente Agnostici e Memoria Cognitiva Fondata sulla Logica**

---

## 👁️ Visione & Origine del Progetto

**Vault Omega** è un progetto sperimentale nato dal desiderio di fondere la **logica pura della programmazione logica dichiarativa (Prolog-style)** con la potenza predittiva dei **modelli linguistici statistici (LLM)**. 

I moderni agenti di coding (come Claude Code, Cursor, Codex, Antigravity) operano su basi statistiche, il che li rende inclini all'allucinazione, alla deriva del contesto e a consumi esponenziali di token. Vault Omega introduce un'infrastruttura **agnostica, auto-espandibile e deterministica** per governare la memoria collettiva dello sciame e consentire la collaborazione parallela di più agenti autonomi, eliminando la dipendenza da un singolo IDE o provider proprietario.

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
├── README.md                 # Questo documento di onboarding bilingue
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

## 🔧 Installazione Rapida & Automazione Agenti

### Installazione Manuale (Tutte le Piattaforme)
Per avviare il server del playground in locale:
```bash
# 1. Clona la repository
git clone https://github.com/davidealbertazzi97-jpg/OPEN-OMEGA-LOGIC.git

# 2. Entra nella cartella
cd OPEN-OMEGA-LOGIC

# 3. Avvia il server
node playground/server.js
```
La dashboard è ora attiva su `http://localhost:8080`.

### 🤖 Prompt di Automazione Plug-and-Play per Agenti AI (Cross-Platform)
Copia e incolla questo blocco di prompt direttamente nella chat del tuo agente di coding (es. Claude Code, Cursor Agent, Aider, Codex) per fargli installare, configurare e rendere persistente il server del playground ad ogni avvio su **Linux, macOS e Windows**:

````markdown
You are an autonomous AI coding agent. Your goal is to install, configure, and set up the Open-Omega-Logic playground vault on this host, ensuring it runs persistently on every system reboot.

Follow these step-by-step instructions:

1. **Clone the Repository**:
   Clone the repository to a dedicated directory in the user's home directory:
   ```bash
   git clone https://github.com/davidealbertazzi97-jpg/OPEN-OMEGA-LOGIC.git ~/OPEN-OMEGA-LOGIC
   ```

2. **Verify Prerequisites**:
   Check if Node.js (or Bun) and Python 3 are installed on the host. Locate the absolute path of `node` (using `which node` on Unix, or `where node` on Windows).

3. **Initialize the Vault State**:
   Enter the directory and compile the initial vault state:
   ```bash
   cd ~/OPEN-OMEGA-LOGIC
   python3 scripts/token_optimizer.py
   ```

4. **Ensure Cross-Platform Reboot Persistence**:
   Depending on the detected host Operating System, set up automatic persistence:

   - **On Linux**:
     Create `~/.config/systemd/user/omega-playground.service`:
     ```ini
     [Unit]
     Description=Omega Playground Server Daemon
     After=network.target

     [Service]
     ExecStart=<NODE_PATH> <REPO_PATH>/playground/server.js
     Restart=always
     Environment=PORT=8080
     WorkingDirectory=<REPO_PATH>

     [Install]
     WantedBy=default.target
     ```
     Enable and start the service:
     ```bash
     systemctl --user daemon-reload
     systemctl --user enable omega-playground.service
     systemctl --user start omega-playground.service
     ```

   - **On macOS**:
     Create `~/Library/LaunchAgents/com.omega.playground.plist`:
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
     <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>com.omega.playground</string>
         <key>ProgramArguments</key>
         <array>
             <string><NODE_PATH></string>
             <string><REPO_PATH>/playground/server.js</string>
         </array>
         <key>RunAtLoad</key>
         <true/>
         <key>KeepAlive</key>
         <true/>
         <key>WorkingDirectory</key>
         <string><REPO_PATH></string>
     </dict>
     </plist>
     ```
     Load the agent:
     ```bash
     launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.omega.playground.plist
     ```

   - **On Windows**:
     Create a silent startup script `omega-startup.vbs` in the Windows Startup Folder (`shell:startup`):
     ```vbs
     Set WshShell = CreateObject("WScript.Shell")
     WshShell.Run "node """ & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\OPEN-OMEGA-LOGIC\playground\server.js""", 0, False
     ```

5. **Validate Server**:
   Query `http://localhost:8080/api/files` to confirm that the server is up and listening. Report back to the user with the service status.
````

---

## 📜 Licenza & Conformità Open Source

Il progetto Vault Omega è rilasciato sotto la **Licenza Apache 2.0** e la **Licenza MIT**. È utilizzabile liberamente, modificabile e distribuibile sia per scopi privati che commerciali.

### Riferimenti di terze parti (Licenze Rispettate):
1. **D3.js** (Visualizzazione Grafico): Rilasciata sotto **Licenza ISC** (compatibile con Apache/MIT).
2. **Marked.js** (Parser Markdown): Rilasciata sotto **Licenza MIT** (compatibile).
3. **Python 3** (Esecuzione Motori Logici): Rilasciata sotto **Python Software Foundation License** (compatibile).
4. **Node.js / Bun** (Runtime Server): Rilasciate sotto licenze permissive MIT/BSD (compatibili).

Nessun codice proprietario o closed-source (compresi i sorgenti commerciali di Obsidian) è presente in questo repository.
