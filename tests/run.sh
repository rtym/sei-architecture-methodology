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

step "8. PlantUML render smoke test (from OUTSIDE the plugin)"
# This one must run from a directory that is NOT inside the plugin: the documented includes
# resolve through PLANTUML_INCLUDE_PATH, and a '../'-traversal regression would still pass if
# we rendered from within this repo (where ../../skills/... happens to exist).
if [ "$QUICK" = "1" ]; then
  echo "(skipped: --quick)"
elif ! command -v java >/dev/null 2>&1 && [ -z "${PLANTUML_JAR:-}" ]; then
  echo "(skipped: no Java — install a JRE to exercise the PlantUML renderer)"
elif ! command -v plantuml >/dev/null 2>&1 && [ -z "${PLANTUML_JAR:-}" ]; then
  echo "(skipped: plantuml not installed — brew install plantuml / apt-get install plantuml)"
else
  tmp="$(mktemp -d)"
  mkdir -p "$tmp/architecture/diagrams"

  # a) the documented C4 include pair resolves and produces a real PNG
  cat > "$tmp/architecture/diagrams/context.puml" <<'EOF'
@startuml context
!include c4/C4_Context.puml
!include c4/sei-c4-palette.puml
title Context diagram — Smoke
Person(user, "User", "web")
System(sys, "System", "does things")
Rel(user, sys, "Uses over HTTPS")
@enduml
EOF
  # b) the plain theme include resolves too
  cat > "$tmp/architecture/diagrams/seq.puml" <<'EOF'
@startuml seq
!include plantuml-theme.puml
title Sequence — Smoke
autonumber
participant "Web" as w
participant "API" as a
w -> a: Request
a --> w: Response
@enduml
EOF
  # c) an unresolvable include must FAIL loudly and publish no PNG
  cat > "$tmp/architecture/diagrams/bad.puml" <<'EOF'
@startuml bad
!include ../../skills/sei-diagrams/assets/plantuml-theme.puml
title Should not render
@enduml
EOF

  ( cd "$tmp" && bash "$ROOT/skills/sei-diagrams/scripts/render-plantuml.sh" \
      architecture/diagrams/context.puml architecture/diagrams/seq.puml ) >/dev/null 2>&1 \
    && [ -s "$tmp/architecture/diagrams/context.png" ] \
    && [ -s "$tmp/architecture/diagrams/seq.png" ] \
    && ok "render-plantuml.sh -> PNG from a user project" \
    || bad "render-plantuml.sh -> PNG from a user project"

  if ( cd "$tmp" && bash "$ROOT/skills/sei-diagrams/scripts/render-plantuml.sh" \
         architecture/diagrams/bad.puml ) >/dev/null 2>&1; then
    bad "render-plantuml.sh should exit non-zero on an unresolvable !include"
  elif [ -e "$tmp/architecture/diagrams/bad.png" ]; then
    bad "render-plantuml.sh published an error image for a failed render"
  else
    ok "render-plantuml.sh fails loudly and publishes nothing on a bad !include"
  fi
  rm -rf "$tmp"
fi

printf '\n===============================\n'
if [ "$fails" -eq 0 ]; then echo "ALL PASS"; exit 0; else echo "$fails FAILURE(S)"; exit 1; fi
