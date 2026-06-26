#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELP_OUTPUT="$("$ROOT_DIR/scripts/local-demo.sh" --help)"
README_CONTENT="$(cat "$ROOT_DIR/README.md")"

[[ "$HELP_OUTPUT" == *"--real"* ]]
[[ "$HELP_OUTPUT" == *"--sample"* ]]
[[ "$HELP_OUTPUT" == *"npm run curate:featured"* ]]
[[ "$README_CONTENT" == *"scripts/local-demo.sh --real --period daily --limit 20"* ]]
[[ "$README_CONTENT" == *"scripts/local-demo.sh --real --period weekly --language Python --limit 20"* ]]
[[ "$README_CONTENT" == *"npm run ingest:trending -- --period daily --limit 20"* ]]
[[ "$README_CONTENT" == *"npm run ingest:trending -- --period weekly --language Python --limit 20"* ]]
[[ "$README_CONTENT" == *"npm run curate:featured -- --limit 5"* ]]
