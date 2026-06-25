# Repo Scout 路线图

## 当前阶段

规划和项目基础建设。

## 已完成

- 创建 GitHub 仓库。
- 添加项目名称和基础描述。
- 添加 `.gitignore`，忽略敏感文件、本地文件、依赖、日志、构建产物和本地数据库。
- 梳理产品定位和计划功能范围。
- 定义 MVP 范围。
- 起草技术架构计划。
- 将公开文档调整为中文为主，并新增英文 README。
- 确认 MVP 技术栈：Next.js、TypeScript、Tailwind CSS、Python、FastAPI、SQLite、SQLAlchemy、Alembic。

## 进行中

- 定义仓库、榜单快照、抓取记录和 AI 精选集合的数据表结构。

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

- 构建第一版 UI，包含榜单、搜索和精选专题栏。
- 实现 GitHub Trending 抓取。
- 添加热门数据定时更新能力。

## 阻塞

- AI 精选方案未确认。
- GitHub Trending 抓取策略未确认。
- SQLite 迁移到 PostgreSQL 的时机未确认。

## 最近验证

- 2026-06-25：已验证 README 和路线图文档内容。
- 2026-06-25：已验证 MVP 和架构文档内容。
- 2026-06-25：已验证中文主文档和英文 README 内容。
- 2026-06-25：已将 4 阶段功能开发计划写入路线图。
- 2026-06-25：已将技术栈调整为 Next.js、FastAPI、SQLite、SQLAlchemy 和 Alembic。
