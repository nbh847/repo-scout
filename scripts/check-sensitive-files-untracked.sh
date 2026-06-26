#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

tracked_sensitive_files="$(
  git ls-files |
    grep -E '(^|/)\.env(\.|$)|\.(pem|key|cert|p12|pfx)$' || true
)"

if [[ -n "$tracked_sensitive_files" ]]; then
  printf 'Sensitive files must not be tracked by git:\n%s\n' "$tracked_sensitive_files" >&2
  exit 1
fi
