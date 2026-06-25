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

项目处于规划阶段。当前进度见 [ROADMAP.md](./ROADMAP.md)。

## 文档

- [MVP 范围](./docs/mvp.md)
- [技术架构计划](./docs/architecture.md)
- [数据模型设计](./docs/data-model.md)

## 本地开发

当前项目采用前后端分离的轻量 monorepo 结构：

- `apps/web`：Next.js 前端。
- `apps/api`：FastAPI 后端。

前端启动命令：

```bash
npm install
npm run dev:web
```

后端启动命令：

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .
cd ../..
npm run dev:api
```

后端默认使用本地 SQLite 数据库，文件会写入 `data/` 目录，该目录已被 `.gitignore` 忽略。
