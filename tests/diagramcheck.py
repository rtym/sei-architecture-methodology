#!/usr/bin/env python3
"""Diagram regression check for the worked examples. Standard library only.

  diagramcheck.py                       static check: every committed PNG against the baseline
  diagramcheck.py --render ENGINE       re-render every example source (mermaid | plantuml | all)
                                        with the installed toolchain and compare its layout
  diagramcheck.py --update              re-measure everything and rewrite the baseline

The baseline (`tests/diagram-baseline.json`) records, for every PNG under `examples/`, the diagram
source it was rendered from and how the approved render looks: pixel size, element counts, the
words it shows, and three layout defects counted from the SVG — edges that cross, nodes that
overlap, and edges drawn through a node they do not connect to. The measuring itself is the
plugin's own `skills/sei-diagrams/scripts/diagramlint.py`, the script a skill runs on a render.

The static check needs no renderer. It fails when a source changed but its PNG did not (a stale
render), when a PNG changed without the baseline being updated, or when a PNG lost resolution.
The render check needs the toolchain. It fails when a fresh render shows different elements or
words than the approved one, has more crossings, overlaps or run-through edges, uses a colour
outside the SEI palette, or changes shape. A renderer upgrade that degrades a diagram fails here.
It also renders every diagram pattern a skill, template or reference teaches: each must compile
and be free of the same defects, because a pattern is what Claude copies into a project.

After changing a diagram on purpose: re-render it, open the PNG, then run `--update`.

Exit codes: 0 clean, 1 problems found, 2 usage error or missing toolchain.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EXAMPLES = ROOT / "examples"
BASELINE = HERE / "diagram-baseline.json"
sys.path.insert(0, str(ROOT / "skills" / "sei-diagrams" / "scripts"))
import diagramlint as lint  # noqa: E402
from diagramlint import (ASSETS, DEFECTS, HEX_RE, MERMAID_THEME_MARKS, UNTHEMED, ToolchainError,  # noqa: E402,F401
                         _six, measure, off_palette, palette, sha, source_colour_errors)

# px on the longer side; a committed PNG below this has lost its high-resolution render. Mermaid
# renders fit a 1600 px box at scale 3; a small PlantUML diagram at 240 dpi is about 900 px.
MIN_LONG_SIDE = {"mermaid": 4000, "plantuml": 850}
ASPECT_TOLERANCE = 0.25     # a fresh render may differ this much in width/height ratio (fonts)
BLOCK_RE = re.compile(r"^[ \t]*```mermaid[ \t]*\n(.*?)^[ \t]*```[ \t]*$", re.DOTALL | re.MULTILINE)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+\.png)\)")
FENCE_RE = re.compile(r"^[ \t]*```(mermaid|plantuml|puml)[ \t]*\n(.*?)^[ \t]*```[ \t]*$", re.DOTALL | re.MULTILINE)


class Diagram:
    """One committed PNG and the source it is rendered from."""

    def __init__(self, png: Path, engine: str, source: str, ref: str):
        self.png, self.engine, self.source, self.ref = png, engine, source, ref

    @property
    def key(self) -> str:
        return _rel(self.png)


# --------------------------------------------------------------------------- #
# Discovery: which source renders which PNG
# --------------------------------------------------------------------------- #

def mermaid_blocks(md: Path) -> list[tuple[str, str]]:
    """(output basename, block text) for every ```mermaid block, named as render.sh names it:
    the `%% name: <slug>` comment, else <mdname>-<NN> in document order."""
    out = []
    for n, m in enumerate(BLOCK_RE.finditer(md.read_text(encoding="utf-8")), 1):
        body = m.group(1)
        name = re.search(r"^[ \t]*%%[ \t]*name:[ \t]*(.+?)[ \t]*$", body, re.MULTILINE)
        base = re.sub(r"[^A-Za-z0-9._-]", "-", name.group(1)) if name else f"{md.stem}-{n:02d}"
        out.append((base, body))
    return out


def discover(root: Path = EXAMPLES) -> tuple[list[Diagram], list[str]]:
    """Every PNG under `root` with its source, plus the problems found while pairing them."""
    found: dict[Path, Diagram] = {}
    errs: list[str] = []
    for src in sorted(root.rglob("*.mmd")):
        found[src.with_suffix(".png").resolve()] = Diagram(
            src.with_suffix(".png"), "mermaid", src.read_text(encoding="utf-8"), _rel(src))
    for src in sorted(root.rglob("*.puml")):
        found[src.with_suffix(".png").resolve()] = Diagram(
            src.with_suffix(".png"), "plantuml", src.read_text(encoding="utf-8"), _rel(src))
    # a Mermaid block that lives only in a Markdown file: the image line beside it names the PNG
    for md in sorted(root.rglob("*.md")):
        blocks = mermaid_blocks(md)
        if not blocks:
            continue
        images = {Path(p).stem: (md.parent / p) for p in IMAGE_RE.findall(md.read_text(encoding="utf-8"))}
        for base, body in blocks:
            png = images.get(base)
            if png is None or png.with_suffix(".mmd").is_file():
                continue
            have = found.get(png.resolve())
            if have is None:
                found[png.resolve()] = Diagram(png, "mermaid", body, f"{_rel(md)}#{base}")
            elif have.source != body:
                errs.append(f"{_rel(md)}: the mermaid block '{base}' differs from the one in "
                            f"{have.ref.split('#')[0]} that renders the same {_rel(png)}")
    diagrams = sorted(found.values(), key=lambda d: d.key)
    known = {d.png.resolve() for d in diagrams}
    for png in sorted(root.rglob("*.png")):
        if png.resolve() not in known:
            errs.append(f"{_rel(png)}: no diagram source found for this PNG")
    for d in diagrams:
        if not d.png.is_file():
            errs.append(f"{d.ref}: no rendered PNG at {d.key}")
    return [d for d in diagrams if d.png.is_file()], errs


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def png_size(path: Path) -> tuple[int, int]:
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def plugin_colour_errors(root: Path = ROOT) -> list[str]:
    """Every diagram the plugin teaches — the fenced examples in skills, templates and references —
    must use palette colours only: what a skill shows is what Claude copies into a project."""
    errs = []
    for sub in ("skills", "templates", "references", "commands"):
        for md in sorted((root / sub).rglob("*.md")):
            if "node_modules" in md.parts:
                continue
            for m in FENCE_RE.finditer(md.read_text(encoding="utf-8")):
                bad = source_colour_errors(m.group(2))
                if bad:
                    line = md.read_text(encoding="utf-8")[:m.start()].count("\n") + 1
                    errs.append(f"{_rel(md)}:{line}: {m.group(1)} block uses colour(s) outside "
                                f"the SEI palette: {', '.join(bad)}")
    return errs


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #

def render_svg(d: Diagram, work: Path) -> str:
    """Render one diagram to SVG with the plugin's own render script; return the SVG text."""
    work.mkdir(parents=True, exist_ok=True)
    src = work / ("diagram.mmd" if d.engine == "mermaid" else "diagram.puml")
    src.write_text(d.source, encoding="utf-8")
    try:
        return lint.render_svg(src, work)
    except ToolchainError as e:
        raise ToolchainError(str(e).replace(str(src), d.ref)) from None


def render_all(diagrams: list[Diagram], workers: int = 4) -> dict[str, dict | str]:
    """key → metrics, or the error text when the render failed."""
    with tempfile.TemporaryDirectory() as td:
        def one(item: tuple[int, Diagram]):
            n, d = item
            try:
                return d.key, measure(render_svg(d, Path(td) / str(n)))
            except (ToolchainError, ET.ParseError) as e:
                return d.key, str(e)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            return dict(pool.map(one, enumerate(diagrams)))


PLACEHOLDER_RE = re.compile(r"<(?!/?(?:br|i|b)\b)(?!<)([A-Za-z][^<>\n]*)>(?!>)")


def taught(root: Path = ROOT) -> list[Diagram]:
    """Every fenced diagram in a skill, template, reference or command — the patterns Claude
    copies into a project. A template's `<placeholder>` is replaced by its own words so the
    pattern compiles; the PNG path is only a label."""
    out = []
    for sub in ("skills", "templates", "references", "commands"):
        for md in sorted((root / sub).rglob("*.md")):
            if "node_modules" in md.parts:
                continue
            text = md.read_text(encoding="utf-8")
            for m in FENCE_RE.finditer(text):
                line = text[:m.start()].count("\n") + 1
                engine = "mermaid" if m.group(1) == "mermaid" else "plantuml"
                out.append(Diagram(md.with_name(f"{md.name}:{line}"), engine,
                                   PLACEHOLDER_RE.sub(lambda x: x.group(1), m.group(2)), f"{_rel(md)}:{line}"))
    return out


def pattern_errors(patterns: list[Diagram], results: dict) -> list[str]:
    """A taught pattern must compile and be free of every counted defect."""
    errs = []
    for d in patterns:
        got = results[d.key]
        if isinstance(got, str):
            errs.append(got)
            continue
        if not lint.measured(got):
            errs.append(f"{d.ref}: the pattern renders nothing diagramlint.py can measure")
        for k, label in DEFECTS:
            if got[k]:
                errs.append(f"{d.ref}: the pattern renders with {got[k]} {label}: {'; '.join(got['details'][k])}")
        # Mermaid's native C4 diagrams ignore the theme; the skill shows them as chat sketches only
        native_c4 = d.source.lstrip().startswith("C4")
        extra = [] if native_c4 else off_palette(got, d.engine)
        if extra:
            errs.append(f"{d.ref}: the pattern renders colour(s) outside the SEI palette: {', '.join(extra)}")
    return errs


def have_toolchain(engine: str) -> bool:
    if engine == "mermaid":
        return (ROOT / "skills/sei-diagrams/node_modules/.bin/mmdc").is_file() or bool(shutil.which("mmdc"))
    jar = os.environ.get("PLANTUML_JAR", "")
    return bool(shutil.which("java")) and (bool(shutil.which("plantuml")) or Path(jar).is_file())


# --------------------------------------------------------------------------- #
# Baseline and the two checks
# --------------------------------------------------------------------------- #

STRUCTURE = ("nodes", "edges", "clusters", "participants", "messages", "words", "words_sha")


def entry(d: Diagram, metrics: dict) -> dict:
    w, h = png_size(d.png)
    out = {"source": d.ref, "engine": d.engine, "source_sha": sha(d.source),
           "png_sha": sha(d.png.read_bytes()), "width": w, "height": h}
    out.update({k: metrics[k] for k in STRUCTURE})
    out.update({k: metrics[k] for k, _ in DEFECTS})
    out["off_palette"] = off_palette(metrics, d.engine)
    return out


def load_baseline(path: Path = BASELINE) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def static_errors(diagrams: list[Diagram], baseline: dict) -> list[str]:
    errs = []
    fix = "re-render it, check the PNG, then run tests/diagramcheck.py --update"
    keys = {d.key for d in diagrams}
    for key in sorted(set(baseline) - keys):
        errs.append(f"{key}: in the baseline but no longer in examples/ (run --update)")
    for d in diagrams:
        b = baseline.get(d.key)
        if b is None:
            errs.append(f"{d.key}: not in the baseline (run tests/diagramcheck.py --update)")
            continue
        w, h = png_size(d.png)
        png_changed = sha(d.png.read_bytes()) != b["png_sha"]
        if sha(d.source) != b["source_sha"]:
            what = "and its PNG changed" if png_changed else "but its PNG did not — the render is stale"
            errs.append(f"{d.key}: the source ({d.ref}) changed {what}; {fix}")
        elif png_changed:
            errs.append(f"{d.key}: the PNG changed but its source did not; {fix}")
        floor = MIN_LONG_SIDE[d.engine]
        if max(w, h) < floor:
            errs.append(f"{d.key}: {w}×{h} px is below the {floor} px high-resolution floor")
        if (w, h) != (b["width"], b["height"]) and not png_changed:
            errs.append(f"{d.key}: baseline records {b['width']}×{b['height']} px, the PNG is {w}×{h}")
        if b["off_palette"]:
            errs.append(f"{d.key}: the approved render uses colour(s) outside the SEI palette: "
                        f"{', '.join(b['off_palette'])}")
        bad = source_colour_errors(d.source)
        if bad:
            errs.append(f"{d.ref}: sets colour(s) outside the SEI palette: {', '.join(bad)}")
    return errs


def accepted_defects(baseline: dict) -> list[str]:
    """Layout defects the approved renders already have — reported, never a failure: some cannot
    be laid out away (two services each using the same two stores always cross once)."""
    return [f"{key}: {b[k]} {label}" for key, b in sorted(baseline.items())
            for k, label in DEFECTS if b.get(k)]


def render_errors(diagrams: list[Diagram], baseline: dict, results: dict) -> list[str]:
    errs = []
    for d in diagrams:
        b, got = baseline.get(d.key), results[d.key]
        if isinstance(got, str):
            errs.append(got)
            continue
        if b is None:
            continue                                    # the static check reports it
        # PlantUML before 1.2026.10 does not tag a sequence diagram's participants and messages
        # in its SVG; the words it shows still have to match.
        untagged = b["participants"] and not got["participants"] and not got["nodes"]
        for k in STRUCTURE:
            if untagged and k in ("participants", "messages"):
                continue
            if got[k] != b[k]:
                errs.append(f"{d.key}: a fresh render has {k} = {got[k]}, the approved one {b[k]}")
        for k, label in DEFECTS:
            if got[k] > b[k]:
                errs.append(f"{d.key}: a fresh render has {got[k]} {label}, the approved one {b[k]}")
        extra = sorted(set(off_palette(got, d.engine)) - set(b["off_palette"]))
        if extra:
            errs.append(f"{d.key}: a fresh render uses colour(s) outside the SEI palette: {', '.join(extra)}")
        drawn = {_six(c) for c in got["colours"]}
        styled = {_six(c) for c in got["style_colours"]}
        unthemed = sorted((drawn | styled if d.engine == "mermaid" else drawn) & UNTHEMED[d.engine])
        if d.engine == "mermaid" and not MERMAID_THEME_MARKS <= styled:
            unthemed = unthemed or ["no SEI colours in the stylesheet"]
        if unthemed:
            errs.append(f"{d.key}: a fresh render shows the renderer's default colours "
                        f"({', '.join(unthemed)}) — the SEI theme was not applied")
        want = b["width"] / b["height"]
        if got["aspect"] and abs(got["aspect"] / want - 1) > ASPECT_TOLERANCE:
            errs.append(f"{d.key}: a fresh render is {got['aspect']:.2f}:1, the approved one "
                        f"{want:.2f}:1 — the layout changed shape")
    return errs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="diagramcheck.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--render", choices=("mermaid", "plantuml", "all"))
    ap.add_argument("--update", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    diagrams, errs = discover()
    engines = ("mermaid", "plantuml") if a.update or a.render == "all" else ((a.render,) if a.render else ())
    missing = [e for e in engines if not have_toolchain(e)]
    if missing:
        print(f"diagramcheck: no {' / '.join(missing)} toolchain — see CLAUDE.md for the setup",
              file=sys.stderr)
        return 2
    if a.update:
        results = render_all(diagrams)
        failed = [v for v in results.values() if isinstance(v, str)]
        if failed or errs:
            print("\n".join(errs + failed), file=sys.stderr)
            return 1
        data = {d.key: entry(d, results[d.key]) for d in diagrams}
        BASELINE.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {_rel(BASELINE)}: {len(data)} diagram(s)")
        baseline = data
        errs = static_errors(diagrams, data) + plugin_colour_errors()
    else:
        baseline = load_baseline()
        errs += static_errors(diagrams, baseline) + plugin_colour_errors()
        if engines:
            todo = [d for d in diagrams if d.engine in engines]
            errs += render_errors(todo, baseline, render_all(todo))
            patterns = [d for d in taught() if d.engine in engines]
            errs += pattern_errors(patterns, render_all(patterns))
            print(f"re-rendered {len(todo)} {' + '.join(engines)} diagram(s) and {len(patterns)} taught pattern(s)")
    for note in accepted_defects(baseline):
        print(f"note  {note} (accepted in the baseline)")
    for e in errs:
        print(f"FAIL  {e}")
    print(f"{len(diagrams)} diagram(s), {len(errs)} problem(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
