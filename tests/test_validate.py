#!/usr/bin/env python3
"""Unit tests for the artifact prose checks in validate.py (filler phrases, template
placeholders, duplicated header bullets). Standard library only; exit 0 on success."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

PASSES = 0
FAILS = 0


def check(name: str, cond: bool) -> None:
    global PASSES, FAILS
    if cond:
        PASSES += 1
    else:
        FAILS += 1
        print(f"FAIL  {name}")


def errors_for(text: str) -> list[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
        p = Path(f.name)
    try:
        return validate.prose_errors(p)
    finally:
        p.unlink()


CLEAN = """# Drivers — Acme

- **Date**: 2026-01-01
- **Status**: reviewed

This register lists four business goals and six scenarios. Start with the prioritised list.

## Body

The dashboard loads in under 1.5 seconds at the 95th percentile.
"""
check("clean artifact has no prose errors", errors_for(CLEAN) == [])

check("filler phrase is flagged",
      any("seamless" in e for e in errors_for("# T\n\nA seamless experience.\n")))
check("filler verb form is flagged",
      any("leverages" in e for e in errors_for("# T\n\nIt leverages queues.\n")))
check("'leverage' as a plain noun is not flagged",
      errors_for("# T\n\nThe point of leverage is the driver set.\n") == [])
check("filler inside a code fence is allowed",
      errors_for("# T\n\n```text\nseamless\n```\n") == [])
check("each filler phrase reported once",
      sum("delve" in e for e in errors_for("# T\n\nWe delve and delve again.\n")) == 1)

check("template placeholder is flagged",
      any("<SystemName>" in e for e in errors_for("# Report — <SystemName>\n\nBody.\n")))
check("unfilled date placeholder is flagged",
      any("<YYYY-MM-DD>" in e for e in errors_for("# T\n\n- **Date**: <YYYY-MM-DD>\n")))

DUP = """# T

- **Status**: draft
- **Owner**: a
- **Status**: draft

## Body
"""
check("duplicated header bullet is flagged",
      any("'**Status**' appears 2" in e for e in errors_for(DUP)))
REPEAT_BELOW = """# T

- **Status**: draft

## Scenario one

- **Attribute(s)**: security

## Scenario two

- **Attribute(s)**: availability
"""
check("repeated bullets after the first section are allowed",
      errors_for(REPEAT_BELOW) == [])

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
