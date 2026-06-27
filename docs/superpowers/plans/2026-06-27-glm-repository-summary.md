# GLM Repository Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate factual Chinese repository summaries with GLM-4.7 when deterministic profiles cannot interpret an existing English GitHub description.

**Architecture:** Keep profile matching inside `repository_content.py`, then add a small OpenAI-compatible HTTP fallback in the same focused module. Read model settings from the existing `REPO_SCOUT_OPENAI_*` process environment, persist generated text only during ingestion/backfill, and make every model failure degrade to source content rather than fail the batch.

**Tech Stack:** Python 3.11, standard-library `urllib`, SQLAlchemy, `unittest`, Bash, GLM-4.7 OpenAI-compatible Chat Completions.

---

### Task 1: Add GLM summary generation with safe fallback

**Files:**
- Modify: `apps/api/tests/test_repository_content.py`
- Modify: `apps/api/app/repository_content.py`

- [ ] **Step 1: Write failing tests for unmatched English descriptions**

Add tests that patch environment variables and `app.repository_content.request.urlopen`.
Assert that:

```python
summary == "用于在 Mac 上通过轻量虚拟机创建和运行 Linux 容器。"
"具体功能暂未完成中文归纳" not in description
```

Also inspect the captured request JSON and assert:

```python
payload["model"] == "glm-4.7"
payload["thinking"] == {"type": "disabled"}
payload["temperature"] == 0.2
request.full_url == "https://open.bigmodel.cn/api/paas/v4/chat/completions"
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
apps/api/.venv/bin/python -m unittest \
  apps.api.tests.test_repository_content.RepositoryChineseContentTest.test_summarizes_unmatched_english_description_with_configured_model -v
```

Expected: FAIL because unmatched descriptions still return the generic placeholder.

- [ ] **Step 3: Write failing fallback tests**

Add separate tests proving:

```python
summary == "An experimental project."
```

when configuration is missing or `urlopen` raises `URLError`, and:

```python
summary == "暂无项目简介，无法归纳具体功能。"
```

when the source description is empty. Assert Chinese descriptions and matching
profiles do not call `urlopen`.

- [ ] **Step 4: Implement the minimal GLM client**

In `repository_content.py`, add:

```python
@dataclass(frozen=True)
class ModelSummaryConfig:
    base_url: str
    api_key: str
    model: str
```

Add `load_model_summary_config()` using the three existing
`REPO_SCOUT_OPENAI_*` variables. Add `request_model_summary()` using
`urllib.request.Request` and `urlopen(..., timeout=20)`. Send repository name,
description, and language with instructions to return one factual Chinese
function sentence. Disable thinking, set `temperature` to `0.2`, and cap output
at 120 tokens.

Add `generate_model_summary()` that catches request, response, and validation
errors. Accept only a non-empty response containing Chinese characters.

Update `build_repository_chinese_content()` so unmatched content uses:

```python
function = generate_model_summary(...) or original or "暂无项目简介，无法归纳具体功能。"
```

Do not call the model for Chinese descriptions, empty descriptions, or matched
profiles. Do not add commentary to model-generated or fallback summaries.

- [ ] **Step 5: Run repository content tests and verify GREEN**

Run:

```bash
apps/api/.venv/bin/python -m unittest apps.api.tests.test_repository_content -v
```

Expected: all repository-content tests pass with no network request.

- [ ] **Step 6: Commit the model fallback**

```bash
git add apps/api/app/repository_content.py apps/api/tests/test_repository_content.py
git commit -m "feat: summarize unmatched repositories with GLM"
```

### Task 2: Load local model configuration in the demo workflow

**Files:**
- Modify: `scripts/test-local-demo.sh`
- Modify: `scripts/local-demo.sh`
- Modify: `README.md`

- [ ] **Step 1: Write a failing shell assertion**

Extend `scripts/test-local-demo.sh` to assert that `scripts/local-demo.sh`
mentions `.env.local` and that README documents the three
`REPO_SCOUT_OPENAI_*` variables without including a real key.

- [ ] **Step 2: Run the shell test and verify RED**

Run:

```bash
bash scripts/test-local-demo.sh
```

Expected: FAIL because `.env.local` loading is not implemented.

- [ ] **Step 3: Add local configuration loading**

Near the start of `scripts/local-demo.sh`, source a root `.env.local` only when
it exists:

```bash
if [[ -f "$ROOT_DIR/.env.local" ]]; then
  set -a
  source "$ROOT_DIR/.env.local"
  set +a
fi
```

Document the endpoint and model in README using `your-api-key` as the only
example secret. State that `.env.local` is ignored by Git.

- [ ] **Step 4: Run the shell test and verify GREEN**

Run:

```bash
bash scripts/test-local-demo.sh
```

Expected: exit 0.

- [ ] **Step 5: Commit local configuration support**

```bash
git add scripts/local-demo.sh scripts/test-local-demo.sh README.md
git commit -m "docs: configure local GLM summaries"
```

### Task 3: Add and run explicit content backfill

**Files:**
- Modify: `apps/api/tests/test_repository_content.py`
- Modify: `apps/api/app/repository_content.py`
- Modify: `package.json`

- [ ] **Step 1: Write a failing backfill CLI test**

Patch `SessionLocal` and `backfill_repository_chinese_content`, invoke `main()`,
and assert the service receives the session and reports the regenerated count.

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
apps/api/.venv/bin/python -m unittest \
  apps.api.tests.test_repository_content.RepositoryChineseContentTest.test_main_backfills_repository_content -v
```

Expected: FAIL because `repository_content.main` does not exist.

- [ ] **Step 3: Implement the backfill entry point**

Add `main()` to `repository_content.py`:

```python
def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        count = backfill_repository_chinese_content(db)
    print(f"Backfilled Chinese content for {count} repositories.")
```

Add:

```json
"backfill:content": "cd apps/api && .venv/bin/python -m app.repository_content"
```

to root `package.json`.

- [ ] **Step 4: Run the focused and full backend tests**

Run:

```bash
apps/api/.venv/bin/python -m unittest discover -s apps/api/tests -v
```

Expected: all backend tests pass with no live model calls.

- [ ] **Step 5: Commit the backfill command**

```bash
git add apps/api/app/repository_content.py apps/api/tests/test_repository_content.py package.json
git commit -m "feat: add repository content backfill command"
```

### Task 4: Configure, backfill, and verify runtime output

**Files:**
- Create locally, never commit: `.env.local`
- Modify: `ROADMAP.md`

- [ ] **Step 1: Create local GLM configuration**

Create `.env.local` with the authorized secret and:

```dotenv
REPO_SCOUT_OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
REPO_SCOUT_OPENAI_API_KEY=<local-secret>
REPO_SCOUT_OPENAI_MODEL=glm-4.7
```

Verify `git status --short --ignored .env.local` reports `!! .env.local`.

- [ ] **Step 2: Run the live backfill**

Load `.env.local` into the process environment, then run:

```bash
npm run backfill:content
```

Expected: the command reports the number of regenerated repositories without
printing the API key.

- [ ] **Step 3: Verify persisted summaries**

Query SQLite and assert:

```sql
select count(*) from repositories
where summary_zh = '具体功能暂未完成中文归纳。';
```

returns `0`. Manually inspect all formerly affected rows for factual,
description-grounded Chinese summaries.

- [ ] **Step 4: Regenerate featured collections**

With the same environment loaded, run:

```bash
npm run curate:featured -- --limit 5
```

Expected: five featured collections are regenerated successfully.

- [ ] **Step 5: Restart and smoke-test services**

Restart API and Web so they inherit `.env.local`, then verify:

```bash
curl -s http://127.0.0.1:8000/health
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000
```

Expected: API returns `"status":"ok"` and Web returns `200`.

- [ ] **Step 6: Update ROADMAP and run final verification**

Record only verified behavior in `ROADMAP.md`, then run:

```bash
apps/api/.venv/bin/python -m unittest discover -s apps/api/tests -v
bash scripts/test-local-demo.sh
git diff --check
git status --short
```

- [ ] **Step 7: Commit verified project state**

```bash
git add ROADMAP.md
git commit -m "docs: record GLM repository summaries"
```

