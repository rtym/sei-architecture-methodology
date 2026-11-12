#!/usr/bin/env python3
"""Measure a rendered diagram's layout: count what the eye is asked to check. Standard library only.

  diagramlint.py FILE [FILE …]      FILE is a rendered .svg, or a .mmd / .puml source (rendered
                                    to SVG first with this skill's render scripts)

For each diagram it prints the elements it found and four defects, each named so it can be fixed:

  crossings     pairs of edges that cross away from a node they share
  overlaps      pairs of nodes whose boxes overlap
  run-through   edges drawn across a node they do not connect to
  label cover   edge labels drawn on top of a node or of another edge label
  overflow      node labels wider or taller than their box
  clipped       nodes or labels that reach past the image edge
  off-palette   colours on shapes that the SEI palette does not define

and warns when the image is an extreme ribbon (longer side over 8× the shorter). It measures
Mermaid flowchart, state, class and ER diagrams and PlantUML component / use case / class / C4
diagrams. A sequence diagram has no graph layout, so only its colours and shape are checked. For
any other diagram type it says the layout was not measured and exits 2, instead of reporting a
clean result it did not check. The check does not replace opening the PNG — it cannot tell a
wrong arrow or a missing element — it makes the counts numbers instead of impressions.

Exit codes: 0 no defects, 1 defects found, 2 usage error, missing file, missing renderer or a
diagram type whose layout it cannot measure.
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ASSETS = SCRIPTS.parent / "assets"
RENDERERS = {".mmd": SCRIPTS / "render.sh", ".mermaid": SCRIPTS / "render.sh", ".puml": SCRIPTS / "render-plantuml.sh"}

HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")
# Colours a renderer draws on its own (arrowheads, page background) — never a palette breach.
NEUTRAL = {"#000000", "#FFFFFF"}
# What an unthemed render looks like: Mermaid's default theme and PlantUML's default skin.
UNTHEMED = {"mermaid": {"#ECECFF", "#9370DB"},
            "plantuml": {"#F1F1F1", "#181818", "#FEFECE", "#A80036", "#EEEEEE"}}
# A themed Mermaid render carries these in its stylesheet (node fill, node border, edge line).
MERMAID_THEME_MARKS = {"#EDF2F8", "#3E6DA5", "#6B7A8D"}
# Fill/stroke attributes Mermaid writes on sequence-diagram shapes and then overrides from its
# stylesheet (where the theme lives), so they are never what is drawn.
MERMAID_INERT = {"#EAEAEA", "#666666", "#999999"}
MAX_ASPECT = 8.0            # longer side / shorter side; beyond this the diagram is a ribbon
DEFECTS = (("crossings", "edge crossing(s)"), ("overlaps", "overlapping node pair(s)"),
           ("run_through", "edge(s) drawn through an unrelated node"),
           ("label_overlaps", "edge label(s) on top of a node or another label"),
           ("overflow", "label(s) wider or taller than their box"),
           ("clipped", "element(s) cut off at the image edge"))


def sha(text: str | bytes) -> str:
    import hashlib
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# SVG geometry
# --------------------------------------------------------------------------- #

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_TOKEN = re.compile(rf"[MmLlHhVvCcSsQqTtAaZz]|{_NUM}")
_ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def path_points(d: str, steps: int = 12) -> list[tuple[float, float]]:
    """The polyline a path's `d` attribute draws; curves are sampled, arcs become chords."""
    pts: list[tuple[float, float]] = []
    tokens = _TOKEN.findall(d)
    i, cmd = 0, ""
    x = y = sx = sy = 0.0
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
        elif not cmd:
            break
        up = cmd.upper()
        n = _ARGS[up]
        if up == "Z":
            x, y = sx, sy
            pts.append((x, y))
            continue
        if i + n > len(tokens) or any(t.isalpha() for t in tokens[i:i + n]):
            break
        a = [float(t) for t in tokens[i:i + n]]
        i += n
        rel = cmd.islower()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if up == "M":
            x, y = a[0] + ox, a[1] + oy
            sx, sy = x, y
            pts.append((x, y))
            cmd = "l" if rel else "L"       # further pairs after a moveto are linetos
        elif up == "L" or up == "T":
            x, y = a[0] + ox, a[1] + oy
            pts.append((x, y))
        elif up == "H":
            x = a[0] + ox
            pts.append((x, y))
        elif up == "V":
            y = a[0] + oy
            pts.append((x, y))
        elif up == "A":
            x, y = a[5] + ox, a[6] + oy
            pts.append((x, y))
        else:                               # C, S, Q: sample the Bézier
            ctrl = [(a[k] + ox, a[k + 1] + oy) for k in range(0, n, 2)]
            if up == "Q":
                c1 = c2 = ctrl[0]
            elif up == "S":
                c1, c2 = (x, y), ctrl[0]
            else:
                c1, c2 = ctrl[0], ctrl[1]
            ex, ey = ctrl[-1]
            for s in range(1, steps + 1):
                t = s / steps
                u = 1 - t
                pts.append((u ** 3 * x + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * ex,
                            u ** 3 * y + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * ey))
            x, y = ex, ey
    return pts


def _translate(el: ET.Element) -> tuple[float, float]:
    m = re.search(rf"translate\(\s*({_NUM})[\s,]*({_NUM})?", el.get("transform", ""))
    return (float(m.group(1)), float(m.group(2) or 0)) if m else (0.0, 0.0)


def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _classes(el: ET.Element) -> set[str]:
    return set(el.get("class", "").split())


def _f(el: ET.Element, name: str) -> float:
    m = re.match(_NUM, el.get(name, "0").strip())
    return float(m.group(0)) if m else 0.0


def _shape_points(el: ET.Element) -> list[tuple[float, float]]:
    tag = _tag(el)
    if tag == "rect":
        x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
        return [(x, y), (x + w, y + h)]
    if tag == "circle":
        cx, cy, r = _f(el, "cx"), _f(el, "cy"), _f(el, "r")
        return [(cx - r, cy - r), (cx + r, cy + r)]
    if tag == "ellipse":
        cx, cy, rx, ry = _f(el, "cx"), _f(el, "cy"), _f(el, "rx"), _f(el, "ry")
        return [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    if tag in ("polygon", "polyline"):
        nums = [float(n) for n in re.findall(_NUM, el.get("points", ""))]
        return list(zip(nums[0::2], nums[1::2]))
    if tag == "path":
        return path_points(el.get("d", ""), steps=4)
    return []


NODE_CLASSES = {"node", "entity"}                       # Mermaid flowchart, PlantUML
# Mermaid: the class sits on the <path> — flowchart, state, class and ER diagrams
EDGE_PATH_CLASSES = {"flowchart-link", "transition", "relation", "relationshipLine"}
EDGE_GROUP_CLASSES = {"link"}                           # PlantUML: a <g> holding path + arrowhead
PARTICIPANT_CLASSES = {"actor-top", "participant-head"}  # sequence diagrams
MESSAGE_CLASSES = {"messageLine0", "messageLine1", "message"}
LABEL_CLASSES = {"label", "cluster-label", "edgeLabel", "nodeLabel"}


def measure(svg: str) -> dict:
    """Layout metrics of one rendered SVG (Mermaid or PlantUML)."""
    root = ET.fromstring(svg)
    nodes: list[tuple[float, float, float, float]] = []
    edges: list[list[tuple[float, float]]] = []
    node_names: list[str] = []
    edge_names: list[str] = []
    counts = {"clusters": 0, "participants": 0, "messages": 0}
    labels: list[tuple[float, float, float, float]] = []     # edge-label boxes
    label_names: list[str] = []
    overflow: list[str] = []
    words: list[str] = []
    colours: set[str] = set()

    def bbox_of(el: ET.Element, tx: float, ty: float) -> tuple[float, float, float, float] | None:
        pts: list[tuple[float, float]] = []

        def collect(e: ET.Element, ox: float, oy: float) -> None:
            if _classes(e) & LABEL_CLASSES or _tag(e) in ("foreignObject", "text"):
                return
            dx, dy = _translate(e)
            ox, oy = ox + dx, oy + dy
            pts.extend((px + ox, py + oy) for px, py in _shape_points(e))
            for c in e:
                collect(c, ox, oy)

        for c in el:
            collect(c, tx, ty)
        if not pts:
            return None
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    def text_boxes(el: ET.Element, tx: float, ty: float) -> list[tuple[float, float, float, float]]:
        """Boxes of the text drawn under `el`: Mermaid HTML labels (foreignObject) and SVG <text>
        that states its length (PlantUML)."""
        out = []
        dx, dy = _translate(el)
        tx, ty = tx + dx, ty + dy
        tag = _tag(el)
        if tag == "foreignObject":
            w, h = _f(el, "width"), _f(el, "height")
            if w > 0 and h > 0:
                x, y = _f(el, "x") + tx, _f(el, "y") + ty
                out.append((x, y, x + w, y + h))
            return out
        if tag == "text" and el.get("textLength"):
            x, y, w, size = _f(el, "x") + tx, _f(el, "y") + ty, _f(el, "textLength"), _f(el, "font-size") or 14.0
            out.append((x, y - 0.8 * size, x + w, y + 0.2 * size))
            return out
        for c in el:
            out.extend(text_boxes(c, tx, ty))
        return out

    def union(boxes):
        return (min(b[0] for b in boxes), min(b[1] for b in boxes),
                max(b[2] for b in boxes), max(b[3] for b in boxes)) if boxes else None

    def said(el: ET.Element) -> str:
        return " ".join(" ".join(el.itertext()).split())[:40] or "?"

    def walk(el: ET.Element, tx: float, ty: float, in_node: bool) -> None:
        tag, cls = _tag(el), _classes(el)
        if tag in ("style", "defs", "marker", "title", "desc"):
            return
        dx, dy = _translate(el)
        tx, ty = tx + dx, ty + dy
        for attr in ("fill", "stroke"):
            colours.update(c.upper() for c in HEX_RE.findall(el.get(attr, "")))
        colours.update(c.upper() for c in HEX_RE.findall(el.get("style", "")))
        if el.text and el.text.strip():
            words.extend(el.text.split())
        if tag == "g" and cls & NODE_CLASSES and not in_node:
            box = bbox_of(el, tx, ty)
            if box:
                nodes.append(box)
                node_names.append(_node_name(el))
                # a label must fit its box; only boxes are checked (an actor's name sits below it)
                boxed = any(_tag(e) == "rect" for e in el.iter()) or "data-qualified-name" not in el.attrib
                text = union([b for c in el for b in text_boxes(c, tx, ty)])
                slack = 0.04 * max(box[2] - box[0], box[3] - box[1]) + 2
                if boxed and text and (text[0] < box[0] - slack or text[2] > box[2] + slack
                                       or text[1] < box[1] - slack or text[3] > box[3] + slack):
                    overflow.append(f"{_node_name(el)}  label does not fit its box")
            in_node = True
        elif tag == "path" and cls & EDGE_PATH_CLASSES:
            pts = [(x + tx, y + ty) for x, y in path_points(el.get("d", ""))]
            if len(pts) >= 2:
                edges.append(pts)
                edge_names.append(_edge_name(el))
        elif tag == "g" and cls & EDGE_GROUP_CLASSES:
            for c in el:
                if _tag(c) == "path":
                    pts = [(x + tx, y + ty) for x, y in path_points(c.get("d", ""))]
                    if len(pts) >= 2:
                        edges.append(pts)
                        edge_names.append(_edge_name(c))
                    break
            box = union([b for c in el for b in text_boxes(c, tx, ty)])
            if box:
                labels.append(box)
                label_names.append(f'label "{said(el)}"')
        elif tag == "g" and "edgeLabel" in cls:
            box = union([b for c in el for b in text_boxes(c, tx, ty)])
            if box:
                labels.append(box)
                label_names.append(f'label "{said(el)}"')
        if cls & {"cluster"}:
            counts["clusters"] += 1
        if cls & PARTICIPANT_CLASSES:
            counts["participants"] += 1
        if cls & MESSAGE_CLASSES:
            counts["messages"] += 1
        for c in el:
            walk(c, tx, ty, in_node)
            if c.tail and c.tail.strip():
                words.extend(c.tail.split())

    walk(root, 0.0, 0.0, False)
    box = [float(n) for n in re.findall(_NUM, root.get("viewBox", ""))]
    width, height = (box[2], box[3]) if len(box) == 4 else (0.0, 0.0)
    near = 0.02 * math.hypot(width, height) if width and height else 10.0
    style = " ".join(e.text or "" for e in root.iter() if _tag(e) == "style")
    crossed = crossing_pairs(edges, near)
    overlapped = overlap_pairs(nodes)
    through = run_through_pairs(edges, nodes, near)
    covered = [f"{label_names[i]}  covers node  {node_names[j]}" for i, j in cover_pairs(labels, nodes)] + \
              [f"{label_names[i]}  covers  {label_names[j]}" for i, j in cover_pairs(labels, labels, same=True)]
    clipped = []
    if len(box) == 4:
        edge = 0.01 * max(width, height)
        for name, (x0, y0, x1, y1) in [*zip(node_names, nodes), *zip(label_names, labels)]:
            if x0 < box[0] - edge or y0 < box[1] - edge or x1 > box[0] + width + edge or y1 > box[1] + height + edge:
                clipped.append(f"{name}  reaches past the image edge")
    return {
        "nodes": len(nodes), "edges": len(edges), "edge_labels": len(labels), **counts,
        "words": len(words), "words_sha": sha(" ".join(sorted(words))),
        "crossings": len(crossed),
        "overlaps": len(overlapped),
        "run_through": len(through),
        "label_overlaps": len(covered),
        "overflow": len(overflow),
        "clipped": len(clipped),
        "details": {
            "label_overlaps": covered,
            "overflow": overflow,
            "clipped": clipped,
            "crossings": [f"{edge_names[i]}  ×  {edge_names[j]}" for i, j in crossed],
            "overlaps": [f"{node_names[i]}  overlaps  {node_names[j]}" for i, j in overlapped],
            "run_through": [f"{edge_names[i]}  crosses node  {node_names[j]}" for i, j in through],
        },
        "colours": sorted(colours),
        "style_colours": sorted({c.upper() for c in HEX_RE.findall(style)}),
        "aspect": round(width / height, 3) if height else 0.0,
    }


def _node_name(el: ET.Element) -> str:
    """The source's own name for a node: PlantUML's qualified name, Mermaid's node id."""
    name = el.get("data-qualified-name") or el.get("data-id")
    if name:
        return name
    m = re.search(r"flowchart-(.+)-\d+$", el.get("id", ""))
    return m.group(1) if m else el.get("id", "?")


def _edge_name(el: ET.Element) -> str:
    """`from → to` when the renderer recorded it: Mermaid `L_<from>_<to>_<n>`, PlantUML `<from>-to-<to>`."""
    ident = el.get("data-id") or el.get("id", "")
    m = re.match(r"(?:.*-)?L_(.+)_(\d+)$", ident)
    if m:
        return f"edge {m.group(1)}" + (f" #{int(m.group(2)) + 1}" if m.group(2) != "0" else "")
    m = re.match(r"(.+?)-(?:to|backto)-(.+?)(?:-\d+)?$", ident)
    if m:
        return f"edge {m.group(1)} → {m.group(2)}"
    return f"edge {ident or '?'}"


def _segments_cross(p1, p2, p3, p4) -> tuple[float, float] | None:
    """The point where segments p1p2 and p3p4 properly cross, or None."""
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if 0 < t < 1 and 0 < u < 1:
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    return None


def crossings(edges, near: float) -> int:
    return len(crossing_pairs(edges, near))


def overlaps(nodes) -> int:
    return len(overlap_pairs(nodes))


def run_through(edges, nodes, near: float) -> int:
    return len(run_through_pairs(edges, nodes, near))


def cover_pairs(labels, boxes, same: bool = False) -> list[tuple[int, int]]:
    """(label, box) pairs where the box hides more than 15 % of the label. With `same`, the boxes
    are the labels themselves and each pair is reported once."""
    pairs = []
    for i, a in enumerate(labels):
        area = (a[2] - a[0]) * (a[3] - a[1])
        for j, b in enumerate(boxes):
            if same and j <= i:
                continue
            w = min(a[2], b[2]) - max(a[0], b[0])
            h = min(a[3], b[3]) - max(a[1], b[1])
            small = min(area, (b[2] - b[0]) * (b[3] - b[1])) if same else area
            if w > 0 and h > 0 and small > 0 and w * h > 0.15 * small:
                pairs.append((i, j))
    return pairs


def crossing_pairs(edges: list[list[tuple[float, float]]], near: float) -> list[tuple[int, int]]:
    """Pairs of edges that cross away from a shared end. Two edges leaving the same node touch
    there by design; a crossing counts only when it is clear of both edges' ends."""
    def ends(e):
        return (e[0], e[-1])

    pairs = []
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            a, b = edges[i], edges[j]
            hit = False
            for k in range(len(a) - 1):
                for m in range(len(b) - 1):
                    p = _segments_cross(a[k], a[k + 1], b[m], b[m + 1])
                    if p is None:
                        continue
                    shared = any(math.dist(p, ea) < near for ea in ends(a)) and \
                        any(math.dist(p, eb) < near for eb in ends(b))
                    if not shared:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                pairs.append((i, j))
    return pairs


def overlap_pairs(nodes: list[tuple[float, float, float, float]]) -> list[tuple[int, int]]:
    """Pairs of nodes whose boxes overlap by more than 2 % of the smaller one."""
    pairs = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, b = nodes[i], nodes[j]
            w = min(a[2], b[2]) - max(a[0], b[0])
            h = min(a[3], b[3]) - max(a[1], b[1])
            if w <= 0 or h <= 0:
                continue
            smaller = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
            if smaller > 0 and w * h > 0.02 * smaller:
                pairs.append((i, j))
    return pairs


def run_through_pairs(edges, nodes, near: float) -> list[tuple[int, int]]:
    """(edge, node) pairs where the edge is drawn across a node it does not start or end at."""
    pairs = []
    for ei, e in enumerate(edges):
        for ni, (x0, y0, x1, y1) in enumerate(nodes):
            attached = any(x0 - near <= px <= x1 + near and y0 - near <= py <= y1 + near
                           for px, py in (e[0], e[-1]))
            if attached:
                continue
            mx, my = 0.15 * (x1 - x0), 0.15 * (y1 - y0)
            core = (x0 + mx, y0 + my, x1 - mx, y1 - my)
            if any(_segment_in_box(e[k], e[k + 1], core) for k in range(len(e) - 1)):
                pairs.append((ei, ni))
    return pairs


def _segment_in_box(p, q, box) -> bool:
    """Does the segment pq pass through the box's interior? (Liang–Barsky clipping.)"""
    t0, t1 = 0.0, 1.0
    dx, dy = q[0] - p[0], q[1] - p[1]
    for d, lo, hi, start in ((dx, box[0], box[2], p[0]), (dy, box[1], box[3], p[1])):
        if abs(d) < 1e-12:
            if not lo < start < hi:
                return False
            continue
        a, b = (lo - start) / d, (hi - start) / d
        if a > b:
            a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 >= t1:
            return False
    return True


def palette() -> set[str]:
    """Every colour the SEI palette and the two theme files define."""
    out = set(NEUTRAL)
    for name in ("palette.md", "mermaid-theme.json", "plantuml-theme.puml", "classdefs.md",
                 "c4/sei-c4-palette.puml"):
        f = ASSETS / name
        if f.is_file():
            out.update(_six(c) for c in HEX_RE.findall(f.read_text(encoding="utf-8")))
    return out


def _six(colour: str) -> str:
    c = colour.upper()
    return "#" + "".join(ch * 2 for ch in c[1:]) if len(c) == 4 else c


def off_palette(metrics: dict, engine: str = "") -> list[str]:
    """Colours drawn on shapes that the palette does not define."""
    allowed = palette() | (MERMAID_INERT if engine == "mermaid" else set())
    return sorted({_six(c) for c in metrics["colours"]} - allowed)


def source_colour_errors(text: str) -> list[str]:
    """Colours a diagram source sets by hand (classDef, style, skinparam) outside the palette."""
    return sorted({_six(c) for c in HEX_RE.findall(text)} - palette())


# --------------------------------------------------------------------------- #
# Rendering a source, and the command line
# --------------------------------------------------------------------------- #

class ToolchainError(Exception):
    """The renderer is missing or the source does not compile; the message says which."""


def engine_of(svg: str) -> str:
    return "plantuml" if "<?plantuml" in svg or "data-diagram-type" in svg else "mermaid"


def render_svg(source: Path, work: Path) -> str:
    """Render one .mmd / .puml to SVG with this skill's own render script; return the SVG text."""
    script = RENDERERS[source.suffix]
    out = work / "out"
    r = subprocess.run(["bash", str(script), "--format", "svg", "--out", str(out), str(source)],
                       capture_output=True, text=True)
    svgs = sorted(out.glob("*.svg")) if out.is_dir() else []
    if r.returncode != 0 or not svgs:
        raise ToolchainError(f"{source}: render failed\n{(r.stderr or r.stdout).strip()}")
    return svgs[0].read_text(encoding="utf-8")


def measured(m: dict) -> bool:
    """False when the SVG holds nothing this script recognises (an unsupported diagram type)."""
    return bool(m["nodes"] or m["participants"])


def report(name: str, m: dict, engine: str) -> tuple[list[str], bool]:
    """The lines to print for one diagram, and whether it has a defect."""
    lines = [name]
    if not measured(m):
        return lines + ["  layout NOT measured: no nodes found — this diagram type is not supported; "
                        "check it by eye"], False
    if m["participants"]:
        lines.append(f"  sequence diagram: {m['participants']} participant(s), {m['messages']} message(s)")
    else:
        lines.append(f"  {m['nodes']} node(s), {m['edges']} edge(s), {m['clusters']} boundary/group(s)")
    bad = False
    for key, label in DEFECTS if not m["participants"] else ():
        lines.append(f"  {label}: {m[key]}")
        lines.extend(f"    - {d}" for d in m["details"][key])
        bad = bad or bool(m[key])
    off = off_palette(m, engine)
    lines.append(f"  colours outside the SEI palette: {', '.join(off) if off else 'none'}")
    bad = bad or bool(off)
    if m["aspect"]:
        ratio = max(m["aspect"], 1 / m["aspect"])
        shape = f"  shape: {m['aspect']:.2f}:1 (width:height)"
        if ratio > MAX_ASPECT:
            shape += f" — an extreme ribbon (over {MAX_ASPECT:.0f}:1); split the diagram"
            bad = True
        lines.append(shape)
    lines.append("  DEFECTS — fix the source, re-render and run this again. A crossing may stay only when no "
                 "ordering removes it (two services that each use the same two stores always cross once)."
                 if bad else "  OK")
    return lines, bad


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if args else 2
    bad = unsupported = False
    with tempfile.TemporaryDirectory() as td:
        for n, arg in enumerate(args):
            path = Path(arg)
            if not path.is_file():
                print(f"diagramlint: {arg} not found", file=sys.stderr)
                return 2
            if path.suffix == ".svg":
                svg = path.read_text(encoding="utf-8")
            elif path.suffix in RENDERERS:
                try:
                    svg = render_svg(path, Path(td) / str(n))
                except ToolchainError as e:
                    print(f"diagramlint: {e}", file=sys.stderr)
                    return 2
            else:
                print(f"diagramlint: {arg}: expected a .svg, .mmd or .puml file", file=sys.stderr)
                return 2
            try:
                m = measure(svg)
            except ET.ParseError as e:
                print(f"diagramlint: {arg} is not well-formed SVG ({e})", file=sys.stderr)
                return 2
            lines, defect = report(arg, m, engine_of(svg))
            print("\n".join(lines))
            bad = bad or defect
            unsupported = unsupported or not measured(m)
    return 1 if bad else 2 if unsupported else 0


if __name__ == "__main__":
    sys.exit(main())
