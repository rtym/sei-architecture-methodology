#!/usr/bin/env bash
# Render PlantUML (.puml) diagrams to PNG with the SEI palette.
# PlantUML needs a Java runtime. If Java is missing this script tells you how to get it.
#
# Usage: render-plantuml.sh [--out DIR] [--format png|svg] TARGET [TARGET ...]
#   TARGET: a .puml file or a directory of .puml files.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
THEME="$SKILL_DIR/assets/plantuml-theme.puml"

OUT_DIR=""
FORMAT="png"
TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --out)    OUT_DIR="${2:?}"; shift 2 ;;
    --format) FORMAT="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
[ "${#TARGETS[@]}" -gt 0 ] || { echo "render-plantuml.sh: no target. Try --help." >&2; exit 2; }

if ! command -v java >/dev/null 2>&1; then
  cat >&2 <<'MSG'
ERROR: no Java runtime found — PlantUML cannot run.

  macOS:   brew install --cask temurin        (or: brew install openjdk && \
           sudo ln -sfn /opt/homebrew/opt/openjdk/libexec/openjdk.jdk \
             /Library/Java/JavaVirtualMachines/openjdk.jdk)
  Debian:  sudo apt-get install default-jre

Then re-run this script. Or use Mermaid instead (scripts/render.sh) — it needs no Java.
MSG
  exit 1
fi

PLANTUML_CMD=()
if command -v plantuml >/dev/null 2>&1; then
  PLANTUML_CMD=("$(command -v plantuml)")
elif [ -n "${PLANTUML_JAR:-}" ] && [ -f "$PLANTUML_JAR" ]; then
  PLANTUML_CMD=(java -jar "$PLANTUML_JAR")
else
  echo "ERROR: 'plantuml' not on PATH and \$PLANTUML_JAR not set." >&2
  echo "  macOS: brew install plantuml" >&2
  exit 1
fi

FILES=()
for t in "${TARGETS[@]}"; do
  if [ -d "$t" ]; then
    while IFS= read -r f; do FILES+=("$f"); done < <(find "$t" -maxdepth 1 -type f -name '*.puml' | sort)
  elif [ -f "$t" ]; then
    FILES+=("$t")
  else
    echo "skip $t (not found)" >&2
  fi
done
[ "${#FILES[@]}" -gt 0 ] || { echo "no .puml files to render" >&2; exit 1; }

echo "render-plantuml: theme=$(basename "$THEME") format=$FORMAT files=${#FILES[@]}"
rc=0
for f in "${FILES[@]}"; do
  dir="$(dirname "$f")"
  dest_dir="${OUT_DIR:-$dir}"
  mkdir -p "$dest_dir"
  if "${PLANTUML_CMD[@]}" -t"$FORMAT" -nometadata -o "$(cd "$dest_dir" && pwd)" "$f" >/dev/null 2>&1; then
    echo "  ok   $dest_dir/$(basename "${f%.puml}").$FORMAT"
  else
    echo "  FAIL $f" >&2
    rc=1
  fi
done
exit $rc
