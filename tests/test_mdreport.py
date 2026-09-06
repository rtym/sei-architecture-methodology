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
                                embed=False, standalone=True)
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

        md = mdreport.to_md([src], "Title One", "sub", want_toc=True)
        check(md.startswith("# Title One"), "md: title")
        check("## Contents" in md, "md: toc")
        check("BG-1" in md and "SQA-1" in md, "md: body preserved")

        # inline() escaping
        esc = mdreport.inline("a < b & c > d")
        check("&lt;" in esc and "&amp;" in esc and "&gt;" in esc, "inline: html-escapes")

    print()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        return 1
    print("all mdreport tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
