import {
  ArrowRight,
  ExternalLink,
  Flame,
  Radar,
  RotateCcw,
  Search,
  SlidersHorizontal,
  Sparkles,
  Star,
  Timer,
} from "lucide-react";
import Link from "next/link";
import {
  type ApiRepository,
  type ApiFeaturedCollection,
  buildCollectionHref,
  buildFeaturedProjects,
  buildRepositoryApiPath,
  buildRepositoryLanguagesApiPath,
  buildRepositoryHref,
  buildMetrics,
  buildRepositoryViewModel,
  type RepositorySortMode,
  type RepositoryViewModel,
  sortRepositories,
} from "./repository-view-models";

export const dynamic = "force-dynamic";

type SearchParams = {
  q?: string | string[];
  period?: string | string[];
  language?: string | string[];
  sort?: string | string[];
};

type HomeProps = {
  searchParams?: Promise<SearchParams>;
};

const apiBaseUrl = process.env.REPO_SCOUT_API_URL ?? "http://127.0.0.1:8000";

const intentFilters = ["全部项目", "好玩", "好用"];
const periodFilters = [
  { label: "日榜", value: "daily" },
  { label: "周榜", value: "weekly" },
  { label: "月榜", value: "monthly" },
];
const sortFilters: { label: string; value: RepositorySortMode }[] = [
  { label: "榜单排名", value: "ranking" },
  { label: "Stars", value: "stars" },
  { label: "新增 Stars", value: "gained" },
];
const fallbackLanguageFilters = ["Python", "TypeScript", "Go", "Rust", "JavaScript"];
const scoreRows = [
  { label: "热度", color: "bg-orange-400", value: 8.8 },
  { label: "增长", color: "bg-cyan", value: 8.4 },
  { label: "学习", color: "bg-emerald-400", value: 8.1 },
  { label: "综合", color: "bg-violet-400", value: 8.5 },
];

async function fetchApi<T>(path: string): Promise<{ data: T | null; error: string | null }> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);

  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      return { data: null, error: `API returned ${response.status}` };
    }
    return { data: (await response.json()) as T, error: null };
  } catch {
    return { data: null, error: "API is not reachable" };
  } finally {
    clearTimeout(timeout);
  }
}

function readSingleParam(value?: string | string[]): string {
  if (Array.isArray(value)) {
    return value[0]?.trim() ?? "";
  }
  return value?.trim() ?? "";
}

function readSearchQuery(searchParams?: SearchParams): string {
  return readSingleParam(searchParams?.q);
}

function readPeriod(searchParams?: SearchParams): string {
  const period = readSingleParam(searchParams?.period);
  return periodFilters.some((filter) => filter.value === period) ? period : "daily";
}

function readLanguage(searchParams: SearchParams | undefined, languageFilters: string[]): string {
  const language = readSingleParam(searchParams?.language);
  return languageFilters.includes(language) ? language : "";
}

function readSort(searchParams?: SearchParams): RepositorySortMode {
  const sort = readSingleParam(searchParams?.sort);
  return sortFilters.some((filter) => filter.value === sort) ? (sort as RepositorySortMode) : "ranking";
}

function buildHomeFilterHref(period: string, language: string, sort: RepositorySortMode): string {
  const params = new URLSearchParams();
  params.set("period", period);
  if (language) {
    params.set("language", language);
  }
  if (sort !== "ranking") {
    params.set("sort", sort);
  }
  return `/?${params.toString()}#ranking`;
}

function metricValue(metrics: ReturnType<typeof buildMetrics>, label: string): string {
  return metrics.find((metric) => metric.label === label)?.value ?? "0";
}

function scoreFor(repository: RepositoryViewModel, offset: number): number {
  const seed = repository.rank + repository.fullName.length + offset;
  return Number((7.2 + (seed % 18) / 10).toFixed(1));
}

function scoreWidth(value: number): string {
  return `${Math.min(96, Math.max(28, value * 10))}%`;
}

export default async function Home({ searchParams }: HomeProps) {
  const params = await searchParams;
  const query = readSearchQuery(params);
  const period = readPeriod(params);
  const languageResult = await fetchApi<string[]>(buildRepositoryLanguagesApiPath());
  const languageFilters = languageResult.data?.length ? languageResult.data : fallbackLanguageFilters;
  const language = readLanguage(params, languageFilters);
  const sort = readSort(params);
  const [repositoryResult, featuredResult] = await Promise.all([
    fetchApi<ApiRepository[]>(buildRepositoryApiPath({ query, period, language })),
    fetchApi<ApiFeaturedCollection[]>("/api/featured"),
  ]);
  const repositories: RepositoryViewModel[] = sortRepositories(repositoryResult.data ?? [], sort).map((repository, index) =>
    buildRepositoryViewModel(repository, index),
  );
  const activeSortLabel = sortFilters.find((filter) => filter.value === sort)?.label ?? "榜单排名";
  const featuredProjects = buildFeaturedProjects(featuredResult.data);
  const metrics = buildMetrics(repositories);
  const dataError = repositoryResult.error ?? featuredResult.error;
  const primaryRepositories = repositories.slice(0, 6);
  const starRepositories = repositories.slice(0, 4);
  const sidebarProjects =
    featuredProjects.length > 0
        ? featuredProjects
        : starRepositories.map((repository) => ({
            title: "GitHub Trending",
            collectionSlug: "",
            repo: repository.fullName,
            reason: repository.description,
          score: repository.gained,
        }));

  return (
    <main className="min-h-screen overflow-hidden bg-[#111325] text-ink">
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-20" />
      <div className="pointer-events-none fixed inset-0 bg-scanline opacity-10" />

      <div className="relative mx-auto min-h-screen max-w-[1500px] px-4 py-5 sm:px-5 md:px-8 lg:px-12">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/" className="flex min-w-0 items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-full border border-orange-400/40 bg-orange-500/10 text-orange-400 shadow-radar">
              <Radar size={22} aria-hidden="true" />
            </span>
            <span className="min-w-0 text-base font-bold text-ink sm:text-lg">Repo Scout 开源雷达</span>
          </Link>
          <nav className="grid grid-cols-2 gap-2 rounded-lg bg-panel/30 p-1 text-center text-sm font-semibold text-muted sm:flex sm:items-center">
            <a href="#ranking" className="rounded-md px-3 py-2 text-ink hover:bg-panel sm:px-4">
              项目榜单
            </a>
            <a href="#useful-projects" className="rounded-md px-3 py-2 hover:bg-panel hover:text-ink sm:px-4">
              明星项目
            </a>
          </nav>
        </header>

        <section className="mx-auto max-w-4xl pb-9 pt-10 text-center md:pb-12 md:pt-16">
          <h1 className="text-balance text-3xl font-black leading-tight text-ink sm:text-4xl md:text-6xl">
            发现你的下一个开源练手项目
          </h1>
          <p className="mx-auto mt-4 max-w-3xl text-base font-semibold leading-7 text-muted md:mt-5 md:text-xl md:leading-8">
            按语言、热度和增长筛选 GitHub 项目，找到适合 AI 学习和产品练手的真实仓库
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3 md:mt-8 md:gap-4">
            {intentFilters.map((filter, index) => (
              <a
                key={filter}
                href={index === 0 ? "#ranking" : index === 1 ? "#fun-projects" : "#useful-projects"}
                className={`inline-flex h-11 min-w-[96px] items-center justify-center rounded-full px-5 text-sm font-bold shadow-terminal transition md:h-12 md:min-w-[108px] md:px-7 ${
                  index === 0
                    ? "bg-orange-500 text-white shadow-[0_0_24px_rgba(249,115,22,0.35)]"
                    : "border border-[#244169] bg-[#17213d] text-muted hover:border-cyan/40 hover:text-ink"
                }`}
              >
                {filter}
              </a>
            ))}
          </div>
        </section>

        <section className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px] lg:gap-9">
          <div>
            <form id="ranking" action="/" className="scroll-mt-8 grid gap-4">
              <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_230px]">
                <label
                  className="flex min-h-14 items-center gap-4 rounded-lg border border-[#244169] bg-[#10213d]/90 px-5 shadow-terminal"
                  aria-label="搜索 GitHub 项目"
                >
                  <Search size={22} className="text-muted" aria-hidden="true" />
                  <input
                    name="q"
                    defaultValue={query}
                    className="w-full bg-transparent text-base font-semibold text-ink outline-none placeholder:text-muted"
                    placeholder="搜索项目名称或技术..."
                  />
                  <input type="hidden" name="period" value={period} />
                  {language ? <input type="hidden" name="language" value={language} /> : null}
                  {sort !== "ranking" ? <input type="hidden" name="sort" value={sort} /> : null}
                </label>
                <div className="grid min-h-14 gap-3 rounded-lg border border-[#244169] bg-[#10213d]/90 px-4 py-3 text-sm font-bold text-muted shadow-terminal">
                  <div className="flex items-center justify-between gap-3">
                    <span>排序</span>
                    <span className="flex items-center gap-2 text-cyan">
                      {activeSortLabel}
                      <SlidersHorizontal size={17} aria-hidden="true" />
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {sortFilters.map((filter) => (
                      <Link
                        key={filter.value}
                        href={buildHomeFilterHref(period, language, filter.value)}
                        className={`inline-flex h-8 min-w-0 items-center justify-center rounded-md border px-2 text-xs font-black transition ${
                          sort === filter.value
                            ? "border-cyan bg-cyan/15 text-cyan"
                            : "border-[#244169] bg-[#17213d] text-muted hover:text-ink"
                        }`}
                      >
                        {filter.label}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-3 overflow-x-auto pb-1 sm:flex-wrap sm:overflow-visible">
                {periodFilters.map((filter) => (
                  <Link
                    key={filter.value}
                    href={buildHomeFilterHref(filter.value, language, sort)}
                    className={`inline-flex h-10 min-w-[70px] shrink-0 items-center justify-center rounded-full border px-4 text-sm font-bold transition ${
                      period === filter.value
                        ? "border-orange-500 bg-orange-500 text-white"
                        : "border-[#244169] bg-[#10213d]/80 text-muted hover:text-ink"
                    }`}
                  >
                    {filter.label}
                  </Link>
                ))}
              </div>

              <div className="flex gap-3 overflow-x-auto pb-1 sm:flex-wrap sm:overflow-visible">
                {["全部", ...languageFilters].map((filter, index) => (
                  <Link
                    key={filter}
                    href={buildHomeFilterHref(period, index === 0 ? "" : filter, sort)}
                    className={`inline-flex h-10 min-w-[74px] shrink-0 items-center justify-center rounded-full border px-4 text-sm font-bold transition ${
                      (index === 0 && !language) || language === filter
                        ? "border-orange-500 bg-orange-500 text-white"
                        : "border-[#244169] bg-[#10213d]/80 text-muted hover:text-ink"
                    }`}
                  >
                    {filter}
                  </Link>
                ))}
              </div>
            </form>

            {dataError ? (
              <div className="mt-8 rounded-lg border border-amber/50 bg-amber/10 p-5 text-sm font-semibold text-amber">
                后端数据暂不可用：{dataError}
              </div>
            ) : null}
            {primaryRepositories.length === 0 && !dataError ? (
              <div className="mt-8 flex flex-col gap-4 rounded-lg border border-line/80 bg-surface/70 p-5 text-sm text-muted shadow-terminal sm:flex-row sm:items-center sm:justify-between">
                <span>暂无匹配项目。换一个关键词重新扫描。</span>
                <Link
                  href="/#ranking"
                  className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 text-sm font-black text-white"
                >
                  <RotateCcw size={16} aria-hidden="true" />
                  清除筛选
                </Link>
              </div>
            ) : null}

            <div id="fun-projects" className="mt-7 scroll-mt-8">
              <div className="mb-4 flex items-end justify-between gap-4">
                <div>
                  <p className="text-sm font-bold text-orange-400">好玩项目</p>
                  <h2 className="mt-1 text-xl font-black text-ink sm:text-2xl">适合拆解和练手的项目卡片</h2>
                </div>
                <span className="hidden rounded-full border border-[#244169] bg-[#10213d] px-4 py-2 text-sm font-bold text-muted md:inline-flex">
                  {primaryRepositories.length} repos
                </span>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {primaryRepositories.map((repository) => (
                <Link
                  key={repository.fullName}
                  href={buildRepositoryHref(repository.fullName)}
                  className="flex min-h-[320px] flex-col rounded-lg border border-[#254a76] bg-[#172b50]/90 p-4 shadow-terminal sm:min-h-[360px] sm:p-5 xl:min-h-[382px]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <h2 className="min-w-0 break-words text-lg font-black leading-tight text-ink sm:text-xl">{repository.name}</h2>
                    <span className="shrink-0 rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-sm font-bold text-cyan">
                      {repository.language}
                    </span>
                  </div>

                  <p className="mt-4 line-clamp-3 min-h-[72px] text-sm font-semibold leading-6 text-muted">
                    {repository.description}
                  </p>
                  <div className="mt-3 flex min-h-[32px] flex-wrap gap-2">
                    {repository.tags.map((tag) => (
                      <span
                        key={tag}
                        className="max-w-full truncate rounded-full border border-[#315987] bg-[#10213d] px-3 py-1 text-xs font-black text-cyan"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 grid gap-3">
                    {scoreRows.map((row, index) => {
                      const value = index === 3 ? scoreFor(repository, 4) : scoreFor(repository, index);
                      return (
                        <div key={row.label} className="grid grid-cols-[76px_1fr_38px] items-center gap-3">
                          <span className="text-sm font-bold text-muted">{row.label}</span>
                          <span className="h-2.5 rounded-full bg-[#20395d]">
                            <span
                              className={`block h-full rounded-full ${row.color}`}
                              style={{ width: scoreWidth(value) }}
                            />
                          </span>
                          <span className="text-right font-mono text-sm font-bold text-muted">{value}</span>
                        </div>
                      );
                    })}
                  </div>

                  <div className="mt-auto flex flex-wrap items-center justify-between gap-3 pt-5 text-sm font-bold text-muted">
                    <span className="flex items-center gap-1.5">
                      难度
                      <span className="text-orange-400">●●</span>
                      <span className="text-[#2a3e5f]">●●●</span>
                    </span>
                    <span className="flex items-center gap-2">
                      <Timer size={15} aria-hidden="true" />
                      {repository.gained} stars
                    </span>
                  </div>
                </Link>
              ))}
              </div>
            </div>
          </div>

          <aside id="useful-projects" className="scroll-mt-8 lg:pt-[76px]">
            <div className="flex items-center gap-3">
              <Flame className="text-orange-400" size={25} aria-hidden="true" />
              <div>
                <p className="text-sm font-bold text-orange-400">好用项目</p>
                <h2 className="mt-1 text-xl font-black text-ink sm:text-2xl">GitHub 明星项目</h2>
                <p className="mt-1 text-sm font-semibold text-muted">最近增长最快的开源仓库</p>
              </div>
            </div>

            <div className="mt-6 grid gap-5">
              {sidebarProjects.map((project) => (
                <article
                  key={project.repo}
                  className="rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal"
                >
                  {project.collectionSlug ? (
                    <Link
                      href={buildCollectionHref(project.collectionSlug)}
                      className="text-xs font-bold text-cyan hover:text-ink"
                    >
                      {project.title}
                    </Link>
                  ) : (
                    <p className="text-xs font-bold text-cyan">{project.title}</p>
                  )}
                  <h3 className="mt-2 break-words text-lg font-black text-ink">{project.repo}</h3>
                  <p className="mt-3 line-clamp-3 text-sm font-semibold leading-6 text-muted">{project.reason}</p>
                  <div className="mt-4 flex items-center gap-2 text-sm font-bold text-muted">
                    <span className="h-2.5 w-2.5 rounded-full bg-cyan" />
                    AI Curated
                  </div>
                  <div className="mt-4 flex items-center gap-4 font-mono text-sm font-bold text-muted">
                    <span className="flex items-center gap-1.5">
                      <Star size={16} className="text-amber" aria-hidden="true" />
                      {project.score}
                    </span>
                    <span className="flex items-center gap-1.5 text-orange-400">
                      <Flame size={16} aria-hidden="true" />
                      Top pick
                    </span>
                  </div>
                  <Link
                    href={buildRepositoryHref(project.repo)}
                    className="mt-5 inline-flex h-10 items-center gap-2 rounded-lg bg-orange-500 px-4 text-sm font-black text-white"
                  >
                    查看
                    <ArrowRight size={16} aria-hidden="true" />
                  </Link>
                </article>
              ))}
            </div>

            <section className="mt-6 rounded-lg border border-line/80 bg-panel/50 p-5">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-muted">实时雷达</span>
                <Sparkles size={18} className="text-amber" aria-hidden="true" />
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-lg bg-[#10213d] p-4">
                  <p className="font-mono text-2xl font-black text-cyan">{metricValue(metrics, "Tracked repos")}</p>
                  <p className="mt-1 text-xs font-bold text-muted">项目</p>
                </div>
                <div className="rounded-lg bg-[#10213d] p-4">
                  <p className="font-mono text-2xl font-black text-cyan">{metricValue(metrics, "Languages")}</p>
                  <p className="mt-1 text-xs font-bold text-muted">语言</p>
                </div>
              </div>
              <a
                href="https://github.com/trending"
                className="mt-4 flex h-11 items-center justify-between rounded-lg border border-line bg-[#10213d] px-4 text-sm font-bold text-ink"
              >
                Open GitHub Trending
                <ExternalLink size={16} aria-hidden="true" />
              </a>
            </section>
          </aside>
        </section>
      </div>
    </main>
  );
}
