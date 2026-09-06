#!/usr/bin/env bash
# Thin wrapper around scripts/mdreport.py.
# Build a Markdown and/or HTML report from one or more SEI artifact Markdown files.
#
# Examples:
#   scripts/build-report.sh architecture/atam/atam-report.md --format html --embed-diagrams
#   scripts/build-report.sh architecture/qaw/qaw-report.md --format both --out architecture/reports/
#   scripts/build-report.sh architecture/docs/*.md --format html --title "Architecture Description" \
#     --out architecture/reports/architecture-description.html
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
[ -n "$PY" ] || { echo "ERROR: python 3 not found" >&2; exit 1; }
exec "$PY" "$SCRIPT_DIR/mdreport.py" "$@"
