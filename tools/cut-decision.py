#!/usr/bin/env python
"""
cut-decision.py -- verdict binaire pour cut sequence sprint MCP server template.

Usage:
    uv run python tools/cut-decision.py

Output: JSON sur stdout + exit code reflétant la sévérité.

Decision rule:
    tools>=4 ET tests>=90% -> KEEP_FULL_SCOPE                  exit 0
    tools=3  ET tests>=80% -> KEEP_FULL_SCOPE_BUFFER_CONSUMED  exit 0
    tools=3  ET tests<80%  -> CUT_PROMPT                       exit 1
    tools<=2               -> CUT_PROMPT_AND_RESOURCE          exit 2
    other                  -> WARN_AMBIGUOUS                   exit 3
    pytest crash           -> BLOCKER_PYTEST                   exit 3

Tools count = nombre de modules avec `def register(` dans src/tools/
Resources count = idem dans src/resources/
Prompts count = idem dans src/prompts/
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def count_register_in_dir(directory: Path) -> int:
    """Count modules with `def register(` in a src/ subdir."""
    if not directory.exists():
        return 0
    count = 0
    for py_file in directory.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        content = py_file.read_text(encoding="utf-8")
        if re.search(r"def\s+register\s*\(", content):
            count += 1
    return count


def run_pytest_quick() -> tuple[int, int]:
    """Run pytest --tb=no -q. Return (passed, failed). (-1, -1) on error."""
    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1, -1
    output = result.stdout + result.stderr
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else 0
    return passed, failed


def decide(
    tools: int, resources: int, prompts: int, passed: int, failed: int
) -> dict:
    """Decision rule formalisée -- single source of truth, ZERO ambiguïté."""
    if passed < 0:
        return {
            "verdict": "BLOCKER_PYTEST",
            "tools_done": tools,
            "resources_done": resources,
            "prompts_done": prompts,
            "rationale": "pytest run failed (timeout or not found). Debug avant decision.",
        }

    total = passed + failed
    pass_pct = (passed / total * 100) if total > 0 else 0.0

    if tools >= 4 and pass_pct >= 90:
        verdict = "KEEP_FULL_SCOPE"
        rationale = "On track. Resource + Prompt J15 GO."
    elif tools == 3 and pass_pct >= 80:
        verdict = "KEEP_FULL_SCOPE_BUFFER_CONSUMED"
        rationale = "Buffer Hofstadter consommé. Resource + Prompt OK, zéro slack J15."
    elif tools == 3 and pass_pct < 80:
        verdict = "CUT_PROMPT"
        rationale = "Tests fragiles. Cut Prompt #6, ship 5 primitives (4 Tools + Resource)."
    elif tools <= 2:
        verdict = "CUT_PROMPT_AND_RESOURCE"
        rationale = (
            "Retard sévère. Ship 4 Tools + Tasks only. Logger ADR-011. "
            "Repositioning v3 dégradé."
        )
    else:
        verdict = "WARN_AMBIGUOUS"
        rationale = (
            f"Cas inattendu tools={tools} resources={resources} "
            f"prompts={prompts} pass_pct={pass_pct:.0f}%. Décision manuelle."
        )

    return {
        "verdict": verdict,
        "tools_done": tools,
        "resources_done": resources,
        "prompts_done": prompts,
        "tests_passed": passed,
        "tests_failed": failed,
        "tests_pass_pct": round(pass_pct, 1),
        "rationale": rationale,
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    src = repo_root / "src"

    tools = count_register_in_dir(src / "tools")
    resources = count_register_in_dir(src / "resources")
    prompts = count_register_in_dir(src / "prompts")
    passed, failed = run_pytest_quick()

    result = decide(tools, resources, prompts, passed, failed)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    exit_codes = {
        "KEEP_FULL_SCOPE": 0,
        "KEEP_FULL_SCOPE_BUFFER_CONSUMED": 0,
        "CUT_PROMPT": 1,
        "CUT_PROMPT_AND_RESOURCE": 2,
        "BLOCKER_PYTEST": 3,
        "WARN_AMBIGUOUS": 3,
    }
    sys.exit(exit_codes.get(result["verdict"], 3))


if __name__ == "__main__":
    main()
