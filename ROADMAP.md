# Repo Scout 路线图

## 当前阶段

产品增强版建设。

## 已完成

- 创建 GitHub 仓库。
- 添加项目名称和基础描述。
- 添加 `.gitignore`，忽略敏感文件、本地文件、依赖、日志、构建产物和本地数据库。
- 梳理产品定位和计划功能范围。
- 定义 MVP 范围。
- 起草技术架构计划。
- 将公开文档调整为中文为主，并新增英文 README。
- 确认 MVP 技术栈：Next.js、TypeScript、Tailwind CSS、Python、FastAPI、SQLite、SQLAlchemy、Alembic。
- 定义仓库、榜单快照、抓取记录和 AI 精选集合的数据表结构。
- 搭建 `apps/web` Next.js 前端骨架。
- 搭建 `apps/api` FastAPI 后端骨架。
- 实现首页 UI 骨架，包含搜索入口、榜单和 AI 精选专题栏。
- 实现后端 SQLAlchemy 模型、示例数据和基础查询接口。
- 实现 GitHub Trending 抓取，支持 `daily`、`weekly`、`monthly` 和可选语言过滤。
- 实现 Trending HTML 解析、仓库 upsert、抓取运行记录和榜单快照写入。
- 添加手动抓取命令 `npm run ingest:trending -- --period daily --limit 20`。
- 将首页视觉从营销页调整为开源发现工作台布局，包含侧边导航、榜单工作区和右侧洞察面板。
- 使用 Open Design 记录首页极客风工作台设计，并将前端首页改造为深色终端雷达风格。
- 优化首页极客风工作台的信息密度，让侧栏、榜单和状态面板更清爽。
- 将首页榜单、搜索和精选专题面板从硬编码示例数据切换为后端 API 数据源，并增加 API 不可用时的降级状态。
- 完成前端连接本地 FastAPI 服务后的真实数据渲染验证。
- 修复热门榜单 API 混合多次抓取快照导致首页排名编号重复的问题，榜单现在只读取最新一次成功抓取 run。
- 将首页改造成参考练手项目站点的布局：顶部导航、居中 Hero、搜索筛选区、项目卡片网格和右侧明星项目栏。
- 调整首页参考布局的筛选文案和展示密度，将主筛选改为“全部项目 / 好玩 / 好用”，并收紧搜索区、卡片和右侧栏间距。
- 优化首页主筛选按钮交互，将跳转改为同页平滑滚动，并为目标区域增加滚动偏移。
- 将首页主筛选按钮分别映射到对应区域：“全部项目”到搜索区，“好玩”到项目卡片网格，“好用”到右侧明星项目栏。
- 固定前端开发服务端口为 `3000`，避免端口占用时自动启动第二个 Next dev server。
- 确认 AI 精选方案：规则评分负责候选筛选和排序，AI 负责生成入选理由和专题说明。
- 将 GitHub Trending HTML 解析从标准库 `HTMLParser` 状态机切换为 BeautifulSoup。
- 确认开发默认：AI 精选先用本地模板降级，定时抓取用应用内轻量调度，MVP 全程使用 SQLite，手动抓取接口使用本地调用或简单 admin token，当前只考虑单机部署。
- 添加热门数据应用内定时更新能力，可通过环境变量启用后台调度。
- 添加手动触发 GitHub Trending 抓取的后端接口 `POST /api/admin/ingest/trending`，支持本地调用或 admin token，并与定时任务共享抓取锁。
- 添加 AI 精选生成能力，支持从最新 Trending run 规则评分生成精选专题和本地模板理由。
- 添加手动触发 AI 精选生成的后端接口 `POST /api/admin/curate` 和本地命令 `npm run curate:featured -- --limit 5`。
- 首页展示真实 AI 精选专题数据，右侧明星项目栏读取 `/api/featured`，并在 API 不可用时回退到 Trending 项目。
- 添加项目详情页 `/repositories/[owner]/[name]`，展示仓库核心信息、GitHub 链接、精选理由和规则评分。
- 扩展项目详情 API，精选项目会返回“为什么值得关注”的入选理由和学习评分。
- 添加本地端到端演示脚本 `scripts/local-demo.sh`，支持真实 GitHub Trending 数据和无网络示例数据两种模式。
- 更新 README 本地开发说明，覆盖依赖安装、真实数据抓取、AI 精选生成、前后端启动和访问入口。
- 优化首页和项目详情页移动端体验，收紧手机端间距、卡片高度和长仓库名换行。
- 增加本地真实运行验收记录 `docs/runtime-acceptance.md`，记录 API、首页、详情页和移动端响应式证据。
- 增加 MVP 发布检查清单 `docs/mvp-release-checklist.md`，集中记录当前能力、发布前检查项、验证命令和已知风险。
- 跟进 Next.js 嵌套 `postcss` 漏洞风险，新增 `docs/dependency-risks.md` 记录 audit 结果、上游状态和当前不采用 `npm audit fix --force` 的原因。
- 增加 MVP 发布就绪摘要 `docs/release-readiness.md`，明确当前适合本地演示/单机自用验收，不适合直接公开生产发布。
- 修复前端 `typecheck` 单独运行依赖 `.next/types` 已存在的问题，改为先执行 `next typegen` 再运行 `tsc --noEmit`。
- 已按功能边界提交 MVP 真实数据闭环、AI 精选、前端详情页、本地演示脚本和发布准备文档。
- 首页支持按 GitHub Trending 周期筛选 `daily`、`weekly`、`monthly`。
- 首页支持按语言筛选 Trending 数据，并将筛选参数透传到后端 `/api/repositories/trending`。
- 首页关键词搜索支持叠加语言筛选，并将语言参数透传到后端 `/api/repositories/search`。
- 项目详情页支持展示基于最近两条历史快照计算的 stars 趋势变化。
- 增加精选专题页 `/collections/[slug]`，展示专题说明、入选项目、理由和评分。
- AI 精选生成支持新手友好、AI Agent、LLM 工具和开发工具四类专题。
- 增加本地发布前完整验证脚本 `scripts/validate-local-release.sh`，按安全顺序运行后端、前端、构建、脚本和 diff 检查。
- 补齐本地发布前完整验证脚本的自检覆盖，确保脚本测试、脚本语法检查和关键命令顺序被自动验证。
- 同步发布就绪摘要的验证基线，明确优先运行完整本地发布验证脚本，并覆盖脚本自检。
- 同步英文 README 的项目阶段、文档入口、本地演示和完整本地发布验证说明。
- 增加本地运行数据未被 Git 跟踪的发布前检查，防止 SQLite 数据库文件进入版本控制。
- 增加敏感文件未被 Git 跟踪的发布前检查，覆盖 `.env`、密钥和证书类文件。

## 进行中

- 本地发布前硬化：不部署远程，继续处理本地验证、依赖风险和文档一致性。

## 功能开发计划

### 阶段 1：MVP 可用版

目标：先做出一个能浏览、搜索、展示热门项目的网站。

- 搭建 `Next.js + TypeScript + Tailwind CSS` 项目。
- 接入 `SQLite + SQLAlchemy + Alembic`。
- 设计基础数据表：仓库、榜单快照、抓取记录、精选专题。
- 首页展示 GitHub 热门项目榜单。
- 支持关键词搜索。
- 项目详情页展示基础信息。
- 使用假数据或种子数据完成第一版页面闭环。

### 阶段 2：真实数据版

目标：让数据来自 GitHub Trending，而不是手写。

- 实现 GitHub Trending 抓取脚本。
- 解析项目名、owner、描述、语言、stars、forks、新增 stars。
- 写入数据库并处理去重。
- 支持手动触发抓取。
- 首页和搜索改为读取真实数据库数据。
- 增加基础错误处理和抓取日志。

### 阶段 3：AI 精选版

目标：实现 AI 自动筛选明星项目专题栏。

- 定义 AI 筛选标准：适合初学者、文档质量、活跃度、学习价值、AI 相关度。
- 从 Trending 项目中筛选候选项目。
- 使用规则评分确定候选短名单和排序。
- 调用 AI 生成入选理由和专题说明。
- 存储精选专题和精选项目。
- 首页展示 AI 精选专题栏。
- 项目详情页展示“为什么值得关注”。

### 阶段 4：产品增强版

目标：从 demo 变成真正可持续使用的项目发现工具。

- 定时抓取 GitHub Trending。
- 支持语言筛选，比如 Python、TypeScript、Go。
- 支持周期筛选，比如 daily、weekly、monthly。
- 增加项目趋势变化，比如 stars 增长趋势。
- 增加专题页，比如“AI Agent 项目”“LLM 工具”“新手友好项目”。
- 优化 UI 视觉和移动端体验。
- 部署上线，配置数据库和环境变量。

## 下一步

- 继续本地发布前硬化，不做远程部署。
- 未进入发布前，继续跟进 Next.js 内部 `postcss@8.4.31` 上游修复状态。
- 后续本地交付优先运行 `scripts/validate-local-release.sh`，避免并行执行 `typecheck` 和 `build:web`。

## 阻塞

- 暂无。

## 已知风险

- `npm audit --omit=dev` 仍报告 Next.js 内部固定依赖 `postcss@8.4.31` 的 moderate 漏洞；项目已将直接依赖 `postcss` 升级到安全版本，并尝试使用 npm `overrides`，但 Next 嵌套依赖未被覆盖。后续需要跟进 Next.js 上游修复或更换到已修复版本。

## 最近验证

- 2026-06-25：已验证 README 和路线图文档内容。
- 2026-06-25：已验证 MVP 和架构文档内容。
- 2026-06-25：已验证中文主文档和英文 README 内容。
- 2026-06-25：已将 4 阶段功能开发计划写入路线图。
- 2026-06-25：已将技术栈调整为 Next.js、FastAPI、SQLite、SQLAlchemy 和 Alembic。
- 2026-06-25：已验证数据模型设计文档内容。
- 2026-06-25：已完成前端首页和后端查询接口骨架。
- 2026-06-25：已通过 `npm run lint:web`、`npm run build:web`、`python3 -m compileall apps/api/app`。
- 2026-06-25：已通过本地接口检查：`GET /health`、`GET /api/repositories/trending`、`GET /api/repositories/search`、`GET /api/featured`。
- 2026-06-25：已启动前端预览服务并确认 `http://127.0.0.1:3000` 返回 200。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`，共 8 个测试。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m compileall apps/api/app`。
- 2026-06-25：已通过真实 GitHub Trending 抓取验证：`python -m app.github_trending --period daily --limit 3` 写入 1 次成功 run 和 3 条快照。
- 2026-06-25：已通过 `npm run lint:web` 和 `npm run build:web` 验证首页工作台视觉改造。
- 2026-06-25：已重启前端开发服务并确认 `http://127.0.0.1:3000` 返回 200。
- 2026-06-25：已通过 `npm run lint:web` 和 `npm run build:web` 验证首页极客风工作台视觉改造。
- 2026-06-25：已通过 `npm run lint:web`、`npm run build:web` 和 `http://127.0.0.1:3000` 返回 200 验证首页清爽化调整。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页 API 数据源改造。
- 2026-06-25：已启动前端开发服务并确认 `http://127.0.0.1:3001` 返回 200；当前环境后端缺少 `uvicorn`，页面以 API 不可用降级状态渲染。
- 2026-06-25：已通过项目内 `apps/api/.venv/bin/uvicorn app.main:app --reload --app-dir apps/api` 启动后端，并验证 `GET /health`、`GET /api/repositories/trending?limit=3`、`GET /api/repositories/search?q=Python&limit=3`、`GET /api/featured`。
- 2026-06-25：已确认 `http://127.0.0.1:3001/` 渲染真实仓库数据 `langchain-ai/langchain` 和 `open-webui/open-webui`，且不再显示后端不可用降级状态；已确认 `http://127.0.0.1:3001/?q=Python` 渲染搜索结果。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest apps/api/tests/test_github_trending.py`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web` 和 `npm run lint:web` 验证榜单编号修复；已确认 `GET /api/repositories/trending?limit=10` 返回连续 `rank`，首页显示 `#01`、`#02`、`#03`。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页布局改造；已确认 `http://127.0.0.1:3001/` 返回 200，包含新 Hero 文案、右侧明星项目栏和真实仓库数据，且不显示后端不可用降级状态。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页布局细节调整；已确认 `http://127.0.0.1:3001/` 包含“全部项目 / 好玩 / 好用”筛选按钮和右侧明星项目栏。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页主筛选平滑滚动交互调整。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页主筛选区域锚点调整。
- 2026-06-25：已确认 `3000/3001` 无残留监听进程，并通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 验证前端 dev 端口固定为 `3000` 的脚本调整。
- 2026-06-25：已确认 AI 精选采用“规则评分优先，AI 生成解释”的方案，并同步更新 MVP、架构和数据模型文档。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests` 和 `apps/api/.venv/bin/python -m compileall apps/api/app` 验证 GitHub Trending BeautifulSoup 解析切换。
- 2026-06-25：已确认剩余开发默认规则，并同步更新 MVP、架构、数据模型和路线图文档。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app` 和 FastAPI 路由导入检查验证手动抓取接口、admin token 拦截、应用内调度器并发跳过和共享抓取锁。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、FastAPI admin 路由导入检查和 `REPO_SCOUT_DATABASE_URL=sqlite:///:memory: npm run curate:featured -- --limit 2` 验证 AI 精选规则评分、模板理由、重复运行去重、手动触发接口和本地命令入口。
- 2026-06-25：已通过 CodeGraph 确认首页读取 `/api/featured` 渲染右侧明星项目栏，并通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证首页真实 AI 精选专题展示路径。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 验证项目详情 API 精选理由、首页详情链接和 `/repositories/[owner]/[name]` 详情页。
- 2026-06-25：已通过 `scripts/test-local-demo.sh`、`bash -n scripts/local-demo.sh`、`bash -n scripts/test-local-demo.sh`、`npm run dev:api -- --help`、`REPO_SCOUT_DATABASE_URL=sqlite:///:memory: npm run seed:api`、`npm run ingest:trending -- --help` 和 `REPO_SCOUT_DATABASE_URL=sqlite:///:memory: npm run curate:featured -- --limit 2` 验证本地端到端演示脚本、README 命令和 root 数据入口。
- 2026-06-25：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck` 和 `npm run build:web` 对当前真实数据闭环改动做全量回归验证。
- 2026-06-25：已通过 `npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck`、`npm run build:web`、`apps/api/.venv/bin/python -m unittest discover apps/api/tests` 和 `apps/api/.venv/bin/python -m compileall apps/api/app` 验证首页与详情页移动端布局优化。
- 2026-06-25：已启动本地 API 和前端服务，验证 `GET /health`、`GET /api/repositories/trending?limit=1`、`GET /api/featured`、首页 `http://127.0.0.1:3000` 和详情页 `http://127.0.0.1:3000/repositories/calesthio/OpenMontage`；本轮 in-app Browser 和 Playwright 不可用，已将运行验收证据记录到 `docs/runtime-acceptance.md`。
- 2026-06-26：已通过 `scripts/test-mvp-release-checklist.sh` 和 `bash -n scripts/test-mvp-release-checklist.sh` 验证 MVP 发布检查清单和 README 文档入口。
- 2026-06-26：已通过 `npm audit --omit=dev`、`npm ls postcss`、`npm view next version`、`npm view next@15 version`、`npm view next@16 version` 和 `npm view next@16.2.9 engines peerDependencies dependencies.postcss version` 跟进 Next.js 内部 `postcss@8.4.31` 风险；确认当前稳定 Next `16.2.9` 仍未修复，已记录到 `docs/dependency-risks.md`。
- 2026-06-26：已新增 `docs/release-readiness.md`，整理 MVP 当前发布就绪判断、已处理事项、剩余风险和交付前验证基线。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`scripts/test-mvp-release-checklist.sh`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck`、`npm run build:web` 和 `git diff --check` 做提交前完整验证；后端测试仍有 SQLite `ResourceWarning`，测试结果为通过。
- 2026-06-26：已按功能边界提交 `dc9b4ae`、`de98763`、`ed6eec0` 三个提交，覆盖后端抓取/精选、前端真实数据/详情页、文档脚本/发布准备。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck`、`npm run build:web`、`scripts/test-local-demo.sh` 和 `scripts/test-mvp-release-checklist.sh` 验证首页 Trending 周期/语言筛选；后端测试仍有 SQLite `ResourceWarning`，测试结果为通过。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck`、`npm run build:web`、`scripts/test-local-demo.sh`、`scripts/test-mvp-release-checklist.sh` 和 `git diff --check` 验证项目详情页 stars 趋势变化；后端测试仍有 SQLite `ResourceWarning`，测试结果为通过。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest discover apps/api/tests`、`apps/api/.venv/bin/python -m compileall apps/api/app`、`npm run test:web`、`npm run lint:web`、`npm --workspace apps/web run typecheck`、`npm run build:web`、`scripts/test-local-demo.sh`、`scripts/test-mvp-release-checklist.sh` 和 `git diff --check` 验证精选专题页 API、链接生成和页面路由。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -W error::ResourceWarning -m unittest discover apps/api/tests` 验证测试内存 SQLite engine 已显式释放，不再出现 SQLite `ResourceWarning`。
- 2026-06-26：已通过 `npm audit --omit=dev`、`npm view next version` 和 `npm view next@16.2.9 dependencies.postcss engines peerDependencies version` 复查 Next.js 内部 `postcss@8.4.31` 风险；当前稳定 Next `16.2.9` 仍未修复，已更新 `docs/dependency-risks.md`。
- 2026-06-26：已通过 `scripts/validate-local-release.sh` 完成本地发布前完整验证，覆盖后端严格 warning 测试、编译、前端测试、lint、typecheck、build、脚本文档检查和 `git diff --check`。
- 2026-06-26：已先确认 `scripts/test-validate-local-release.sh` 对当前脚本缺口失败，再补齐 `scripts/validate-local-release.sh` 的脚本自检和语法检查，并通过 `scripts/test-validate-local-release.sh`、`bash -n scripts/validate-local-release.sh`、`bash -n scripts/test-validate-local-release.sh` 和 `scripts/validate-local-release.sh` 验证。
- 2026-06-26：已先确认 `scripts/test-mvp-release-checklist.sh` 对发布就绪摘要验证基线缺口失败，再同步 `docs/release-readiness.md`，并通过 `scripts/test-mvp-release-checklist.sh`、`scripts/test-validate-local-release.sh` 和 `git diff --check` 验证。
- 2026-06-26：已修复文档自检脚本中失败断言不可靠的问题，先确认 `scripts/test-mvp-release-checklist.sh` 能捕捉英文 README 缺口，再同步 `README.en.md`，并通过文档脚本验证。
- 2026-06-26：已先确认 `scripts/test-validate-local-release.sh` 对本地数据跟踪检查缺口失败，再新增 `scripts/check-local-data-untracked.sh` 并接入完整本地发布验证。
- 2026-06-26：已先确认 `scripts/test-validate-local-release.sh` 对敏感文件跟踪检查缺口失败，再新增 `scripts/check-sensitive-files-untracked.sh` 并接入完整本地发布验证。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest apps/api/tests/test_github_trending.py` 和 `npm run test:web` 验证关键词搜索叠加语言筛选。
- 2026-06-26：已通过 `apps/api/.venv/bin/python -m unittest apps/api/tests/test_curation.py` 验证 AI Agent 和 LLM 工具精选专题生成。
