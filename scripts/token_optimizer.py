#!/usr/bin/env python3
"""Token Optimizer: compiles Obsidian vault state into a single, compact summary.
Helps LLM agents understand the current status without reading dozens of files.
"""

from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime

VAULT = Path(__file__).resolve().parents[1]
CANTIERI_DIR = VAULT / "CANTIERI"
SESSIONI_DIR = VAULT / "sessioni"
PROTOCOLLI_DIR = VAULT / "scoperte e processi"
OUTPUT_FILE = VAULT / "context_summary.md"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


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


def extract_section(text: str, header: str) -> str:
    """Extracts a section from markdown text under a specific header."""
    lines = text.splitlines()
    section_lines = []
    in_section = False
    for line in lines:
        if line.startswith("## ") or line.startswith("# "):
            if in_section:
                break
            if header.lower() in line.lower():
                in_section = True
                continue
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines).strip()


def compile_state() -> str:
    summary = []
    summary.append("# Context Summary (Token-Optimized)")
    summary.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    summary.append("## Active Worksites (CANTIERI)")
    if CANTIERI_DIR.exists():
        cantieri = [p for p in CANTIERI_DIR.glob("*.md") if p.name != "README.md" and not p.name.startswith("Template_")]
        if not cantieri:
            summary.append("- No active worksites found.")
        for p in sorted(cantieri):
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            objective = extract_section(text, "Obiettivo")
            next_steps = extract_section(text, "Prossimi passi")
            
            summary.append(f"### [[{p.stem}]] (Status: {fm.get('status', 'unknown')})")
            if fm.get("owners"):
                summary.append(f"**Owners**: {fm.get('owners')}")
            if objective:
                summary.append(f"**Objective**:\n{objective}")
            if next_steps:
                summary.append(f"**Next Steps**:\n{next_steps}")
            summary.append("")
    else:
        summary.append("- CANTIERI folder not found.\n")

    summary.append("## Recent Session Logs (Last 3 Handoffs)")
    if SESSIONI_DIR.exists():
        sessions = sorted(SESSIONI_DIR.glob("Sessione_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
        if not sessions:
            summary.append("- No sessions logged.")
        for p in sessions:
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            status = extract_section(text, "Stato finale")
            next_steps = extract_section(text, "Prossimi passi")
            where = extract_section(text, "Dove")
            
            summary.append(f"### [[{p.stem}]] ({fm.get('date', 'no date')})")
            summary.append(f"- **Project**: {fm.get('project', 'unknown')}")
            if status:
                summary.append(f"- **Final Status**: {status.replace('\n', ' ')}")
            if next_steps:
                summary.append(f"- **Next Steps**:\n{next_steps}")
            if where:
                summary.append(f"- **Entry Points**:\n{where}")
            summary.append("")
    else:
        summary.append("- Sessioni folder not found.\n")

    summary.append("## Core Execution Protocols")
    if PROTOCOLLI_DIR.exists():
        protocols = sorted(PROTOCOLLI_DIR.glob("Protocollo_*.md"))
        if not protocols:
            summary.append("- No protocols registered.")
        for p in protocols:
            text = p.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text)
            summary.append(f"- [[{p.stem}]] - Tag: {fm.get('tags', 'none')}")
    else:
        summary.append("- scoperte e processi folder not found.")
        
    return "\n".join(summary)


def main() -> None:
    print("Compiling Obsidian vault state summary...")
    state_content = compile_state()
    OUTPUT_FILE.write_text(state_content, encoding="utf-8")
    print(f"Success! Summary written to: {OUTPUT_FILE}")
    print(f"Token count estimation: ~{len(state_content.split()) * 1.3:.0f} tokens.")


if __name__ == "__main__":
    main()
