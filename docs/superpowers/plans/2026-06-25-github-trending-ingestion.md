# GitHub Trending Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a zero-dependency GitHub Trending ingestion path that parses Trending HTML and writes repositories, runs, and snapshots into the existing database.

**Architecture:** Keep the feature in `apps/api/app/github_trending.py` so URL building, fetching, parsing, and ingestion stay together while the codebase is still small. Use Python standard library parsing and isolated unit tests with HTML fixtures.

**Tech Stack:** Python 3.11+, FastAPI project structure, SQLAlchemy ORM, `unittest`, `html.parser`, `urllib.request`.

---

## File Structure

- Create `apps/api/app/github_trending.py`: Trending URL builder, parser, fetcher, and database ingestion function.
- Create `apps/api/tests/test_github_trending.py`: parser and ingestion tests.
- Modify `package.json`: add a root script for manual Trending ingestion.
- Modify `ROADMAP.md`: move GitHub Trending ingestion from in progress to completed only after validation.

### Task 1: Parser

**Files:**
- Create: `apps/api/app/github_trending.py`
- Test: `apps/api/tests/test_github_trending.py`

- [ ] Write a failing parser test with one representative GitHub Trending article.
- [ ] Run `python3 -m unittest apps.api.tests.test_github_trending.GitHubTrendingParserTest`.
- [ ] Implement `TrendingRepository`, `build_trending_url`, `parse_count`, `parse_stars_gained`, and `parse_trending_html`.
- [ ] Run the parser test again and confirm it passes.

### Task 2: Database Ingestion

**Files:**
- Modify: `apps/api/app/github_trending.py`
- Test: `apps/api/tests/test_github_trending.py`

- [ ] Write a failing ingestion test that uses an in-memory SQLite database and two parsed repositories.
- [ ] Run `python3 -m unittest apps.api.tests.test_github_trending.GitHubTrendingIngestionTest`.
- [ ] Implement `ingest_trending_repositories` and `ingest_github_trending`.
- [ ] Run the ingestion test again and confirm it passes.

### Task 3: Manual CLI and Validation

**Files:**
- Modify: `apps/api/app/github_trending.py`
- Modify: `package.json`
- Modify: `ROADMAP.md`

- [ ] Add a `main()` function in `github_trending.py` with `--period`, `--language`, and `--limit`.
- [ ] Add `ingest:trending` script to `package.json`.
- [ ] Run `python3 -m unittest discover apps/api/tests`.
- [ ] Run `python3 -m compileall apps/api/app`.
- [ ] Update `ROADMAP.md` with completed ingestion work and fresh validation.
