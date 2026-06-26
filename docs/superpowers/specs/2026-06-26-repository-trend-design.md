# Repository Trend Design

## Goal

Show a simple project trend signal without changing the database schema or adding a new analytics pipeline.

## Behavior

- Repository detail responses include `trend_delta_stars` and `trend_snapshot_count`.
- `trend_delta_stars` is calculated from the latest two `repository_snapshots` for the same repository.
- If fewer than two snapshots exist, `trend_delta_stars` is `null` and the frontend displays `暂无历史`.
- The detail page displays the formatted trend in the existing project signal panel.

## Data Flow

1. `GET /api/repositories/{owner}/{name}` loads the repository.
2. The API queries the latest two snapshots joined to their `TrendingRun` rows, ordered by newest run first.
3. The API returns the stars delta between the newest and previous snapshot.
4. The frontend formats positive deltas with a `+` prefix and shows neutral or missing history directly.

## Scope

This is intentionally a lightweight trend indicator. It does not add charts, time-series endpoints, schema migrations, multi-period aggregation, or external analytics jobs.

## Testing

- Backend unit test covers the two-snapshot delta calculation.
- Frontend view-model test covers trend delta formatting.
- Existing build, lint, typecheck, backend test, and script checks remain the validation baseline.
