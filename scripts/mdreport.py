#!/usr/bin/env python3
"""
mdreport — turn SEI architecture Markdown artifacts into a clean report,
in Markdown or self-contained HTML, with no third-party dependencies.

Usage:
  python scripts/mdreport.py INPUT.md [INPUT2.md ...] --format {md,html,both} [options]

Options:
  --format md|html|both     output format(s)                     (default: html)
  --out PATH                 output file (single input) or dir    (default: alongside input)
  --title "TEXT"            report title (default: first H1 of first input)
  --subtitle "TEXT"        cover subtitle
  --toc / --no-toc          table of contents                    (default: --toc)
  --embed-diagrams          render ```mermaid blocks to PNG (via sei-diagrams/render.sh)
                            and embed them as base64 <img>       (html only)
  --standalone              full HTML document with embedded CSS  (default on for html)

HTML uses the SEI diagram palette. The Markdown subset covered is what the SEI
skill templates emit: ATX headings, GFM pipe tables, ordered/unordered nested
lists, fenced code (```lang and ```mermaid), blockquotes, thematic breaks,
inline **bold** / *italic* / `code` / [links](url) / images, and raw HTML passthrough.
"""
from __future__ import annotations

import argparse
import base64
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PALETTE = {
    "ink": "#1F2933", "line": "#6B7A8D", "internal": "#EDF2F8", "internal_b": "#3E6DA5",
    "external": "#F5EEE3", "external_b": "#B07D3B", "store": "#E4F0E9", "store_b": "#3F7D5C",
    "person": "#E7E3F3", "person_b": "#6B5BA6", "emph": "#F6E4E4", "emph_b": "#B04A46",
    "page": "#FFFFFF", "muted": "#5B6672", "rule": "#DCE2E9", "codebg": "#F5F7FA",
}

CSS = f"""
:root {{ color-scheme: light; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 0; background: {PALETTE['page']}; color: {PALETTE['ink']};
  font: 16px/1.65 Inter, "Helvetica Neue", Arial, sans-serif;
}}
.wrap {{ max-width: 920px; margin: 0 auto; padding: 48px 32px 96px; }}
.cover {{ border-bottom: 3px solid {PALETTE['internal_b']}; margin-bottom: 40px; padding-bottom: 24px; }}
.cover h1 {{ font-size: 2.1rem; margin: 0 0 6px; }}
.cover .sub {{ color: {PALETTE['muted']}; font-size: 1.05rem; }}
.cover .meta {{ color: {PALETTE['muted']}; font-size: .9rem; margin-top: 10px; }}
h1, h2, h3, h4, h5 {{ line-height: 1.25; margin: 1.8em 0 .6em; }}
h1 {{ font-size: 1.8rem; border-bottom: 2px solid {PALETTE['rule']}; padding-bottom: .2em; }}
h2 {{ font-size: 1.4rem; border-bottom: 1px solid {PALETTE['rule']}; padding-bottom: .2em; }}
h3 {{ font-size: 1.15rem; }}
h4 {{ font-size: 1rem; color: {PALETTE['muted']}; }}
a {{ color: {PALETTE['internal_b']}; }}
p {{ margin: .7em 0; }}
code {{ background: {PALETTE['codebg']}; border: 1px solid {PALETTE['rule']}; border-radius: 4px;
  padding: .08em .35em; font: .9em/1.5 "SF Mono", ui-monospace, Menlo, Consolas, monospace; }}
pre {{ background: {PALETTE['codebg']}; border: 1px solid {PALETTE['rule']}; border-radius: 8px;
  padding: 14px 16px; overflow-x: auto; }}
pre code {{ background: none; border: none; padding: 0; }}
blockquote {{ margin: .8em 0; padding: .2em 1em; border-left: 4px solid {PALETTE['external_b']};
  background: {PALETTE['external']}; color: {PALETTE['ink']}; border-radius: 0 6px 6px 0; }}
hr {{ border: none; border-top: 1px solid {PALETTE['rule']}; margin: 2em 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: .95rem; display: block; overflow-x: auto; }}
th, td {{ border: 1px solid {PALETTE['rule']}; padding: 7px 10px; text-align: left; vertical-align: top; }}
thead th {{ background: {PALETTE['internal']}; border-bottom: 2px solid {PALETTE['internal_b']}; }}
tbody tr:nth-child(even) {{ background: #FAFBFD; }}
ul, ol {{ margin: .6em 0; padding-left: 1.6em; }}
li {{ margin: .25em 0; }}
img {{ max-width: 100%; height: auto; border: 1px solid {PALETTE['rule']}; border-radius: 8px; background: #fff; }}
.diagram {{ margin: 1.2em 0; }}
.diagram figcaption {{ color: {PALETTE['muted']}; font-size: .85rem; margin-top: 6px; }}
nav.toc {{ background: #FBFCFE; border: 1px solid {PALETTE['rule']}; border-radius: 8px;
  padding: 14px 20px; margin: 0 0 32px; }}
nav.toc h2 {{ margin: 0 0 .4em; font-size: 1rem; border: none; }}
nav.toc ul {{ list-style: none; padding-left: 0; margin: 0; }}
nav.toc li {{ margin: .2em 0; }}
nav.toc li.h1 {{ margin-top: .5em; font-weight: 600; }}
nav.toc li.h1:first-child {{ margin-top: 0; }}
nav.toc li.h2 {{ padding-left: 1em; }}
nav.toc li.h3 {{ padding-left: 2.2em; font-size: .92rem; }}
nav.toc li.h4 {{ padding-left: 3.4em; font-size: .88rem; color: {PALETTE['muted']}; }}
@media print {{ .wrap {{ max-width: none; padding: 0; }} nav.toc {{ break-after: page; }} pre, table, figure {{ break-inside: avoid; }} }}
"""

# --------------------------------------------------------------------------- #
# Inline markdown
# --------------------------------------------------------------------------- #

def inline(text: str) -> str:
    """Convert inline markdown to HTML. Order matters."""
    out = []
    i = 0
    # protect inline code first
    code_spans: list[str] = []

    def stash_code(m: re.Match) -> str:
        code_spans.append(m.group(1))
        return f"\x00CODE{len(code_spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash_code, text)
    text = html.escape(text, quote=False)
    # images ![alt](src)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
                  lambda m: f'<img alt="{m.group(1)}" src="{m.group(2)}">', text)
    # links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)",
                  lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    # bold then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"(?<![A-Za-z0-9_])_([^_]+)_(?![A-Za-z0-9_])", r"<em>\1</em>", text)
    # bare autolink
    text = re.sub(r"(?<!\")(https?://[^\s<)]+)", r'<a href="\1">\1</a>', text)

    def restore_code(m: re.Match) -> str:
        return f"<code>{html.escape(code_spans[int(m.group(1))], quote=False)}</code>"

    text = re.sub(r"\x00CODE(\d+)\x00", restore_code, text)
    return text


# --------------------------------------------------------------------------- #
# Block parser
# --------------------------------------------------------------------------- #

class Renderer:
    def __init__(self, embed_diagrams: bool, source_dir: Path):
        self.embed = embed_diagrams
        self.source_dir = source_dir
        self.headings: list[tuple[int, str, str]] = []  # (level, text, slug)
        self._slugs: dict[str, int] = {}
        self._mermaid_n = 0

    def slug(self, text: str) -> str:
        base = re.sub(r"[^\w\- ]", "", text).strip().lower().replace(" ", "-") or "section"
        n = self._slugs.get(base, 0)
        self._slugs[base] = n + 1
        return base if n == 0 else f"{base}-{n}"

    def render(self, md: str) -> str:
        lines = md.replace("\r\n", "\n").split("\n")
        html_parts: list[str] = []
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]

            # fenced code / mermaid
            m = re.match(r"^(\s*)(`{3,}|~{3,})\s*([\w+-]*)\s*$", line)
            if m:
                fence = m.group(2)[0]
                lang = m.group(3).lower()
                i += 1
                buf: list[str] = []
                while i < n and not re.match(rf"^\s*{re.escape(fence)}{{3,}}\s*$", lines[i]):
                    buf.append(lines[i])
                    i += 1
                i += 1  # closing fence
                code = "\n".join(buf)
                if lang == "mermaid":
                    html_parts.append(self._mermaid(code))
                elif lang in ("plantuml", "puml", "uml"):
                    html_parts.append(self._plantuml(code))
                else:
                    cls = f' class="language-{lang}"' if lang else ""
                    html_parts.append(f"<pre><code{cls}>{html.escape(code, quote=False)}</code></pre>")
                continue

            # headings
            hm = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
            if hm:
                level = len(hm.group(1))
                text = hm.group(2).strip()
                slug = self.slug(text)
                if level <= 4:
                    self.headings.append((level, text, slug))
                html_parts.append(f'<h{level} id="{slug}">{inline(text)}</h{level}>')
                i += 1
                continue

            # thematic break
            if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
                html_parts.append("<hr>")
                i += 1
                continue

            # blockquote
            if re.match(r"^\s*>", line):
                buf = []
                while i < n and re.match(r"^\s*>", lines[i]):
                    buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                    i += 1
                inner = self.render("\n".join(buf))
                html_parts.append(f"<blockquote>{inner}</blockquote>")
                continue

            # table (GFM pipe): header row + delimiter row
            if "|" in line and i + 1 < n and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]):
                header = self._split_row(line)
                aligns = [self._align(c) for c in self._split_row(lines[i + 1])]
                i += 2
                rows = []
                while i < n and "|" in lines[i] and lines[i].strip():
                    rows.append(self._split_row(lines[i]))
                    i += 1
                html_parts.append(self._table(header, aligns, rows))
                continue

            # list (ordered/unordered, one level of nesting)
            if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line):
                block, i = self._collect_list_block(lines, i)
                html_parts.append(self._render_list(block))
                continue

            # blank
            if not line.strip():
                i += 1
                continue

            # paragraph (gather until blank / block start)
            buf = [line]
            i += 1
            while i < n and lines[i].strip() and not self._is_block_start(lines[i], lines[i + 1] if i + 1 < n else ""):
                buf.append(lines[i])
                i += 1
            para = " ".join(s.strip() for s in buf)
            if re.match(r"^\s*<[a-zA-Z/]", para):  # raw HTML line
                html_parts.append(para)
            else:
                html_parts.append(f"<p>{inline(para)}</p>")

        return "\n".join(html_parts)

    # -- helpers -----------------------------------------------------------

    @staticmethod
    def _is_block_start(line: str, nxt: str) -> bool:
        return bool(
            re.match(r"^\s*#{1,6}\s", line)
            or re.match(r"^\s*(`{3,}|~{3,})", line)
            or re.match(r"^\s*>", line)
            or re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line)
            or re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line)
            or ("|" in line and re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", nxt))
        )

    @staticmethod
    def _split_row(row: str) -> list[str]:
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in re.split(r"(?<!\\)\|", row)]

    @staticmethod
    def _align(delim: str) -> str:
        d = delim.strip()
        if d.startswith(":") and d.endswith(":"):
            return "center"
        if d.endswith(":"):
            return "right"
        return "left"

    def _table(self, header, aligns, rows) -> str:
        def cells(cs, tag):
            out = []
            for j, c in enumerate(cs):
                a = aligns[j] if j < len(aligns) else "left"
                style = f' style="text-align:{a}"' if a != "left" else ""
                out.append(f"<{tag}{style}>{inline(c)}</{tag}>")
            return "".join(out)

        thead = f"<thead><tr>{cells(header, 'th')}</tr></thead>"
        body = "".join(f"<tr>{cells(r, 'td')}</tr>" for r in rows)
        return f"<table>{thead}<tbody>{body}</tbody></table>"

    def _collect_list_block(self, lines, i):
        buf = []
        while i < len(lines):
            ln = lines[i]
            if re.match(r"^(\s*)([-*+]|\d+[.)])\s+", ln):
                buf.append(ln)
                i += 1
            elif ln.strip() == "":
                # allow a single blank line inside a list
                if i + 1 < len(lines) and re.match(r"^(\s*)([-*+]|\d+[.)])\s+", lines[i + 1]):
                    i += 1
                    continue
                break
            elif ln.startswith(("  ", "\t")):  # continuation / nested text
                buf.append(ln)
                i += 1
            else:
                break
        return buf, i

    def _render_list(self, block) -> str:
        root: list[dict] = []
        stack: list[tuple[int, list]] = [(-1, root)]
        for ln in block:
            m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
            if not m:
                if root:
                    _deepest(root)["text"] += " " + ln.strip()
                continue
            indent = len(m.group(1).expandtabs(4))
            ordered = bool(re.match(r"\d+[.)]", m.group(2)))
            item = {"text": m.group(3), "children": [], "ordered": ordered}
            while stack and stack[-1][0] >= indent:
                stack.pop()
            parent = stack[-1][1]
            parent.append(item)
            stack.append((indent, item["children"]))
        return _emit_list(root)


def _deepest(items):
    node = items[-1]
    while node["children"]:
        node = node["children"][-1]
    return node


def _emit_list(items) -> str:
    if not items:
        return ""
    tag = "ol" if items[0]["ordered"] else "ul"
    parts = [f"<{tag}>"]
    for it in items:
        kids = _emit_list(it["children"]) if it["children"] else ""
        parts.append(f"<li>{inline(it['text'])}{kids}</li>")
    parts.append(f"</{tag}>")
    return "".join(parts)


# add mermaid rendering as a method (kept out of class body for readability)
def _mermaid(self: Renderer, code: str) -> str:
    self._mermaid_n += 1
    idx = self._mermaid_n
    title = ""
    tm = re.search(r"title\s+(.+)", code) or re.search(r"%%\s*(.+)", code)
    if tm:
        title = tm.group(1).strip()
    if not self.embed:
        return (f'<figure class="diagram"><pre><code class="language-mermaid">'
                f"{html.escape(code, quote=False)}</code></pre>"
                f"<figcaption>Diagram {idx}"
                f"{' — ' + html.escape(title) if title else ''} "
                f"(source shown; run with --embed-diagrams to render)</figcaption></figure>")
    render_sh = (Path(__file__).resolve().parent.parent
                 / "skills" / "sei-diagrams" / "scripts" / "render.sh")
    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / f"diagram-{idx}.mmd"
            src.write_text(code, encoding="utf-8")
            subprocess.run(["bash", str(render_sh), str(src)],
                           check=True, capture_output=True, text=True, timeout=180)
            png = src.with_suffix(".png")
            data = base64.b64encode(png.read_bytes()).decode("ascii")
        cap = f"<figcaption>Diagram {idx}{' — ' + html.escape(title) if title else ''}</figcaption>"
        return (f'<figure class="diagram">'
                f'<img alt="{html.escape(title) or f"diagram {idx}"}" '
                f'src="data:image/png;base64,{data}">{cap}</figure>')
    except Exception as exc:  # fall back to source block
        return (f'<figure class="diagram"><pre><code class="language-mermaid">'
                f"{html.escape(code, quote=False)}</code></pre>"
                f"<figcaption>Diagram {idx} — render failed: {html.escape(str(exc))}</figcaption></figure>")


Renderer._mermaid = _mermaid


def _plantuml(self: Renderer, code: str) -> str:
    """Render a fenced ```plantuml block to PNG via render-plantuml.sh and inline it."""
    self._mermaid_n += 1
    idx = self._mermaid_n
    title = ""
    tm = re.search(r"^\s*title\s+(.+)$", code, re.MULTILINE)
    if tm:
        title = tm.group(1).strip()
    if not self.embed:
        return (f'<figure class="diagram"><pre><code class="language-plantuml">'
                f"{html.escape(code, quote=False)}</code></pre>"
                f"<figcaption>Diagram {idx}"
                f"{' — ' + html.escape(title) if title else ''} "
                f"(source shown; run with --embed-diagrams to render)</figcaption></figure>")
    root = Path(__file__).resolve().parent.parent
    assets = root / "skills" / "sei-diagrams" / "assets"
    render_sh = root / "skills" / "sei-diagrams" / "scripts" / "render-plantuml.sh"

    # rewrite relative !include paths (…/assets/…​) to absolute so the block renders
    # from a temp dir independent of where the original .puml lived.
    def _abs_include(m: re.Match) -> str:
        tail = m.group(1).replace("\\", "/")
        j = tail.find("skills/sei-diagrams/assets/")
        rel = tail[j + len("skills/sei-diagrams/assets/"):] if j >= 0 else tail.split("assets/")[-1]
        return f"!include {assets / rel}"

    fixed = re.sub(r"!include\s+(\S+)", _abs_include, code)
    # drop the diagram name from '@startuml <name>' so PlantUML writes <src-stem>.png,
    # not <name>.png
    fixed = re.sub(r"(?m)^\s*@startuml\b.*$", "@startuml", fixed, count=1)
    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / f"diagram-{idx}.puml"
            src.write_text(fixed, encoding="utf-8")
            subprocess.run(["bash", str(render_sh), str(src)],
                           check=True, capture_output=True, text=True, timeout=240)
            pngs = sorted(Path(td).glob("*.png"))
            if not pngs:
                raise FileNotFoundError("plantuml produced no PNG")
            data = base64.b64encode(pngs[0].read_bytes()).decode("ascii")
        cap = f"<figcaption>Diagram {idx}{' — ' + html.escape(title) if title else ''}</figcaption>"
        return (f'<figure class="diagram">'
                f'<img alt="{html.escape(title) or f"diagram {idx}"}" '
                f'src="data:image/png;base64,{data}">{cap}</figure>')
    except Exception as exc:  # fall back to source block
        return (f'<figure class="diagram"><pre><code class="language-plantuml">'
                f"{html.escape(code, quote=False)}</code></pre>"
                f"<figcaption>Diagram {idx} — render failed: {html.escape(str(exc))}</figcaption></figure>")


Renderer._plantuml = _plantuml


# --------------------------------------------------------------------------- #
# Document assembly
# --------------------------------------------------------------------------- #

def build_toc(headings, skip_title: str = "") -> str:
    if not headings:
        return ""
    items = []
    skipped_title = False
    for level, text, slug in headings:
        # drop the first H1 if it just repeats the report title
        if level == 1 and not skipped_title and skip_title \
                and text.strip().lower() == skip_title.strip().lower():
            skipped_title = True
            continue
        if level > 4:
            continue
        cls = f"h{level}"
        items.append(f'<li class="{cls}"><a href="#{slug}">{html.escape(text)}</a></li>')
    if not items:
        return ""
    return '<nav class="toc"><h2>Contents</h2><ul>' + "".join(items) + "</ul></nav>"


def to_html(inputs: list[Path], title: str, subtitle: str, want_toc: bool,
            embed: bool, standalone: bool) -> str:
    renderer = Renderer(embed_diagrams=embed, source_dir=inputs[0].parent)
    body_sections = []
    for p in inputs:
        renderer.source_dir = p.parent
        body_sections.append(renderer.render(p.read_text(encoding="utf-8")))
    body = "\n<hr>\n".join(body_sections)
    toc = build_toc(renderer.headings, skip_title=title) if want_toc else ""
    meta = f"Generated {_today()} · {len(inputs)} source file(s)"
    cover = (f'<header class="cover"><h1>{html.escape(title)}</h1>'
             + (f'<div class="sub">{html.escape(subtitle)}</div>' if subtitle else "")
             + f'<div class="meta">{meta}</div></header>')
    inner = f'<div class="wrap">{cover}{toc}{body}</div>'
    if not standalone:
        return inner
    return (f"<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f"<body>{inner}</body></html>\n")


def to_md(inputs: list[Path], title: str, subtitle: str, want_toc: bool) -> str:
    parts = [f"# {title}", ""]
    if subtitle:
        parts += [f"_{subtitle}_", ""]
    parts += [f"> Generated {_today()} · {len(inputs)} source file(s)", ""]
    if want_toc:
        heads = []
        seen: dict[str, int] = {}
        in_fence = False
        for p in inputs:
            for line in p.read_text(encoding="utf-8").splitlines():
                if re.match(r"^\s*(`{3,}|~{3,})", line):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                hm = re.match(r"^(#{1,4})\s+(.*?)\s*#*$", line)
                if not hm:
                    continue
                lvl = len(hm.group(1))
                txt = hm.group(2).strip()
                if lvl == 1 and txt.strip().lower() == title.strip().lower():
                    continue
                base = re.sub(r"[^\w\- ]", "", txt).strip().lower().replace(" ", "-") or "section"
                n = seen.get(base, 0)
                seen[base] = n + 1
                slug = base if n == 0 else f"{base}-{n}"
                heads.append(f'{"  " * (lvl - 1)}- [{txt}](#{slug})')
        if heads:
            parts += ["## Contents", "", *heads, ""]
    for p in inputs:
        parts += ["", "---", "", p.read_text(encoding="utf-8").strip(), ""]
    return "\n".join(parts) + "\n"


def _today() -> str:
    import datetime
    return datetime.date.today().isoformat()


def _first_h1(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#\s+(.+)", line)
        if m:
            return m.group(1).strip()
    return path.stem


def _vandb_order(md_files: list[Path]) -> list[Path]:
    """Order a docs/ package per the Views-and-Beyond document structure."""
    def rank(p: Path) -> tuple:
        n = p.name.lower()
        if n in ("index.md", "readme.md", "roadmap.md"):
            return (0, n)
        if "system-overview" in n or n == "overview.md":
            return (1, n)
        if n.startswith("view-"):
            if "module" in n:
                return (2, 0, n)
            if "cnc" in n or "c&c" in n or "component-and-connector" in n or "connector" in n:
                return (2, 1, n)
            if "alloc" in n or "deploy" in n:
                return (2, 2, n)
            return (2, 3, n)
        if "mapping" in n:
            return (3, n)
        if "rationale" in n:
            return (4, n)
        if "directory" in n or "glossary" in n:
            return (5, n)
        if "change" in n:
            return (6, n)
        return (7, n)
    return sorted(md_files, key=rank)


def _expand_inputs(inputs: list[Path], profile: str | None) -> list[Path]:
    files: list[Path] = []
    for p in inputs:
        if p.is_dir():
            found = sorted(f for f in p.glob("*.md"))
            files += _vandb_order(found) if profile == "vandb" else found
        else:
            files.append(p)
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mdreport", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--format", choices=["md", "html", "both"], default="html")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--title")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--profile", choices=["vandb"],
                    help="'vandb' orders a docs/ directory per the Views-and-Beyond structure")
    ap.add_argument("--toc", dest="toc", action="store_true", default=True)
    ap.add_argument("--no-toc", dest="toc", action="store_false")
    ap.add_argument("--embed-diagrams", action="store_true")
    ap.add_argument("--standalone", action="store_true", default=True)
    ap.add_argument("--no-standalone", dest="standalone", action="store_false")
    args = ap.parse_args(argv)

    args.inputs = _expand_inputs(args.inputs, args.profile)
    if not args.inputs:
        print("error: no input .md files (a directory with no *.md?)", file=sys.stderr)
        return 2
    for p in args.inputs:
        if not p.is_file():
            print(f"error: not a file: {p}", file=sys.stderr)
            return 2
    if args.profile == "vandb" and not args.subtitle:
        args.subtitle = "Views-and-Beyond architecture description"

    title = args.title or _first_h1(args.inputs[0])
    formats = ["md", "html"] if args.format == "both" else [args.format]
    base_out = args.out
    # treat --out as a FILE only when it exists as one, ends with a real format extension,
    # or its parent is a directory and it doesn't look like a dir path
    out_is_file = bool(base_out) and (
        base_out.is_file()
        or base_out.suffix.lower() in (".md", ".markdown", ".html", ".htm")
    )
    out_is_dir = bool(base_out) and not out_is_file
    written = []

    for fmt in formats:
        if out_is_file:
            target = base_out if base_out.suffix.lstrip(".").lower() in (fmt, "htm") \
                else base_out.with_suffix(f".{fmt}")
        elif out_is_dir:
            target = base_out / f"{args.inputs[0].stem}-report.{fmt}"
        else:
            target = args.inputs[0].with_name(f"{args.inputs[0].stem}-report.{fmt}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "html":
            content = to_html(args.inputs, title, args.subtitle, args.toc,
                              args.embed_diagrams, args.standalone)
        else:
            content = to_md(args.inputs, title, args.subtitle, args.toc)
        target.write_text(content, encoding="utf-8")
        written.append(target)

    for w in written:
        print(f"wrote {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
