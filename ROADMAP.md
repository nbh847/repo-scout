# Repo Scout 路线图

## 当前阶段

真实数据版建设。

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

## 进行中

- 将前端示例数据切换为后端 API 数据。

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
- 调用 AI 生成入选理由和专题分类。
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

- 添加热门数据定时更新能力。
- 添加手动触发抓取的后端接口。

## 阻塞

- AI 精选方案未确认。
- SQLite 迁移到 PostgreSQL 的时机未确认。

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
