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

    # --- Views-and-Beyond ordering and directory expansion ---
    names = ["zz-notes.md", "rationale.md", "view-allocation-deployment.md", "README.md",
             "mapping-between-views.md", "view-cnc-runtime.md", "directory.md",
             "view-module-decomposition.md", "system-overview.md", "change-log.md", "view-security.md"]
    order = [p.name for p in mdreport._vandb_order([Path(n) for n in names])]
    check(order == ["README.md", "system-overview.md", "view-module-decomposition.md", "view-cnc-runtime.md",
                    "view-allocation-deployment.md", "view-security.md", "mapping-between-views.md",
                    "rationale.md", "directory.md", "change-log.md", "zz-notes.md"],
          "vandb: roadmap, overview, module/C&C/allocation/other views, mapping, rationale, directory, change log, rest")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "docs"
        d.mkdir()
        for n in ("rationale.md", "README.md", "view-cnc-x.md"):
            (d / n).write_text(f"# {n}\n", encoding="utf-8")
        plain = [p.name for p in mdreport._expand_inputs([d], None)]
        check(plain == ["README.md", "rationale.md", "view-cnc-x.md"], "a directory expands to its *.md, sorted")
        check([p.name for p in mdreport._expand_inputs([d], "vandb")] == ["README.md", "view-cnc-x.md", "rationale.md"],
              "a directory expands in V&B order with --profile vandb")

    # --- command line ---
    import contextlib, io
    def cli(*args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mdreport.main([str(a) for a in args])
        return rc, out.getvalue(), err.getvalue()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "doc.md"
        src.write_text("# The Doc Title\n\nBody.\n", encoding="utf-8")
        rc, out, _ = cli(src, "--format", "both", "--out", root / "out" / "report.html")
        check(rc == 0 and (root / "out" / "report.html").is_file() and (root / "out" / "report.md").is_file(),
              "cli: --format both with a file --out writes .html and .md side by side")
        check("The Doc Title" in (root / "out" / "report.html").read_text(), "cli: the title defaults to the first H1")
        rc, _, _ = cli(src, "--format", "md", "--out", root / "dir")
        check(rc == 0 and (root / "dir" / "doc-report.md").is_file(), "cli: a directory --out names the file after the input")
        rc, _, _ = cli(src, "--title", "Given")
        check(rc == 0 and "Given" in (root / "doc-report.html").read_text(), "cli: no --out writes beside the input; --title wins")
        (root / "empty").mkdir()
        rc, _, err = cli(root / "empty")
        check(rc == 2 and "no input" in err, "cli: a directory with no .md exits 2")
        rc, _, err = cli(root / "missing.md")
        check(rc == 2 and "not a file" in err, "cli: a missing input exits 2")
        docs = root / "docs"
        docs.mkdir()
        (docs / "README.md").write_text("# Roadmap\n", encoding="utf-8")
        rc, _, _ = cli("--profile", "vandb", docs, "--out", root / "vb.html")
        check(rc == 0 and "Views-and-Beyond architecture description" in (root / "vb.html").read_text(),
              "cli: --profile vandb supplies the V&B subtitle")

    # The examples' committed Markdown reports are what a fresh build gives (the HTML twins embed
    # the same content), so a source edited without regenerating the reports fails here.
    import re
    import shutil
    for ex in sorted((ROOT / "examples").iterdir()):
        if not (ex / "reports").is_dir():
            continue
        with tempfile.TemporaryDirectory() as td:
            work = Path(td) / ex.name
            shutil.copytree(ex, work, ignore=shutil.ignore_patterns("reports", "*.png", "*.html"))
            builds = (
                ("architecture-package.md", "Personal Finance Tracker — Architecture Package",
                 [work / "drivers" / "README.md", *sorted((work / "add").glob("*-Architecture.md"))]),
                ("vandb-architecture-description.md", "Architecture Description — Personal Finance Tracker",
                 ["--profile", "vandb", work / "docs"]),
            )
            for name, title, inputs in builds:
                rc, _, _ = cli(*inputs, "--format", "md", "--title", title, "--out", work / "reports" / name)
                fresh = (work / "reports" / name).read_text(encoding="utf-8") if rc == 0 else ""
                dated = re.compile(r"^> Generated \d{4}-\d{2}-\d{2}", re.MULTILINE)
                same = dated.sub("> Generated", fresh) == dated.sub("> Generated", (ex / "reports" / name).read_text(encoding="utf-8"))
                check(rc == 0 and same, f"example report {ex.name}/reports/{name} matches a fresh build "
                                        "(regenerate it with the commands in the example README)")
            for name, _, _ in builds:
                html = (ex / "reports" / name).with_suffix(".html")
                check(html.is_file() and "<img" in html.read_text(encoding="utf-8"),
                      f"example report {ex.name}/reports/{html.name} exists with its diagrams embedded")

    print()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        return 1
    print("all mdreport tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
