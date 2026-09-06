#!/usr/bin/env bash
# Install the Mermaid renderer locally under the sei-diagrams skill.
# Run once. Needs network. Safe to re-run (npm install is idempotent).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "sei-diagrams setup"
echo "  skill dir: $SKILL_DIR"

if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: node is not on PATH. Install Node.js 18+ and retry." >&2
  exit 1
fi
echo "  node:      $(node -v)"

if command -v mmdc >/dev/null 2>&1; then
  echo "  mmdc already on PATH ($(command -v mmdc)) — nothing to install."
  echo "  (setup will still add a pinned local copy so renders are reproducible.)"
fi

cd "$SKILL_DIR"
if [ ! -f package.json ]; then
  cat > package.json <<'JSON'
{
  "name": "sei-diagrams-renderer",
  "private": true,
  "description": "Local Mermaid CLI for the sei-diagrams skill",
  "dependencies": {
    "@mermaid-js/mermaid-cli": "^11.4.2",
    "@mermaid-js/layout-elk": "^0.1.7"
  }
}
JSON
  echo "  wrote $SKILL_DIR/package.json"
fi

echo "  installing @mermaid-js/mermaid-cli (+ layout-elk) ... this downloads a headless Chromium once."
npm install --no-audit --no-fund

if [ -x "$SKILL_DIR/node_modules/.bin/mmdc" ]; then
  echo "OK: $("$SKILL_DIR/node_modules/.bin/mmdc" --version 2>/dev/null || echo 'mmdc installed')"
  echo "Done. Render with:  bash $SCRIPT_DIR/render.sh <file-or-dir>"
else
  echo "ERROR: mmdc did not install as expected." >&2
  exit 1
fi
