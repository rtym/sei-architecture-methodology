#!/usr/bin/env python3
"""Unit tests for scripts/appbundle.py — the Claude app edition, where every skill is
self-contained for claude.ai chat and Cowork. Builds the real plugin into a temp folder and checks
the claude.ai limits, that no skill reaches outside its own folder, that the bundled QAW scripts
run from inside the bundle and give the same output as the plugin's own, and that two builds are
byte-identical. Small fake plugins cover the failure paths. Standard library only; exit 0 on
success."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))
import appbundle  # noqa: E402
import qawkit  # noqa: E402

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
    except appbundle.BuildError:
        return True
    return False


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


SKILL_DIR_REF = re.compile(r"\$\{CLAUDE_SKILL_DIR\}(/[A-Za-z0-9_./-]*[A-Za-z0-9_-])?/?")
MANIFEST = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
SKILLS = [Path(s).name for s in MANIFEST["skills"]]

# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #

check("own skill files keep their place", appbundle.bundle_path("skills/atam/SKILL.md", "atam") == "SKILL.md")
check("the skill folder itself maps to the folder root", appbundle.bundle_path("skills/atam", "atam") == "")
check("another skill's files go under related/",
      appbundle.bundle_path("skills/sei-diagrams/scripts/render.sh", "atam") == "related/sei-diagrams/scripts/render.sh")
check("another skill's SKILL.md becomes GUIDE.md",
      appbundle.bundle_path("skills/sei-diagrams/SKILL.md", "atam") == "related/sei-diagrams/GUIDE.md")
check("plugin-level files keep their plugin path",
      appbundle.bundle_path("references/glossary.md", "atam") == "references/glossary.md")
check("rewrite points plugin paths into the skill folder",
      appbundle.rewrite("Read `${CLAUDE_PLUGIN_ROOT}/references/x.md` and "
                        "${CLAUDE_PLUGIN_ROOT}/skills/s/SKILL.md, then ${CLAUDE_PLUGIN_ROOT}/assets/c4/.", "s")
      == "Read `${CLAUDE_SKILL_DIR}/references/x.md` and ${CLAUDE_SKILL_DIR}/SKILL.md, then "
         "${CLAUDE_SKILL_DIR}/assets/c4/.")
check("rewrite leaves other text alone", appbundle.rewrite("no paths here ${CLAUDE_SESSION_ID}", "s")
      == "no paths here ${CLAUDE_SESSION_ID}")

fields, body = appbundle.front_matter("---\nname: x\ndescription: >-\n  one\n  two\nallowed-tools: [Read]\n"
                                      "user-invocable: false\n---\n# X\n")
check("front matter folds a >- description", fields["description"] == "one two")
check("front matter keeps scalar fields", fields["user-invocable"] == "false" and fields["name"] == "x")
check("front matter returns the body", body == "# X\n")
check("quoted scalars lose their quotes", appbundle.front_matter('---\nname: "x"\n---\n')[0]["name"] == "x")
check("a file without front matter is an error", raises(appbundle.front_matter, "# X\n"))

md = appbundle.skill_md("---\nname: s\ndescription: Does a thing.\nuser-invocable: false\nallowed-tools: [Read]\n"
                        "---\n\n# Title\n\nUse ${CLAUDE_PLUGIN_ROOT}/references/r.md.\n", "s", "> NOTE", "MIT")
check("SKILL.md keeps only fields claude.ai accepts",
      md.startswith('---\nname: s\ndescription: "Does a thing."\nlicense: MIT\n---\n'))
check("the app note follows the title", "# Title\n\n> NOTE\n\nUse ${CLAUDE_SKILL_DIR}/references/r.md." in md)
check("a name that differs from the folder is an error",
      raises(appbundle.skill_md, "---\nname: t\ndescription: d\n---\n# T\n", "s", "", ""))
check("an upper-case name is an error",
      raises(appbundle.skill_md, "---\nname: S\ndescription: d\n---\n# T\n", "S", "", ""))
check("a description over 1024 characters is an error",
      raises(appbundle.skill_md, f"---\nname: s\ndescription: {'x' * 1025}\n---\n# T\n", "s", "", ""))
check("an empty description is an error", raises(appbundle.skill_md, "---\nname: s\n---\n# T\n", "s", "", ""))

# --------------------------------------------------------------------------- #
# Failure paths on small fake plugins
# --------------------------------------------------------------------------- #


def fake_plugin(root: Path, skill_body: str, extra: dict[str, str] | None = None) -> Path:
    write(root, ".claude-plugin/plugin.json", json.dumps({"name": "p", "version": "0.0.1", "skills": ["./skills/s"]}))
    write(root, "skills/s/SKILL.md", f"---\nname: s\ndescription: d\n---\n# S\n\n{skill_body}\n")
    for rel, text in (extra or {}).items():
        write(root, rel, text)
    return root


with tempfile.TemporaryDirectory() as td:
    root = fake_plugin(Path(td) / "src", "See ${CLAUDE_PLUGIN_ROOT}/references/gone.md.")
    check("a skill that names a missing file is an error", raises(appbundle.build, Path(td) / "out", root))
with tempfile.TemporaryDirectory() as td:
    root = fake_plugin(Path(td) / "src", "Run ${CLAUDE_PLUGIN_ROOT}/scripts/a.py and ${CLAUDE_SKILL_DIR}/scripts/a.py.",
                       {"scripts/a.py": "print(1)\n", "skills/s/scripts/a.py": "print(2)\n"})
    check("two files that would land on the same path are an error", raises(appbundle.build, Path(td) / "out", root))
with tempfile.TemporaryDirectory() as td:
    root = fake_plugin(Path(td) / "src", "Read ${CLAUDE_PLUGIN_ROOT}/references/a.md.",
                       {"references/a.md": "Then ${CLAUDE_PLUGIN_ROOT}/templates/b.md\n", "templates/b.md": "B\n",
                        "references/unused.md": "U\n"})
    folder, archive, _ = appbundle.build(Path(td) / "out", root)
    check("files named by named files are copied too", (folder / "skills/s/templates/b.md").read_text() == "B\n")
    check("files nobody names are not copied", not (folder / "skills/s/references/unused.md").exists())
    check("copied files have their paths rewritten",
          (folder / "skills/s/references/a.md").read_text() == "Then ${CLAUDE_SKILL_DIR}/templates/b.md\n")
    write(Path(td), "out/sei-architecture-methodology-app/README.md", "changed\n")
    folder2, _, _ = appbundle.build(Path(td) / "out", root)
    check("a rebuild replaces an earlier build", (folder2 / "README.md").read_text() != "changed\n")
    write(Path(td), "other/sei-architecture-methodology-app/precious.txt", "keep\n")
    check("a folder that is not an earlier build is never deleted",
          raises(appbundle.build, Path(td) / "other", root)
          and (Path(td) / "other/sei-architecture-methodology-app/precious.txt").is_file())
    check("--no-zip writes no archive", appbundle.build(Path(td) / "nz", root, make_zip=False)[1] is None)
    saved = appbundle.MAX_FILES
    appbundle.MAX_FILES = 2
    try:
        check("an edition over claude.ai's file limit is an error", raises(appbundle.build, Path(td) / "big", root))
    finally:
        appbundle.MAX_FILES = saved

# --------------------------------------------------------------------------- #
# The real plugin's app edition
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    out = Path(td)
    folder, archive, warnings = appbundle.build(out / "a")
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    rels = [p.relative_to(folder).as_posix() for p in files]

    check("the app edition has one folder per skill",
          sorted(p.name for p in (folder / "skills").iterdir()) == sorted(SKILLS))
    check("the manifest is the only file in .claude-plugin",
          [p.name for p in (folder / ".claude-plugin").iterdir()] == ["plugin.json"])
    app_manifest = json.loads((folder / ".claude-plugin/plugin.json").read_text())
    check("the manifest carries the plugin's version under its own name",
          app_manifest["name"] == appbundle.APP_NAME and app_manifest["version"] == MANIFEST["version"])
    check("the manifest lists no component paths", "skills" not in app_manifest and "commands" not in app_manifest)
    check("there is no top-level bin/ (claude.ai refuses such plugins)", not (folder / "bin").exists())
    check("the slash commands are left out", not (folder / "commands").exists())
    check("LICENSE and NOTICE travel with it", (folder / "LICENSE").is_file() and (folder / "NOTICE").is_file())
    check("within claude.ai's file and size limits",
          len(files) <= appbundle.MAX_FILES and sum(p.stat().st_size for p in files) <= appbundle.MAX_BYTES)
    check("no node_modules or caches are shipped",
          not any(part in appbundle.SKIP_DIRS for r in rels for part in r.split("/")))
    check("no nested SKILL.md that could be mistaken for a skill",
          all(re.fullmatch(r"skills/[a-z0-9-]+/SKILL\.md", r) for r in rels if r.endswith("/SKILL.md") or r == "SKILL.md"))
    check("the only size warning is the long diagram skill",
          all("sei-diagrams" in w for w in warnings))

    leaks, unresolved = [], []
    for p in files:
        if p.suffix not in appbundle.TEXT_SUFFIXES:
            continue
        text = p.read_text(encoding="utf-8")
        if "${CLAUDE_PLUGIN_ROOT}" in text:
            leaks.append(p.relative_to(folder).as_posix())
        skill = p.relative_to(folder).parts[1] if p.relative_to(folder).parts[0] == "skills" else None
        for m in SKILL_DIR_REF.finditer(text):
            if skill and not (folder / "skills" / skill / (m.group(1) or "/").lstrip("/")).exists():
                unresolved.append(f"{p.relative_to(folder)} -> {m.group(0)}")
    check(f"no file still points at the plugin root ({leaks[:3]})", leaks == [])
    check(f"every ${{CLAUDE_SKILL_DIR}} path resolves inside its own skill ({unresolved[:3]})", unresolved == [])

    for skill in SKILLS:
        text = (folder / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        fields, _ = appbundle.front_matter(text)
        check(f"{skill}: front matter has only claude.ai fields",
              set(fields) <= {"name", "description", "license", "compatibility", "metadata", "allowed-tools"})
        check(f"{skill}: name matches the folder and the spec",
              fields["name"] == skill and appbundle.NAME_RE.match(skill) and len(skill) <= appbundle.MAX_NAME)
        check(f"{skill}: description fits", 0 < len(fields["description"]) <= appbundle.MAX_DESCRIPTION)
        check(f"{skill}: carries the app note with the command map",
              "Claude app edition" in text and "`/qaw` is the `quality-attribute-workshop` skill" in text)

    qaw = folder / "skills" / "quality-attribute-workshop"
    for need in ("references/qaw-question-guide.md", "references/qaw-facilitation-playbook.md",
                 "templates/qaw-report.md", "scripts/qawkit.py", "tests/validate.py", "scripts/mdreport.py"):
        check(f"the QAW skill carries {need}", (qaw / need).is_file())
    check("the QAW skill keeps its chat section", "## Running in the Claude app (chat)" in (qaw / "SKILL.md").read_text())

    # the bundled QAW kit and validator run from inside the bundle, from another working folder
    ex = ROOT / "examples" / "personal-finance-tracker-mermaid"
    work = out / "work"
    work.mkdir()

    def run(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, *args], cwd=work, capture_output=True, text=True)

    r = run(str(qaw / "scripts/qawkit.py"), "agenda", "--format", "remote", "--date", "2026-11-10",
            "--start", "10:00", "--system", "Personal Finance Tracker", "--out", "agenda.md")
    check("the bundled qawkit runs from the bundle", r.returncode == 0)
    check("the bundled qawkit reads the bundled playbook and gives the plugin's output",
          (work / "agenda.md").read_text() == qawkit.build_agenda("remote", "Personal Finance Tracker", "2026-11-10", "10:00"))
    r = run(str(qaw / "scripts/qawkit.py"), "lint", str(ex / "qaw" / "qaw-report.md"))
    check("the bundled lint reads the bundled guide and passes the example", r.returncode == 0)
    r = run(str(qaw / "scripts/qawkit.py"), "prep", "--drivers", str(ex / "drivers"), "--domain", "regulated",
            "--previous-report", str(ex / "qaw" / "qaw-report.md"), "--system", "Personal Finance Tracker",
            "--date", "2026-11-02", "--out", str(work / "prep.md"))
    check("the bundled prep reads the bundled guide", r.returncode == 0 and "### Regulated data" in (work / "prep.md").read_text())
    r = run(str(qaw / "tests/validate.py"), str(ex / "qaw" / "qaw-report.md"))
    check("the bundled validator passes the example report", r.returncode == 0)
    r = subprocess.run(["bash", str(qaw / "scripts/build-report.sh"), str(ex / "qaw" / "qaw-summary.md"),
                        "--format", "html", "--out", str(work / "s.html")], cwd=work, capture_output=True, text=True)
    check("the bundled report builder finds its converter", r.returncode == 0 and (work / "s.html").is_file())

    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        check("the zip holds the plugin folder as its single top-level entry",
              {n.split("/")[0] for n in names} == {appbundle.APP_NAME})
        check("the zip holds .claude-plugin/plugin.json under that folder",
              f"{appbundle.APP_NAME}/.claude-plugin/plugin.json" in names)
        check("the zip lists every built file", {n.split("/", 1)[1] for n in names if not n.endswith("/")} == set(rels))
        check("zip entries carry a fixed timestamp",
              all(i.date_time == appbundle.ZIP_DATE for i in z.infolist()))
        mode = (z.getinfo(f"{appbundle.APP_NAME}/skills/quality-attribute-workshop/scripts/build-report.sh").external_attr >> 16) & 0o777
        check("shell scripts stay executable in the zip", mode == 0o755)
    check("the zip is named after the version", archive.name == f"{appbundle.APP_NAME}-{MANIFEST['version']}.zip")
    _, archive2, _ = appbundle.build(out / "b")
    check("two builds give byte-identical zips",
          hashlib.sha256(archive.read_bytes()).hexdigest() == hashlib.sha256(archive2.read_bytes()).hexdigest())

with tempfile.TemporaryDirectory() as td:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = appbundle.main(["--out", td])
        bad = appbundle.main(["--bogus"])
    check("the CLI builds and exits 0", rc == 0 and any(Path(td).glob("*.zip")))
    check("an unknown option exits 2", bad == 2)
    write(Path(td), "x/sei-architecture-methodology-app/keep.txt", "keep\n")
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        refused = appbundle.main(["--out", str(Path(td) / "x")])
    check("the CLI refuses to replace a folder it did not build, with exit 2", refused == 2)

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
