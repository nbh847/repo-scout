# 技术架构计划

## 推荐技术栈

- 前端：Next.js + TypeScript。
- 样式：Tailwind CSS。
- 后端 API：Python + FastAPI。
- 数据库：SQLite。
- ORM 和迁移：SQLAlchemy + Alembic。
- 后台抓取：Python 脚本，MVP 使用应用内轻量定时任务。
- AI 精选：封装成独立服务层，避免和具体模型供应商强绑定。

## 选择理由

MVP 阶段的重点是尽快跑通“展示、搜索、抓取、入库、AI 精选”的产品闭环。Next.js 适合做展示型网站和交互界面，FastAPI 适合承载项目查询、搜索和后台能力。Python 更适合 GitHub Trending 抓取、数据清洗和 AI 筛选。

SQLite 可以降低早期启动成本，不需要单独维护数据库服务，适合本地开发、demo 和单机部署。MVP 全程使用 SQLite，不把 PostgreSQL 迁移作为当前开发阻塞。SQLAlchemy 让业务代码不直接绑定 SQLite，后续如果数据量、并发或部署需求增长，可以迁移到 PostgreSQL。

## 核心模块

- `web`：页面、布局、UI 组件和客户端交互。
- `api`：榜单、搜索、项目详情和精选专题接口。
- `db`：数据库 schema、迁移和种子数据。
- `ingestion`：GitHub Trending 抓取、解析、标准化和入库。
- `curation`：AI 辅助项目评分和精选专题生成。

## 当前目录结构

- `apps/web`：Next.js 前端应用，当前包含首页 UI 骨架。
- `apps/api`：FastAPI 后端应用，当前包含 SQLAlchemy 模型、示例数据和基础查询接口。
- `docs`：产品、架构、数据模型等稳定文档。
- `data`：本地 SQLite 数据目录，不提交到 Git。

## 数据模型草案

- `Repository`：仓库稳定身份和基础元数据。
- `RepositorySnapshot`：某次抓取时的 stars、forks、语言、描述、topics 和榜单位置。
- `TrendingRun`：一次抓取任务的来源、日期、语言过滤条件和执行状态。
- `FeaturedCollection`：精选专题，例如“适合初学者的 AI 工具”。
- `FeaturedRepository`：某个精选专题下的项目和入选理由。

详细字段、约束和索引见 [数据模型设计](./data-model.md)。

## 数据抓取流程

1. 按周期和语言抓取 GitHub Trending。
2. 解析仓库 owner、name、URL、描述、语言、stars、forks 和周期新增 stars。
3. 按 owner 和 name upsert 仓库记录。
4. 为本次抓取写入榜单快照。
5. 可选：把候选项目传入 AI 精选层。
6. 存储 AI 精选项目和入选理由。

## AI 精选方案

AI 精选采用“规则评分优先，AI 生成解释”的方案。排序主体由可复现的规则完成，AI 不直接决定最终榜单，避免模型波动影响结果稳定性。

核心流程：

1. 从最新成功的 GitHub Trending 抓取结果中取候选项目。
2. 使用规则评分筛选候选项目，评分维度包括 AI 相关度、初学者友好度、学习价值、活跃度和热度增长。
3. 按综合分生成候选短名单，并按专题目标分组，例如“新手友好 AI 项目”“值得关注的开发工具”。
4. 调用 AI 为入选项目生成简短入选理由和专题说明。
5. 将专题、项目排序、评分和入选理由写入精选表。

规则评分负责可解释的筛选和排序，AI 只负责把结构化评分结果转成用户能理解的理由。模型供应商通过独立服务层封装，业务代码只依赖统一的 curation 接口；MVP 默认使用“规则评分 + 本地模板理由”运行，保证没有模型配置时也不阻塞核心流程。配置 OpenAI-compatible 模型环境变量后，再启用 AI 生成理由。

AI 模型配置默认规则：

- `AI_PROVIDER` 默认可选值为 `openai_compatible`。
- `AI_MODEL` 指定实际模型名称。
- `AI_BASE_URL` 和 `AI_API_KEY` 从环境变量读取，不写入代码和文档示例值。
- 缺少模型配置时，精选流程必须自动降级为本地模板理由，不报错中断。

MVP 不做完整个性化推荐，不读取用户行为，也不要求项目 README 深度抓取。后续如果要提升精选质量，再增加 GitHub README、topics、release 活跃度和 issue 活跃度等数据源。

## API 草案

- `GET /api/repositories/trending`：获取热门项目榜单，支持 `period` 和 `language` 查询参数，读取匹配条件下最新一次成功抓取 run。
- `GET /api/repositories/search`：关键词搜索。
- `GET /api/repositories/:owner/:name`：获取项目详情；如果项目已进入精选专题，同时返回入选理由和评分；如果存在历史快照，同时返回最近两次快照的 stars 趋势差值。
- `GET /api/featured`：获取 AI 精选专题。
- `GET /api/featured/:slug`：获取单个 AI 精选专题，用于专题页。
- `POST /api/admin/ingest/trending`：本地或管理员手动触发抓取。
- `POST /api/admin/curate`：本地或管理员手动触发 AI 精选生成。

当前已实现前四个查询接口、`GET /health`、`POST /api/admin/ingest/trending` 和 `POST /api/admin/curate`。首页在没有关键词搜索时会把周期和语言筛选透传给 `/api/repositories/trending`；有关键词搜索时使用 `/api/repositories/search`，不混入 Trending 周期筛选，但会继续透传语言筛选。

`POST /api/admin/ingest/trending` 的 MVP 权限策略：

- 允许本地开发环境调用。
- 非本地调用必须携带简单 admin token。
- token 从环境变量读取，不提交默认密钥。
- MVP 不引入用户系统、角色权限或后台管理界面。

`POST /api/admin/curate` 复用同一套 MVP 权限策略。它从最新成功的 GitHub Trending run 读取候选项目，使用规则评分生成 `beginner-friendly-ai`、`ai-agent-projects`、`llm-tools` 和 `notable-developer-tools` 精选专题。缺少模型配置时，使用本地模板理由并将 `model_name` 写为 `local-template`。

本地手动生成精选专题可运行：

```bash
npm run curate:featured -- --limit 5
```

## 定时任务和部署默认

MVP 只面向本地或单机部署，不考虑远程多机部署。定时抓取使用应用内轻量调度，避免引入 Celery、Redis 或独立队列。定时任务和手动抓取必须复用同一套 ingestion 逻辑，并避免同时写入同一个 SQLite 数据库文件。

应用内定时抓取通过环境变量启用：

- `REPO_SCOUT_TRENDING_SCHEDULER_ENABLED=1`：启动后台定时抓取。
- `REPO_SCOUT_TRENDING_INTERVAL_SECONDS`：抓取间隔，默认 86400 秒。
- `REPO_SCOUT_TRENDING_PERIOD`：抓取周期，默认 `daily`。
- `REPO_SCOUT_TRENDING_LANGUAGE`：可选语言过滤。
- `REPO_SCOUT_TRENDING_LIMIT`：抓取数量上限，默认 20。

调度抓取和手动抓取共享同一个进程内锁。已有抓取运行时，定时任务会跳过本轮，手动触发接口返回 409。

远程部署、外部调度器、PostgreSQL、多实例运行和完整运维配置都放到产品增强阶段单独规划。当前 Agent 开发时不应因这些事项停下来询问，除非任务明确进入部署或数据库迁移阶段。

## 已确认开发默认

- AI 精选默认先用规则评分和本地模板理由；配置 OpenAI-compatible 模型后再启用 AI 生成理由。
- 定时抓取默认使用应用内轻量调度。
- MVP 全程使用 SQLite；PostgreSQL 仅在触发迁移条件后再规划。
- 手动抓取接口默认只支持本地调用或简单 admin token。
- 当前只考虑本地和单机部署，不考虑远程机器部署。
