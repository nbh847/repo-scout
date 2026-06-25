# 技术架构计划

## 推荐技术栈

- 前端：Next.js + TypeScript。
- 样式：Tailwind CSS。
- 后端 API：Python + FastAPI。
- 数据库：SQLite。
- ORM 和迁移：SQLAlchemy + Alembic。
- 后台抓取：Python 脚本，后续接入定时任务。
- AI 精选：封装成独立服务层，避免和具体模型供应商强绑定。

## 选择理由

MVP 阶段的重点是尽快跑通“展示、搜索、抓取、入库、AI 精选”的产品闭环。Next.js 适合做展示型网站和交互界面，FastAPI 适合承载项目查询、搜索和后台能力。Python 更适合 GitHub Trending 抓取、数据清洗和 AI 筛选。

SQLite 可以降低早期启动成本，不需要单独维护数据库服务，适合本地开发、demo 和单机部署。SQLAlchemy 让业务代码不直接绑定 SQLite，后续如果数据量、并发或部署需求增长，可以迁移到 PostgreSQL。

## 核心模块

- `web`：页面、布局、UI 组件和客户端交互。
- `api`：榜单、搜索、项目详情和精选专题接口。
- `db`：数据库 schema、迁移和种子数据。
- `ingestion`：GitHub Trending 抓取、解析、标准化和入库。
- `curation`：AI 辅助项目评分和精选专题生成。

## 数据模型草案

- `Repository`：仓库稳定身份和基础元数据。
- `RepositorySnapshot`：某次抓取时的 stars、forks、语言、描述、topics 和榜单位置。
- `TrendingRun`：一次抓取任务的来源、日期、语言过滤条件和执行状态。
- `FeaturedCollection`：精选专题，例如“适合初学者的 AI 工具”。
- `FeaturedRepository`：某个精选专题下的项目和入选理由。

## 数据抓取流程

1. 按周期和语言抓取 GitHub Trending。
2. 解析仓库 owner、name、URL、描述、语言、stars、forks 和周期新增 stars。
3. 按 owner 和 name upsert 仓库记录。
4. 为本次抓取写入榜单快照。
5. 可选：把候选项目传入 AI 精选层。
6. 存储 AI 精选项目和入选理由。

## API 草案

- `GET /api/repositories/trending`：获取热门项目榜单。
- `GET /api/repositories/search`：关键词搜索。
- `GET /api/repositories/:owner/:name`：获取项目详情。
- `GET /api/featured`：获取 AI 精选专题。
- `POST /api/admin/ingest/trending`：本地或管理员手动触发抓取。

## 待决策事项

- GitHub Trending 数据是直接解析网页，还是使用其他 GitHub 数据源。
- AI 精选使用哪个模型供应商和模型。
- 定时抓取运行在应用宿主里，还是使用外部调度器。
- 什么时候从 SQLite 迁移到 PostgreSQL。
