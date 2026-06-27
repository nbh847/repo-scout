# GLM Repository Summary Design

## Goal

Replace the generic “具体功能暂未完成中文归纳” placeholder with a concise Chinese
function summary derived from each repository's existing GitHub description.

## Decision

Keep the current deterministic content profiles as the first choice. When a
repository has a non-Chinese description but matches no profile, call the
configured GLM-4.7 model through its OpenAI-compatible HTTP API.

This preserves the existing predictable summaries for recognized repository
types while allowing arbitrary clear descriptions to be summarized instead of
discarded.

## Configuration

Reuse the project's existing model environment variables:

- `REPO_SCOUT_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4`
- `REPO_SCOUT_OPENAI_MODEL=glm-4.7`
- `REPO_SCOUT_OPENAI_API_KEY` contains the local secret.

The secret is stored only in a Git-ignored local environment file and must
never appear in source code, tests, logs, or commits. No new SDK dependency is
needed. The local demo script loads that file before ingestion, curation, and
service startup; direct commands must receive the same variables through their
process environment.

## Content Flow

1. Preserve a Chinese GitHub description as the summary.
2. Use the existing deterministic profile when the name or description matches.
3. For an unmatched, non-empty English description, ask GLM-4.7 for one factual
   Chinese sentence describing the repository's function.
4. Validate and normalize the response before persistence.
5. If the model is unavailable or returns invalid content, use the original
   repository description instead of a generic placeholder.
6. If no description exists, use “暂无项目简介，无法归纳具体功能。”

Generated content remains persisted during ingestion or backfill. Page requests
never call the model.

## Model Request

The prompt includes only repository name, GitHub description, and primary
language. It instructs GLM-4.7 to:

- state only the repository's function;
- return one concise Chinese sentence;
- avoid commentary, recommendations, marketing language, and invented facts;
- return no labels, Markdown, or surrounding explanation.

Use a low temperature, a short output limit, and a bounded request timeout.

## Failure Handling

Model configuration is optional. Missing configuration, network failures,
non-2xx responses, malformed JSON, empty output, or non-Chinese output all use
the deterministic fallback. One failed model request must not fail an entire
Trending ingestion or backfill run.

## Backfill

Provide an explicit command that regenerates stored Chinese content. Run it
after implementation to replace the existing placeholder rows, then rerun
featured curation so dependent display content remains consistent.

## Testing

Cover:

- an unmatched English description uses a mocked GLM response;
- the request uses `glm-4.7` and the official OpenAI-compatible endpoint shape;
- missing configuration and request failures fall back to the original
  description;
- empty descriptions use the honest no-description message;
- existing Chinese descriptions and deterministic profiles do not call GLM;
- ingestion persists the generated Chinese content.
