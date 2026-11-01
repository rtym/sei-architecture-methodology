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
  echo "  (setup will still install the lockfile-pinned local copy so renders are reproducible.)"
fi

cd "$SKILL_DIR"
if [ ! -f package.json ]; then
  cat > package.json <<'JSON'
{
  "name": "sei-diagrams-renderer",
  "private": true,
  "description": "Local Mermaid CLI for the sei-diagrams skill",
  "dependencies": {
    "@mermaid-js/mermaid-cli": "^12.0.0",
    "@mermaid-js/layout-elk": "^1.0.1"
  }
}
JSON
  echo "  wrote $SKILL_DIR/package.json"
fi

echo "  installing @mermaid-js/mermaid-cli (+ layout-elk) ... this downloads a headless Chromium once."
if [ -f package-lock.json ]; then
  # The committed lockfile pins the exact renderer versions: same PNGs on every machine and in CI.
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi

# npm may block puppeteer's postinstall (its allow-scripts guard), and a cached browser from an
# older puppeteer may not match the build this one expects — ensure it explicitly. Idempotent:
# a present, matching browser is a no-op.
if [ -x "$SKILL_DIR/node_modules/.bin/puppeteer" ]; then
  "$SKILL_DIR/node_modules/.bin/puppeteer" browsers install chrome-headless-shell
  "$SKILL_DIR/node_modules/.bin/puppeteer" browsers install chrome
fi

if [ -x "$SKILL_DIR/node_modules/.bin/mmdc" ]; then
  echo "OK: $("$SKILL_DIR/node_modules/.bin/mmdc" --version 2>/dev/null || echo 'mmdc installed')"
  echo "Done. Render with:  bash $SCRIPT_DIR/render.sh <file-or-dir>"
else
  echo "ERROR: mmdc did not install as expected." >&2
  exit 1
fi
