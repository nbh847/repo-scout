#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOC_CONTENT="$(cat "$ROOT_DIR/docs/mvp-release-checklist.md")"
README_CONTENT="$(cat "$ROOT_DIR/README.md")"
RISK_CONTENT="$(cat "$ROOT_DIR/docs/dependency-risks.md")"
READINESS_CONTENT="$(cat "$ROOT_DIR/docs/release-readiness.md")"

[[ "$DOC_CONTENT" == *"## 当前 MVP 能力"* ]]
[[ "$DOC_CONTENT" == *"## 发布前检查项"* ]]
[[ "$DOC_CONTENT" == *"## 验证命令"* ]]
[[ "$DOC_CONTENT" == *"## 已知风险"* ]]
[[ "$DOC_CONTENT" == *"npm run ingest:trending -- --period daily --limit 20"* ]]
[[ "$DOC_CONTENT" == *"npm run curate:featured -- --limit 5"* ]]
[[ "$DOC_CONTENT" == *"npm run build:web"* ]]
[[ "$README_CONTENT" == *"./docs/mvp-release-checklist.md"* ]]
[[ "$README_CONTENT" == *"./docs/dependency-risks.md"* ]]
[[ "$README_CONTENT" == *"./docs/release-readiness.md"* ]]
[[ "$DOC_CONTENT" == *"./dependency-risks.md"* ]]
[[ "$RISK_CONTENT" == *"npm audit --omit=dev"* ]]
[[ "$RISK_CONTENT" == *"next@9.3.3"* ]]
[[ "$RISK_CONTENT" == *"16.2.9"* ]]
[[ "$READINESS_CONTENT" == *"不适合直接公开生产发布"* ]]
[[ "$READINESS_CONTENT" == *"scripts/local-demo.sh --sample"* ]]
[[ "$READINESS_CONTENT" == *"scripts/validate-local-release.sh"* ]]
[[ "$READINESS_CONTENT" == *"scripts/test-validate-local-release.sh"* ]]
