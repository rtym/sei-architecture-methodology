#!/usr/bin/env python3
"""Set a driver's status everywhere the drivers register records it. Standard library only; the
same inputs always give the same files.

  driverstatus.py DRIVERS_DIR ID STATUS [--detail TEXT]

The register keeps a driver's status in up to four places: the driver file (`- **Status**:`), its
kind's index (`<kind>/README.md`), the traceability matrix in the drivers `README.md` (use cases,
scenarios and constraints), and, for a quality attribute scenario, the utility tree
(`quality-attributes/utility-tree.md`). Changing one by
hand and missing another is how a register drifts, so ADD and ATAM write statuses back through
this script. `--detail` adds a note to the driver file only, e.g. `--detail "ATAM R-1, R-2"` gives
`at risk (ATAM R-1, R-2)`; the index tables carry the bare status. Nothing is written unless every
place that should list the driver does.

Exit codes: 0 written (or already current), 2 unknown status, missing driver, or a table that
does not list the driver.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

STATUSES = ("open", "in design", "partially", "addressed", "at risk", "retired")
KINDS = (("BG", "business-goals"), ("UC", "use-cases"), ("CON", "constraints"),
         ("AC", "concerns"), ("QA", "quality-attributes"))
STATUS_LINE = re.compile(r"^(\s*-\s*\*\*Status\*\*\s*:\s*)(.*?)\s*$", re.MULTILINE)


class StatusError(Exception):
    """A request the register cannot satisfy; the message says what is missing."""


def kind_dir(driver_id: str) -> str:
    if re.fullmatch(r"[A-Z]{1,4}QA-\d+", driver_id):
        return "quality-attributes"
    prefix = driver_id.split("-", 1)[0]
    for p, d in KINDS:
        if p == prefix and re.fullmatch(rf"{p}-\d+", driver_id):
            return d
    raise StatusError(f"{driver_id!r} is not a driver ID (BG-, UC-, CON-, AC- or <ATTR>QA-<n>)")


def set_table_status(text: str, driver_id: str, status: str, id_column: int = 0) -> tuple[str, bool]:
    """Set the Status column of the row whose ID cell (`id_column`) names `driver_id`, in every
    table with a Status column. Returns (text, found)."""
    lines = text.split("\n")
    found = False
    i = 0
    while i < len(lines):
        ln = lines[i]
        sep = lines[i + 1] if i + 1 < len(lines) else ""
        if ln.lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", sep):
            head = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
            col = head.index("status") if "status" in head else -1
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = lines[j].strip().strip("|").split("|")
                if col >= 0 and len(cells) > max(col, id_column) and \
                        re.search(rf"(?<![\w-]){re.escape(driver_id)}(?![\w-])", cells[id_column]):
                    cells[col] = f" {status} "
                    lines[j] = "|" + "|".join(cells) + "|"
                    found = True
                j += 1
            i = j
        else:
            i += 1
    return "\n".join(lines), found


def plan(drivers: Path, driver_id: str, status: str, detail: str = "") -> dict[Path, str]:
    """Every file that changes → its new text. Raises StatusError before anything is written."""
    if status not in STATUSES:
        raise StatusError(f"status {status!r} is not one of: {', '.join(STATUSES)}")
    if not drivers.is_dir():
        raise StatusError(f"drivers directory not found: {drivers}")
    sub = kind_dir(driver_id)
    driver_file = drivers / sub / f"{driver_id}.md"
    if not driver_file.is_file():
        raise StatusError(f"{driver_file} does not exist")
    out: dict[Path, str] = {}
    text = driver_file.read_text(encoding="utf-8")
    value = f"{status} ({detail})" if detail else status
    if not STATUS_LINE.search(text):
        raise StatusError(f"{driver_file.name} has no '- **Status**:' line")
    out[driver_file] = STATUS_LINE.sub(lambda m: m.group(1) + value, text, count=1)
    # (file, column naming the ID, must the file list this driver?) — the README matrix traces use
    # cases, scenarios and constraints; a goal or concern is updated there only if it is listed.
    traced = sub in ("use-cases", "quality-attributes", "constraints")
    tables = [(drivers / sub / "README.md", 0, True), (drivers / "README.md", 0, traced)]
    if sub == "quality-attributes" and (drivers / sub / "utility-tree.md").is_file():
        tables.append((drivers / sub / "utility-tree.md", 2, True))   # the leaf column names the ID
    for path, col, required in tables:
        if not path.is_file():
            raise StatusError(f"{path} does not exist")
        new, found = set_table_status(path.read_text(encoding="utf-8"), driver_id, status, col)
        if not found and not required:
            continue
        if not found:
            raise StatusError(f"{path.relative_to(drivers.parent)} has no table row with a Status "
                              f"column for {driver_id}")
        out[path] = new
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="driverstatus.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("drivers", type=Path)
    ap.add_argument("id")
    ap.add_argument("status")
    ap.add_argument("--detail", default="")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        changes = plan(a.drivers, a.id, a.status, a.detail)
    except StatusError as e:
        print(f"driverstatus: {e}", file=sys.stderr)
        return 2
    changed = 0
    for path, text in changes.items():
        if path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"updated {path}")
    if not changed:
        print(f"{a.id} is already {a.status} everywhere")
    return 0


if __name__ == "__main__":
    sys.exit(main())
