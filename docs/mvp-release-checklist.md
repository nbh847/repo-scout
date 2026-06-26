# MVP 发布检查清单

## 当前 MVP 能力

- 首页展示 GitHub Trending 项目榜单，默认读取最新一次成功抓取 run，并支持按 `daily`、`weekly`、`monthly` 和语言筛选匹配 run。
- 支持关键词搜索，覆盖仓库名、描述、语言和 topics。
- 支持项目详情页 `/repositories/[owner]/[name]`，展示仓库核心信息、GitHub 链接、精选理由和规则评分。
- 支持 GitHub Trending 抓取，覆盖 `daily`、`weekly`、`monthly` 和可选语言过滤。
- 支持手动抓取命令：

```bash
npm run ingest:trending -- --period daily --limit 20
npm run ingest:trending -- --period weekly --language Python --limit 20
```

- 支持本地或 admin token 保护的手动抓取接口 `POST /api/admin/ingest/trending`。
- 支持应用内轻量定时抓取，通过 `REPO_SCOUT_TRENDING_SCHEDULER_ENABLED=1` 启用。
- 支持规则评分生成 AI 精选专题，缺少模型配置时使用本地模板理由。
- 支持手动生成精选专题命令：

```bash
npm run curate:featured -- --limit 5
```

- 支持本地或 admin token 保护的精选生成接口 `POST /api/admin/curate`。
- 提供本地端到端演示脚本：

```bash
scripts/local-demo.sh --real --period daily --limit 20
scripts/local-demo.sh --real --period weekly --language Python --limit 20
scripts/local-demo.sh --sample
```

## 发布前检查项

- 确认 `data/` 本地 SQLite 数据库未进入 Git 跟踪。
- 确认 `.env`、token、密钥和模型 API key 未进入仓库。
- 确认 `REPO_SCOUT_ADMIN_TOKEN` 仅在需要非本地 admin 调用时配置。
- 确认没有开启远程多机部署或多实例同时写 SQLite。
- 确认 `REPO_SCOUT_TRENDING_SCHEDULER_ENABLED` 只在需要后台定时抓取的单机环境启用。
- 确认真实数据演示能完成抓取、精选生成、首页展示和详情页访问。
- 确认移动端首页和详情页没有明显横向溢出或文字重叠。
- 确认 `docs/runtime-acceptance.md` 包含最近一次运行验收记录。
- 确认 `docs/dependency-risks.md` 包含最近一次依赖风险跟进记录。
- 确认 README 的本地开发命令与 `package.json` scripts 一致。
- 确认 `ROADMAP.md` 的当前阶段、进行中、下一步和最近验证已同步。

## 验证命令

后端验证：

```bash
apps/api/.venv/bin/python -m unittest discover apps/api/tests
apps/api/.venv/bin/python -m compileall apps/api/app
```

前端验证：

```bash
npm run test:web
npm run lint:web
npm --workspace apps/web run typecheck
npm run build:web
```

脚本文档验证：

```bash
scripts/test-local-demo.sh
scripts/test-mvp-release-checklist.sh
bash -n scripts/local-demo.sh
bash -n scripts/test-local-demo.sh
bash -n scripts/test-mvp-release-checklist.sh
```

本地命令入口验证：

```bash
npm run dev:api -- --help
REPO_SCOUT_DATABASE_URL=sqlite:///:memory: npm run seed:api
npm run ingest:trending -- --help
REPO_SCOUT_DATABASE_URL=sqlite:///:memory: npm run curate:featured -- --limit 2
```

## 已知风险

- `npm audit --omit=dev` 仍报告 Next.js 内部固定依赖 `postcss@8.4.31` 的 moderate 漏洞。项目已将直接依赖 `postcss` 升级到安全版本，并尝试使用 npm `overrides`，但 Next 嵌套依赖未被覆盖，需要跟进 Next.js 上游修复或更换到已修复版本。
- 当前已确认 Next `16.2.9` 仍声明内部 `postcss@8.4.31`，`npm audit fix --force` 会回退到 `next@9.3.3`，不作为当前处理方案。细节见 [依赖风险记录](./dependency-risks.md)。
- 当前数据库默认 SQLite，只适合本地或单机低并发写入，不支持多实例同时写入。
- 当前 AI 精选默认是规则评分加本地模板理由；模型生成理由需要配置 OpenAI-compatible 环境变量后再启用。
- 本轮运行验收没有真实截图，因为 in-app Browser 和 Playwright 均不可用；已用 API 响应和页面 HTML 记录替代证据。
