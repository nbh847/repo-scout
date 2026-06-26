# Trending Filter Design

## Goal

Add product-enhancement filtering for the homepage GitHub Trending list without expanding scope into recommendation, deployment, or database migration work.

## Behavior

- The homepage supports Trending period filters: `daily`, `weekly`, and `monthly`.
- The homepage supports language filters for the Trending list.
- When no search keyword is present, the frontend calls `/api/repositories/trending` with `period`, optional `language`, and `limit`.
- When a search keyword is present, the frontend calls `/api/repositories/search` with `q` and `limit`; Trending period and language filters do not affect keyword search.
- The backend returns snapshots from the latest successful `github_trending` run matching the requested `period` and optional `language`.
- If no matching run exists, the API returns an empty list rather than falling back to unrelated data.

## Components

- `apps/api/app/main.py`: extends the existing Trending query handler with optional `period` and `language` filters.
- `apps/web/src/app/repository-view-models.ts`: owns the tested API path builder used by the homepage.
- `apps/web/src/app/page.tsx`: reads URL params, renders period/language controls, and passes filters to the API path builder.
- `scripts/local-demo.sh`: already supports `--period` and `--language`, so no runtime script change is needed.

## Testing

- Backend unit test verifies that Trending results select the latest successful run matching `period` and `language`.
- Frontend view-model test verifies that Trending API paths include filters and search API paths ignore Trending filters.
- Full validation remains the existing backend, frontend, build, and script-documentation checks.
