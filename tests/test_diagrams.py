#!/usr/bin/env python3
"""Unit tests for tests/diagramcheck.py — the diagram regression check: pairing sources with
PNGs, the SVG layout metrics (crossings, overlaps, run-through edges, palette), the static
baseline check and the fresh-render comparison. Needs no renderer. Standard library only;
exit 0 on success."""
from __future__ import annotations

import contextlib
import copy
import io
import struct
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import diagramcheck as dc  # noqa: E402
import diagramlint as dl  # noqa: E402  (diagramcheck puts the skill's scripts on the path)

PASSES = 0
FAILS = 0


def check(name: str, cond: bool) -> None:
    global PASSES, FAILS
    if cond:
        PASSES += 1
    else:
        FAILS += 1
        print(f"FAIL  {name}")


def png(path: Path, w: int, h: int, salt: bytes = b"") -> None:
    """A file with a real PNG signature and IHDR — all the size check reads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I4sII", 13, b"IHDR", w, h) + salt)


def run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = dc.main(argv)
    return rc, out.getvalue(), err.getvalue()


def lint(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = dl.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


# --------------------------------------------------------------------------- #
# Path geometry
# --------------------------------------------------------------------------- #

check("a moveto and linetos give their points", dl.path_points("M0,0 L10,0 L10,5") == [(0, 0), (10, 0), (10, 5)])
check("pairs after a moveto are implicit linetos", dl.path_points("M 0 0 4 4 8 0") == [(0, 0), (4, 4), (8, 0)])
check("relative commands are offsets", dl.path_points("m1,1 l2,0 l0,3") == [(1, 1), (3, 1), (3, 4)])
check("H and V move along one axis", dl.path_points("M0,0 H5 V7 h-5 v-7") == [(0, 0), (5, 0), (5, 7), (0, 7), (0, 0)])
check("Z returns to the subpath start", dl.path_points("M2,3 L5,3 L5,9 Z")[-1] == (2, 3))
curve = dl.path_points("M0,0 C0,10 10,10 10,0", steps=10)
check("a cubic is sampled and ends on its end point", len(curve) == 11 and curve[-1] == (10, 0))
check("a sampled cubic bulges toward its control points", max(p[1] for p in curve) > 7)
check("a quadratic ends on its end point", dl.path_points("M0,0 Q5,10 10,0")[-1] == (10, 0))
check("a smooth cubic ends on its end point", dl.path_points("M0,0 S5,5 9,1")[-1] == (9, 1))
check("an arc becomes a chord to its end point", dl.path_points("M0,0 A5,5 0 0 1 10,0") == [(0, 0), (10, 0)])
check("negative and exponent numbers parse", dl.path_points("M-1.5,2e1 L.5-3") == [(-1.5, 20.0), (0.5, -3.0)])
check("an empty path gives no points", dl.path_points("") == [])
check("a truncated command is dropped, not raised", dl.path_points("M0,0 L5") == [(0, 0)])
check("numbers before any command are ignored", dl.path_points("5 5") == [])

# --------------------------------------------------------------------------- #
# Layout defects
# --------------------------------------------------------------------------- #

X = [[(0, 0), (100, 100)], [(0, 100), (100, 0)]]
check("two edges that cross in the open count once", dl.crossings(X, 5) == 1)
check("parallel edges do not cross", dl.crossings([[(0, 0), (100, 0)], [(0, 10), (100, 10)]], 5) == 0)
check("edges that only share an end do not cross", dl.crossings([[(0, 0), (100, 0)], [(0, 0), (100, 50)]], 5) == 0)
fan = [[(50, 0), (48, 4), (0, 100)], [(49, 0), (51, 4), (100, 100)]]
check("edges crossing right at a shared node are a fan, not a crossing", dl.crossings(fan, 10) == 0)
check("the same crossing counts when it is clear of the ends", dl.crossings(fan, 1) == 1)
check("a crossing near only ONE edge's end still counts",
      dl.crossings([[(0, 50), (100, 50)], [(50, 48), (50, 100)]], 10) == 1)
tri = [[(0, 0), (100, 100)], [(0, 100), (100, 0)], [(0, 40), (100, 40)]]
check("three mutually crossing edges are three crossings", dl.crossings(tri, 2) == 3)
check("two edges crossing twice are one crossing pair",
      dl.crossings([[(0, 0), (100, 0)], [(0, -10), (30, 10), (60, -10), (100, -10)]], 2) == 1)
check("no edges, no crossings", dl.crossings([], 5) == 0)

check("boxes that overlap count", dl.overlaps([(0, 0, 10, 10), (5, 5, 15, 15)]) == 1)
check("boxes that touch do not overlap", dl.overlaps([(0, 0, 10, 10), (10, 0, 20, 10)]) == 0)
check("a sliver under 2 % is not an overlap", dl.overlaps([(0, 0, 100, 100), (99.9, 0, 200, 100)]) == 0)
check("separate boxes do not overlap", dl.overlaps([(0, 0, 10, 10), (20, 20, 30, 30)]) == 0)
check("a box inside another overlaps it", dl.overlaps([(0, 0, 100, 100), (40, 40, 60, 60)]) == 1)

mid = (40, -10, 60, 10)
check("an edge across an unrelated node runs through it", dl.run_through([[(0, 0), (100, 0)]], [mid], 3) == 1)
check("an edge that ends at the node does not run through it", dl.run_through([[(0, 0), (50, 0)]], [mid], 3) == 0)
check("an edge that starts beside the node is attached to it", dl.run_through([[(38, 0), (100, 0)]], [mid], 3) == 0)
check("an edge that only clips a corner does not run through",
      dl.run_through([[(0, 9.5), (100, 9.5)]], [mid], 3) == 0)
check("an edge that passes clear of the node is fine", dl.run_through([[(0, 30), (100, 30)]], [mid], 3) == 0)

# --------------------------------------------------------------------------- #
# Measuring an SVG
# --------------------------------------------------------------------------- #

MERMAID = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200" class="flowchart">
<style>#g .node rect{fill:#EDF2F8;stroke:#3E6DA5;} .flowchart-link{stroke:#6B7A8D;}</style>
<g class="root" transform="translate(10, 20)">
 <g class="clusters"><g class="cluster"><rect x="0" y="0" width="380" height="160"/>
   <g class="cluster-label"><foreignObject><div xmlns="http://www.w3.org/1999/xhtml"><p>The system</p></div></foreignObject></g></g></g>
 <g class="edgePaths">
  <path class="edge-thickness-normal flowchart-link" d="M60,40 L300,120"/>
  <path class="edge-thickness-normal flowchart-link" d="M60,120 L300,40"/>
 </g>
 <g class="nodes">
  <g class="node default internal" transform="translate(30, 40)"><rect x="-30" y="-20" width="60" height="40" style="fill:#EDF2F8"/>
    <g class="label"><foreignObject><div xmlns="http://www.w3.org/1999/xhtml"><span class="nodeLabel"><p>Web App</p></span></div></foreignObject></g></g>
  <g class="node default internal" transform="translate(30, 120)"><rect x="-30" y="-20" width="60" height="40"/></g>
  <g class="node default datastore" transform="translate(330, 40)"><path d="M-30,-20 L30,-20 L30,20 L-30,20 Z"/></g>
  <g class="node default datastore" transform="translate(330, 120)"><rect x="-30" y="-20" width="60" height="40" fill="#123456"/></g>
 </g>
</g></svg>"""
m = dl.measure(MERMAID)
check("Mermaid nodes are counted", m["nodes"] == 4)
check("Mermaid edges are counted", m["edges"] == 2)
check("Mermaid clusters are counted", m["clusters"] == 1)
check("the two diagonal edges are one crossing", m["crossings"] == 1)
check("separate nodes do not overlap", m["overlaps"] == 0)
check("label text is read from HTML labels", m["words"] == 4)
check("the aspect ratio comes from the viewBox", m["aspect"] == 2.0)
check("stylesheet colours are kept apart from drawn colours",
      "#3E6DA5" in m["style_colours"] and "#3E6DA5" not in m["colours"])
check("a colour set on a shape is a drawn colour", "#123456" in m["colours"] and "#EDF2F8" in m["colours"])
check("an off-palette colour is reported", dl.off_palette(m) == ["#123456"])
check("the word hash ignores order",
      dl.measure(MERMAID.replace("<p>Web App</p>", "<p>App Web</p>"))["words_sha"] == m["words_sha"])
check("the word hash changes with the words",
      dl.measure(MERMAID.replace("Web App", "Web Application"))["words_sha"] != m["words_sha"])
moved = MERMAID.replace('transform="translate(330, 40)"', 'transform="translate(45, 50)"')
check("a node moved onto another is an overlap", dl.measure(moved)["overlaps"] == 1)
through = MERMAID.replace('<g class="nodes">',
                          '<g class="nodes"><g class="node" transform="translate(180,80)"><rect x="-30" y="-25" width="60" height="50"/></g>')
check("a node placed on the edges is run through twice", dl.measure(through)["run_through"] == 2)
check("uncrossing the edges clears the crossing",
      dl.measure(MERMAID.replace("M60,120 L300,40", "M60,120 L300,120").replace("M60,40 L300,120", "M60,40 L300,40"))["crossings"] == 0)
nested = MERMAID.replace('<g class="nodes">', '<g class="nodes"><g class="root" transform="translate(1000,0)">'
                         '<g class="node" transform="translate(30,40)"><rect x="-30" y="-20" width="60" height="40"/></g></g>')
check("nested translations are applied (no false overlap)", dl.measure(nested)["overlaps"] == 0 and dl.measure(nested)["nodes"] == 5)

PLANTUML = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" style="background:#FFFFFF;">
<g><g class="title"><text x="10" y="10" fill="#1F2933">Context diagram</text></g>
<g class="cluster"><rect x="5" y="30" width="590" height="260" fill="none" style="stroke:#9AA7B4;"/><text x="9" y="40" fill="#1F2933">Boundary</text></g>
<g class="entity"><rect x="20" y="60" width="100" height="60" fill="#EDF2F8" style="stroke:#3E6DA5;stroke-width:1.25;"/>
  <text x="30" y="80" fill="#1F2933">API</text><text x="60" y="80" fill="#1F2933">Service</text></g>
<g class="entity"><ellipse cx="450" cy="90" rx="60" ry="30" fill="#F1F1F1" style="stroke:#181818;"/><text x="420" y="90" fill="#1F2933">UC-1</text></g>
<g class="link"><path d="M120,90 C200,90 300,90 390,90" style="stroke:#6B7A8D;" fill="none"/>
  <polygon points="390,90,380,85,380,95" fill="#6B7A8D"/><text x="200" y="80" fill="#1F2933">Uses</text></g>
</g></svg>"""
p = dl.measure(PLANTUML)
check("PlantUML entities, links and clusters are counted", (p["nodes"], p["edges"], p["clusters"]) == (2, 1, 1))
check("PlantUML text is read from <text> elements", p["words"] == 7)
check("an attached edge does not run through its own nodes", p["run_through"] == 0)
check("PlantUML's default skin colours are off-palette", dl.off_palette(p) == ["#181818", "#F1F1F1"])
check("an arrowhead polygon is not an edge", p["edges"] == 1)

SEQ = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300">
<g><rect class="actor actor-top" fill="#eaeaea" stroke="#666" x="0" y="0" width="80" height="30"/><text class="actor"><tspan>Web App</tspan></text></g>
<g><rect class="actor actor-top" fill="#eaeaea" stroke="#666" x="150" y="0" width="80" height="30"/><text class="actor"><tspan>API</tspan></text></g>
<line class="messageLine0" x1="40" y1="60" x2="190" y2="60"/><text class="messageText">GET /dashboard</text>
<line class="messageLine1" x1="190" y1="90" x2="40" y2="90"/><text class="messageText">200</text></svg>"""
s = dl.measure(SEQ)
check("sequence participants and messages are counted", (s["participants"], s["messages"]) == (2, 2))
check("a sequence diagram has no graph nodes or edges", (s["nodes"], s["edges"]) == (0, 0))
check("Mermaid's overridden sequence attributes are not palette breaches", dl.off_palette(s, "mermaid") == [])
check("the same colours ARE breaches from PlantUML", dl.off_palette(s, "plantuml") == ["#666666", "#EAEAEA"])
check("text nested in tspans is read", s["words"] == 6)
check("an SVG without a viewBox has no aspect", dl.measure('<svg xmlns="http://www.w3.org/2000/svg"/>')["aspect"] == 0.0)

# ----- defects are named, so the source line to change is obvious -----
NAMED = MERMAID.replace('class="edge-thickness-normal flowchart-link" d="M60,40', 'data-id="L_web_db_0" class="flowchart-link" d="M60,40') \
               .replace('class="edge-thickness-normal flowchart-link" d="M60,120', 'id="my-svg-L_api_cache_1" class="flowchart-link" d="M60,120') \
               .replace('<g class="node default internal" transform="translate(30, 40)">',
                        '<g class="node default internal" id="my-svg-flowchart-web-0" transform="translate(30, 40)">')
n = dl.measure(NAMED)
check("a crossing names both edges from the renderer's ids",
      n["details"]["crossings"] == ["edge web_db  ×  edge api_cache #2"])
check("a Mermaid node is named by its source id",
      dl.measure(NAMED.replace('transform="translate(330, 40)"', 'transform="translate(45, 50)"'))["details"]["overlaps"][0]
      .startswith("web  overlaps"))
check("a PlantUML edge is named from → to",
      dl._edge_name(dl.ET.fromstring('<path id="user-to-spa"/>')) == "edge user → spa"
      and dl._edge_name(dl.ET.fromstring('<path id="api-backto-web-1"/>')) == "edge api → web")
check("a PlantUML node is named by its qualified name",
      dl._node_name(dl.ET.fromstring('<g data-qualified-name="sys.api" id="ent0004"/>')) == "sys.api")
check("an edge without an id is still reported", dl._edge_name(dl.ET.fromstring("<path/>")) == "edge ?")
check("details are empty for a clean diagram", all(v == [] for v in p["details"].values()))
check("the engine is recognised from the SVG",
      dl.engine_of('<svg><?plantuml 1.2026.10?></svg>') == "plantuml" and dl.engine_of(MERMAID) == "mermaid")
lines, bad = dl.report("x.svg", m, "mermaid")
check("the report lists counts, names the crossing and gives a verdict",
      bad and lines[0] == "x.svg" and any("4 node(s), 2 edge(s), 1 boundary" in ln for ln in lines)
      and any(ln.startswith("    - edge") for ln in lines) and lines[-1].startswith("  DEFECTS"))
lines, bad = dl.report("s.svg", s, "mermaid")
check("a sequence diagram reports participants, no graph defects",
      not bad and any("2 participant(s), 2 message(s)" in ln for ln in lines) and not any("crossing" in ln for ln in lines))
ribbon = dl.measure(PLANTUML.replace('viewBox="0 0 600 300"', 'viewBox="0 0 6000 300"').replace("#F1F1F1", "#EDF2F8").replace("#181818", "#3E6DA5"))
check("an extreme ribbon is a defect", dl.report("r.svg", ribbon, "plantuml")[1]
      and any("extreme ribbon" in ln for ln in dl.report("r.svg", ribbon, "plantuml")[0]))
tall = dl.measure(PLANTUML.replace('viewBox="0 0 600 300"', 'viewBox="0 0 300 3000"').replace("#F1F1F1", "#EDF2F8").replace("#181818", "#3E6DA5"))
check("a tall ribbon is a defect too", dl.report("t.svg", tall, "plantuml")[1])

# ----- text defects: labels on top of things, labels that do not fit, clipping -----
check("a label mostly hidden by a box is covered", dl.cover_pairs([(0, 0, 10, 10)], [(5, 0, 50, 10)]) == [(0, 0)])
check("a label that only touches a box is not covered", dl.cover_pairs([(0, 0, 10, 10)], [(9.5, 0, 50, 10)]) == [])
check("two labels on top of each other are one pair",
      dl.cover_pairs([(0, 0, 10, 10), (2, 2, 12, 12)], [(0, 0, 10, 10), (2, 2, 12, 12)], same=True) == [(0, 1)])
check("a label is not compared with itself", dl.cover_pairs([(0, 0, 10, 10)], [(0, 0, 10, 10)], same=True) == [])

LABEL = '''<g class="edgeLabel" transform="translate({x}, {y})"><g class="label" transform="translate(-30, -10)">
  <foreignObject width="60" height="20"><div xmlns="http://www.w3.org/1999/xhtml"><span class="edgeLabel"><p>{text}</p></span></div></foreignObject></g></g>'''
def with_labels(*labels):
    return MERMAID.replace('<g class="nodes">', "".join(LABEL.format(x=x, y=y, text=s) for x, y, s in labels) + '<g class="nodes">')

lm = dl.measure(with_labels((180, 80, "Reads rows")))
check("an edge label in the open is counted and clean", lm["edge_labels"] == 1 and lm["label_overlaps"] == 0)
lm = dl.measure(with_labels((30, 40, "Reads rows")))
check("an edge label drawn on a node is a defect, named by its text",
      lm["label_overlaps"] == 1 and lm["details"]["label_overlaps"][0].startswith('label "Reads rows"  covers node'))
lm = dl.measure(with_labels((180, 80, "SQL"), (190, 84, "RESP")))
check("two edge labels on top of each other are a defect",
      lm["label_overlaps"] == 1 and 'label "SQL"  covers  label "RESP"' in lm["details"]["label_overlaps"][0])
check("an edge without a label (zero-size box) is not a label",
      dl.measure(with_labels((180, 80, "x")).replace('width="60" height="20"', 'width="0" height="0"'))["edge_labels"] == 0)
wide = MERMAID.replace("<foreignObject>", '<foreignObject x="-80" y="-10" width="160" height="20">', 2)
om = dl.measure(wide)
check("a node label wider than its box overflows", om["overflow"] == 1 and "label does not fit its box" in om["details"]["overflow"][0])
fits = MERMAID.replace("<foreignObject>", '<foreignObject x="-25" y="-10" width="50" height="20">', 2)
check("a node label inside its box does not overflow", dl.measure(fits)["overflow"] == 0)
cm = dl.measure(MERMAID.replace('transform="translate(330, 120)"', 'transform="translate(395, 120)"'))
check("a node past the image edge is clipped", cm["clipped"] == 1 and "reaches past the image edge" in cm["details"]["clipped"][0])
check("nodes inside the viewBox are not clipped", m["clipped"] == 0 and m["overflow"] == 0 and m["label_overlaps"] == 0)
check("a viewBox that does not start at 0 is honoured",
      dl.measure(MERMAID.replace('viewBox="0 0 400 200"', 'viewBox="-50 -20 450 220"'))["clipped"] == 0)

pm = dl.measure(PLANTUML.replace('<text x="60" y="80" fill="#1F2933">Service</text>',
                                 '<text x="60" y="80" font-size="14" textLength="140" fill="#1F2933">Service</text>'))
check("PlantUML text longer than its rectangle overflows", pm["overflow"] == 1)
pm = dl.measure(PLANTUML.replace('<text x="60" y="80" fill="#1F2933">Service</text>',
                                 '<text x="60" y="80" font-size="14" textLength="40" fill="#1F2933">Service</text>'))
check("PlantUML text inside its rectangle is fine", pm["overflow"] == 0)
ACTOR = PLANTUML.replace('<g class="entity"><ellipse cx="450" cy="90" rx="60" ry="30"',
                         '<g class="entity" data-qualified-name="user"><ellipse cx="450" cy="90" rx="10" ry="10"') \
                .replace('<text x="420" y="90" fill="#1F2933">UC-1</text>',
                         '<text x="400" y="130" font-size="14" textLength="110" fill="#1F2933">Registered user</text>')
check("an actor's name below its figure is not an overflow", dl.measure(ACTOR)["overflow"] == 0)
pm = dl.measure(PLANTUML.replace('<text x="200" y="80" fill="#1F2933">Uses</text>',
                                 '<text x="40" y="95" font-size="14" textLength="60" fill="#1F2933">Uses</text>'))
check("a PlantUML link label on an entity is a defect", pm["label_overlaps"] == 1 and pm["edge_labels"] == 1)

for cls, kind in (("transition", "state"), ("relation", "class"), ("relationshipLine", "ER")):
    other = MERMAID.replace("edge-thickness-normal flowchart-link", f"edge-thickness-normal edge-pattern-solid {cls}")
    check(f"a Mermaid {kind} diagram's edges are measured", dl.measure(other)["edges"] == 2 and dl.measure(other)["crossings"] == 1)

EMPTY = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 50"><g class="section"><rect x="0" y="0" width="50" height="20"/></g></svg>'
check("an SVG with nothing recognisable is not measured", not dl.measured(dl.measure(EMPTY)) and dl.measured(m) and dl.measured(s))
lines, bad = dl.report("gantt.svg", dl.measure(EMPTY), "mermaid")
check("an unsupported diagram is reported as not measured, never as OK",
      not bad and "NOT measured" in lines[-1] and not any(ln.strip() == "OK" for ln in lines))

# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #

pal = dl.palette()
for colour in ("#EDF2F8", "#3E6DA5", "#F5EEE3", "#B07D3B", "#E7E3F3", "#6B5BA6", "#E4F0E9", "#3F7D5C",
               "#F6E4E4", "#B04A46", "#9AA7B4", "#1F2933", "#6B7A8D", "#FBF6EC"):
    check(f"{colour} is a palette colour", colour in pal)
check("the renderers' default colours are not in the palette",
      not (dl.UNTHEMED["mermaid"] | dl.UNTHEMED["plantuml"]) & pal)
check("a 3-digit colour expands to 6 digits", dl._six("#abc") == "#AABBCC" and dl._six("#ffffff") == "#FFFFFF")
check("a source with palette colours only is clean",
      dl.source_colour_errors("classDef internal fill:#EDF2F8,stroke:#3E6DA5,color:#1F2933;") == [])
check("a near-miss colour in a source is caught",
      dl.source_colour_errors("classDef note fill:#FBF7EE,stroke:#B07D3B;") == ["#FBF7EE"])
check("the PlantUML theme styles use cases (not the default grey)",
      "skinparam usecase" in (dl.ASSETS / "plantuml-theme.puml").read_text())
check("the PlantUML theme styles sequence group frames",
      "GroupBackgroundColor" in (dl.ASSETS / "plantuml-theme.puml").read_text())
check("every diagram the plugin teaches uses palette colours", dc.plugin_colour_errors() == [])

with tempfile.TemporaryDirectory() as td:
    skill = Path(td) / "skills" / "x" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# X\n\n```mermaid\nflowchart LR\n  a --> b\n  classDef hot fill:#FF0000;\n```\n\n"
                     "Colour `#00FF00` in prose is fine.\n\n```plantuml\nskinparam x #EDF2F8\n```\n")
    errs = dc.plugin_colour_errors(Path(td))
    check("an off-palette colour in a skill's diagram is caught, with its line",
          len(errs) == 1 and ":3: mermaid block" in errs[0] and "#FF0000" in errs[0])

# --------------------------------------------------------------------------- #
# Pairing sources with PNGs
# --------------------------------------------------------------------------- #

with tempfile.TemporaryDirectory() as td:
    ex = Path(td) / "examples" / "demo"
    (ex / "diagrams").mkdir(parents=True)
    (ex / "docs" / "diagrams").mkdir(parents=True)
    (ex / "diagrams" / "uc.mmd").write_text("flowchart LR\n  a --> b\n")
    png(ex / "diagrams" / "uc.png", 4800, 900)
    (ex / "diagrams" / "ctx.puml").write_text("@startuml\nA -> B\n@enduml\n")
    png(ex / "diagrams" / "ctx.png", 1200, 900)
    doc = ex / "docs" / "view.md"
    doc.write_text("# View\n\n```mermaid\nflowchart TB\n  %% name: my view!\n  x --> y\n```\n\n"
                   "![named](diagrams/my-view-.png)\n\n```mermaid\nflowchart TB\n  p --> q\n```\n\n"
                   "Some prose between the block and its image.\n\n![numbered](diagrams/view-02.png)\n\n"
                   "```mermaid\nflowchart LR\n  a --> b\n```\n\n![has a source file](../diagrams/uc.png)\n")
    png(ex / "docs" / "diagrams" / "my-view-.png", 4800, 2000)
    png(ex / "docs" / "diagrams" / "view-02.png", 4800, 2000)

    blocks = dc.mermaid_blocks(doc)
    check("a block is named by its `%% name:` slug, sanitised", blocks[0][0] == "my-view-")
    check("an unnamed block is numbered in document order", [b[0] for b in blocks[1:]] == ["view-02", "view-03"])
    diagrams, errs = dc.discover(ex)
    refs = {d.png.name: d for d in diagrams}
    check("every PNG is paired with a source", len(diagrams) == 4 and errs == [])
    check("a .mmd beside the PNG is its source", refs["uc.png"].ref.endswith("diagrams/uc.mmd") and refs["uc.png"].engine == "mermaid")
    check("a .puml beside the PNG is its source", refs["ctx.png"].engine == "plantuml")
    check("a Markdown block is the source when there is no .mmd",
          refs["my-view-.png"].ref.endswith("docs/view.md#my-view-") and "x --> y" in refs["my-view-.png"].source)
    check("the image line need not follow the block directly", "p --> q" in refs["view-02.png"].source)
    check("a block whose PNG has a .mmd defers to the .mmd", refs["uc.png"].source == "flowchart LR\n  a --> b\n")

    copy_doc = ex / "reports" / "all.md"
    copy_doc.parent.mkdir()
    copy_doc.write_text("```mermaid\nflowchart TB\n  %% name: my view!\n  x --> y\n```\n\n![same](../docs/diagrams/my-view-.png)\n")
    check("the same block in a second document is not a conflict", dc.discover(ex)[1] == [])
    copy_doc.write_text("```mermaid\nflowchart TB\n  %% name: my view!\n  x --> z\n```\n\n![same](../docs/diagrams/my-view-.png)\n")
    errs = dc.discover(ex)[1]
    check("two different blocks for one PNG are reported", len(errs) == 1 and "differs from the one in" in errs[0])
    copy_doc.unlink()

    png(ex / "diagrams" / "orphan.png", 100, 100)
    check("a PNG without a source is reported", any("orphan.png: no diagram source" in e for e in dc.discover(ex)[1]))
    (ex / "diagrams" / "orphan.png").unlink()
    (ex / "diagrams" / "new.puml").write_text("@startuml\n@enduml\n")
    d2, errs = dc.discover(ex)
    check("a source without a PNG is reported and left out", any("no rendered PNG" in e for e in errs) and len(d2) == 4)
    (ex / "diagrams" / "new.puml").unlink()

    # ----- static check against a baseline built from this tree -----
    metrics = {**{k: 0 for k in dc.STRUCTURE}, **{k: 0 for k, _ in dl.DEFECTS}, "colours": [], "words_sha": "x"}
    base = {d.key: dc.entry(d, metrics) for d in diagrams}
    check("a tree that matches its baseline is clean", dc.static_errors(diagrams, base) == [])
    check("an entry records the PNG's size", base[refs["uc.png"].key]["width"] == 4800 and base[refs["uc.png"].key]["height"] == 900)

    (ex / "diagrams" / "uc.mmd").write_text("flowchart LR\n  a --> c\n")
    errs = dc.static_errors(dc.discover(ex)[0], base)
    check("a source edited without a re-render is a stale render", len(errs) == 1 and "the render is stale" in errs[0])
    png(ex / "diagrams" / "uc.png", 4800, 900, b"new")
    errs = dc.static_errors(dc.discover(ex)[0], base)
    check("source and PNG both changed: the baseline needs updating", len(errs) == 1 and "and its PNG changed" in errs[0])
    (ex / "diagrams" / "uc.mmd").write_text("flowchart LR\n  a --> b\n")
    errs = dc.static_errors(dc.discover(ex)[0], base)
    check("a PNG changed without its source is caught", len(errs) == 1 and "PNG changed but its source did not" in errs[0])
    png(ex / "diagrams" / "uc.png", 4800, 900)
    check("restoring both clears the errors", dc.static_errors(dc.discover(ex)[0], base) == [])

    doc.write_text(doc.read_text().replace("p --> q", "p --> r"))
    errs = dc.static_errors(dc.discover(ex)[0], base)
    check("editing a Markdown-only block makes its PNG stale", len(errs) == 1 and "view-02.png" in errs[0] and "stale" in errs[0])
    doc.write_text(doc.read_text().replace("p --> r", "p --> q"))

    fewer = {k: v for k, v in base.items() if not k.endswith("ctx.png")}
    check("a PNG missing from the baseline is reported",
          any("not in the baseline" in e for e in dc.static_errors(diagrams, fewer)))
    extra = {**base, "examples/demo/gone.png": base[refs["uc.png"].key]}
    check("a baseline entry without a PNG is reported",
          any("no longer in examples/" in e for e in dc.static_errors(diagrams, extra)))

    low = copy.deepcopy(base)
    png(ex / "diagrams" / "uc.png", 1600, 300)
    low[refs["uc.png"].key].update(png_sha=dl.sha((ex / "diagrams" / "uc.png").read_bytes()), width=1600, height=300)
    check("a Mermaid PNG rendered at low scale is below the floor",
          any("high-resolution floor" in e for e in dc.static_errors(diagrams, low)))
    png(ex / "diagrams" / "uc.png", 4800, 900)
    png(ex / "diagrams" / "ctx.png", 500, 400)
    low = copy.deepcopy(base)
    low[refs["ctx.png"].key].update(png_sha=dl.sha((ex / "diagrams" / "ctx.png").read_bytes()), width=500, height=400)
    check("a PlantUML PNG at 96 dpi size is below the floor",
          any("850 px high-resolution floor" in e for e in dc.static_errors(diagrams, low)))
    png(ex / "diagrams" / "ctx.png", 1200, 900)

    dirty = copy.deepcopy(base)
    dirty[refs["ctx.png"].key]["off_palette"] = ["#F1F1F1"]
    check("a baseline may not accept off-palette colours",
          any("outside the SEI palette: #F1F1F1" in e for e in dc.static_errors(diagrams, dirty)))
    (ex / "diagrams" / "ctx.puml").write_text("@startuml\nskinparam x #ABCDEF\nA -> B\n@enduml\n")
    d3 = dc.discover(ex)[0]
    b3 = {d.key: dc.entry(d, metrics) for d in d3}
    check("a source that sets an off-palette colour is caught",
          any("sets colour(s) outside the SEI palette: #ABCDEF" in e for e in dc.static_errors(d3, b3)))
    (ex / "diagrams" / "ctx.puml").write_text("@startuml\nA -> B\n@enduml\n")

    crossed = copy.deepcopy(base)
    crossed[refs["uc.png"].key]["crossings"] = 1
    check("an accepted crossing is a note, not a failure",
          dc.static_errors(diagrams, crossed) == [] and len(dc.accepted_defects(crossed)) == 1)

    # ----- fresh-render comparison -----
    def fresh(**over):
        out = {**metrics, "style_colours": sorted(dl.MERMAID_THEME_MARKS), "aspect": 0.0}
        out.update(over)
        return out

    key = refs["uc.png"].key
    only = [refs["uc.png"]]
    check("a render identical to the baseline is clean", dc.render_errors(only, base, {key: fresh()}) == [])
    for field in ("nodes", "edges", "clusters", "participants", "messages", "words"):
        check(f"a different {field} count fails",
              any(f"{field} = 3" in e for e in dc.render_errors(only, base, {key: fresh(**{field: 3})})))
    check("different words fail", any("words_sha" in e for e in dc.render_errors(only, base, {key: fresh(words_sha="y")})))
    for field, label in dl.DEFECTS:
        check(f"more {field} than approved fails",
              any(label in e for e in dc.render_errors(only, base, {key: fresh(**{field: 1})})))
        check(f"fewer {field} than approved passes",
              dc.render_errors(only, crossed if field == "crossings" else base, {key: fresh()}) == [])
    check("an accepted crossing does not fail a render that still has it",
          dc.render_errors(only, crossed, {key: fresh(crossings=1)}) == [])
    check("a second crossing on top of an accepted one fails",
          any("2 edge crossing" in e for e in dc.render_errors(only, crossed, {key: fresh(crossings=2)})))
    check("a new off-palette colour fails",
          any("outside the SEI palette: #ABCDEF" in e for e in dc.render_errors(only, base, {key: fresh(colours=["#ABCDEF"])})))
    check("Mermaid's default theme in the stylesheet fails",
          any("theme was not applied" in e for e in
              dc.render_errors(only, base, {key: fresh(style_colours=["#ECECFF", "#9370DB"])})))
    check("a Mermaid stylesheet without the SEI colours fails",
          any("theme was not applied" in e for e in dc.render_errors(only, base, {key: fresh(style_colours=[])})))
    pkey = refs["ctx.png"].key
    check("PlantUML's default skin on a shape fails",
          any("theme was not applied" in e for e in
              dc.render_errors([refs["ctx.png"]], base, {pkey: fresh(colours=["#f1f1f1"], style_colours=[])})))
    check("a PlantUML render needs no stylesheet colours",
          dc.render_errors([refs["ctx.png"]], base, {pkey: fresh(style_colours=[])}) == [])
    seq = copy.deepcopy(base)
    seq[key].update(participants=4, messages=7)
    check("a renderer that does not tag sequence participants is not a structure change",
          dc.render_errors(only, seq, {key: fresh()}) == [])
    check("a sequence diagram that lost a message still fails",
          any("messages = 6" in e for e in dc.render_errors(only, seq, {key: fresh(participants=4, messages=6)})))
    check("the same shape within tolerance passes", dc.render_errors(only, base, {key: fresh(aspect=4800 / 900 * 1.2)}) == [])
    check("a render that changed shape fails",
          any("changed shape" in e for e in dc.render_errors(only, base, {key: fresh(aspect=1.0)})))
    check("a failed render is reported with its text",
          dc.render_errors(only, base, {key: "x.mmd: render failed\nParse error"}) == ["x.mmd: render failed\nParse error"])
    check("a diagram outside the baseline is left to the static check",
          dc.render_errors(only, {}, {key: fresh(nodes=9)}) == [])

    svg = Path(td) / "one.svg"
    svg.write_text(MERMAID)
    rc, out, _ = lint(str(svg))
    check("diagramlint exits 1 on a defect and names the crossing edges",
          rc == 1 and "edge crossing(s): 1" in out and "DEFECTS" in out)
    clean = Path(td) / "clean.svg"
    clean.write_text(PLANTUML.replace("#F1F1F1", "#EDF2F8").replace("#181818", "#3E6DA5"))
    rc, out, _ = lint(str(clean))
    check("diagramlint exits 0 on a clean diagram", rc == 0 and out.rstrip().endswith("OK") and "palette: none" in out)
    rc, out, _ = lint(str(clean), str(svg))
    check("several files are reported in order; one defect fails the run",
          rc == 1 and out.index("clean.svg") < out.index("one.svg"))
    check("a missing file exits 2", lint(str(Path(td) / "none.svg"))[0] == 2)
    other = Path(td) / "x.txt"
    other.write_text("hello")
    check("an unsupported file type exits 2", lint(str(other))[0] == 2 and "expected a .svg" in lint(str(other))[2])
    broken = Path(td) / "broken.svg"
    broken.write_text("<svg><g></svg>")
    check("malformed SVG exits 2, not a traceback", lint(str(broken))[0] == 2 and "not well-formed" in lint(str(broken))[2])
    gantt = Path(td) / "gantt.svg"
    gantt.write_text(EMPTY)
    rc, out, _ = lint(str(gantt))
    check("an unsupported diagram type exits 2 and says so", rc == 2 and "NOT measured" in out)
    check("a defect outranks an unsupported file in the exit code", lint(str(gantt), str(svg))[0] == 1)
    check("no arguments exits 2 with the usage", lint()[0] == 2 and "diagramlint.py FILE" in lint()[1])
    check("--help exits 0", lint("--help")[0] == 0)

# ----- the patterns a skill teaches -----
with tempfile.TemporaryDirectory() as td:
    tpl = Path(td) / "templates" / "t.md"
    tpl.parent.mkdir(parents=True)
    tpl.write_text("# T\n\n```mermaid\nflowchart LR\n  a[\"<SystemName><br/><i>tech</i>\"] --> b\n```\n\n"
                   "```plantuml\n@startuml\nA ..> B : <<include>>\n@enduml\n```\n\n```bash\necho no\n```\n")
    for sub in ("skills", "references", "commands"):
        (Path(td) / sub).mkdir()
    found = dc.taught(Path(td))
    check("every fenced diagram is a taught pattern; other fences are not", [d.engine for d in found] == ["mermaid", "plantuml"])
    check("a pattern is named by its file and line", found[0].ref.endswith("templates/t.md:3") and found[1].ref.endswith(":8"))
    check("a <placeholder> becomes plain words; <br/>, <i> and <<stereotypes>> stay",
          'a["SystemName<br/><i>tech</i>"]' in found[0].source and "<<include>>" in found[1].source)
    ok_m = {**metrics, "details": {k: [] for k, _ in dl.DEFECTS}, "nodes": 2, "participants": 0, "colours": []}
    k0 = found[0].key
    check("a clean pattern passes", dc.pattern_errors(found[:1], {k0: ok_m}) == [])
    check("a pattern that does not compile fails", dc.pattern_errors(found[:1], {k0: "t.md:3: render failed"}) == ["t.md:3: render failed"])
    bad_m = {**ok_m, "crossings": 1, "details": {**ok_m["details"], "crossings": ["edge a_b  ×  edge c_d"]}}
    check("a pattern with a crossing fails and names it",
          any("1 edge crossing(s): edge a_b" in e for e in dc.pattern_errors(found[:1], {k0: bad_m})))
    check("a pattern with an off-palette colour fails",
          any("outside the SEI palette: #ABCDEF" in e for e in dc.pattern_errors(found[:1], {k0: {**ok_m, "colours": ["#ABCDEF"]}})))
    check("a pattern that renders nothing measurable fails",
          any("nothing diagramlint.py can measure" in e for e in dc.pattern_errors(found[:1], {k0: {**ok_m, "nodes": 0}})))
    c4 = dc.Diagram(tpl, "mermaid", "C4Context\n  Person(u, \"User\")\n", "t.md:1")
    check("Mermaid's native C4 sketch is exempt from the palette only",
          dc.pattern_errors([c4], {c4.key: {**ok_m, "colours": ["#08427B"]}}) == []
          and dc.pattern_errors([c4], {c4.key: {**bad_m, "colours": ["#08427B"]}}) != [])
patterns = dc.taught()
check("the plugin teaches patterns in both notations",
      sum(d.engine == "mermaid" for d in patterns) >= 15 and sum(d.engine == "plantuml" for d in patterns) >= 4)
check("every taught pattern has a distinct reference", len({d.ref for d in patterns}) == len(patterns))

check("an unknown option exits 2", run(["--bogus"])[0] == 2)
check("an unknown engine exits 2", run(["--render", "graphviz"])[0] == 2)
def _raises() -> bool:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "x.png"
        f.write_bytes(b"not a png at all, just text padding....")
        try:
            dc.png_size(f)
        except ValueError:
            return True
        return False


check("png_size raises on a non-PNG", _raises())

# --------------------------------------------------------------------------- #
# The repository's own examples and baseline
# --------------------------------------------------------------------------- #

diagrams, errs = dc.discover()
baseline = dc.load_baseline()
check("every example PNG has a source", errs == [])
check("the baseline covers exactly the example PNGs", sorted(baseline) == [d.key for d in diagrams])
check("the committed examples match the baseline", dc.static_errors(diagrams, baseline) == [])
by_engine = {e: [d for d in diagrams if d.engine == e] for e in ("mermaid", "plantuml")}
check("both examples carry the same number of diagrams",
      len(by_engine["mermaid"]) == len(by_engine["plantuml"]) > 0)
check("each example's PNGs sit in its own notation's directory",
      all(f"-{d.engine}/" in d.key for d in diagrams))
check("every Mermaid PNG is rendered at scale 3 (4800 px on its longer side)",
      all(max(dc.png_size(d.png)) == 4800 for d in by_engine["mermaid"]))
check("every PlantUML PNG is at least as large as a 240 dpi render",
      all(max(dc.png_size(d.png)) >= dc.MIN_LONG_SIDE["plantuml"] for d in by_engine["plantuml"]))
check("no approved render overlaps nodes or runs an edge through one",
      all(b["overlaps"] == 0 and b["run_through"] == 0 for b in baseline.values()))
check("no approved render uses an off-palette colour", all(b["off_palette"] == [] for b in baseline.values()))
check("no approved render has an edge crossing", all(b["crossings"] == 0 for b in baseline.values()))
check("the baseline accepts no layout defect at all", dc.accepted_defects(baseline) == [])
check("every graph diagram in the baseline has nodes and edges (a legend has nodes only)",
      all(b["nodes"] and (b["edges"] or k.endswith("/legend.png"))
          for k, b in baseline.items() if not b["participants"]))
check("every sequence diagram in the baseline has participants and messages",
      all(b["messages"] for b in baseline.values() if b["participants"]))
check("every approved render shows text", all(b["words"] > 0 for b in baseline.values()))
check("baseline keys are repo-relative paths without '..'", all(".." not in k and k.startswith("examples/") for k in baseline))
import json  # noqa: E402
import subprocess  # noqa: E402

listed = subprocess.run(["bash", str(ROOT / "scripts" / "render-all.sh"), "--list", "examples"],
                        cwd=ROOT, capture_output=True, text=True)
targets = sorted(dc._rel(ROOT / ln.split(" -> ")[1]) for ln in listed.stdout.splitlines() if " -> " in ln)
check("render-all.sh would render every example PNG — embedded Mermaid blocks included",
      listed.returncode == 0 and targets == [d.key for d in diagrams])
pkg = json.loads((ROOT / "skills/sei-diagrams/package.json").read_text())["dependencies"]
setup = (ROOT / "skills/sei-diagrams/scripts/setup.sh").read_text()
check("setup.sh's fallback package.json pins the same renderer versions as package.json",
      all(f'"{name}": "{version}"' in setup for name, version in pkg.items()))
lock = json.loads((ROOT / "skills/sei-diagrams/package-lock.json").read_text())["packages"]
check("the lockfile satisfies package.json's renderer versions",
      all(lock[f"node_modules/{name}"]["version"].split(".")[0] == version.lstrip("^~").split(".")[0]
          and tuple(map(int, lock[f"node_modules/{name}"]["version"].split(".")))
          >= tuple(map(int, version.lstrip("^~").split("."))) for name, version in pkg.items()))

stems = {e: {Path(d.key).stem for d in by_engine[e]} for e in by_engine}
check("both examples draw the same set of diagrams, under the same names", stems["mermaid"] == stems["plantuml"])

print(f"{PASSES} passed, {FAILS} failed")
sys.exit(1 if FAILS else 0)
