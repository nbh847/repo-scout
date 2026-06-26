# 依赖风险记录

## 2026-06-26：Next.js 内部 PostCSS 漏洞

### 最新复查

2026-06-26 再次运行：

- `npm audit --omit=dev`
- `npm view next version`
- `npm view next@16.2.9 dependencies.postcss engines peerDependencies version`

结果仍未变化：当前稳定 Next 仍为 `16.2.9`，其内部 `dependencies.postcss` 仍为 `8.4.31`，`npm audit --omit=dev` 仍报告 `next 9.3.4-canary.0 - 16.3.0-canary.5` 依赖 vulnerable PostCSS。`npm audit fix --force` 仍会安装 `next@9.3.3`，不采用。

### 现象

`npm audit --omit=dev` 仍报告 2 个 moderate 漏洞：

- `postcss < 8.5.10`
- 来源：`node_modules/next/node_modules/postcss`
- 关联公告：`GHSA-qx2v-qp2m-jg93`

### 当前依赖状态

`npm ls postcss` 显示：

- 项目直接依赖和 Tailwind 相关依赖使用 `postcss@8.5.15`。
- `next@15.5.19` 内部仍依赖 `postcss@8.4.31`。

`npm view next version` 显示当前稳定版为 `16.2.9`，但 `npm view next@16.2.9 dependencies.postcss` 仍为 `8.4.31`，升级到当前稳定版不能消除该 audit 项。

### 已尝试处理

- root `package.json` 已配置 `overrides.postcss`。
- root `package.json` 已尝试为 `next@15.5.19` 配置嵌套 `postcss` override。
- 已运行 `npm install` 重新解析依赖。

结果：`npm audit --omit=dev` 仍报告同一问题，`npm ls postcss` 仍显示 `next@15.5.19 -> postcss@8.4.31`。

### 不采用的处理

不运行 `npm audit fix --force`。当前 npm 建议会安装 `next@9.3.3`，这是大版本回退且会破坏当前 Next 15/React 19 项目基础。

### 当前结论

该风险暂作为发布前已知风险保留，等待 Next.js 上游将内部 `postcss` 升级到 `>=8.5.10`，或后续迁移到确认已修复的 Next 版本。

### 发布前要求

- 发布前再次运行 `npm audit --omit=dev`。
- 如果 Next 上游已修复，优先升级 Next 并跑完整验证。
- 如果仍未修复，只允许本地/单机演示使用，不做公开生产发布。
