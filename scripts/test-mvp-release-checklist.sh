#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOC_CONTENT="$(cat "$ROOT_DIR/docs/mvp-release-checklist.md")"
README_CONTENT="$(cat "$ROOT_DIR/README.md")"
README_EN_CONTENT="$(cat "$ROOT_DIR/README.en.md")"
RISK_CONTENT="$(cat "$ROOT_DIR/docs/dependency-risks.md")"
READINESS_CONTENT="$(cat "$ROOT_DIR/docs/release-readiness.md")"

assert_contains() {
  local content="$1"
  local expected="$2"
  local label="$3"

  if [[ "$content" != *"$expected"* ]]; then
    printf 'Expected %s to contain: %s\n' "$label" "$expected" >&2
    exit 1
  fi
}

assert_contains "$DOC_CONTENT" "## 当前 MVP 能力" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "## 发布前检查项" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "## 验证命令" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "## 已知风险" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "npm run ingest:trending -- --period daily --limit 20" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "npm run curate:featured -- --limit 5" "docs/mvp-release-checklist.md"
assert_contains "$DOC_CONTENT" "npm run build:web" "docs/mvp-release-checklist.md"
assert_contains "$README_CONTENT" "./docs/mvp-release-checklist.md" "README.md"
assert_contains "$README_CONTENT" "./docs/dependency-risks.md" "README.md"
assert_contains "$README_CONTENT" "./docs/release-readiness.md" "README.md"
assert_contains "$README_EN_CONTENT" "./docs/mvp-release-checklist.md" "README.en.md"
assert_contains "$README_EN_CONTENT" "./docs/dependency-risks.md" "README.en.md"
assert_contains "$README_EN_CONTENT" "./docs/release-readiness.md" "README.en.md"
assert_contains "$README_EN_CONTENT" "product enhancement stage" "README.en.md"
assert_contains "$README_EN_CONTENT" "scripts/local-demo.sh --real --period daily --limit 20" "README.en.md"
assert_contains "$README_EN_CONTENT" "scripts/validate-local-release.sh" "README.en.md"
assert_contains "$DOC_CONTENT" "./dependency-risks.md" "docs/mvp-release-checklist.md"
assert_contains "$RISK_CONTENT" "npm audit --omit=dev" "docs/dependency-risks.md"
assert_contains "$RISK_CONTENT" "next@9.3.3" "docs/dependency-risks.md"
assert_contains "$RISK_CONTENT" "16.2.9" "docs/dependency-risks.md"
assert_contains "$READINESS_CONTENT" "不适合直接公开生产发布" "docs/release-readiness.md"
assert_contains "$READINESS_CONTENT" "scripts/local-demo.sh --sample" "docs/release-readiness.md"
assert_contains "$READINESS_CONTENT" "scripts/validate-local-release.sh" "docs/release-readiness.md"
assert_contains "$READINESS_CONTENT" "scripts/test-validate-local-release.sh" "docs/release-readiness.md"
