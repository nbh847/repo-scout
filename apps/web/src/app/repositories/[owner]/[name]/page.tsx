import { ArrowLeft, ArrowRight, ExternalLink, Flame, GitFork, Star, TrendingUp } from "lucide-react";
import Link from "next/link";
import {
  type ApiFeaturedCollection,
  type ApiRepository,
  buildCollectionHref,
  buildRelatedCollectionProjects,
  buildRepositoryHref,
  buildRepositoryViewModel,
  formatTrendDelta,
} from "../../../repository-view-models";

export const dynamic = "force-dynamic";

type RepositoryDetail = ApiRepository & {
  featured_reason: string | null;
  featured_collection_slug: string | null;
  featured_collection_title: string | null;
  beginner_score: number | null;
  learning_value_score: number | null;
  trend_delta_stars: number | null;
  trend_snapshot_count: number;
};

type RepositoryDetailPageProps = {
  params: Promise<{
    owner: string;
    name: string;
  }>;
  searchParams?: Promise<{
    from?: string | string[];
  }>;
};

const apiBaseUrl = process.env.REPO_SCOUT_API_URL ?? "http://127.0.0.1:8000";

async function fetchRepositoryDetail(
  owner: string,
  name: string,
): Promise<{ data: RepositoryDetail | null; error: string | null }> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);

  try {
    const response = await fetch(
      `${apiBaseUrl}/api/repositories/${encodeURIComponent(owner)}/${encodeURIComponent(name)}`,
      {
        cache: "no-store",
        signal: controller.signal,
      },
    );
    if (!response.ok) {
      return { data: null, error: `API returned ${response.status}` };
    }
    return { data: (await response.json()) as RepositoryDetail, error: null };
  } catch {
    return { data: null, error: "API is not reachable" };
  } finally {
    clearTimeout(timeout);
  }
}

async function fetchFeaturedCollection(
  slug: string,
): Promise<{ data: ApiFeaturedCollection | null; error: string | null }> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2000);

  try {
    const response = await fetch(`${apiBaseUrl}/api/featured/${encodeURIComponent(slug)}`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!response.ok) {
      return { data: null, error: `API returned ${response.status}` };
    }
    return { data: (await response.json()) as ApiFeaturedCollection, error: null };
  } catch {
    return { data: null, error: "API is not reachable" };
  } finally {
    clearTimeout(timeout);
  }
}

function scoreLabel(value: number | null): string {
  return value ? `${value}/5` : "未精选";
}

function readReturnHref(searchParams?: { from?: string | string[] }): string {
  const rawValue = Array.isArray(searchParams?.from) ? searchParams?.from[0] : searchParams?.from;
  const value = rawValue?.trim() ?? "";
  if (!value.startsWith("/") || value.startsWith("//")) {
    return "/#ranking";
  }
  return value;
}

export default async function RepositoryDetailPage({ params, searchParams }: RepositoryDetailPageProps) {
  const { owner, name } = await params;
  const returnHref = readReturnHref(await searchParams);
  const result = await fetchRepositoryDetail(owner, name);

  if (!result.data) {
    return (
      <main className="min-h-screen bg-[#111325] px-4 py-6 text-ink sm:px-5 md:px-10 md:py-8">
        <div className="mx-auto max-w-4xl">
          <Link href={returnHref} className="inline-flex items-center gap-2 text-sm font-bold text-cyan">
            <ArrowLeft size={16} aria-hidden="true" />
            返回榜单
          </Link>
          <section className="mt-8 rounded-lg border border-amber/50 bg-amber/10 p-5 text-sm font-semibold text-amber md:mt-10 md:p-6">
            项目详情暂不可用：{result.error ?? "Repository not found"}
          </section>
        </div>
      </main>
    );
  }

  const repository = buildRepositoryViewModel(result.data);
  const reason =
    result.data.featured_reason ??
    "这个项目已经进入 Repo Scout 跟踪列表，可结合语言、热度和增长信号判断是否适合继续研究。";
  const collectionHref = result.data.featured_collection_slug
    ? buildCollectionHref(result.data.featured_collection_slug)
    : null;
  const collectionResult = result.data.featured_collection_slug
    ? await fetchFeaturedCollection(result.data.featured_collection_slug)
    : { data: null };
  const relatedProjects = buildRelatedCollectionProjects(collectionResult.data, repository.fullName);

  return (
    <main className="min-h-screen bg-[#111325] px-4 py-6 text-ink sm:px-5 md:px-10 md:py-8">
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-20" />
      <div className="relative mx-auto max-w-5xl">
        <Link href={returnHref} className="inline-flex items-center gap-2 text-sm font-bold text-cyan">
          <ArrowLeft size={16} aria-hidden="true" />
          返回榜单
        </Link>

        <section className="mt-7 grid gap-6 md:mt-8 lg:grid-cols-[minmax(0,1fr)_320px] lg:gap-8">
          <div>
            <p className="text-sm font-bold text-orange-400">{repository.language}</p>
            <h1 className="mt-3 break-words text-3xl font-black leading-tight text-ink sm:text-4xl md:text-6xl">
              {repository.fullName}
            </h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-muted md:mt-5 md:text-lg md:leading-8">
              {repository.summary}
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {repository.tags.map((tag) => (
                <span
                  key={tag}
                  className="max-w-full truncate rounded-full border border-[#315987] bg-[#10213d] px-3 py-1.5 text-xs font-black text-cyan"
                >
                  {tag}
                </span>
              ))}
            </div>

            <section className="mt-6 rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal md:mt-8 md:p-6">
              <h2 className="text-xl font-black text-ink sm:text-2xl">项目说明</h2>
              <p className="mt-4 text-sm font-semibold leading-7 text-muted sm:text-base md:leading-8">
                {repository.descriptionZh}
              </p>
              {repository.description !== repository.descriptionZh ? (
                <div className="mt-5 border-t border-[#254a76] pt-5">
                  <p className="text-xs font-black uppercase text-cyan">原始说明</p>
                  <p className="mt-2 text-sm font-semibold leading-7 text-muted sm:text-base md:leading-8">
                    {repository.description}
                  </p>
                </div>
              ) : null}
            </section>

            <section className="mt-6 rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal md:mt-8 md:p-6">
              <div className="flex items-center gap-3">
                <Flame className="text-orange-400" size={22} aria-hidden="true" />
                <h2 className="text-xl font-black text-ink sm:text-2xl">为什么值得关注</h2>
              </div>
              {collectionHref && result.data.featured_collection_title ? (
                <Link
                  href={collectionHref}
                  className="mt-3 inline-flex rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-xs font-black text-cyan hover:text-ink"
                >
                  {result.data.featured_collection_title}
                </Link>
              ) : null}
              <p className="mt-4 text-sm font-semibold leading-7 text-muted sm:text-base md:leading-8">{reason}</p>
            </section>

            {relatedProjects.length > 0 ? (
              <section className="mt-6 rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal md:mt-8 md:p-6">
                <h2 className="text-xl font-black text-ink sm:text-2xl">同专题更多项目</h2>
                <div className="mt-4 grid gap-3">
                  {relatedProjects.map((project) => (
                    <Link
                      key={project.repo}
                      href={buildRepositoryHref(project.repo, returnHref)}
                      className="rounded-lg border border-[#244169] bg-[#10213d] p-4 hover:border-cyan/50"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <h3 className="break-words text-sm font-black text-ink">{project.repo}</h3>
                        <span className="shrink-0 font-mono text-xs font-black text-amber">{project.score}</span>
                      </div>
                      <p className="mt-2 line-clamp-2 text-sm font-semibold leading-6 text-muted">{project.reason}</p>
                      <span className="mt-3 inline-flex items-center gap-1.5 text-xs font-black text-cyan">
                        查看项目
                        <ArrowRight size={14} aria-hidden="true" />
                      </span>
                    </Link>
                  ))}
                </div>
              </section>
            ) : null}
          </div>

          <aside className="rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal md:p-6">
            <h2 className="text-lg font-black text-ink">项目信号</h2>
            <div className="mt-5 grid gap-4 text-sm font-bold text-muted">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Star size={16} className="text-amber" aria-hidden="true" />
                  Stars
                </span>
                <span className="font-mono text-ink">{repository.stars}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <GitFork size={16} className="text-cyan" aria-hidden="true" />
                  Forks
                </span>
                <span className="font-mono text-ink">{repository.forks}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>近期增长</span>
                <span className="font-mono text-orange-400">{repository.gained}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <TrendingUp size={16} className="text-emerald-400" aria-hidden="true" />
                  历史趋势
                </span>
                <span className="font-mono text-emerald-400">{formatTrendDelta(result.data.trend_delta_stars)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>入门友好</span>
                <span className="font-mono text-ink">{scoreLabel(result.data.beginner_score)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>学习价值</span>
                <span className="font-mono text-ink">{scoreLabel(result.data.learning_value_score)}</span>
              </div>
            </div>
            <a
              href={repository.url}
              className="mt-7 flex h-11 items-center justify-between rounded-lg bg-orange-500 px-4 text-sm font-black text-white"
            >
              打开 GitHub
              <ExternalLink size={16} aria-hidden="true" />
            </a>
          </aside>
        </section>
      </div>
    </main>
  );
}
