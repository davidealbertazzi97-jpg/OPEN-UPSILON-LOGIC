---
type: project
status: active
owners: [Lo_Sciame_AI]
tags: [cantiere, progetto, parallelismo]
---
# Template Cantiere

Model note to open a new active project in `CANTIERI/`. Copy this structure, then replace its details.

## Obiettivo
- Concrete output or goal this worksite aims to achieve.

## Stato attuale
- Verified current status (not desired).
- Code, documentation, active branches, and known blockers.

## Perimetro e isolamento
- Nodo memoria: [[Template_Cantiere]]
- Repo/path codice: `/home/user/project-repo`
- Path consentiti: `/home/user/project-repo`, `/home/user/obsidian-vault`
- Path vietati: `/home/user/other-sensitive-repos`
- Git: branch or worktree specifications
- Env/segreti: isolated environments, forbidden reuse of other projects env files
- Runtime: container names, host ports, databases
- Sessioni: prefix `Sessione_YYYY-MM-DD_<ProjectName>_...`

## Lane aperte
| Lane | Owner | Scope | Stato | Bloccante |
| --- | --- | --- | --- | --- |
| product | TBD | Framing, UX, user value | pending | no |
| backend | TBD | APIs, data, test suite | pending | yes |
| frontend | TBD | UI components, flow | pending | no |
| ops | TBD | Deployment, git structure | pending | yes |
| memory | TBD | MOCs, session logs | pending | yes |

## Decisioni
- Irreversible or high-cost decisions.

## Blocchi
- Technical or environment blocks.

## Prossimi passi
- Recommended entry point for the next agent.

## Sessioni collegate
- List chronological sessions related to this project here.

## Protocolli collegati
- [[Protocollo_Isolamento_Cantieri]]
