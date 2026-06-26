# MVP 发布就绪摘要

## 当前判断

Repo Scout 当前适合进入本地演示版和单机自用版验收，不适合直接公开生产发布。

原因：

- MVP 核心产品闭环已经跑通：首页浏览、搜索、周期/语言筛选、项目详情、精选专题页、GitHub Trending 抓取、AI 精选生成、本地演示脚本和运行验收记录均已具备。
- 当前设计明确限定为本地或单机部署，数据库仍为 SQLite。
- 仍存在 Next.js 内部 `postcss@8.4.31` 的 moderate audit 风险，尚无合适的非破坏性修复路径。

## 已处理事项

- 本地数据闭环：`npm run ingest:trending`、`npm run curate:featured` 和 `scripts/local-demo.sh` 可串起抓取、精选和页面展示。
- 后端接口：健康检查、榜单、搜索、项目详情、精选专题、单专题详情、手动抓取和手动精选生成已实现。
- 前端页面：首页、搜索筛选、周期/语言筛选、明星项目栏、项目详情页和精选专题页已实现，并完成移动端间距和长文本优化。
- 项目信号：详情页已展示精选理由、评分和基于最近两条历史快照计算的 stars 趋势变化。
- 权限边界：admin 能力默认允许本地调用，非本地调用需要 `REPO_SCOUT_ADMIN_TOKEN`。
- 并发边界：定时抓取和手动抓取共享进程内锁，避免同进程内并发写 SQLite。
- 文档闭环：README、MVP 范围、架构、数据模型、运行验收、MVP 发布检查和依赖风险记录已补齐。

## 剩余风险

- Next.js 内部 `postcss@8.4.31` 漏洞仍由 `npm audit --omit=dev` 报告，细节见 [依赖风险记录](./dependency-risks.md)。
- SQLite 仅适合本地或单机低并发写入，不适合多实例部署。
- 当前 AI 精选默认使用本地模板理由，未验证真实模型生成路径。
- 浏览器截图验收未完成，当前仅有 API 响应和页面 HTML 运行证据，细节见 [运行验收记录](./runtime-acceptance.md)。

## 发布前必须确认

- 不做公开生产发布，除非 Next/PostCSS 风险已有可验证修复。
- 不做远程多机部署，除非先重新设计数据库和调度方案。
- 不提交 `.env`、API key、token、本地数据库或运行日志。
- 如需演示，优先使用本地端到端脚本：

```bash
scripts/local-demo.sh --sample
```

或真实数据：

```bash
scripts/local-demo.sh --real --period daily --limit 20
```

## 验证基线

每次准备交付前优先运行完整本地发布验证：

```bash
scripts/validate-local-release.sh
```

该脚本会按顺序运行后端严格 warning 测试、后端编译、前端测试、lint、typecheck、build、本地演示脚本文档检查、MVP 发布清单检查、发布验证脚本自检、本地运行数据未被 Git 跟踪检查、敏感文件未被 Git 跟踪检查、脚本语法检查和 `git diff --check`。

如需拆分排查，可按相同顺序单独运行：

```bash
apps/api/.venv/bin/python -m unittest discover apps/api/tests
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
```
