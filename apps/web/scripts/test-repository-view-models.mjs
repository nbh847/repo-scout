import assert from "node:assert/strict";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import vm from "node:vm";
import ts from "typescript";

const require = createRequire(import.meta.url);
const sourcePath = path.resolve("src/app/repository-view-models.ts");
const source = fs.readFileSync(sourcePath, "utf8");
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
  buildCollectionHref,
  buildRepositoryHref,
  buildRepositoryViewModel,
  buildMetrics,
  formatTrendDelta,
} = sandbox.module.exports;
const normalize = (value) => JSON.parse(JSON.stringify(value));

const repository = buildRepositoryViewModel({
  rank: 3,
  owner: "openai",
  name: "agents",
  full_name: "openai/agents",
  url: "https://github.com/openai/agents",
  description: "Agent framework for production apps",
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
  primary_language: null,
  topics: [],
  stars: 0,
  forks: 0,
  stars_gained: 0,
});

assert.equal(fallbackRepository.description, "No description provided.");
assert.equal(fallbackRepository.language, "Unknown");
assert.equal(fallbackRepository.gained, "+0");
assert.equal(fallbackRepository.fit, "General");

assert.deepEqual(normalize(buildMetrics([repository, fallbackRepository])), [
  { label: "Tracked repos", value: "2" },
  { label: "Languages", value: "2" },
]);

assert.equal(buildRepositoryHref("openai/agents"), "/repositories/openai/agents");
assert.equal(buildRepositoryHref("owner with space/project/name"), "/repositories/owner%20with%20space/project%2Fname");
assert.equal(buildCollectionHref("beginner-friendly-ai"), "/collections/beginner-friendly-ai");
assert.equal(buildCollectionHref("AI Picks"), "/collections/AI%20Picks");
assert.equal(
  buildRepositoryApiPath({ query: "", period: "weekly", language: "Python" }),
  "/api/repositories/trending?limit=20&period=weekly&language=Python",
);
assert.equal(
  buildRepositoryApiPath({ query: "agent", period: "monthly", language: "Go" }),
  "/api/repositories/search?q=agent&limit=20",
);
assert.equal(formatTrendDelta(55), "+55");
assert.equal(formatTrendDelta(0), "0");
assert.equal(formatTrendDelta(null), "暂无历史");
