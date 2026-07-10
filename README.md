# Vault Upsilon & Playground
> **A Logical Agentic Memory Vault & Swarm Orchestrator — Upgrading Karpathy's LLM-Wiki Model with Prolog-Style Guardrails**

---

## 👁️ Vision & Origin of the Project

**Vault Upsilon** is an open-source framework designed to address the core limitations of modern autonomous coding agents (such as Claude Code, Cursor, Codex, Gemini, and Antigravity). While these systems excel at code generation, they operate on statistical probabilities, making them inherently prone to context drift, exponential token waste, and hallucinations. 

### Upgrading the Karpathy LLM-Wiki Model
In Andrej Karpathy's vision, an LLM-centric OS uses a structured wiki-style memory layout where agents navigate via semantic links instead of raw directory listings. **Vault Upsilon directly upgrades and supercharges Karpathy's LLM-wiki model**. 

We overlay this semantic graph with a **deterministic, Prolog-style logical checker**. This logic layer acts as rigid **logical tracks (binari logici)**, channeling the statistical noise of the LLM into a bounded, verifiable path. If an agent tries to hallucinate or violate repository boundaries, the logic validator flags the conflict, forcing compliance before a task can be finalized.

### Homelab Heritage & Swarm Control
This project is not a theoretical prototype. It was born out of a real-world multi-agent setup **created months ago and run daily in a private homelab** to manage coding tasks. It features:
*   **Logical Agentic Memory**: A self-correcting memory structure that prevents context pollution.
*   **Swarm Agent Orchestration**: A native orchestrator that allows a lead agent to dispatch, monitor, and coordinate sub-agents in parallel slots.

---

## 🚀 Core Goals

1. **Drastic Reduction of Hallucinations**: By checking files against a deterministic logical engine, agents are guided along logical tracks. An agent cannot declare a task complete unless the repository satisfies the strict validation contract.
2. **Context Savings (Token Optimizer)**: Reducing up to 95% of tokens wasted in exploratory file scans, thanks to the dynamic compilation of the active state into a single compressed file (`context_summary.md`).
3. **Parallel Multi-Agent Swarming**: Natively integrates a swarm orchestrator to dispatch, recommend, and route tasks to specialized sub-agents (`gemini`, `goose`, `opencode`, `codex`, `copilot`, `cursor`).
4. **IDE & Provider Agnostic**: A decentralized infrastructure running locally, accessible via standard filesystem, REST API, or MCP (Model Context Protocol).
5. **Autonomous Logical Self-Expansion**: Agents themselves can write new protocols and modify Python validation scripts to introduce new rules that apply to all future swarm runs.

---

## 📁 Archive & Vault Structure

The vault is structured as a cognitive graph based on **WikiLinks (`[[Link]]`)** and divided into specific compartments:

```text
├── .gitignore
├── LICENSE                   # Apache 2.0 / MIT License
├── README.md                 # This bilingual documentation
├── context_summary.md        # Compiled token-saving state summary (~150 tokens)
├── indices/                   # Maps of Content (MOC) for semantic navigation
│   ├── MOC_Architecture.md   # Grafo and topology of the vault
│   ├── MOC_Worksites.md       # Active worksites registry
│   ├── MOC_Projects.md       # Long-term stable/system projects index
│   ├── MOC_Protocols.md     # Guides and execution protocols registry
│   └── MOC_Sessions.md       # Chronological session handoff logs index
├── progetti/                 # stable system projects notes
├── worksites/                 # Active high-iteration worksites
│   ├── README.md             # Worksite sandbox isolation guidelines
│   └── Template_Worksite.md  # Template for initiating a new worksite
├── sessions/                 # Chronological handoff notes
├── protocols/      # Reusable execution protocols and guides
├── knowledge_base/    # Stable knowledge base (e.g. Agent_Integration.md)
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
- **Worksite Contract**: Every file in `worksites/` must have frontmatter `type: project`, status, and standard headings (`## Obiettivo`, `## Perimetro`, `## Lane`, `## Prossimi passi`).
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

## 🖥️ Web UI: Upsilon Playground

The **Upsilon Playground** is a **dependency-free, open-source** local web application located in `playground/`.

```text
+-----------------------------------------------------------------------------+
|                            Upsilon Playground Web UI                          |
+----------------------+------------------------------+-----------------------+
|  [Sidebar]           |  [Markdown Editor]           |  [D3 WikiLink Graph]  |
|  - indices/           |                              |                       |
|  - progetti/         |  Edit note contents          |  Visualizes floating  |
|  - worksites/         |  & write double-click        |  nodes. Click to      |
|  - sessions/         |  [[WikiLinks]]               |  navigate notes.      |
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
git clone https://github.com/davidealbertazzi97-jpg/OPEN-UPSILON-LOGIC.git

# 2. Enter the folder
cd OPEN-UPSILON-LOGIC

# 3. Launch the server
node playground/server.js
```
The dashboard is now running at `http://localhost:8080`.

### 🤖 Plug-and-Play Agent Automation Prompt (Cross-Platform)
Copy and paste this single prompt block directly into your AI coding agent (e.g. Claude Code, Cursor Agent, Aider, Codex) to let it automatically install, configure, and persist the playground server across reboots on **Linux, macOS, and Windows**:

````markdown
You are an autonomous AI coding agent. Your goal is to install, configure, and set up the Open-Upsilon-Logic playground vault on this host, ensuring it runs persistently on every system reboot.

Follow these step-by-step instructions:

1. **Clone the Repository**:
   Clone the repository to a dedicated directory in the user's home directory:
   ```bash
   git clone https://github.com/davidealbertazzi97-jpg/OPEN-UPSILON-LOGIC.git ~/OPEN-UPSILON-LOGIC
   ```

2. **Verify Prerequisites**:
   Check if Node.js (or Bun) and Python 3 are installed on the host. Locate the absolute path of `node` (using `which node` on Unix, or `where node` on Windows).

3. **Initialize the Vault State**:
   Enter the directory and compile the initial vault state:
   ```bash
   cd ~/OPEN-UPSILON-LOGIC
   python3 scripts/token_optimizer.py
   ```

4. **Ensure Cross-Platform Reboot Persistence**:
   Depending on the detected host Operating System, set up automatic persistence:

   - **On Linux**:
     Create `~/.config/systemd/user/upsilon-playground.service`:
     ```ini
     [Unit]
     Description=Upsilon Playground Server Daemon
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
     systemctl --user enable upsilon-playground.service
     systemctl --user start upsilon-playground.service
     ```

   - **On macOS**:
     Create `~/Library/LaunchAgents/com.upsilon.playground.plist`:
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
     <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>com.upsilon.playground</string>
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
     launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.upsilon.playground.plist
     ```

   - **On Windows**:
     Create a silent startup script `upsilon-startup.vbs` in the Windows Startup Folder (`shell:startup`):
     ```vbs
     Set WshShell = CreateObject("WScript.Shell")
     WshShell.Run "node """ & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\OPEN-UPSILON-LOGIC\playground\server.js""", 0, False
     ```

5. **Validate Server**:
   Query `http://localhost:8080/api/files` to confirm that the server is up and listening. Report back to the user with the service status.
````

---

## ⚠️ Disclaimer & Warranty
This is an experimental, proof-of-concept project. While it has been designed to reduce hallucinations, save tokens, and coordinate multiple agents, **we cannot guarantee 100% that it will always work perfectly, remain bug-free, or be compatible with all future LLM client changes**. 

The software is provided **"as is"**, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability.

## 🏆 What We Have Achieved (Results)
- **Deterministic Guardrails**: Built a Prolog-style Python logic validator that strictly prevents workspace structural decay.
- **Context Consolidation**: Achieved up to 95% token savings (from ~4000+ down to ~150 tokens) per turn by compiling active states.
- **Multi-Agent Orchestration**: Successfully tested local parallel runs using 6 separate agent engines on different platforms.
- **Zero-Dependency Web Portal**: Created a beautiful visual node-link and editor dashboard with zero node_modules.

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

# Vault Upsilon & Playground (Italiano)
> **Una Memoria Agentica Logica & Swarm Orchestrator — Un potenziamento del modello LLM-Wiki di Karpathy tramite Guardrail in stile Prolog**

---

## 👁️ Visione & Origine del Progetto

**Vault Upsilon** è un framework open-source progettato per superare i limiti strutturali dei moderni agenti autonomi di coding (come Claude Code, Cursor, Codex, Gemini e Antigravity). Sebbene questi sistemi siano eccellenti nella generazione di codice, essi operano su basi puramente statistiche, rendendoli inclini alla deriva del contesto, al consumo esponenziale di token e alle allucinazioni.

### Potenziare il modello LLM-Wiki di Karpathy
Nella visione originale di Andrej Karpathy, un sistema operativo basato su LLM (LLM-as-OS) trae beneficio da un'infrastruttura di memoria strutturata a wiki, dove gli agenti navigano tramite link semantici anziché scansionare ciecamente il filesystem. **Vault Upsilon evolve direttamente il modello LLM-wiki di Karpathy**.

Abbiamo sovrapposto a questo grafo semantico un **validatore logico deterministico ispirato a Prolog**. Questo livello logico agisce come veri e propri **binari logici**, incanalando il rumore statistico dei modelli linguistici all'interno di un percorso ordinato e verificabile. Se un agente tenta di allucinare o violare i vincoli del repository, il validatore solleva un conflitto bloccante, costringendolo a correggersi prima di completare il lavoro.

### L'Origine nel mio Homelab & Controllo Swarm
Questo progetto non è un prototipo teorico. Nasce da un setup reale multi-agente **creato mesi fa e utilizzato quotidianamente nel mio homelab personale** per gestire e coordinare i lavori di programmazione dello sciame. Offre:
*   **Memoria Agentica Logica**: Una struttura a grafo auto-correttiva che impedisce la contaminazione del contesto.
*   **Orchestra Swarm Nativo**: Uno script che permette a un agente principale di istruire, monitorare e coordinare in parallelo più agenti delegati.

---

## 🚀 Obiettivi Fondamentali

1. **Riduzione Drastica delle Allucinazioni**: Guidando l'agente lungo binari logici deterministici. Un agente non può dichiarare un compito completato se non soddisfa il contratto strutturale del vault.
2. **Risparmio del Contesto (Token Saving)**: Riduzione fino al 95% dei token sprecati in letture esplorative del filesystem, grazie alla compilazione dinamica dello stato attivo in un singolo file compresso (`context_summary.md`).
3. **Collaborazione e Swarm Multi-Agente**: Integra nativamente un orchestratore per raccomandare, delegare e instradare i compiti a corsie di agenti specializzate (`gemini`, `goose`, `opencode`, `codex`, `copilot`, `cursor`).
4. **Indipendenza da IDE e Provider (Agnostico)**: Un'infrastruttura decentralizzata che gira in locale sulla macchina, accessibile tramite filesystem, REST API o protocollo MCP.
5. **Autonomia Logica e Auto-Espansione (Self-Expanding Mind)**: Gli agenti stessi possono scrivere nuovi protocolli e modificare i file di verifica logica Python per introdurre nuove regole che si applicheranno a tutti i futuri agenti dello sciame.

---

## 📁 Architettura & Struttura del Vault

Il vault è strutturato come un grafo cognitivo basato su **WikiLinks (`[[Link]]`)** e diviso in compartimenti specifici:

```text
├── .gitignore
├── LICENSE                   # Licenza Apache 2.0 / MIT
├── README.md                 # Questo documento di onboarding bilingue
├── context_summary.md        # Sommario compresso compilato (~150 token)
├── indices/                   # Mappe dei Contenuti (MOC) per la navigazione semantica
│   ├── MOC_Architecture.md   # Grafo e topology del vault
│   ├── MOC_Worksites.md       # Tracciatore dei progetti in sviluppo attivo
│   ├── MOC_Projects.md       # Indice dei progetti stabili di sistema
│   ├── MOC_Protocols.md     # Indice delle guide e dei processi
│   └── MOC_Sessions.md       # Indice cronologico dei log di sessione
├── progetti/                 # Schede descrittive dei progetti stabili
├── worksites/                 # Cartelle di lavoro attivo ad alta iterazione
│   ├── README.md             # Regole per l'isolamento dei cantieri
│   └── Template_Worksite.md  # Modello per avviare un nuovo cantiere
├── sessions/                 # Log di handoff che descrivono stato finale e prossimi passi
├── protocols/      # Guide operative e protocolli riutilizzabili
├── knowledge_base/    # KB stabile (es: Agent_Integration.md)
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
Funge da motore di inferenza Prolog-style. Mappa le note markdown come predicati logici (es: `worksite(id, status)`, `session(id, project)`) e verifica che le regole di coerenza siano soddisfatte:
- **Nessuna nota orfana**: Qualsiasi file markdown (fuori da sessioni e dump) deve essere linkato da almeno un MOC.
- **Contratto del Cantiere**: Ogni file in `worksites/` deve avere frontmatter `type: project` e contenere le intestazioni standard in inglese (`## Objective`, `## Current State`, `## Perimeter and Isolation`, `## Open Lanes`, `## Next Steps`, `## Linked Sessions`).
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

## 🖥️ La Web UI: Upsilon Playground

Il modulo **Upsilon Playground** è un'interfaccia web di cantiere interamente **open-source e dependency-free** situata in **`playground/`**.

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
git clone https://github.com/davidealbertazzi97-jpg/OPEN-UPSILON-LOGIC.git

# 2. Entra nella cartella
cd OPEN-UPSILON-LOGIC

# 3. Avvia il server
node playground/server.js
```
La dashboard è ora attiva su `http://localhost:8080`.

### 🤖 Prompt di Automazione Plug-and-Play per Agenti AI (Cross-Platform)
Copia e incolla questo blocco di prompt direttamente nella chat del tuo agente di coding (es. Claude Code, Cursor Agent, Aider, Codex) per fargli installare, configurare e rendere persistente il server del playground ad ogni avvio su **Linux, macOS e Windows**:

````markdown
You are an autonomous AI coding agent. Your goal is to install, configure, and set up the Open-Upsilon-Logic playground vault on this host, ensuring it runs persistently on every system reboot.

Follow these step-by-step instructions:

1. **Clone the Repository**:
   Clone the repository to a dedicated directory in the user's home directory:
   ```bash
   git clone https://github.com/davidealbertazzi97-jpg/OPEN-UPSILON-LOGIC.git ~/OPEN-UPSILON-LOGIC
   ```

2. **Verify Prerequisites**:
   Check if Node.js (or Bun) and Python 3 are installed on the host. Locate the absolute path of `node` (using `which node` on Unix, or `where node` on Windows).

3. **Initialize the Vault State**:
   Enter the directory and compile the initial vault state:
   ```bash
   cd ~/OPEN-UPSILON-LOGIC
   python3 scripts/token_optimizer.py
   ```

4. **Ensure Cross-Platform Reboot Persistence**:
   Depending on the detected host Operating System, set up automatic persistence:

   - **On Linux**:
     Create `~/.config/systemd/user/upsilon-playground.service`:
     ```ini
     [Unit]
     Description=Upsilon Playground Server Daemon
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
     systemctl --user enable upsilon-playground.service
     systemctl --user start upsilon-playground.service
     ```

   - **On macOS**:
     Create `~/Library/LaunchAgents/com.upsilon.playground.plist`:
     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
     <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>com.upsilon.playground</string>
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
     launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.upsilon.playground.plist
     ```

   - **On Windows**:
     Create a silent startup script `upsilon-startup.vbs` in the Windows Startup Folder (`shell:startup`):
     ```vbs
     Set WshShell = CreateObject("WScript.Shell")
     WshShell.Run "node """ & WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\OPEN-UPSILON-LOGIC\playground\server.js""", 0, False
     ```

5. **Validate Server**:
   Query `http://localhost:8080/api/files` to confirm that the server is up and listening. Report back to the user with the service status.
````

---

## ⚠️ Disclaimer & Limitazione di Garanzia
Questo è un progetto sperimentale e concettuale (proof-of-concept). Sebbene sia stato progettato per ridurre le allucinazioni, risparmiare token e coordinare più agenti in parallelo, **non possiamo garantire al 100% che funzioni sempre in modo perfetto, esente da bug o compatibile con tutti i futuri aggiornamenti dei client LLM**.

Il software viene fornito **"così com'è"**, senza garanzie di alcun tipo, esplicite o implicite. In nessun caso gli autori o i titolari del copyright saranno responsabili per eventuali reclami, danni o altre responsabilità derivanti dall'uso di questo software.

## 🏆 Risultati Ottenuti (Cosa Abbiamo Realizzato)
- **Guardrail Deterministici**: Creato un validatore logico Python in stile Prolog per prevenire la disorganizzazione dello spazio di lavoro.
- **Consolidamento del Contesto**: Raggiunto fino al 95% di risparmio sui token di contesto (da 4000+ a ~150 token per turno) tramite compilazione dinamica degli stati attivi.
- **Orchestrazione Multilivello**: Testate con successo le corse in parallelo di 6 diversi motori di agenti locali.
- **Dashboard Leggera a Zero Dipendenze**: Sviluppato un portale grafico interattivo di modifica e visualizzazione dei WikiLink senza moduli NPM di terze parti sul server.

---

## 📜 Licenza & Conformità Open Source

Il progetto Vault Upsilon è rilasciato sotto la **Licenza Apache 2.0** e la **Licenza MIT**. È utilizzabile liberamente, modificabile e distribuibile sia per scopi privati che commerciali.

### Riferimenti di terze parti (Licenze Rispettate):
1. **D3.js** (Visualizzazione Grafico): Rilasciata sotto **Licenza ISC** (compatibile con Apache/MIT).
2. **Marked.js** (Parser Markdown): Rilasciata sotto **Licenza MIT** (compatibile).
3. **Python 3** (Esecuzione Motori Logici): Rilasciata sotto **Python Software Foundation License** (compatibile).
4. **Node.js / Bun** (Runtime Server): Rilasciate sotto licenze permissive MIT/BSD (compatibili).

Nessun codice proprietario o closed-source (compresi i sorgenti commerciali di Obsidian) è presente in questo repository.
