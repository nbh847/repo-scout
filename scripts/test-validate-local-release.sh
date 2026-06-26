#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_CONTENT="$(cat "$ROOT_DIR/scripts/validate-local-release.sh")"
CHECKLIST_CONTENT="$(cat "$ROOT_DIR/docs/mvp-release-checklist.md")"

assert_contains() {
  local content="$1"
  local expected="$2"
  local label="$3"

  if [[ "$content" != *"$expected"* ]]; then
    printf 'Expected %s to contain: %s\n' "$label" "$expected" >&2
    exit 1
  fi
}

EXPECTED_COMMANDS=(
  "apps/api/.venv/bin/python -W error::ResourceWarning -m unittest discover apps/api/tests"
  "apps/api/.venv/bin/python -m compileall apps/api/app"
  "npm run test:web"
  "npm run lint:web"
  "npm --workspace apps/web run typecheck"
  "npm run build:web"
  "scripts/validate-runtime.sh"
  "scripts/test-local-demo.sh"
  "scripts/test-mvp-release-checklist.sh"
  "scripts/test-runtime-validation.sh"
  "scripts/test-validate-local-release.sh"
  "scripts/check-local-data-untracked.sh"
  "scripts/check-sensitive-files-untracked.sh"
  "bash -n scripts/local-demo.sh"
  "bash -n scripts/validate-runtime.sh"
  "bash -n scripts/check-local-data-untracked.sh"
  "bash -n scripts/check-sensitive-files-untracked.sh"
  "bash -n scripts/test-local-demo.sh"
  "bash -n scripts/test-mvp-release-checklist.sh"
  "bash -n scripts/test-runtime-validation.sh"
  "bash -n scripts/validate-local-release.sh"
  "bash -n scripts/test-validate-local-release.sh"
  "git diff --check"
)

for command in "${EXPECTED_COMMANDS[@]}"; do
  assert_contains "$SCRIPT_CONTENT" "$command" "scripts/validate-local-release.sh"
done

previous_line=0
for command in "${EXPECTED_COMMANDS[@]}"; do
  line_number="$(grep -Fn "$command" "$ROOT_DIR/scripts/validate-local-release.sh" | cut -d: -f1 | head -n 1)"
  if [[ -z "$line_number" ]]; then
    printf 'Expected scripts/validate-local-release.sh to contain: %s\n' "$command" >&2
    exit 1
  fi
  if [[ "$line_number" -le "$previous_line" ]]; then
    printf 'Expected command after line %s: %s\n' "$previous_line" "$command" >&2
    exit 1
  fi
  previous_line="$line_number"
done

assert_contains "$CHECKLIST_CONTENT" "scripts/validate-local-release.sh" "docs/mvp-release-checklist.md"
