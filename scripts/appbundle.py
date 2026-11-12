#!/usr/bin/env python3
"""Build the Claude app edition of the plugin, where every skill is self-contained, for
claude.ai chat and Cowork. Standard library only; the same sources give a byte-identical zip.

  appbundle.py [--out DIR] [--no-zip]

In chat, the Claude app copies only a skill's own folder into the code-execution sandbox, so a
skill cannot read the plugin's shared references/, templates/, scripts/ or tests/. This build
copies every file a skill names, and every file those files name, into the skill's folder. It
rewrites ${CLAUDE_PLUGIN_ROOT}/<path> to ${CLAUDE_SKILL_DIR}/<path inside the folder>, trims
SKILL.md front-matter to the fields claude.ai accepts, and adds a note on running in the app.

Writes DIR/sei-architecture-methodology-app/ and DIR/sei-architecture-methodology-app-<version>.zip
(DIR defaults to dist/claude-app). Upload the zip in Customize > Plugins > Add > Upload plugin.

Exit codes: 0 built, 2 a named file is missing, a limit is broken, or DIR holds something else.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_NAME = "sei-architecture-methodology-app"

# Path references a skill can make to plugin files; a trailing slash names a whole directory.
REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]*[A-Za-z0-9_-])(/?)")
TEXT_SUFFIXES = {".md", ".py", ".sh", ".puml", ".json", ".mmd", ".txt", ".yml", ".yaml"}
SKIP_DIRS = {"node_modules", "__pycache__", ".git"}
SKIP_FILES = {".DS_Store"}
# Files a script loads without naming them as ${CLAUDE_PLUGIN_ROOT}/… (paths from its own folder).
IMPLICIT_DEPS = {
    "scripts/build-report.sh": ["scripts/mdreport.py"],
    "tests/validate.py": ["templates/"],       # the structure check reads every artifact's template
    "scripts/qawkit.py": ["references/qaw-question-guide.md", "references/qaw-facilitation-playbook.md"],
    "skills/sei-diagrams/scripts/render.sh": ["skills/sei-diagrams/assets/", "skills/sei-diagrams/scripts/setup.sh"],
    "skills/sei-diagrams/scripts/render-plantuml.sh": ["skills/sei-diagrams/assets/"],
    "skills/sei-diagrams/scripts/diagramlint.py": ["skills/sei-diagrams/assets/",
                                                   "skills/sei-diagrams/scripts/render.sh",
                                                   "skills/sei-diagrams/scripts/render-plantuml.sh"],
    "skills/sei-diagrams/scripts/setup.sh": ["skills/sei-diagrams/package.json",
                                             "skills/sei-diagrams/package-lock.json"],
}
# Limits for skills and plugins uploaded to claude.ai (Agent Skills spec and the app's docs).
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME, MAX_DESCRIPTION = 64, 1024
MAX_FILES, MAX_BYTES = 5000, 200 * 1024 * 1024
ADVISED_SKILL_LINES = 500
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


class BuildError(Exception):
    """A source problem the build cannot work around; the message says what to fix."""


# --------------------------------------------------------------------------- #
# Reading the plugin
# --------------------------------------------------------------------------- #

def front_matter(text: str) -> tuple[dict[str, str], str]:
    """Scalar and folded (`>-`, `>`, `|`) front-matter fields, and the body after it."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        raise BuildError("no YAML front-matter")
    fields: dict[str, str] = {}
    key, block = None, []
    for ln in m.group(1).splitlines() + ["end:"]:
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", ln)
        if km:
            if key is not None:
                fields[key] = " ".join(b.strip() for b in block if b.strip())
            key, value = km.group(1), km.group(2).strip()
            block = [] if value in (">-", ">", "|", "|-") else [value.strip("'\"")]
        elif key is not None:
            block.append(ln)
    return fields, text[m.end():]


def skill_dirs(root: Path) -> list[str]:
    manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    listed = manifest.get("skills") or sorted(
        f"skills/{p.parent.name}" for p in (root / "skills").glob("*/SKILL.md"))
    return [Path(s).name for s in listed]


def command_map(root: Path) -> list[tuple[str, str]]:
    """[(command, skill)] from each commands/*.md that points at a skill's SKILL.md."""
    out = []
    for cmd in sorted((root / "commands").glob("*.md")):
        m = re.search(r"skills/([a-z0-9-]+)/SKILL\.md", cmd.read_text(encoding="utf-8"))
        if m:
            out.append((f"/{cmd.stem}", m.group(1)))
    return out


def _walk(path: Path) -> list[Path]:
    return sorted(p for p in path.rglob("*") if p.is_file() and p.name not in SKIP_FILES
                  and not SKIP_DIRS.intersection(p.relative_to(path).parts))


# --------------------------------------------------------------------------- #
# Placing files inside a skill
# --------------------------------------------------------------------------- #

def bundle_path(plugin_path: str, skill: str) -> str:
    """Where a plugin file lives inside `skill`'s folder. The skill's own files keep their place;
    another skill's files go under related/<skill>/, its SKILL.md renamed GUIDE.md so that no
    nested SKILL.md is mistaken for a skill; everything else keeps its plugin-relative path."""
    parts = plugin_path.strip("/").split("/")
    if parts[0] == "skills" and len(parts) >= 2:
        if parts[1] == skill:
            return "/".join(parts[2:])
        rest = ["GUIDE.md"] if parts[2:] == ["SKILL.md"] else parts[2:]
        return "/".join(["related", parts[1], *rest])
    return "/".join(parts)


def rewrite(text: str, skill: str) -> str:
    def sub(m: re.Match) -> str:
        target = bundle_path(m.group(1), skill)
        return "${CLAUDE_SKILL_DIR}" + (f"/{target}" if target else "") + m.group(2)
    return REF_RE.sub(sub, text)


def skill_closure(root: Path, skill: str) -> dict[str, str]:
    """plugin path → path inside the skill folder, for the skill's own files and every file they
    name, transitively."""
    own = [p.relative_to(root).as_posix() for p in _walk(root / "skills" / skill)]
    placed: dict[str, str] = {}
    queue = list(own)
    while queue:
        rel = queue.pop(0)
        if rel in placed:
            continue
        src = root / rel
        placed[rel] = bundle_path(rel, skill)
        named: list[str] = list(IMPLICIT_DEPS.get(rel, []))
        if src.suffix in TEXT_SUFFIXES:
            named += [m.group(1) + m.group(2) for m in REF_RE.finditer(src.read_text(encoding="utf-8"))]
        for ref in named:
            target = root / ref.rstrip("/")
            if target.is_dir():
                queue += [p.relative_to(root).as_posix() for p in _walk(target)]
            elif target.is_file():
                queue.append(target.relative_to(root).as_posix())
            else:
                raise BuildError(f"{rel} names {ref}, which does not exist in the plugin")
    seen: dict[str, str] = {}
    for rel, dest in placed.items():
        if dest in seen and seen[dest] != rel:
            raise BuildError(f"skill {skill}: {seen[dest]} and {rel} would both be {dest}")
        seen[dest] = rel
    return placed


# --------------------------------------------------------------------------- #
# Writing the app edition
# --------------------------------------------------------------------------- #

def app_note(commands: list[tuple[str, str]]) -> str:
    cmds = "; ".join(f"`{c}` is the `{s}` skill" for c, s in commands)
    return "\n".join([
        "> **Claude app edition.** Every file this skill names is inside its own folder, and",
        "> `${CLAUDE_SKILL_DIR}` is that folder. Where the variable is not replaced by a path",
        "> (claude.ai chat), read the path relative to the folder this `SKILL.md` was loaded from.",
        "> With no project folder, write the artifacts under `architecture/` in the code-execution",
        "> working folder and offer them as files; without code execution, show them in the reply",
        "> and say which checks did not run. The diagram renderers need Node.js, Chromium, Java and",
        "> Graphviz, which chat does not have: keep each diagram's source in the artifact and list",
        "> the PNGs for the user to render later in Claude Code. Slash commands in this text are the",
        f"> Claude Code commands; here, ask for the activity by name ({cmds}).",
    ])


def skill_md(text: str, skill: str, note: str, license_id: str) -> str:
    fields, body = front_matter(text)
    name, desc = fields.get("name", ""), fields.get("description", "")
    if name != skill or not NAME_RE.match(name) or len(name) > MAX_NAME:
        raise BuildError(f"skill {skill}: name {name!r} must equal its folder and be at most "
                         f"{MAX_NAME} lower-case letters, digits and single hyphens")
    if not desc or len(desc) > MAX_DESCRIPTION:
        raise BuildError(f"skill {skill}: description is {len(desc)} characters; claude.ai "
                         f"accepts 1 to {MAX_DESCRIPTION}")
    head = ["---", f"name: {name}", f"description: {json.dumps(desc, ensure_ascii=False)}"]
    if license_id:
        head.append(f"license: {license_id}")
    body = rewrite(body, skill)
    m = re.search(r"^# .+$", body, re.MULTILINE)
    at = m.end() if m else 0
    body = body[:at] + "\n\n" + note + "\n\n" + body[at:].lstrip("\n")
    return "\n".join(head + ["---", ""]) + body.lstrip("\n")


def readme(manifest: dict, skills: list[str], commands: list[tuple[str, str]]) -> str:
    rows = [f"| `{s}` | {next((c for c, k in commands if k == s), '—')} |" for s in skills]
    return "\n".join([
        f"# SEI Architecture Methodology — Claude app edition {manifest['version']}", "",
        "This is the Claude app edition of the `sei-architecture-methodology` plugin for chat and "
        "Cowork. Every skill carries its own copy of the references, templates and scripts it "
        "uses, because the app gives a skill only its own folder. It is generated by "
        "`scripts/appbundle.py` from the plugin source; do not edit it by hand.", "",
        "## Install", "",
        "1. In claude.ai or the desktop app, open **Customize > Plugins**.",
        "2. Choose **Add > Upload plugin** and select the zip.",
        "3. In a new chat, ask Claude which skills it has from plugins to check the install.", "",
        "For Claude Code, install the plugin itself from the marketplace "
        f"(`/plugin marketplace add {manifest.get('repository', '').replace('https://github.com/', '')}`) "
        "instead of this edition.", "",
        "## Skills", "",
        "| Skill | Claude Code command |", "|-------|---------------------|", *rows, "",
        "## What differs from Claude Code", "",
        "- Paths start with `${CLAUDE_SKILL_DIR}`, the skill's own folder, instead of the plugin root.",
        "- Diagrams are not rendered in chat: the renderers need Node.js, Chromium, Java and "
        "Graphviz. Each diagram's source stays in the artifact for rendering later.",
        "- The slash commands are not included; ask for an activity by name instead.", "",
    ])


def build(out_dir: Path, root: Path = ROOT, make_zip: bool = True) -> tuple[Path, Path | None, list[str]]:
    """Write the app edition under out_dir; return (folder, zip or None, warnings)."""
    manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "")
    dest = out_dir / APP_NAME
    if dest.exists():
        old = dest / ".claude-plugin" / "plugin.json"
        try:
            ours = json.loads(old.read_text(encoding="utf-8")).get("name") == APP_NAME
        except (OSError, ValueError):
            ours = False
        if not ours:
            raise BuildError(f"{dest} exists and is not an earlier build; remove it or pick another --out")
        shutil.rmtree(dest)
    skills, commands = skill_dirs(root), command_map(root)
    note = app_note(commands)
    warnings: list[str] = []
    files: dict[str, bytes] = {}
    for skill in skills:
        for rel, inside in skill_closure(root, skill).items():
            src = root / rel
            data = src.read_bytes()
            if src.suffix in TEXT_SUFFIXES:
                text = data.decode("utf-8")
                if rel == f"skills/{skill}/SKILL.md":
                    text = skill_md(text, skill, note, manifest.get("license", ""))
                    if text.count("\n") > ADVISED_SKILL_LINES:
                        warnings.append(f"skills/{skill}/SKILL.md has {text.count(chr(10))} lines; "
                                        f"the app advises at most {ADVISED_SKILL_LINES}")
                else:
                    text = rewrite(text, skill)
                data = text.encode("utf-8")
            files[f"skills/{skill}/{inside}"] = data
    app_manifest = {k: manifest[k] for k in ("version", "author", "homepage", "repository", "license", "keywords")
                    if k in manifest}
    app_manifest = {"name": APP_NAME, "displayName": "SEI Architecture Methodology (Claude app)",
                    "description": manifest.get("description", "") + " Claude app edition: every skill "
                    "carries the files it needs, for chat and Cowork.", **app_manifest}
    files[".claude-plugin/plugin.json"] = (json.dumps(app_manifest, indent=2, ensure_ascii=False) + "\n").encode()
    files["README.md"] = readme(manifest, skills, commands).encode("utf-8")
    for legal in ("LICENSE", "NOTICE"):
        if (root / legal).is_file():
            files[legal] = (root / legal).read_bytes()
    if len(files) > MAX_FILES or sum(map(len, files.values())) > MAX_BYTES:
        raise BuildError(f"the app edition has {len(files)} files and {sum(map(len, files.values()))} "
                         f"bytes; claude.ai accepts {MAX_FILES} files and {MAX_BYTES} bytes")
    executable = {f"skills/{s}/{inside}" for s in skills for rel, inside in skill_closure(root, s).items()
                  if (root / rel).stat().st_mode & stat.S_IXUSR}
    for rel, data in files.items():
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o755 if rel in executable else 0o644)
    archive = None
    if make_zip:
        archive = out_dir / f"{APP_NAME}-{version}.zip"
        dirs = sorted({str(Path(rel).parent) for rel in files} - {"."})
        all_dirs = sorted({"/".join(d.split("/")[:i]) for d in dirs for i in range(1, d.count("/") + 2)})
        with zipfile.ZipFile(archive, "w") as z:
            for d in all_dirs:
                info = zipfile.ZipInfo(f"{APP_NAME}/{d}/", ZIP_DATE)
                info.external_attr = (0o40755 << 16) | 0x10
                z.writestr(info, b"")
            for rel in sorted(files):
                info = zipfile.ZipInfo(f"{APP_NAME}/{rel}", ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o100755 if rel in executable else 0o100644) << 16
                z.writestr(info, files[rel], compresslevel=9)
    return dest, archive, warnings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="appbundle.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "claude-app")
    ap.add_argument("--no-zip", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        folder, archive, warnings = build(a.out, make_zip=not a.no_zip)
    except BuildError as e:
        print(f"appbundle: {e}", file=sys.stderr)
        return 2
    for w in warnings:
        print(f"note: {w}")
    print(f"wrote {folder}")
    if archive:
        print(f"wrote {archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
