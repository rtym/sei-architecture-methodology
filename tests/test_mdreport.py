#!/usr/bin/env python3
"""Unit tests for scripts/mdreport.py — standard library only."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import mdreport  # noqa: E402

SAMPLE = """# Title One

Intro **bold** and *italic* and `code` and a [link](https://sei.cmu.edu).

## Section A

| ID | Name | P |
|----|------|:-:|
| BG-1 | Grow | H |
| SQA-1 | Lock down | H |

1. first
2. second
   - nested x
   - nested y

> a quote

```mermaid
flowchart LR
  %% t
  a["A"] --> b["B"]
```

---

Closing paragraph.
"""

FAILS: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "sample.md"
        src.write_text(SAMPLE, encoding="utf-8")

        html = mdreport.to_html([src], "Title One", "sub", want_toc=True,
                                embed=False, standalone=True, out_dir=src.parent)
        check(html.startswith("<!doctype html>"), "html: doctype present")
        check("<title>Title One</title>" in html, "html: title tag")
        check('class="cover"' in html, "html: cover block")
        check('nav class="toc"' in html, "html: toc rendered")
        check("<table>" in html and "<th" in html, "html: table rendered")
        check("text-align:center" in html, "html: column alignment honoured")
        check("<strong>bold</strong>" in html, "html: bold inline")
        check("<em>italic</em>" in html, "html: italic inline")
        check("<code>code</code>" in html, "html: code inline")
        check('href="https://sei.cmu.edu"' in html, "html: link inline")
        check("<ol>" in html and "<ul>" in html, "html: ordered + nested list")
        check("<blockquote>" in html, "html: blockquote")
        check("<hr>" in html, "html: thematic break")
        check("language-mermaid" in html, "html: mermaid kept as source when not embedding")
        check(html.count("<h2") >= 1, "html: section heading")

        # a ```plantuml block falls back to a source block when not embedding
        puml = "# T\n\n```plantuml\n@startuml\ntitle X\nA --> B\n@enduml\n```\n"
        p2 = Path(td) / "puml.md"
        p2.write_text(puml, encoding="utf-8")
        h2 = mdreport.to_html([p2], "T", "", want_toc=False, embed=False, standalone=True,
                             out_dir=p2.parent)
        check("language-plantuml" in h2, "html: plantuml kept as source when not embedding")

        md = mdreport.to_md([src], "Title One", "sub", want_toc=True, out_dir=src.parent)
        check(md.startswith("# Title One"), "md: title")
        check("## Contents" in md, "md: toc")
        check("BG-1" in md and "SQA-1" in md, "md: body preserved")

        # inline() escaping
        esc = mdreport.inline("a < b & c > d")
        check("&lt;" in esc and "&amp;" in esc and "&gt;" in esc, "inline: html-escapes")

        # cross-directory link/image rewriting: a report built from files that live in
        # sibling directories must keep local links/images resolvable from its own
        # output directory (not from each source file's original directory).
        (Path(td) / "docs").mkdir()
        (Path(td) / "reports").mkdir()
        (Path(td) / "docs" / "sibling.md").write_text("# Sibling\n", encoding="utf-8")
        (Path(td) / "docs" / "diagram.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        doc = Path(td) / "docs" / "page.md"
        doc.write_text(
            "# Page\n\n[Sibling](sibling.md) and ![pic](diagram.png)\n", encoding="utf-8"
        )
        out_dir = Path(td) / "reports"
        rhtml = mdreport.to_html([doc], "Page", "", want_toc=False,
                                 embed=False, standalone=True, out_dir=out_dir)
        check('href="../docs/sibling.md"' in rhtml,
              "html: cross-dir link re-relativized to out_dir")
        check('src="../docs/diagram.png"' in rhtml,
              "html: cross-dir image re-relativized to out_dir")
        rmd = mdreport.to_md([doc], "Page", "", want_toc=False, out_dir=out_dir)
        check("(../docs/sibling.md)" in rmd, "md: cross-dir link re-relativized to out_dir")
        check("(../docs/diagram.png)" in rmd, "md: cross-dir image re-relativized to out_dir")

    print()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        return 1
    print("all mdreport tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
