#!/usr/bin/env python3
"""Behaviour tests for the render scripts — render.sh, render-plantuml.sh, render-all.sh — and for
diagramlint.py on real renders. Each engine's tests run only when its toolchain is installed
(tests/run.sh says which were skipped). Everything renders in a temporary directory outside the
repository. Standard library only; exit 0 on success."""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import diagramcheck as dc  # noqa: E402

SCRIPTS = ROOT / "skills" / "sei-diagrams" / "scripts"
RENDER, PLANTUML, LINT = SCRIPTS / "render.sh", SCRIPTS / "render-plantuml.sh", SCRIPTS / "diagramlint.py"
RENDER_ALL = ROOT / "scripts" / "render-all.sh"
PASSES = 0
FAILS = 0


def check(name: str, cond: bool) -> None:
    global PASSES, FAILS
    if cond:
        PASSES += 1
    else:
        FAILS += 1
        print(f"FAIL  {name}")


def sh(*args, cwd: Path) -> tuple[int, str]:
    r = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def size(png: Path) -> tuple[int, int]:
    return struct.unpack(">II", png.read_bytes()[16:24])


FLOW = 'flowchart LR\n  %% Smoke\n  a["A"] --> b["B"]\n  classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;\n  class a,b internal\n'
# two services that each use the same two stores, side by side: one crossing in a layered layout
CROSSED = ('flowchart TB\n  a["Service A"]\n  b["Service B"]\n  c[("Store C")]\n  d[("Store D")]\n'
           '  a --> c\n  a --> d\n  b --> c\n  b --> d\n')
STACKED = CROSSED + "  c ~~~ d\n"
PUML = "@startuml {name}\n!include plantuml-theme.puml\ntitle Smoke\nrectangle \"A\" as a\nrectangle \"B\" as b\na --> b : uses\n@enduml\n"

engines = [e for e in ("mermaid", "plantuml") if dc.have_toolchain(e)]

# --------------------------------------------------------------------------- #
# Mermaid — render.sh
# --------------------------------------------------------------------------- #

if "mermaid" in engines:
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        (work / "one.mmd").write_text(FLOW)
        rc, out = sh("bash", RENDER, "one.mmd", cwd=work)
        check("a .mmd renders to a PNG beside it", rc == 0 and (work / "one.png").is_file())
        check("the default render is 4800 px on its longer side (1600 px box at scale 3)",
              (work / "one.png").is_file() and max(size(work / "one.png")) == 4800)
        rc, out = sh("bash", RENDER, "--scale", "1", "--out", "small", "one.mmd", cwd=work)
        check("--scale and --out are honoured",
              rc == 0 and (work / "small" / "one.png").is_file() and max(size(work / "small" / "one.png")) == 1600)
        rc, out = sh("bash", RENDER, "--format", "svg", "--out", "svg", "one.mmd", cwd=work)
        svg = (work / "svg" / "one.svg").read_text() if (work / "svg" / "one.svg").is_file() else ""
        check("--format svg writes an SVG that carries the SEI theme", rc == 0 and "#EDF2F8" in svg and "#6B7A8D" in svg)

        doc = work / "docs" / "view.md"
        doc.parent.mkdir()
        doc.write_text("# View\n\n```mermaid\n" + FLOW.replace("%% Smoke", "%% Smoke\n  %% name: context") +
                       "```\n\nText.\n\n```mermaid\n" + FLOW + "```\n\n```bash\necho not a diagram\n```\n")
        rc, out = sh("bash", RENDER, "--out", "docs/diagrams", "docs/view.md", cwd=work)
        made = sorted(p.name for p in (work / "docs" / "diagrams").glob("*.png"))
        check("Markdown blocks render as <name>.png and <mdname>-<NN>.png in document order",
              rc == 0 and made == ["context.png", "view-02.png"])
        doc.write_text("```mermaid\n" + FLOW.replace("%% Smoke", "%% name: same") + "```\n\n```mermaid\n" +
                       FLOW.replace("%% Smoke", "%% name: same") + "```\n")
        rc, out = sh("bash", RENDER, "--out", "dup", "docs/view.md", cwd=work)
        check("two blocks with the same name fail and say which", rc != 0 and "both resolve" in out)
        doc.write_text("# No diagrams here\n")
        rc, out = sh("bash", RENDER, "docs/view.md", cwd=work)
        check("a Markdown file without blocks is reported, not an error", rc == 0 and "no ```mermaid blocks" in out)

        spaced = work / "my project" / "diagrams"
        spaced.mkdir(parents=True)
        (spaced / "x.mmd").write_text(FLOW)
        (spaced / "y.mmd").write_text(FLOW)
        rc, out = sh("bash", RENDER, "my project/diagrams/*.mmd", cwd=work)
        check("a quoted glob under a directory with a space renders every match",
              rc == 0 and (spaced / "x.png").is_file() and (spaced / "y.png").is_file())
        rc, out = sh("bash", RENDER, "my project/diagrams/*.nothing", cwd=work)
        check("a glob that matches nothing fails and says so", rc != 0 and "no file matches" in out)
        for f in spaced.glob("*.png"):
            f.unlink()
        rc, out = sh("bash", RENDER, "my project/diagrams", cwd=work)
        check("a directory renders every .mmd in it", rc == 0 and len(list(spaced.glob("*.png"))) == 2)
        rc, out = sh("bash", RENDER, "missing.mmd", cwd=work)
        check("a missing source fails", rc != 0 and "not found" in out)
        (work / "bad.mmd").write_text("flowchart LR\n  a --> --> b\n")
        rc, out = sh("bash", RENDER, "bad.mmd", "one.mmd", cwd=work)
        check("a source that does not compile fails the run but the others still render",
              rc != 0 and "FAIL" in out and "1 rendered, 1 failed" in out and not (work / "bad.png").is_file())
        rc, out = sh("bash", RENDER, "notes.txt", cwd=work)
        check("an unknown file type is not found or skipped, never rendered", "skip" in out)

        # ----- diagramlint.py on real renders -----
        (work / "crossed.mmd").write_text(CROSSED)
        (work / "stacked.mmd").write_text(STACKED)
        rc, out = sh(sys.executable, LINT, "crossed.mmd", cwd=work)
        check("diagramlint finds the crossing between two services sharing two stores",
              rc == 1 and "edge crossing(s): 1" in out and "×" in out)
        rc, out = sh(sys.executable, LINT, "stacked.mmd", "one.mmd", cwd=work)
        check("stacking the stores with an invisible link removes it (the layout playbook's rule)",
              rc == 0 and out.count("  OK") == 2 and "edge crossing(s): 0" in out)
        check("diagramlint leaves no file beside the source", not list(work.glob("*.svg")) and not (work / "crossed.png").is_file())
        (work / "state.mmd").write_text("stateDiagram-v2\n  [*] --> Queued\n  Queued --> Done : ok\n  Done --> [*]\n")
        rc, out = sh(sys.executable, LINT, "state.mmd", cwd=work)
        check("a state diagram is measured", rc == 0 and "3 edge(s)" in out)
        (work / "seq.mmd").write_text("sequenceDiagram\n  participant A\n  participant B\n  A->>B: call\n  B-->>A: reply\n")
        rc, out = sh(sys.executable, LINT, "seq.mmd", cwd=work)
        check("a sequence diagram reports participants and messages", rc == 0 and "2 participant(s), 2 message(s)" in out)
        (work / "gantt.mmd").write_text("gantt\n  title Plan\n  section A\n  Task :a1, 2026-01-01, 30d\n")
        rc, out = sh(sys.executable, LINT, "gantt.mmd", cwd=work)
        check("an unsupported diagram type exits 2 and is not called OK", rc == 2 and "NOT measured" in out)
        rc, out = sh(sys.executable, LINT, "bad.mmd", cwd=work)
        check("a source that does not compile exits 2 with the renderer's error", rc == 2 and "render failed" in out)

        # ----- render-all.sh: standalone sources and blocks embedded in Markdown -----
        tree = work / "architecture"
        (tree / "drivers" / "diagrams").mkdir(parents=True)
        (tree / "add" / "diagrams").mkdir(parents=True)
        (tree / "drivers" / "diagrams" / "UC-1.mmd").write_text(FLOW)
        (tree / "drivers" / "UC-1.md").write_text("# UC-1\n\n```mermaid\n" + FLOW + "```\n\n![UC-1](diagrams/UC-1.png)\n")
        (tree / "add" / "arch.md").write_text(
            "# Arch\n\n```mermaid\n" + FLOW.replace("%% Smoke", "%% name: context") + "```\n\n![Context](diagrams/context.png)\n\n"
            "```mermaid\n" + FLOW + "```\n\n> A note.\n\n![Second](diagrams/arch-02.png)\n\n"
            "```mermaid\n" + FLOW + "```\n\nA sketch with no image line.\n")
        rc, out = sh("bash", RENDER_ALL, "--list", "architecture", cwd=work)
        check("--list plans three renders and makes none",
              rc == 0 and len(out.strip().splitlines()) == 3 and not list(tree.rglob("*.png")))
        rc, out = sh("bash", RENDER_ALL, "architecture", cwd=work)
        made = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*.png"))
        check("render-all renders the .mmd and the embedded blocks to the PNGs their image lines name",
              rc == 0 and made == ["add/diagrams/arch-02.png", "add/diagrams/context.png", "drivers/diagrams/UC-1.png"])
        check("render-all reports what it rendered", "1 mermaid + 2 embedded mermaid" in out)
        check("a block that has a .mmd is not rendered a second time under another name",
              not (tree / "drivers" / "UC-1-01.png").exists() and not (tree / "drivers" / "diagrams" / "UC-1-01.png").exists())

# --------------------------------------------------------------------------- #
# PlantUML — render-plantuml.sh
# --------------------------------------------------------------------------- #

if "plantuml" in engines:
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        d = work / "architecture" / "diagrams"
        d.mkdir(parents=True)
        (d / "ctx.puml").write_text(PUML.format(name="ctx"))
        (d / "other.puml").write_text(PUML.format(name="other"))
        rc, out = sh("bash", PLANTUML, "architecture/diagrams/ctx.puml", cwd=work)
        check("a .puml renders to a PNG beside it, from outside the plugin", rc == 0 and (d / "ctx.png").is_file())
        rc, out = sh("bash", PLANTUML, "--out", "out", "architecture/diagrams", cwd=work)
        check("a directory renders every .puml, and --out redirects them",
              rc == 0 and sorted(p.name for p in (work / "out").glob("*.png")) == ["ctx.png", "other.png"])
        rc, out = sh("bash", PLANTUML, "--format", "svg", "--out", "svg", "architecture/diagrams/ctx.puml", cwd=work)
        svg = (work / "svg" / "ctx.svg").read_text() if (work / "svg" / "ctx.svg").is_file() else ""
        check("--format svg writes an SVG drawn with the SEI theme", rc == 0 and "#EDF2F8" in svg and "#3E6DA5" in svg)
        (d / "uc.puml").write_text("@startuml uc\n!include plantuml-theme.puml\nactor \"User\" as u\n"
                                   "rectangle \"System\" {\n  usecase \"UC-1\\nDo it\" as uc1\n}\nu --> uc1\n@enduml\n")
        rc, out = sh("bash", PLANTUML, "--format", "svg", "--out", "svg", "architecture/diagrams/uc.puml", cwd=work)
        svg = (work / "svg" / "uc.svg").read_text() if (work / "svg" / "uc.svg").is_file() else ""
        check("a use case is drawn in the palette, not PlantUML's default grey",
              rc == 0 and "#EDF2F8" in svg and "#F1F1F1" not in svg.upper())
        (d / "broken.puml").write_text("@startuml broken\n!include no-such-theme.puml\nA -> B\n@enduml\n")
        rc, out = sh("bash", PLANTUML, "architecture/diagrams/broken.puml", "architecture/diagrams/other.puml", cwd=work)
        check("a .puml that does not compile fails the run, publishes nothing, and the others still render",
              rc != 0 and not (d / "broken.png").exists() and (d / "other.png").is_file())
        rc, out = sh("bash", PLANTUML, "architecture/diagrams/none.puml", cwd=work)
        check("no renderable input fails", rc != 0)

        rc, out = sh(sys.executable, LINT, "architecture/diagrams/ctx.puml", "architecture/diagrams/uc.puml", cwd=work)
        check("diagramlint measures PlantUML sources", rc == 0 and out.count("  OK") == 2 and "2 node(s), 1 edge(s)" in out)
        check("diagramlint leaves no file beside the source", not list(d.glob("*.svg")))

        if "mermaid" in engines:
            tree = work / "mixed"
            (tree / "diagrams").mkdir(parents=True)
            (tree / "diagrams" / "a.mmd").write_text(FLOW)
            (tree / "diagrams" / "b.puml").write_text(PUML.format(name="b"))
            rc, out = sh("bash", RENDER_ALL, "mixed", cwd=work)
            check("render-all renders both notations in one pass",
                  rc == 0 and (tree / "diagrams" / "a.png").is_file() and (tree / "diagrams" / "b.png").is_file())
            (tree / "diagrams" / "bad.puml").write_text("@startuml\n!include nope.puml\n@enduml\n")
            rc, out = sh("bash", RENDER_ALL, "mixed", cwd=work)
            check("render-all exits non-zero when any render fails", rc != 0 and "FAILED" in out)

print(f"{PASSES} passed, {FAILS} failed" + (f" ({' + '.join(engines)})" if engines else " (no renderer installed)"))
sys.exit(1 if FAILS else 0)
