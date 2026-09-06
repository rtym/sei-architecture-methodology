#!/usr/bin/env bash
# Full test suite for the sei-architecture-methodology plugin.
#   tests/run.sh            run everything
#   tests/run.sh --quick    skip the diagram-render smoke test
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="$(command -v python3 || command -v python)"
QUICK=0; [ "${1:-}" = "--quick" ] && QUICK=1
fails=0
step() { printf '\n=== %s ===\n' "$1"; }
ok()   { echo "PASS  $1"; }
bad()  { echo "FAIL  $1"; fails=$((fails+1)); }

step "1. plugin.json is valid JSON"
"$PY" -c "import json,sys; json.load(open('.claude-plugin/plugin.json')); print('ok')" && ok "plugin.json" || bad "plugin.json"

step "2. shell scripts parse (bash -n)"
while IFS= read -r sh; do
  bash -n "$sh" && ok "$sh" || bad "$sh"
done < <(find . -name '*.sh' -not -path './node_modules/*' -not -path '*/node_modules/*')

step "3. plugin structure — validate.py --self"
"$PY" tests/validate.py --self && ok "validate --self" || bad "validate --self"

step "4. mdreport converter unit test"
"$PY" tests/test_mdreport.py && ok "test_mdreport" || bad "test_mdreport"

step "5. example artifacts validate"
if [ -d examples ]; then
  # drivers/ directories get the cross-file check + every file
  while IFS= read -r d; do
    "$PY" tests/validate.py "$d" && ok "$d/" || bad "$d/"
  done < <(find examples -type d -name drivers)
  while IFS= read -r f; do
    case "$f" in */drivers/*) continue ;; esac
    "$PY" tests/validate.py "$f" && ok "$f" || bad "$f"
  done < <(find examples \( -name '*.md' -o -name '*.mmd' \))
else
  echo "(no examples/ dir)"
fi

step "6. mdreport builds HTML + MD from an example"
src="examples/personal-finance-tracker-mermaid/drivers/README.md"
if [ -f "$src" ]; then
  tmp="$(mktemp -d)"
  "$PY" scripts/mdreport.py "$src" --format both --out "$tmp/rep.html" \
    && [ -s "$tmp/rep.html" ] && [ -s "$tmp/rep.md" ] \
    && ok "mdreport example" || bad "mdreport example"
  rm -rf "$tmp"
fi

step "7. diagram render smoke test"
if [ "$QUICK" = "1" ]; then
  echo "(skipped: --quick)"
elif command -v mmdc >/dev/null 2>&1 || [ -x skills/sei-diagrams/node_modules/.bin/mmdc ]; then
  tmp="$(mktemp -d)"
  cat > "$tmp/t.mmd" <<'EOF'
flowchart LR
  %% smoke test
  a["A"] --> b["B"]
EOF
  bash skills/sei-diagrams/scripts/render.sh "$tmp/t.mmd" && [ -s "$tmp/t.png" ] \
    && ok "render.sh -> PNG" || bad "render.sh -> PNG"
  rm -rf "$tmp"
else
  echo "(skipped: mermaid CLI not installed — run: bash skills/sei-diagrams/scripts/setup.sh)"
fi

printf '\n===============================\n'
if [ "$fails" -eq 0 ]; then echo "ALL PASS"; exit 0; else echo "$fails FAILURE(S)"; exit 1; fi
