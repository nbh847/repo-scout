#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

tracked_runtime_data="$(
  git ls-files |
    grep -E '(^data/|/data/|\.db$|\.sqlite3?$)' || true
)"

if [[ -n "$tracked_runtime_data" ]]; then
  printf 'Runtime data files must not be tracked by git:\n%s\n' "$tracked_runtime_data" >&2
  exit 1
fi
