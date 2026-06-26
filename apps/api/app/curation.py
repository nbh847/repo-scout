import argparse
from dataclasses import dataclass
import json
import os
from urllib import request

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import FeaturedCollection, FeaturedRepository, Repository, RepositorySnapshot, TrendingRun


AI_KEYWORDS = {
    "ai",
    "agent",
    "agents",
    "chat",
    "diffusion",
    "inference",
    "llm",
    "model",
    "models",
    "openai",
    "rag",
    "retrieval",
    "transformer",
}
DEVELOPER_TOOL_KEYWORDS = {
    "api",
    "automation",
    "cli",
    "developer",
    "devtool",
    "framework",
    "sdk",
    "tool",
    "toolkit",
}
AGENT_KEYWORDS = {
    "agent",
    "agents",
    "automation",
    "tool calling",
    "workflow",
    "rag",
    "retrieval",
}
LLM_TOOL_KEYWORDS = {"llm", "model", "models", "inference", "openai", "rag", "retrieval"}
COMMON_LEARNING_LANGUAGES = {"Python", "TypeScript", "JavaScript", "Go", "Rust"}
OPENAI_BASE_URL_ENV = "REPO_SCOUT_OPENAI_BASE_URL"
OPENAI_API_KEY_ENV = "REPO_SCOUT_OPENAI_API_KEY"
OPENAI_MODEL_ENV = "REPO_SCOUT_OPENAI_MODEL"


@dataclass(frozen=True)
class RepositoryScore:
    ai_relevance: int
    beginner_friendliness: int
    learning_value: int
    activity: int
    growth: int

    @property
    def total(self) -> int:
        return (
            self.ai_relevance * 3
            + self.beginner_friendliness * 2
            + self.learning_value * 2
            + self.activity
            + self.growth
        )


@dataclass(frozen=True)
class CurationCandidate:
    repository: Repository
    snapshot: RepositorySnapshot
    score: RepositoryScore


@dataclass(frozen=True)
class CollectionTarget:
    slug: str
    title: str
    description: str
    prompt: str
    minimum_ai_relevance: int = 1
    prefer_developer_tools: bool = False
    required_keywords: frozenset[str] = frozenset()


@dataclass(frozen=True)
class ModelReasonConfig:
    base_url: str
    api_key: str
    model: str


COLLECTION_TARGETS = [
    CollectionTarget(
        slug="beginner-friendly-ai",
        title="适合初学者的 AI 项目",
        description="从最新热门项目中挑选出定位清晰、学习价值明确的 AI 项目。",
        prompt="Select beginner-friendly AI repositories with clear learning value.",
        minimum_ai_relevance=3,
    ),
    CollectionTarget(
        slug="ai-agent-projects",
        title="AI Agent 项目",
        description="聚焦 Agent、工具调用、检索增强和自动化工作流方向的热门项目。",
        prompt="Select AI agent repositories focused on tool calling, retrieval, and automation workflows.",
        minimum_ai_relevance=3,
        required_keywords=frozenset(AGENT_KEYWORDS),
    ),
    CollectionTarget(
        slug="llm-tools",
        title="LLM 工具",
        description="聚焦大模型推理、模型调用、RAG 和开发集成工具的热门项目。",
        prompt="Select LLM tools for inference, RAG, model integration, and developer workflows.",
        minimum_ai_relevance=3,
        required_keywords=frozenset(LLM_TOOL_KEYWORDS),
    ),
    CollectionTarget(
        slug="notable-developer-tools",
        title="值得关注的开发工具",
        description="从最新热门项目中挑选出适合开发者试用、拆解或复用的工具型项目。",
        prompt="Select notable developer tools from recent GitHub Trending repositories.",
        prefer_developer_tools=True,
    ),
]


def score_repository(repository: Repository, stars_gained: int = 0) -> RepositoryScore:
    text = searchable_text(repository)
    ai_hits = count_keyword_hits(text, AI_KEYWORDS)
    tool_hits = count_keyword_hits(text, DEVELOPER_TOOL_KEYWORDS)
    description_words = len((repository.description or "").split())

    ai_relevance = clamp_score(1 + ai_hits)
    beginner_friendliness = clamp_score(
        2
        + (1 if 4 <= description_words <= 28 else 0)
        + (1 if repository.primary_language in COMMON_LEARNING_LANGUAGES else 0)
        + (1 if ai_hits or tool_hits else 0)
    )
    learning_value = clamp_score(
        2
        + (1 if ai_hits else 0)
        + (1 if tool_hits else 0)
        + (1 if repository.primary_language in COMMON_LEARNING_LANGUAGES else 0)
    )
    activity = score_activity(repository.stars, repository.forks)
    growth = score_growth(stars_gained)

    return RepositoryScore(
        ai_relevance=ai_relevance,
        beginner_friendliness=beginner_friendliness,
        learning_value=learning_value,
        activity=activity,
        growth=growth,
    )


def curate_featured_collections(db: Session, limit: int = 5) -> list[FeaturedCollection]:
    candidates = load_latest_trending_candidates(db)
    if not candidates:
        return []

    collections: list[FeaturedCollection] = []
    for target in COLLECTION_TARGETS:
        shortlist = select_shortlist(candidates, target, limit)
        if not shortlist:
            continue

        collection = upsert_collection(db, target)
        db.flush()
        db.execute(
            delete(FeaturedRepository).where(
                FeaturedRepository.collection_id == collection.id
            )
        )
        for rank, candidate in enumerate(shortlist, start=1):
            db.add(
                FeaturedRepository(
                    collection_id=collection.id,
                    repository_id=candidate.repository.id,
                    rank=rank,
                    reason=build_featured_reason(candidate, target),
                    beginner_score=candidate.score.beginner_friendliness,
                    learning_value_score=candidate.score.learning_value,
                )
            )
        collections.append(collection)

    db.commit()
    for collection in collections:
        db.refresh(collection)
    return collections


def load_latest_trending_candidates(db: Session) -> list[CurationCandidate]:
    latest_run = db.scalar(
        select(TrendingRun)
        .where(TrendingRun.source == "github_trending", TrendingRun.status == "success")
        .order_by(desc(TrendingRun.finished_at), desc(TrendingRun.id))
        .limit(1)
    )
    if latest_run is None:
        return []

    rows = db.execute(
        select(RepositorySnapshot, Repository)
        .join(Repository, Repository.id == RepositorySnapshot.repository_id)
        .where(RepositorySnapshot.trending_run_id == latest_run.id)
        .order_by(RepositorySnapshot.rank.asc())
    ).all()
    return [
        CurationCandidate(
            repository=repository,
            snapshot=snapshot,
            score=score_repository(repository, stars_gained=snapshot.stars_gained),
        )
        for snapshot, repository in rows
    ]


def select_shortlist(
    candidates: list[CurationCandidate],
    target: CollectionTarget,
    limit: int,
) -> list[CurationCandidate]:
    filtered = [
        candidate
        for candidate in candidates
        if candidate.score.ai_relevance >= target.minimum_ai_relevance
    ]
    if target.required_keywords:
        filtered = [
            candidate
            for candidate in filtered
            if count_keyword_hits(searchable_text(candidate.repository), set(target.required_keywords))
        ]
    if target.prefer_developer_tools:
        filtered = sorted(
            filtered,
            key=lambda candidate: (
                developer_tool_score(candidate.repository),
                candidate.score.total,
                candidate.snapshot.stars_gained,
            ),
            reverse=True,
        )
    else:
        filtered = sorted(
            filtered,
            key=lambda candidate: (
                candidate.score.total,
                candidate.snapshot.stars_gained,
                candidate.repository.stars,
            ),
            reverse=True,
        )
    return filtered[:limit]


def upsert_collection(db: Session, target: CollectionTarget) -> FeaturedCollection:
    collection = db.scalar(
        select(FeaturedCollection).where(FeaturedCollection.slug == target.slug)
    )
    if collection is None:
        collection = FeaturedCollection(slug=target.slug)
        db.add(collection)

    collection.title = target.title
    collection.description = target.description
    collection.curation_prompt = target.prompt
    collection.model_name = configured_model_name()
    return collection


def build_featured_reason(candidate: CurationCandidate, target: CollectionTarget) -> str:
    config = load_model_reason_config()
    if config is None:
        return build_template_reason(candidate, target)

    try:
        model_reason = request_model_reason(candidate, target, config)
    except Exception:
        return build_template_reason(candidate, target)

    return model_reason or build_template_reason(candidate, target)


def configured_model_name() -> str:
    config = load_model_reason_config()
    if config is None:
        return "local-template"
    return config.model


def load_model_reason_config() -> ModelReasonConfig | None:
    base_url = os.environ.get(OPENAI_BASE_URL_ENV, "").strip()
    api_key = os.environ.get(OPENAI_API_KEY_ENV, "").strip()
    model = os.environ.get(OPENAI_MODEL_ENV, "").strip()
    if not base_url or not api_key or not model:
        return None
    return ModelReasonConfig(base_url=base_url.rstrip("/"), api_key=api_key, model=model)


def request_model_reason(
    candidate: CurationCandidate,
    target: CollectionTarget,
    config: ModelReasonConfig,
) -> str:
    repository = candidate.repository
    payload = {
        "model": config.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是 Repo Scout 的开源项目策展助手。"
                    "请用中文写一句具体、克制的精选理由，不要营销化。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"集合目标：{target.prompt}\n"
                    f"仓库：{repository.full_name}\n"
                    f"描述：{repository.description or '无'}\n"
                    f"语言：{repository.primary_language or '未知'}\n"
                    f"Stars：{repository.stars}\n"
                    f"Forks：{repository.forks}\n"
                    f"评分：AI 相关 {candidate.score.ai_relevance}/5，"
                    f"入门友好 {candidate.score.beginner_friendliness}/5，"
                    f"学习价值 {candidate.score.learning_value}/5。"
                ),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 120,
    }
    http_request = request.Request(
        f"{config.base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(http_request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result["choices"][0]["message"]["content"]
    return str(content).strip()


def build_template_reason(candidate: CurationCandidate, target: CollectionTarget) -> str:
    repository = candidate.repository
    if target.prefer_developer_tools:
        return (
            f"{repository.name} 是近期热度较高的开发工具项目，"
            f"适合观察工具型开源项目的设计取舍。"
        )
    if target.slug == "ai-agent-projects":
        return (
            f"{repository.name} 命中 Agent、检索或工具调用方向信号，"
            f"适合观察 AI Agent 项目的工程组织方式。"
        )
    if target.slug == "llm-tools":
        return (
            f"{repository.name} 与 LLM、模型调用或 RAG 工具链相关，"
            f"适合拆解大模型应用基础设施。"
        )
    return (
        f"{repository.name} 与 AI/LLM 方向相关，描述清晰，"
        f"适合作为入门学习和拆解实践的候选项目。"
    )


def searchable_text(repository: Repository) -> str:
    topics = []
    if repository.topics_json:
        try:
            value = json.loads(repository.topics_json)
            if isinstance(value, list):
                topics = [str(item) for item in value]
        except json.JSONDecodeError:
            topics = []
    return " ".join(
        [
            repository.full_name,
            repository.description or "",
            repository.primary_language or "",
            " ".join(topics),
        ]
    ).lower()


def count_keyword_hits(text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def developer_tool_score(repository: Repository) -> int:
    return count_keyword_hits(searchable_text(repository), DEVELOPER_TOOL_KEYWORDS)


def score_activity(stars: int, forks: int) -> int:
    if stars >= 50_000 or forks >= 5_000:
        return 5
    if stars >= 10_000 or forks >= 1_000:
        return 4
    if stars >= 3_000 or forks >= 300:
        return 3
    if stars >= 500 or forks >= 50:
        return 2
    return 1


def score_growth(stars_gained: int) -> int:
    if stars_gained >= 500:
        return 5
    if stars_gained >= 200:
        return 4
    if stars_gained >= 80:
        return 3
    if stars_gained >= 20:
        return 2
    return 1


def clamp_score(value: int) -> int:
    return max(1, min(5, value))


def main() -> None:
    parser = argparse.ArgumentParser(description="Curate featured repositories.")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        collections = curate_featured_collections(db, limit=args.limit)
        print(f"Curated {len(collections)} featured collections.")


if __name__ == "__main__":
    main()
