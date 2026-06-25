import { BookOpen, ExternalLink, Search, Sparkles, Star, TrendingUp } from "lucide-react";

const trendingRepositories = [
  {
    rank: 1,
    fullName: "langchain-ai/langchain",
    description: "构建 RAG、Agent 和上下文感知 LLM 应用的基础框架。",
    language: "Python",
    stars: "104k",
    gained: "+640",
    tags: ["LLM", "Agent", "RAG"],
  },
  {
    rank: 2,
    fullName: "open-webui/open-webui",
    description: "面向本地模型和托管模型的自托管 AI 聊天界面。",
    language: "TypeScript",
    stars: "82k",
    gained: "+580",
    tags: ["UI", "Chat", "Self-hosted"],
  },
  {
    rank: 3,
    fullName: "ollama/ollama",
    description: "在本地运行大语言模型的开发者工具。",
    language: "Go",
    stars: "145k",
    gained: "+520",
    tags: ["Local LLM", "Models", "CLI"],
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

const filters = ["全部", "Python", "TypeScript", "Go", "AI Agent", "LLM 工具"];

export default function Home() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-white/50 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-accent text-white">
              <TrendingUp size={22} aria-hidden="true" />
            </div>
            <div>
              <p className="text-sm text-muted">开源雷达</p>
              <h1 className="text-xl font-semibold text-ink">Repo Scout</h1>
            </div>
          </div>
          <nav className="hidden items-center gap-6 text-sm text-muted md:flex">
            <a href="#ranking">榜单</a>
            <a href="#featured">AI 精选</a>
            <a href="#search">搜索</a>
          </nav>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 py-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="flex min-h-[420px] flex-col justify-center rounded-lg bg-white/86 p-8 shadow-soft backdrop-blur">
          <div className="mb-5 inline-flex w-fit items-center gap-2 rounded-md border border-line bg-panel px-3 py-2 text-sm text-muted">
            <Sparkles size={16} aria-hidden="true" />
            AI 初学者的 GitHub 项目发现工具
          </div>
          <h2 className="max-w-2xl text-4xl font-semibold leading-tight text-ink md:text-5xl">
            从热门榜单里找到真正值得学习的开源项目
          </h2>
          <p className="mt-5 max-w-2xl text-base leading-8 text-muted">
            Repo Scout 聚合 GitHub Trending、搜索、项目详情和 AI 精选专题，帮助你更快判断一个项目是否适合学习、关注或尝试。
          </p>
          <div id="search" className="mt-8 flex flex-col gap-3 rounded-lg border border-line bg-white p-3 md:flex-row">
            <label className="flex flex-1 items-center gap-3 px-2" aria-label="搜索 GitHub 项目">
              <Search size={20} className="text-muted" aria-hidden="true" />
              <input
                className="w-full bg-transparent py-3 text-base outline-none"
                placeholder="搜索项目名、语言、主题，比如 Agent、Python、RAG"
              />
            </label>
            <button className="inline-flex items-center justify-center gap-2 rounded-md bg-accent px-5 py-3 font-medium text-white">
              <Search size={18} aria-hidden="true" />
              搜索
            </button>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {filters.map((filter) => (
              <button
                key={filter}
                className="rounded-md border border-line bg-white px-3 py-2 text-sm text-muted hover:border-accent hover:text-accent"
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        <aside id="featured" className="rounded-lg bg-ink p-6 text-white shadow-soft">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm text-white/60">AI Curated</p>
              <h2 className="text-2xl font-semibold">明星项目专题</h2>
            </div>
            <Sparkles className="text-amber-300" size={26} aria-hidden="true" />
          </div>
          <div className="space-y-4">
            {featuredProjects.map((project) => (
              <article key={project.repo} className="rounded-lg border border-white/12 bg-white/8 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm text-white/58">{project.title}</p>
                    <h3 className="mt-1 text-lg font-semibold">{project.repo}</h3>
                  </div>
                  <div className="rounded-md bg-white px-2 py-1 text-sm font-semibold text-ink">
                    {project.score}
                  </div>
                </div>
                <p className="mt-4 text-sm leading-6 text-white/72">{project.reason}</p>
              </article>
            ))}
          </div>
        </aside>
      </section>

      <section id="ranking" className="mx-auto max-w-7xl px-5 pb-12">
        <div className="rounded-lg bg-white/90 p-6 shadow-soft backdrop-blur">
          <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm text-muted">GitHub Trending</p>
              <h2 className="text-2xl font-semibold text-ink">今日热门项目榜单</h2>
            </div>
            <button className="inline-flex w-fit items-center gap-2 rounded-md border border-line px-4 py-2 text-sm text-ink">
              <BookOpen size={16} aria-hidden="true" />
              查看全部
            </button>
          </div>

          <div className="grid gap-4">
            {trendingRepositories.map((repository) => (
              <article
                key={repository.fullName}
                className="grid gap-4 rounded-lg border border-line bg-white p-5 md:grid-cols-[64px_1fr_auto]"
              >
                <div className="grid h-12 w-12 place-items-center rounded-md bg-panel text-lg font-semibold text-accent">
                  {repository.rank}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="text-lg font-semibold text-ink">{repository.fullName}</h3>
                    <span className="rounded-md bg-panel px-2 py-1 text-xs text-muted">{repository.language}</span>
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
                  <div className="text-sm">
                    <div className="flex items-center gap-1 font-semibold text-ink">
                      <Star size={16} className="text-amber" aria-hidden="true" />
                      {repository.stars}
                    </div>
                    <p className="mt-1 text-muted">{repository.gained} today</p>
                  </div>
                  <a
                    className="grid h-10 w-10 place-items-center rounded-md border border-line text-muted hover:border-accent hover:text-accent"
                    href={`https://github.com/${repository.fullName}`}
                    aria-label={`打开 ${repository.fullName}`}
                  >
                    <ExternalLink size={18} aria-hidden="true" />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
