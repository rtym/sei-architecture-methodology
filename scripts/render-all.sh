#!/usr/bin/env bash
# Re-render every diagram source under the given directories, in place.
#
#   scripts/render-all.sh <dir> [<dir>…]
#
# Finds every *.mmd and *.puml (node_modules excluded), renders each next to its source as
# <name>.png via the pinned renderers, and exits non-zero if any render fails. One command
# replaces the per-file render calls, in a deterministic (sorted) order — use it after editing
# diagram sources in architecture/ or examples/, then open the changed PNGs and check them
# before committing.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -lt 1 ]; then
  echo "usage: render-all.sh <dir> [<dir>…]" >&2
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

if [ "${#mmd[@]}" -eq 0 ] && [ "${#puml[@]}" -eq 0 ]; then
  echo "no *.mmd or *.puml sources under: $*" >&2
  exit 2
fi

fails=0
if [ "${#mmd[@]}" -gt 0 ]; then
  bash "$ROOT/skills/sei-diagrams/scripts/render.sh" "${mmd[@]}" || fails=1
fi
if [ "${#puml[@]}" -gt 0 ]; then
  bash "$ROOT/skills/sei-diagrams/scripts/render-plantuml.sh" "${puml[@]}" || fails=1
fi

echo "render-all: ${#mmd[@]} mermaid + ${#puml[@]} plantuml source(s)"
if [ "$fails" -ne 0 ]; then
  echo "render-all: FAILED — see renderer output above" >&2
  exit 1
fi
