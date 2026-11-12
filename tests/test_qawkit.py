#!/usr/bin/env python3
"""Unit tests for scripts/qawkit.py — the QAW kit generator (prep sheet, agenda, vote sheet, tally,
status, lint, summary). Covers every reader and builder, the CLI's exit codes, and golden files:
the kit committed under each worked example must equal a fresh regeneration, and the example's
vote sheet, tally and Step 7 must agree. Standard library only; exit 0 on success."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import qawkit  # noqa: E402
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


def raises(fn, *args, **kw) -> bool:
    try:
        fn(*args, **kw)
    except qawkit.KitError:
        return True
    return False


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def quiet_main(argv: list[str]) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return qawkit.main(argv)


GUIDE = qawkit.GUIDE.read_text(encoding="utf-8")
PLAYBOOK = qawkit.PLAYBOOK.read_text(encoding="utf-8")

# --------------------------------------------------------------------------- #
# Markdown readers
# --------------------------------------------------------------------------- #

kv = qawkit.kv_bullets("# T\n\n- **Status**: open\n- **Owner**: Eng lead\n- **Status**: later\nplain - **No**: x\n")
check("kv_bullets reads bullets", kv.get("Owner") == "Eng lead")
check("kv_bullets keeps the first occurrence", kv.get("Status") == "open")
check("kv_bullets ignores text that is not a bullet", "No" not in kv)

TBL = "intro\n\n| ID | Name | Role |\n|----|------|------|\n| ST-1 | Ana | sponsor |\n| ST-2 | Bo |\n\nafter\n| ST-3 | x | y |\n"
rows = qawkit.table(TBL, "Role")
check("table reads rows keyed by header", rows[0] == {"ID": "ST-1", "Name": "Ana", "Role": "sponsor"})
check("table pads short rows", rows[1]["Role"] == "")
check("table stops at the first non-table line", len(rows) == 2)
check("table with no matching header is empty", qawkit.table(TBL, "Budget") == [])

kvt = qawkit.kv_table("| Part | Value |\n|------|-------|\n| **Stimulus** | a request |\n| Response | served |\n")
check("kv_table strips bold from keys", kvt.get("Stimulus") == "a request")
check("kv_table skips the separator row", not any(set(k) <= set("-: ") for k in kvt))

DOC = "# X\n\n## Step 1 — Intro\n\none\n\n## Step 2 — Business\n\ntwo\n"
check("section returns its own body only", qawkit.section(DOC, r"intro").strip() == "one")
check("section is case-insensitive", qawkit.section(DOC, r"BUSINESS").strip() == "two")
check("missing section is empty", qawkit.section(DOC, r"nothing") == "")

check("title_of strips the ID prefix", qawkit.title_of("# BG-12: Grow users\n") == "Grow users")
check("title_of keeps a heading with no ID", qawkit.title_of("# Quality Attribute Workshop — X\n")
      == "Quality Attribute Workshop — X")
check("title_of with no heading is empty", qawkit.title_of("no heading") == "")

items = qawkit.numbered_items("1. First line\n   continues here\n2. Second\n\n3. Third\n")
check("numbered_items joins wrapped lines", items[0] == "First line continues here")
check("numbered_items reads every item", len(items) == 3)

# --------------------------------------------------------------------------- #
# Reading the question guide
# --------------------------------------------------------------------------- #

aq = qawkit.guide_attribute_questions(GUIDE)
check("guide has questions for every characteristic the kit checks",
      all(c in aq and aq[c] for c in qawkit.ISO_CHARACTERISTICS))
check("parenthetical heading suffixes are dropped",
      "Reliability" in aq and not any("(" in k for k in aq))
check("each characteristic's questions end with the measure question",
      all(aq[c][-1].startswith("Measure:") for c in qawkit.ISO_CHARACTERISTICS))
check("questions carry no Markdown emphasis", not any("*" in q for qs in aq.values() for q in qs))

rq = qawkit.guide_role_questions(GUIDE)
check("guide role table has eight roles", len(rq) == 8)
check("every role has at least two questions ending in '?'",
      all(len(qs) >= 2 and all(q.endswith("?") for q in qs) for _, qs in rq))

check("'end-user representative' matches the end-user row",
      (qawkit.match_role("end-user representative", rq) or ("",))[0].startswith("End user"))
check("'tester' matches Tester / QA", (qawkit.match_role("tester", rq) or ("",))[0] == "Tester / QA")
check("'sponsor / product owner' matches the sponsor row",
      (qawkit.match_role("sponsor / product owner", rq) or ("",))[0].startswith("Sponsor"))
check("an unknown role has no match", qawkit.match_role("maintainer (role, unfilled)", rq) is None)
check("a tie goes to the earlier row",
      (qawkit.match_role("ops", [("ops one", ["a?"]), ("ops two", ["b?"])]) or ("",))[0] == "ops one")
check("single-letter words never match", qawkit.match_role("x", [("x one", ["a?"])]) is None)

# --------------------------------------------------------------------------- #
# Reading the drivers register
# --------------------------------------------------------------------------- #

BG = "# {id}: Goal {id}\n\n- **Statement**: statement {id}\n- **Measure of success**: measure {id}\n- **Status**: {st}\n"
QA = ("# {id}: Scenario\n\n- **Status**: open\n\n| Part | Value |\n|------|-------|\n"
      "| **ISO/IEC 25010 characteristic** | {ch} |\n| **Response measure** | {m} |\n")


def make_drivers(root: Path, qas: dict[str, str] | None = None, bgs: tuple = ("BG-2", "BG-10", "BG-1"),
                 stakeholders: str | None = None) -> Path:
    d = root / "architecture" / "drivers"
    write(root, "architecture/drivers/README.md", "# Drivers\n")
    for b in bgs:
        write(root, f"architecture/drivers/business-goals/{b}.md", BG.format(id=b, st="open"))
    write(root, "architecture/drivers/business-goals/BG-9.md", BG.format(id="BG-9", st="retired"))
    write(root, "architecture/drivers/constraints/CON-1.md",
          "# CON-1: Postgres\n\n- **Constraint**: must use a | b\n- **Status**: open\n")
    for qid, ch in (qas or {}).items():
        write(root, f"architecture/drivers/quality-attributes/{qid}.md", QA.format(id=qid, ch=ch, m="p95 < 1 s"))
    write(root, "architecture/drivers/quality-attributes/README.md", "# index\n")
    if stakeholders is not None:
        write(root, "architecture/drivers/stakeholders.md", stakeholders)
    return d


with tempfile.TemporaryDirectory() as td:
    d = make_drivers(Path(td), {"PQA-1": "Performance efficiency", "SQA-1": "**Security**"})
    dr = qawkit.load_drivers(d)
    check("business goals load in numeric ID order", [b["id"] for b in dr["bg"]] == ["BG-1", "BG-2", "BG-10"])
    check("retired business goals are skipped", "BG-9" not in [b["id"] for b in dr["bg"]])
    check("a goal's measure of success is what the documentation says", dr["bg"][0]["says"] == "measure BG-1")
    check("constraints load", [c["id"] for c in dr["con"]] == ["CON-1"])
    check("QA scenarios load; README is not a scenario", [q["id"] for q in dr["qa"]] == ["PQA-1", "SQA-1"])
    check("a scenario's characteristic is read without emphasis", dr["qa"][1]["characteristic"] == "Security")
    check("suggested mode with scenarios is refresh", qawkit.suggest_mode(dr) == "refresh")
check("a missing drivers directory is an error", raises(qawkit.load_drivers, Path("/nonexistent/drivers")))
with tempfile.TemporaryDirectory() as td:
    d = make_drivers(Path(td), {"PQA-1": "Performance efficiency", "SQA-1": "Security"})
    write(Path(td), "architecture/drivers/constraints/CON-2.md", "# CON-2: Old\n\n- **Constraint**: x\n- **Status**: retired\n")
    q = d / "quality-attributes" / "SQA-1.md"
    q.write_text(q.read_text().replace("- **Status**: open", "- **Status**: retired (merged into PQA-1)"))
    write(Path(td), "architecture/drivers/quality-attributes/PQA-draft.md", "# notes\n")
    dr = qawkit.load_drivers(d)
    check("retired constraints are skipped", [c["id"] for c in dr["con"]] == ["CON-1"])
    check("retired scenarios are skipped, whatever follows the word", [x["id"] for x in dr["qa"]] == ["PQA-1"])

check("suggested mode with goals only is partial",
      qawkit.suggest_mode({"bg": [{"id": "BG-1"}], "con": [], "qa": []}) == "partial")
check("suggested mode with nothing is greenfield",
      qawkit.suggest_mode({"bg": [], "con": [], "qa": []}) == "greenfield")

ST = ("# Stakeholders\n\n| ID | Name / representative | Role | Concerns | QAW |\n|----|----|----|----|:---:|\n"
      "| ST-1 | Ana | sponsor | cost | ✓ |\n| ST-2 | Bo | tester | tests | — |\n| ST-3 | Cy | maintainer | code | ✓ |\n")
with tempfile.TemporaryDirectory() as td:
    p = write(Path(td), "stakeholders.md", ST)
    people = qawkit.load_participants(p)
    check("participants marked '—' in the QAW column are left out", [x["id"] for x in people] == ["ST-1", "ST-3"])
    p3 = write(Path(td), "s3.md", ST + "| — | (role unfilled) | maintainer | — | ✓ |\n")
    check("rows without an ST-<n> ID are not participants", [x["id"] for x in qawkit.load_participants(p3)] == ["ST-1", "ST-3"])
    p2 = write(Path(td), "s2.md", ST.replace(" QAW |", " Other |"))
    check("with no QAW column everyone is a participant", len(qawkit.load_participants(p2)) == 3)
check("a missing stakeholder register gives no participants",
      qawkit.load_participants(Path("/nonexistent/stakeholders.md")) == [])

PQ = ("# R\n\n## Parked questions\n\n| ID | Question | Raised in | Who can answer | Owner | Due | Status |\n"
      "|----|----|----|----|----|----|----|\n| PQ-1 | Open one? | Step 2 | sponsor | ST-1 | 2026-01-01 | open |\n"
      "| PQ-2 | Done one? | Step 3 | ops | ST-2 | 2026-01-02 | answered |\n\n## Next steps\n")
with tempfile.TemporaryDirectory() as td:
    pq = qawkit.open_parked_questions(write(Path(td), "r.md", PQ))
    check("answered parked questions are not carried over", [r["ID"] for r in pq] == ["PQ-1"])
check("a missing previous report is an error", raises(qawkit.open_parked_questions, Path("/nonexistent.md")))

# --------------------------------------------------------------------------- #
# prep
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = make_drivers(root, {"PQA-1": "Performance efficiency"}, stakeholders=ST)
    out = root / "architecture" / "qaw" / "qaw-prep.md"
    text = qawkit.build_prep(d, "Acme", "2026-01-05", out, write(root, "architecture/qaw/qaw-report.md", PQ))
    check("prep is deterministic", text == qawkit.build_prep(d, "Acme", "2026-01-05", out,
                                                              root / "architecture/qaw/qaw-report.md"))
    check("prep suggests the mode from the register", "- **Suggested entry mode**: refresh" in text)
    check("prep links each documented answer to its source relative to the output",
          "[BG-1](../drivers/business-goals/BG-1.md)" in text)
    check("prep quotes the documented measure", "| BG-1 | measure BG-1 |" in text)
    check("prep escapes a pipe inside a documented answer", "must use a \\| b" in text)
    check("prep lists the uncovered characteristics", "### Security" in text and "### Safety" in text)
    check("prep does not list a covered characteristic", "### Performance efficiency" not in text)
    check("prep never lists functional suitability as a gap", "### Functional suitability" not in text)
    check("prep gives a matched participant their role's questions",
          "### ST-1 — Ana (sponsor)" in text and "What does success look like in numbers?" in text)
    check("prep says when a role has no row in the guide", "has no role row for this role" in text)
    check("prep carries over open parked questions only", "PQ-1" in text and "PQ-2" not in text)
    out.write_text(text, encoding="utf-8")
    check("a generated prep sheet passes the validator", validate.validate_file(out) == [])

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = root / "drivers"
    d.mkdir()
    write(root, "drivers/README.md", "# Drivers\n")
    text = qawkit.build_prep(d, "Blank", "2026-01-05", root / "qaw" / "qaw-prep.md")
    check("an empty register suggests greenfield", "- **Suggested entry mode**: greenfield" in text)
    check("an empty register says every step starts from open questions", "starts from the guide's open questions" in text)
    check("an empty register lists all eight characteristics as gaps", "8 of the 8" in text)
    check("no stakeholder register is said plainly", "No stakeholder register with QAW participants" in text)
    check("without --previous-report there is no parked-questions section", "Parked questions" not in text)

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = make_drivers(root, {f"{chr(65 + i)}QA-1": c for i, c in enumerate(qawkit.ISO_CHARACTERISTICS)})
    text = qawkit.build_prep(d, "Full", "2026-01-05", root / "qaw" / "qaw-prep.md")
    check("full coverage says every characteristic has a scenario", "has at least one scenario" in text)

# --------------------------------------------------------------------------- #
# ballot
# --------------------------------------------------------------------------- #

for n, want in ((1, 1), (3, 1), (4, 2), (6, 2), (10, 3), (11, 4), (12, 4), (20, 6)):
    check(f"vote budget for {n} scenarios is {want}", qawkit.vote_budget(n) == want)
check("no scenarios to vote on is an error", raises(qawkit.vote_budget, 0))

REPORT = """# Quality Attribute Workshop — Acme

- **Date(s)**: 2026-01-10
- **Status**: complete

## Step 0 — Starting point

- **Entry mode**: refresh

## Step 1 — QAW presentation and introductions

| ID | Name | Role | Concerns brought |
|----|------|------|------------------|
| ST-1 | Ana | Sponsor | cost |
| ST-2 | Bo | Architect | change |

## Step 5 — Scenario brainstorming (raw, verbatim)

| ID | Scenario | Type | Contributor | Driver(s) |
|----|----------|------|-------------|-----------|
| S-1 | a | use-case | Ana | AD-1 |
| S-2 | b | growth | Bo | AD-1 |
| S-3 | c | exploratory | Bo | AD-2 |

## Step 6 — Scenario consolidation

| Consolidated ID | Merged from | Scenario |
|-----------------|-------------|----------|
| CS-1 | S-1, S-2 | **Fast** dashboard |
| CS-2 | S-3 | Survive a zone loss |

## Step 7 — Scenario prioritisation

**Ranked**: CS-2 (3) > CS-1 (1).

## Step 8 — Scenario refinement (top scenarios)

### CS-2 — Survive a zone loss

## Step 9 — Quality attribute utility tree

| Quality attribute | Refinement | Leaf scenario (ID — one line) | Priority (V, R) | Status |
|---|---|---|:---:|:---:|
| Reliability | Availability | AQA-1 (CS-2) — survive a zone loss | (H, H) ★ | open |
| Performance efficiency | Time behaviour | PQA-1 (CS-1) — fast dashboard | (M, L) | open |

## Parked questions

| ID | Question | Raised in | Who can answer | Owner | Due | Status |
|----|----------|-----------|----------------|-------|-----|--------|
| PQ-1 | What RPO? | CS-2 | ops | ST-2 | 2026-02-01 | open |
| PQ-2 | Which region? | Step 3 | sponsor | ST-1 | 2026-02-01 | answered |

## Next steps — hand-off to the drivers register

| Workshop ID | Becomes | Notes |
|-------------|---------|-------|
| CS-1 | PQA-1 | |
| CS-2 | AQA-1 | |
| AD-1 | PQA-1 | |
"""

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    rep = write(root, "qaw/qaw-report.md", REPORT)
    out = root / "qaw" / "qaw-vote-sheet.md"
    b = qawkit.build_ballot(rep, out)
    check("ballot states the computed budget", "- **Votes per participant**: 1" in b)
    check("ballot has one column per participant", "| Scenario | ST-1 | ST-2 | Total |" in b)
    check("ballot has one row per consolidated scenario, without emphasis",
          "| CS-1 — Fast dashboard |" in b and "| CS-2 — Survive a zone loss |" in b)
    check("ballot names the system from the report title", b.startswith("# QAW vote sheet — Acme"))
    out.write_text(b, encoding="utf-8")
    check("a generated vote sheet passes the validator", validate.validate_file(out) == [])
    no_people = write(root, "qaw2/qaw-report.md", REPORT.replace("| ST-1 | Ana", "| X-1 | Ana").replace("| ST-2 | Bo", "| X-2 | Bo"))
    check("a report with no ST-<n> participants is an error", raises(qawkit.build_ballot, no_people, out))
    no_cs = write(root, "qaw3/qaw-report.md", REPORT.replace("| CS-1 | S-1", "| X | S-1").replace("| CS-2 | S-3", "| Y | S-3"))
    check("a report with no consolidated scenarios is an error", raises(qawkit.build_ballot, no_cs, out))
check("a missing report is an error", raises(qawkit.build_ballot, Path("/nonexistent.md"), Path("/tmp/x.md")))

# --------------------------------------------------------------------------- #
# summary
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    rep = write(root, "qaw/qaw-report.md", REPORT)
    out = root / "qaw" / "qaw-summary.md"
    s = qawkit.build_summary(rep, out)
    check("summary counts participants, raw, consolidated and refined scenarios",
          "2 participants produced 3 raw scenarios, consolidated to 2; 1 was refined" in s)
    check("summary agrees verbs with singular counts",
          "1 carries the highest business value" in s and "and 1 question remains open." in s)
    check("summary carries the header fields",
          "- **Workshop date**: 2026-01-10" in s and "- **Report status**: complete" in s)
    check("summary carries the entry mode", "- **Entry mode**: refresh" in s)
    check("summary copies the vote ranking", "Vote ranking: CS-2 (3) > CS-1 (1)." in s)
    check("summary lists only the ★ leaves as highest priority",
          "- AQA-1 (CS-2) — survive a zone loss" in s and "PQA-1 (CS-1) — fast" not in s)
    check("summary lists refined scenarios", "- CS-2 — Survive a zone loss" in s)
    check("summary lists open parked questions only", "PQ-1" in s and "PQ-2" not in s)
    check("summary counts hand-off rows", "3 workshop IDs are mapped" in s)
    out.write_text(s, encoding="utf-8")
    check("a generated summary passes the validator", validate.validate_file(out) == [])
    bare = write(root, "q2/qaw-report.md", "# Quality Attribute Workshop — Bare\n\n## Step 1 — Intro\n")
    sb = qawkit.build_summary(bare, root / "q2" / "s.md")
    check("a report without entry mode or ranking says 'not recorded'",
          "- **Entry mode**: not recorded" in sb and "Vote ranking: not recorded." in sb)
    check("a report with nothing refined or parked says so", "None refined yet." in sb and "\nNone.\n" in sb)

# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    rep = write(root, "qaw/qaw-report.md", REPORT)
    d = make_drivers(root)
    check("summary command writes its file and exits 0",
          quiet_main(["summary", str(rep), "--out", str(root / "out" / "s.md")]) == 0
          and (root / "out" / "s.md").is_file())
    check("ballot command exits 0", quiet_main(["ballot", str(rep), "--out", str(root / "b.md")]) == 0)
    check("prep command exits 0", quiet_main(["prep", "--drivers", str(d), "--system", "A", "--date",
                                              "2026-01-01", "--out", str(root / "p.md")]) == 0)
    check("prep with a malformed date exits 2", quiet_main(["prep", "--drivers", str(d), "--system", "A",
                                                            "--date", "Jan 1", "--out", str(root / "p.md")]) == 2)
    check("a missing report exits 2 and writes nothing",
          quiet_main(["summary", str(root / "none.md"), "--out", str(root / "never.md")]) == 2
          and not (root / "never.md").exists())
    check("an unknown command exits 2", quiet_main(["publish"]) == 2)
    check("a missing required option exits 2", quiet_main(["ballot", str(rep)]) == 2)

# --------------------------------------------------------------------------- #
# Guide sections the new commands read
# --------------------------------------------------------------------------- #

st = qawkit.guide_system_types(GUIDE)
check("the guide has seven system types", sorted(st) == ["ai", "api", "data", "iot", "mobile", "regulated", "saas"])
check("every system type has at least four questions ending with the measure",
      all(len(qs) >= 4 and qs[-1].startswith("Measure:") for _, qs in st.values()))
check("system-type headings are read whole", st["regulated"][0] == "Regulated data — payments, health, personal data")
check("a guide without system types gives none", qawkit.guide_system_types("# G\n\n## Other\n") == {})
check("a system-type section without a Key line is skipped",
      qawkit.guide_system_types("## Questions by system type\n\n### Thing\n\n1. Why?\n") == {})

pq_parts = qawkit.guide_part_questions(GUIDE)
check("the guide's Step 8 table has a question for each of the six parts",
      all(pq_parts.get(part, "").endswith("?") or "?" in pq_parts.get(part, "") for part in qawkit.SIX_PARTS))
check("a guide without a Step 8 gives no part questions", qawkit.guide_part_questions("# G\n") == {})

va = qawkit.guide_vague_answers(GUIDE)
check("the vague-answer table has eight rows keyed without quotes", len(va) == 8 and "it must be fast" in va)
check("every lint phrase exists in the guide's vague-answer table",
      all(phrase.lower() in va for _, phrase in qawkit.VAGUE_TERMS if phrase))

# --------------------------------------------------------------------------- #
# Reading the facilitation playbook
# --------------------------------------------------------------------------- #

fm = qawkit.playbook_formats(PLAYBOOK)
check("the playbook times exactly the formats the validator knows", tuple(fm) == validate.QAW_FORMATS)
for fmt, blocks in fm.items():
    names = [b for b, _ in blocks]
    check(f"format {fmt} runs Steps 1 to 9 in order",
          [n for n in range(1, 10) if any(b.startswith(f"Step {n} ") for b in names)] == list(range(1, 10))
          and sorted(names.index(next(b for b in names if b.startswith(f"Step {n} "))) for n in range(1, 10))
          == [names.index(next(b for b in names if b.startswith(f"Step {n} "))) for n in range(1, 10)])
check("half-day is four hours", sum(m for _, m in fm["half-day"]) == 240)
check("remote is three sessions", sum(1 for b, _ in fm["remote"] if b == qawkit.NEXT_DAY) == 2)
check("a block without minutes is an error", raises(
    qawkit.playbook_formats, "## Timeboxes\n\n### x\n\n| Block | Minutes |\n|---|---|\n| Step 1 — a | soon |\n"))
check("a playbook without timeboxes has no formats", qawkit.playbook_formats("# P\n") == {})

# --------------------------------------------------------------------------- #
# Small readers
# --------------------------------------------------------------------------- #

check("logical_lines joins wrapped list items",
      qawkit.logical_lines("- a b\n  c d\n- e\n  1. f\nplain\n") == ["- a b c d", "- e", "  1. f", "plain"])
ns = qawkit.not_significant_reasons("x\n- **Safety** is not significant here:\n  nothing can hurt anyone.\n"
                                    "- Security matters.\nCompatibility: not significant here.\n")
check("not-significant reasons are read whole and without markers",
      ns == {"Safety": "Safety is not significant here: nothing can hurt anyone.",
             "Compatibility": "Compatibility: not significant here."})
check("not_significant is the set of characteristics", qawkit.not_significant("Safety — not significant here") == {"Safety"})

# --------------------------------------------------------------------------- #
# prep: system types and characteristics set aside last time
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    d = make_drivers(root, {"PQA-1": "Performance efficiency"})
    out = root / "architecture" / "qaw" / "qaw-prep.md"
    text = qawkit.build_prep(d, "Acme", "2026-01-05", out, domains=["ai", "regulated", "ai"])
    check("prep adds the system-type questions in the order given, once each",
          text.count("### AI and machine-learning components") == 1
          and text.index("### AI and machine") < text.index("### Regulated data"))
    check("prep numbers the system-type questions", "1. Which decisions does the model make" in text)
    check("an unknown system type is an error naming the valid keys",
          raises(qawkit.build_prep, d, "Acme", "2026-01-05", out, domains=["blockchain"]))
    try:
        qawkit.build_prep(d, "Acme", "2026-01-05", out, domains=["blockchain"])
    except qawkit.KitError as e:
        check("the unknown-type error lists the keys", "ai" in str(e) and "regulated" in str(e))
    check("no --domain adds no system-type section",
          "Questions for this kind of system" not in qawkit.build_prep(d, "Acme", "2026-01-05", out))
    prev = write(root, "architecture/qaw/qaw-report-2025.md",
                 "# R\n\n- **Safety** is not significant here: no hardware.\n- **Compatibility** is\n"
                 "  not significant here: no partners.\n\n## Parked questions\n\nNone.\n")
    text = qawkit.build_prep(d, "Acme", "2026-01-05", out, prev)
    check("characteristics set aside last time are not asked from scratch",
          "### Safety" not in text and "### Compatibility" not in text and "### Security" in text)
    check("they are listed with the recorded reason to re-check",
          "## Characteristics set aside last time" in text
          and "| Compatibility | Compatibility is not significant here: no partners. |" in text)
    check("the gap count says what was set aside", "and were not set aside at the last workshop" in text)
    out.write_text(text, encoding="utf-8")
    check("a prep sheet with set-aside characteristics passes the validator", validate.validate_file(out) == [])
    every = "\n".join(f"- {c} is not significant here." for c in qawkit.ISO_CHARACTERISTICS)
    prev2 = write(root, "architecture/qaw/qaw-report-2024.md", "# R\n\n" + every + "\n")
    text = qawkit.build_prep(d, "Acme", "2026-01-05", out, prev2)
    check("when every gap was set aside, prep says so",
          "Every characteristic without a scenario was set aside" in text)

# --------------------------------------------------------------------------- #
# agenda
# --------------------------------------------------------------------------- #

a1 = qawkit.build_agenda("one-day", "Acme", "2026-11-10")
check("agenda starts at 09:00 by default", "| 09:00–09:20 | Step 1 — QAW presentation and introductions | 20 |" in a1)
check("agenda one-day ends at 16:45", "| 16:30–16:45 | Wrap-up — parked questions and next steps | 15 |" in a1)
check("agenda names the weekday", "## Day 1 — 2026-11-10 (Tuesday)" in a1)
check("agenda splits workshop time from breaks", "6 h 20 min of workshop time and 1 h 25 min of breaks" in a1)
check("agenda is deterministic", a1 == qawkit.build_agenda("one-day", "Acme", "2026-11-10"))
a2 = qawkit.build_agenda("two-day", "Acme", "2026-11-13", "08:30")
check("a two-day workshop starting on Friday continues on Monday",
      "## Day 1 — 2026-11-13 (Friday)" in a2 and "## Day 2 — 2026-11-16 (Monday)" in a2)
check("each day restarts at the start time", a2.count("| 08:30–") == 2)
check("two days are counted", "- **Length**: 2 days," in a2)
a3 = qawkit.build_agenda("remote", "Acme", "2026-11-10", "14:00")
check("remote agendas are in sessions", "## Session 3 — 2026-11-12 (Thursday)" in a3 and "3 sessions" in a3)
a4 = qawkit.build_agenda("half-day", "Acme", "2026-11-10", "13:00")
check("a half-day from 13:00 ends at 17:00", "–17:00 | Wrap-up" in a4)
check("an unknown format is an error", raises(qawkit.build_agenda, "weekend", "Acme", "2026-11-10"))
check("a malformed start time is an error", raises(qawkit.build_agenda, "one-day", "Acme", "2026-11-10", "9am"))
check("25:00 is not a time", raises(qawkit.build_agenda, "one-day", "Acme", "2026-11-10", "25:00"))
check("a malformed date is an error", raises(qawkit.build_agenda, "one-day", "Acme", "10/11/2026"))
check("an impossible date is an error", raises(qawkit.build_agenda, "one-day", "Acme", "2026-02-30"))
check("a day that runs past midnight is an error", raises(qawkit.build_agenda, "one-day", "Acme", "2026-11-10", "20:00"))
custom = ("## Timeboxes\n\n### tiny\n\n| Block | Minutes |\n|---|---:|\n| Step 1 — a | 5 |\n"
          "| Next day | — |\n| Next day | — |\n| Step 2 — b | 70 |\n| Break | 10 |\n")
a5 = qawkit.build_agenda("tiny", "Acme", "2026-11-10", "09:00", playbook_text=custom)
check("an empty day between two Next day rows is dropped, and dates still advance",
      "## Day 1 — 2026-11-10" in a5 and "## Day 2 — 2026-11-12" in a5 and "## Day 3" not in a5)
check("durations under an hour read in minutes", "1 h 15 min of workshop time and 10 min of breaks" in a5)
check("next_working_day skips the weekend",
      qawkit.next_working_day(qawkit.parse_date("2026-11-14")).isoformat() == "2026-11-16")
check("clock formats minutes", qawkit.clock(9 * 60 + 5) == "09:05")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "qaw-agenda.md"
    out.write_text(a2, encoding="utf-8")
    check("a generated agenda passes the validator", validate.validate_file(out) == [])

# --------------------------------------------------------------------------- #
# tally
# --------------------------------------------------------------------------- #

check("ranking puts most votes first and marks ties",
      qawkit.ranking([("CS-1", 1), ("CS-2", 3), ("CS-3", 1), ("CS-4", 0)]) == "CS-2 (3) > CS-1 (1) = CS-3 (1) > CS-4 (0)")
check("ranking of one scenario has no separator", qawkit.ranking([("CS-1", 2)]) == "CS-1 (2)")

SHEET = """# QAW vote sheet — Acme

- **Workshop report**: [qaw-report.md](qaw-report.md)
- **Votes per participant**: 2

| Scenario | ST-1 | ST-2 | ST-3 | Total |
|----------|:---:|:---:|:---:|:-----:|
| CS-1 — **Fast** dashboard | 1 |  | 2 | |
| CS-2 — Zone loss | 1 | 1 |  | |
| CS-3 — Audit log |  | 1 |  | 9 |
| CS-4 — Import |  |  |  | |
| CS-5 — Onboarding |  |  |  | |
"""
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    sheet = write(root, "qaw/qaw-vote-sheet.md", SHEET)
    out = root / "qaw" / "qaw-tally.md"
    t = qawkit.build_tally(sheet, out)
    check("tally reads blank cells as no votes and adds each row",
          "| CS-1 | 1 | 0 | 2 | 3 |" in t and "| CS-4 | 0 | 0 | 0 | 0 |" in t)
    check("tally ignores a hand-written total", "| CS-3 | 0 | 1 | 0 | 1 |" in t)
    check("tally ranks with ties in sheet order",
          "**Ranked**: CS-1 (3) > CS-2 (2) > CS-3 (1) > CS-4 (0) = CS-5 (0)." in t)
    check("tally states the budget line for Step 7",
          "**Vote budget** = ceil(0.30 × 5) = **2** votes per stakeholder (3 stakeholders → 6 votes)." in t)
    check("tally reports unspent votes", "- ST-3 cast 2 of 2 votes." not in t and "- ST-2 cast 2 of 2" not in t
          and "## Unspent votes" not in t)
    check("tally counts votes cast", "- **Votes cast**: 6 of 6" in t)
    out.write_text(t, encoding="utf-8")
    check("a generated tally passes the validator", validate.validate_file(out) == [])
    block = t.split("## Step 7 of the report\n\n", 1)[1]
    fake = ("# Quality Attribute Workshop — Acme\n\n## Step 6 — Scenario consolidation\n\n| Consolidated ID | Merged from | Scenario |\n"
            "|---|---|---|\n" + "".join(f"| CS-{i} | S-{i} | s |\n" for i in range(1, 6)) +
            "\n## Step 7 — Scenario prioritisation\n\n" + block + "\n## Step 8 — Scenario refinement\n")
    check("the Step 7 block tally writes passes the validator's vote checks", validate._qaw_vote_errors(fake) == [])
    under = write(root, "u/qaw-vote-sheet.md", SHEET.replace("| CS-1 — **Fast** dashboard | 1 |  | 2 |",
                                                            "| CS-1 — **Fast** dashboard | 1 |  | 1 |"))
    tu = qawkit.build_tally(under, root / "u" / "t.md")
    check("tally lists who left votes unspent", "## Unspent votes" in tu and "- ST-3 cast 1 of 2 votes." in tu)
    over = write(root, "o/qaw-vote-sheet.md", SHEET.replace("| CS-4 — Import |  |  |  |", "| CS-4 — Import | 1 |  |  |"))
    check("a participant over budget is an error", raises(qawkit.build_tally, over, out))
    bad = write(root, "b/qaw-vote-sheet.md", SHEET.replace("| CS-4 — Import |  |", "| CS-4 — Import | x |"))
    check("a non-number vote is an error", raises(qawkit.build_tally, bad, out))
    wrong = write(root, "w/qaw-vote-sheet.md", SHEET.replace("participant**: 2", "participant**: 3"))
    check("a stated budget that is not 30 % of the scenarios is an error", raises(qawkit.build_tally, wrong, out))
    words = write(root, "v/qaw-vote-sheet.md", SHEET.replace("participant**: 2", "participant**: two"))
    check("a stated budget in words is an error", raises(qawkit.build_tally, words, out))
    nobudget = write(root, "n/qaw-vote-sheet.md", SHEET.replace("- **Votes per participant**: 2\n", ""))
    check("without a stated budget the tally computes it", "**Votes per participant**: 2" in qawkit.build_tally(nobudget, out))
    notable = write(root, "x/qaw-vote-sheet.md", "# QAW vote sheet — Acme\n\nno table\n")
    check("a sheet with no vote table is an error", raises(qawkit.build_tally, notable, out))
    norows = write(root, "y/qaw-vote-sheet.md", "| Scenario | ST-1 | Total |\n|---|---|---|\n| total | 1 | |\n")
    check("a sheet with no scenario rows is an error", raises(qawkit.build_tally, norows, out))
    check("a missing sheet is an error", raises(qawkit.build_tally, root / "none.md", out))
    piped = write(root, "p/qaw-vote-sheet.md", SHEET.replace("CS-2 — Zone loss", "CS-2 — p95 \\| p99 latency"))
    check("an escaped pipe in a scenario does not shift the vote columns",
          "| CS-2 | 1 | 1 | 0 | 2 |" in qawkit.build_tally(piped, root / "p" / "t.md"))
    check("a table cell keeps an escaped pipe as one cell, unescaped",
          qawkit.table_cells("| A | B |\n|---|---|\n| x \\| y | z |\n", "A")[1] == [["x | y", "z"]])
    check("a cell written by the kit reads back as it was",
          qawkit._row("| " + qawkit._cell("a | b") + " | c |") == ["a | b", "c"])
    check("tally command exits 0", quiet_main(["tally", str(sheet), "--out", str(root / "t2.md")]) == 0)
    check("tally command over budget exits 2", quiet_main(["tally", str(over), "--out", str(root / "t3.md")]) == 2
          and not (root / "t3.md").exists())

# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

TEMPLATE = (ROOT / "templates" / "qaw-report.md").read_text(encoding="utf-8")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    tpl = write(root, "qaw/qaw-report.md", TEMPLATE)
    prog = qawkit.report_progress(TEMPLATE)
    check("status sees twelve stages", len(prog) == 12)
    check("a fresh template has every stage not started",
          all(state == "not started" for _, state, _ in prog))
    st_text = qawkit.build_status(tpl)
    check("status of a fresh template names Step 0 as next", "- **Next step**: Step 0 — Starting point" in st_text)
    check("status of a fresh template reports no gaps", "None found in the steps recorded so far." in st_text)
    rep = write(root, "q2/qaw-report.md", REPORT)
    prog2 = dict((s, (state, d)) for s, state, d in qawkit.report_progress(REPORT))
    check("a section that is absent is missing", prog2["Step 2 — Business drivers"][0] == "missing")
    check("an entry mode without inputs is not started", prog2["Step 0 — Starting point"][0] == "not started")
    check("status counts scenario types", prog2["Step 5 — Scenario brainstorming"][1]
          == "3 raw scenarios: 1 use-case, 1 growth, 1 exploratory")
    check("a ranking without a budget is not started", prog2["Step 7 — Prioritisation"][0] == "not started")
    check("status counts leaves and stars", prog2["Step 9 — Utility tree"][1] == "2 leaves, 1 ★")
    check("status counts parked questions", prog2["Parked questions"][1] == "2 questions, 1 open")
    check("status counts hand-off mappings", prog2["Hand-off to the drivers register"][1] == "3 mappings")
    s2 = qawkit.build_status(rep, "2026-03-01")
    check("status names the first unfinished stage as next", "- **Next step**: Step 0 — Starting point" in s2)
    check("status flags an overdue parked question", "PQ-1 is open (owner ST-2, due 2026-02-01, overdue since 2026-02-01)" in s2)
    check("an answered parked question is not a gap", "PQ-2" not in s2)
    check("without a date nothing is overdue", "overdue" not in qawkit.build_status(rep))
    typo = write(root, "q3/qaw-report.md", REPORT.replace("2026-02-01", "2026-02-31"))
    check("a due date that is not a calendar date is reported, not a crash",
          "due 2026-02-31, due date is not a calendar date" in qawkit.build_status(typo, "2026-03-01"))
    gapped = REPORT + ("\n## Step 4 — Architectural drivers\n\n| ID | Architectural driver | Kind | Supports |\n"
                       "|---|---|---|---|\n| AD-1 | a | QA | BG-1 |\n| AD-2 | b | QA | BG-1 |\n| AD-3 | c | QA | BG-1 |\n")
    gaps = "\n".join(qawkit.report_gaps(gapped))
    check("status lists drivers with no scenario", "Drivers with no brainstormed scenario: AD-3." in gaps)
    check("status lists characteristics with no leaf", "Compatibility" in gaps and "Reliability" not in gaps)
    one_type = REPORT.replace("| growth |", "| use-case |").replace("| exploratory |", "| use-case |")
    check("status lists scenario types never used",
          "Scenario types with no brainstormed scenario: growth, exploratory." in "\n".join(qawkit.report_gaps(one_type)))
    unmapped = REPORT.replace("| CS-2 | AQA-1 | |\n", "")
    check("status lists consolidated scenarios missing from the hand-off",
          "missing from the hand-off table: CS-2." in "\n".join(qawkit.report_gaps(unmapped)))
    check("a characteristic recorded as not significant is not a gap",
          "Safety" not in "\n".join(qawkit.report_gaps(REPORT + "\nSafety is not significant here.\n")))
    check("status command prints to stdout and exits 0", quiet_main(["status", str(rep)]) == 0)
    check("status command with a bad date exits 2", quiet_main(["status", str(rep), "--date", "soon"]) == 2)
    check("status command can write a file", quiet_main(["status", str(rep), "--out", str(root / "s.md")]) == 0
          and (root / "s.md").is_file())
    (root / "s.md").write_text(s2, encoding="utf-8")
    check("a generated status passes the validator", validate.validate_file(root / "s.md") == [])

# --------------------------------------------------------------------------- #
# lint
# --------------------------------------------------------------------------- #

SMELLY = """# Quality Attribute Workshop — Acme

## Step 5 — Scenario brainstorming

| ID | Scenario | Type | Contributor | Driver(s) |
|----|----------|------|-------------|-----------|
| S-1 | a | use-case | Ana | AD-1 |
| S-2 | b | wishlist | Bo | AD-1 |

## Step 8 — Scenario refinement

### CS-1 — Dashboard

| Part | Value |
|------|-------|
| Source of stimulus | The user |
| Stimulus | Opens the dashboard |
| Artifact | Web app |
| Environment | |
| Response | Page loads quickly |
| Response measure | Fast enough for PQA-1 |

- **Business goals**: none yet

### CS-2 — Zone loss

| Part | Value |
|------|-------|
| Source of stimulus | Cloud provider |
| Stimulus | A zone fails |
| Artifact | Whole system |
| Environment | Peak load |
| Response | Traffic moves to the other zone |
| Response measure | Recovery < 60 s; reasonable data loss |

- **Business goals**: BG-1

### CS-3 — Clean

| Part | Value |
|------|-------|
| Source of stimulus | Attacker with a stolen session |
| Stimulus | Requests another user's data |
| Artifact | API |
| Environment | Normal operation |
| Response | Request is refused and logged |
| Response measure | 0 successful reads; alert < 1 min |

- **Business goals**: BG-2

## Step 9 — Quality attribute utility tree

| Quality attribute | Refinement | Leaf scenario | Priority (V, R) | Status |
|---|---|---|---|---|
| Performance efficiency | Time | PQA-1 (CS-1) — dashboard is fast | (H, M) | open |
| Reliability | Availability | AQA-1 (CS-2) — recover < 60 s | (H, H) ★ | open |
| Security | Confidentiality | SQA-1 (CS-3) — 0 reads | (H, H) ★ | open |
"""
findings = qawkit.lint_report(SMELLY, GUIDE)
by = {}
for where, problem, ask in findings:
    by.setdefault(where, []).append((problem, ask))
check("lint flags a raw scenario with an unknown type", any("wishlist" in p for p, _ in by.get("S-2", [])))
check("lint flags an empty part with its guide question",
      any(p == "environment is empty" and ask.startswith("What state is the system in") for p, ask in by["CS-1"]))
check("lint flags a generic source", any("'the user' names no role" in p for p, _ in by["CS-1"]))
check("an ID's digits do not count as a measure", ("response measure has no number", pq_parts["Response measure"]) in by["CS-1"])
check("lint flags a vague word in the measure with the guide's follow-up",
      any("vague word 'Fast'" in p and ask == va["it must be fast"] for p, ask in by["CS-1"]))
check("lint flags a vague word in the response", any(p == "response uses the vague word 'quickly'" for p, _ in by["CS-1"]))
check("lint flags a missing business goal", any("cites no business goal" in p for p, _ in by["CS-1"]))
check("a generic vague word asks for a number",
      ("response measure uses the vague word 'reasonable'", pq_parts["Response measure"]) in by["CS-2"])
check("a clean scenario has no findings", "CS-3" not in by)
check("lint flags a leaf with no measure", any("leaf has no measure" in p for p, _ in by.get("PQA-1", [])))
check("lint flags characteristics neither covered nor set aside",
      "Compatibility" in by and "Security" not in by and "Reliability" not in by)
check("a characteristic set aside is not flagged",
      "Safety" not in {w for w, _, _ in qawkit.lint_report(SMELLY + "\nSafety is not significant here.\n", GUIDE)})
check("a report with no utility tree has no coverage findings",
      not any(w in qawkit.ISO_CHARACTERISTICS for w, _, _ in qawkit.lint_report("# Q\n", GUIDE)))
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    smelly = write(root, "q/qaw-report.md", SMELLY)
    text, n = qawkit.build_lint(smelly)
    check("lint output counts findings", f"- **Findings**: {n}" in text and n == len(findings))
    check("lint command exits 1 with findings", quiet_main(["lint", str(smelly)]) == 1)
    clean = write(root, "c/qaw-report.md", "# Quality Attribute Workshop — Clean\n")
    check("lint command exits 0 with no findings", quiet_main(["lint", str(clean)]) == 0)
    check("a clean lint says so", "No findings" in qawkit.build_lint(clean)[0])
    check("lint command on a missing report exits 2", quiet_main(["lint", str(root / "none.md")]) == 2)
    check("lint can write its findings to a file and still exits 1",
          quiet_main(["lint", str(smelly), "--out", str(root / "lint.md")]) == 1 and (root / "lint.md").is_file())
    check("a generated lint report passes the validator", validate.validate_file(root / "lint.md") == [])

# --------------------------------------------------------------------------- #
# summary and prep CLI details
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    rep = write(root, "qaw/qaw-report.md", REPORT.replace("- **Status**: complete", "- **Format**: one-day\n- **Status**: complete"))
    check("summary carries the format when the report states it",
          "- **Format**: one-day" in qawkit.build_summary(rep, root / "qaw" / "s.md"))
    check("summary has no format line when the report has none",
          "**Format**" not in qawkit.build_summary(write(root, "q2/qaw-report.md", REPORT), root / "q2" / "s.md"))
    d = make_drivers(root)
    check("prep accepts comma-separated and repeated --domain",
          quiet_main(["prep", "--drivers", str(d), "--system", "A", "--date", "2026-01-01", "--domain", "ai,saas",
                      "--domain", "api", "--out", str(root / "p.md")]) == 0
          and all(h in (root / "p.md").read_text() for h in ("### Multi-tenant SaaS", "### Public APIs")))
    check("prep with an unknown --domain exits 2",
          quiet_main(["prep", "--drivers", str(d), "--system", "A", "--date", "2026-01-01", "--domain", "x",
                      "--out", str(root / "p2.md")]) == 2)
    check("agenda command exits 0", quiet_main(["agenda", "--format", "half-day", "--date", "2026-01-05",
                                                "--system", "A", "--out", str(root / "a.md")]) == 0)
    check("agenda command with an unknown format exits 2",
          quiet_main(["agenda", "--format", "x", "--date", "2026-01-05", "--system", "A", "--out", str(root / "a2.md")]) == 2)

# --------------------------------------------------------------------------- #
# Golden files: the kit committed in each worked example equals a fresh regeneration
# --------------------------------------------------------------------------- #

def blank_votes(sheet: str) -> str:
    """The filled-in vote sheet with its vote cells emptied — what `ballot` wrote."""
    out = []
    for ln in sheet.splitlines():
        cells = ln.split("|")
        if ln.startswith("| CS-") and len(cells) > 3:
            ln = "|".join(cells[:2] + ["  " for _ in cells[2:-2]] + [" ", ""])
        out.append(ln)
    return "\n".join(out) + "\n"


for ex in sorted((ROOT / "examples").glob("personal-finance-tracker-*")):
    q = ex / "qaw"
    rep = q / "qaw-report.md"
    want = {
        "qaw-prep.md": qawkit.build_prep(ex / "drivers", "Personal Finance Tracker", "2026-11-02",
                                         q / "qaw-prep.md", rep, domains=["regulated"]),
        "qaw-agenda.md": qawkit.build_agenda("remote", "Personal Finance Tracker", "2026-11-10", "10:00"),
        "qaw-tally.md": qawkit.build_tally(q / "qaw-vote-sheet.md", q / "qaw-tally.md"),
        "qaw-summary.md": qawkit.build_summary(rep, q / "qaw-summary.md"),
    }
    for name, text in want.items():
        committed = q / name
        check(f"{ex.name}/qaw/{name} matches a fresh regeneration "
              f"(re-run scripts/qawkit.py — see the example README)",
              committed.is_file() and committed.read_text(encoding="utf-8") == text)
    sheet = (q / "qaw-vote-sheet.md").read_text(encoding="utf-8")
    check(f"{ex.name}/qaw/qaw-vote-sheet.md is the ballot with votes filled in",
          blank_votes(sheet) == qawkit.build_ballot(rep, q / "qaw-vote-sheet.md"))
    block = want["qaw-tally.md"].split("## Step 7 of the report\n\n", 1)[1].split("\n## ", 1)[0].strip()
    check(f"{ex.name}: Step 7 of the report is the tally's block", block in rep.read_text(encoding="utf-8"))
    check(f"{ex.name}: the report lints clean", qawkit.lint_report(rep.read_text(encoding="utf-8"), GUIDE) == [])
    check(f"{ex.name}: status finds every stage done",
          all(state == "done" for _, state, _ in qawkit.report_progress(rep.read_text(encoding="utf-8"))))

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
