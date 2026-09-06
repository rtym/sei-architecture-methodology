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
    tr = text.split("raceability", 1)[-1]
    tr_rows = _table_rows("x\n" + tr, "Driver") or _table_rows("x\n" + tr, "Supports")
    if tr_rows:
        supported_bgs = set()
        traced_children = set()
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


def check_scenarios(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8")
    if BARE_QAS_RE.search(text):
        errs.append("uses deprecated flat 'QAS-<n>' IDs")
    rows = _table_rows(text, "Response measure")
    n = len([r for r in rows if re.search(r"[A-Z]{1,4}QA-\d+", " ".join(r))])
    if rows and not (4 <= n <= 25):
        errs.append(f"{n} quality attribute scenarios — expected roughly 8–15 (min 5, max ~20)")
    for r in rows:
        joined = " ".join(r)
        if re.search(r"[A-Z]{1,4}QA-\d+", joined) and not NUM_RE.search(joined):
            errs.append(f"scenario row has no numeric response measure: {joined[:80]!r}")
    if rows and "25010" not in text:
        errs.append("no ISO/IEC 25010 classification anywhere in the file")
    for j, blk in enumerate(diagrams_in_markdown(text), 1):
        errs += check_diagram(blk, f"scenario diagram #{j}")
    return errs


def check_qaw(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(encoding="utf-8").lower()
    for kw in ("introduction", "business", "architectural plan", "architectural driver",
               "brainstorm", "consolidat", "prioriti", "refine"):
        if kw not in text:
            errs.append(f"QAW report missing a step about '{kw}'")
    if "30" not in text or "vote" not in text:
        errs.append("QAW report does not state the 30%-of-scenarios vote budget")
    if "verbatim" not in text and "raw" not in text:
        errs.append("QAW report should keep raw brainstormed scenarios verbatim (say so)")
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
        errs.append("utility-tree leaves should carry an (Importance, Difficulty) pair")
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
    if name.endswith("-Architecture.md"):
        return check_architecture(path)
    if name.endswith("-session.md") or re.search(r"-\d{4}-\d{2}-\d{2}\.md$", name):
        return check_session(path)
    if name == "drivers.md":
        return check_drivers(path)
    if name == "scenarios.md":
        return check_scenarios(path)
    if name == "qaw-report.md":
        return check_qaw(path)
    if name == "atam-report.md":
        return check_atam(path)
    if name.startswith("view-") and name.endswith(".md"):
        return check_view_packet(path)
    if name.endswith((".mmd", ".mermaid")):
        return check_mmd(path)
    if name.endswith((".md", ".markdown")):
        return check_generic_md(path)
    return None


# --------------------------------------------------------------------------- #
# Self-check of the plugin
# --------------------------------------------------------------------------- #

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

    listed = set(data.get("skills", []))
    for rel in listed:
        if not (ROOT / rel).is_file():
            errs.append(f"plugin.json lists missing skill file: {rel}")

    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for sf in skill_files:
        rel = sf.relative_to(ROOT).as_posix()
        if rel not in listed:
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

    # commands delegate to a skill
    for cmd in sorted((ROOT / ".claude" / "commands").glob("*.md")):
        if "SKILL.md" not in cmd.read_text(encoding="utf-8"):
            errs.append(f"{cmd.relative_to(ROOT)}: command does not reference a SKILL.md")

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
    files = [Path(a) for a in argv if not a.startswith("-")]

    total = 0
    if do_self:
        errs = check_self()
        tag = "PASS" if not errs else "FAIL"
        print(f"{tag}  --self (plugin structure)")
        for e in errs:
            print(f"      ✗ {e}")
        total += len(errs)

    if not files and not argv:
        art = Path("architecture")
        if art.is_dir():
            files = sorted(art.rglob("*.md")) + sorted(art.rglob("*.mmd"))

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
