#!/usr/bin/env bash
# Re-render every diagram source under the given directories, in place.
#
#   scripts/render-all.sh [--list] <dir> [<dir>…]
#
# Finds every *.mmd and *.puml (node_modules excluded) and renders each next to its source as
# <name>.png via the pinned renderers. A ```mermaid block that lives only in a Markdown file
# (no .mmd beside its PNG) is rendered too, to the PNG its image line names — so a diagram
# embedded in a document is not left stale. Exits non-zero if any render fails. One command
# replaces the per-file render calls, in a deterministic (sorted) order — use it after editing
# diagram sources in architecture/ or examples/, then open the changed PNGs and check them
# before committing.
#
# --list prints what would be rendered (source -> PNG) and renders nothing; needs no toolchain.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python || true)"

LIST=0
if [ "${1:-}" = "--list" ]; then LIST=1; shift; fi
if [ $# -lt 1 ]; then
  echo "usage: render-all.sh [--list] <dir> [<dir>…]" >&2
  exit 2
fi

mmd=()
puml=()
for d in "$@"; do
  if [ ! -e "$d" ]; then
    echo "not found: $d" >&2
    exit 2
  fi
  while IFS= read -r f; do mmd+=("$f"); done \
    < <(find "$d" -name '*.mmd' -not -path '*/node_modules/*' | sort)
  while IFS= read -r f; do puml+=("$f"); done \
    < <(find "$d" -name '*.puml' -not -path '*/node_modules/*' | sort)
done

# Mermaid blocks embedded in Markdown with no .mmd beside their PNG. Each is written to a
# temporary <name>.mmd, named as render.sh names a block (`%% name: <slug>`, else <mdname>-<NN>),
# and paired with the directory of the image line that shows it. Lines: <tmp .mmd>\t<out dir>\t<md>.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
embedded=()
if [ -n "$PY" ]; then
  while IFS= read -r line; do [ -n "$line" ] && embedded+=("$line"); done < <("$PY" - "$TMP_DIR" "$@" <<'PYEOF'
import re, sys
from pathlib import Path
tmp, roots = Path(sys.argv[1]), [Path(a) for a in sys.argv[2:]]
block_re = re.compile(r"^[ \t]*```mermaid[ \t]*\n(.*?)^[ \t]*```[ \t]*$", re.DOTALL | re.MULTILINE)
image_re = re.compile(r"!\[[^\]]*\]\(([^)\s]+\.png)\)")
seen, n = set(), 0
for md in sorted(p for r in roots for p in r.rglob("*.md") if "node_modules" not in p.parts):
    text = md.read_text(encoding="utf-8")
    images = {Path(i).stem: md.parent / i for i in image_re.findall(text)}
    for k, m in enumerate(block_re.finditer(text), 1):
        name = re.search(r"^[ \t]*%%[ \t]*name:[ \t]*(.+?)[ \t]*$", m.group(1), re.MULTILINE)
        base = re.sub(r"[^A-Za-z0-9._-]", "-", name.group(1)) if name else f"{md.stem}-{k:02d}"
        png = images.get(base)
        if png is None or png.with_suffix(".mmd").is_file() or png.resolve() in seen:
            continue
        seen.add(png.resolve())
        n += 1
        src = tmp / str(n) / f"{base}.mmd"
        src.parent.mkdir(parents=True)
        src.write_text(m.group(1), encoding="utf-8")
        print(f"{src}\t{png.parent}\t{md}")
PYEOF
  )
fi

if [ "${#mmd[@]}" -eq 0 ] && [ "${#puml[@]}" -eq 0 ] && [ "${#embedded[@]}" -eq 0 ]; then
  echo "no *.mmd or *.puml sources (or embedded mermaid blocks) under: $*" >&2
  exit 2
fi

if [ "$LIST" -eq 1 ]; then
  for f in ${mmd[@]+"${mmd[@]}"} ${puml[@]+"${puml[@]}"}; do echo "$f -> ${f%.*}.png"; done
  for e in ${embedded[@]+"${embedded[@]}"}; do
    IFS=$'\t' read -r src out md <<< "$e"
    echo "$md#$(basename "${src%.mmd}") -> $out/$(basename "${src%.mmd}").png"
  done
  exit 0
fi

fails=0
if [ "${#mmd[@]}" -gt 0 ]; then
  bash "$ROOT/skills/sei-diagrams/scripts/render.sh" "${mmd[@]}" || fails=1
fi
for e in ${embedded[@]+"${embedded[@]}"}; do
  IFS=$'\t' read -r src out md <<< "$e"
  bash "$ROOT/skills/sei-diagrams/scripts/render.sh" --out "$out" "$src" | grep -v '^render:\|^done:' || true
  [ -s "$out/$(basename "${src%.mmd}").png" ] || fails=1
done
if [ "${#puml[@]}" -gt 0 ]; then
  bash "$ROOT/skills/sei-diagrams/scripts/render-plantuml.sh" "${puml[@]}" || fails=1
fi

echo "render-all: ${#mmd[@]} mermaid + ${#embedded[@]} embedded mermaid + ${#puml[@]} plantuml source(s)"
if [ "$fails" -ne 0 ]; then
  echo "render-all: FAILED — see renderer output above" >&2
  exit 1
fi
