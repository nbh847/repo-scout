#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELP_OUTPUT="$("$ROOT_DIR/scripts/local-demo.sh" --help)"
SCRIPT_CONTENT="$(cat "$ROOT_DIR/scripts/local-demo.sh")"
README_CONTENT="$(cat "$ROOT_DIR/README.md")"

assert_contains() {
  local content="$1"
  local expected="$2"
  local label="$3"

  if [[ "$content" != *"$expected"* ]]; then
    printf 'Expected %s to contain: %s\n' "$label" "$expected" >&2
    exit 1
  fi
}

assert_contains "$HELP_OUTPUT" "--real" "local-demo help"
assert_contains "$HELP_OUTPUT" "--sample" "local-demo help"
assert_contains "$HELP_OUTPUT" "npm run curate:featured" "local-demo help"
assert_contains "$SCRIPT_CONTENT" 'if [[ -f "$ROOT_DIR/.env.local" ]]; then' "local-demo script"
assert_contains "$SCRIPT_CONTENT" 'source "$ROOT_DIR/.env.local"' "local-demo script"
assert_contains "$README_CONTENT" "scripts/local-demo.sh --real --period daily --limit 20" "README.md"
assert_contains "$README_CONTENT" "scripts/local-demo.sh --real --period weekly --language Python --limit 20" "README.md"
assert_contains "$README_CONTENT" "npm run ingest:trending -- --period daily --limit 20" "README.md"
assert_contains "$README_CONTENT" "npm run ingest:trending -- --period weekly --language Python --limit 20" "README.md"
assert_contains "$README_CONTENT" "npm run curate:featured -- --limit 5" "README.md"
assert_contains "$README_CONTENT" "REPO_SCOUT_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4" "README.md"
assert_contains "$README_CONTENT" "REPO_SCOUT_OPENAI_API_KEY=your-api-key" "README.md"
assert_contains "$README_CONTENT" "REPO_SCOUT_OPENAI_MODEL=glm-4.7" "README.md"
