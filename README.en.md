# Repo Scout

English | [简体中文](./README.md)

Repo Scout is an AI-friendly GitHub repository discovery platform for beginners.

It helps users discover GitHub projects worth learning from, following, or trying through trending rankings, search, AI-curated collections, and automated data updates.

## What It Does

Repo Scout is designed for people who are starting to learn AI and open source. It is not a code hosting platform or a full recommendation engine. It is a focused discovery tool for browsing, searching, and understanding trending GitHub repositories.

## Planned Features

- Trending repository rankings from GitHub Trending
- Search by keyword, language, topic, and popularity
- AI-curated featured project collections for beginners
- Repository detail pages with stars, language, description, topics, and repository links
- Backend database for repository snapshots and ranking history
- Scheduled GitHub Trending ingestion for automated updates

## Target Users

- AI beginners looking for projects to learn from
- Developers tracking open-source AI tools
- Builders looking for useful GitHub repositories and project inspiration

## Status

This project is in the product enhancement stage. See [ROADMAP.md](./ROADMAP.md) for the current progress.

## Docs

- [MVP Scope](./docs/mvp.md)
- [Architecture Plan](./docs/architecture.md)
- [Data Model Design](./docs/data-model.md)
- [Runtime Acceptance Record](./docs/runtime-acceptance.md)
- [MVP Release Checklist](./docs/mvp-release-checklist.md)
- [Dependency Risk Record](./docs/dependency-risks.md)
- [MVP Release Readiness Summary](./docs/release-readiness.md)

## Local Development

The project uses a lightweight monorepo structure:

- `apps/web`: Next.js frontend.
- `apps/api`: FastAPI backend.

Install dependencies:

```bash
npm install
cd apps/api
python -m venv .venv
.venv/bin/python -m pip install -e .
cd ../..
```

Run a real-data end-to-end demo:

```bash
scripts/local-demo.sh --real --period daily --limit 20
scripts/local-demo.sh --real --period weekly --language Python --limit 20
```

Use sample data when offline or when you only need a local demo:

```bash
scripts/local-demo.sh --sample
```

The demo script writes local SQLite data, generates AI-curated collections, and starts:

- Backend API: `http://127.0.0.1:8000`
- Frontend page: `http://127.0.0.1:3000`

You can also run the steps manually:

```bash
npm run ingest:trending -- --period daily --limit 20
npm run ingest:trending -- --period weekly --language Python --limit 20
npm run curate:featured -- --limit 5
npm run dev:api
npm run dev:web
```

Run the complete local release validation before delivery:

```bash
scripts/validate-local-release.sh
```

The backend uses a local SQLite database by default. The database file is stored in `data/`, which is ignored by git. AI curation defaults to deterministic rule scoring and local template reasons. When `REPO_SCOUT_OPENAI_BASE_URL`, `REPO_SCOUT_OPENAI_API_KEY`, and `REPO_SCOUT_OPENAI_MODEL` are configured together, Repo Scout calls an OpenAI-compatible `chat/completions` endpoint for featured reasons and falls back to local templates on model failures.
