---
type: protocol
status: active
tags: [protocol, swarm, orchestration]
---
# Protocol Swarm Orchestration

This protocol describes how the orchestrator agent coordinates delegated agents (external lanes) to execute bounded tasks within active worksites.

## Principle of Delegation
The lead agent acts as an orchestrator, maintaining strategic vision, code reviews, and final synthesis, while delegating executive tasks to specialized agent slots:
- **`gemini`**: Specialized in visual polishing, UX, copy, and frontend reviews.
- **`goose`**: Used for system diagnostics, low-level operations, and isolated experiments.
- **`opencode`**: Used for exploration, writing documentation, and running smoke tests.
- **`codex`**: Specialized in rigorous structural changes, backend refactoring, and security patches.
- **`copilot`**: Integrated with native GitHub workflows (Issues, PRs, pushes).
- **`cursor`**: Used as an alternative lane for interactive programming and resolving IDE issues.

## Swarm Workflow
1. **Planning and Selection**: The orchestrator analyzes the task and requests a recommendation:
   ```bash
   python3 scripts/swarm_orchestrator.py recommend --task "Write integration tests for login endpoint"
   ```
2. **Dispatch**: Start the dedicated worker on the worksite repository in background or foreground mode:
   ```bash
   python3 scripts/swarm_orchestrator.py dispatch --agent codex --project /home/user/my-project --task "Write login tests"
   ```
3. **Execution and Logging**: The worker runs the agent inside the sandbox/host, writing stdout to `agent.log` inside the run directory (`dump/swarm_runs/run-YYYYMMDD-.../`).
4. **Validation and Closure**: Before completing the task, the delegated agent MUST run a self-review (reread modifications, fix issues) and print a `FINAL REPORT`.
5. **Takeover**: The orchestrator performs the code review, runs memory guardrails, and accepts the work.

---
[[MOC_Protocols]] | [[MOC_Worksites]]
