#!/usr/bin/env python3
"""Unit tests for scripts/qawkit.py — the QAW kit generator (prep sheet, vote sheet, summary).
Covers every reader and builder, the CLI's exit codes, and golden files: the kit committed under
each worked example must equal a fresh regeneration. Standard library only; exit 0 on success."""
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
          "2 participants produced 3 raw scenarios, consolidated to 2; 1 were refined" in s)
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
# Golden files: the kit committed in each worked example equals a fresh regeneration
# --------------------------------------------------------------------------- #

for ex in sorted((ROOT / "examples").glob("personal-finance-tracker-*")):
    q = ex / "qaw"
    rep = q / "qaw-report.md"
    want = {
        "qaw-prep.md": qawkit.build_prep(ex / "drivers", "Personal Finance Tracker", "2026-11-02",
                                         q / "qaw-prep.md", rep),
        "qaw-vote-sheet.md": qawkit.build_ballot(rep, q / "qaw-vote-sheet.md"),
        "qaw-summary.md": qawkit.build_summary(rep, q / "qaw-summary.md"),
    }
    for name, text in want.items():
        committed = q / name
        check(f"{ex.name}/qaw/{name} matches a fresh regeneration "
              f"(re-run scripts/qawkit.py — see the example README)",
              committed.is_file() and committed.read_text(encoding="utf-8") == text)

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
