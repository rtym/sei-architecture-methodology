#!/usr/bin/env python3
"""Unit tests for validate.py's artifact checkers: prose rules (filler phrases, template
placeholders, duplicated header bullets), diagram rules, per-driver-file checks, traceability,
link checking, and the drivers-directory cross-file check. Standard library only; exit 0 on
success."""
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


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def run_checker(fn, rel: str, text: str, extra: dict[str, str] | None = None) -> list[str]:
    """Write `text` at `rel` (plus any extra files) inside a temp tree and run fn on it."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        p = write(root, rel, text)
        for erel, etext in (extra or {}).items():
            write(root, erel, etext)
        return fn(p)


# --------------------------------------------------------------------------- #
# Prose checks
# --------------------------------------------------------------------------- #

def errors_for(text: str) -> list[str]:
    return run_checker(validate.prose_errors, "artifact.md", text)


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

# --------------------------------------------------------------------------- #
# Diagram rules (check_diagram)
# --------------------------------------------------------------------------- #

def diag(block: str) -> list[str]:
    return validate.check_diagram(block, "t")


check("flowchart with a title comment passes",
      diag('flowchart LR\n  %% module view — demo\n  a["A"] -->|"uses"| b["B"]\n') == [])
check("flowchart without a title is flagged",
      any("title" in e for e in diag('flowchart LR\n  a["A"] --> b["B"]\n')))
check("%% name: alone does not count as a title",
      any("title" in e for e in diag('flowchart LR\n  %% name: x\n  a["A"] --> b["B"]\n')))
check("C4Context without a title line is flagged",
      any("title" in e for e in diag("C4Context\nPerson(u, \"U\")\n")))
check("space in a C4 alias is flagged",
      any("space in alias" in e
          for e in diag('C4Context\ntitle t\nPerson(my user, "U")\n')))
over10 = "C4Container\ntitle t\nContainer_Boundary(b, \"B\")\n" + \
         "".join(f'Container(c{i}, "C{i}", "t", "d")\n' for i in range(11))
check("more than 10 C4 leaf nodes is flagged",
      any("max 10" in e for e in diag(over10)))
check("C4Container content without a Boundary is flagged",
      any("Boundary" in e for e in diag('C4Container\ntitle t\nContainer(a, "A", "t", "d")\n')))
check("Rel without a label is flagged",
      any("Rel" in e
          for e in diag('C4Context\ntitle t\nPerson(u, "U")\nSystem(s, "S", "d")\nRel(u, s, "")\n')))
seq = "sequenceDiagram\n  title t\n" + "  a->>b: m\n" * 5
check("long sequence without autonumber is flagged",
      any("autonumber" in e for e in diag(seq)))
check("sequence with autonumber passes",
      diag("sequenceDiagram\n  title t\n  autonumber\n" + "  a->>b: m\n" * 5) == [])
qas_vert = ('flowchart TD\n  %% SQA-1 quality attribute scenario\n'
            '  a["Source of stimulus"] --> b["Stimulus"] --> c["Artifact"] --> '
            'd["Environment"] --> e["Response"] --> f["Response measure"]\n')
check("vertical quality-attribute-scenario diagram is flagged",
      any("flowchart LR" in e for e in diag(qas_vert)))
check("scenario diagram missing a six-part box is flagged",
      any("missing" in e for e in diag(
          'flowchart LR\n  %% six-part scenario\n  a["Stimulus"] --> b["Response"]\n')))
check("unlabelled edge in a C4-level flowchart is flagged",
      any("unlabelled" in e for e in diag(
          'flowchart LR\n  %% container diagram — demo\n  subgraph s["S"]\n  a["A"]\n  end\n'
          '  a --> b["B"]\n')))

# --------------------------------------------------------------------------- #
# Per-driver-file checks
# --------------------------------------------------------------------------- #

BG_OK = """# BG-1: Reach 10k users

- **Status**: open

The founder needs 10 000 active users within 12 months so that the seed round closes.
"""
check("valid business goal passes",
      run_checker(validate.check_bg_file, "business-goals/BG-1.md", BG_OK) == [])
check("business goal without 'needs … so that' form is flagged",
      any("so that" in e for e in run_checker(
          validate.check_bg_file, "business-goals/BG-1.md",
          "# BG-1\n\n- **Status**: open\n\nGrow the user base.\n")))

UC_OK = """# UC-1: Record a transaction

- **Status**: open
- **Primary actor**: Registered user
- **Trigger**: the user taps Add

## Main success scenario

1. The user enters the amount.
2. The system saves the transaction.

```mermaid
flowchart TD
  %% UC-1 use case diagram
  a(["Registered user"]) -->|"records"| b(["Record a transaction"])
```

![UC-1 use case diagram](diagrams/UC-1.png)
"""
check("valid use case passes",
      run_checker(validate.check_uc_file, "use-cases/UC-1.md", UC_OK) == [])
check("use case without a numbered main success scenario is flagged",
      any("numbered" in e for e in run_checker(
          validate.check_uc_file, "use-cases/UC-1.md",
          UC_OK.replace("1. The user enters the amount.\n2. The system saves the transaction.",
                        "The user enters the amount and the system saves it."))))
check("use case without a diagram is flagged",
      any("diagram" in e for e in run_checker(
          validate.check_uc_file, "use-cases/UC-1.md",
          UC_OK.split("```mermaid")[0])))

CON_OK = """# CON-1: Mobile web only

- **Status**: open
- **Type**: technical
- **Source**: founder decision, 2026-01-01
"""
check("valid constraint passes",
      run_checker(validate.check_con_file, "constraints/CON-1.md", CON_OK) == [])
check("constraint without a type is flagged",
      any("type" in e for e in run_checker(
          validate.check_con_file, "constraints/CON-1.md",
          "# CON-1\n\n- **Status**: open\n- **Source**: contract\n")))

QA_OK = """# SQA-1: Cross-user access is rejected

- **Status**: open

Classified ISO/IEC 25010 Security / confidentiality.

| Part | Value |
|------|-------|
| **Source of stimulus** | authenticated user |
| **Stimulus** | requests another user's data |
| **Artifact** | API |
| **Environment** | normal operation |
| **Response** | rejected and logged |
| **Response measure** | 0 successful reads in 10 000 attempts |

```mermaid
flowchart LR
  %% SQA-1 scenario
  a["Source of stimulus"] -->|"sends"| b["Stimulus"]
```

![SQA-1 six-part scenario](diagrams/scenario-SQA-1.png)
"""
check("valid quality attribute scenario passes",
      run_checker(validate.check_qa_file, "quality-attributes/SQA-1.md", QA_OK) == [])
check("non-numeric response measure is flagged",
      any("numeric" in e for e in run_checker(
          validate.check_qa_file, "quality-attributes/SQA-1.md",
          QA_OK.replace("0 successful reads in 10 000 attempts", "very few reads"))))
check("missing six-part row is flagged",
      any("Environment" in e for e in run_checker(
          validate.check_qa_file, "quality-attributes/SQA-1.md",
          QA_OK.replace("| **Environment** | normal operation |\n", ""))))

ST_OK = """# Stakeholders — Acme

| ID | Name | Role | Concerns |
|----|------|------|----------|
| ST-1 | Ada | sponsor | cost |
"""
check("valid stakeholder register passes",
      run_checker(validate.check_stakeholders, "stakeholders.md", ST_OK) == [])
check("stakeholder register without ST ids is flagged",
      any("ST-" in e for e in run_checker(
          validate.check_stakeholders, "stakeholders.md",
          "# Stakeholders\n\n| ID | Name | Role |\n|----|------|------|\n| 1 | Ada | sponsor |\n")))

UT_OK = """# Utility tree

Rated against ISO/IEC 25010.

| Quality attribute | Refinement | Leaf scenario | Priority (V, R) | Status |
|-------------------|------------|---------------|-----------------|--------|
| Security | confidentiality | SQA-1 — 0 cross-user reads | (H, H) | open |
"""
check("valid tabular utility tree passes",
      run_checker(validate.check_utility_tree, "utility-tree.md", UT_OK) == [])
check("utility tree drawn as a diagram is flagged",
      any("table" in e for e in run_checker(
          validate.check_utility_tree, "utility-tree.md",
          UT_OK + "\n```mermaid\nmindmap\n  root\n```\n")))
check("utility tree without a (V, R) pair is flagged",
      any("(V, R)" in e for e in run_checker(
          validate.check_utility_tree, "utility-tree.md", UT_OK.replace("(H, H)", "high"))))

# --------------------------------------------------------------------------- #
# Report-level checks
# --------------------------------------------------------------------------- #

def scenarios_text(n: int) -> str:
    rows = "\n".join(
        f"| SQA-{i} | Security | rejected | 0 reads in 10 000 | [SQA-{i}](../drivers/quality-attributes/SQA-{i}.md) |"
        for i in range(1, n + 1))
    return ("# Scenarios\n\nISO/IEC 25010.\n\n"
            "| ID | Attribute | Response | Response measure | File |\n"
            "|----|-----------|----------|------------------|------|\n" + rows + "\n")


check("scenario count below the minimum is flagged",
      any("expected" in e for e in run_checker(
          validate.check_scenarios, "scenarios.md", scenarios_text(3))))
check("in-range scenario register passes",
      run_checker(validate.check_scenarios, "scenarios.md", scenarios_text(8)) == [])
check("bare backtick diagram path is flagged",
      any("backtick" in e for e in run_checker(
          validate.check_scenarios, "scenarios.md",
          scenarios_text(8) + "\nSee `diagrams/scenario-SQA-1.png`.\n")))

ATAM_STUB = """# ATAM report

- **Mode**: Full ATAM

architectural approach · utility tree (H, M) · risk · non-risk · sensitivity point ·
tradeoff point · risk theme

| Theme | Threatens |
|-------|-----------|
| data isolation gaps | BG-2 |
"""
check("minimal ATAM stub passes the section scan",
      run_checker(validate.check_atam, "atam-report.md", ATAM_STUB) == [])
check("ATAM report without a Mode header is flagged",
      any("Mode" in e for e in run_checker(
          validate.check_atam, "atam-report.md", ATAM_STUB.replace("- **Mode**: Full ATAM", ""))))
check("risk theme without a business goal is flagged",
      any("business goal" in e for e in run_checker(
          validate.check_atam, "atam-report.md", ATAM_STUB.replace("BG-2", "unknown"))))

# --------------------------------------------------------------------------- #
# Traceability
# --------------------------------------------------------------------------- #

def orphans(text: str, bgs: set, ucs: set, qas: set = None, cons: set = None) -> list[str]:
    return validate._traceability_orphans(text, bgs, ucs, qas or set(), cons or set())


MATRIX = """## Traceability matrix

| Driver | Supports BG | Status |
|--------|-------------|--------|
| UC-1 | BG-1 | open |
"""
check("traced matrix has no orphans",
      orphans(MATRIX, {"BG-1"}, {"UC-1"}) == [])
check("untraced use case is an orphan",
      any("UC-2" in e for e in orphans(MATRIX, {"BG-1"}, {"UC-1", "UC-2"})))
check("unsupported business goal is an orphan",
      any("BG-2" in e for e in orphans(MATRIX, {"BG-1", "BG-2"}, {"UC-1"})))
RETIRED = MATRIX + "| UC-2 | BG-1 | retired |\n"
check("a retired driver is not an orphan",
      orphans(RETIRED, {"BG-1"}, {"UC-1", "UC-2"}) == [])

# --------------------------------------------------------------------------- #
# Link checking
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    write(root, "pkg/exists.md", "# here\n")
    doc = write(root, "pkg/doc.md",
                "[ok](exists.md) · [gone](missing.md) · [web](https://example.com) · [sec](#top)\n")
    errs = validate.broken_links(doc)
    check("broken relative link is flagged", any("missing.md" in e for e in errs))
    check("existing, web and anchor links pass", len(errs) == 1)
    rep = write(root, "reports/flat.md", "[inherited](../drivers/README.md)\n")
    check("generated reports are exempt from link checking",
          validate.broken_links(rep) == [])

# --------------------------------------------------------------------------- #
# Drivers directory cross-file check
# --------------------------------------------------------------------------- #

def make_drivers_tree(root: Path) -> Path:
    d = root / "architecture" / "drivers"
    write(root, "architecture/README.md", "# package index\n")
    write(root, "architecture/drivers/README.md",
          "# Drivers\n\nBG-1 UC-1 SQA-1 listed. Traceability, coverage, change log, utility tree.\n")
    for rel, name in (("business-goals", "BG-1"), ("use-cases", "UC-1"),
                      ("quality-attributes", "SQA-1")):
        write(root, f"architecture/drivers/{rel}/README.md", "# index\n")
        write(root, f"architecture/drivers/{rel}/{name}.md", f"# {name}\n")
    write(root, "architecture/drivers/quality-attributes/utility-tree.md", "# tree\n")
    return d


with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = make_drivers_tree(root)
    check("complete drivers directory passes the cross-file check",
          validate.check_drivers_dir(d) == [])
    (d / "quality-attributes" / "utility-tree.md").unlink()
    check("missing utility tree is flagged",
          any("utility-tree" in e for e in validate.check_drivers_dir(d)))

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = make_drivers_tree(root)
    write(root, "architecture/drivers/use-cases/UC-2.md", "# UC-2\n")
    check("driver file missing from the README is flagged",
          any("UC-2 is not listed" in e for e in validate.check_drivers_dir(d)))
    write(root, "architecture/drivers/use-cases/notes.md", "# stray\n")
    check("a stray file in a driver directory is flagged",
          any("notes.md" in e for e in validate.check_drivers_dir(d)))

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
