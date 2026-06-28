import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import vm from "node:vm";
import ts from "typescript";

const require = createRequire(import.meta.url);
const sourcePath = path.resolve("src/app/repository-view-models.ts");
const source = fs.readFileSync(sourcePath, "utf8");
const homePageSource = fs.readFileSync(path.resolve("src/app/page.tsx"), "utf8");
const detailPageSource = fs.readFileSync(
  path.resolve("src/app/repositories/[owner]/[name]/page.tsx"),
  "utf8",
);
const ingestionRouteSource = fs.readFileSync(
  path.resolve("src/app/api/ingest/trending/route.ts"),
  "utf8",
);
const ingestionConfigSource = fs.readFileSync(
  path.resolve("src/app/trending-ingestion-config.ts"),
  "utf8",
);
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
    strict: true,
  },
});

const module = { exports: {} };
const sandbox = {
  exports: module.exports,
  module,
  require,
  URLSearchParams,
};

vm.runInNewContext(compiled.outputText, sandbox, { filename: sourcePath });
const {
  buildRepositoryApiPath,
  buildRepositoryLanguagesApiPath,
  buildCollectionHref,
  buildFeaturedProjects,
  buildRelatedCollectionProjects,
  buildRepositoryHref,
  buildRepositoryViewModel,
  buildMetrics,
  formatTrendDelta,
  paginateRepositories,
  repositoryMetricForSort,
  sortRepositories,
} = sandbox.module.exports;
const normalize = (value) => JSON.parse(JSON.stringify(value));

const repository = buildRepositoryViewModel({
  rank: 3,
  owner: "openai",
  name: "agents",
  full_name: "openai/agents",
  url: "https://github.com/openai/agents",
  description: "Agent framework for production apps",
  summary_zh: "一个用于构建生产级 AI Agent 的开源框架。",
  description_zh: "该项目提供构建生产级 AI Agent 所需的工作流和工具。",
  primary_language: "Python",
  topics: ["agents", "llm"],
  stars: 15420,
  forks: 930,
  stars_gained: 640,
});

assert.deepEqual(normalize(repository), {
  rank: 3,
  owner: "openai",
  name: "agents",
  fullName: "openai/agents",
  url: "https://github.com/openai/agents",
  description: "Agent framework for production apps",
  summary: "一个用于构建生产级 AI Agent 的开源框架。",
  descriptionZh: "该项目提供构建生产级 AI Agent 所需的工作流和工具。",
  language: "Python",
  stars: "15.4k",
  forks: "930",
  gained: "+640",
  tags: ["agents", "llm"],
  fit: "Python",
});

const fallbackRepository = buildRepositoryViewModel({
  rank: 1,
  owner: "example",
  name: "tool",
  full_name: "example/tool",
  url: "https://github.com/example/tool",
  description: null,
  summary_zh: null,
  description_zh: null,
  primary_language: null,
  topics: [],
  stars: 0,
  forks: 0,
  stars_gained: 0,
});

assert.equal(fallbackRepository.description, "No description provided.");
assert.equal(fallbackRepository.summary, "暂无中文摘要。");
assert.equal(fallbackRepository.descriptionZh, "暂无中文说明。");
assert.equal(fallbackRepository.language, "Unknown");
assert.equal(fallbackRepository.gained, "+0");
assert.equal(fallbackRepository.fit, "General");

assert.deepEqual(normalize(buildMetrics([repository, fallbackRepository])), [
  { label: "Tracked repos", value: "2" },
  { label: "Languages", value: "2" },
]);

assert.deepEqual(
  normalize(
    buildFeaturedProjects([
      {
        slug: "ai-agent-projects",
        title: "AI Agent 项目",
        repositories: [
          {
            ...repository,
            full_name: "openai/agents",
            stars: 15420,
            reason: "Agent workflow pick.",
            beginner_score: 4,
            learning_value_score: 5,
          },
          {
            ...repository,
            full_name: "openai/second-agent",
            stars: 15420,
            reason: "Second pick.",
            beginner_score: 5,
            learning_value_score: 5,
          },
        ],
      },
      {
        slug: "llm-tools",
        title: "LLM 工具",
        repositories: [
          {
            ...fallbackRepository,
            full_name: "example/llm-tool",
            stars: 0,
            reason: "LLM tool pick.",
            beginner_score: 3,
            learning_value_score: 4,
          },
        ],
      },
    ]),
  ),
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
  ],
);
assert.deepEqual(
  normalize(
    buildRelatedCollectionProjects(
      {
        slug: "ai-agent-projects",
        title: "AI Agent 项目",
        repositories: [
          {
            ...repository,
            full_name: "openai/agents",
            reason: "Current project.",
            beginner_score: 4,
            learning_value_score: 5,
          },
          {
            ...repository,
            full_name: "openai/second-agent",
            reason: "Second pick.",
            beginner_score: 5,
            learning_value_score: 5,
          },
          {
            ...repository,
            full_name: "openai/third-agent",
            reason: "Third pick.",
            beginner_score: 3,
            learning_value_score: 4,
          },
        ],
      },
      "openai/agents",
      1,
    ),
  ),
  [
    {
      repo: "openai/second-agent",
      reason: "Second pick.",
      score: "5.0",
    },
  ],
);

assert.equal(buildRepositoryHref("openai/agents"), "/repositories/openai/agents");
assert.equal(
  buildRepositoryHref("openai/agents", "/?period=weekly&language=Python&sort=gained#ranking"),
  "/repositories/openai/agents?from=%2F%3Fperiod%3Dweekly%26language%3DPython%26sort%3Dgained%23ranking",
);
assert.equal(buildRepositoryHref("owner with space/project/name"), "/repositories/owner%20with%20space/project%2Fname");
assert.equal(buildCollectionHref("beginner-friendly-ai"), "/collections/beginner-friendly-ai");
assert.equal(buildCollectionHref("AI Picks"), "/collections/AI%20Picks");
assert.equal(
  buildRepositoryApiPath({ query: "", period: "weekly", language: "Python" }),
  "/api/repositories/trending?limit=20&period=weekly&language=Python",
);
assert.equal(
  buildRepositoryApiPath({ query: "agent", period: "monthly", language: "Go" }),
  "/api/repositories/search?q=agent&limit=20&language=Go",
);
assert.equal(
  buildRepositoryApiPath({ query: "", period: "monthly", language: "", limit: 50 }),
  "/api/repositories/trending?limit=50&period=monthly",
);
assert.equal(buildRepositoryLanguagesApiPath(), "/api/repositories/languages");
assert.equal(formatTrendDelta(55), "+55");
assert.equal(formatTrendDelta(0), "0");
assert.equal(formatTrendDelta(null), "暂无历史");
const sortableRepositories = [
  { ...repository, full_name: "owner/low-gain", rank: 1, stars: 500, stars_gained: 10 },
  { ...repository, full_name: "owner/high-gain", rank: 2, stars: 400, stars_gained: 90 },
  { ...repository, full_name: "owner/high-stars", rank: 3, stars: 900, stars_gained: 20 },
];
assert.deepEqual(normalize(sortRepositories(sortableRepositories, "ranking").map((item) => item.full_name)), [
  "owner/low-gain",
  "owner/high-gain",
  "owner/high-stars",
]);
assert.deepEqual(normalize(sortRepositories(sortableRepositories, "stars").map((item) => item.full_name)), [
  "owner/high-stars",
  "owner/low-gain",
  "owner/high-gain",
]);
assert.deepEqual(normalize(sortRepositories(sortableRepositories, "gained").map((item) => item.full_name)), [
  "owner/high-gain",
  "owner/high-stars",
  "owner/low-gain",
]);
assert.deepEqual(normalize(repositoryMetricForSort(repository, "ranking")), {
  label: "Stars",
  value: "15.4k",
});
assert.deepEqual(normalize(repositoryMetricForSort(repository, "stars")), {
  label: "Stars",
  value: "15.4k",
});
assert.deepEqual(normalize(repositoryMetricForSort(repository, "gained")), {
  label: "新增 Stars",
  value: "+640",
});
assert.deepEqual(
  normalize(paginateRepositories(sortableRepositories, 2, 2)),
  {
    items: [sortableRepositories[2]],
    page: 2,
    totalPages: 2,
    totalItems: 3,
  },
);
assert.equal(paginateRepositories(sortableRepositories, 99, 2).page, 2);
assert.match(homePageSource, /repository\.tags\.map/);
assert.match(homePageSource, /repository\.summary/);
assert.match(homePageSource, /paginateRepositories/);
assert.match(homePageSource, /pageNumbers/);
assert.match(homePageSource, /href="https:\/\/github\.com\/trending"[\s\S]*target="_blank"/);
assert.match(homePageSource, /key=\{`\$\{project\.collectionSlug\}:\$\{project\.repo\}`\}/);
assert.doesNotMatch(homePageSource, /key=\{project\.repo\}/);
assert.match(homePageSource, /sortRepositories/);
assert.match(homePageSource, /RankingSortControl/);
assert.match(homePageSource, /TrendingIngestionPanel/);
assert.doesNotMatch(homePageSource, /\{activeSortLabel\}/);
assert.match(homePageSource, /aria-label="难度 2\/5"/);
assert.doesNotMatch(homePageSource, /●●/);
assert.match(ingestionConfigSource, /daily: 20/);
assert.match(ingestionConfigSource, /weekly: 30/);
assert.match(ingestionConfigSource, /monthly: 50/);
assert.match(ingestionRouteSource, /ingestionLimitForPeriod\(period\)/);
assert.match(homePageSource, /清除筛选/);
assert.match(homePageSource, /href="\/#ranking"/);
assert.match(homePageSource, /returnHref/);
assert.match(homePageSource, /buildRepositoryHref\(repository\.fullName, returnHref\)/);
assert.match(detailPageSource, /repository\.tags\.map/);
assert.match(detailPageSource, /featured_collection_slug/);
assert.match(detailPageSource, /buildCollectionHref/);
assert.match(detailPageSource, /searchParams/);
assert.match(detailPageSource, /返回榜单/);
assert.match(detailPageSource, /repository\.descriptionZh/);
assert.match(detailPageSource, /原始说明/);
assert.match(detailPageSource, /href=\{repository\.url\}[\s\S]*target="_blank"/);
assert.match(detailPageSource, /rel="noopener noreferrer"/);
