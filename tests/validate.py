#!/usr/bin/env python3
"""
Validator for the sei-architecture-methodology plugin and the artifacts it produces.

Modes
-----
  python tests/validate.py --self            check the plugin's own structure (skills, plugin.json,
                                             commands, templates, embedded diagrams)
  python tests/validate.py <file> [<file>…]  check produced artifacts:
        *-Architecture.md     -> 9 sections + mermaid rules
        *-session.md          -> header fields, status, driver coverage in the iteration plan
        drivers.md            -> four driver kinds, attribute-prefixed QA IDs, traceability present
        *.mmd / any *.md      -> mermaid diagram rules on every diagram / fenced ```mermaid block
  python tests/validate.py                   with no args: --self, then every architecture/**/*.md

Exit code 0 if everything passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# An architectural-driver ID: BG-1, UC-2, CON-3, or <ATTR>QA-<n> (AQA-1, SQA-2, PQA-3, SCQA-1…)
DRIVER_RE = re.compile(r"\b(BG-\d+|UC-\d+|CON-\d+|[A-Z]{1,4}QA-\d+|AC-\d+)\b")
QA_ID_RE = re.compile(r"\b([A-Z]{1,4}QA)-\d+\b")
BARE_QAS_RE = re.compile(r"\bQAS-\d+\b")  # the deprecated flat prefix — must not appear as an ID

C4_KEYWORDS = {"C4Context", "C4Container", "C4Component", "C4Deployment", "C4Dynamic"}
LEAF_RE = re.compile(
    r"\b(?:Person|Container|Component|System|ContainerDb|ComponentDb|SystemDb"
    r"|Person_Ext|System_Ext|Container_Ext|Component_Ext|SystemQueue|ContainerQueue)\("
)
ALIAS_RE = re.compile(
    r"\b(?:Person|Container|Component|System|ContainerDb|ComponentDb|SystemDb"
    r"|Person_Ext|System_Ext|Container_Ext|Component_Ext|Boundary|Enterprise_Boundary"
    r"|System_Boundary|Container_Boundary)\(([^,)]+)"
)


# --------------------------------------------------------------------------- #
# Diagram checks (shared by .mmd files and fenced ```mermaid blocks)
# --------------------------------------------------------------------------- #

def check_diagram(block: str, label: str) -> list[str]:
    errs: list[str] = []
    lines = [l for l in block.strip().splitlines()]
    if not lines:
        return [f"{label}: empty diagram"]

    # skip a leading YAML front-matter / config block (---\n…\n---)
    body = lines[:]
    if body and body[0].strip() == "---":
        try:
            end = next(i for i in range(1, len(body)) if body[i].strip() == "---")
            body = body[end + 1:]
        except StopIteration:
            errs.append(f"{label}: unterminated '---' front-matter")
    body = [l for l in body if l.strip()]
    if not body:
        return errs + [f"{label}: no diagram body"]

    dtype = body[0].strip().split()[0]

    # Rule 1 — a title is present
    if dtype in C4_KEYWORDS:
        line2 = body[1].strip() if len(body) > 1 else ""
        if not line2.startswith("title"):
            errs.append(f"{label}: {dtype} needs a 'title' line right after the keyword")
    elif dtype == "sequenceDiagram":
        line2 = body[1].strip() if len(body) > 1 else ""
        if not line2.startswith("title"):
            errs.append(f"{label}: sequenceDiagram needs 'title …' on the next line")
    else:  # flowchart / classDiagram / stateDiagram-v2 / mindmap / erDiagram
        if not re.search(r"^\s*(%%(?!\s*name:)|title\b)", block, re.MULTILINE):
            errs.append(f"{label}: {dtype} needs a title in a leading '%% …' comment")

    # Rule 2 — aliases have no spaces
    for m in ALIAS_RE.finditer(block):
        alias = m.group(1).strip()
        if " " in alias:
            errs.append(f"{label}: space in alias {alias!r}")

    # Rule 6 — ≤ 10 leaf nodes
    leaf_n = len(LEAF_RE.findall(block))
    if dtype in C4_KEYWORDS and leaf_n > 10:
        errs.append(f"{label}: {dtype} has {leaf_n} nodes (max 10 — split the diagram)")

    # Rule 7 — C4 container/component diagrams with real content declare a boundary
    if dtype in {"C4Container", "C4Component"} and leaf_n > 0 \
            and not re.search(r"\b(Enterprise_|System_|Container_)?Boundary\(", block):
        errs.append(f"{label}: {dtype} should wrap owned elements in a Boundary(...)")

    # Rule 8 — sequence specifics
    if dtype == "sequenceDiagram":
        msg = [l for l in body if re.search(r"-?->>|-->>|->>|-\)|--\)", l)]
        if len(msg) > 4 and "autonumber" not in block:
            errs.append(f"sequenceDiagram {label}: >4 steps but no 'autonumber'")
        for l in msg:
            lbl = l.split(":", 1)[1] if ":" in l else ""
            if ";" in lbl:
                errs.append(f"sequenceDiagram {label}: ';' in message text — {l.strip()!r}")

    # Rule 5 — C4 relationships carry a label
    for m in re.finditer(r"\bRel(?:_[UDLR]|_Back)?\(([^)]*)\)", block):
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) < 3 or not parts[2].strip().strip('"'):
            errs.append(f"{label}: Rel(...) without a label — {m.group(0)[:60]}")

    title_comment = ""
    tc = re.search(r"^\s*%%(?!\s*name:)\s*(.+)$", block, re.MULTILINE)
    if tc:
        title_comment = tc.group(1).lower()

    # Quality attribute scenario diagram must be horizontal (flowchart LR)
    if "quality attribute scenario" in title_comment or "six-part scenario" in title_comment:
        if not re.match(r"flowchart\s+LR\b", body[0].strip()):
            errs.append(f"{label}: quality attribute scenario diagram must be horizontal — 'flowchart LR'")
        for part in ("source of stimulus", "stimulus", "artifact", "environment", "response"):
            if part not in block.lower():
                errs.append(f"{label}: scenario diagram is missing the '{part}' box")

    # Context / Container diagrams must follow C4 principles
    is_c4_struct = dtype in {"C4Context", "C4Container"} or (
        dtype.startswith("flowchart") and re.search(r"c4 level\s*[12]|context —|container diagram", title_comment)
    )
    if is_c4_struct and dtype.startswith("flowchart"):
        if "subgraph " not in block:
            errs.append(f"{label}: C4 context/container diagram needs an explicit system boundary (subgraph)")
        unlabelled = len(re.findall(r"-->(?!\s*\|)", block))
        if unlabelled:
            errs.append(f"{label}: {unlabelled} unlabelled relationship(s) — every C4 edge carries an action label")
        if leaf_n == 0:
            n_nodes = len(re.findall(r'^\s*\w+[\[(]', block, re.MULTILINE))
            if n_nodes > 12:
                errs.append(f"{label}: {n_nodes} elements — a C4 context/container diagram stays ≤ ~10 (split it)")

    return errs


def diagrams_in_markdown(text: str) -> list[str]:
    return re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL)


# --------------------------------------------------------------------------- #
# Artifact checks
# --------------------------------------------------------------------------- #

NUM_RE = re.compile(r"\d")
# IDs carry digits too (PQA-1, BG-2, CS-3); a "has a number" check must not count them.
ID_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]{0,6}-\d+\b")


def has_measure(text: str) -> bool:
    return bool(NUM_RE.search(ID_TOKEN_RE.sub("", text)))
BEST_PRACTICE = True  # deep, best-practice checks on produced artifacts (not just syntax)


def _table_rows(text: str, header_contains: str) -> list[list[str]]:
    """Return the data rows of the first GFM table whose header row contains `header_contains`."""
    rows: list[list[str]] = []
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "|" in ln and header_contains.lower() in ln.lower() and i + 1 < len(lines) \
                and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            for r in lines[i + 2:]:
                if "|" not in r or not r.strip():
                    break
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                if set("".join(cells)) <= set("-: "):
                    continue
                rows.append(cells)
            break
    return rows


def _traceability_orphans(text: str, bgs: set, ucs: set, qas: set, cons: set) -> list[str]:
    errs: list[str] = []
    tr = text.split("raceability", 1)[-1]
    tr_rows = _table_rows("x\n" + tr, "Driver") or _table_rows("x\n" + tr, "Supports")
    if not tr_rows:
        return errs
    supported_bgs: set = set()
    traced_children: set = set()
    retired: set = set()
    for r in tr_rows:
        row_ids = set(re.findall(r"\b(BG-\d+|UC-\d+|CON-\d+|[A-Z]{1,4}QA-\d+)\b", " ".join(r)))
        if any(c.strip().lower() == "retired" for c in r):
            retired |= row_ids          # a retired driver is not an orphan
            continue
        child = {i for i in row_ids if not i.startswith("BG-")}
        bg_here = {i for i in row_ids if i.startswith("BG-")}
        if child and bg_here:
            traced_children |= child
            supported_bgs |= bg_here
    orphan_bgs = bgs - supported_bgs - retired
    orphan_children = (ucs | qas | cons) - traced_children - retired
    if orphan_bgs:
        errs.append(f"business goals with no UC/QA support in the matrix: {', '.join(sorted(orphan_bgs))}")
    if orphan_children:
        errs.append(f"drivers not traced to a business goal in the matrix: {', '.join(sorted(orphan_children))}")
    return errs


def check_architecture(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    for i in range(1, 10):
        if not re.search(rf"^##\s+{i}\.", text, re.MULTILINE):
            errs.append(f"missing section '## {i}.'")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"diagram #{j}")
    # every sequence diagram is followed by prose
    for m in re.finditer(r"```mermaid\nsequenceDiagram\b.*?```", text, re.DOTALL):
        after = text[m.end():].lstrip("\n").splitlines()
        first = after[0] if after else ""
        if not first or first.startswith(("#", "```", "|")):
            errs.append("a sequenceDiagram is not followed by a plain-English description")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs — use attribute-prefixed IDs (AQA-, SQA-, …)")
    # best practice: §9 design decisions cite driver IDs
    dec = text.split("## 9.", 1)[-1] if "## 9." in text else ""
    dec_rows = _table_rows(dec, "Decision") or _table_rows(dec, "Rationale")
    for r in dec_rows:
        joined = " ".join(r)
        if not DRIVER_RE.search(joined):
            errs.append(f"§9 decision row cites no driver ID: {joined[:70]!r}")
    if "## 9." in text and not dec_rows:
        errs.append("§9 Design decisions has no decision rows")
    if (path.parent / "adr").is_dir():
        for r in dec_rows:
            if not re.search(r"ADR-\d+", " ".join(r)):
                errs.append(f"§9 decision row has no ADR link although adr/ exists: {' '.join(r)[:60]!r}")
    # best practice: no leftover placeholders
    if re.search(r"<name>|<one line>|<Plain-English explanation\.>|TODO", text):
        errs.append("contains unfilled template placeholders (<name>, <one line>, TODO, …)")
    return errs


def check_session(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    for field in ("**Date**", "**Purpose**", "**Status**"):
        if field not in text:
            errs.append(f"missing header field {field}")
    m = re.search(r"\*\*Status\*\*:\s*(\S+)", text)
    if m and m.group(1).lower().rstrip(".") not in ("active", "completed", "draft"):
        errs.append(f"unexpected status {m.group(1)!r}")
    if "## Iteration Plan" in text:
        pre, _, rest = text.partition("## Iteration Plan")
        defined = {d for d in DRIVER_RE.findall(pre)}
        plan = re.split(r"\n##\s", rest, maxsplit=1)[0]
        covered = set(DRIVER_RE.findall(plan))
        missing = defined - covered
        if missing:
            errs.append(f"drivers not covered by the Iteration Plan: {', '.join(sorted(missing))}")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs")
    return errs


def check_drivers(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    bgs = set(re.findall(r"\bBG-\d+\b", text))
    ucs = set(re.findall(r"\bUC-\d+\b", text))
    qas = set(re.findall(r"\b[A-Z]{1,4}QA-\d+\b", text))
    cons = set(re.findall(r"\bCON-\d+\b", text))
    if not bgs:
        errs.append("no business goals (BG-n)")
    if not ucs:
        errs.append("no use cases (UC-n)")
    if not qas:
        errs.append("no quality attribute scenarios (<ATTR>QA-n)")
    if "raceability" not in text:
        errs.append("no traceability matrix section")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs — use AQA-/SQA-/PQA-/… ")

    # best practice: business-goal wording
    for r in _table_rows(text, "Goal"):
        joined = " ".join(r).lower()
        if joined and not ("need" in joined and ("so that" in joined or "so-that" in joined)):
            errs.append(f"business goal not in '<who> needs <what> so that <why>' form: {' '.join(r)[:70]!r}")

    # best practice: QA scenario rows carry a numeric response measure + an ISO 25010 class
    qa_rows = _table_rows(text, "Response measure") or _table_rows(text, "One-line scenario") \
        or _table_rows(text, "ISO 25010")
    for r in qa_rows:
        joined = " ".join(r)
        if re.search(r"[A-Z]{1,4}QA-\d+", joined) and not has_measure(joined):
            errs.append(f"QA scenario row has no numeric measure: {joined[:80]!r}")

    # best practice: traceability has no orphans
    errs += _traceability_orphans(text, bgs, ucs, qas, cons)
    return errs


# --------------------------------------------------------------------------- #
# Split drivers directory: architecture/drivers/{business-goals,use-cases,constraints,quality-attributes}/*.md
# --------------------------------------------------------------------------- #

SIX_PARTS = ("Source of stimulus", "Stimulus", "Artifact", "Environment", "Response",
             "Response measure")


def _has_diagram(text: str) -> bool:
    return "```mermaid" in text or "```plantuml" in text or "@startuml" in text


def _has_image_line(text: str) -> bool:
    return bool(re.search(r"^!\[[^\]]*\]\([^)]+\.(png|svg)\)\s*$", text, re.MULTILINE))


def check_bg_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not re.search(r"\bBG-\d+\b", text):
        errs.append("no BG-<n> id in the file")
    low = text.lower()
    if "need" not in low or "so that" not in low:
        errs.append("business goal not stated as '<who> needs <what> so that <why>'")
    if "**status**" not in low and "status:" not in low:
        errs.append("no Status field")
    return errs


def check_uc_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    if not re.search(r"\bUC-\d+\b", text):
        errs.append("no UC-<n> id in the file")
    for field in ("primary actor", "trigger"):
        if field not in low:
            errs.append(f"use case missing '{field}'")
    if not re.search(r"main success scenario", low):
        errs.append("use case missing a 'Main success scenario'")
    if not re.search(r"^\s*1\.\s+\S", text, re.MULTILINE):
        errs.append("main success scenario is not a numbered list")
    if "**status**" not in low:
        errs.append("no Status field")
    dia = path.parent / "diagrams"
    src_exists = any((dia / f"{path.stem}{ext}").is_file() for ext in (".puml", ".mmd", ".mermaid"))
    if not (_has_diagram(text) or src_exists):
        errs.append("use case has no UML use case diagram (```plantuml/```mermaid block "
                    "or a diagrams/UC-<n>.puml|.mmd source)")
    if not _has_image_line(text):
        errs.append("use case diagram is not embedded as a ![...](diagrams/UC-*.png) image line")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"{path.name} diagram #{j}")
    return errs


def check_con_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    if not re.search(r"\bCON-\d+\b", text):
        errs.append("no CON-<n> id in the file")
    if not re.search(r"business|technical|regulatory", low):
        errs.append("constraint has no type (business / technical / regulatory)")
    if "source" not in low:
        errs.append("constraint has no Source")
    if "**status**" not in low:
        errs.append("no Status field")
    return errs


def check_qa_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' id")
    if not re.search(r"\b[A-Z]{1,4}QA-\d+\b", text):
        errs.append("no <ATTR>QA-<n> id in the file")
    for part in SIX_PARTS:
        if part.lower() not in text.lower():
            errs.append(f"six-part scenario missing '{part}'")
    if "25010" not in text:
        errs.append("no ISO/IEC 25010 classification")
    # numeric response measure
    m = re.search(r"Response measure\**\s*\|(.+)", text)
    if m and not NUM_RE.search(m.group(1)):
        errs.append("Response measure is not numeric")
    if "**status**" not in text.lower():
        errs.append("no Status field")
    dia = path.parent / "diagrams"
    src_exists = any((dia / f"scenario-{path.stem}{ext}").is_file()
                     for ext in (".puml", ".mmd", ".mermaid"))
    if not (_has_diagram(text) or src_exists):
        errs.append("quality attribute has no six-part scenario diagram (```mermaid block or a "
                    "diagrams/scenario-<ATTR>QA-<n>.puml|.mmd source)")
    if not _has_image_line(text):
        errs.append("scenario diagram is not embedded as a ![...](diagrams/scenario-*.png) image line")
    puml_src = (dia / f"scenario-{path.stem}.puml").is_file()
    if puml_src and "```mermaid" not in text and not re.search(
            r"\]\(\s*(?:\./)?diagrams/scenario-" + re.escape(path.stem) + r"\.puml\s*\)", text):
        errs.append("PlantUML scenario diagram: no link to the diagrams/scenario-*.puml source "
                    "(PlantUML is referenced by a source link, not inlined)")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"{path.name} diagram #{j}")
    return errs


def check_drivers_index(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs")
    if "raceability" not in text:
        errs.append("drivers README has no traceability matrix")
    if "overage" not in text:
        errs.append("drivers README has no coverage check")
    if "hange log" not in text:
        errs.append("drivers README has no change log")
    if "utility tree" not in text.lower() and "utility-tree" not in text.lower():
        errs.append("drivers README does not reference the quality-attribute utility tree")
    # driver files are referenced as relative Markdown links, not bare backtick paths
    if not re.search(r"\]\((?:\./)?(?:business-goals|use-cases|constraints|quality-attributes)/"
                     r"[A-Za-z0-9-]+\.md\)", text):
        errs.append("driver files are not linked as relative Markdown links "
                    "(use [UC-1](use-cases/UC-1.md), not a backtick path)")
    bgs = set(re.findall(r"\bBG-\d+\b", text))
    ucs = set(re.findall(r"\bUC-\d+\b", text))
    qas = set(re.findall(r"\b[A-Z]{1,4}QA-\d+\b", text))
    cons = set(re.findall(r"\bCON-\d+\b", text))
    if not (bgs and ucs and qas):
        errs.append("drivers README does not list all of business goals, use cases, and QA scenarios")
    errs += _traceability_orphans(text, bgs, ucs, qas, cons)
    return errs


def check_drivers_dir(root: Path) -> list[str]:
    """Cross-file checks over an architecture/drivers/ directory."""
    errs: list[str] = []
    idx = root / "README.md"
    if not idx.is_file():
        idx = root / "index.md"        # legacy fallback
    if not idx.is_file():
        errs.append("architecture/drivers/README.md is missing")
    kinds = {
        "business-goals": re.compile(r"BG-\d+\.md$"),
        "use-cases": re.compile(r"UC-\d+\.md$"),
        "constraints": re.compile(r"CON-\d+\.md$"),
        "quality-attributes": re.compile(r"[A-Z]{1,4}QA-\d+\.md$"),
        "concerns": re.compile(r"AC-\d+\.md$"),          # optional kind: ADD architectural concerns
    }
    # the package index every sub-package's Navigation footer links up to
    if not (root.parent / "README.md").is_file():
        errs.append(f"{root.parent}/README.md (architecture package index) is missing — /drivers "
                    f"creates it from templates/architecture-readme.md; footers link up to it")
    present = {}
    for sub, pat in kinds.items():
        d = root / sub
        files = sorted(f for f in d.glob("*.md")) if d.is_dir() else []
        present[sub] = [f for f in files if pat.search(f.name)]
        allowed = {"index.md", "README.md", "utility-tree.md"}
        if d.is_dir():
            for f in files:
                if not pat.search(f.name) and f.name not in allowed:
                    errs.append(f"{sub}/{f.name}: name does not match the {sub} id pattern")
            if not (d / "README.md").is_file():
                errs.append(f"{sub}/README.md index is missing")
    if not present.get("business-goals"):
        errs.append("no business-goals/BG-*.md files")
    if not present.get("use-cases"):
        errs.append("no use-cases/UC-*.md files")
    if not present.get("quality-attributes"):
        errs.append("no quality-attributes/<ATTR>QA-*.md files")
    if not (root / "quality-attributes" / "utility-tree.md").is_file():
        errs.append("quality-attributes/utility-tree.md is missing")
    errs += _driver_status_errors(root)
    # every id in the top README has a file and vice versa
    if idx.is_file():
        itext = idx.read_text(encoding="utf-8")
        for sub, files in present.items():
            ids_in_files = {f.stem for f in files}
            for fid in ids_in_files:
                if fid not in itext:
                    errs.append(f"{sub}/{fid}.md exists but {fid} is not listed in the drivers README")
    return errs


DRIVER_ID_RE = re.compile(r"(?<![\w-])(?:BG|UC|CON|AC)-\d+(?![\w-])|(?<![\w-])[A-Z]{1,4}QA-\d+(?![\w-])")


def _field(text: str, name: str) -> str:
    """A driver file's `- **Name**: value`, lower-cased, without emphasis or a parenthetical note."""
    m = re.search(r"^[ \t]*-[ \t]*\*\*" + name + r"\*\*[ \t]*:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE)
    return re.sub(r"\s*\(.*$", "", m.group(1)).strip(" `*_").lower() if m else ""


def _driver_status_errors(root: Path) -> list[str]:
    """Every copy of a driver's status — its kind's index, the README matrix, the utility tree —
    and its priority in the kind's index agree with the driver file. scripts/driverstatus.py
    writes them together; this catches a copy edited by hand."""
    files = {f.stem: f for f in root.glob("*/*.md") if DRIVER_ID_RE.fullmatch(f.stem)}
    facts = {k: (_field(f.read_text(encoding="utf-8"), "Status"),
                 _field(f.read_text(encoding="utf-8"), "Priority")) for k, f in files.items()}
    errs: list[str] = []
    tables = [p for p in sorted(root.glob("*/README.md"))] + [root / "README.md",
                                                             root / "quality-attributes" / "utility-tree.md"]
    for path in tables:
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, ln in enumerate(lines[:-1]):
            if not (ln.lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
                continue
            head = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
            if "status" not in head:
                continue
            id_col = next((j for j, h in enumerate(head) if h.startswith("leaf")), 0)
            st_col = head.index("status")
            pr_col = head.index("priority") if "priority" in head else -1
            for row in lines[i + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                m = DRIVER_ID_RE.search(cells[id_col]) if len(cells) > id_col else None
                if not m or m.group(0) not in facts:
                    continue
                did, (fstatus, fprio) = m.group(0), facts[m.group(0)]
                rel = path.relative_to(root).as_posix()
                if len(cells) > st_col:
                    status = re.sub(r"\s*\(.*$", "", cells[st_col]).strip(" `*_").lower()
                    if fstatus and status and status != fstatus:
                        errs.append(f"{rel}: {did} status is '{status}' but {did}.md says '{fstatus}' "
                                    f"(set statuses with scripts/driverstatus.py)")
                if pr_col >= 0 and len(cells) > pr_col:
                    prio = cells[pr_col].strip(" `*_").lower()
                    if prio in ("high", "medium", "low") and fprio in ("high", "medium", "low") and prio != fprio:
                        errs.append(f"{rel}: {did} priority is '{prio}' but {did}.md says '{fprio}'")
    return errs


def check_scenarios(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs")
    rows = _table_rows(text, "Response measure")
    n = len([r for r in rows if re.search(r"[A-Z]{1,4}QA-\d+", " ".join(r))])
    if rows and not (5 <= n <= 20):
        errs.append(f"{n} quality attribute scenarios — expected 8–15 (min 5, max 20)")
    for r in rows:
        joined = " ".join(r)
        if re.search(r"[A-Z]{1,4}QA-\d+", joined) and not has_measure(joined):
            errs.append(f"scenario row has no numeric response measure: {joined[:80]!r}")
    if rows and "25010" not in text:
        errs.append("no ISO/IEC 25010 classification anywhere in the file")
    # every scenario is drawn: an image line to diagrams/scenario-<ID>.png (both notations) —
    # a fenced mermaid block alone is not enough, the PNG is what was visually verified
    images = " ".join(re.findall(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", text, re.MULTILINE))
    for r in rows:
        m = re.search(r"\b([A-Z]{1,4}QA-\d+)\b", " ".join(r))
        if not m:
            continue
        sid = m.group(1)
        # standalone mode: the diagram is embedded here; register mode: the row links the
        # per-scenario file in architecture/drivers/quality-attributes/ which carries it
        linked = re.search(r"\]\([^)]*\b" + re.escape(sid) + r"\.md\)", text)
        if f"scenario-{sid}." not in images and not linked:
            errs.append(f"{sid}: no embedded scenario diagram and no link to its register file — "
                        f"add ![{sid} six-part scenario](diagrams/scenario-{sid}.png) or link "
                        f"../drivers/quality-attributes/{sid}.md")
    for m in re.finditer(r"`[^`\n]*diagrams/[^`\n]+\.(?:png|svg)`", text):
        errs.append(f"diagram referenced as a bare backtick path, not an image line: {m.group(0)}")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"scenario diagram #{j}")
    return errs


def check_qaw(path: Path) -> list[str]:
    errs: list[str] = []
    raw = path.read_text(encoding="utf-8")
    text = raw.lower()
    # Step 8 — every refined scenario carries its rendered six-part diagram
    m = re.search(r"^##[^\n]*refine[^\n]*$(.*?)(?=^##\s|\Z)", raw, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if m:
        refined = re.findall(r"^###\s+(\S+)", m.group(1), re.MULTILINE)
        images = " ".join(re.findall(r"^!\[[^\]]*\]\(([^)]+\.(?:png|svg))\)\s*$", m.group(1), re.MULTILINE))
        for rid in refined:
            sid = rid.rstrip(":")
            if f"scenario-{sid}." not in images:
                errs.append(f"refined scenario {rid} has no embedded six-part scenario diagram "
                            f"(![...](diagrams/scenario-{rid}.png))")
        # every refined scenario is handed off to a register ID somewhere in the report
        for rid in refined:
            rid = rid.rstrip(":")
            if rid.startswith("CS-") and not re.search(
                    r"^.*\b" + re.escape(rid) + r"\b.*\b[A-Z]{1,4}QA-\d+\b.*$", raw, re.MULTILINE):
                errs.append(f"{rid} is never mapped to a <ATTR>QA-<n> register ID (add the hand-off table)")
    # Step 5 raw scenarios carry their type (use-case / growth / exploratory)
    bm = re.search(r"^##[^\n]*brainstorm[^\n]*$(.*?)(?=^##\s|\Z)", raw, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if bm:
        header = re.search(r"^\|[^\n]*\|\s*$", bm.group(1), re.MULTILINE)
        if header and "type" not in header.group(0).lower():
            errs.append("brainstormed-scenario table has no Type column (use-case / growth / exploratory)")
    for mm in re.finditer(r"`[^`\n]*diagrams/[^`\n]+\.(?:png|svg)`", raw):
        errs.append(f"diagram referenced as a bare backtick path, not an image line: {mm.group(0)}")
    for j, blk in enumerate(diagrams_in_markdown(raw), 1):
        errs += check_diagram(blk, f"QAW diagram #{j}")
    for kw in ("introduction", "business", "architectural plan", "architectural driver",
               "brainstorm", "consolidat", "prioriti", "refine"):
        if kw not in text:
            errs.append(f"QAW report missing a step about '{kw}'")
    if "30" not in text or "vote" not in text:
        errs.append("QAW report does not state the 30%-of-scenarios vote budget")
    if "verbatim" not in text and "raw" not in text:
        errs.append("QAW report should keep raw brainstormed scenarios verbatim (say so)")
    if "utility tree" not in text:
        errs.append("QAW report has no utility tree (build one from the refined scenarios)")
    else:
        if not re.search(r"\(\s*[hml]\s*,\s*[hml]\s*\)", text):
            errs.append("QAW utility-tree leaves carry no (V, R) pair like (H, M)")
        if "mindmap" in text:
            errs.append("QAW utility tree must be a table, not a mindmap")
    errs += _qaw_starting_point_errors(raw)
    errs += _qaw_parked_question_errors(raw)
    errs += _qaw_format_errors(raw)
    errs += _qaw_vote_errors(raw)
    return errs


QAW_ENTRY_MODES = ("greenfield", "partial", "refresh")
# The formats the facilitation playbook times (its ### headings under *Timeboxes*).
QAW_FORMATS = ("two-day", "one-day", "half-day", "remote")


def _qaw_format_errors(raw: str) -> list[str]:
    # Optional header bullet; reports written before formats existed have none.
    head = raw.split("\n## ", 1)[0]
    m = re.search(r"^\s*-\s*\*\*Format\*\*\s*:\s*(.+?)\s*$", head, re.MULTILINE)
    if m and m.group(1).strip().strip("`*_").lower() not in QAW_FORMATS:
        return [f"QAW format {m.group(1).strip()!r} is not one of {' / '.join(QAW_FORMATS)}"]
    return []


def _qaw_vote_errors(raw: str) -> list[str]:
    """Step 7 arithmetic: row totals, the 30 % budget, nobody over budget, and a ranking that
    follows the totals. Cells that are not numbers (template placeholders) are skipped."""
    sec = _qaw_section(raw, r"prioriti")
    if sec is None:
        return []
    lines = sec.splitlines()
    head: list[str] = []
    rows: list[list[str]] = []
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and "total" in ln.lower() and i + 1 < len(lines) \
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            for r in lines[i + 2:]:
                if not r.strip().startswith("|"):
                    break
                rows.append([c.strip() for c in r.strip().strip("|").split("|")])
            break
    if len(head) < 3 or head[-1].lower() != "total":
        return []
    errs: list[str] = []
    people = head[1:-1]
    totals: dict[str, int] = {}
    spent = [0] * len(people)
    numeric = True
    for row in rows:
        m = re.match(r"\s*((?:CS|S)-\d+)\b", row[0].replace("*", ""))
        cells = (row[1:-1] + [""] * len(people))[:len(people)]
        if not m or not all(re.fullmatch(r"\d*", c) for c in cells + [row[-1]]):
            numeric = numeric and not m
            continue
        votes = [int(c or 0) for c in cells]
        spent = [a + b for a, b in zip(spent, votes)]
        totals[m.group(1)] = sum(votes)
        if row[-1] and int(row[-1]) != sum(votes):
            errs.append(f"Step 7: {m.group(1)} total is {row[-1]}, but its votes add up to {sum(votes)}")
    if not totals or not numeric:
        return errs
    budget = re.search(r"\*\*(\d+)\*\*\s*votes?\s+per", sec)
    n_cs = len(re.findall(r"^\|\s*CS-\d+\s*\|", _qaw_section(raw, r"consolidat") or "", re.MULTILINE))
    if budget:
        b = int(budget.group(1))
        if n_cs and b != max(1, -(-n_cs * 3 // 10)):
            errs.append(f"Step 7: vote budget {b} is not 30 % of {n_cs} consolidated scenarios "
                        f"rounded up ({max(1, -(-n_cs * 3 // 10))})")
        for person, n in zip(people, spent):
            if n > b:
                errs.append(f"Step 7: {person} cast {n} votes, over the budget of {b}")
    ranked = re.search(r"^\*\*Ranked\*\*\s*:\s*(.+)$", sec, re.MULTILINE)
    if ranked:
        seq = re.findall(r"((?:CS|S)-\d+)\s*\((\d+)\)\s*([=>])?", ranked.group(1))
        prev = None
        for sid, n, sep in seq:
            n = int(n)
            if sid in totals and totals[sid] != n:
                errs.append(f"Step 7: the ranking gives {sid} {n} votes, the table {totals[sid]}")
            if prev is not None:
                psid, pn, psep = prev
                if pn < n:
                    errs.append(f"Step 7: the ranking puts {psid} ({pn}) above {sid} ({n})")
                elif psep == "=" and pn != n:
                    errs.append(f"Step 7: the ranking says {psid} = {sid}, but they have {pn} and {n} votes")
                elif psep == ">" and pn == n:
                    errs.append(f"Step 7: the ranking says {psid} > {sid}, but both have {n} votes")
            prev = (sid, n, sep)
        listed = {sid for sid, _, _ in seq}
        missing = [sid for sid in totals if sid not in listed]
        if seq and missing:
            errs.append(f"Step 7: the ranking leaves out {', '.join(missing)}")
    return errs


def _qaw_section(raw: str, title_re: str) -> str | None:
    m = re.search(r"^##[^\n]*" + title_re + r"[^\n]*$(.*?)(?=^##\s|\Z)", raw,
                  re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else None


def _qaw_starting_point_errors(raw: str) -> list[str]:
    # Reports written before the entry modes existed have no Starting point; they stay valid.
    sec = _qaw_section(raw, r"starting point")
    if sec is None:
        return []
    m = re.search(r"^\s*-\s*\*\*Entry mode\*\*\s*:\s*(.+?)\s*$", sec, re.MULTILINE)
    if not m:
        return ["QAW Starting point does not state the entry mode "
                "(- **Entry mode**: greenfield / partial / refresh)"]
    mode = m.group(1).strip().strip("`*_").lower()
    if mode not in QAW_ENTRY_MODES:
        return [f"QAW entry mode {m.group(1).strip()!r} is not exactly one of "
                f"{' / '.join(QAW_ENTRY_MODES)}"]
    errs: list[str] = []
    inputs = _table_rows("x\n" + sec, "Input")
    if not any(any(c for c in row) for row in inputs):
        errs.append("QAW Starting point has no inputs table rows (greenfield: "
                    "one row saying it started from open questions)")
    elif mode != "greenfield" and not any(
            row and row[0].strip() and not row[0].strip().lower().startswith("none") for row in inputs):
        errs.append(f"QAW {mode} mode lists no input document in Starting point — the workshop "
                    f"must rely on the documentation available, so name what it read")
    if mode == "refresh":
        bm = _qaw_section(raw, r"brainstorm")
        if bm is not None and "existing" not in bm.lower():
            errs.append("QAW refresh mode: no brainstormed scenario is tagged 'existing' — "
                        "the existing scenarios should enter Step 5 first")
    return errs


def _qaw_parked_question_errors(raw: str) -> list[str]:
    sec = _qaw_section(raw, r"parked question")
    if sec is None:
        return []
    lines = sec.splitlines()
    header: list[str] = []
    errs: list[str] = []
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            header = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
            break
    rows = _table_rows("x\n" + sec, "Question")
    if not rows:
        if "none" not in sec.lower():
            errs.append("QAW Parked questions section has no table and does not say 'None'")
        return errs
    col = {name: header.index(name) for name in ("owner", "status") if name in header}
    for row in rows:
        ids = re.findall(r"\bPQ-\d+\b", " ".join(row))
        if not ids:
            continue
        pid = ids[0]
        for name, idx in col.items():
            if idx >= len(row) or not row[idx].strip():
                errs.append(f"parked question {pid} has no {name}")
    return errs


def check_atam(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    for kw in ("architectural approach", "utility tree", "risk", "non-risk",
               "sensitivity point", "tradeoff point", "risk theme"):
        if kw not in low:
            errs.append(f"ATAM report missing a '{kw}' section")
    if not re.search(r"\*\*mode\*\*", low):
        errs.append("ATAM report has no **Mode** header (Full ATAM | Lightweight)")
    if "utility tree" in low and "(h" not in low.replace(" ", ""):
        errs.append("utility-tree leaves should carry a (V, R) pair like (H, M)")
    if "utility tree" in low and "mindmap" in low:
        errs.append("the utility tree must be a table, not a mindmap")
    for r in _table_rows(text, "Non-risk"):
        # the Non-risks register must fill the "assumption under which it holds" column
        if r and len([c for c in r if c.strip()]) < 3:
            errs.append(f"non-risk row leaves the assumption column empty: {' '.join(r)[:70]!r}")
    for r in _table_rows(text, "Tradeoff"):
        joined = " ".join(r)
        if r and len([c for c in r if c.strip()]) < 3 and " vs " not in joined.lower() and "↑" not in joined:
            errs.append(f"tradeoff row names only one attribute: {joined[:70]!r}")
    for r in _table_rows(text, "Theme"):
        if r and not re.search(r"BG-\d+", " ".join(r)):
            errs.append(f"risk theme not mapped to a business goal: {' '.join(r)[:70]!r}")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"ATAM diagram #{j}")
    return errs


def check_view_packet(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    for sect in ("Primary presentation", "Element catalog", "Context diagram",
                 "Variability guide", "Rationale"):
        if not re.search(re.escape(sect), text, re.IGNORECASE):
            errs.append(f"view packet missing the '{sect}' section")
    if not DRIVER_RE.search(text.split("Rationale", 1)[-1]):
        errs.append("view rationale cites no driver ID")
    # the primary C&C view documents behaviour: a rendered diagram per significant use case
    vt = re.search(r"^\s*-\s*\*\*Viewtype\*\*:\s*(.+)$", text, re.MULTILINE)
    if vt and re.search(r"component-and-connector|c&c", vt.group(1), re.IGNORECASE):
        bm = re.search(r"^###\s*2\.4[^\n]*$(.*?)(?=^##\s|^###\s|\Z)", text, re.MULTILINE | re.DOTALL)
        beh = bm.group(1) if bm else ""
        if not (_has_image_line(beh) or "```mermaid" in beh):
            errs.append("C&C view §2.4 Element behavior has no rendered behaviour diagram "
                        "(one per architecturally significant UC-<n>)")
        elif not re.search(r"\bUC-\d+\b", beh):
            errs.append("C&C view §2.4 behaviour diagram(s) cite no UC-<n>")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"view diagram #{j}")
    return errs


def check_mapping(path: Path) -> list[str]:
    """mapping-between-views.md is how a V&B package proves internal consistency — it must
    contain real cross-view tables, not a placeholder."""
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    n_rows = sum(len(_table_rows(text, h)) for h in ("Module", "Runtime", "Component", "Driver", "Element"))
    if n_rows == 0:
        errs.append("mapping-between-views has no populated mapping table")
    views = set(re.findall(r"\bview-[a-z0-9-]+", text))
    if len(views) < 2:
        errs.append(f"mapping-between-views names {len(views)} view file(s) — it must cross-reference "
                    f"at least two views (view-<name>.md)")
    if re.search(r"<[a-z][^>]*>|\bTODO\b|\bTBD\b", text):
        errs.append("mapping-between-views contains placeholders (<…>, TODO, TBD)")
    return errs


def check_ac_file(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    if not re.search(r"\bAC-\d+\b", text):
        errs.append("no AC-<n> id in the file")
    if "concern" not in low:
        errs.append("architectural concern file does not state the concern")
    if "**status**" not in low:
        errs.append("no Status field")
    return errs


def check_stakeholders(path: Path) -> list[str]:
    """architecture/drivers/stakeholders.md — the one ST-<n> register QAW / ATAM / V&B read."""
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not re.search(r"\bST-\d+\b", text):
        errs.append("stakeholder register has no ST-<n> ids")
    rows = _table_rows(text, "Role")
    if not rows:
        errs.append("stakeholder register has no table with a Role column")
    if re.search(r"<name>|<growth", text):
        errs.append("stakeholder register still contains template placeholders")
    return errs


def check_utility_tree(path: Path) -> list[str]:
    """The utility tree is a TABLE, not a diagram (Cervantes & Kazman, tabular form)."""
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    if "utility" not in low:
        errs.append("utility tree has no root 'Utility'")
    if not re.search(r"\b[A-Z]{1,4}QA-\d+\b", text):
        errs.append("utility tree has no leaf quality attribute scenarios (<ATTR>QA-n)")
    # it must be a GFM table
    if not re.search(r"^\s*\|?[\s:|-]*-{2,}[\s:|-]*\|", text, re.MULTILINE):
        errs.append("utility tree must be a Markdown table (columns: Quality attribute · "
                    "Refinement · Leaf scenario · Priority (V, R) · Status)")
    # a value/importance column and a risk/difficulty column
    if not re.search(r"\|[^|\n]*\b(priority|business value|value|importance)\b[^|\n]*\|",
                     text, re.IGNORECASE):
        errs.append("utility-tree table needs a business-value / (V, R) column")
    if not re.search(r"\(\s*[HML]\s*,\s*[HML]\s*\)", text):
        errs.append("utility-tree leaves carry no (V, R) pair like (H, M)")
    if "25010" not in text:
        errs.append("utility tree does not reference ISO/IEC 25010")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs")
    if re.search(r"^\s*mindmap\b", text, re.MULTILINE) \
            or "```mermaid" in text or "```plantuml" in text:
        errs.append("utility tree must be a table, not a diagram — remove the diagram block")
    return errs


_LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^)\s]+)")


def headerless_tables(text: str) -> list[int]:
    """1-based line numbers of pipe-table blocks with no separator row under the first line —
    GitHub renders them as plain text (usually a paragraph or blank line wedged into a table)."""
    lines = _FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text).splitlines()
    bad, i = [], 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            if not (j > i + 1 and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
                bad.append(i + 1)
            i = j
        else:
            i += 1
    return bad


def crowded_headings(text: str) -> list[int]:
    """1-based line numbers of headings with text on the line directly above — a section glued to
    the end of the previous one (what a careless find-and-replace on a header bullet leaves).
    A heading directly under its parent heading is fine."""
    lines = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"),
                   _FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text), flags=re.DOTALL).splitlines()
    return [i + 1 for i in range(1, len(lines))
            if re.match(r"^#{1,6} \S", lines[i]) and lines[i - 1].strip()
            and not re.match(r"^#{1,6} \S", lines[i - 1])]


def template_meta_errors(path: Path) -> list[str]:
    """Self-description in a template's visible text is copied into every artifact made from it;
    instructions to the writer belong in HTML comments."""
    visible = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    return [f"visible text {m!r} would be copied into every artifact — move the instruction into "
            f"an HTML comment" for m in sorted({m.group(0).lower() for m in META_RE.finditer(_without_code(visible))})]


def mermaid_source_drift(path: Path) -> list[str]:
    """A ```mermaid block above an image line whose PNG has a .mmd source beside it must be that
    source: two sources for one picture drift, and re-rendering the .mmd silently replaces it."""
    text = path.read_text(encoding="utf-8")
    errs = []
    for m in re.finditer(r"```mermaid\n(.*?)```\s*\n+!\[[^\]]*\]\(([^)\s]+\.png)\)", text, re.DOTALL):
        src = (path.parent / m.group(2)).with_suffix(".mmd")
        if src.is_file() and src.read_text(encoding="utf-8").strip() != m.group(1).strip():
            errs.append(f"the mermaid block above {m.group(2)} differs from {src.name} beside it — "
                        f"keep one source (delete the .mmd, or make the block identical)")
    return errs


def broken_links(path: Path) -> list[str]:
    """Report relative Markdown links / images whose target file does not exist on disk."""
    errs: list[str] = []
    # generated reports are flattened concatenations — their inherited relative links
    # are not expected to resolve from the reports/ directory.
    if path.parent.name == "reports":
        return errs
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return errs
    for m in _LINK_RE.finditer(text):
        target = m.group(1).strip().lstrip("<").rstrip(">")
        if not target or target.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        dest = (path.parent / target).resolve()
        if not dest.exists():
            errs.append(f"broken link: {target!r} -> {dest}")
    # a relative path written as code (`../x.png`) is a reference the reader will follow too
    # (a code span that is a link's text is already covered by the link check above)
    for m in re.finditer(r"(?<!\[)`(\.\.?/[^`\s]+\.(?:png|svg|md|mmd|puml))`(?!\]\()", _without_code(text)):
        if not (path.parent / m.group(1)).exists():
            errs.append(f"names a file that does not exist: `{m.group(1)}`")
    return errs


# Filler phrases that mark machine-padded prose. Artifacts are read by people; a sentence
# that needs one of these is better rewritten (see references/writing-style.md, which is the
# one file allowed to name them).
FILLER_RE = re.compile(
    r"\b(leverag(?:es|ed|ing)|seamless(?:ly)?|cutting-edge|state-of-the-art|best-in-class"
    r"|world-class|game-chang\w*|revolutioniz\w*|delv(?:e|es|ed|ing)|utili[sz](?:e|es|ed|ing)"
    r"|holistic\w*|synerg\w*|it is worth noting|it is important to note|in conclusion"
    r"|in today'?s fast)\b",
    re.IGNORECASE)

# Tokens that exist only in templates/. One of these in a finished artifact means a template
# was copied without being filled in.
PLACEHOLDER_TOKENS = (
    "<YYYY-MM-DD>", "<SystemName>", "<System name>", "<name>", "<one line>", "<slug>",
    "<role>", "<short title>", "<who needs", "<goal-phrased",
    "<One or two plain sentences", "<Two or three plain sentences",
    "<only the prefixes that actually appear", "<the (H, H) and (H, M) leaf IDs>",
)

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)

# An artifact describing how it was produced is meta-commentary (writing-style.md): the reader
# needs what the diagram shows, not that someone rendered and checked it.
META_RE = re.compile(r"visually verified|rendered (?:\+|and) (?:visually )?verified"
                     r"|this is the (?:mermaid|plantuml) tree", re.IGNORECASE)


def _without_code(text: str) -> str:
    return _FENCE_RE.sub("", text)


def prose_errors(path: Path) -> list[str]:
    """Human-readability checks shared by every produced Markdown artifact."""
    errs: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return errs
    prose = _without_code(text)
    for m in sorted({m.group(0).lower() for m in FILLER_RE.finditer(prose)}):
        errs.append(f"filler phrase {m!r} — rewrite plainly (references/writing-style.md)")
    for tok in PLACEHOLDER_TOKENS:
        if tok in prose:
            errs.append(f"unfilled template placeholder {tok!r}")
    for m in sorted({m.group(0).lower() for m in META_RE.finditer(prose)}):
        errs.append(f"self-description {m!r} — say what the artifact shows, not how it was made "
                    f"(references/writing-style.md)")
    for n in headerless_tables(text):
        errs.append(f"line {n}: table rows without a header separator — they render as plain text")
    for n in crowded_headings(text):
        errs.append(f"line {n}: heading has no blank line above it")
    # duplicated '- **Key**:' bullets in the header block (before the first '## ') are
    # copy-paste bugs: one Date, one Status, one Owner …
    head = text.split("\n## ", 1)[0]
    seen: dict[str, int] = {}
    for m in re.finditer(r"^- \*\*([^*]+)\*\*:", head, re.MULTILINE):
        seen[m.group(1)] = seen.get(m.group(1), 0) + 1
    for key, n in seen.items():
        if n > 1:
            errs.append(f"header bullet '**{key}**' appears {n} times — remove the duplicate")
    return errs


def check_generic_md(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"{path.name} diagram #{j}")
    return errs


def check_mmd(path: Path) -> list[str]:
    return check_diagram(path.read_text(encoding="utf-8"), path.name)


# --------------------------------------------------------------------------- #
# Template structure: every generated artifact keeps its template's headings
# --------------------------------------------------------------------------- #

# Artifact path (POSIX, matched at the end) → the template that fixes its structure. Files the
# QAW kit writes (qawkit.py fixes their structure, test_qawkit.py pins it) and generated reports
# have none; an example's root README is the package index plus notes on regenerating it.
STRUCTURE_TEMPLATES: tuple[tuple[str, str], ...] = (
    (r"/adr/ADR-\d+\.md$", "adr.md"),
    (r"-session\.md$", "add-session.md"),
    (r"-Architecture\.md$", "architecture-document.md"),
    (r"/atam/atam-report\.md$", "atam-report.md"),
    (r"/business-goals/BG-\d+\.md$", "business-goal.md"),
    (r"/concerns/AC-\d+\.md$", "concern.md"),
    (r"/constraints/CON-\d+\.md$", "constraint.md"),
    (r"/use-cases/UC-\d+\.md$", "use-case.md"),
    (r"/quality-attributes/[A-Z]{1,4}QA-\d+\.md$", "quality-attribute-scenario.md"),
    (r"/drivers/(?:business-goals|use-cases|constraints|quality-attributes|concerns)/README\.md$", "subdir-readme.md"),
    (r"/drivers/README\.md$", "drivers-readme.md"),
    (r"/drivers/stakeholders\.md$", "stakeholders.md"),
    (r"/quality-attributes/utility-tree\.md$", "utility-tree.md"),
    (r"/quality-attributes/scenarios\.md$", "scenarios.md"),
    (r"/qaw/qaw-report(?:-\d{4}-\d{2}-\d{2})?\.md$", "qaw-report.md"),
    (r"/docs/view-[^/]+\.md$", "view-packet.md"),
    (r"/docs/README\.md$", "docs-readme.md"),
    (r"/docs/system-overview\.md$", "system-overview.md"),
    (r"/docs/mapping-between-views\.md$", "mapping-between-views.md"),
    (r"/docs/rationale\.md$", "rationale.md"),
    (r"/docs/directory\.md$", "directory.md"),
    (r"/docs/change-log\.md$", "change-log.md"),
    (r"(?:^|/)architecture/README\.md$", "architecture-readme.md"),
)
_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)
_FENCES_RE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)


def template_for(path: Path) -> Path | None:
    posix = "/" + path.as_posix().lstrip("/")
    for pattern, name in STRUCTURE_TEMPLATES:
        if re.search(pattern, posix):
            return ROOT / "templates" / name
    return None


def heading_list(text: str) -> list[tuple[int, str]]:
    """(level, title) of every heading outside code fences and HTML comments."""
    text = re.sub(r"<!--.*?-->", "", _FENCES_RE.sub("", text), flags=re.DOTALL)
    return [(len(m.group(1)), m.group(2)) for m in _HEADING_RE.finditer(text)]


def heading_key(title: str) -> str:
    """What a heading says, compared loosely: link text only, no code marks or emphasis, no
    parenthetical notes, one kind of separator, lower case."""
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title).replace("`", "").replace("*", "")
    t = re.sub(r"\s*\([^()]*\)", "", t)
    t = re.sub(r"\s*(?::|—|–|\s-\s)\s*", " — ", t)
    return re.sub(r"\s+", " ", t).strip(" .—").lower()


def template_structure(template_text: str) -> list[dict]:
    """The template's headings as nodes: level, title, a pattern for the artifact's heading key
    (placeholders `<…>` and a lone `N` match anything; the artifact may add words after the
    template's), whether it repeats (it has a placeholder) and whether it is optional (it says
    optional / omit in)."""
    nodes = []
    for level, title in heading_list(template_text):
        # a note on when to include the section is not part of its name
        key = heading_key(re.sub(r"\s*[—–]\s*optional\b.*$", "", title, flags=re.IGNORECASE))
        parts = re.split(r"(<[^>]+>|\bn\b)", key)
        pattern = "".join(r"[^\n]+?" if (p.startswith("<") or p == "n") else re.escape(p) for p in parts)
        nodes.append({"level": level, "title": title, "re": re.compile(pattern + r"[^\n]*"),
                      "repeat": level > 1 and bool(re.search(r"<[^>]+>|\bN\b", title)),
                      "optional": bool(re.search(r"\boptional\b|\bomit in\b", title, re.IGNORECASE)),
                      "slot": not re.sub(r"<[^>]+>|\bn\b|[\s—]", "", key)})
    return nodes


def _structure_regex(nodes: list[dict]) -> re.Pattern:
    def build(i: int, parent: int) -> tuple[str, int]:
        out = []
        while i < len(nodes) and nodes[i]["level"] > parent:
            n = nodes[i]
            sub, j = build(i + 1, n["level"])
            group = f"(?:{n['level']}\\t{n['re'].pattern}\\n{sub})"
            out.append(group + {(True, True): "*", (True, False): "+", (False, True): "?",
                                (False, False): ""}[(n["repeat"], n["optional"])])
            i = j
        return "".join(out), i
    return re.compile(build(0, 0)[0])


def check_template_structures() -> list[str]:
    """Every template governs some artifact and is itself a valid structure: the mapping names
    only templates that exist, every template is mapped, and each template matches its own
    heading pattern (so its optional and repeated sections are written the way the check reads
    them)."""
    errs: list[str] = []
    mapped = {name for _, name in STRUCTURE_TEMPLATES}
    for name in sorted(mapped):
        if not (ROOT / "templates" / name).is_file():
            errs.append(f"validate.py STRUCTURE_TEMPLATES names templates/{name}, which does not exist")
    for t in sorted((ROOT / "templates").glob("*.md")):
        if t.name not in mapped:
            errs.append(f"templates/{t.name} is not mapped to the artifacts it governs (STRUCTURE_TEMPLATES)")
        errs += [f"templates/{t.name}: {e}" for e in structure_errors(t, t)]
    return errs


def _ancestors(nodes: list[dict], k: int) -> list[int]:
    out, level = [], nodes[k]["level"]
    for j in range(k - 1, -1, -1):
        if nodes[j]["level"] < level:
            out.append(j)
            level = nodes[j]["level"]
    return out


def structure_errors(path: Path, template: Path | None = None) -> list[str]:
    """Headings the artifact adds, drops, moves or re-levels relative to its template. The
    template's heading pattern decides; an in-order alignment explains a failure."""
    template = template or template_for(path)
    if template is None or not template.is_file():
        return []
    nodes = template_structure(template.read_text(encoding="utf-8"))
    heads = heading_list(path.read_text(encoding="utf-8"))
    if _structure_regex(nodes).fullmatch("".join(f"{lvl}\t{heading_key(t)}\n" for lvl, t in heads)):
        return []
    name = f"templates/{template.name}"

    def fits(k: int, lvl: int, key: str) -> bool:
        return nodes[k]["level"] == lvl and bool(nodes[k]["re"].fullmatch(key))

    errs: list[str] = []
    matched: set[int] = set()
    mislevelled: set[int] = set()
    t, prev = 0, None
    for lvl, title in heads:
        key = heading_key(title)
        k = next((j for j in range(t, len(nodes)) if fits(j, lvl, key)), None)
        if k is None:
            # another round of the repeatable section we are still inside
            k = next((r for r in range(t - 1, -1, -1) if nodes[r]["repeat"] and r in matched
                      and all(nodes[x]["level"] > nodes[r]["level"] for x in range(r + 1, t))
                      and fits(r, lvl, key)), None)
        if k is None:
            dup = next((j for j in sorted(matched) if fits(j, lvl, key) and not nodes[j]["repeat"]), None)
            other = next((j for j in range(len(nodes)) if nodes[j]["level"] != lvl and not nodes[j]["slot"]
                          and nodes[j]["re"].fullmatch(key)), None)
            if dup is not None:
                errs.append(f"section '{'#' * lvl} {title}' appears more than once; {name} has it once")
            elif other is not None:
                mislevelled.add(other)
                errs.append(f"section '{'#' * lvl} {title}' is at level {lvl}; {name} has it at level "
                            f"{nodes[other]['level']} ('{'#' * nodes[other]['level']} {nodes[other]['title']}')")
            elif any(fits(j, lvl, key) and not nodes[j]["slot"] for j in range(len(nodes))):
                errs.append(f"section '{'#' * lvl} {title}' comes after '{prev}'; {name} puts it before")
            else:
                errs.append(f"section '{'#' * lvl} {title}' is not in {name} — use the template's sections "
                            f"and put this content under the one it belongs to")
            continue
        matched.add(k)
        t, prev = k + 1, title
    for k, n in enumerate(nodes):
        skippable = n["optional"] or any(nodes[a]["optional"] and a not in matched for a in _ancestors(nodes, k))
        if k not in matched and k not in mislevelled and not skippable:
            errs.append(f"missing the template section '{'#' * n['level']} {n['title']}' ({name})")
    return errs or [f"headings do not follow the structure of {name} (a section is at the wrong level or repeated)"]


def validate_file(path: Path) -> list[str] | None:
    name = path.name
    parent = path.parent.name

    def _md(res: list[str]) -> list[str]:
        return (res + broken_links(path) + prose_errors(path) + mermaid_source_drift(path)
                + structure_errors(path))

    if name.endswith("-Architecture.md"):
        return _md(check_architecture(path))
    # an earlier workshop kept beside the current one; its dated name must not read as an ADD session
    if re.match(r"qaw-report-\d{4}-\d{2}-\d{2}\.md$", name):
        return _md(check_qaw(path))
    if name.endswith("-session.md") or re.search(r"-\d{4}-\d{2}-\d{2}\.md$", name):
        return _md(check_session(path))
    if name == "drivers.md":
        return _md(check_drivers(path))
    if name in ("README.md", "index.md") and parent == "drivers":
        return _md(check_drivers_index(path))
    if name == "utility-tree.md":
        return _md(check_utility_tree(path))
    if name == "mapping-between-views.md":
        return _md(check_mapping(path))
    if parent == "business-goals" and re.match(r"BG-\d+\.md$", name):
        return _md(check_bg_file(path))
    if parent == "use-cases" and re.match(r"UC-\d+\.md$", name):
        return _md(check_uc_file(path))
    if parent == "constraints" and re.match(r"CON-\d+\.md$", name):
        return _md(check_con_file(path))
    if parent == "concerns" and re.match(r"AC-\d+\.md$", name):
        return _md(check_ac_file(path))
    if name == "stakeholders.md":
        return _md(check_stakeholders(path))
    if parent == "quality-attributes" and re.match(r"[A-Z]{1,4}QA-\d+\.md$", name):
        return _md(check_qa_file(path))
    if name == "scenarios.md":
        return _md(check_scenarios(path))
    if name == "qaw-report.md":
        return _md(check_qaw(path))
    if name == "atam-report.md":
        return _md(check_atam(path))
    if name.startswith("view-") and name.endswith(".md"):
        return _md(check_view_packet(path))
    if name.endswith((".mmd", ".mermaid")):
        return check_mmd(path)
    if name.endswith((".md", ".markdown")):
        return _md(check_generic_md(path))
    return None


# --------------------------------------------------------------------------- #
# Self-check of the plugin
# --------------------------------------------------------------------------- #

# A PlantUML !include, minus any leading whitespace. Vendored upstream C4 files are exempt:
# they are copied verbatim from plantuml-stdlib and include each other by ./name.
INCLUDE_RE = re.compile(r"^\s*!include(?:sub|url)?\s+(\S+)", re.MULTILINE)


def check_plantuml_includes() -> list[str]:
    """Every !include we ship must resolve through PLANTUML_INCLUDE_PATH, not by walking `../`.

    render-plantuml.sh puts skills/sei-diagrams/assets/ on PlantUML's include path, so an
    include is written as a bare name (`plantuml-theme.puml`, `c4/C4_Container.puml`). A `../`
    traversal only ever resolved because the examples happen to sit inside this repo — from
    `architecture/diagrams/` in a user's project no number of `../` reaches an installed plugin.
    """
    errs: list[str] = []
    assets = ROOT / "skills" / "sei-diagrams" / "assets"

    # the theme + C4 macro set the documented includes resolve to must actually be there
    for rel in ("plantuml-theme.puml", "c4/C4.puml", "c4/C4_Context.puml", "c4/C4_Container.puml",
                "c4/C4_Component.puml", "c4/C4_Deployment.puml", "c4/sei-c4-palette.puml"):
        if not (assets / rel).is_file():
            errs.append(f"skills/sei-diagrams/assets/{rel}: missing — !include {rel} cannot resolve")

    targets = [*sorted((ROOT / "skills").glob("*/SKILL.md")),
               *sorted((ROOT / "templates").glob("*.md")),
               *sorted((ROOT / "references").glob("*.md")),
               *sorted((ROOT / "examples").rglob("*.puml")),
               *sorted((ROOT / "examples").rglob("*.md"))]
    for f in targets:
        for m in INCLUDE_RE.finditer(f.read_text(encoding="utf-8", errors="replace")):
            inc = m.group(1)
            rel = f.relative_to(ROOT)
            if inc.startswith(("http://", "https://", "<")):
                errs.append(f"{rel}: '!include {inc}' fetches over the network — "
                            f"use the vendored copy under assets/")
            elif ".." in inc.split("/"):
                errs.append(f"{rel}: '!include {inc}' walks out with '../' — write it as a bare "
                            f"assets-relative name (PLANTUML_INCLUDE_PATH resolves it anywhere)")
            elif inc.startswith("/") or inc.startswith("${"):
                errs.append(f"{rel}: '!include {inc}' is absolute — PlantUML does not expand "
                            f"variables; use a bare assets-relative name")
            elif not (assets / inc).is_file():
                errs.append(f"{rel}: '!include {inc}' does not resolve under assets/")

    # the renderer has to put assets/ on the include path, or every bare include above breaks
    render_pl = (ROOT / "skills" / "sei-diagrams" / "scripts" / "render-plantuml.sh") \
        .read_text(encoding="utf-8")
    if "export PLANTUML_INCLUDE_PATH" not in render_pl:
        errs.append("render-plantuml.sh: does not export PLANTUML_INCLUDE_PATH — bare "
                    "'!include plantuml-theme.puml' will not resolve outside this repo")
    return errs


def check_license() -> list[str]:
    """The license must actually grant something, and say the same thing everywhere.

    The repo previously shipped an "all rights reserved / no permission is granted" LICENSE while
    the README told people to install the plugin — anyone following the README was doing what the
    LICENSE forbade. Guard against that reappearing, and against LICENSE / plugin.json / NOTICE
    drifting apart.
    """
    errs: list[str] = []
    lic_path = ROOT / "LICENSE"
    if not lic_path.is_file():
        return ["LICENSE: missing"]
    lic = lic_path.read_text(encoding="utf-8")

    # 1. it has to be a real grant, not a placeholder
    if re.search(r"(?i)no permission is granted", lic):
        errs.append("LICENSE: still says 'no permission is granted' — the README tells people to "
                    "install this plugin, which that language forbids")
    if re.search(r"(?i)^#?\s*license\s*[-—]+\s*TBD\s*$", lic, re.MULTILINE):
        errs.append("LICENSE: is a TBD placeholder, not a license")

    # 2. Apache-2.0 must be present unaltered in the parts that matter
    for marker in ("Apache License", "Version 2.0, January 2004",
                   "Licensed under the Apache License, Version 2.0"):
        if marker not in lic:
            errs.append(f"LICENSE: missing Apache-2.0 text marker {marker!r}")

    # 3. plugin.json must declare the same license
    try:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except Exception as e:
        return errs + [f"plugin.json unreadable: {e}"]
    declared = manifest.get("license")
    if not declared:
        errs.append("plugin.json: no 'license' field (SPDX id, e.g. \"Apache-2.0\")")
    elif declared != "Apache-2.0":
        errs.append(f"plugin.json: license '{declared}' does not match the Apache-2.0 LICENSE file")

    # 4. Apache-2.0 ships a NOTICE; it is also where third-party attribution belongs
    notice_path = ROOT / "NOTICE"
    if not notice_path.is_file():
        errs.append("NOTICE: missing — Apache-2.0 projects carry one, and it is where the "
                    "vendored C4-PlantUML attribution belongs")
    else:
        notice = notice_path.read_text(encoding="utf-8")
        for expected in ("C4-PlantUML", "Ricardo Niepel", "MIT"):
            if expected not in notice:
                errs.append(f"NOTICE: does not mention {expected!r}")

    return errs


def check_vendored_c4() -> list[str]:
    """The vendored C4-PlantUML macro set is MIT code we redistribute — attribution must ship.

    MIT asks for exactly one thing in return for the grant: "The above copyright notice and this
    permission notice shall be included in all copies or substantial portions of the Software."
    assets/c4/ is ~96 KB of substantial portion, so the notice has to be there — and has to stay
    there through future edits, hence this check rather than a one-off fix.
    """
    errs: list[str] = []
    c4 = ROOT / "skills" / "sei-diagrams" / "assets" / "c4"
    upstream = ["C4.puml", "C4_Context.puml", "C4_Container.puml",
                "C4_Component.puml", "C4_Deployment.puml"]

    lic = c4 / "LICENSE"
    if not lic.is_file():
        errs.append("skills/sei-diagrams/assets/c4/LICENSE: missing — vendored C4-PlantUML is "
                    "MIT and its copyright + permission notice must ship with the copies")
    else:
        text = lic.read_text(encoding="utf-8")
        # the copyright line and the permission clause are the two things MIT actually requires
        if not re.search(r"Copyright \(c\) \d{4} .+", text):
            errs.append("assets/c4/LICENSE: no 'Copyright (c) <year> <holder>' line")
        if "The above copyright notice and this permission notice shall be included" not in text:
            errs.append("assets/c4/LICENSE: missing the MIT permission notice clause")

    readme = c4 / "README.md"
    if not readme.is_file():
        errs.append("skills/sei-diagrams/assets/c4/README.md: missing — vendored code needs "
                    "provenance (upstream URL, pinned version, modified-or-not)")
        return errs

    prov = readme.read_text(encoding="utf-8")
    if "plantuml-stdlib/C4-PlantUML" not in prov:
        errs.append("assets/c4/README.md: does not name the upstream repository")

    # The pinned version is asserted in three places; drift between them is how a vendored
    # dependency quietly stops being the version everyone believes it is.
    tags = set()
    for name in upstream:
        f = c4 / name
        if not f.is_file():
            errs.append(f"assets/c4/{name}: missing — vendored C4-PlantUML is incomplete")
            continue
        tags |= set(re.findall(r"C4-PlantUML/(v[\d.]+)/", f.read_text(encoding="utf-8")))
    if len(tags) > 1:
        errs.append(f"assets/c4/: vendored files reference more than one upstream tag {sorted(tags)}")
    for tag in tags:
        if tag not in prov:
            errs.append(f"assets/c4/README.md: does not state the pinned version {tag}")
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        if "C4-PlantUML" in root_readme and tag.lstrip("v") not in root_readme:
            errs.append(f"README.md: C4-PlantUML version is out of sync with assets/c4/ ({tag})")

    # the top-level README must disclose that the repo redistributes third-party code
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if not re.search(r"(?im)^#+\s.*third[- ]party", root_readme):
        errs.append("README.md: no 'Third-party' section disclosing the vendored C4-PlantUML")

    return errs


ISO_25010_CHARACTERISTICS = (
    "Performance efficiency", "Compatibility", "Interaction capability", "Reliability",
    "Security", "Maintainability", "Flexibility", "Safety", "Functional suitability",
)


def check_qaw_question_guide(path: Path | None = None) -> list[str]:
    """The QAW skill scripts every step from this guide, so its coverage is part of the contract:
    a question section per workshop step, per ISO/IEC 25010 characteristic, and per entry mode."""
    path = path or ROOT / "references" / "qaw-question-guide.md"
    if not path.is_file():
        return [f"{path.name}: missing — the QAW skill reads its questions from it"]
    text = path.read_text(encoding="utf-8")
    headings = [h.strip().lower() for h in re.findall(r"^#{2,4}\s+(.+)$", text, re.MULTILINE)]
    errs: list[str] = []
    for n in range(1, 10):
        if not any(h.startswith(f"step {n} ") or h == f"step {n}" for h in headings):
            errs.append(f"{path.name}: no '### Step {n}' question section")
    for ch in ISO_25010_CHARACTERISTICS:
        if not any(h.startswith(ch.lower()) for h in headings):
            errs.append(f"{path.name}: no question section for ISO/IEC 25010 '{ch}'")
    for mode in QAW_ENTRY_MODES:
        if f"**{mode}**" not in text:
            errs.append(f"{path.name}: entry mode '{mode}' is not described")
    for name, body in re.findall(r"^###\s+(.+?)\n(.*?)(?=^##|\Z)", text, re.MULTILINE | re.DOTALL):
        if name.lower().startswith(("step ", *(c.lower() for c in ISO_25010_CHARACTERISTICS))) \
                and "?" not in body:
            errs.append(f"{path.name}: section '{name.strip()}' asks no questions")
    # system-type packs: each names the --domain key qawkit.py uses and ends with its measure
    st = re.search(r"^##\s+Questions by system type.*?$(.*?)(?=^##\s|\Z)", text,
                   re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not st:
        errs.append(f"{path.name}: no 'Questions by system type' section")
    else:
        keys: list[str] = []
        for name, body in re.findall(r"^###\s+(.+?)\n(.*?)(?=^###\s|\Z)", st.group(1),
                                     re.MULTILINE | re.DOTALL):
            key = re.search(r"Key:\s*`([a-z0-9-]+)`", body)
            items = re.findall(r"^\d+\.\s+(.*)$", body, re.MULTILINE)
            if not key:
                errs.append(f"{path.name}: system type '{name.strip()}' names no Key: `<key>`")
            else:
                keys.append(key.group(1))
            if len(items) < 3 or "?" not in body:
                errs.append(f"{path.name}: system type '{name.strip()}' has fewer than 3 questions")
            elif not items[-1].startswith("*Measure:*"):
                errs.append(f"{path.name}: system type '{name.strip()}' does not end with a *Measure:* question")
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            errs.append(f"{path.name}: system-type key used twice: {', '.join(dup)}")
        if not keys:
            errs.append(f"{path.name}: 'Questions by system type' has no system types")
    return errs


def check_qaw_playbook(path: Path | None = None) -> list[str]:
    """`qawkit.py agenda` times the workshop from this playbook, so every format needs a
    timebox table that runs all nine steps with whole minutes; the difficult-moments table is
    what the skill turns to when the room goes wrong."""
    path = path or ROOT / "references" / "qaw-facilitation-playbook.md"
    if not path.is_file():
        return [f"{path.name}: missing — the QAW skill and qawkit.py agenda read it"]
    text = path.read_text(encoding="utf-8")
    errs: list[str] = []
    tb = re.search(r"^##\s+Timeboxes.*?$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    found: dict[str, str] = {}
    if tb:
        found = {m.group(1).strip(): m.group(2) for m in
                 re.finditer(r"^###\s+(\S+)\s*\n(.*?)(?=^###\s|\Z)", tb.group(1), re.MULTILINE | re.DOTALL)}
    else:
        errs.append(f"{path.name}: no 'Timeboxes' section")
    for fmt in QAW_FORMATS:
        if fmt not in found:
            errs.append(f"{path.name}: no timebox table for format '{fmt}'")
    for fmt, body in found.items():
        if fmt not in QAW_FORMATS:
            errs.append(f"{path.name}: timebox table '{fmt}' is not a known format ({' / '.join(QAW_FORMATS)})")
        rows = _table_rows("x\n" + body, "Block")
        names = [r[0] for r in rows if r]
        for n in range(1, 10):
            if not any(re.match(rf"Step {n}\b", nm) for nm in names):
                errs.append(f"{path.name}: format '{fmt}' never runs Step {n}")
        for r in rows:
            if len(r) < 2:
                continue
            if r[0].lower() == "next day":
                if r[1] not in ("—", "-", ""):
                    errs.append(f"{path.name}: format '{fmt}': 'Next day' takes no minutes")
            elif not re.fullmatch(r"[1-9]\d*", r[1]):
                errs.append(f"{path.name}: format '{fmt}': block '{r[0]}' has no whole minutes ({r[1]!r})")
        if f"**{fmt}**" not in text:
            errs.append(f"{path.name}: format '{fmt}' is not described in 'Choose a format'")
    dm = re.search(r"^##\s+Difficult moments.*?$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
    if not dm or len(_table_rows("x\n" + dm.group(1), "Signal")) < 8:
        errs.append(f"{path.name}: 'Difficult moments' needs a Signal table with at least 8 rows")
    for title in ("Before the workshop", "After the workshop", "Scenarios that hold up"):
        if not re.search(rf"^##\s+{title}", text, re.MULTILINE):
            errs.append(f"{path.name}: no '{title}' section")
    return errs


def check_self() -> list[str]:
    errs: list[str] = []

    manifest = ROOT / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"plugin.json invalid: {e}"]
    for key in ("name", "version", "description", "skills"):
        if key not in data:
            errs.append(f"plugin.json missing '{key}'")

    listed_dirs = {p[2:] if p.startswith("./") else p for p in data.get("skills", [])}
    for rel in listed_dirs:
        if not (ROOT / rel / "SKILL.md").is_file():
            errs.append(f"plugin.json lists missing skill directory: {rel}")

    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for sf in skill_files:
        rel = sf.parent.relative_to(ROOT).as_posix()
        if rel not in listed_dirs:
            errs.append(f"skill not registered in plugin.json: {rel}")
        text = sf.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not fm:
            errs.append(f"{rel}: missing YAML front-matter")
            continue
        front = fm.group(1)
        nm = re.search(r"^name:\s*(.+)$", front, re.MULTILINE)
        ds = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
        if not nm:
            errs.append(f"{rel}: front-matter has no 'name'")
        elif nm.group(1).strip() != sf.parent.name:
            errs.append(f"{rel}: name '{nm.group(1).strip()}' != directory '{sf.parent.name}'")
        if not ds:
            errs.append(f"{rel}: front-matter has no 'description'")

    # commands live at the plugin root (.claude/commands is only a symlink for in-place hacking)
    cmd_dir = ROOT / "commands"
    cmds = sorted(cmd_dir.glob("*.md"))
    if not cmds:
        errs.append("no commands/*.md at the plugin root — slash commands will not load when installed")
    for cmd in cmds:
        ctext = cmd.read_text(encoding="utf-8")
        if "SKILL.md" not in ctext:
            errs.append(f"{cmd.relative_to(ROOT)}: command does not reference a SKILL.md")
        cfm = re.match(r"^---\n(.*?)\n---\n", ctext, re.DOTALL)
        if not cfm:
            errs.append(f"{cmd.relative_to(ROOT)}: missing YAML front-matter "
                        f"(the slash-command picker shows no description without it)")
        elif not re.search(r"^description:\s*\S", cfm.group(1), re.MULTILINE):
            errs.append(f"{cmd.relative_to(ROOT)}: front-matter has no 'description'")

    # One picker entry per activity: a skill either shares its name with a commands/*.md (the
    # collision collapses them) or is hidden from the / menu with `user-invocable: false` while
    # staying model-invocable. Otherwise every activity shows up twice in the slash-command list.
    cmd_names = {c.stem for c in cmds}
    for sf in skill_files:
        fm = re.match(r"^---\n(.*?)\n---\n", sf.read_text(encoding="utf-8"), re.DOTALL)
        if not fm or sf.parent.name in cmd_names:
            continue
        if not re.search(r"^user-invocable:\s*false\s*$", fm.group(1), re.MULTILINE):
            errs.append(f"{sf.parent.relative_to(ROOT).as_posix()}: has a differently-named "
                        f"command alias, so it needs 'user-invocable: false' or it appears twice "
                        f"in the slash-command menu")
        if re.search(r"^version:", fm.group(1), re.MULTILINE):
            errs.append(f"{sf.parent.relative_to(ROOT).as_posix()}: 'version' is not a SKILL.md "
                        f"front-matter field — the plugin version lives in plugin.json")

    # The version is asserted in three places; they must agree or `/plugin marketplace update`
    # and the plugin manager disagree about what is installed.
    try:
        mp = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        versions = {
            "plugin.json": data.get("version"),
            "marketplace.json metadata.version": mp.get("metadata", {}).get("version"),
        }
        for i, pl in enumerate(mp.get("plugins", [])):
            versions[f"marketplace.json plugins[{i}].version"] = pl.get("version")
            if pl.get("name") != data.get("name"):
                errs.append(f"marketplace.json plugins[{i}].name {pl.get('name')!r} != "
                            f"plugin.json name {data.get('name')!r}")
        if len(set(versions.values())) != 1:
            errs.append("version drift: " + ", ".join(f"{k}={v}" for k, v in versions.items()))
    except Exception as e:
        errs.append(f"marketplace.json unreadable: {e}")

    # skills must be able to revise what they wrote, not just overwrite it
    for sf in skill_files:
        fm = re.match(r"^---\n(.*?)\n---\n", sf.read_text(encoding="utf-8"), re.DOTALL)
        if not fm:
            continue
        at = re.search(r"^allowed-tools:\s*\[(.*?)\]", fm.group(1), re.MULTILINE)
        if at:
            tools = {x.strip() for x in at.group(1).split(",")}
            for needed in ("Read", "Write", "Edit"):
                if needed not in tools:
                    errs.append(f"{sf.parent.relative_to(ROOT).as_posix()}: "
                                f"allowed-tools is missing '{needed}'")

    # Every cross-file path in anything the model reads at runtime must be plugin-root-anchored,
    # because the cwd at runtime is the user's project, not the plugin. That covers commands and
    # SKILL.md, and equally templates/ and references/ — those are read mid-task too, so a bare
    # `references/foo.md` inside one of them is just as unresolvable.
    BARE_PATH_RE = re.compile(
        r"(?<![/{\w-])(references|templates|assets)/[A-Za-z0-9_./-]+"
        r"|(?<![/{\w-])scripts/(?:build-report|render|render-plantuml|setup)\.sh"
        r"|(?<![/{\w-])scripts/(?:qawkit|driverstatus)\.py"
        r"|(?<![/{\w-])skills/[a-z-]+/SKILL\.md"
        r"|(?<![/{\w-])tests/validate\.py")
    template_files = sorted((ROOT / "templates").glob("*.md"))
    reference_files = sorted((ROOT / "references").glob("*.md"))
    for md in [*cmds, *skill_files, *template_files, *reference_files]:
        for m in BARE_PATH_RE.finditer(md.read_text(encoding="utf-8")):
            errs.append(f"{md.relative_to(ROOT)}: path '{m.group(0)}' is not "
                        f"anchored to ${{CLAUDE_PLUGIN_ROOT}}")

    # a reference nobody can find from the index is a reference that does not exist
    ref_index = (ROOT / "references" / "README.md").read_text(encoding="utf-8")
    for rf in sorted((ROOT / "references").glob("*.md")):
        if rf.name != "README.md" and f"({rf.name})" not in ref_index:
            errs.append(f"references/{rf.name}: not linked from references/README.md")

    errs += check_qaw_question_guide()
    errs += check_qaw_playbook()
    errs += check_template_structures()
    errs += check_plantuml_includes()
    errs += check_vendored_c4()
    errs += check_license()

    # embedded diagrams in skills/templates/references must obey the rules
    for md in [*skill_files,
               *sorted((ROOT / "templates").glob("*.md")),
               *sorted((ROOT / "references").glob("*.md")),
               *sorted((ROOT / "examples").rglob("*.md"))]:
        for j, blk in enumerate(diagrams_in_markdown(md.read_text(encoding="utf-8")), 1):
            # examples of "what not to do" are allowed only in classdefs/palette notes
            errs += [f"{md.relative_to(ROOT)} [{j}]: {e}"
                     for e in check_diagram(blk, f"block {j}")]

    # no deprecated flat QA IDs anywhere in the shipped docs
    for md in [*skill_files, *sorted((ROOT / "templates").glob("*.md")),
               *sorted((ROOT / "references").glob("*.md"))]:
        if BARE_QAS_RE.search(md.read_text(encoding="utf-8")):
            errs.append(f"{md.relative_to(ROOT)}: contains deprecated flat 'QAS-<n>' ID")

    for md in [*cmds, *skill_files, *template_files, *reference_files]:
        for n in headerless_tables(md.read_text(encoding="utf-8")):
            errs.append(f"{md.relative_to(ROOT)}:{n}: table rows without a header separator")
    for md in template_files:
        errs += [f"{md.relative_to(ROOT)}: {e}" for e in template_meta_errors(md)]

    # the plugin's own prose honours the writing-style rules it imposes on artifacts
    # (writing-style.md itself is the one file allowed to name the banned phrases)
    for md in [*cmds, *skill_files, *template_files, *reference_files]:
        if md.name == "writing-style.md":
            continue
        hits = sorted({m.group(0).lower()
                       for m in FILLER_RE.finditer(_without_code(md.read_text(encoding="utf-8")))})
        for h in hits:
            errs.append(f"{md.relative_to(ROOT)}: filler phrase {h!r}")

    # examples/ diagram hygiene: every source has its committed render, and every committed
    # render is reachable — referenced from some Markdown file or sitting beside its source.
    ex_root = ROOT / "examples"
    if ex_root.is_dir():
        referenced: set[Path] = set()
        for md in ROOT.rglob("*.md"):
            if "node_modules" in md.parts:
                continue
            try:
                text = md.read_text(encoding="utf-8")
            except Exception:
                continue
            for m in _LINK_RE.finditer(text):
                target = m.group(1).strip().lstrip("<").rstrip(">")
                target = target.split("#", 1)[0].split("?", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
                    continue
                try:
                    referenced.add((md.parent / target).resolve())
                except OSError:
                    pass
        for src in sorted([*ex_root.rglob("*.mmd"), *ex_root.rglob("*.puml")]):
            if not src.with_suffix(".png").is_file():
                errs.append(f"{src.relative_to(ROOT)}: diagram source has no rendered .png beside it")
        for png in sorted(ex_root.rglob("*.png")):
            has_source = png.with_suffix(".mmd").is_file() or png.with_suffix(".puml").is_file()
            if png.resolve() not in referenced and not has_source:
                errs.append(f"{png.relative_to(ROOT)}: orphan render — nothing references it "
                            f"and it has no source beside it")

    # shell scripts parse
    import subprocess
    for sh in sorted(ROOT.rglob("*.sh")):
        r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
        if r.returncode != 0:
            errs.append(f"{sh.relative_to(ROOT)}: bash -n failed: {r.stderr.strip()}")

    # mermaid theme JSON parses
    theme = ROOT / "skills" / "sei-diagrams" / "assets" / "mermaid-theme.json"
    try:
        json.loads(theme.read_text(encoding="utf-8"))
    except Exception as e:
        errs.append(f"mermaid-theme.json invalid: {e}")

    return errs


# --------------------------------------------------------------------------- #

def main(argv: list[str]) -> int:
    do_self = "--self" in argv or not [a for a in argv if not a.startswith("-")]
    raw = [Path(a) for a in argv if not a.startswith("-")]

    total = 0
    if do_self:
        errs = check_self()
        tag = "PASS" if not errs else "FAIL"
        print(f"{tag}  --self (plugin structure)")
        for e in errs:
            print(f"      ✗ {e}")
        total += len(errs)

    if not raw and not argv:
        art = Path("architecture")
        if art.is_dir():
            raw = [art]

    # expand directories: cross-file checks for a drivers/ dir, then every *.md / *.mmd under it
    files: list[Path] = []
    for p in raw:
        if p.is_dir():
            if p.name == "drivers" or (((p / "README.md").is_file() or (p / "index.md").is_file())
                                       and (p / "use-cases").is_dir()):
                errs = check_drivers_dir(p)
                tag = "PASS" if not errs else "FAIL"
                print(f"{tag}  {p}/ (drivers directory — cross-file)")
                for e in errs:
                    print(f"      ✗ {e}")
                total += len(errs)
            files += sorted(p.rglob("*.md")) + sorted(p.rglob("*.mmd"))
        else:
            files.append(p)

    for f in files:
        if not f.exists():
            print(f"FAIL  {f}\n      ✗ not found")
            total += 1
            continue
        res = validate_file(f)
        if res is None:
            print(f"SKIP  {f} (unrecognised)")
            continue
        tag = "PASS" if not res else "FAIL"
        print(f"{tag}  {f}")
        for e in res:
            print(f"      ✗ {e}")
        total += len(res)

    print(f"\n{total} problem(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
