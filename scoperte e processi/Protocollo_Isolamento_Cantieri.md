---
type: protocol
status: active
priority: mandatory
tags: [protocollo, cantieri, isolamento, routing]
---
# Protocollo Isolamento Cantieri

Protocollo obbligatorio per gestire e aprire nuovi cantieri software senza contaminare codice, segreti, variabili d'ambiente o la memoria operativa globale.

## Principio di Isolamento
Ogni progetto in sviluppo deve essere confinato nel proprio perimetro:
- Ha un nodo descrittore dedicato in `CANTIERI/`.
- Ha un percorso assoluto (`repo_path` o `workspace_path`).
- Dichiara i percorsi a cui l'agente ha accesso consentito e quelli vietati.
- Ha file di ambiente (`.env`) dedicati. È vietato ereditare segreti o configurazioni da altri progetti.
- Ha porte HTTP, database, container Docker ed endpoint dedicati per evitare conflitti a runtime.

## Contratto Minimo di un Cantiere
La sezione `## Perimetro e isolamento` di ogni cantiere deve obbligatoriamente definire:
```text
- Nodo memoria: [[Nome_Cantiere]]
- Repo/path codice: `/home/user/my-project`
- Path consentiti: `/home/user/my-project`, `/home/user/my-obsidian-vault`
- Path vietati: cartelle di altri progetti sensibili
- Git: branch o worktree dedicati
- Env/segreti: file env dedicati (es: .env.local)
- Runtime: porte host, database e container
- Sessioni: prefisso `Sessione_YYYY-MM-DD_<CantiereSlug>_...`
```

## Regole Operative per gli Agenti
Tutti i prompt forniti ad agenti dello sciame devono includere:
1. `WORKDIR` (directory di lavoro) preciso.
2. Elenco dei percorsi consentiti e vietati.
3. Divieto assoluto di scansione automatica (es: `find` o `grep`) al di fuori dei percorsi consentiti.
4. Obbligo di mostrare il diff di Git e compilare la sezione `FINAL REPORT` prima del completamento del task.

---
[[MOC_Protocolli]] | [[MOC_Cantieri]]
