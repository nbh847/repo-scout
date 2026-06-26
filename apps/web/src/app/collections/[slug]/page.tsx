import { ArrowLeft, ArrowRight, Sparkles, Star } from "lucide-react";
import Link from "next/link";
import {
  type ApiRepository,
  buildRepositoryHref,
  buildRepositoryViewModel,
} from "../../repository-view-models";

export const dynamic = "force-dynamic";

type FeaturedCollection = {
  slug: string;
  title: string;
  description: string | null;
  repositories: Array<
    ApiRepository & {
      rank: number;
      reason: string;
      beginner_score: number;
      learning_value_score: number;
    }
  >;
};

type CollectionPageProps = {
  params: Promise<{
    slug: string;
  }>;
};

const apiBaseUrl = process.env.REPO_SCOUT_API_URL ?? "http://127.0.0.1:8000";

async function fetchCollection(slug: string): Promise<{ data: FeaturedCollection | null; error: string | null }> {
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
    return { data: (await response.json()) as FeaturedCollection, error: null };
  } catch {
    return { data: null, error: "API is not reachable" };
  } finally {
    clearTimeout(timeout);
  }
}

export default async function CollectionPage({ params }: CollectionPageProps) {
  const { slug } = await params;
  const result = await fetchCollection(slug);

  if (!result.data) {
    return (
      <main className="min-h-screen bg-[#111325] px-4 py-6 text-ink sm:px-5 md:px-10 md:py-8">
        <div className="mx-auto max-w-4xl">
          <Link href="/" className="inline-flex items-center gap-2 text-sm font-bold text-cyan">
            <ArrowLeft size={16} aria-hidden="true" />
            返回首页
          </Link>
          <section className="mt-8 rounded-lg border border-amber/50 bg-amber/10 p-5 text-sm font-semibold text-amber md:mt-10 md:p-6">
            专题暂不可用：{result.error ?? "Featured collection not found"}
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#111325] px-4 py-6 text-ink sm:px-5 md:px-10 md:py-8">
      <div className="pointer-events-none fixed inset-0 bg-grid opacity-20" />
      <div className="relative mx-auto max-w-6xl">
        <Link href="/" className="inline-flex items-center gap-2 text-sm font-bold text-cyan">
          <ArrowLeft size={16} aria-hidden="true" />
          返回首页
        </Link>

        <header className="mt-7 max-w-4xl md:mt-8">
          <p className="flex items-center gap-2 text-sm font-bold text-orange-400">
            <Sparkles size={17} aria-hidden="true" />
            AI Curated
          </p>
          <h1 className="mt-3 text-3xl font-black leading-tight text-ink sm:text-4xl md:text-6xl">
            {result.data.title}
          </h1>
          <p className="mt-4 text-base font-semibold leading-7 text-muted md:text-lg md:leading-8">
            {result.data.description ?? "Repo Scout 根据规则评分和本地模板理由生成的精选专题。"}
          </p>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {result.data.repositories.map((item) => {
            const repository = buildRepositoryViewModel(item);
            const score = ((item.beginner_score + item.learning_value_score) / 2).toFixed(1);

            return (
              <article
                key={repository.fullName}
                className="flex min-h-[300px] flex-col rounded-lg border border-[#254a76] bg-[#172b50]/90 p-5 shadow-terminal"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-mono text-sm font-black text-orange-400">#{String(item.rank).padStart(2, "0")}</p>
                    <h2 className="mt-2 break-words text-xl font-black text-ink">{repository.fullName}</h2>
                  </div>
                  <span className="shrink-0 rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-sm font-bold text-cyan">
                    {repository.language}
                  </span>
                </div>

                <p className="mt-4 line-clamp-4 text-sm font-semibold leading-6 text-muted">{item.reason}</p>

                <div className="mt-auto flex items-center justify-between gap-3 pt-5">
                  <span className="flex items-center gap-1.5 font-mono text-sm font-bold text-amber">
                    <Star size={16} aria-hidden="true" />
                    {score}
                  </span>
                  <Link
                    href={buildRepositoryHref(repository.fullName)}
                    className="inline-flex h-10 items-center gap-2 rounded-lg bg-orange-500 px-4 text-sm font-black text-white"
                  >
                    查看项目
                    <ArrowRight size={16} aria-hidden="true" />
                  </Link>
                </div>
              </article>
            );
          })}
        </section>
      </div>
    </main>
  );
}
