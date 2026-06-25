#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_PYTHON="$ROOT_DIR/apps/api/.venv/bin/python"
API_UVICORN="$ROOT_DIR/apps/api/.venv/bin/uvicorn"
MODE="real"
PERIOD="daily"
LIMIT="20"
LANGUAGE=""

usage() {
  cat <<'EOF'
Usage: scripts/local-demo.sh [--real|--sample] [--period daily|weekly|monthly] [--limit N] [--language NAME]

Runs Repo Scout's local demo loop:
  1. Load repository data with GitHub Trending (--real) or seed data (--sample).
  2. Generate featured collections with npm run curate:featured.
  3. Start the FastAPI backend and Next.js frontend.

Examples:
  scripts/local-demo.sh --real --period daily --limit 20
  scripts/local-demo.sh --sample

Requires:
  - apps/api/.venv with the API package installed
  - npm dependencies installed
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --real)
      MODE="real"
      shift
      ;;
    --sample)
      MODE="sample"
      shift
      ;;
    --period)
      PERIOD="${2:-}"
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      shift 2
      ;;
    --language)
      LANGUAGE="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -x "$API_PYTHON" || ! -x "$API_UVICORN" ]]; then
  echo "Missing API virtualenv. Run the backend setup from README.md first." >&2
  exit 1
fi

cd "$ROOT_DIR"

if [[ "$MODE" == "real" ]]; then
  ingest_args=(--period "$PERIOD" --limit "$LIMIT")
  if [[ -n "$LANGUAGE" ]]; then
    ingest_args+=(--language "$LANGUAGE")
  fi
  npm run ingest:trending -- "${ingest_args[@]}"
else
  npm run seed:api
fi

npm run curate:featured -- --limit 5

"$API_UVICORN" app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000 &
API_PID="$!"
npm --workspace apps/web run dev &
WEB_PID="$!"

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Repo Scout local demo is running:"
echo "- API: http://127.0.0.1:8000/health"
echo "- Web: http://127.0.0.1:3000"
echo "Press Ctrl+C to stop both servers."

wait
