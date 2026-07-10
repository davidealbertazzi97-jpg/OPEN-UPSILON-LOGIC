#!/usr/bin/env python3
"""Logical validation guardrails for Obsidian agent vaults (Prolog-style check)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Vault root folder is the parent of the scripts folder
VAULT = Path(__file__).resolve().parents[1]
MOC_DIR = VAULT / "indices"
CANTIERI_DIR = VAULT / "worksites"
SESSIONI_DIR = VAULT / "sessions"
PROTOCOLLI_DIR = VAULT / "protocols"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass(frozen=True)
class Fact:
    predicate: str
    subject: str
    value: str | bool | int | None = None


@dataclass
class Finding:
    level: str
    code: str
    subject: str
    message: str
    rule: str


@dataclass
class Report:
    facts: list[Fact] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    def add_fact(self, predicate: str, subject: str, value: str | bool | int | None = None) -> None:
        self.facts.append(Fact(predicate, subject, value))

    def add(self, level: str, code: str, subject: str, message: str, rule: str) -> None:
        self.findings.append(Finding(level, code, subject, message, rule))

    @property
    def has_conflict(self) -> bool:
        return any(f.level == "conflict" for f in self.findings)

    @property
    def has_warning(self) -> bool:
        return any(f.level == "warning" for f in self.findings)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return ""


def note_id(path: Path) -> str:
    return path.stem


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    values: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def wikilinks(text: str) -> set[str]:
    return {match.strip() for match in WIKILINK_RE.findall(text)}


def moc_links() -> dict[str, set[str]]:
    links: dict[str, set[str]] = {}
    if MOC_DIR.exists():
        for moc in sorted(MOC_DIR.glob("MOC_*.md")):
            links[moc.stem] = wikilinks(read_text(moc))
    return links


def git_status() -> tuple[bool, list[str]]:
    completed = subprocess.run(
        ["git", "-C", str(VAULT), "status", "--short"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return False, [completed.stderr.strip() or "git status failed"]
    return True, [line for line in completed.stdout.splitlines() if line.strip()]


def markdown_files() -> list[Path]:
    excluded = {".git", ".obsidian"}
    files: list[Path] = []
    for path in VAULT.rglob("*.md"):
        if any(part in excluded for part in path.relative_to(VAULT).parts):
            continue
        files.append(path)
    return sorted(files)


def require_sections(report: Report, path: Path, sections: Iterable[str], rule: str) -> None:
    text = read_text(path)
    for section in sections:
        if section not in text:
            report.add(
                "conflict",
                "missing_section",
                str(path.relative_to(VAULT)),
                f"Required section missing: {section}",
                rule,
            )


def check_git(report: Report, strict: bool) -> None:
    ok, lines = git_status()
    report.add_fact("git_repository", "Obsidian_Vault", ok)
    if not ok:
        report.add("conflict", "git_missing", "Obsidian_Vault", lines[0], "git_repository_required")
        return
    report.add_fact("git_changed_files", "Obsidian_Vault", len(lines))
    if lines:
        level = "warning" if strict else "info"
        report.add(
            level,
            "git_dirty",
            "Obsidian_Vault",
            f"{len(lines)} files are uncommitted or untracked",
            "git_changes_must_be_committed_or_declared",
        )


def check_worksites(report: Report, links_by_moc: dict[str, set[str]]) -> None:
    worksite_links = links_by_moc.get("MOC_Worksites", set())
    projects_links = links_by_moc.get("MOC_Projects", set())
    required = [
        "## Objective",
        "## Current State",
        "## Perimeter and Isolation",
        "## Open Lanes",
        "## Next Steps",
        "## Linked Sessions",
    ]
    if CANTIERI_DIR.exists():
        for path in sorted(CANTIERI_DIR.glob("*.md")):
            if path.name == "README.md" or path.name.startswith("Template_"):
                continue
            nid = note_id(path)
            text = read_text(path)
            fm = parse_frontmatter(text)
            report.add_fact("worksite", nid, True)
            if fm.get("type") != "project":
                report.add("conflict", "worksite_type", nid, "frontmatter type must be 'project'", "worksite_contract")
            if "status" not in fm:
                report.add("conflict", "worksite_status_missing", nid, "frontmatter status is missing", "worksite_contract")
            if nid not in worksite_links:
                report.add("conflict", "worksite_not_in_moc", nid, "worksite is not linked in MOC_Worksites", "worksite_moc_link")
            if "MOC_Worksites" not in wikilinks(text):
                report.add("warning", "missing_backlink", nid, "missing return link to [[MOC_Worksites]]", "worksite_backlink")
            require_sections(report, path, required, "worksite_required_sections")


def check_sessions(report: Report, links_by_moc: dict[str, set[str]]) -> None:
    session_links = links_by_moc.get("MOC_Sessions", set())
    required = [
        "## Objective",
        "## Files",
        "## Final State",
        "## Next Steps",
        "## Where",
    ]
    if SESSIONI_DIR.exists():
        recent = sorted(SESSIONI_DIR.glob("Session_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:25]
        for path in recent:
            nid = note_id(path)
            text = read_text(path)
            report.add_fact("session", nid, True)
            if nid not in session_links:
                report.add("warning", "session_not_in_moc", nid, "session is not linked in MOC_Sessions", "session_moc_link")
            if not parse_frontmatter(text):
                report.add("warning", "session_no_frontmatter", nid, "frontmatter is missing", "session_frontmatter")
            # Legacy or relaxed heading validation (matching prefixes)
            for section in required:
                if section not in text:
                    report.add(
                        "warning",
                        "session_weak_handoff",
                        nid,
                        f"potentially incomplete handoff: missing prefix {section}",
                        "session_handoff_contract",
                    )


def check_protocols(report: Report, links_by_moc: dict[str, set[str]]) -> None:
    protocol_links = links_by_moc.get("MOC_Protocols", set())
    if PROTOCOLLI_DIR.exists():
        for path in sorted(PROTOCOLLI_DIR.glob("Protocol_*.md")):
            nid = note_id(path)
            report.add_fact("protocol", nid, True)
            if nid not in protocol_links:
                report.add("warning", "protocol_not_in_moc", nid, "protocol is not linked in MOC_Protocols", "protocol_moc_link")


def check_orphans(report: Report, links_by_moc: dict[str, set[str]]) -> None:
    linked = set().union(*links_by_moc.values()) if links_by_moc else set()
    for path in markdown_files():
        rel = path.relative_to(VAULT)
        if rel.parts[0] in {"sessions", "dump"}:
            continue
        if path.name in {"README.md", "GEMINI.md", "LICENSE", "context_summary.md"}:
            continue
        nid = note_id(path)
        text = read_text(path)
        has_metadata = bool(parse_frontmatter(text)) or "Tags:" in text
        if not has_metadata:
            report.add("warning", "missing_metadata", str(rel), "note without frontmatter or Tags", "node_metadata")
        if rel.parts[0] not in {"indices", "worksites"} and nid not in linked:
            report.add("warning", "possibly_orphan", str(rel), "note not linked by any MOC", "no_orphan_nodes")


def build_report(strict: bool) -> Report:
    report = Report()
    links_by_moc = moc_links()
    check_git(report, strict)
    check_worksites(report, links_by_moc)
    check_sessions(report, links_by_moc)
    check_protocols(report, links_by_moc)
    check_orphans(report, links_by_moc)
    return report


def print_report(report: Report, show_facts: bool) -> None:
    status = "conflict" if report.has_conflict else "warning" if report.has_warning else "ok"
    print(f"vault_guardrails: {status}")
    if show_facts:
        for fact in report.facts:
            print(f"FACT {fact.predicate}({fact.subject}, {fact.value})")
    for finding in report.findings:
        print(f"{finding.level.upper()} {finding.code} [{finding.subject}] {finding.message} ({finding.rule})")


def write_json(report: Report, path: Path) -> None:
    payload = {
        "facts": [fact.__dict__ for fact in report.facts],
        "findings": [finding.__dict__ for finding in report.findings],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Logical consistency guardrails for agent vaults")
    parser.add_argument("--strict", action="store_true", help="treat conflicts as exit code 1")
    parser.add_argument("--facts", action="store_true", help="print derived logical facts database")
    parser.add_argument("--json-output", type=Path, help="write report to JSON file")
    args = parser.parse_args(argv)

    report = build_report(strict=args.strict)
    print_report(report, args.facts)
    if args.json_output:
        write_json(report, args.json_output)

    if report.has_conflict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
