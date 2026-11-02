#!/usr/bin/env python3
"""QAW kit: generate the Quality Attribute Workshop's working artifacts from the documentation
that already exists. Standard library only; the same inputs always give the same output.

  qawkit.py prep    --drivers DIR [--previous-report FILE] --system NAME --date YYYY-MM-DD --out FILE
  qawkit.py ballot  REPORT --out FILE
  qawkit.py summary REPORT --out FILE

prep     before the session: documented answers to confirm (with their sources), the ISO/IEC
         25010 characteristics with no scenario and their questions, each participant's
         questions for their role, and parked questions still open from the last workshop.
ballot   at Step 7: the vote sheet for the consolidated scenarios, with the vote budget computed.
summary  after the session: a one-page result for the sponsor, taken from the finished report.

Exit codes: 0 written, 2 bad arguments or unreadable input.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "references" / "qaw-question-guide.md"

# Functional suitability is captured as use cases, not quality attribute scenarios, so a missing
# scenario for it is not a gap.
ISO_CHARACTERISTICS = (
    "Performance efficiency", "Compatibility", "Interaction capability", "Reliability",
    "Security", "Maintainability", "Flexibility", "Safety",
)
ROLE_STOPWORDS = {"or", "and", "the", "their", "role", "unfilled", "of", "a"}


class KitError(Exception):
    """Input the kit cannot work from; the message says what is wrong."""


# --------------------------------------------------------------------------- #
# Markdown reading helpers
# --------------------------------------------------------------------------- #

def kv_bullets(text: str) -> dict[str, str]:
    """`- **Key**: value` lines → {key: value}; the first occurrence of a key wins."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^\s*-\s*\*\*([^*]+)\*\*\s*:\s*(.*?)\s*$", text, re.MULTILINE):
        out.setdefault(m.group(1).strip(), m.group(2).strip())
    return out


def table(text: str, header_contains: str) -> list[dict[str, str]]:
    """Rows of the first pipe table whose header contains `header_contains`, keyed by header."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and header_contains.lower() in ln.lower() \
                and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            for r in lines[i + 2:]:
                if not r.strip().startswith("|"):
                    break
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                cells += [""] * (len(head) - len(cells))
                rows.append(dict(zip(head, cells)))
            return rows
    return []


def kv_table(text: str) -> dict[str, str]:
    """A two-column `| Part | Value |` table → {part: value}, bold markers removed from keys."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$", text, re.MULTILINE):
        key = m.group(1).strip().strip("*").strip()
        if key and not set(key) <= set("-: "):
            out.setdefault(key, m.group(2).strip())
    return out


def section(text: str, title_re: str) -> str:
    """Body of the first `## ` section whose title matches, up to the next `## ` heading."""
    m = re.search(r"^##\s[^\n]*" + title_re + r"[^\n]*$(.*?)(?=^##\s|\Z)", text,
                  re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def title_of(text: str) -> str:
    """`# ID: Title` → `Title` (the whole heading if it has no `ID:` prefix)."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if not m:
        return ""
    return re.sub(r"^[A-Z]{1,4}-\d+\s*:\s*", "", m.group(1).strip())


def numbered_items(text: str) -> list[str]:
    """`1. …` list items, with wrapped continuation lines joined."""
    items: list[str] = []
    for ln in text.splitlines():
        m = re.match(r"^\d+\.\s+(.*)$", ln)
        if m:
            items.append(m.group(1).strip())
        elif items and ln.startswith("   ") and ln.strip():
            items[-1] += " " + ln.strip()
        elif items and not ln.strip():
            continue
    return items


def strip_md(s: str) -> str:
    return re.sub(r"[*`]", "", s).strip()


# --------------------------------------------------------------------------- #
# Reading the question guide
# --------------------------------------------------------------------------- #

def guide_attribute_questions(guide: str) -> dict[str, list[str]]:
    """Characteristic → its questions, from the guide's *Questions by quality attribute*."""
    body = section(guide, r"questions by quality attribute")
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###\s|\Z)", body, re.MULTILINE | re.DOTALL):
        name = re.sub(r"\s*\(.*\)\s*$", "", m.group(1)).strip()
        out[name] = [strip_md(q) for q in numbered_items(m.group(2))]
    return out


def guide_role_questions(guide: str) -> list[tuple[str, list[str]]]:
    """[(role, [questions])] from the guide's *Questions by stakeholder role* table."""
    rows = table(section(guide, r"questions by stakeholder role"), "Role")
    out = []
    for r in rows:
        qs = [q.strip() + "?" for q in r.get("Ask", "").split("?") if q.strip()]
        out.append((r.get("Role", ""), qs))
    return out


def _role_words(role: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", role.lower().replace("end-user", "end user"))
            if w not in ROLE_STOPWORDS and len(w) > 1}


def match_role(stakeholder_role: str, guide_roles: list[tuple[str, list[str]]]) -> tuple[str, list[str]] | None:
    """The guide role sharing the most words with the stakeholder's role; ties go to the
    earlier row, and no shared word means no match."""
    want = _role_words(stakeholder_role)
    best, best_n = None, 0
    for role, qs in guide_roles:
        n = len(want & _role_words(role))
        if n > best_n:
            best, best_n = (role, qs), n
    return best


# --------------------------------------------------------------------------- #
# Reading the drivers register
# --------------------------------------------------------------------------- #

def _id_key(path: Path) -> tuple[str, int]:
    m = re.match(r"([A-Z]+)-(\d+)", path.stem)
    return (m.group(1), int(m.group(2))) if m else (path.stem, 0)


def _retired(text: str) -> bool:
    return kv_bullets(text).get("Status", "").lower().startswith("retired")


def load_drivers(drivers: Path) -> dict[str, list[dict[str, str]]]:
    """Business goals, constraints and QA scenarios that are not retired, in ID order."""
    if not drivers.is_dir():
        raise KitError(f"drivers directory not found: {drivers}")
    out: dict[str, list[dict[str, str]]] = {"bg": [], "con": [], "qa": []}
    for p in sorted((drivers / "business-goals").glob("BG-*.md"), key=_id_key):
        t = p.read_text(encoding="utf-8")
        if _retired(t):
            continue
        kv = kv_bullets(t)
        out["bg"].append({"id": p.stem, "path": str(p), "title": title_of(t),
                          "says": kv.get("Measure of success") or kv.get("Statement", "")})
    for p in sorted((drivers / "constraints").glob("CON-*.md"), key=_id_key):
        t = p.read_text(encoding="utf-8")
        if _retired(t):
            continue
        kv = kv_bullets(t)
        out["con"].append({"id": p.stem, "path": str(p), "title": title_of(t),
                           "says": kv.get("Constraint", "")})
    for p in sorted((drivers / "quality-attributes").glob("*QA-*.md"), key=_id_key):
        if not re.match(r"[A-Z]{1,4}QA-\d+$", p.stem):
            continue
        t = p.read_text(encoding="utf-8")
        if _retired(t):
            continue
        kv = kv_table(t)
        out["qa"].append({"id": p.stem, "path": str(p), "title": title_of(t),
                          "characteristic": strip_md(kv.get("ISO/IEC 25010 characteristic", "")),
                          "says": kv.get("Response measure", "")})
    return out


def load_participants(stakeholders: Path) -> list[dict[str, str]]:
    """QAW participants from the stakeholder register (everyone when it has no QAW column)."""
    if not stakeholders.is_file():
        return []
    rows = table(stakeholders.read_text(encoding="utf-8"), "Role")
    people = []
    for r in rows:
        sid = r.get("ID", "")
        if not re.match(r"ST-\d+$", sid):
            continue
        if "QAW" in r and r["QAW"].strip() in ("—", "-", "", "no"):
            continue
        name = r.get("Name / representative") or r.get("Name", "")
        people.append({"id": sid, "name": name, "role": r.get("Role", "")})
    return people


def suggest_mode(drivers: dict[str, list[dict[str, str]]]) -> str:
    if drivers["qa"]:
        return "refresh"
    if drivers["bg"] or drivers["con"]:
        return "partial"
    return "greenfield"


def open_parked_questions(report: Path) -> list[dict[str, str]]:
    if not report.is_file():
        raise KitError(f"previous report not found: {report}")
    rows = table(section(report.read_text(encoding="utf-8"), r"parked question"), "Question")
    return [r for r in rows if re.match(r"PQ-\d+$", r.get("ID", ""))
            and r.get("Status", "").strip().lower() not in ("answered", "closed", "done")]


# --------------------------------------------------------------------------- #
# prep
# --------------------------------------------------------------------------- #

def _link(target: str, out: Path, label: str) -> str:
    rel = os.path.relpath(target, out.parent).replace(os.sep, "/")
    return f"[{label}]({rel})"


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def build_prep(drivers_dir: Path, system: str, date: str, out: Path,
               previous_report: Path | None = None, guide_text: str | None = None) -> str:
    guide_text = guide_text if guide_text is not None else GUIDE.read_text(encoding="utf-8")
    drivers = load_drivers(drivers_dir)
    people = load_participants(drivers_dir / "stakeholders.md")
    mode = suggest_mode(drivers)
    attr_q = guide_attribute_questions(guide_text)
    role_q = guide_role_questions(guide_text)

    covered = {q["characteristic"].lower() for q in drivers["qa"]}
    gaps = [c for c in ISO_CHARACTERISTICS if c.lower() not in covered]
    n_doc = len(drivers["bg"]) + len(drivers["con"]) + len(drivers["qa"])

    L: list[str] = [f"# QAW preparation — {system}", "",
                    f"- **Generated**: {date}",
                    f"- **Suggested entry mode**: {mode}",
                    f"- **Drivers register**: {_link(str(drivers_dir / 'README.md'), out, 'drivers register')}",
                    ""]
    L += [f"This sheet prepares the facilitator for the next Quality Attribute Workshop on {system}. "
          f"It lists {n_doc} answers the documentation already gives, to confirm rather than ask "
          f"again, then the quality characteristics no scenario covers yet, and the questions for "
          f"each participant's role. Start with the first table in Steps 2–4.", ""]

    L += ["## Documented answers to confirm", "",
          "Each row is already answered in the drivers register. Read it out with its source and "
          "ask only whether it still holds; a changed answer is recorded in the report with both "
          "versions.", ""]
    if n_doc:
        L += ["| ID | What the documentation says | Source | Ask |",
              "|----|-----------------------------|--------|-----|"]
        for d in drivers["bg"]:
            L.append(f"| {d['id']} | {_cell(d['says'] or d['title'])} | {_link(d['path'], out, d['id'])} "
                     f"| Is this still the target, and still a goal? |")
        for d in drivers["con"]:
            L.append(f"| {d['id']} | {_cell(d['says'] or d['title'])} | {_link(d['path'], out, d['id'])} "
                     f"| Who still requires this, and what would lifting it cost? |")
        for d in drivers["qa"]:
            says = f"{d['characteristic']}: {d['says']}" if d["characteristic"] else d["says"]
            L.append(f"| {d['id']} | {_cell(says or d['title'])} | {_link(d['path'], out, d['id'])} "
                     f"| Does this measure still hold, and is there evidence the system meets it? |")
    else:
        L.append("The drivers register holds no business goals, constraints or scenarios yet, so "
                 "every step starts from the guide's open questions.")
    L.append("")

    L += ["## Quality characteristics with no scenario", ""]
    if gaps:
        L += [f"{len(gaps)} of the {len(ISO_CHARACTERISTICS)} ISO/IEC 25010 characteristics that "
              f"scenarios cover have no scenario in the register. Ask these in Step 4; record each "
              f"answer as a driver, or as not significant here with the reason. Functional "
              f"suitability is left out because use cases cover it.", ""]
        for c in gaps:
            L += [f"### {c}", ""]
            L += [f"{i}. {q}" for i, q in enumerate(attr_q.get(c, []), 1)] or \
                 ["The question guide has no questions for this characteristic."]
            L.append("")
    else:
        L += ["Every ISO/IEC 25010 characteristic that scenarios cover has at least one scenario. "
              "Spend Step 5 on what has changed since the scenarios were written.", ""]

    L += ["## Questions by participant", ""]
    if people:
        L += ["Taken from the stakeholder register's QAW participants and the question guide's "
              "role table. Ask them of the person directly when they are quiet.", ""]
        for p in people:
            L += [f"### {p['id']} — {p['name']} ({p['role']})", ""]
            match = match_role(p["role"], role_q)
            if match:
                L += [f"- {q}" for q in match[1]]
            else:
                L.append("- The question guide has no role row for this role; use the step "
                         "questions and ask what concern they bring.")
            L.append("")
    else:
        L += ["No stakeholder register with QAW participants was found. Capture participants in "
              "Step 1 and create the register then.", ""]

    if previous_report is not None:
        pqs = open_parked_questions(previous_report)
        L += ["## Parked questions still open", ""]
        if pqs:
            L += [f"From {_link(str(previous_report), out, 'the previous workshop')}. Get each "
                  f"answer before the session, or ask it in the step named.", "",
                  "| ID | Question | Raised in | Who can answer | Owner | Due |",
                  "|----|----------|-----------|----------------|-------|-----|"]
            for r in pqs:
                L.append("| " + " | ".join(_cell(r.get(k, "")) for k in
                                           ("ID", "Question", "Raised in", "Who can answer", "Owner", "Due")) + " |")
        else:
            L.append(f"None — every parked question from "
                     f"{_link(str(previous_report), out, 'the previous workshop')} has been answered.")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# ballot
# --------------------------------------------------------------------------- #

def vote_budget(n_scenarios: int) -> int:
    """Votes per stakeholder: 30 % of the consolidated scenarios, rounded up (at least 1)."""
    if n_scenarios < 1:
        raise KitError("no consolidated scenarios to vote on")
    return max(1, math.ceil(n_scenarios * 3 / 10))


def read_report(report: Path) -> str:
    if not report.is_file():
        raise KitError(f"report not found: {report}")
    return report.read_text(encoding="utf-8")


def report_participants(text: str) -> list[dict[str, str]]:
    rows = table(section(text, r"introduction"), "Role")
    return [r for r in rows if re.match(r"ST-\d+$", r.get("ID", ""))]


def report_consolidated(text: str) -> list[dict[str, str]]:
    rows = table(section(text, r"consolidation"), "Consolidated")
    out = []
    for r in rows:
        cid = r.get("Consolidated ID", "")
        if re.match(r"CS-\d+$", cid):
            out.append({"id": cid, "scenario": r.get("Scenario", "")})
    return out


def build_ballot(report: Path, out: Path) -> str:
    text = read_report(report)
    system = re.sub(r"^Quality Attribute Workshop\s*[—-]\s*", "", title_of(text))
    people = report_participants(text)
    scenarios = report_consolidated(text)
    if not people:
        raise KitError("no ST-<n> participants in the report's Step 1 table")
    budget = vote_budget(len(scenarios))
    L = [f"# QAW vote sheet — {system}", "",
         f"- **Workshop report**: {_link(str(report), out, 'qaw-report.md')}",
         f"- **Votes per participant**: {budget}", "",
         f"Each participant has {budget} votes: 30 % of the {len(scenarios)} consolidated "
         f"scenarios, rounded up. Votes may be stacked on one scenario. Fill a column per "
         f"participant, then add each row into Total and copy the table into Step 7 of the report.",
         "",
         "| Scenario | " + " | ".join(p["ID"] for p in people) + " | Total |",
         "|----------|" + "|".join(":---:" for _ in people) + "|:-----:|"]
    for s in scenarios:
        L.append(f"| {s['id']} — {_cell(strip_md(s['scenario']))} | " + " | ".join("" for _ in people) + " | |")
    L += ["", "Participants: " + "; ".join(f"{p['ID']} {p.get('Name', '')}".strip() for p in people) + "."]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# summary
# --------------------------------------------------------------------------- #

def build_summary(report: Path, out: Path) -> str:
    text = read_report(report)
    head = kv_bullets(text.split("\n## ", 1)[0])
    system = re.sub(r"^Quality Attribute Workshop\s*[—-]\s*", "", title_of(text))
    mode = kv_bullets(section(text, r"starting point")).get("Entry mode", "not recorded")
    people = report_participants(text)
    raw = set(re.findall(r"^\|\s*(S-\d+)\s*\|", section(text, r"brainstorm"), re.MULTILINE))
    cons = report_consolidated(text)
    refined = re.findall(r"^###\s+(CS-\d+)\s*[—-]\s*(.+)$", section(text, r"refine"), re.MULTILINE)
    ranked = re.search(r"^\*\*Ranked\*\*\s*:\s*(.+)$", section(text, r"prioriti"), re.MULTILINE)
    tree = table(section(text, r"utility tree"), "Priority")
    star = [r for r in tree if "★" in r.get("Priority (V, R)", "")]
    pqs = [r for r in table(section(text, r"parked question"), "Question")
           if re.match(r"PQ-\d+$", r.get("ID", ""))]
    open_pqs = [r for r in pqs if r.get("Status", "").strip().lower() not in ("answered", "closed", "done")]
    handoff = [r for r in table(section(text, r"hand-off"), "Becomes") if re.match(r"(CS|AD)-\d+$", r.get("Workshop ID", ""))]

    L = [f"# QAW summary — {system}", "",
         f"- **Workshop date**: {head.get('Date(s)', head.get('Date', 'not recorded'))}",
         f"- **Report status**: {head.get('Status', 'not recorded')}",
         f"- **Entry mode**: {mode}",
         f"- **Full report**: {_link(str(report), out, 'qaw-report.md')}", ""]
    L += [f"{len(people)} participants produced {len(raw)} raw scenarios, consolidated to "
          f"{len(cons)}; {len(refined)} were refined into measurable six-part scenarios. "
          f"{len(star)} carry the highest business value and technical risk, and "
          f"{len(open_pqs)} questions remain open.", ""]
    L += ["## Priorities", ""]
    L.append(f"Vote ranking: {strip_md(ranked.group(1))}" if ranked else "Vote ranking: not recorded.")
    L.append("")
    if star:
        L += ["Highest value and risk — (H, H) in the utility tree:", ""]
        L += [f"- {_cell(strip_md(next((v for k, v in r.items() if k.startswith('Leaf')), '')))}"
              for r in star]
        L.append("")
    L += ["## Refined scenarios", ""]
    L += [f"- {cid} — {name.strip()}" for cid, name in refined] or ["None refined yet."]
    L += ["", "## Open questions", ""]
    if open_pqs:
        L += ["| ID | Question | Owner | Due |", "|----|----------|-------|-----|"]
        L += [f"| {r['ID']} | {_cell(r.get('Question', ''))} | {_cell(r.get('Owner', ''))} | {_cell(r.get('Due', ''))} |"
              for r in open_pqs]
    else:
        L.append("None.")
    L += ["", "## Next step", "",
          f"{len(handoff)} workshop IDs are mapped to register IDs in the report's hand-off table. "
          f"Run `/drivers` to carry them into the drivers register, then `/add` to design against them."]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="qawkit.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prep")
    p.add_argument("--drivers", required=True, type=Path)
    p.add_argument("--previous-report", type=Path)
    p.add_argument("--system", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--out", required=True, type=Path)
    for name in ("ballot", "summary"):
        s = sub.add_parser(name)
        s.add_argument("report", type=Path)
        s.add_argument("--out", required=True, type=Path)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        if a.cmd == "prep":
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", a.date):
                raise KitError(f"--date must be YYYY-MM-DD, got {a.date!r}")
            text = build_prep(a.drivers, a.system, a.date, a.out, a.previous_report)
        elif a.cmd == "ballot":
            text = build_ballot(a.report, a.out)
        else:
            text = build_summary(a.report, a.out)
    except KitError as e:
        print(f"qawkit: {e}", file=sys.stderr)
        return 2
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
