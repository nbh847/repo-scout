#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_CONTENT="$(cat "$ROOT_DIR/scripts/validate-local-release.sh")"
CHECKLIST_CONTENT="$(cat "$ROOT_DIR/docs/mvp-release-checklist.md")"

[[ "$SCRIPT_CONTENT" == *"-W error::ResourceWarning"* ]]
[[ "$SCRIPT_CONTENT" == *"npm --workspace apps/web run typecheck"* ]]
[[ "$SCRIPT_CONTENT" == *"npm run build:web"* ]]
[[ "$SCRIPT_CONTENT" == *"git diff --check"* ]]
[[ "$CHECKLIST_CONTENT" == *"scripts/validate-local-release.sh"* ]]
