#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: scripts/validate-local-release.sh

Runs the local release validation baseline in a safe sequential order.
This script does not deploy, publish, migrate databases, or modify secrets.
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

cd "$ROOT_DIR"

apps/api/.venv/bin/python -W error::ResourceWarning -m unittest discover apps/api/tests
apps/api/.venv/bin/python -m compileall apps/api/app
npm run test:web
npm run lint:web
npm --workspace apps/web run typecheck
npm run build:web
scripts/test-local-demo.sh
scripts/test-mvp-release-checklist.sh
scripts/test-validate-local-release.sh
scripts/check-local-data-untracked.sh
scripts/check-sensitive-files-untracked.sh
bash -n scripts/local-demo.sh
bash -n scripts/check-local-data-untracked.sh
bash -n scripts/check-sensitive-files-untracked.sh
bash -n scripts/test-local-demo.sh
bash -n scripts/test-mvp-release-checklist.sh
bash -n scripts/validate-local-release.sh
bash -n scripts/test-validate-local-release.sh
git diff --check
