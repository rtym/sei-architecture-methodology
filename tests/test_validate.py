#!/usr/bin/env python3
"""Unit tests for validate.py's artifact checkers: prose rules (filler phrases, template
placeholders, duplicated header bullets), diagram rules, per-driver-file checks, traceability,
link checking, and the drivers-directory cross-file check. Standard library only; exit 0 on
success."""
from __future__ import annotations

import re
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

# --------------------------------------------------------------------------- #
# QAW report — entry mode (Starting point) and parked questions
# --------------------------------------------------------------------------- #

QAW_EXAMPLE = (Path(__file__).resolve().parent.parent / "examples"
               / "personal-finance-tracker-mermaid" / "qaw" / "qaw-report.md").read_text(encoding="utf-8")


def qaw(text: str) -> list[str]:
    return run_checker(validate.check_qaw, "architecture/qaw/qaw-report.md", text)


def qaw_new_rule_errors(text: str) -> list[str]:
    return [e for e in qaw(text) if "Starting point" in e or "entry mode" in e
            or "parked question" in e.lower() or "refresh mode" in e]


check("worked example QAW report passes", qaw(QAW_EXAMPLE) == [])

legacy = QAW_EXAMPLE.split("## Step 0", 1)[0] + "## Step 1" + QAW_EXAMPLE.split("## Step 1", 1)[1]
legacy = legacy.split("## Parked questions", 1)[0] + "## Next steps" + legacy.split("## Next steps", 1)[1]
check("a report written before entry modes existed (no Step 0, no parked questions) still passes",
      qaw(legacy) == [])

check("unfilled entry mode 'greenfield | partial | refresh' is flagged",
      any("not exactly one of" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("**Entry mode**: partial", "**Entry mode**: greenfield | partial | refresh"))))
check("unknown entry mode is flagged",
      any("not exactly one of" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("**Entry mode**: partial", "**Entry mode**: brownfield"))))
check("missing entry-mode line is flagged",
      any("does not state the entry mode" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("- **Entry mode**: partial\n", ""))))
check("each entry mode is accepted, bold or plain",
      all(qaw_new_rule_errors(QAW_EXAMPLE.replace("**Entry mode**: partial", f"**Entry mode**: {m}")) == []
          for m in ("greenfield", "partial", "`partial`"))
      )
check("Starting point with an empty inputs table is flagged",
      any("no inputs table rows" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("| Founder's product brief | shared by the sponsor before the session | "
                              "draft business goals (Step 2) and the five constraints (Step 3), "
                              "corrected by the group |", "| | | |"))))

no_docs = QAW_EXAMPLE.replace(
    "| Founder's product brief | shared by the sponsor before the session | "
    "draft business goals (Step 2) and the five constraints (Step 3), corrected by the group |",
    "| none — started from open questions | | |")
check("partial mode that names no input document is flagged",
      any("lists no input document" in e for e in qaw_new_rule_errors(no_docs)))
check("greenfield mode with a 'none' input row passes",
      qaw_new_rule_errors(no_docs.replace("**Entry mode**: partial", "**Entry mode**: greenfield")) == [])

refresh = QAW_EXAMPLE.replace("**Entry mode**: partial", "**Entry mode**: refresh")
check("refresh mode with no scenario tagged 'existing' is flagged",
      any("refresh mode" in e for e in qaw_new_rule_errors(refresh)))
tagged = refresh.replace("| use-case | Advisor | AD-1 |", "| use-case | existing (SQA-1) | AD-1 |", 1)
check("refresh-mode fixture really tags a Step 5 row", tagged != refresh)
check("refresh mode passes once an existing scenario enters Step 5", qaw_new_rule_errors(tagged) == [])

check("parked question without an owner is flagged",
      any("PQ-1 has no owner" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("| SOC 2 auditor | ST-4 |", "| SOC 2 auditor | |"))))
check("parked question without a status is flagged",
      any("PQ-2 has no status" in e for e in qaw_new_rule_errors(
          QAW_EXAMPLE.replace("| ST-5 | 2026-09-03 | open |", "| ST-5 | 2026-09-03 | |"))))
none_section = (QAW_EXAMPLE.split("## Parked questions", 1)[0]
                + "## Parked questions\n\nNone — every question was answered in the session.\n\n## Next steps"
                + QAW_EXAMPLE.split("## Next steps", 1)[1])
check("a parked-questions section that says None passes", qaw_new_rule_errors(none_section) == [])
empty_section = none_section.replace("None — every question was answered in the session.", "TBD")
check("an empty parked-questions section is flagged",
      any("does not say 'None'" in e for e in qaw_new_rule_errors(empty_section)))

def without_links(errs: list[str]) -> list[str]:
    return [e for e in errs if not e.startswith("broken link")]


archived = without_links(run_checker(validate.validate_file, "architecture/qaw/qaw-report-2026-08-20.md", QAW_EXAMPLE))
check("an archived QAW report (qaw-report-<date>.md) is validated as a QAW report, not an ADD session",
      archived == [] and archived == without_links(
          run_checker(validate.validate_file, "architecture/qaw/qaw-report.md", QAW_EXAMPLE)))
check("an archived QAW report with a QAW defect is still caught",
      any("vote budget" in e for e in run_checker(
          validate.validate_file, "architecture/qaw/qaw-report-2026-08-20.md",
          QAW_EXAMPLE.replace("30", "XX").replace("vote", "ballot").replace("Vote", "Ballot"))))
check("a dated ADD session file is still validated as a session",
      any("**Purpose**" in e for e in
          run_checker(validate.validate_file, "architecture/add/acme-2026-08-20.md", "# Acme\n")))

# --------------------------------------------------------------------------- #
# QAW question guide coverage (self-check)
# --------------------------------------------------------------------------- #

GUIDE = (Path(__file__).resolve().parent.parent / "references" / "qaw-question-guide.md").read_text(encoding="utf-8")


def guide_errors(text: str) -> list[str]:
    return run_checker(validate.check_qaw_question_guide, "references/qaw-question-guide.md", text)


check("shipped QAW question guide covers every step, characteristic and mode", guide_errors(GUIDE) == [])
check("guide without a Step 5 section is flagged",
      any("Step 5" in e for e in guide_errors(GUIDE.replace("### Step 5 — Scenario brainstorming",
                                                             "### Brainstorming"))))
check("guide without a Safety section is flagged",
      any("'Safety'" in e for e in guide_errors(GUIDE.replace("### Safety", "### Hazards"))))
check("guide that drops the refresh mode is flagged",
      any("'refresh'" in e for e in guide_errors(GUIDE.replace("**refresh**", "refresh"))))
s7 = GUIDE.index("### Step 7")
s8 = GUIDE.index("### Step 8")
check("a step section with no questions is flagged",
      any("asks no questions" in e for e in guide_errors(
          GUIDE[:s7] + "### Step 7 — Prioritisation\n\nVote.\n\n" + GUIDE[s8:])))
check("a missing guide file is reported",
      any("missing" in e for e in validate.check_qaw_question_guide(Path("/nonexistent/qaw-question-guide.md"))))

st_section = GUIDE.index("## Questions by system type")
st_end = GUIDE.index("## Questions by stakeholder role")
check("guide without system types is flagged",
      any("no 'Questions by system type'" in e for e in guide_errors(GUIDE[:st_section] + GUIDE[st_end:])))
check("a system type without a Key line is flagged",
      any("names no Key" in e for e in guide_errors(GUIDE.replace("Key: `saas`.", "For SaaS."))))
check("a system type with a duplicate key is flagged",
      any("used twice: ai" in e for e in guide_errors(GUIDE.replace("Key: `saas`.", "Key: `ai`."))))
check("a system type that does not end with its measure is flagged",
      any("Multi-tenant SaaS' does not end" in e for e in guide_errors(
          GUIDE.replace("5. *Measure:* How much may one tenant's peak", "5. How much may one tenant's peak"))))
ai_start = GUIDE.index("### AI and machine-learning components")
ai_end = GUIDE.index("### Multi-tenant SaaS")
check("a system type with too few questions is flagged",
      any("fewer than 3 questions" in e for e in guide_errors(
          GUIDE[:ai_start] + "### AI and machine-learning components\n\nKey: `ai`.\n\n1. Why?\n2. *Measure:* How?\n\n"
          + GUIDE[ai_end:])))

# --------------------------------------------------------------------------- #
# QAW facilitation playbook (self-check)
# --------------------------------------------------------------------------- #

PLAYBOOK = (Path(__file__).resolve().parent.parent / "references" / "qaw-facilitation-playbook.md").read_text(encoding="utf-8")


def playbook_errors(text: str) -> list[str]:
    return run_checker(validate.check_qaw_playbook, "references/qaw-facilitation-playbook.md", text)


check("shipped facilitation playbook passes", playbook_errors(PLAYBOOK) == [])
check("a format with no timebox table is flagged",
      any("no timebox table for format 'remote'" in e for e in playbook_errors(PLAYBOOK.replace("### remote", "### online"))))
check("an unknown timebox table is flagged", any("'online' is not a known format" in e
                                                  for e in playbook_errors(PLAYBOOK.replace("### remote", "### online"))))
check("a format that skips a step is flagged",
      any("'half-day' never runs Step 6" in e for e in playbook_errors(
          PLAYBOOK.replace("| Step 6 — Scenario consolidation | 15 |\n", ""))))
check("a block without whole minutes is flagged",
      any("block 'Step 6 — Scenario consolidation' has no whole minutes" in e for e in playbook_errors(
          PLAYBOOK.replace("| Step 6 — Scenario consolidation | 15 |", "| Step 6 — Scenario consolidation | ~15 |"))))
check("a Next day row with minutes is flagged",
      any("'Next day' takes no minutes" in e for e in playbook_errors(
          PLAYBOOK.replace("| Next day | — |", "| Next day | 30 |", 1))))
check("a format not described in 'Choose a format' is flagged",
      any("'half-day' is not described" in e for e in playbook_errors(PLAYBOOK.replace("**half-day**", "half-day"))))
dm_start, dm_end = PLAYBOOK.index("## Difficult moments"), PLAYBOOK.index("## Scenarios that hold up")
check("a difficult-moments table with too few rows is flagged",
      any("Difficult moments" in e for e in playbook_errors(
          PLAYBOOK[:dm_start] + "## Difficult moments\n\n| Signal | What to do | What to say |\n|---|---|---|\n"
          "| Quiet | Ask | \"Hi\" |\n\n" + PLAYBOOK[dm_end:])))
check("a playbook without 'After the workshop' is flagged",
      any("'After the workshop'" in e for e in playbook_errors(PLAYBOOK.replace("## After the workshop", "## Later"))))
check("a playbook without timeboxes is flagged",
      any("no 'Timeboxes' section" in e for e in playbook_errors(PLAYBOOK.replace("## Timeboxes", "## Times"))))
check("a missing playbook file is reported",
      any("missing" in e for e in validate.check_qaw_playbook(Path("/nonexistent/qaw-facilitation-playbook.md"))))

# --------------------------------------------------------------------------- #
# QAW report — format and Step 7 vote arithmetic
# --------------------------------------------------------------------------- #

def qaw_vote_errors(text: str) -> list[str]:
    return [e for e in qaw(text) if e.startswith("Step 7") or "format" in e.lower()]


check("the example's format and vote table pass", qaw_vote_errors(QAW_EXAMPLE) == [])
check("every known format is accepted",
      all(qaw_vote_errors(QAW_EXAMPLE.replace("**Format**: half-day", f"**Format**: {f}")) == []
          for f in validate.QAW_FORMATS))
check("an unknown format is flagged",
      any("format 'full-day'" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace("**Format**: half-day", "**Format**: full-day"))))
check("a report without a format line passes",
      qaw_vote_errors(QAW_EXAMPLE.replace("- **Format**: half-day\n", "")) == [])
check("a row total that does not add up is flagged",
      any("CS-2 total is 3" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace("| CS-2 | 1 | 1 | 0 | 0 | 0 | 2 |",
                                                                              "| CS-2 | 1 | 1 | 0 | 0 | 0 | 3 |"))))
over = QAW_EXAMPLE.replace("| CS-6 | 0 | 0 | 0 | 0 | 0 | 0 |", "| CS-6 | 1 | 0 | 0 | 0 | 0 | 1 |")
check("a participant over the budget is flagged", any("ST-1 cast 3 votes, over the budget of 2" in e
                                                      for e in qaw_vote_errors(over)))
check("a budget that is not 30 % of the consolidated scenarios is flagged",
      any("vote budget 3 is not 30 %" in e for e in qaw_vote_errors(
          QAW_EXAMPLE.replace("= **2** votes per stakeholder", "= **3** votes per stakeholder"))))
ranked = "**Ranked**: CS-1 (3) = CS-5 (3) > CS-2 (2) > CS-3 (1) = CS-4 (1) > CS-6 (0)."
check("the vote fixture holds the expected ranking line", ranked in QAW_EXAMPLE)
check("a ranking out of order is flagged",
      any("puts CS-3 (1) above CS-2 (2)" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace(
          ranked, "**Ranked**: CS-1 (3) = CS-5 (3) > CS-3 (1) > CS-2 (2) > CS-4 (1) > CS-6 (0).")))
      )
check("a ranking count that differs from the table is flagged",
      any("gives CS-2 4 votes, the table 2" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace("CS-2 (2)", "CS-2 (4)"))))
check("'=' between different totals is flagged",
      any("says CS-5 = CS-2" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace("CS-5 (3) > CS-2 (2)", "CS-5 (3) = CS-2 (2)"))))
check("'>' between equal totals is flagged",
      any("says CS-1 > CS-5" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace("CS-1 (3) = CS-5 (3)", "CS-1 (3) > CS-5 (3)"))))
check("a ranking that leaves a scenario out is flagged",
      any("leaves out CS-6" in e for e in qaw_vote_errors(QAW_EXAMPLE.replace(" > CS-6 (0).", "."))))
tpl = (Path(__file__).resolve().parent.parent / "templates" / "qaw-report.md").read_text(encoding="utf-8")
check("the template's placeholder Step 7 raises no vote arithmetic error", validate._qaw_vote_errors(tpl) == [])
check("a non-numeric vote cell switches the arithmetic off rather than guessing",
      validate._qaw_vote_errors(QAW_EXAMPLE.replace("| CS-1 | 1 | 0 | 0 | 2 | 0 | 3 |", "| CS-1 | one | 0 | 0 | 2 | 0 | 3 |")) == [])
check("a report with no Step 7 has no vote errors", validate._qaw_vote_errors("# Q\n\n## Step 1\n") == [])

check("a Step 7 with no vote table raises no vote error",
      validate._qaw_vote_errors("## Step 7 — Scenario prioritisation\n\nVoting by a show of hands.\n") == [])
check("a parked-question row without a PQ ID is ignored",
      validate._qaw_parked_question_errors("## Parked questions\n\n| ID | Question | Owner | Status |\n|---|---|---|---|\n"
                                           "| — | later? | | |\n") == [])
check("a system-type section with no types is flagged",
      any("has no system types" in e for e in guide_errors(
          GUIDE[:st_section] + "## Questions by system type\n\nNone yet.\n\n" + GUIDE[st_end:])))
check("a one-cell timebox row is skipped, not misread",
      playbook_errors(PLAYBOOK.replace("| Wrap-up — parked questions and next steps | 15 |\n\n### one-day",
                                       "| Wrap-up — parked questions and next steps | 15 |\n|\n\n### one-day")) == [])

# --------------------------------------------------------------------------- #
# QAW report — the long-standing structural rules
# --------------------------------------------------------------------------- #

def qaw_has(text: str, needle: str) -> bool:
    return any(needle in e for e in qaw(text))


check("a refined scenario without its diagram is flagged",
      qaw_has(QAW_EXAMPLE.replace("![CS-5 six-part scenario](diagrams/scenario-CS-5.png)", ""),
              "refined scenario CS-5 has no embedded six-part scenario diagram"))
no_cs5_handoff = QAW_EXAMPLE.replace("| CS-5 | [UQA-1](../drivers/quality-attributes/UQA-1.md) | refined here (Step 8) |\n", "")
no_cs5_handoff = no_cs5_handoff.replace("UQA-1 (CS-5)", "UQA-1 (from the usability scenario)")
no_cs5_handoff = no_cs5_handoff.replace("(refined into `UQA-1` in the drivers register)", "(refined in the drivers register)")
no_cs5_handoff = no_cs5_handoff.replace("CS-5 (refined into UQA-1)", "CS-5")
check("a refined scenario never mapped to a register ID is flagged",
      qaw_has(no_cs5_handoff, "CS-5 is never mapped to a <ATTR>QA-<n> register ID"))
check("a brainstorm table without a Type column is flagged",
      qaw_has(QAW_EXAMPLE.replace("| ID | Scenario (stimulus · environment · response) | Type | Contributor | Driver(s) |",
                                  "| ID | Scenario (stimulus · environment · response) | Kind | Contributor | Driver(s) |"),
              "has no Type column"))
check("a diagram named as a bare backtick path is flagged",
      qaw_has(QAW_EXAMPLE + "\nSee `diagrams/scenario-CS-1.png`.\n", "bare backtick path"))
check("a report missing a step is flagged",
      qaw_has(re.sub(r"(?i)consolidat", "merg", QAW_EXAMPLE), "missing a step about 'consolidat'"))
no_tree = QAW_EXAMPLE.replace("utility tree", "priority table").replace("Utility tree", "Priority table")
check("a report without a utility tree is flagged", qaw_has(no_tree, "has no utility tree"))
check("utility-tree leaves without a (V, R) pair are flagged",
      qaw_has(QAW_EXAMPLE.replace("(H, H)", "high").replace("(H, M)", "high").replace("(M, M)", "medium")
              .replace("`(V, R)`", "priority"), "carry no (V, R) pair"))
check("a utility tree drawn as a mindmap is flagged",
      qaw_has(QAW_EXAMPLE + "\n```mermaid\nmindmap\n  root((Utility))\n```\n", "must be a table, not a mindmap"))
check("a report that never says its raw scenarios are kept verbatim is flagged",
      qaw_has(QAW_EXAMPLE.replace("verbatim", "as said").replace("raw", "first").replace("Raw", "First"),
              "verbatim"))

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
