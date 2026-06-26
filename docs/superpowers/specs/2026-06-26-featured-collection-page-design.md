# Featured Collection Page Design

## Goal

Add a focused page for existing AI curated collections without introducing admin UI, user accounts, or new collection management flows.

## Behavior

- `GET /api/featured/{slug}` returns one featured collection by slug.
- Missing slugs return 404.
- The homepage links curated collection titles to `/collections/{slug}`.
- `/collections/[slug]` fetches the matching collection and lists ranked repositories with reasons and scores.

## Components

- `apps/api/app/main.py`: extracts collection serialization into a reusable helper and adds the single-collection endpoint.
- `apps/web/src/app/repository-view-models.ts`: adds `buildCollectionHref`.
- `apps/web/src/app/page.tsx`: links featured collection titles to the new route.
- `apps/web/src/app/collections/[slug]/page.tsx`: renders the collection page.

## Scope

This page only displays already-generated collections. It does not create, edit, delete, schedule, or regenerate collections.

## Testing

- Backend unit test covers single-collection lookup by slug.
- Frontend view-model test covers collection URL generation.
- Full validation uses the standard backend, frontend, build, and script checks.
