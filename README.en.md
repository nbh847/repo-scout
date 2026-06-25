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

This project is in the planning stage. See [ROADMAP.md](./ROADMAP.md) for the current progress.

## Docs

- [MVP Scope](./docs/mvp.md)
- [Architecture Plan](./docs/architecture.md)
- [Data Model Design](./docs/data-model.md)

## Local Development

The project uses a lightweight monorepo structure:

- `apps/web`: Next.js frontend.
- `apps/api`: FastAPI backend.

Frontend:

```bash
npm install
npm run dev:web
```

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e .
cd ../..
npm run dev:api
```

The backend uses a local SQLite database by default. The database file is stored in `data/`, which is ignored by git.
