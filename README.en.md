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

> Repo Scout **runs fully without any LLM configuration**. AI curation and Chinese summaries default to deterministic rule scoring and local templates. Configuring a model is an optional enhancement — see [Optional: LLM Enhancement](#optional-llm-enhancement).

The demo script writes local SQLite data, generates AI-curated collections, and starts:

- Backend API: `http://127.0.0.1:8000`
- Frontend page: `http://127.0.0.1:3000`

You can also run the steps manually:

```bash
npm run ingest:trending -- --period daily --limit 20
npm run ingest:trending -- --period weekly --language Python --limit 20
npm run curate:featured -- --limit 5
npm run backfill:content   # Regenerate Chinese summaries for existing repos (optional)
npm run dev:api
npm run dev:web
```

Run the complete local release validation before delivery:

```bash
scripts/validate-local-release.sh
```

The backend uses a local SQLite database by default. The database file is stored in `data/`, which is ignored by git.

## Optional: LLM Enhancement

Repo Scout's full functionality does not depend on any LLM. The following two capabilities run on local fallback paths when **no model is configured**:

- **AI featured reasons**: rule scoring + local template reasons.
- **Chinese summaries**: keyword profiles + the original English description.

Once an OpenAI-compatible model is configured, English descriptions that miss the local profiles are sent to the model for a factual Chinese summary, and AI featured reasons switch to model output. **If the model is unavailable, the request fails, or the response contains no Chinese, Repo Scout automatically falls back to the local path — the main flow is never broken**.

Create `.env.local` at the project root (already ignored by `.gitignore`):

```dotenv
REPO_SCOUT_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
REPO_SCOUT_OPENAI_API_KEY=your-api-key
REPO_SCOUT_OPENAI_MODEL=glm-4.7
```

All three variables must be set together to enable the model; if any is missing, the local fallback stays in effect. `scripts/local-demo.sh` sources this file automatically; when running commands manually, `set -a; source .env.local; set +a` first, or export the variables yourself.

Any OpenAI-compatible `chat/completions` endpoint works (e.g. Zhipu GLM, OpenAI, DeepSeek, Moonshot). **Never commit a real API key** — `.env.local` is already ignored; do not rename it or copy it elsewhere.

Once the model is enabled, you can backfill Chinese summaries for existing repositories in one pass:

```bash
npm run backfill:content
```

## Project Origin

The birth of this project is documented in Lin Yi LYi's video *"300 Employees for ¥0.3/Month"* — using the multi-agent collaboration of KimiWork desktop, an "open-source repository radar" went from local development to server deployment in 30 minutes.

🔗 https://www.bilibili.com/video/BV18Qjo6QEFw/
