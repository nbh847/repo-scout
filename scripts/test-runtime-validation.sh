#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_CONTENT="$(cat "$ROOT_DIR/scripts/validate-runtime.sh")"
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

assert_contains "$SCRIPT_CONTENT" "REPO_SCOUT_DATABASE_URL=\"sqlite:///\${DB_PATH}\"" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "cd \"\$ROOT_DIR/apps/web\"" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "node_modules/.bin/next\" dev -H 127.0.0.1 -p \"\$WEB_PORT\"" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "trap cleanup EXIT" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "/api/repositories/trending?limit=3&period=daily" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "/repositories/langchain-ai/langchain" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "/collections/beginner-friendly-ai" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "?period=daily&sort=gained" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "?period=daily&language=Python" "scripts/validate-runtime.sh"
assert_contains "$SCRIPT_CONTENT" "?q=repo-scout-no-match" "scripts/validate-runtime.sh"
assert_contains "$CHECKLIST_CONTENT" "scripts/validate-runtime.sh" "docs/mvp-release-checklist.md"
