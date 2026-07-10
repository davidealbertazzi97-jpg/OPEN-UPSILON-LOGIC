---
type: protocol
status: active
priority: mandatory
tags: [protocol, worksites, isolation, routing]
---
# Protocol Worksite Isolation

Mandatory protocol for managing and initiating new software worksites without contaminating code, secrets, environment variables, or global cognitive memory.

## Principle of Isolation
Every project in development must be confined to its own perimeter:
- It has a dedicated descriptor node in `worksites/`.
- It has an absolute path (`repo_path` or `workspace_path`).
- It declares paths that the agent is permitted to access, and forbidden paths.
- It has dedicated environment files (`.env`). Inheriting secrets or configurations from other projects is forbidden.
- It has dedicated HTTP ports, databases, Docker containers, and endpoints to prevent runtime conflicts.

## Minimum Worksite Contract
The `## Perimeter and Isolation` section of every worksite must define:
```text
- Memory Node: [[Worksite_Name]]
- Repo/Path Code: `/home/user/my-project`
- Allowed Paths: `/home/user/my-project`, `/home/user/my-vault`
- Forbidden Paths: Folders of other sensitive projects
- Git: Dedicated branch or worktree
- Env/Secrets: Dedicated environment files (e.g. .env.local)
- Runtime: Host ports, databases, and containers
- Sessions: Prefix `Session_YYYY-MM-DD_<WorksiteSlug>_...`
```

## Operational Rules for Agents
All prompts provided to swarm agents must include:
1. Exact `WORKDIR` (working directory).
2. List of allowed and forbidden paths.
3. Absolute prohibition of automated scans (e.g. `find` or `grep`) outside allowed paths.
4. Obligation to show the Git diff and fill in the `FINAL REPORT` section before task completion.

---
[[MOC_Protocols]] | [[MOC_Worksites]]
