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
        if not re.search(r"^\s*(%%|title\b)", block, re.MULTILINE):
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
    tc = re.search(r"^\s*%%\s*(.+)$", block, re.MULTILINE)
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
    for r in tr_rows:
        row_ids = set(re.findall(r"\b(BG-\d+|UC-\d+|CON-\d+|[A-Z]{1,4}QA-\d+)\b", " ".join(r)))
        child = {i for i in row_ids if not i.startswith("BG-")}
        bg_here = {i for i in row_ids if i.startswith("BG-")}
        if child and bg_here:
            traced_children |= child
            supported_bgs |= bg_here
    orphan_bgs = bgs - supported_bgs
    orphan_children = (ucs | qas | cons) - traced_children
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
        if re.search(r"[A-Z]{1,4}QA-\d+", joined) and not NUM_RE.search(joined):
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
    }
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
    # every id in the top README has a file and vice versa
    if idx.is_file():
        itext = idx.read_text(encoding="utf-8")
        for sub, files in present.items():
            ids_in_files = {f.stem for f in files}
            for fid in ids_in_files:
                if fid not in itext:
                    errs.append(f"{sub}/{fid}.md exists but {fid} is not listed in the drivers README")
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
        if re.search(r"[A-Z]{1,4}QA-\d+", joined) and not NUM_RE.search(joined):
            errs.append(f"scenario row has no numeric response measure: {joined[:80]!r}")
    if rows and "25010" not in text:
        errs.append("no ISO/IEC 25010 classification anywhere in the file")
    # every scenario is drawn: an image line to diagrams/scenario-<ID>.png (both notations) —
    # a fenced mermaid block alone is not enough, the PNG is what was visually verified
    images = " ".join(re.findall(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", text, re.MULTILINE))
    for r in rows:
        m = re.search(r"\b([A-Z]{1,4}QA-\d+)\b", " ".join(r))
        if m and f"scenario-{m.group(1)}." not in images:
            errs.append(f"{m.group(1)}: no embedded scenario diagram — add "
                        f"![{m.group(1)} six-part scenario](diagrams/scenario-{m.group(1)}.png)")
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
            if rid.rstrip(":") not in images:
                errs.append(f"refined scenario {rid} has no embedded six-part scenario diagram "
                            f"(![...](diagrams/scenario-{rid}.png))")
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
    return errs


def check_atam(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    for kw in ("architectural approach", "utility tree", "risk", "non-risk",
               "sensitivity point", "tradeoff point", "risk theme"):
        if kw not in low:
            errs.append(f"ATAM report missing a '{kw}' section")
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
    return errs


def check_generic_md(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"{path.name} diagram #{j}")
    return errs


def check_mmd(path: Path) -> list[str]:
    return check_diagram(path.read_text(encoding="utf-8"), path.name)


def validate_file(path: Path) -> list[str] | None:
    name = path.name
    parent = path.parent.name

    def _md(res: list[str]) -> list[str]:
        return res + broken_links(path)

    if name.endswith("-Architecture.md"):
        return _md(check_architecture(path))
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
        r"|(?<![/{\w-])skills/[a-z-]+/SKILL\.md"
        r"|(?<![/{\w-])tests/validate\.py")
    template_files = sorted((ROOT / "templates").glob("*.md"))
    reference_files = sorted((ROOT / "references").glob("*.md"))
    for md in [*cmds, *skill_files, *template_files, *reference_files]:
        for m in BARE_PATH_RE.finditer(md.read_text(encoding="utf-8")):
            errs.append(f"{md.relative_to(ROOT)}: path '{m.group(0)}' is not "
                        f"anchored to ${{CLAUDE_PLUGIN_ROOT}}")

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
