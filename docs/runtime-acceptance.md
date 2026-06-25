# 运行验收记录

## 2026-06-25 本地真实运行验收

### 环境

- 后端：`http://127.0.0.1:8000`
- 前端：`http://127.0.0.1:3000`
- 数据：本地 SQLite，已执行 `npm run seed:api` 和 `npm run curate:featured -- --limit 5`

### 服务检查

- `GET /health` 返回 `{"status":"ok"}`。
- `GET /api/repositories/trending?limit=1` 返回 `calesthio/OpenMontage`。
- `GET /api/featured` 返回 `beginner-friendly-ai` 和 `notable-developer-tools` 两个精选专题。

### 页面检查

- 首页 `http://127.0.0.1:3000` 返回 200。
- 首页包含品牌文案 `Repo Scout 开源雷达`。
- 首页包含站内详情链接 `/repositories/calesthio/OpenMontage`。
- 首页右侧明星项目栏包含 `AI Curated`。
- 首页输出包含移动端布局类 `px-4 py-5`。
- 详情页 `http://127.0.0.1:3000/repositories/calesthio/OpenMontage` 返回 200。
- 详情页包含 `为什么值得关注`。
- 详情页包含精选评分 `5/5`。
- 详情页输出包含移动端布局类 `px-4 py-6`。

### 浏览器说明

本轮 in-app Browser 返回 `Browser is not available: iab`，本地环境也没有可用的 Playwright 包，因此未产出截图。已用运行中的本地服务、API 响应和页面 HTML 做端到端验收记录。
