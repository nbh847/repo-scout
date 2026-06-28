# Featured Collection Count Link Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在首页每个精选专题的 Top pick 下方显示“查看全部 N 个项目”入口，并链接到现有专题页。

**Architecture:** 复用 `/api/featured` 已返回的完整 `repositories` 数组，在 `buildFeaturedProjects` 中将专题项目总数转换为首页视图模型字段。首页只负责渲染数量文案和现有专题链接，不修改后端、精选逻辑或专题页。

**Tech Stack:** Next.js 15、React 19、TypeScript、Node.js `assert`

---

## File Structure

- Modify: `apps/web/src/app/repository-view-models.ts` — 为首页精选项目视图模型增加专题项目总数。
- Modify: `apps/web/scripts/test-repository-view-models.mjs` — 测试专题项目总数转换和首页数量入口。
- Modify: `apps/web/src/app/page.tsx` — 渲染“查看全部 N 个项目”专题链接。
- Modify: `ROADMAP.md` — 记录实现和验证结果。

### Task 1: Add the collection size to the homepage view model

**Files:**
- Modify: `apps/web/scripts/test-repository-view-models.mjs:118-177`
- Modify: `apps/web/src/app/repository-view-models.ts:47-54`
- Modify: `apps/web/src/app/repository-view-models.ts:222-244`

- [ ] **Step 1: Write the failing view-model test**

在 `buildFeaturedProjects` 的期望结果中增加 `collectionSize`：

```javascript
[
  {
    title: "AI Agent 项目",
    collectionSlug: "ai-agent-projects",
    collectionSize: 2,
    repo: "openai/agents",
    reason: "Agent workflow pick.",
    score: "4.5",
    stars: "15.4k",
  },
  {
    title: "LLM 工具",
    collectionSlug: "llm-tools",
    collectionSize: 1,
    repo: "example/llm-tool",
    reason: "LLM tool pick.",
    score: "3.5",
    stars: "0",
  },
]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm run test:web
```

Expected: FAIL because `buildFeaturedProjects` does not return `collectionSize`.

- [ ] **Step 3: Add the minimal view-model field**

在 `FeaturedProjectViewModel` 中增加：

```typescript
collectionSize: number;
```

在 `buildFeaturedProjects` 返回对象中增加：

```typescript
collectionSize: collection.repositories.length,
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
npm run test:web
```

Expected: PASS.

### Task 2: Render the collection count link

**Files:**
- Modify: `apps/web/scripts/test-repository-view-models.mjs:8-23`
- Modify: `apps/web/scripts/test-repository-view-models.mjs:287-307`
- Modify: `apps/web/src/app/page.tsx:510-517`

- [ ] **Step 1: Write the failing homepage source assertions**

在现有 `homePageSource` 断言区域（当前第 292 行后）增加：

```javascript
assert.match(homePageSource, /查看全部 \\{project\\.collectionSize\\} 个项目/);
assert.match(homePageSource, /href=\\{buildCollectionHref\\(project\\.collectionSlug\\)\\}/);
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
npm run test:web
```

Expected: FAIL because `page.tsx` does not contain the collection count link.

- [ ] **Step 3: Render the minimal link**

在现有“查看”项目按钮之后、`article` 结束之前增加：

```tsx
{project.collectionSlug ? (
  <Link
    href={buildCollectionHref(project.collectionSlug)}
    className="mt-4 inline-flex items-center gap-1 text-sm font-bold text-cyan hover:text-ink"
  >
    查看全部 {project.collectionSize} 个项目
    <ArrowRight size={15} aria-hidden="true" />
  </Link>
) : null}
```

- [ ] **Step 4: Run focused frontend verification**

Run:

```bash
npm run test:web
npm run lint:web
npm --workspace apps/web run typecheck
```

Expected: all commands exit 0.

### Task 3: Run runtime verification and update project status

**Files:**
- Modify: `ROADMAP.md`

- [ ] **Step 1: Verify the rendered homepage**

Run:

```bash
scripts/validate-runtime.sh
```

Expected: exit 0, including homepage and featured collection page checks.

- [ ] **Step 2: Record the verified feature**

在 `ROADMAP.md` 的“已完成”中增加：

```markdown
- 首页每个 AI 精选专题的 Top pick 下方展示“查看全部 N 个项目”入口，明确专题项目数量并链接到专题页。
```

在“最近验证”中增加：

```markdown
- 2026-06-28：已通过前端测试、lint、typecheck 和运行态验证，确认首页精选专题数量入口展示正确并链接到专题页。
```

- [ ] **Step 3: Run final diff validation**

Run:

```bash
git diff --check
git status --short
```

Expected: `git diff --check` exits 0; status contains only the planned implementation, test, roadmap, and plan files.

- [ ] **Step 4: Commit the implementation**

```bash
git add apps/web/src/app/repository-view-models.ts apps/web/scripts/test-repository-view-models.mjs apps/web/src/app/page.tsx ROADMAP.md docs/superpowers/plans/2026-06-28-featured-collection-count-link.md
git commit -m "feat: show featured collection project counts"
```
