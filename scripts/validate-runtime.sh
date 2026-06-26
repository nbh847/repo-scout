#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_PORT="${REPO_SCOUT_RUNTIME_API_PORT:-8000}"
WEB_PORT="${REPO_SCOUT_RUNTIME_WEB_PORT:-3000}"
API_URL="http://127.0.0.1:${API_PORT}"
WEB_URL="http://127.0.0.1:${WEB_PORT}"
RUNTIME_DIR="${TMPDIR:-/tmp}/repo-scout-runtime-acceptance-$$"
DB_PATH="${RUNTIME_DIR}/repo_scout.db"
API_LOG="${RUNTIME_DIR}/api.log"
WEB_LOG="${RUNTIME_DIR}/web.log"
API_PID=""
WEB_PID=""

usage() {
  cat <<'EOF'
Usage: scripts/validate-runtime.sh

Starts a temporary local API and web server, validates key pages, then stops
the servers. Uses a temporary SQLite database outside the repository.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

cleanup() {
  if [[ -n "$WEB_PID" ]] && kill -0 "$WEB_PID" >/dev/null 2>&1; then
    kill "$WEB_PID" >/dev/null 2>&1 || true
    wait "$WEB_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "$API_PID" ]] && kill -0 "$API_PID" >/dev/null 2>&1; then
    kill "$API_PID" >/dev/null 2>&1 || true
    wait "$API_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

fail() {
  printf 'Runtime validation failed: %s\n' "$1" >&2
  if [[ -f "$API_LOG" ]]; then
    printf '\n--- API log ---\n' >&2
    tail -n 80 "$API_LOG" >&2
  fi
  if [[ -f "$WEB_LOG" ]]; then
    printf '\n--- Web log ---\n' >&2
    tail -n 80 "$WEB_LOG" >&2
  fi
  exit 1
}

assert_port_free() {
  local port="$1"
  if (echo >"/dev/tcp/127.0.0.1/${port}") >/dev/null 2>&1; then
    fail "port ${port} is already in use"
  fi
}

wait_for_url() {
  local url="$1"
  local label="$2"

  for _ in {1..90}; do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      return
    fi
    sleep 1
  done

  fail "${label} did not become ready at ${url}"
}

assert_url_contains() {
  local url="$1"
  local expected="$2"
  local label="$3"
  local output_file="${RUNTIME_DIR}/${label}.html"

  curl -fsS --max-time 10 "$url" -o "$output_file" || fail "${label} request failed: ${url}"
  grep -q "$expected" "$output_file" || fail "${label} did not contain: ${expected}"
}

cd "$ROOT_DIR"
mkdir -p "$RUNTIME_DIR"

assert_port_free "$API_PORT"
assert_port_free "$WEB_PORT"

REPO_SCOUT_DATABASE_URL="sqlite:///${DB_PATH}" \
  apps/api/.venv/bin/uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port "$API_PORT" \
  >"$API_LOG" 2>&1 &
API_PID="$!"

(
  cd "$ROOT_DIR/apps/web"
  REPO_SCOUT_API_URL="$API_URL" NEXT_TELEMETRY_DISABLED=1 \
    "$ROOT_DIR/node_modules/.bin/next" dev -H 127.0.0.1 -p "$WEB_PORT"
) >"$WEB_LOG" 2>&1 &
WEB_PID="$!"

wait_for_url "${API_URL}/health" "API"
wait_for_url "$WEB_URL" "web"

assert_url_contains "${API_URL}/api/repositories/trending?limit=3&period=daily" "langchain-ai/langchain" "api-trending"
assert_url_contains "$WEB_URL" "Repo Scout 开源雷达" "home"
assert_url_contains "${WEB_URL}/repositories/langchain-ai/langchain" "为什么值得关注" "detail"
assert_url_contains "${WEB_URL}/repositories/langchain-ai/langchain?from=%2F%3Fperiod%3Ddaily%26sort%3Dgained%23ranking" "返回榜单" "detail-return"
assert_url_contains "${WEB_URL}/collections/beginner-friendly-ai" "适合初学者的 AI 项目" "collection"
assert_url_contains "${WEB_URL}/?period=daily&sort=gained" "新增 Stars" "sort"
assert_url_contains "${WEB_URL}/?period=daily&language=Python" "langchain-ai/langchain" "language"
assert_url_contains "${WEB_URL}/?q=repo-scout-no-match" "清除筛选" "empty-state"

printf 'Runtime validation passed: %s\n' "$WEB_URL"
