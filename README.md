# Repo Scout 开源雷达

[English](./README.en.md) | 简体中文

Repo Scout（开源雷达）是一个面向 AI 初学者的 GitHub 热门开源项目搜索与发现网站。

它通过热门榜单、项目搜索、AI 精选专题和自动化数据更新，帮助用户快速发现值得学习、关注和尝试的 GitHub 开源项目。

## 项目定位

Repo Scout 面向刚开始接触 AI 和开源项目的用户。它不是代码托管平台，也不是完整的推荐系统，而是一个更容易浏览、搜索和理解 GitHub 热门项目的发现工具。

## 计划功能

- GitHub Trending 热门项目榜单
- 按关键词、语言、主题和热度搜索 GitHub 项目
- 面向 AI 初学者的 AI 精选明星项目专题
- 项目详情页，展示 stars、语言、描述、topics 和仓库链接
- 后端数据库，存储项目快照和榜单历史
- 定时抓取 GitHub Trending，自动更新热门项目数据

## 目标用户

- 想通过开源项目学习 AI 的初学者
- 关注开源 AI 工具的开发者
- 想寻找项目灵感和可用工具的产品或技术人员

## 当前状态

项目处于产品增强版建设阶段。当前进度见 [ROADMAP.md](./ROADMAP.md)。

## 文档

- [MVP 范围](./docs/mvp.md)
- [技术架构计划](./docs/architecture.md)
- [数据模型设计](./docs/data-model.md)
- [运行验收记录](./docs/runtime-acceptance.md)
- [MVP 发布检查清单](./docs/mvp-release-checklist.md)
- [依赖风险记录](./docs/dependency-risks.md)
- [MVP 发布就绪摘要](./docs/release-readiness.md)

## 本地开发

当前项目采用前后端分离的轻量 monorepo 结构：

- `apps/web`：Next.js 前端。
- `apps/api`：FastAPI 后端。

首次安装依赖：

```bash
npm install
cd apps/api
python -m venv .venv
.venv/bin/python -m pip install -e .
cd ../..
```

真实数据端到端演示：

```bash
scripts/local-demo.sh --real --period daily --limit 20
scripts/local-demo.sh --real --period weekly --language Python --limit 20
```

无网络或只想看本地示例数据时：

```bash
scripts/local-demo.sh --sample
```

> Repo Scout **无需任何大模型配置即可完整运行**。AI 精选和中文摘要默认走确定性规则评分与本地模板，配置大模型只是可选增强，详见[可选：启用大模型增强](#可选启用大模型增强)。

演示脚本会写入本地 SQLite 数据、生成 AI 精选专题，并启动：

- 后端 API：`http://127.0.0.1:8000`
- 前端页面：`http://127.0.0.1:3000`

也可以手动分步运行：

```bash
npm run ingest:trending -- --period daily --limit 20
npm run ingest:trending -- --period weekly --language Python --limit 20
npm run curate:featured -- --limit 5
npm run backfill:content   # 重新生成已有仓库的中文摘要（可选）
npm run dev:api
npm run dev:web
```

本地发布前完整验证：

```bash
scripts/validate-local-release.sh
```

只验证网站运行态：

```bash
scripts/validate-runtime.sh
```

后端默认使用本地 SQLite 数据库，文件会写入 `data/` 目录，该目录已被 `.gitignore` 忽略。

## 可选：启用大模型增强

Repo Scout 完整功能不依赖任何大模型。下列两项能力在**未配置模型时**走本地降级路径：

- **AI 精选理由**：默认走规则评分 + 本地模板理由。
- **中文摘要**：默认走关键词 profile + 原英文简介。

配置 OpenAI-compatible 模型后，未命中本地规则的英文简介会调用模型生成事实性中文摘要，AI 精选理由也会改用模型输出。**模型不可用、请求失败或返回不含中文时，自动回退到本地降级，不影响主流程**。

在项目根目录创建 `.env.local`（已被 `.gitignore` 忽略）：

```dotenv
REPO_SCOUT_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
REPO_SCOUT_OPENAI_API_KEY=your-api-key
REPO_SCOUT_OPENAI_MODEL=glm-4.7
```

三个变量必须同时配置才会启用，任一缺失即保持本地降级。`scripts/local-demo.sh` 会自动 `source` 此文件；手动运行命令时请先 `set -a; source .env.local; set +a` 或自行 export。

支持任意 OpenAI-compatible `chat/completions` 端点（如智谱 GLM、OpenAI、DeepSeek、Moonshot 等）。**不要把真实 API Key 提交到仓库**——`.env.local` 已被忽略，请勿改文件名或复制到其他路径。

启用模型后可一次性回填已有仓库的中文摘要：

```bash
npm run backfill:content
```

## 项目出处

本项目的诞生过程记录在林亦LYi 的视频《月薪0.3元，我有了300个员工》中——使用 KimiWork 桌面端的多 Agent 协作能力，30 分钟内从本地开发到服务器部署完成"开源项目雷达"。

🔗 https://www.bilibili.com/video/BV18Qjo6QEFw/
