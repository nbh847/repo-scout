import {
  Activity,
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

const languageSignals = [
  { label: "Python", value: "42%", tone: "bg-emerald-500" },
  { label: "TypeScript", value: "31%", tone: "bg-sky-500" },
  { label: "Go", value: "18%", tone: "bg-amber-500" },
];

const metrics = [
  { label: "Tracked repos", value: "128", icon: Radar },
  { label: "Daily growth", value: "+1.7k", icon: Activity },
  { label: "Beginner fit", value: "24", icon: BookOpen },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-canvas text-ink">
      <div className="mx-auto grid min-h-screen max-w-[1500px] grid-cols-1 lg:grid-cols-[252px_1fr_360px]">
        <aside className="border-b border-line bg-surface px-5 py-5 lg:min-h-screen lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-lg bg-ink text-white">
              <Radar size={23} aria-hidden="true" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.18em] text-muted">Repo Scout</p>
              <h1 className="text-lg font-semibold">开源雷达</h1>
            </div>
          </div>

          <nav className="mt-8 grid gap-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.label}
                  href={item.active ? "#ranking" : "#featured"}
                  className={`flex h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium ${
                    item.active
                      ? "bg-ink text-white"
                      : "text-muted hover:bg-panel hover:text-ink"
                  }`}
                >
                  <Icon size={17} aria-hidden="true" />
                  {item.label}
                </a>
              );
            })}
          </nav>

          <section className="mt-8">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Period</p>
            <div className="mt-3 grid grid-cols-3 gap-2">
              {["Day", "Week", "Month"].map((period, index) => (
                <button
                  key={period}
                  className={`h-9 rounded-lg border text-xs font-medium ${
                    index === 0
                      ? "border-ink bg-ink text-white"
                      : "border-line bg-white text-muted hover:text-ink"
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </section>

          <section className="mt-8">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Languages</p>
            <div className="mt-3 space-y-3">
              {languageSignals.map((signal) => (
                <div key={signal.label}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-ink">{signal.label}</span>
                    <span className="text-muted">{signal.value}</span>
                  </div>
                  <div className="h-2 rounded-full bg-panel">
                    <div className={`h-2 rounded-full ${signal.tone}`} style={{ width: signal.value }} />
                  </div>
                </div>
              ))}
            </div>
          </section>
        </aside>

        <section className="px-5 py-6 md:px-8 lg:px-9">
          <header className="flex flex-col gap-5 border-b border-line pb-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="flex items-center gap-2 text-sm font-medium text-accent">
                <Bot size={16} aria-hidden="true" />
                AI-assisted open source discovery
              </p>
              <h2 className="mt-3 max-w-3xl text-3xl font-semibold leading-tight md:text-4xl">
                从 GitHub Trending 里筛出值得学习和跟进的项目
              </h2>
            </div>
            <div className="grid grid-cols-3 gap-3 md:w-[360px]">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="rounded-lg border border-line bg-white p-3">
                    <Icon className="text-muted" size={16} aria-hidden="true" />
                    <p className="mt-3 text-lg font-semibold">{metric.value}</p>
                    <p className="mt-1 text-xs text-muted">{metric.label}</p>
                  </div>
                );
              })}
            </div>
          </header>

          <div id="search" className="mt-6 rounded-lg border border-line bg-white p-3 shadow-soft">
            <div className="flex flex-col gap-3 md:flex-row">
              <label className="flex min-h-12 flex-1 items-center gap-3 rounded-lg bg-panel px-4" aria-label="搜索 GitHub 项目">
                <Search size={19} className="text-muted" aria-hidden="true" />
                <input
                  className="w-full bg-transparent text-sm outline-none"
                  placeholder="Search repositories, languages, topics"
                />
              </label>
              <button className="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-accent px-5 text-sm font-semibold text-white">
                <Search size={17} aria-hidden="true" />
                Search
              </button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {filters.map((filter, index) => (
                <button
                  key={filter}
                  className={`rounded-lg border px-3 py-2 text-xs font-medium ${
                    index === 0
                      ? "border-accent bg-accent-soft text-accent"
                      : "border-line bg-white text-muted hover:text-ink"
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          <section id="ranking" className="mt-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">GitHub Trending</p>
                <h2 className="text-2xl font-semibold">今日热门项目榜单</h2>
              </div>
              <button className="inline-flex h-10 items-center gap-2 rounded-lg border border-line bg-white px-4 text-sm font-medium text-ink">
                <BookOpen size={16} aria-hidden="true" />
                View all
              </button>
            </div>

            <div className="grid gap-3">
              {trendingRepositories.map((repository) => (
                <article key={repository.fullName} className="rounded-lg border border-line bg-white p-4 shadow-soft">
                  <div className="grid gap-4 md:grid-cols-[56px_1fr_auto]">
                    <div className="grid h-12 w-12 place-items-center rounded-lg bg-panel text-lg font-semibold text-accent">
                      {repository.rank}
                    </div>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-lg font-semibold">{repository.fullName}</h3>
                        <span className="rounded-md bg-panel px-2 py-1 text-xs font-medium text-muted">
                          {repository.language}
                        </span>
                        <span className="rounded-md bg-accent-soft px-2 py-1 text-xs font-medium text-accent">
                          {repository.fit}
                        </span>
                      </div>
                      <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">{repository.description}</p>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {repository.tags.map((tag) => (
                          <span key={tag} className="rounded-md border border-line px-2 py-1 text-xs text-muted">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-5 md:justify-end">
                      <div className="grid gap-2 text-sm">
                        <div className="flex items-center gap-2 font-semibold">
                          <Star size={15} className="text-amber" aria-hidden="true" />
                          {repository.stars}
                        </div>
                        <div className="flex items-center gap-2 text-muted">
                          <GitFork size={15} aria-hidden="true" />
                          {repository.forks}
                        </div>
                      </div>
                      <div className="text-right text-sm">
                        <p className="font-semibold text-emerald-700">{repository.gained}</p>
                        <p className="mt-1 text-muted">today</p>
                      </div>
                      <a
                        className="grid h-10 w-10 place-items-center rounded-lg border border-line text-muted hover:border-accent hover:text-accent"
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

        <aside id="featured" className="border-t border-line bg-surface px-5 py-6 lg:min-h-screen lg:border-l lg:border-t-0">
          <div className="rounded-lg border border-line bg-white p-5 shadow-soft">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted">AI Curated</p>
                <h2 className="mt-1 text-xl font-semibold">明星项目专题</h2>
              </div>
              <Sparkles className="text-amber" size={24} aria-hidden="true" />
            </div>
            <div className="mt-5 space-y-3">
              {featuredProjects.map((project) => (
                <article key={project.repo} className="rounded-lg border border-line bg-panel p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-medium text-muted">{project.title}</p>
                      <h3 className="mt-1 text-sm font-semibold">{project.repo}</h3>
                    </div>
                    <div className="rounded-md bg-white px-2 py-1 text-xs font-semibold text-ink">{project.score}</div>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-muted">{project.reason}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="mt-4 rounded-lg border border-line bg-ink p-5 text-white shadow-soft">
            <div className="flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-lg bg-white/10">
                <Gauge size={18} aria-hidden="true" />
              </div>
              <div>
                <p className="text-sm text-white/58">Radar status</p>
                <h2 className="font-semibold">Daily sync ready</h2>
              </div>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-white/10 bg-white/8 p-3">
                <p className="text-2xl font-semibold">3</p>
                <p className="mt-1 text-xs text-white/58">New snapshots</p>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/8 p-3">
                <p className="text-2xl font-semibold">8</p>
                <p className="mt-1 text-xs text-white/58">Tests passed</p>
              </div>
            </div>
          </div>

          <a
            href="https://github.com/trending"
            className="mt-4 flex h-12 items-center justify-between rounded-lg border border-line bg-white px-4 text-sm font-medium text-ink"
          >
            Open GitHub Trending
            <ArrowUpRight size={17} aria-hidden="true" />
          </a>
        </aside>
      </div>
    </main>
  );
}
