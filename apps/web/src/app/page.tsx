import {
  ArrowUpRight,
  BookOpen,
  Bot,
  Code2,
  ExternalLink,
  Gauge,
  GitFork,
  Layers3,
  Radar,
  Search,
  Sparkles,
  Star,
  Terminal,
  TrendingUp,
} from "lucide-react";

const trendingRepositories = [
  {
    rank: 1,
    fullName: "langchain-ai/langchain",
    description: "构建 RAG、Agent 和上下文感知 LLM 应用的基础框架。",
    language: "Python",
    stars: "104k",
    forks: "16k",
    gained: "+640",
    tags: ["LLM", "Agent", "RAG"],
    fit: "Concepts",
  },
  {
    rank: 2,
    fullName: "open-webui/open-webui",
    description: "面向本地模型和托管模型的自托管 AI 聊天界面。",
    language: "TypeScript",
    stars: "82k",
    forks: "9.8k",
    gained: "+580",
    tags: ["UI", "Chat", "Self-hosted"],
    fit: "Product",
  },
  {
    rank: 3,
    fullName: "ollama/ollama",
    description: "在本地运行大语言模型的开发者工具。",
    language: "Go",
    stars: "145k",
    forks: "12k",
    gained: "+520",
    tags: ["Local LLM", "Models", "CLI"],
    fit: "Runtime",
  },
];

const featuredProjects = [
  {
    title: "适合初学者的 AI 项目",
    repo: "open-webui/open-webui",
    reason: "界面完整、部署路径清晰，适合理解 AI 产品如何组织模型、会话和设置。",
    score: "4.6",
  },
  {
    title: "值得关注的 Agent 框架",
    repo: "langchain-ai/langchain",
    reason: "生态成熟，学习材料丰富，适合建立 RAG 和 Agent 的基础概念。",
    score: "4.8",
  },
];

const navigationItems = [
  { label: "Trending", icon: TrendingUp, active: true },
  { label: "AI Picks", icon: Sparkles, active: false },
  { label: "Languages", icon: Code2, active: false },
  { label: "Collections", icon: Layers3, active: false },
];

const filters = ["All", "Python", "TypeScript", "Go", "AI Agent", "LLM Tools"];

const metrics = [
  { label: "Tracked repos", value: "128", icon: Radar },
  { label: "Beginner fit", value: "24", icon: BookOpen },
];

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-canvas text-ink">
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-40" />
      <div className="pointer-events-none fixed inset-0 bg-scanline opacity-20" />

      <div className="relative mx-auto grid min-h-screen max-w-[1460px] grid-cols-1 border-line/60 lg:grid-cols-[228px_minmax(0,1fr)_320px] lg:border-x">
        <aside className="border-b border-line/60 bg-surface/80 px-5 py-6 backdrop-blur-xl lg:min-h-screen lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg border border-accent/50 bg-accent/10 text-accent shadow-radar">
              <Radar size={23} aria-hidden="true" />
            </div>
            <div>
              <p className="font-mono text-xs uppercase text-accent">Repo Scout</p>
              <h1 className="text-lg font-semibold text-ink">开源雷达</h1>
            </div>
          </div>

          <nav className="mt-10 grid gap-1.5">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.label}
                  href={item.active ? "#ranking" : "#featured"}
                  className={`flex h-11 items-center gap-3 rounded-lg border px-3 text-sm font-medium transition ${
                    item.active
                      ? "border-accent/50 bg-accent/10 text-ink shadow-radar"
                      : "border-transparent text-muted hover:border-line hover:bg-panel/70 hover:text-ink"
                  }`}
                >
                  <Icon size={17} aria-hidden="true" />
                  {item.label}
                </a>
              );
            })}
          </nav>

          <section className="mt-10">
            <p className="font-mono text-xs uppercase text-muted">Period</p>
            <div className="mt-3 grid grid-cols-3 gap-2">
              {["Day", "Week", "Month"].map((period, index) => (
                <button
                  key={period}
                  className={`h-9 rounded-lg border font-mono text-xs font-semibold transition ${
                    index === 0
                      ? "border-accent bg-accent text-canvas"
                      : "border-line bg-panel/70 text-muted hover:text-ink"
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </section>
        </aside>

        <section className="px-5 py-8 md:px-10 lg:px-12">
          <header className="flex flex-col gap-6 border-b border-line/60 pb-8 xl:flex-row xl:items-start xl:justify-between">
            <div>
              <p className="flex items-center gap-2 font-mono text-sm text-accent">
                <Bot size={16} aria-hidden="true" />
                AI-assisted open source discovery
              </p>
              <h2 className="mt-3 max-w-3xl text-3xl font-semibold leading-tight text-ink md:text-4xl">
                从 GitHub Trending 中锁定值得学习和跟进的项目
              </h2>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 xl:w-[260px]">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="rounded-lg border border-line/80 bg-panel/70 p-3">
                    <Icon className="text-muted" size={16} aria-hidden="true" />
                    <p className="mt-3 font-mono text-xl font-semibold text-accent">{metric.value}</p>
                    <p className="mt-1 text-xs text-muted">{metric.label}</p>
                  </div>
                );
              })}
            </div>
          </header>

          <div id="search" className="mt-8 rounded-lg border border-line/80 bg-surface/80 p-3 shadow-terminal">
            <div className="flex flex-col gap-3 md:flex-row">
              <label
                className="flex min-h-12 flex-1 items-center gap-3 rounded-lg border border-line bg-panel/100 px-4"
                aria-label="搜索 GitHub 项目"
              >
                <Terminal size={18} className="text-accent" aria-hidden="true" />
                <span className="font-mono text-sm font-semibold text-accent">scout&gt;</span>
                <input
                  className="w-full bg-transparent text-sm text-ink outline-none placeholder:text-muted"
                  placeholder="search repositories, languages, topics"
                />
              </label>
              <button className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-cyan px-5 text-sm font-bold text-canvas">
                <Search size={17} aria-hidden="true" />
                Run scan
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {filters.map((filter, index) => (
                <button
                  key={filter}
                  className={`rounded-lg border px-3 py-2 font-mono text-xs font-medium transition ${
                    index === 0
                      ? "border-accent/60 bg-accent/10 text-accent"
                      : "border-line bg-panel/60 text-muted hover:text-ink"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          <section id="ranking" className="mt-8">
            <div className="mb-4 flex items-end justify-between gap-4">
              <div>
                <p className="text-sm text-muted">GitHub Trending</p>
                <h2 className="text-2xl font-semibold text-ink">今日热门项目榜单</h2>
              </div>
              <button className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-panel/100 px-4 text-sm font-medium text-ink">
                <BookOpen size={16} aria-hidden="true" />
                View all
              </button>
            </div>

            <div className="grid gap-4">
              {trendingRepositories.map((repository) => (
                <article
                  key={repository.fullName}
                  className="relative overflow-hidden rounded-lg border border-line/80 bg-surface/70 p-5 shadow-terminal before:absolute before:inset-y-0 before:left-0 before:w-[2px] before:bg-accent"
                >
                  <div className="grid gap-4 md:grid-cols-[52px_1fr] xl:grid-cols-[52px_1fr_170px]">
                    <div className="font-mono text-xl font-bold text-accent">
                      #{String(repository.rank).padStart(2, "0")}
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-semibold text-ink">{repository.fullName}</h3>
                        <span className="rounded-md border border-line bg-panel/100 px-2 py-1 font-mono text-xs font-medium text-cyan">
                          {repository.language}
                        </span>
                        <span className="rounded-md border border-accent/40 bg-accent/10 px-2 py-1 font-mono text-xs font-medium text-accent">
                          {repository.fit}
                        </span>
                      </div>
                      <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{repository.description}</p>
                      <div className="mt-3 hidden flex-wrap gap-2 md:flex">
                        {repository.tags.map((tag) => (
                          <span
                            key={tag}
                            className="rounded-md border border-line px-2 py-1 font-mono text-xs text-muted"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-[1fr_40px] items-center gap-3 md:col-start-2 xl:col-start-auto">
                      <div className="border-l border-line pl-4 text-sm">
                        <div className="flex items-center gap-2 font-mono font-semibold text-ink">
                          <Star size={15} className="text-amber" aria-hidden="true" />
                          {repository.stars}
                        </div>
                        <div className="mt-2 flex items-center gap-2 font-mono text-muted">
                          <GitFork size={15} aria-hidden="true" />
                          {repository.forks}
                        </div>
                      </div>
                      <a
                        className="grid h-10 w-10 place-items-center rounded-lg border border-line text-muted hover:border-cyan hover:text-cyan"
                        href={`https://github.com/${repository.fullName}`}
                        aria-label={`打开 ${repository.fullName}`}
                      >
                        <ExternalLink size={18} aria-hidden="true" />
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </section>

        <aside id="featured" className="border-t border-line/60 bg-surface/80 px-5 py-8 backdrop-blur-xl lg:min-h-screen lg:border-l lg:border-t-0">
          <section className="rounded-lg border border-line/80 bg-panel/60 p-5 shadow-terminal">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">AI Curated</p>
                <h2 className="mt-1 text-xl font-semibold text-ink">明星项目专题</h2>
              </div>
              <Sparkles className="text-amber" size={24} aria-hidden="true" />
            </div>
            <div className="mt-5 divide-y divide-line">
              {featuredProjects.map((project) => (
                <article key={project.repo} className="py-4 first:pt-0 last:pb-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-medium text-muted">{project.title}</p>
                      <h3 className="mt-1 text-sm font-semibold text-ink">{project.repo}</h3>
                    </div>
                    <div className="rounded-md border border-accent/30 bg-accent/10 px-2 py-1 font-mono text-xs font-semibold text-accent">
                      {project.score}
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted">{project.reason}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="mt-5 rounded-lg border border-accent/30 bg-accent/10 p-5 shadow-radar">
            <div className="flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-lg border border-accent/30 bg-canvas/50">
                <Gauge size={18} aria-hidden="true" />
              </div>
              <div>
                <p className="text-sm text-muted">Radar status</p>
                <h2 className="font-semibold text-ink">Daily sync ready</h2>
              </div>
            </div>
            <div className="mt-5 flex items-center justify-between rounded-lg border border-line/80 bg-panel/50 px-3 py-2">
              <span className="text-xs text-muted">New snapshots</span>
              <span className="font-mono text-sm font-semibold text-accent">3 / 8 tests</span>
            </div>
          </section>

          <a
            href="https://github.com/trending"
            className="mt-4 flex h-12 items-center justify-between rounded-lg border border-line bg-panel/75 px-4 text-sm font-medium text-ink"
          >
            Open GitHub Trending
            <ArrowUpRight size={17} aria-hidden="true" />
          </a>
        </aside>
      </div>
    </main>
  );
}
