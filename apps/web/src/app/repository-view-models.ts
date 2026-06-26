export type ApiRepository = {
  rank?: number;
  owner: string;
  name: string;
  full_name: string;
  url: string;
  description: string | null;
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
  language: string;
  stars: string;
  forks: string;
  gained: string;
  tags: string[];
  fit: string;
};

export type MetricViewModel = {
  label: string;
  value: string;
};

export type RepositoryApiPathOptions = {
  query: string;
  period: string;
  language: string;
};

export function buildRepositoryApiPath(options: RepositoryApiPathOptions): string {
  const query = options.query.trim();
  if (query) {
    return `/api/repositories/search?q=${encodeURIComponent(query)}&limit=20`;
  }

  const params = new URLSearchParams();
  params.set("limit", "20");
  if (options.period) {
    params.set("period", options.period);
  }
  if (options.language) {
    params.set("language", options.language);
  }
  return `/api/repositories/trending?${params.toString()}`;
}

export function buildRepositoryHref(fullName: string): string {
  const separatorIndex = fullName.indexOf("/");
  const owner = separatorIndex >= 0 ? fullName.slice(0, separatorIndex) : fullName;
  const name = separatorIndex >= 0 ? fullName.slice(separatorIndex + 1) : "";
  return `/repositories/${encodeURIComponent(owner)}/${encodeURIComponent(name)}`;
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
    language,
    stars: formatCount(repository.stars),
    forks: formatCount(repository.forks),
    gained: `+${repository.stars_gained ?? 0}`,
    tags: topics.length > 0 ? topics : [language],
    fit: language === "Unknown" ? "General" : language,
  };
}

export function buildMetrics(repositories: RepositoryViewModel[]): MetricViewModel[] {
  const languages = new Set(repositories.map((repository) => repository.language));

  return [
    { label: "Tracked repos", value: String(repositories.length) },
    { label: "Languages", value: String(languages.size) },
  ];
}
