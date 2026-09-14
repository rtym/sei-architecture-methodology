#!/usr/bin/env bash
# Render PlantUML (.puml) diagrams to PNG with the SEI palette.
# PlantUML needs a Java runtime. If Java is missing this script tells you how to get it.
#
# Usage: render-plantuml.sh [--out DIR] [--format png|svg] TARGET [TARGET ...]
#   TARGET: a .puml file or a directory of .puml files.
#
# Includes: this script puts the skill's assets/ directory on PlantUML's include path, so a
# .puml anywhere on disk — including inside the user's project, where no number of `../`
# reaches the installed plugin — can simply say:
#     !include plantuml-theme.puml
#     !include c4/C4_Container.puml
#     !include c4/sei-c4-palette.puml
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS="$SKILL_DIR/assets"
THEME="$ASSETS/plantuml-theme.puml"

[ -f "$THEME" ] || { echo "ERROR: missing theme $THEME" >&2; exit 1; }
[ -d "$ASSETS/c4" ] || { echo "ERROR: missing C4 macros $ASSETS/c4" >&2; exit 1; }

# Resolve `!include <name>` against the skill's assets/ regardless of the .puml file's location.
# Anything the caller already had on the include path is preserved.
if [ -n "${PLANTUML_INCLUDE_PATH:-}" ]; then
  export PLANTUML_INCLUDE_PATH="$ASSETS:$PLANTUML_INCLUDE_PATH"
else
  export PLANTUML_INCLUDE_PATH="$ASSETS"
fi

OUT_DIR=""
FORMAT="png"
TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --out)    OUT_DIR="${2:?}"; shift 2 ;;
    --format) FORMAT="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
[ "${#TARGETS[@]}" -gt 0 ] || { echo "render-plantuml.sh: no target. Try --help." >&2; exit 2; }

# Find Java: PATH first, then common keg-only / SDK locations.
if ! command -v java >/dev/null 2>&1; then
  for jdkbin in \
    /opt/homebrew/opt/openjdk/bin \
    /usr/local/opt/openjdk/bin \
    "$HOME/.sdkman/candidates/java/current/bin" \
    /Library/Java/JavaVirtualMachines/*/Contents/Home/bin ; do
    if [ -x "$jdkbin/java" ]; then PATH="$jdkbin:$PATH"; export PATH; break; fi
  done
fi
if ! command -v java >/dev/null 2>&1; then
  cat >&2 <<'MSG'
ERROR: no Java runtime found — PlantUML cannot run.

  macOS:   brew install openjdk        (this script auto-detects the keg-only path)
           or: brew install --cask temurin
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
  echo "  Debian: sudo apt-get install plantuml" >&2
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

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "render-plantuml: theme=$(basename "$THEME") include=$ASSETS format=$FORMAT files=${#FILES[@]}"
rc=0
for f in "${FILES[@]}"; do
  dir="$(dirname "$f")"
  dest_dir="${OUT_DIR:-$dir}"
  mkdir -p "$dest_dir"
  dest_abs="$(cd "$dest_dir" && pwd)"

  # Render into a staging directory first. PlantUML exits non-zero on a bad diagram but STILL
  # writes an "error image" PNG, so rendering straight into dest_dir would leave a broken image
  # sitting where a good one is expected. Staging means a failed render publishes nothing.
  stage="$TMP_DIR/stage"
  rm -rf "$stage"; mkdir -p "$stage"

  if "${PLANTUML_CMD[@]}" -t"$FORMAT" -nometadata -o "$stage" "$f" \
        >"$TMP_DIR/out.log" 2>"$TMP_DIR/err.log"; then
    produced=()
    while IFS= read -r p; do produced+=("$p"); done \
      < <(find "$stage" -maxdepth 1 -type f -name "*.$FORMAT" | sort)
    if [ "${#produced[@]}" -eq 0 ]; then
      echo "  FAIL $f (plantuml produced no .$FORMAT)" >&2
      rc=1
      continue
    fi
    for p in "${produced[@]}"; do
      mv -f "$p" "$dest_abs/"
      echo "  ok   $dest_abs/$(basename "$p")"
    done
  else
    # Replay PlantUML's own diagnostics — a missing !include reports the offending line here,
    # and silently swallowing it is how an unresolvable include looks like a mystery.
    echo "  FAIL $f" >&2
    sed 's/^/       /' "$TMP_DIR/err.log" >&2 || true
    sed 's/^/       /' "$TMP_DIR/out.log" >&2 || true
    rc=1
  fi
done
exit $rc
