# GitHub Trending Ingestion Design

## Goal

Implement the first real-data ingestion path for Repo Scout by fetching GitHub Trending, parsing repository cards, and writing the results into the existing SQLAlchemy models.

## Scope

- Support `daily`, `weekly`, and `monthly` GitHub Trending periods.
- Support an optional language path segment, such as `python`.
- Parse repository owner, name, URL, description, language, stars, forks, and period stars gained.
- Upsert `Repository` rows by `full_name`.
- Create one `TrendingRun` and related `RepositorySnapshot` rows per ingestion.
- Provide a local CLI entry point for manual ingestion.

Out of scope:

- Scheduled jobs.
- AI curation.
- Admin HTTP trigger.
- New third-party dependencies.

## Architecture

Add one focused module under `apps/api/app/`:

- `github_trending.py` owns URL construction, HTML fetching, HTML parsing, and database ingestion.

The parser uses BeautifulSoup with the built-in `html.parser` parser backend. Tests use a local HTML fixture so parsing and ingestion can be verified without network access.

## Data Flow

1. Build a GitHub Trending URL from `period` and optional `language`.
2. Fetch HTML with a normal browser-like user agent.
3. Parse each repository card into a small value object.
4. Create a `TrendingRun` with `pending` status.
5. Upsert repositories and create snapshots in rank order.
6. Mark the run `success`; on failure, mark it `failed` with the error message.

## Error Handling

Invalid periods fail before network access. Fetch or parsing failures are recorded on the `TrendingRun` when a run has already started, then re-raised for the caller.

## Testing

- Parser tests cover repository fields and numeric normalization.
- Ingestion tests cover repository upsert, snapshot creation, and run metadata.
- Validation uses `python3 -m unittest discover apps/api/tests` and `python3 -m compileall apps/api/app`.
