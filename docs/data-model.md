# 数据模型设计

## 设计目标

MVP 阶段的数据模型要支撑四件事：

- 展示 GitHub Trending 热门项目榜单。
- 支持按关键词、语言、主题搜索项目。
- 记录每次抓取的榜单快照，避免只有当前状态。
- 存储 AI 精选专题和项目入选理由。

数据库先使用 SQLite，表结构保持关系型设计，后续可以迁移到 PostgreSQL。

## 表结构

### `repositories`

存储 GitHub 仓库的稳定身份和基础信息。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `owner` | text | 仓库 owner |
| `name` | text | 仓库名 |
| `full_name` | text | `owner/name` |
| `url` | text | GitHub 仓库地址 |
| `description` | text | 仓库描述 |
| `primary_language` | text | 主要语言 |
| `topics_json` | text | topics JSON 字符串 |
| `stars` | integer | 当前 stars 数 |
| `forks` | integer | 当前 forks 数 |
| `created_at` | datetime | 本地记录创建时间 |
| `updated_at` | datetime | 本地记录更新时间 |

约束：

- `full_name` 唯一。
- `owner + name` 唯一。

索引：

- `full_name`
- `primary_language`
- `stars`

### `trending_runs`

记录一次 GitHub Trending 抓取任务。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `source` | text | 数据源，MVP 固定为 `github_trending` |
| `period` | text | `daily`、`weekly` 或 `monthly` |
| `language` | text | 抓取语言过滤条件，可为空 |
| `status` | text | `pending`、`success`、`failed` |
| `started_at` | datetime | 开始时间 |
| `finished_at` | datetime | 结束时间 |
| `error_message` | text | 失败原因 |

索引：

- `source + period + language`
- `started_at`
- `status`

### `repository_snapshots`

记录某个仓库在某次抓取中的榜单状态。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `repository_id` | integer | 关联 `repositories.id` |
| `trending_run_id` | integer | 关联 `trending_runs.id` |
| `rank` | integer | 本次榜单排名 |
| `stars` | integer | 本次抓取时的 stars |
| `forks` | integer | 本次抓取时的 forks |
| `stars_gained` | integer | 当前周期新增 stars |
| `description` | text | 本次抓取时的描述 |
| `primary_language` | text | 本次抓取时的主要语言 |
| `captured_at` | datetime | 快照时间 |

约束：

- `trending_run_id + repository_id` 唯一，避免同一次抓取重复写入同一个仓库。

索引：

- `trending_run_id + rank`
- `repository_id + captured_at`
- `stars_gained`

### `featured_collections`

存储 AI 精选专题。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `slug` | text | 专题唯一标识 |
| `title` | text | 专题标题 |
| `description` | text | 专题说明 |
| `curation_prompt` | text | 生成专题时使用的筛选提示词 |
| `model_name` | text | 使用的模型名称 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

约束：

- `slug` 唯一。

### `featured_repositories`

存储专题下的精选项目和入选理由。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键 |
| `collection_id` | integer | 关联 `featured_collections.id` |
| `repository_id` | integer | 关联 `repositories.id` |
| `rank` | integer | 专题内排序 |
| `reason` | text | 入选理由 |
| `beginner_score` | integer | 初学者友好度评分，范围 1-5 |
| `learning_value_score` | integer | 学习价值评分，范围 1-5 |
| `created_at` | datetime | 创建时间 |

约束：

- `collection_id + repository_id` 唯一。

索引：

- `collection_id + rank`
- `repository_id`

## 关系

- 一个 `repositories` 记录可以对应多个 `repository_snapshots`。
- 一个 `trending_runs` 记录可以对应多个 `repository_snapshots`。
- 一个 `featured_collections` 记录可以对应多个 `featured_repositories`。
- 一个 `repositories` 记录可以出现在多个 `featured_collections` 中。

## 搜索策略

MVP 先使用 SQLite 的基础 `LIKE` 搜索，覆盖：

- `repositories.full_name`
- `repositories.description`
- `repositories.primary_language`
- `repositories.topics_json`

当数据量增长或搜索体验不够时，再评估：

- SQLite FTS5。
- Meilisearch。
- PostgreSQL full-text search。

## 去重策略

- 仓库按 `owner + name` 或 `full_name` 去重。
- 同一次抓取按 `trending_run_id + repository_id` 去重。
- 精选专题内按 `collection_id + repository_id` 去重。

## SQLite 注意点

- 早期只允许单进程或低并发写入。
- 定时抓取和手动抓取不能同时写入同一个数据库文件。
- 本地数据库文件必须被 `.gitignore` 忽略。
- 业务代码通过 SQLAlchemy 访问数据库，不直接拼接 SQLite 专属 SQL。

## 迁移到 PostgreSQL 的触发条件

出现以下情况时再迁移：

- 需要多实例部署。
- 抓取任务和用户请求存在明显写入竞争。
- 搜索数据量增长到 SQLite 查询体验变差。
- 需要更稳定的线上备份、恢复和权限管理。
