---
type: project
status: active
owners: [Swarm_AI]
tags: [worksite, project, parallel]
---
# Template Worksite

Model note to open a new active project in `worksites/`. Copy this structure, then replace its details.

## Objective
- Concrete output or goal this worksite aims to achieve.

## Current State
- Verified current status (not desired).
- Code, documentation, active branches, and known blockers.

## Perimeter and Isolation
- Memory Node: [[Template_Worksite]]
- Repo/Path Code: `/home/user/project-repo`
- Allowed Paths: `/home/user/project-repo`, `/home/user/vault`
- Forbidden Paths: `/home/user/other-sensitive-repos`
- Git: branch or worktree specifications
- Env/Secrets: isolated environments, forbidden reuse of other projects env files
- Runtime: container names, host ports, databases
- Sessions: prefix `Session_YYYY-MM-DD_<ProjectName>_...`

## Open Lanes
| Lane | Owner | Scope | Status | Blocker |
| --- | --- | --- | --- | --- |
| product | TBD | Framing, UX, user value | pending | no |
| backend | TBD | APIs, data, test suite | pending | yes |
| frontend | TBD | UI components, flow | pending | no |
| ops | TBD | Deployment, git structure | pending | yes |
| memory | TBD | MOCs, session logs | pending | yes |

## Decisions
- Irreversible or high-cost decisions.

## Blockers
- Technical or environment blocks.

## Next Steps
- Recommended entry point for the next agent.

## Linked Sessions
- List chronological sessions related to this project here.

## Linked Protocols
- [[Protocol_Worksite_Isolation]]
