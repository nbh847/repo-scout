#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_CONTENT="$(cat "$ROOT_DIR/scripts/validate-local-release.sh")"
CHECKLIST_CONTENT="$(cat "$ROOT_DIR/docs/mvp-release-checklist.md")"

EXPECTED_COMMANDS=(
  "apps/api/.venv/bin/python -W error::ResourceWarning -m unittest discover apps/api/tests"
  "apps/api/.venv/bin/python -m compileall apps/api/app"
  "npm run test:web"
  "npm run lint:web"
  "npm --workspace apps/web run typecheck"
  "npm run build:web"
  "scripts/test-local-demo.sh"
  "scripts/test-mvp-release-checklist.sh"
  "scripts/test-validate-local-release.sh"
  "bash -n scripts/local-demo.sh"
  "bash -n scripts/test-local-demo.sh"
  "bash -n scripts/test-mvp-release-checklist.sh"
  "bash -n scripts/validate-local-release.sh"
  "bash -n scripts/test-validate-local-release.sh"
  "git diff --check"
)

for command in "${EXPECTED_COMMANDS[@]}"; do
  [[ "$SCRIPT_CONTENT" == *"$command"* ]]
done

previous_line=0
for command in "${EXPECTED_COMMANDS[@]}"; do
  line_number="$(grep -Fn "$command" "$ROOT_DIR/scripts/validate-local-release.sh" | cut -d: -f1 | head -n 1)"
  [[ -n "$line_number" ]]
  [[ "$line_number" -gt "$previous_line" ]]
  previous_line="$line_number"
done

[[ "$CHECKLIST_CONTENT" == *"scripts/validate-local-release.sh"* ]]
