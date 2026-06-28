export type ApiRepository = {
  rank?: number;
  owner: string;
  name: string;
  full_name: string;
  url: string;
  description: string | null;
  summary_zh: string | null;
  description_zh: string | null;
  primary_language: string | null;
  topics: string[];
  stars: number;
  forks: number;
  stars_gained?: number;
};

export type RepositoryViewModel = {
  rank: number;
  owner: string;
  name: string;
  fullName: string;
  url: string;
  description: string;
  summary: string;
  descriptionZh: string;
  language: string;
  stars: string;
  forks: string;
  gained: string;
  tags: string[];
  fit: string;
};

export type ApiFeaturedRepository = ApiRepository & {
  reason: string;
  beginner_score: number;
  learning_value_score: number;
};

export type ApiFeaturedCollection = {
  slug: string;
  title: string;
  description?: string | null;
  repositories: ApiFeaturedRepository[];
};

export type FeaturedProjectViewModel = {
  title: string;
  collectionSlug: string;
  collectionSize: number;
  repo: string;
  reason: string;
  score: string;
  stars: string;
};

export type RelatedProjectViewModel = {
  repo: string;
  reason: string;
  score: string;
};

export type MetricViewModel = {
  label: string;
  value: string;
};

export type RepositoryApiPathOptions = {
  query: string;
  period: string;
  language: string;
  limit?: number;
};

export type RepositorySortMode = "ranking" | "stars" | "gained";

export function buildRepositoryLanguagesApiPath(): string {
  return "/api/repositories/languages";
}

export function buildRepositoryApiPath(options: RepositoryApiPathOptions): string {
  const query = options.query.trim();
  const limit = options.limit ?? 20;
  if (query) {
    const params = new URLSearchParams();
    params.set("q", query);
    params.set("limit", String(limit));
    if (options.language) {
      params.set("language", options.language);
    }
    return `/api/repositories/search?${params.toString()}`;
  }

  const params = new URLSearchParams();
  params.set("limit", String(limit));
  if (options.period) {
    params.set("period", options.period);
  }
  if (options.language) {
    params.set("language", options.language);
  }
  return `/api/repositories/trending?${params.toString()}`;
}

export function buildRepositoryHref(fullName: string, returnHref = ""): string {
  const separatorIndex = fullName.indexOf("/");
  const owner = separatorIndex >= 0 ? fullName.slice(0, separatorIndex) : fullName;
  const name = separatorIndex >= 0 ? fullName.slice(separatorIndex + 1) : "";
  const href = `/repositories/${encodeURIComponent(owner)}/${encodeURIComponent(name)}`;
  if (!returnHref) {
    return href;
  }
  const params = new URLSearchParams();
  params.set("from", returnHref);
  return `${href}?${params.toString()}`;
}

export function buildCollectionHref(slug: string): string {
  return `/collections/${encodeURIComponent(slug)}`;
}

export function formatTrendDelta(value: number | null): string {
  if (value === null) {
    return "暂无历史";
  }
  if (value > 0) {
    return `+${value}`;
  }
  return String(value);
}

function formatCount(value: number): string {
  if (value < 1000) {
    return String(value);
  }

  const thousands = value / 1000;
  const formatted = Number.isInteger(thousands) ? String(thousands) : thousands.toFixed(1);
  return `${formatted}k`;
}

export function buildRepositoryViewModel(
  repository: ApiRepository,
  index = 0,
): RepositoryViewModel {
  const language = repository.primary_language ?? "Unknown";
  const topics = repository.topics.slice(0, 3);

  return {
    rank: repository.rank ?? index + 1,
    owner: repository.owner,
    name: repository.name,
    fullName: repository.full_name,
    url: repository.url,
    description: repository.description ?? "No description provided.",
    summary: repository.summary_zh ?? "暂无中文摘要。",
    descriptionZh: repository.description_zh ?? "暂无中文说明。",
    language,
    stars: formatCount(repository.stars),
    forks: formatCount(repository.forks),
    gained: `+${repository.stars_gained ?? 0}`,
    tags: topics.length > 0 ? topics : [language],
    fit: language === "Unknown" ? "General" : language,
  };
}

export function sortRepositories(
  repositories: ApiRepository[],
  sortMode: RepositorySortMode,
): ApiRepository[] {
  if (sortMode === "ranking") {
    return [...repositories];
  }

  return [...repositories].sort((left, right) => {
    const valueDiff =
      sortMode === "stars"
        ? right.stars - left.stars
        : (right.stars_gained ?? 0) - (left.stars_gained ?? 0);
    if (valueDiff !== 0) {
      return valueDiff;
    }
    return (left.rank ?? 0) - (right.rank ?? 0);
  });
}

export function repositoryMetricForSort(
  repository: RepositoryViewModel,
  sortMode: RepositorySortMode,
): { label: string; value: string } {
  if (sortMode === "gained") {
    return { label: "新增 Stars", value: repository.gained };
  }
  return { label: "Stars", value: repository.stars };
}

export function paginateRepositories<T>(
  items: T[],
  requestedPage: number,
  pageSize: number,
): { items: T[]; page: number; totalPages: number; totalItems: number } {
  const totalItems = items.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const page = Math.min(Math.max(1, requestedPage), totalPages);
  const start = (page - 1) * pageSize;
  return {
    items: items.slice(start, start + pageSize),
    page,
    totalPages,
    totalItems,
  };
}

export function buildMetrics(repositories: RepositoryViewModel[]): MetricViewModel[] {
  const languages = new Set(repositories.map((repository) => repository.language));

  return [
    { label: "Tracked repos", value: String(repositories.length) },
    { label: "Languages", value: String(languages.size) },
  ];
}

export function buildFeaturedProjects(collections: ApiFeaturedCollection[] | null): FeaturedProjectViewModel[] {
  if (!collections) {
    return [];
  }

  return collections.flatMap((collection) => {
    const repository = collection.repositories[0];
    if (!repository) {
      return [];
    }

    return [
      {
        title: collection.title,
        collectionSlug: collection.slug,
        collectionSize: collection.repositories.length,
        repo: repository.full_name,
        reason: repository.reason,
        score: ((repository.beginner_score + repository.learning_value_score) / 2).toFixed(1),
        stars: formatCount(repository.stars),
      },
    ];
  });
}

export function buildRelatedCollectionProjects(
  collection: ApiFeaturedCollection | null,
  currentFullName: string,
  limit = 3,
): RelatedProjectViewModel[] {
  if (!collection) {
    return [];
  }

  return collection.repositories
    .filter((repository) => repository.full_name !== currentFullName)
    .slice(0, limit)
    .map((repository) => ({
      repo: repository.full_name,
      reason: repository.reason,
      score: ((repository.beginner_score + repository.learning_value_score) / 2).toFixed(1),
    }));
}
