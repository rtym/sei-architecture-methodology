#!/usr/bin/env bash
# Render Mermaid diagrams to high-resolution PNG with the SEI palette.
#
# Usage:
#   render.sh [--out DIR] [--format png|svg|pdf] [--width N] [--scale N] TARGET [TARGET ...]
#
# TARGET may be:
#   *.mmd / *.mermaid   a Mermaid source file            -> <name>.png
#   *.md                a Markdown file; each ```mermaid  -> <mdname>-<NN>.png
#                       fenced block is extracted and rendered
#   a directory         every *.mmd / *.mermaid inside it
#
# Output goes next to the source unless --out DIR is given.
# First run: bash setup.sh   (installs the renderer + a headless Chromium).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
THEME="$SKILL_DIR/assets/mermaid-theme.json"
PUPPET="$SKILL_DIR/assets/puppeteer-config.json"

OUT_DIR=""
FORMAT="png"
WIDTH="1600"
SCALE="3"
BACKGROUND="white"
TARGETS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --out)        OUT_DIR="${2:?--out needs a directory}"; shift 2 ;;
    --format)     FORMAT="${2:?}"; shift 2 ;;
    --width)      WIDTH="${2:?}"; shift 2 ;;
    --scale)      SCALE="${2:?}"; shift 2 ;;
    --background) BACKGROUND="${2:?}"; shift 2 ;;
    -h|--help)    sed -n '2,20p' "$0"; exit 0 ;;
    *)            TARGETS+=("$1"); shift ;;
  esac
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "render.sh: no target given. Try --help." >&2
  exit 2
fi

# ---- locate the renderer -----------------------------------------------------
MMDC=()
if [ -x "$SKILL_DIR/node_modules/.bin/mmdc" ]; then
  MMDC=("$SKILL_DIR/node_modules/.bin/mmdc")
elif command -v mmdc >/dev/null 2>&1; then
  MMDC=("$(command -v mmdc)")
elif command -v npx >/dev/null 2>&1; then
  echo "note: no local mmdc — using 'npx @mermaid-js/mermaid-cli' (slower; run setup.sh to fix)."
  MMDC=(npx -y "@mermaid-js/mermaid-cli")
else
  echo "ERROR: no Mermaid renderer. Run: bash $SCRIPT_DIR/setup.sh" >&2
  exit 1
fi

[ -f "$THEME" ]  || { echo "ERROR: missing theme $THEME" >&2; exit 1; }
[ -f "$PUPPET" ] || { echo "ERROR: missing puppeteer config $PUPPET" >&2; exit 1; }

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

rendered=0
failed=0

render_one() { # <src.mmd> <dest.png>
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  if "${MMDC[@]}" \
        --input "$src" \
        --output "$dest" \
        --configFile "$THEME" \
        --puppeteerConfigFile "$PUPPET" \
        --backgroundColor "$BACKGROUND" \
        --width "$WIDTH" \
        --scale "$SCALE" >/dev/null 2>"$TMP_DIR/err.log"; then
    echo "  ok   $dest"
    rendered=$((rendered + 1))
  else
    echo "  FAIL $src" >&2
    sed 's/^/       /' "$TMP_DIR/err.log" >&2 || true
    failed=$((failed + 1))
  fi
}

dest_for() { # <src-basename-no-ext>
  local base="$1"
  if [ -n "$OUT_DIR" ]; then echo "$OUT_DIR/$base.$FORMAT"; else echo "$2/$base.$FORMAT"; fi
}

extract_md() { # <file.md>  -> writes <base>-NN.mmd into TMP_DIR, echoes their paths
  local md="$1" base
  base="$(basename "${md%.*}")"
  awk -v out="$TMP_DIR" -v base="$base" '
    /^[[:space:]]*```mermaid[[:space:]]*$/ { inblk=1; n++; fn=sprintf("%s/%s-%02d.mmd", out, base, n); next }
    inblk && /^[[:space:]]*```[[:space:]]*$/ { inblk=0; close(fn); print fn; next }
    inblk { print $0 > fn }
  ' "$md"
}

process() { # <path>
  local path="$1"
  if [ -d "$path" ]; then
    local found=0
    while IFS= read -r f; do
      found=1
      render_one "$f" "$(dest_for "$(basename "${f%.*}")" "$path")"
    done < <(find "$path" -maxdepth 1 -type f \( -name '*.mmd' -o -name '*.mermaid' \) | sort)
    [ "$found" -eq 1 ] || echo "  (no .mmd/.mermaid files in $path)"
  elif [ -f "$path" ]; then
    case "$path" in
      *.mmd|*.mermaid)
        render_one "$path" "$(dest_for "$(basename "${path%.*}")" "$(dirname "$path")")" ;;
      *.md|*.markdown)
        local any=0
        while IFS= read -r frag; do
          [ -n "$frag" ] || continue
          any=1
          render_one "$frag" "$(dest_for "$(basename "${frag%.*}")" "$(dirname "$path")")"
        done < <(extract_md "$path")
        [ "$any" -eq 1 ] || echo "  (no \`\`\`mermaid blocks in $path)" ;;
      *)
        echo "  skip $path (unknown type; expected .mmd/.mermaid/.md)" ;;
    esac
  else
    echo "  skip $path (not found)" >&2
    failed=$((failed + 1))
  fi
}

echo "render: theme=$(basename "$THEME") format=$FORMAT width=$WIDTH scale=$SCALE bg=$BACKGROUND"
for t in "${TARGETS[@]}"; do
  # allow unquoted globs passed as a single quoted string
  if [[ "$t" == *"*"* ]]; then
    for g in $t; do process "$g"; done
  else
    process "$t"
  fi
done

echo "done: $rendered rendered, $failed failed"
[ "$failed" -eq 0 ]
