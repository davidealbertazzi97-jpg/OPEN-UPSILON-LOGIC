#!/usr/bin/env python3
"""Swarm Orchestrator: CLI tool to recommendation, dispatch, and monitor agent runs.
Adapted from the local swarm orchestrator to be portable and integration-friendly.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Resolve paths dynamically relative to the script location
ROOT = Path(__file__).resolve().parent
VAULT = ROOT.parent
RUNS_DIR = VAULT / "dump" / "swarm_runs"
CONFIG_PATH = ROOT / "agents.json"
DEFAULT_TIMEOUT_MINUTES = 45
VAULT_GUARDRAILS = ROOT / "vault_guardrails.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    chars = []
    for ch in value.lower():
        if ch.isalnum():
            chars.append(ch)
        else:
            chars.append("-")
    result = "".join(chars)
    while "--" in result:
        result = result.replace("--", "-")
    return result.strip("-")[:48] or "task"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {"agents": {}}
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_layout() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def list_run_dirs() -> list[Path]:
    if not RUNS_DIR.exists():
        return []
    return sorted([path for path in RUNS_DIR.iterdir() if path.is_dir()], reverse=True)


def load_metadata(run_dir: Path) -> dict[str, Any]:
    return read_json(run_dir / "metadata.json")


def evaluate_run_log(log_path: Path) -> tuple[str, list[str]]:
    if not log_path.exists():
        return "failed", ["missing log output"]

    raw_text = log_path.read_text(encoding="utf-8", errors="replace")
    if "[swarm] agent_output_begin\n" in raw_text:
        log_text = raw_text.split("[swarm] agent_output_begin\n", 1)[1]
    else:
        log_lines = raw_text.splitlines()
        agent_lines = [line for line in log_lines if not line.startswith("[swarm] command=")]
        log_text = "\n".join(agent_lines)
    log_lc = log_text.lower()
    issues: list[str] = []

    if "final report" not in log_lc:
        issues.append("missing FINAL REPORT section")
    if "self_review" not in log_lc:
        issues.append("missing self_review field in FINAL REPORT")

    for required_field in ("reread_files", "issues_found", "fixes_applied", "debug_validation"):
        if required_field not in log_lc:
            issues.append(f"missing self_review detail: {required_field}")

    if issues:
        return "needs_review", issues
    return "ok", []


def run_memory_guardrails() -> tuple[str, list[str], list[dict[str, Any]]]:
    checks: list[tuple[str, list[str], Path]] = []
    if VAULT_GUARDRAILS.exists():
        checks.append(
            (
                "vault_guardrails",
                [str(VAULT_GUARDRAILS), "--strict"],
                VAULT_GUARDRAILS.parent,
            )
        )
    else:
        return "needs_review", [f"missing memory guardrail script: {VAULT_GUARDRAILS}"], []

    issues: list[str] = []
    details: list[dict[str, Any]] = []
    for name, command, cwd in checks:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except FileNotFoundError as exc:
            issues.append(f"{name}: missing executable: {exc.filename}")
            details.append({"name": name, "returncode": 127, "output": str(exc)})
            continue
        except subprocess.TimeoutExpired:
            issues.append(f"{name}: timeout")
            details.append({"name": name, "returncode": 124, "output": "timeout"})
            continue

        output = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part and part.strip()
        )
        details.append({"name": name, "returncode": completed.returncode, "output": output})
        if completed.returncode != 0:
            issues.append(f"{name}: exit {completed.returncode}")

    return ("needs_review" if issues else "ok"), issues, details


def detect_python_command(project: Path) -> str:
    venv_python = project / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return "python3"


def lane_runtime_notes(agent: str, project: Path) -> list[str]:
    notes: list[str] = []
    python_cmd = detect_python_command(project)
    notes.append(f"Use `{python_cmd}` for Python commands. Do not assume plain `python` exists.")
    notes.append("Stay inside the project path unless the prompt explicitly grants another path.")
    notes.append("If a command fails because of a missing executable, retry once with the explicit interpreter or tool path before declaring a blocker.")
    if agent == "gemini":
        notes.append("Do not try to read the shared vault or files outside the project unless summarized in the prompt.")
        notes.append("Prefer short repository-only tasks and close with a concise FINAL REPORT.")
    if agent == "opencode":
        notes.append("When running tests, prefer the project's virtualenv first, then fall back to `python3` only if the virtualenv is absent.")
        notes.append("Avoid broad scouting once the target files are identified; make the bounded change, verify it, then close.")
    if agent == "goose":
        notes.append("If the lane depends on an external provider or quota and it is unavailable, stop quickly and report the exact blocker.")
    if agent == "copilot":
        notes.append("Use GitHub-native issue, pull request, and repository context only when the task needs it.")
    if agent == "cursor":
        notes.append("Use Cursor Agent as an alternate implementation lane; it consumes the signed-in Cursor account usage.")
    return notes


def prompt_template(agent: str, project: Path, task: str, label: str | None, extra: str | None) -> str:
    heading = f"Task label: {label}" if label else "Task label: none"
    runtime_block = "\n".join(f"- {note}" for note in lane_runtime_notes(agent, project))
    extra_text = extra.strip() if extra else ""
    extra_parts = [runtime_block]
    if extra_text:
        extra_parts.append(extra_text)
    extra_block = "\n".join(part for part in extra_parts if part).strip()
    return textwrap.dedent(
        f"""\
        You are being launched as a delegated agent inside a local swarm runner.

        Agent slot: {agent}
        Project path: {project}
        {heading}

        Primary task:
        {task}

        Operating rules:
        - Work inside the project path above.
        - Respect any AGENTS.md or local repo instructions if present.
        - Treat the instructions in `Extra instructions` below as hard requirements, not suggestions.
        - Do not revert unrelated existing changes.
        - Prefer concrete progress over long analysis, but do not guess when the code disproves you.
        - If you modify code, say exactly which files changed.
        - If you run tests or verification, report exactly what passed or failed.
        - If you hit a blocker, try one concrete recovery step, then either continue or report the blocker precisely in FINAL REPORT.
        - If you write or edit code, before concluding you must reread your own changes, review them critically, fix defects you notice, and run focused debugging/verification on what you just wrote.
        - Treat self-review as mandatory completion work, not as an optional suggestion.
        - End with a section titled FINAL REPORT.
        - In FINAL REPORT include:
          - outcome
          - files_changed
          - verification
          - self_review
          - self_review.reread_files
          - self_review.issues_found
          - self_review.fixes_applied
          - self_review.debug_validation
          - open_risks
          - next_best_step

        Mandatory completion workflow:
        1. Execute the assigned task.
        2. If you changed code, reread the files you changed and actively look for bugs, regressions, missing imports, syntax problems, broken assumptions, and edge cases.
        3. Fix any issue you find in your own fresh code before stopping.
        4. Run targeted debugging or verification for the changed area and report the result precisely.
        5. Only then write FINAL REPORT, including the self_review details listed above.

        Handoff requirement:
        Another agent may need to take over from your stdout log alone. Be explicit.

        Extra instructions:
        {extra_block}
        """
    )


@dataclass
class AgentSpec:
    name: str
    label: str
    role: str
    command: str
    defaults: dict[str, Any]


def get_agent_spec(name: str) -> AgentSpec:
    config = load_config()
    agents = config.get("agents", {})
    payload = agents.get(name)
    if not payload:
        raise SystemExit(f"Unknown agent: {name}")
    return AgentSpec(
        name=name,
        label=payload["label"],
        role=payload["role"],
        command=payload["command"],
        defaults=payload.get("defaults", {}),
    )


def build_command(agent: AgentSpec, project: Path, prompt: str, timeout_minutes: int) -> list[str]:
    if agent.name == "gemini":
        return [
            agent.command,
            "--prompt",
            prompt,
            "--skip-trust",
            "--yolo",
            "--output-format",
            "text",
        ]
    if agent.name == "goose":
        return [
            agent.command,
            "run",
            "--text",
            prompt,
            "--no-session",
            "--quiet",
            "--output-format",
            "text",
            "--max-turns",
            "100",
        ]
    if agent.name == "opencode":
        return [
            agent.command,
            "run",
            "--dir",
            str(project),
            "--dangerously-skip-permissions",
            "--format",
            "default",
            prompt,
        ]
    if agent.name == "codex":
        return [
            agent.command,
            "exec",
            "-C",
            str(project),
            "--dangerously-bypass-approvals-and-sandbox",
            "-s",
            "workspace-write",
            "--skip-git-repo-check",
            "--color",
            "never",
            prompt,
        ]
    if agent.name == "copilot":
        return [
            agent.command,
            "-C",
            str(project),
            "-p",
            prompt,
            "--allow-all",
            "--no-color",
            "--output-format",
            "text",
        ]
    if agent.name == "cursor":
        return [
            agent.command,
            "--workspace",
            str(project),
            "--trust",
            "--print",
            "--output-format",
            "text",
            "--force",
            prompt,
        ]
    raise SystemExit(f"No command builder configured for agent: {agent.name}")


def build_agent_env(project: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    env.setdefault("CLICOLOR", "0")
    env.setdefault("TERM", "dumb")

    venv_bin = project / ".venv" / "bin"
    venv_python = venv_bin / "python"
    python_cmd = str(venv_python) if venv_python.exists() else "python3"
    if venv_bin.exists():
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
        env["VIRTUAL_ENV"] = str(project / ".venv")
    env["PYTHON"] = python_cmd
    env["PYTHON3"] = python_cmd
    env["SWARM_PROJECT"] = str(project)
    return env


def run_probe(command: list[str], timeout: int = 12) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return False, f"missing executable: {command[0]}"
    except subprocess.TimeoutExpired:
        return False, f"timeout while probing: {shlex.join(command)}"

    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    if result.returncode == 0:
        return True, output or "ok"
    return False, output or f"exit code {result.returncode}"


def check_agent_readiness(agent_name: str) -> tuple[str, list[str]]:
    spec = get_agent_spec(agent_name)
    issues: list[str] = []

    executable = shutil.which(spec.command)
    if not executable:
        return "blocked", [f"command not found: {spec.command}"]

    details = [f"command={executable}"]
    if agent_name == "copilot":
        ok, version_output = run_probe([spec.command, "--version"])
        details.append(f"copilot_version={version_output.splitlines()[0] if version_output else 'unknown'}")
        if not ok:
            issues.append(f"copilot version check failed: {version_output}")

        gh_path = shutil.which("gh")
        if not gh_path:
            issues.append("GitHub CLI `gh` not found; Copilot auth status cannot be checked")
        else:
            ok, auth_output = run_probe(["gh", "auth", "status"])
            if not ok:
                issues.append(f"GitHub auth blocked: {auth_output}")
            else:
                details.append("github_auth=ok")
    if agent_name == "cursor":
        ok, version_output = run_probe([spec.command, "--version"])
        details.append(f"cursor_version={version_output.splitlines()[0] if version_output else 'unknown'}")
        if not ok:
            issues.append(f"cursor version check failed: {version_output}")

        ok, status_output = run_probe([spec.command, "status"])
        status_summary = status_output.splitlines()[0] if status_output else "unknown"
        details.append(f"cursor_auth={status_summary}")
        if not ok or "not logged in" in status_output.lower():
            issues.append(f"Cursor auth blocked: {status_output}")

    return ("ready" if not issues else "blocked"), details + issues


def record_worker_failure(run_dir: Path, metadata: dict[str, Any], reason: str) -> None:
    completed_at = now_utc()
    result = {
        "run_id": metadata["run_id"],
        "agent": metadata["agent"],
        "project": metadata["project"],
        "returncode": metadata.get("returncode", 1),
        "timed_out": metadata.get("timed_out", False),
        "completed_at": completed_at,
        "status": "failed",
        "log_path": str(run_dir / "agent.log"),
        "compliance_issues": [reason],
    }
    write_json(run_dir / "result.json", result)
    metadata["state"] = "failed"
    metadata["completed_at"] = completed_at
    metadata.setdefault("compliance_issues", []).append(reason)
    write_json(run_dir / "metadata.json", metadata)


def recommend_agents(task: str, top_n: int) -> list[tuple[str, int, list[str]]]:
    task_lc = task.lower()
    config = load_config()
    scores: dict[str, int] = {name: 0 for name in config.get("agents", {})}
    reasons: dict[str, list[str]] = {name: [] for name in scores}

    keyword_map = {
        "gemini": [
            ("ui", 4, "ui keyword"),
            ("ux", 4, "ux keyword"),
            ("copy", 3, "copy keyword"),
            ("frontend", 4, "frontend keyword"),
            ("hero", 2, "hero keyword"),
            ("polish", 4, "polish keyword"),
            ("design", 3, "design keyword"),
        ],
        "codex": [
            ("bug", 3, "bug keyword"),
            ("fix", 3, "fix keyword"),
            ("review", 5, "review keyword"),
            ("audit", 5, "audit keyword"),
            ("refactor", 3, "refactor keyword"),
            ("migration", 3, "migration keyword"),
            ("backend", 3, "backend keyword"),
            ("auth", 4, "auth keyword"),
            ("security", 5, "security keyword"),
        ],
        "goose": [
            ("ops", 4, "ops keyword"),
            ("diagnostic", 3, "diagnostic keyword"),
            ("experiment", 4, "experiment keyword"),
            ("cli", 3, "cli keyword"),
            ("alternate", 2, "alternate path"),
        ],
        "opencode": [
            ("docs", 4, "docs keyword"),
            ("documentation", 4, "documentation keyword"),
            ("explore", 3, "exploration keyword"),
            ("research", 3, "research keyword"),
            ("smoke", 2, "smoke keyword"),
            ("quick", 2, "quick implementation"),
        ],
        "copilot": [
            ("github", 5, "github workflow keyword"),
            ("issue", 4, "issue keyword"),
            ("pr", 4, "pull request keyword"),
            ("pull request", 5, "pull request keyword"),
            ("copilot", 5, "explicit copilot keyword"),
            ("agent", 2, "agent keyword"),
        ],
        "cursor": [
            ("cursor", 7, "explicit cursor keyword"),
            ("agent", 2, "agent keyword"),
            ("model", 2, "model comparison keyword"),
            ("alternative", 2, "alternative lane keyword"),
            ("review", 2, "review keyword"),
        ],
    }

    for agent, rules in keyword_map.items():
        if agent not in scores:
            continue
        for needle, score, reason in rules:
            if needle in task_lc:
                scores[agent] += score
                reasons[agent].append(reason)

    if not any(scores.values()) and scores:
        fallback = list(scores.keys())[0]
        scores[fallback] += 2
        reasons[fallback].append("default slot fallback")

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [(name, score, reasons[name]) for name, score in ranked[:top_n]]


def create_run(
    agent_name: str,
    project: Path,
    task: str,
    label: str | None,
    timeout_minutes: int,
    extra: str | None,
    batch_id: str | None,
    execution_mode: str,
) -> tuple[Path, dict[str, Any]]:
    ensure_layout()
    run_id = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{agent_name}-{uuid.uuid4().hex[:6]}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    prompt = prompt_template(agent_name, project, task, label, extra)
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    metadata = {
        "run_id": run_id,
        "batch_id": batch_id,
        "agent": agent_name,
        "project": str(project),
        "task": task,
        "label": label,
        "execution_mode": execution_mode,
        "timeout_minutes": timeout_minutes,
        "created_at": now_utc(),
        "state": "queued",
        "prompt_path": str(run_dir / "prompt.txt"),
        "log_path": str(run_dir / "agent.log"),
        "result_path": str(run_dir / "result.json"),
        "worker_command": f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'swarm_orchestrator.py'))} _worker --run-dir {shlex.quote(str(run_dir))}",
    }
    write_json(run_dir / "metadata.json", metadata)
    return run_dir, metadata


def launch_worker(run_dir: Path, foreground: bool) -> int:
    cmd = [sys.executable, str(ROOT / "swarm_orchestrator.py"), "_worker", "--run-dir", str(run_dir)]
    if foreground:
        return subprocess.call(cmd)
    with (run_dir / "worker.stdout.log").open("a", encoding="utf-8") as stdout:
        process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=stdout,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            text=True,
        )
    metadata = load_metadata(run_dir)
    metadata["worker_pid"] = process.pid
    metadata["state"] = "starting"
    write_json(run_dir / "metadata.json", metadata)
    return 0


def worker_main(run_dir: Path) -> int:
    metadata_path = run_dir / "metadata.json"
    metadata = load_metadata(run_dir)
    log_path = run_dir / "agent.log"
    try:
        agent = get_agent_spec(metadata["agent"])
        project = Path(metadata["project"])
        prompt = (run_dir / "prompt.txt").read_text(encoding="utf-8")
        command = build_command(agent, project, prompt, metadata["timeout_minutes"])
        env = build_agent_env(project)
        started_at = time.time()

        metadata["state"] = "running"
        metadata["started_at"] = now_utc()
        metadata["command"] = command
        metadata["command_pretty"] = shlex.join(command)
        write_json(metadata_path, metadata)

        timed_out = False
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"[swarm] started_at={metadata['started_at']}\n")
            log_handle.write(f"[swarm] command={shlex.join(command)}\n")
            log_handle.write("[swarm] agent_output_begin\n")
            log_handle.flush()
            process = subprocess.Popen(
                command,
                cwd=metadata["project"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                env=env,
                text=True,
                bufsize=1,
            )
            metadata["agent_pid"] = process.pid
            write_json(metadata_path, metadata)

            while True:
                line = process.stdout.readline() if process.stdout else ""
                if line:
                    log_handle.write(line)
                    log_handle.flush()
                elif process.poll() is not None:
                    break

                if time.time() - started_at > metadata["timeout_minutes"] * 60:
                    timed_out = True
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=10)
                    break

            returncode = process.wait()
            completed_at = now_utc()
            result = {
                "run_id": metadata["run_id"],
                "agent": metadata["agent"],
                "project": metadata["project"],
                "returncode": returncode,
                "timed_out": timed_out,
                "completed_at": completed_at,
                "status": "timeout" if timed_out else ("ok" if returncode == 0 else "failed"),
                "log_path": str(log_path),
            }
            if not timed_out and returncode == 0:
                compliance_status, compliance_issues = evaluate_run_log(log_path)
                result["status"] = compliance_status
                if compliance_issues:
                    result["compliance_issues"] = compliance_issues
            guardrail_status, guardrail_issues, guardrail_details = run_memory_guardrails()
            result["memory_guardrails"] = {
                "status": guardrail_status,
                "checks": guardrail_details,
            }
            if guardrail_issues:
                existing = result.get("compliance_issues", [])
                result["compliance_issues"] = existing + [
                    f"memory_guardrail: {issue}" for issue in guardrail_issues
                ]
                result["status"] = "needs_review"
            write_json(run_dir / "result.json", result)
            metadata["state"] = result["status"]
            metadata["completed_at"] = completed_at
            metadata["returncode"] = returncode
            metadata["timed_out"] = timed_out
            if result.get("compliance_issues"):
                metadata["compliance_issues"] = result["compliance_issues"]
            metadata["memory_guardrails"] = result["memory_guardrails"]
            write_json(metadata_path, metadata)
            for check in guardrail_details:
                log_handle.write(
                    f"\n[swarm] memory_guardrail={check['name']} returncode={check['returncode']}\n"
                )
                if check.get("output"):
                    log_handle.write(str(check["output"]).rstrip() + "\n")
            log_handle.write(f"\n[swarm] completed_at={completed_at} returncode={returncode} timed_out={timed_out}\n")
            log_handle.flush()
    except Exception as exc:
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"\n[swarm] worker_exception={type(exc).__name__}: {exc}\n")
            log_handle.flush()
        metadata["returncode"] = 1
        metadata["timed_out"] = False
        record_worker_failure(run_dir, metadata, f"worker_exception: {type(exc).__name__}: {exc}")
        return 1
    return 0


def command_agents(_: argparse.Namespace) -> int:
    config = load_config()["agents"]
    for name, payload in config.items():
        print(f"{name}: {payload['label']}")
        print(f"  role: {payload['role']}")
        print(f"  command: {payload['command']}")
        if payload.get("defaults", {}).get("execution_preference"):
            print(f"  execution_preference: {payload['defaults']['execution_preference']}")
    return 0


def command_check_agent(args: argparse.Namespace) -> int:
    config = load_config()
    names = list(config.get("agents", {}).keys()) if args.all else [args.agent]
    exit_code = 0
    for name in names:
        state, details = check_agent_readiness(name)
        print(f"{name}: {state}")
        for detail in details:
            print(f"  {detail}")
        if state != "ready":
            exit_code = 1
    return exit_code


def command_recommend(args: argparse.Namespace) -> int:
    ranked = recommend_agents(args.task, args.top)
    for idx, (name, score, reasons) in enumerate(ranked, start=1):
        reason_text = ", ".join(reasons) if reasons else "no explicit keyword match"
        print(f"{idx}. {name} score={score} reasons={reason_text}")
    return 0


def command_dispatch(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    if not project.exists():
        raise SystemExit(f"Project path not found: {project}")
    spec = get_agent_spec(args.agent)
    execution_mode = args.mode or spec.defaults.get("execution_preference", "sandbox")
    run_dir, metadata = create_run(
        agent_name=args.agent,
        project=project,
        task=args.task,
        label=args.label,
        timeout_minutes=args.timeout,
        extra=args.extra,
        batch_id=args.batch_id,
        execution_mode=execution_mode,
    )
    metadata["worker_command"] = f"{shlex.quote(sys.executable)} {shlex.quote(str(ROOT / 'swarm_orchestrator.py'))} _worker --run-dir {shlex.quote(str(run_dir))}"
    write_json(run_dir / "metadata.json", metadata)
    if args.dry_run:
        prompt = (run_dir / "prompt.txt").read_text(encoding="utf-8")
        command = build_command(spec, project, prompt, args.timeout)
        metadata["command_pretty"] = shlex.join(command)
        write_json(run_dir / "metadata.json", metadata)
        print(str(run_dir))
        print(f"mode={execution_mode}")
        print(shlex.join(command))
        print(metadata["worker_command"])
        return 0
    exit_code = launch_worker(run_dir, foreground=args.foreground)
    print(run_dir.name)
    print(run_dir)
    return exit_code


def command_fanout(args: argparse.Namespace) -> int:
    batch_id = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    agents = [item.strip() for item in args.agents.split(",") if item.strip()]
    if args.agents == "auto":
        agents = [name for name, _, _ in recommend_agents(args.task, args.parallel)]
    for agent_name in agents:
        dispatch_args = argparse.Namespace(
            agent=agent_name,
            project=args.project,
            task=args.task,
            label=args.label,
            timeout=args.timeout,
            extra=args.extra,
            mode=args.mode,
            dry_run=args.dry_run,
            foreground=False,
            batch_id=batch_id,
        )
        command_dispatch(dispatch_args)
    print(f"batch_id={batch_id}")
    return 0


def pid_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def command_status(args: argparse.Namespace) -> int:
    run_dirs = list_run_dirs()
    if args.run_id:
        run_dirs = [RUNS_DIR / args.run_id]
    if args.batch_id:
        run_dirs = [run_dir for run_dir in run_dirs if load_metadata(run_dir).get("batch_id") == args.batch_id]
    if args.limit:
        run_dirs = run_dirs[: args.limit]
    for run_dir in run_dirs:
        if not run_dir.exists():
            print(f"missing: {run_dir.name}")
            continue
        metadata = load_metadata(run_dir)
        worker_live = pid_alive(metadata.get("worker_pid"))
        agent_live = pid_alive(metadata.get("agent_pid"))
        print(
            f"{metadata['run_id']} agent={metadata['agent']} mode={metadata.get('execution_mode')} state={metadata.get('state')} "
            f"worker_live={worker_live} agent_live={agent_live} project={metadata['project']}"
        )
    return 0


def command_worker_command(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    metadata = load_metadata(run_dir)
    print(metadata["worker_command"])
    return 0


def command_show(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    metadata = load_metadata(run_dir)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


def command_logs(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    log_path = run_dir / "agent.log"
    if not log_path.exists():
        raise SystemExit(f"No log for run: {args.run_id}")
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-args.tail :] if args.tail else lines
    for line in tail:
        print(line)
    return 0


def command_collect(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    metadata = load_metadata(run_dir)
    result_path = run_dir / "result.json"
    result = read_json(result_path) if result_path.exists() else {}
    print(f"run_id: {metadata['run_id']}")
    print(f"agent: {metadata['agent']}")
    print(f"state: {metadata.get('state')}")
    print(f"project: {metadata['project']}")
    if result:
        print(f"returncode: {result.get('returncode')}")
        print(f"timed_out: {result.get('timed_out')}")
        print(f"completed_at: {result.get('completed_at')}")
        if result.get("compliance_issues"):
            print("compliance_issues:")
            for issue in result["compliance_issues"]:
                print(f"- {issue}")
        if result.get("memory_guardrails"):
            print(f"memory_guardrails: {result['memory_guardrails'].get('status')}")
    print(f"log_path: {run_dir / 'agent.log'}")
    print("")
    command_logs(argparse.Namespace(run_id=args.run_id, tail=args.tail))
    return 0


def command_reevaluate(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    metadata = load_metadata(run_dir)
    log_path = run_dir / "agent.log"
    result_path = run_dir / "result.json"
    result = read_json(result_path) if result_path.exists() else {}

    status, issues = evaluate_run_log(log_path)
    guardrail_status, guardrail_issues, guardrail_details = run_memory_guardrails()
    if guardrail_issues:
        issues.extend(f"memory_guardrail: {issue}" for issue in guardrail_issues)
        status = "needs_review"
    result["status"] = status
    result["memory_guardrails"] = {
        "status": guardrail_status,
        "checks": guardrail_details,
    }
    if issues:
        result["compliance_issues"] = issues
    else:
        result.pop("compliance_issues", None)
    write_json(result_path, result)

    metadata["state"] = status
    metadata["memory_guardrails"] = result["memory_guardrails"]
    if issues:
        metadata["compliance_issues"] = issues
    else:
        metadata.pop("compliance_issues", None)
    write_json(run_dir / "metadata.json", metadata)

    print(f"{metadata['run_id']} state={status}")
    for issue in issues:
        print(f"- {issue}")
    return 0 if status == "ok" else 1


def command_takeover(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    metadata = load_metadata(run_dir)
    result_path = run_dir / "result.json"
    result = read_json(result_path) if result_path.exists() else {}
    tail_capture = subprocess.run(
        [sys.executable, str(ROOT / "swarm_orchestrator.py"), "logs", args.run_id, "--tail", "60"],
        capture_output=True,
        text=True,
        check=False,
    )
    takeover_text = textwrap.dedent(
        f"""\
        # Takeover Brief

        Run ID: {metadata['run_id']}
        Agent: {metadata['agent']}
        Project: {metadata['project']}
        State: {metadata.get('state')}
        Created at: {metadata.get('created_at')}
        Started at: {metadata.get('started_at')}
        Completed at: {metadata.get('completed_at')}
        Return code: {result.get('returncode')}
        Timed out: {result.get('timed_out')}

        ## Task
        {metadata['task']}

        ## Artefacts
        - Prompt: {run_dir / 'prompt.txt'}
        - Metadata: {run_dir / 'metadata.json'}
        - Log: {run_dir / 'agent.log'}
        - Result: {run_dir / 'result.json'}

        ## Last Log Lines
        {tail_capture.stdout.strip() if tail_capture.stdout.strip() else "(no log output)"}
        """
    )
    path = run_dir / "takeover.md"
    path.write_text(takeover_text, encoding="utf-8")
    print(path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local swarm orchestrator for CLI agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    agents_parser = subparsers.add_parser("agents")
    agents_parser.set_defaults(func=command_agents)

    check_parser = subparsers.add_parser("check-agent")
    check_group = check_parser.add_mutually_exclusive_group(required=True)
    check_group.add_argument("--agent")
    check_group.add_argument("--all", action="store_true")
    check_parser.set_defaults(func=command_check_agent)

    rec_parser = subparsers.add_parser("recommend")
    rec_parser.add_argument("--task", required=True)
    rec_parser.add_argument("--top", type=int, default=3)
    rec_parser.set_defaults(func=command_recommend)

    dispatch_parser = subparsers.add_parser("dispatch")
    dispatch_parser.add_argument("--agent", required=True)
    dispatch_parser.add_argument("--project", required=True)
    dispatch_parser.add_argument("--task", required=True)
    dispatch_parser.add_argument("--label")
    dispatch_parser.add_argument("--extra")
    dispatch_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_MINUTES)
    dispatch_parser.add_argument("--mode", choices=["sandbox", "host"])
    dispatch_parser.add_argument("--foreground", action="store_true")
    dispatch_parser.add_argument("--dry-run", action="store_true")
    dispatch_parser.add_argument("--batch-id")
    dispatch_parser.set_defaults(func=command_dispatch)

    fanout_parser = subparsers.add_parser("fanout")
    fanout_parser.add_argument("--agents", required=True, help="comma-separated list or 'auto'")
    fanout_parser.add_argument("--project", required=True)
    fanout_parser.add_argument("--task", required=True)
    fanout_parser.add_argument("--label")
    fanout_parser.add_argument("--extra")
    fanout_parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_MINUTES)
    fanout_parser.add_argument("--parallel", type=int, default=3)
    fanout_parser.add_argument("--mode", choices=["sandbox", "host"])
    fanout_parser.add_argument("--dry-run", action="store_true")
    fanout_parser.set_defaults(func=command_fanout)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--run-id")
    status_parser.add_argument("--batch-id")
    status_parser.add_argument("--limit", type=int, default=20)
    status_parser.set_defaults(func=command_status)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("run_id")
    show_parser.set_defaults(func=command_show)

    logs_parser = subparsers.add_parser("logs")
    logs_parser.add_argument("run_id")
    logs_parser.add_argument("--tail", type=int, default=40)
    logs_parser.set_defaults(func=command_logs)

    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("run_id")
    collect_parser.add_argument("--tail", type=int, default=80)
    collect_parser.set_defaults(func=command_collect)

    reevaluate_parser = subparsers.add_parser("reevaluate")
    reevaluate_parser.add_argument("run_id")
    reevaluate_parser.set_defaults(func=command_reevaluate)

    takeover_parser = subparsers.add_parser("takeover")
    takeover_parser.add_argument("run_id")
    takeover_parser.set_defaults(func=command_takeover)

    worker_command_parser = subparsers.add_parser("worker-command")
    worker_command_parser.add_argument("run_id")
    worker_command_parser.set_defaults(func=command_worker_command)

    worker_parser = subparsers.add_parser("_worker")
    worker_parser.add_argument("--run-dir", required=True)
    worker_parser.set_defaults(func=None)

    return parser


def main() -> int:
    ensure_layout()
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "_worker":
        return worker_main(Path(args.run_dir))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
