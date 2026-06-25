# AI Curation Design

## Goal

Define Repo Scout's AI curation approach before implementation. The feature should help AI beginners understand which trending repositories are worth attention and why.

## Decision

Use rule-based scoring for candidate selection and ranking. Use AI only to generate user-facing reasons and collection descriptions from structured repository metadata and scores.

This keeps the ranking reproducible, testable, and cheap while still delivering the explanatory value promised by AI curation.

## Scope

In scope:

- Select candidates from the latest successful GitHub Trending ingestion.
- Score repositories by AI relevance, beginner friendliness, learning value, activity, and growth.
- Generate shortlists for collections such as beginner-friendly AI projects and notable developer tools.
- Generate concise reasons and collection descriptions with an AI model when configured.
- Store final collections and featured repositories in the existing featured tables.

Out of scope:

- Personalized recommendations.
- User behavior tracking.
- GitHub data sources beyond Trending.
- README deep analysis.
- Letting the model directly choose the final ranking without rule scores.

## Data Flow

1. Load repositories from the latest successful `TrendingRun`.
2. Compute deterministic scores from existing repository and snapshot fields.
3. Build a ranked shortlist for each collection target.
4. Send only the shortlist metadata and score summary to the AI curation service.
5. Validate the generated reason length and required fields.
6. Persist `FeaturedCollection` and `FeaturedRepository` rows.

## Scoring

Initial scoring dimensions:

- AI relevance: repository name, description, language, and topics indicate AI, LLM, agent, model, data, or developer tooling relevance.
- Beginner friendliness: description is clear, project purpose is understandable, and the stack is not too obscure.
- Learning value: project demonstrates reusable engineering ideas or common AI application patterns.
- Activity: stars and forks show enough adoption to be worth attention.
- Growth: `stars_gained` indicates current momentum.

The score should be deterministic so tests can verify ordering without calling an AI model.

## AI Role

The AI service generates:

- Collection descriptions.
- Per-repository selection reasons.
- Optional short category labels.

The AI service does not:

- Decide the final ranking.
- Invent facts outside stored repository metadata.
- Store raw long-form model responses in core display tables.

If no model is configured, the curation flow can still run with deterministic scoring and fallback template reasons.

## Storage

Use the existing data model:

- `FeaturedCollection` stores collection identity, description, prompt, model name, and timestamps.
- `FeaturedRepository` stores repository membership, rank, reason, beginner score, and learning value score.

If future auditing requires full model input and output retention, add a separate curation run log table instead of expanding the core display tables.

## Testing

Implementation should cover:

- Deterministic scoring for known repository fixtures.
- Candidate filtering and ranking.
- Fallback reason generation when no AI provider is configured.
- Persistence of collections and featured repositories without duplicates.
- API output shape for `GET /api/featured`.
