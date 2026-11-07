#!/usr/bin/env python3
"""Unit tests for scripts/driverstatus.py — setting a driver's status in every place the drivers
register keeps it (driver file, kind index, README matrix, utility tree). Works on copies of the
worked example's register; every result must also pass validate.py's cross-file status check.
Standard library only; exit 0 on success."""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import driverstatus  # noqa: E402
import validate  # noqa: E402

PASSES = 0
FAILS = 0
EXAMPLE = ROOT / "examples" / "personal-finance-tracker-mermaid" / "drivers"


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
    except driverstatus.StatusError:
        return True
    return False


def register(td: str) -> Path:
    """A copy of the example's drivers register (with the package index it links up to)."""
    d = Path(td) / "architecture" / "drivers"
    shutil.copytree(EXAMPLE, d)
    (d.parent / "README.md").write_text("# Architecture\n", encoding="utf-8")
    return d


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = driverstatus.main(argv)
    return rc, out.getvalue(), err.getvalue()


def status_errors(d: Path) -> list[str]:
    return validate._driver_status_errors(d)


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #

for did, kind in (("BG-1", "business-goals"), ("UC-12", "use-cases"), ("CON-3", "constraints"),
                  ("AC-2", "concerns"), ("SQA-1", "quality-attributes"), ("PERFQA-9", "quality-attributes")):
    check(f"{did} lives in {kind}", driverstatus.kind_dir(did) == kind)
for bad in ("QAS-1", "BG1", "XYZ-1", "UC-", "sqa-1", "TOOLONGQA-1"):
    check(f"{bad!r} is not a driver ID", raises(driverstatus.kind_dir, bad))

TABLE = ("| ID | Name | Status |\n|----|------|:------:|\n| [UC-1](UC-1.md) | a | open |\n"
         "| [UC-10](UC-10.md) | b | open |\n\nText UC-1.\n")
text, found = driverstatus.set_table_status(TABLE, "UC-1", "addressed")
check("only the row for the exact ID changes", found and "| [UC-1](UC-1.md) | a | addressed |" in text
      and "| [UC-10](UC-10.md) | b | open |" in text)
check("text outside tables is untouched", text.endswith("Text UC-1.\n"))
check("a table without the ID reports not found", driverstatus.set_table_status(TABLE, "UC-2", "open")[1] is False)
check("a table without a Status column is not changed",
      driverstatus.set_table_status("| ID | Name |\n|---|---|\n| UC-1 | a |\n", "UC-1", "open")
      == ("| ID | Name |\n|---|---|\n| UC-1 | a |\n", False))
leaf = ("| QA | Ref | Leaf | (V, R) | Status |\n|---|---|---|---|---|\n| Security | C | [SQA-1](SQA-1.md) — x | (H, H) | open |\n")
check("the ID can be looked up in another column (utility-tree leaves)",
      "| at risk |" in driverstatus.set_table_status(leaf, "SQA-1", "at risk", id_column=2)[0])
check("an ID in another column is ignored when looking in the first",
      driverstatus.set_table_status(leaf, "SQA-1", "at risk")[1] is False)

# --------------------------------------------------------------------------- #
# Against a copy of the worked example's register
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    d = register(td)
    check("the example register starts consistent", status_errors(d) == [])
    changes = driverstatus.plan(d, "PQA-1", "addressed", "ADD iteration 2 load test")
    check("a scenario's status lands in four files",
          sorted(p.relative_to(d).as_posix() for p in changes) ==
          ["README.md", "quality-attributes/PQA-1.md", "quality-attributes/README.md",
           "quality-attributes/utility-tree.md"])
    check("plan writes nothing", "addressed" not in (d / "quality-attributes/PQA-1.md").read_text())
    rc, out, _ = run([str(d), "PQA-1", "addressed", "--detail", "ADD iteration 2 load test"])
    check("the CLI writes and exits 0", rc == 0 and out.count("updated") == 4)
    check("the driver file carries the detail",
          "- **Status**: addressed (ADD iteration 2 load test)" in (d / "quality-attributes/PQA-1.md").read_text())
    check("the index tables carry the bare status",
          "| addressed |" in (d / "quality-attributes/README.md").read_text()
          and "(ADD iteration 2" not in (d / "quality-attributes/README.md").read_text())
    check("the register stays consistent after the change", status_errors(d) == [])
    check("the whole drivers directory still validates", validate.check_drivers_dir(d) == [])
    rc, out, _ = run([str(d), "PQA-1", "addressed", "--detail", "ADD iteration 2 load test"])
    check("running it again changes nothing", rc == 0 and "already addressed everywhere" in out)

    rc, out, _ = run([str(d), "CON-2", "partially"])
    check("a constraint lands in its file, its index and the matrix (no utility tree)",
          rc == 0 and out.count("updated") == 3 and status_errors(d) == [])
    rc, _, _ = run([str(d), "UC-2", "in design"])
    check("a use case's status is set", rc == 0 and "- **Status**: in design" in (d / "use-cases/UC-2.md").read_text())
    rc, out, _ = run([str(d), "BG-3", "retired"])
    check("a business goal lands in its file and its index; the matrix does not list goals",
          rc == 0 and out.count("updated") == 2
          and "- **Status**: retired" in (d / "business-goals/BG-3.md").read_text() and status_errors(d) == [])
    rc, out, _ = run([str(d), "AC-1", "addressed"])
    check("a concern is set in its file and its index", rc == 0 and out.count("updated") == 2)

    before = {p: p.read_text() for p in d.rglob("*.md")}
    rc, _, err = run([str(d), "UC-9", "open"])
    check("an unknown driver exits 2 and names the missing file", rc == 2 and "UC-9.md does not exist" in err)
    rc, _, err = run([str(d), "UC-1", "done"])
    check("an unknown status exits 2 and lists the valid ones", rc == 2 and "at risk" in err)
    rc, _, err = run([str(d), "QAS-1", "open"])
    check("a malformed ID exits 2", rc == 2 and "not a driver ID" in err)
    check("failed runs write nothing", all(p.read_text() == t for p, t in before.items()))

    matrix = d / "README.md"
    matrix.write_text(matrix.read_text().replace("| UQA-1 | [UQA-1](quality-attributes/UQA-1.md)", "| UXQA-1 | [UXQA-1](x.md)"))
    before = {p: p.read_text() for p in d.rglob("*.md")}
    rc, _, err = run([str(d), "UQA-1", "addressed"])
    check("a driver missing from the matrix stops the whole change", rc == 2 and "README.md has no table row" in err
          and all(p.read_text() == t for p, t in before.items()))

with tempfile.TemporaryDirectory() as td:
    d = register(td)
    (d / "use-cases" / "UC-1.md").write_text("# UC-1\n\nNo status here.\n")
    check("a driver file without a Status line is an error", raises(driverstatus.plan, d, "UC-1", "open"))
    (d / "constraints" / "README.md").unlink()
    check("a missing kind index is an error", raises(driverstatus.plan, d, "CON-1", "open"))
check("a missing drivers directory is an error", raises(driverstatus.plan, Path("/nonexistent"), "UC-1", "open"))
check("an unknown option exits 2", run(["--bogus"])[0] == 2)

# --------------------------------------------------------------------------- #
# The validator catches what the script prevents
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    d = register(td)
    qa = d / "quality-attributes" / "README.md"
    qa.write_text(qa.read_text().replace("| [scenario](diagrams/scenario-SQA-1.png) | at risk |",
                                         "| [scenario](diagrams/scenario-SQA-1.png) | in design |"))
    errs = status_errors(d)
    check("a kind index edited by hand is caught",
          errs == ["quality-attributes/README.md: SQA-1 status is 'in design' but SQA-1.md says 'at risk' "
                   "(set statuses with scripts/driverstatus.py)"])
    check("the drivers-directory check reports it", any("SQA-1 status" in e for e in validate.check_drivers_dir(d)))
    run([str(d), "SQA-1", "at risk", "--detail", "ATAM R-1, R-2"])
    check("driverstatus.py repairs it", status_errors(d) == [])
    tree = d / "quality-attributes" / "utility-tree.md"
    tree.write_text(tree.read_text().replace("(H, H) `★` | at risk |", "(H, H) `★` | open |", 1))
    check("a utility-tree leaf edited by hand is caught",
          any(e.startswith("quality-attributes/utility-tree.md: SQA-1 status is 'open'") for e in status_errors(d)))
    uc = d / "use-cases" / "UC-3.md"
    uc.write_text(uc.read_text().replace("- **Priority**: medium", "- **Priority**: high"))
    check("a priority that differs between file and index is caught",
          "use-cases/README.md: UC-3 priority is 'medium' but UC-3.md says 'high'" in status_errors(d))

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
