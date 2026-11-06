#!/usr/bin/env python3
"""QAW kit: generate the Quality Attribute Workshop's working artifacts from the documentation
that already exists. Standard library only; the same inputs always give the same output.

  qawkit.py prep    --drivers DIR [--previous-report FILE] [--domain KEY[,KEY]] --system NAME
                    --date YYYY-MM-DD --out FILE
  qawkit.py agenda  --format NAME --date YYYY-MM-DD [--start HH:MM] --system NAME --out FILE
  qawkit.py ballot  REPORT --out FILE
  qawkit.py tally   VOTE_SHEET --out FILE
  qawkit.py status  REPORT [--date YYYY-MM-DD] [--out FILE]
  qawkit.py lint    REPORT [--out FILE]
  qawkit.py summary REPORT --out FILE

prep     before the session: documented answers to confirm (with their sources), the ISO/IEC
         25010 characteristics with no scenario and their questions, the questions for the kind
         of system (--domain), each participant's questions for their role, and parked
         questions still open from the last workshop.
agenda   before the session: a dated, timed agenda from the facilitation playbook's timeboxes.
ballot   at Step 7: the vote sheet for the consolidated scenarios, with the vote budget computed.
tally    at Step 7: totals, the budget check and the ranking from a filled-in vote sheet.
status   at any time: which steps are done, the next step, and the gaps so far.
lint     at Step 8 and before the quality gate: scenario smells, each with the question to ask.
summary  after the session: a one-page result for the sponsor, taken from the finished report.

Exit codes: 0 written (lint: no findings), 1 lint findings, 2 bad arguments or unreadable input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "references" / "qaw-question-guide.md"
PLAYBOOK = ROOT / "references" / "qaw-facilitation-playbook.md"

# Functional suitability is captured as use cases, not quality attribute scenarios, so a missing
# scenario for it is not a gap.
ISO_CHARACTERISTICS = (
    "Performance efficiency", "Compatibility", "Interaction capability", "Reliability",
    "Security", "Maintainability", "Flexibility", "Safety",
)
ROLE_STOPWORDS = {"or", "and", "the", "their", "role", "unfilled", "of", "a"}
SCENARIO_TYPES = ("use-case", "growth", "exploratory")
OPEN_DONE = ("answered", "closed", "done")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


class KitError(Exception):
    """Input the kit cannot work from; the message says what is wrong."""


# --------------------------------------------------------------------------- #
# Markdown reading helpers
# --------------------------------------------------------------------------- #

def kv_bullets(text: str) -> dict[str, str]:
    """`- **Key**: value` lines → {key: value}; the first occurrence of a key wins."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^[ \t]*-[ \t]*\*\*([^*]+)\*\*[ \t]*:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE):
        out.setdefault(m.group(1).strip(), m.group(2).strip())
    return out


def table_cells(text: str, header_contains: str) -> tuple[list[str], list[list[str]]]:
    """Header and rows (lists of cells, padded to the header) of the first pipe table whose
    header contains `header_contains`."""
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
                rows.append(cells)
            return head, rows
    return [], []


def table(text: str, header_contains: str) -> list[dict[str, str]]:
    """Rows of the first pipe table whose header contains `header_contains`, keyed by header."""
    head, rows = table_cells(text, header_contains)
    return [dict(zip(head, cells)) for cells in rows]


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


def logical_lines(text: str) -> list[str]:
    """Lines with wrapped continuations (indented, not a new list item) joined to the line above."""
    out: list[str] = []
    for ln in text.splitlines():
        if out and out[-1].strip() and re.match(r"^\s{2,}\S", ln) and not re.match(r"^\s*([-*]|\d+\.)\s", ln):
            out[-1] += " " + ln.strip()
        else:
            out.append(ln)
    return out


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


def guide_system_types(guide: str) -> dict[str, tuple[str, list[str]]]:
    """`--domain` key → (heading, questions), from the guide's *Questions by system type*.
    Each section names its key on a line such as: Key: `ai`."""
    body = section(guide, r"questions by system type")
    out: dict[str, tuple[str, list[str]]] = {}
    for m in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###\s|\Z)", body, re.MULTILINE | re.DOTALL):
        key = re.search(r"Key:\s*`([a-z0-9-]+)`", m.group(2))
        if key:
            out[key.group(1)] = (m.group(1).strip(), [strip_md(q) for q in numbered_items(m.group(2))])
    return out


def guide_part_questions(guide: str) -> dict[str, str]:
    """Six-part scenario part → the question that fills it (the guide's Step 8 table)."""
    step8 = re.search(r"^###\s+Step 8\b.*?$(.*?)(?=^###\s|^##\s|\Z)", guide,
                      re.MULTILINE | re.DOTALL)
    rows = table(step8.group(1), "Part") if step8 else []
    return {r.get("Part", ""): r.get("Question", "") for r in rows if r.get("Part")}


def _phrase_key(s: str) -> str:
    return strip_md(s).strip('"“”').strip().rstrip(".").lower()


def guide_vague_answers(guide: str) -> dict[str, str]:
    """Vague phrase (lower case, no quotes or final full stop) → the follow-up question, from the
    guide's *Turning vague answers into scenarios* table."""
    rows = table(section(guide, r"turning vague answers"), "stakeholder says")
    return {_phrase_key(r.get("The stakeholder says", "")): r.get("Ask next", "") for r in rows}


# --------------------------------------------------------------------------- #
# Reading the facilitation playbook
# --------------------------------------------------------------------------- #

NEXT_DAY = "Next day"


def playbook_formats(playbook: str) -> dict[str, list[tuple[str, int]]]:
    """Format → [(block, minutes)] from the playbook's *Timeboxes*; a *Next day* row is kept as
    (NEXT_DAY, 0)."""
    body = section(playbook, r"timeboxes")
    out: dict[str, list[tuple[str, int]]] = {}
    for m in re.finditer(r"^###\s+(\S+)\s*\n(.*?)(?=^###\s|\Z)", body, re.MULTILINE | re.DOTALL):
        fmt, blocks = m.group(1).strip(), []
        for r in table(m.group(2), "Block"):
            name, mins = r.get("Block", "").strip(), r.get("Minutes", "").strip()
            if name.lower() == NEXT_DAY.lower():
                blocks.append((NEXT_DAY, 0))
            elif re.fullmatch(r"\d+", mins) and int(mins) > 0:
                blocks.append((name, int(mins)))
            else:
                raise KitError(f"playbook format {fmt}: block {name!r} has no minutes ({mins!r})")
        out[fmt] = blocks
    return out


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
            and r.get("Status", "").strip().lower() not in OPEN_DONE]


# --------------------------------------------------------------------------- #
# prep
# --------------------------------------------------------------------------- #

def _link(target: str, out: Path, label: str) -> str:
    rel = os.path.relpath(target, out.parent).replace(os.sep, "/")
    return f"[{label}]({rel})"


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


def build_prep(drivers_dir: Path, system: str, date: str, out: Path,
               previous_report: Path | None = None, guide_text: str | None = None,
               domains: list[str] | None = None) -> str:
    guide_text = guide_text if guide_text is not None else GUIDE.read_text(encoding="utf-8")
    system_types = guide_system_types(guide_text)
    domains = list(dict.fromkeys(domains or []))
    unknown = [d for d in domains if d not in system_types]
    if unknown:
        raise KitError(f"unknown --domain {', '.join(unknown)}; the question guide has "
                       f"{', '.join(sorted(system_types)) or 'none'}")
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

    set_aside = not_significant_reasons(read_report(previous_report, "previous report")) \
        if previous_report is not None else {}
    open_gaps = [c for c in gaps if c not in set_aside]
    L += ["## Quality characteristics with no scenario", ""]
    if open_gaps:
        L += [f"{len(open_gaps)} of the {len(ISO_CHARACTERISTICS)} ISO/IEC 25010 characteristics "
              f"that scenarios cover have no scenario in the register"
              + (" and were not set aside at the last workshop" if set_aside else "")
              + ". Ask these in Step 4; record each answer as a driver, or as not significant here "
              "with the reason. Functional suitability is left out because use cases cover it.", ""]
        for c in open_gaps:
            L += [f"### {c}", ""]
            L += [f"{i}. {q}" for i, q in enumerate(attr_q.get(c, []), 1)] or \
                 ["The question guide has no questions for this characteristic."]
            L.append("")
    elif gaps:
        L += ["Every characteristic without a scenario was set aside as not significant at the "
              "last workshop; the next section asks whether that still holds.", ""]
    else:
        L += ["Every ISO/IEC 25010 characteristic that scenarios cover has at least one scenario. "
              "Spend Step 5 on what has changed since the scenarios were written.", ""]

    kept = [c for c in gaps if c in set_aside]
    if kept:
        L += ["## Characteristics set aside last time", "",
              f"The last workshop recorded these as not significant. Read the reason out and ask "
              f"whether it still holds; if it no longer does, ask the characteristic's questions "
              f"from the guide.", "",
              "| Characteristic | Reason recorded | Ask |", "|----------------|-----------------|-----|"]
        L += [f"| {c} | {_cell(set_aside[c])} | Does this still hold, or has something changed "
              f"that makes it matter now? |" for c in kept]
        L.append("")

    if domains:
        L += ["## Questions for this kind of system", "",
              "From the question guide's system-type sections. Add them to Steps 4 and 5.", ""]
        for d in domains:
            heading, qs = system_types[d]
            L += [f"### {heading}", ""]
            L += [f"{i}. {q}" for i, q in enumerate(qs, 1)]
            L.append("")

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


def read_report(report: Path, what: str = "report") -> str:
    if not report.is_file():
        raise KitError(f"{what} not found: {report}")
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
         f"scenarios, rounded up. Votes may be stacked on one scenario. Fill in a column per "
         f"participant and leave Total empty; `qawkit.py tally` adds the totals, checks the "
         f"budget and writes the ranking for Step 7 of the report.",
         "",
         "| Scenario | " + " | ".join(p["ID"] for p in people) + " | Total |",
         "|----------|" + "|".join(":---:" for _ in people) + "|:-----:|"]
    for s in scenarios:
        L.append(f"| {s['id']} — {_cell(strip_md(s['scenario']))} | " + " | ".join("" for _ in people) + " | |")
    L += ["", "Participants: " + "; ".join(f"{p['ID']} {p.get('Name', '')}".strip() for p in people) + "."]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# agenda
# --------------------------------------------------------------------------- #

def parse_date(s: str, flag: str = "--date") -> dt.date:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        raise KitError(f"{flag} must be YYYY-MM-DD, got {s!r}")
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        raise KitError(f"{flag} is not a calendar date: {s!r}") from None


def parse_clock(s: str) -> int:
    """`HH:MM` (24-hour) → minutes after midnight."""
    m = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", s)
    if not m:
        raise KitError(f"--start must be HH:MM on a 24-hour clock, got {s!r}")
    return int(m.group(1)) * 60 + int(m.group(2))


def clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def next_working_day(d: dt.date) -> dt.date:
    """The next Monday-to-Friday date after `d`."""
    d += dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def _is_break(block: str) -> bool:
    return block.lower() in ("break", "lunch")


def build_agenda(fmt: str, system: str, date: str, start: str = "09:00",
                 playbook_text: str | None = None) -> str:
    playbook_text = playbook_text if playbook_text is not None else PLAYBOOK.read_text(encoding="utf-8")
    formats = playbook_formats(playbook_text)
    if fmt not in formats:
        raise KitError(f"unknown --format {fmt!r}; the facilitation playbook has "
                       f"{', '.join(formats) or 'none'}")
    day, t0 = parse_date(date), parse_clock(start)
    unit = "Session" if fmt == "remote" else "Day"
    days: list[tuple[dt.date, list[tuple[int, int, str, int]]]] = [(day, [])]
    t = t0
    for name, mins in formats[fmt]:
        if name == NEXT_DAY:
            day, t = next_working_day(day), t0
            days.append((day, []))
            continue
        if t + mins > 24 * 60:
            raise KitError(f"the {fmt} agenda runs past midnight when it starts at {start}")
        days[-1][1].append((t, t + mins, name, mins))
        t += mins
    days = [d for d in days if d[1]]
    blocks = [b for _, rows in days for b in rows]
    breaks = sum(b[3] for b in blocks if _is_break(b[2]))
    work = sum(b[3] for b in blocks) - breaks
    first = days[0][0]
    L = [f"# QAW agenda — {system}", "",
         f"- **Format**: {fmt}",
         f"- **Starts**: {first.isoformat()} ({WEEKDAYS[first.weekday()]}) at {start}",
         f"- **Length**: {plural(len(days), unit.lower())}, {duration(work)} of workshop time "
         f"and {duration(breaks)} of breaks", ""]
    L += [f"This is the {fmt} agenda for the {system} Quality Attribute Workshop, timed from the "
          f"facilitation playbook. When a block overruns, take the time from Step 8 and never "
          f"from the vote in Step 7: a scenario can be refined later, an unprioritised list "
          f"cannot be used.", ""]
    for i, (d, rows) in enumerate(days, 1):
        L += [f"## {unit} {i} — {d.isoformat()} ({WEEKDAYS[d.weekday()]})", "",
              "| Time | Block | Minutes |", "|------|-------|--------:|"]
        L += [f"| {clock(a)}–{clock(b)} | {name} | {mins} |" for a, b, name, mins in rows]
        L.append("")
    L += ["## Before the workshop", "",
          "Send this agenda three days ahead with the business drivers and, when a drivers "
          "register exists, the preparation sheet (`qaw-prep.md`). Ask the sponsor to bring "
          "numbers: users, budget and deadlines."]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# tally
# --------------------------------------------------------------------------- #

def read_vote_sheet(text: str) -> tuple[list[str], list[tuple[str, list[int]]], str]:
    """Participants, [(scenario ID, votes per participant)] and the stated budget ('' if none)
    from a filled-in vote sheet; a blank cell is no votes."""
    head, rows = table_cells(text, "Total")
    if len(head) < 3 or head[-1].strip().lower() != "total":
        raise KitError("the vote sheet has no table ending in a Total column")
    people = head[1:-1]
    votes: list[tuple[str, list[int]]] = []
    for cells in rows:
        m = re.match(r"\s*((?:CS|S)-\d+)\b", strip_md(cells[0]))
        if not m:
            continue
        counts = []
        for person, c in zip(people, cells[1:-1]):
            c = strip_md(c)
            if not c:
                counts.append(0)
            elif re.fullmatch(r"\d+", c):
                counts.append(int(c))
            else:
                raise KitError(f"{m.group(1)}, {person}: {c!r} is not a whole number of votes")
        votes.append((m.group(1), counts))
    if not votes:
        raise KitError("the vote sheet has no scenario rows")
    return people, votes, kv_bullets(text).get("Votes per participant", "")


def ranking(totals: list[tuple[str, int]]) -> str:
    """`CS-1 (3) = CS-5 (3) > CS-2 (2)`: most votes first, ties in sheet order."""
    order = sorted(range(len(totals)), key=lambda i: (-totals[i][1], i))
    parts: list[str] = []
    prev: int | None = None
    for i in order:
        sid, total = totals[i]
        if prev is not None:
            parts.append("=" if total == prev else ">")
        parts.append(f"{sid} ({total})")
        prev = total
    return " ".join(parts)


def build_tally(sheet: Path, out: Path) -> str:
    text = read_report(sheet, "vote sheet")
    system = re.sub(r"^QAW vote sheet\s*[—-]\s*", "", title_of(text))
    people, votes, stated = read_vote_sheet(text)
    budget = vote_budget(len(votes))
    if stated and (not stated.isdigit() or int(stated) != budget):
        raise KitError(f"the sheet gives {stated!r} votes per participant, but 30 % of "
                       f"{len(votes)} scenarios rounded up is {budget}")
    spent = [sum(v[1][j] for v in votes) for j in range(len(people))]
    for person, n in zip(people, spent):
        if n > budget:
            raise KitError(f"{person} cast {n} votes; each participant has {budget}")
    totals = [(sid, sum(counts)) for sid, counts in votes]
    possible = budget * len(people)
    L = [f"# QAW vote tally — {system}" if system else "# QAW vote tally", "",
         f"- **Vote sheet**: {_link(str(sheet), out, sheet.name)}",
         f"- **Votes per participant**: {budget}",
         f"- **Votes cast**: {sum(spent)} of {possible}", ""]
    L += [f"{plural(len(people), 'participant')} cast {sum(spent)} of their {possible} votes on "
          f"{plural(len(votes), 'consolidated scenario')}. The next section replaces the budget "
          f"line, the vote table and the ranking in Step 7 of the report.", ""]
    L += ["## Step 7 of the report", "",
          f"**Vote budget** = ceil(0.30 × {len(votes)}) = **{budget}** votes per stakeholder "
          f"({len(people)} stakeholders → {possible} votes).", "",
          "| Scenario | " + " | ".join(people) + " | Total |",
          "|----------|" + "|".join(":---:" for _ in people) + "|:-----:|"]
    for (sid, counts), (_, total) in zip(votes, totals):
        L.append(f"| {sid} | " + " | ".join(str(c) for c in counts) + f" | {total} |")
    L += ["", f"**Ranked**: {ranking(totals)}."]
    unspent = [(person, n) for person, n in zip(people, spent) if n < budget]
    if unspent:
        L += ["", "## Unspent votes", "",
              "Ask each of these participants whether to place the rest before the ranking is "
              "final; a proxy vote may stay partial, and the report says so.", ""]
        L += [f"- {person} cast {n} of {budget} votes." for person, n in unspent]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

def _filled(cell: str) -> bool:
    c = strip_md(cell)
    return bool(c) and not re.fullmatch(r"<[^>]*>", c)


def _id_rows(sec: str, header: str, id_re: str, col: str) -> list[dict[str, str]]:
    return [r for r in table(sec, header)
            if re.match(id_re + r"$", strip_md(r.get(next(iter(r), ""), ""))) and _filled(r.get(col, ""))]


def without_comments(text: str) -> str:
    """The report without HTML comments, which hold template guidance, not content."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def report_progress(text: str) -> list[tuple[str, str, str]]:
    """[(step, state, detail)] for Steps 0–9, parked questions and the hand-off; state is
    done, not started (section present, nothing filled in) or missing (no section)."""
    text = without_comments(text)
    def sec(title_re: str) -> str | None:
        m = re.search(r"^##\s[^\n]*" + title_re, text, re.MULTILINE | re.IGNORECASE)
        return section(text, title_re) if m else None

    rows: list[tuple[str, str, str]] = []

    def add(step: str, body: str | None, n: int, detail: str) -> None:
        state = "missing" if body is None else ("done" if n else "not started")
        rows.append((step, state, detail if n else ""))

    s0 = sec(r"starting point")
    mode = strip_md(kv_bullets(s0 or "").get("Entry mode", "")).lower()
    inputs = [r for r in table(s0 or "", "Input") if _filled(r.get("Input", ""))]
    add("Step 0 — Starting point", s0, int(mode in ("greenfield", "partial", "refresh") and bool(inputs)),
        f"{mode} mode, {plural(len(inputs), 'input')}")
    s1 = sec(r"introduction")
    people = [r for r in report_participants(s1 and text or "") if _filled(r.get("Name", ""))]
    add("Step 1 — Introductions", s1, len(people), plural(len(people), "participant"))
    s2 = sec(r"business")
    goals = _id_rows(s2 or "", "ID", r"BG-\d+", "Business driver / goal")
    add("Step 2 — Business drivers", s2, len(goals), plural(len(goals), "business goal"))
    s3 = sec(r"architectural plan")
    facts = [v for v in kv_bullets(s3 or "").values() if _filled(v)]
    add("Step 3 — Architectural plan", s3, len(facts), plural(len(facts), "item") + " recorded")
    s4 = sec(r"architectural driver")
    ads = _id_rows(s4 or "", "Architectural driver", r"AD-\d+", "Architectural driver")
    add("Step 4 — Architectural drivers", s4, len(ads), plural(len(ads), "driver"))
    s5 = sec(r"brainstorm")
    raw = [r for r in table(s5 or "", "Scenario") if re.match(r"S-\d+$", r.get("ID", ""))
           and _filled(next((v for k, v in r.items() if k.startswith("Scenario")), ""))]
    types = {t: sum(1 for r in raw if strip_md(next((v for k, v in r.items() if k.startswith("Type")), "")).lower() == t)
             for t in SCENARIO_TYPES}
    add("Step 5 — Scenario brainstorming", s5, len(raw),
        plural(len(raw), "raw scenario") + ": " + ", ".join(f"{n} {t}" for t, n in types.items()))
    s6 = sec(r"consolidat")
    cons = [c for c in report_consolidated(text) if _filled(c["scenario"])] if s6 is not None else []
    add("Step 6 — Consolidation", s6, len(cons), plural(len(cons), "consolidated scenario"))
    s7 = sec(r"prioriti")
    budget = re.search(r"\*\*(\d+)\*\*\s*votes?", s7 or "")
    ranked = re.search(r"^\*\*Ranked\*\*\s*:\s*(.+)$", s7 or "", re.MULTILINE)
    add("Step 7 — Prioritisation", s7, int(bool(budget and ranked)),
        f"{budget.group(1) if budget else '?'} votes each, ranking recorded")
    s8 = sec(r"refine")
    refined = re.findall(r"^###\s+(CS-\d+)\b", s8 or "", re.MULTILINE)
    add("Step 8 — Refinement", s8, len(refined), plural(len(refined), "refined scenario"))
    s9 = sec(r"utility tree")
    leaves = [r for r in table(s9 or "", "Priority")
              if re.search(r"\b[A-Z]{1,4}QA-\d+\b", next((v for k, v in r.items() if k.startswith("Leaf")), ""))]
    stars = sum(1 for r in leaves if "★" in "".join(r.values()))
    add("Step 9 — Utility tree", s9, len(leaves), f"{plural(len(leaves), 'leaf')}, {stars} ★".replace("leafs", "leaves"))
    pq = sec(r"parked question")
    pqs = [r for r in table(pq or "", "Question") if re.match(r"PQ-\d+$", r.get("ID", "")) and _filled(r.get("Question", ""))]
    none_said = pq is not None and not pqs and re.search(r"\bnone\b", pq, re.IGNORECASE) is not None
    open_n = sum(1 for r in pqs if r.get("Status", "").strip().lower() not in OPEN_DONE)
    add("Parked questions", pq, int(bool(pqs) or none_said),
        f"{plural(len(pqs), 'question')}, {open_n} open" if pqs else "none")
    ho = sec(r"hand-off")
    maps = [r for r in table(ho or "", "Becomes") if re.match(r"(CS|AD)-\d+$", r.get("Workshop ID", ""))
            and re.search(r"\b(BG|UC|CON)-\d+\b|\b[A-Z]{1,4}QA-\d+\b", r.get("Becomes", ""))]
    add("Hand-off to the drivers register", ho, len(maps), plural(len(maps), "mapping"))
    return rows


def not_significant_reasons(text: str) -> dict[str, str]:
    """Characteristic → the first line that records it as not significant, without list or
    emphasis markers."""
    out: dict[str, str] = {}
    for ln in logical_lines(text):
        if "not significant" not in ln.lower():
            continue
        for c in ISO_CHARACTERISTICS:
            if c.lower() in ln.lower() and c not in out:
                out[c] = strip_md(re.sub(r"^\s*[-*]\s+", "", ln))
    return out


def not_significant(text: str) -> set[str]:
    """Characteristics the report records as not significant (on a line saying so)."""
    return set(not_significant_reasons(text))


def uncovered_characteristics(text: str, attrs: set[str]) -> list[str]:
    """ISO/IEC 25010 characteristics with no utility-tree leaf and no not-significant record."""
    skip = not_significant(text)
    return [c for c in ISO_CHARACTERISTICS
            if c not in skip and not any(a.startswith(c.lower()) for a in attrs)]


def tree_characteristics(text: str) -> set[str]:
    """Lower-cased first-column values of utility-tree rows that carry a leaf scenario ID."""
    return {strip_md(next(iter(r.values()), "")).lower()
            for r in table(section(text, r"utility tree"), "Priority")
            if re.search(r"\b[A-Z]{1,4}QA-\d+\b", " ".join(r.values()))}


def report_gaps(text: str, today: dt.date | None = None) -> list[str]:
    text = without_comments(text)
    gaps: list[str] = []
    s4, s5 = section(text, r"architectural driver"), section(text, r"brainstorm")
    ads = [r["ID"] for r in _id_rows(s4, "Architectural driver", r"AD-\d+", "Architectural driver")]
    raw = [r for r in table(s5, "Scenario") if re.match(r"S-\d+$", r.get("ID", ""))
           and _filled(next((v for k, v in r.items() if k.startswith("Scenario")), ""))]
    if ads and raw:
        missing = [a for a in ads if not re.search(r"\b" + a + r"\b", s5)]
        if missing:
            gaps.append(f"Drivers with no brainstormed scenario: {', '.join(missing)}. Ask the "
                        f"Step 5 restart prompt: which driver has no scenario yet?")
    if raw:
        types = {strip_md(next((v for k, v in r.items() if k.startswith("Type")), "")).lower() for r in raw}
        absent = [t for t in SCENARIO_TYPES if t not in types]
        if absent:
            gaps.append(f"Scenario types with no brainstormed scenario: {', '.join(absent)}. Use "
                        f"the guide's Step 5 prompt for that type.")
    attrs = tree_characteristics(text)
    if attrs:
        uncovered = uncovered_characteristics(text, attrs)
        if uncovered:
            gaps.append(f"ISO/IEC 25010 characteristics with no utility-tree leaf: "
                        f"{', '.join(uncovered)}. Record each as not significant here with the "
                        f"reason, or ask its questions from the guide.")
    cons = [c["id"] for c in report_consolidated(text) if _filled(c["scenario"])]
    handoff = section(text, r"hand-off")
    if cons and re.search(r"^\|\s*(CS|AD)-\d+\s*\|", handoff, re.MULTILINE):
        unmapped = [c for c in cons if not re.search(r"^\|\s*" + c + r"\s*\|", handoff, re.MULTILINE)]
        if unmapped:
            gaps.append(f"Consolidated scenarios missing from the hand-off table: {', '.join(unmapped)}.")
    for r in table(section(text, r"parked question"), "Question"):
        if not re.match(r"PQ-\d+$", r.get("ID", "")) or not _filled(r.get("Question", "")) \
                or r.get("Status", "").strip().lower() in OPEN_DONE:
            continue
        due = r.get("Due", "").strip()
        late = ""
        if today and re.fullmatch(r"\d{4}-\d{2}-\d{2}", due) and dt.date.fromisoformat(due) < today:
            late = f", overdue since {due}"
        gaps.append(f"{r['ID']} is open (owner {r.get('Owner', '').strip() or 'none'}, due "
                    f"{due or 'not set'}{late}): {r.get('Question', '').strip()}")
    return gaps


def build_status(report: Path, today: str | None = None) -> str:
    text = read_report(report)
    system = re.sub(r"^Quality Attribute Workshop\s*[—-]\s*", "", title_of(text))
    day = parse_date(today) if today else None
    progress = report_progress(text)
    nxt = next((step for step, state, _ in progress if state != "done"), None)
    L = [f"# QAW status — {system}", "",
         f"- **Report**: {report.name}",
         f"- **Next step**: {nxt or 'none — every step is recorded; run the quality gate'}"]
    if day:
        L.append(f"- **Checked on**: {day.isoformat()}")
    L += ["", "| Step | State | Recorded |", "|------|-------|----------|"]
    L += [f"| {step} | {state} | {detail} |" for step, state, detail in progress]
    gaps = report_gaps(text, day)
    L += ["", "## Gaps", ""]
    L += [f"- {g}" for g in gaps] or ["None found in the steps recorded so far."]
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# lint
# --------------------------------------------------------------------------- #

SIX_PARTS = ("Source of stimulus", "Stimulus", "Artifact", "Environment", "Response", "Response measure")

# Vague words → the guide's *Turning vague answers* row whose follow-up question to ask. The
# phrases must exist in the guide (the unit tests check); None means "ask for a number".
VAGUE_TERMS: tuple[tuple[str, str | None], ...] = (
    (r"fast|faster|quick|quickly|speedy|snappy|responsive|instant(?:ly)?", "It must be fast"),
    (r"always (?:up|on|available)|highly available|high availability|no downtime|24/7", "It must always be up"),
    (r"secure|securely", "It must be secure"),
    (r"scale|scales|scalable|scalability", "It must scale"),
    (r"easy to use|user[- ]friendly|intuitive|simple to use", "It must be easy to use"),
    (r"easy to (?:change|modify|extend|maintain)|flexible|maintainable", "It must be easy to change"),
    (r"real[- ]time", "Real-time"),
    (r"like the (?:current|old|existing) system", "Like the current system"),
    (r"robust|reliable|reliably|efficient|efficiently|performant|minimal|reasonable|acceptable"
     r"|appropriate|adequate|sufficient|as soon as possible|asap", None),
)
GENERIC_SOURCES = {"user", "users", "the user", "a user", "the users", "system", "the system",
                   "someone", "anyone", "client", "the client", "stakeholder", "actor"}
ID_RE = re.compile(r"\b(?:[A-Z]{1,4}QA|CS|S|AD|BG|UC|CON|PQ|ST)-\d+\b")


def _vague_hits(value: str, only_guide_rows: bool) -> list[tuple[str, str | None]]:
    hits = []
    for pattern, phrase in VAGUE_TERMS:
        if only_guide_rows and phrase is None:
            continue
        m = re.search(r"\b(?:" + pattern + r")\b", value, re.IGNORECASE)
        if m:
            hits.append((m.group(0), phrase))
    return hits


def lint_report(text: str, guide_text: str) -> list[tuple[str, str, str]]:
    """[(where, problem, question to ask)] for scenario smells the guide can fix."""
    text = without_comments(text)
    parts_q = guide_part_questions(guide_text)
    vague_q = guide_vague_answers(guide_text)
    ask_measure = parts_q.get("Response measure", "")
    findings: list[tuple[str, str, str]] = []

    for r in table(section(text, r"brainstorm"), "Scenario"):
        if re.match(r"S-\d+$", r.get("ID", "")):
            t = strip_md(next((v for k, v in r.items() if k.startswith("Type")), "")).lower()
            if t not in SCENARIO_TYPES:
                findings.append((r["ID"], f"type {t or 'missing'!r} is not one of {' / '.join(SCENARIO_TYPES)}",
                                 "Is this a normal use, an expected change, or a stress or failure situation?"))

    refine = section(text, r"refine")
    for m in re.finditer(r"^###\s+((?:CS|S)-\d+)\b.*?$(.*?)(?=^###\s|\Z)", refine, re.MULTILINE | re.DOTALL):
        sid, body = m.group(1), m.group(2)
        kv = kv_table(body)
        for part in SIX_PARTS:
            if not _filled(kv.get(part, "")):
                findings.append((sid, f"{part.lower()} is empty", parts_q.get(part, "")))
        source = strip_md(kv.get("Source of stimulus", "")).lower().rstrip(".")
        if source in GENERIC_SOURCES:
            findings.append((sid, f"source of stimulus {source!r} names no role or system",
                             parts_q.get("Source of stimulus", "")))
        measure = kv.get("Response measure", "")
        if _filled(measure) and not re.search(r"\d", ID_RE.sub("", measure)):
            findings.append((sid, "response measure has no number", ask_measure))
        for field, only_rows in (("Response measure", False), ("Response", True)):
            for word, phrase in _vague_hits(kv.get(field, ""), only_rows):
                ask = vague_q.get(phrase.lower(), "") if phrase else ask_measure
                findings.append((sid, f"{field.lower()} uses the vague word {word!r}", ask))
        goals = kv_bullets(body).get("Business goals", "")
        if not re.search(r"\bBG-\d+\b", goals):
            findings.append((sid, "cites no business goal (BG-<n>)",
                             "Which business goal does this scenario protect?"))

    attrs = tree_characteristics(text)
    if attrs:
        for c in uncovered_characteristics(text, attrs):
            findings.append((c, "no utility-tree leaf and not recorded as not significant here",
                             "Is this characteristic truly unimportant here, or did nobody ask? "
                             "Record a driver, or 'not significant here' with the reason."))

    for r in table(section(text, r"utility tree"), "Priority"):
        leaf = next((v for k, v in r.items() if k.startswith("Leaf")), "")
        ids = re.findall(r"\b[A-Z]{1,4}QA-\d+\b", leaf)
        if ids and not re.search(r"\d", ID_RE.sub("", leaf)):
            findings.append((ids[0], "utility-tree leaf has no measure", ask_measure))
    return findings


def build_lint(report: Path, guide_text: str | None = None) -> tuple[str, int]:
    text = read_report(report)
    guide_text = guide_text if guide_text is not None else GUIDE.read_text(encoding="utf-8")
    system = re.sub(r"^Quality Attribute Workshop\s*[—-]\s*", "", title_of(text))
    findings = lint_report(text, guide_text)
    L = [f"# QAW lint — {system}", "", f"- **Report**: {report.name}",
         f"- **Findings**: {len(findings)}", ""]
    if findings:
        L += ["Each finding is a gap one question can close. Ask the question in the "
              "last column, record the answer in the report, and run the lint again.", "",
              "| Where | Problem | Ask next |", "|-------|---------|----------|"]
        L += [f"| {w} | {_cell(p)} | {_cell(q)} |" for w, p, q in findings]
    else:
        L.append("No findings: every refined scenario has six filled parts, a named source, a "
                 "numeric response measure without vague words and a business goal, and every "
                 "utility-tree leaf carries a measure.")
    return "\n".join(L).rstrip() + "\n", len(findings)


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
    open_pqs = [r for r in pqs if r.get("Status", "").strip().lower() not in OPEN_DONE]
    handoff = [r for r in table(section(text, r"hand-off"), "Becomes") if re.match(r"(CS|AD)-\d+$", r.get("Workshop ID", ""))]

    L = [f"# QAW summary — {system}", "",
         f"- **Workshop date**: {head.get('Date(s)', head.get('Date', 'not recorded'))}"]
    if head.get("Format"):
        L.append(f"- **Format**: {head['Format']}")
    L += [f"- **Report status**: {head.get('Status', 'not recorded')}",
          f"- **Entry mode**: {mode}",
          f"- **Full report**: {_link(str(report), out, 'qaw-report.md')}", ""]
    def agree(n: int, one: str, many: str) -> str:
        return f"{n} {one if n == 1 else many}"
    L += [f"{plural(len(people), 'participant')} produced {plural(len(raw), 'raw scenario')}, "
          f"consolidated to {len(cons)}; {agree(len(refined), 'was', 'were')} refined into measurable "
          f"six-part scenarios. {agree(len(star), 'carries', 'carry')} the highest business value "
          f"and technical risk, and {agree(len(open_pqs), 'question remains', 'questions remain')} open.", ""]
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
    p.add_argument("--domain", action="append", default=[],
                   help="system type from the question guide (ai, saas, …); repeat or comma-separate")
    p.add_argument("--system", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--out", required=True, type=Path)
    g = sub.add_parser("agenda")
    g.add_argument("--format", required=True, dest="fmt")
    g.add_argument("--date", required=True)
    g.add_argument("--start", default="09:00")
    g.add_argument("--system", required=True)
    g.add_argument("--out", required=True, type=Path)
    for name in ("ballot", "summary"):
        s = sub.add_parser(name)
        s.add_argument("report", type=Path)
        s.add_argument("--out", required=True, type=Path)
    t = sub.add_parser("tally")
    t.add_argument("sheet", type=Path)
    t.add_argument("--out", required=True, type=Path)
    st = sub.add_parser("status")
    st.add_argument("report", type=Path)
    st.add_argument("--date")
    st.add_argument("--out", type=Path)
    lt = sub.add_parser("lint")
    lt.add_argument("report", type=Path)
    lt.add_argument("--out", type=Path)
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    rc = 0
    try:
        if a.cmd == "prep":
            parse_date(a.date)
            domains = [d.strip() for arg in a.domain for d in arg.split(",") if d.strip()]
            text = build_prep(a.drivers, a.system, a.date, a.out, a.previous_report, domains=domains)
        elif a.cmd == "agenda":
            text = build_agenda(a.fmt, a.system, a.date, a.start)
        elif a.cmd == "ballot":
            text = build_ballot(a.report, a.out)
        elif a.cmd == "tally":
            text = build_tally(a.sheet, a.out)
        elif a.cmd == "status":
            text = build_status(a.report, a.date)
        elif a.cmd == "lint":
            text, n = build_lint(a.report)
            rc = 1 if n else 0
        else:
            text = build_summary(a.report, a.out)
    except KitError as e:
        print(f"qawkit: {e}", file=sys.stderr)
        return 2
    if getattr(a, "out", None) is None:
        sys.stdout.write(text)
        return rc
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(text, encoding="utf-8")
    print(f"wrote {a.out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
