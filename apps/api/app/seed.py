from datetime import UTC, datetime
import json

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import (
    FeaturedCollection,
    FeaturedRepository,
    Repository,
    RepositorySnapshot,
    TrendingRun,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


SAMPLE_REPOSITORIES = [
    {
        "owner": "langchain-ai",
        "name": "langchain",
        "description": "Build context-aware reasoning applications.",
        "primary_language": "Python",
        "topics": ["llm", "agents", "rag"],
        "stars": 104000,
        "forks": 16000,
        "stars_gained": 640,
    },
    {
        "owner": "open-webui",
        "name": "open-webui",
        "description": "User-friendly AI interface for local and hosted models.",
        "primary_language": "TypeScript",
        "topics": ["llm", "chat", "self-hosted"],
        "stars": 82000,
        "forks": 9800,
        "stars_gained": 580,
    },
    {
        "owner": "ollama",
        "name": "ollama",
        "description": "Run large language models locally.",
        "primary_language": "Go",
        "topics": ["local-llm", "models", "developer-tools"],
        "stars": 145000,
        "forks": 12000,
        "stars_gained": 520,
    },
]


def seed_database(db: Session) -> None:
    if db.query(Repository).first():
        return

    run = TrendingRun(
        source="github_trending",
        period="daily",
        language=None,
        status="success",
        started_at=utc_now(),
        finished_at=utc_now(),
    )
    db.add(run)
    db.flush()

    repositories: list[Repository] = []
    for rank, item in enumerate(SAMPLE_REPOSITORIES, start=1):
        full_name = f"{item['owner']}/{item['name']}"
        repository = Repository(
            owner=item["owner"],
            name=item["name"],
            full_name=full_name,
            url=f"https://github.com/{full_name}",
            description=item["description"],
            primary_language=item["primary_language"],
            topics_json=json.dumps(item["topics"]),
            stars=item["stars"],
            forks=item["forks"],
        )
        db.add(repository)
        db.flush()
        repositories.append(repository)
        db.add(
            RepositorySnapshot(
                repository_id=repository.id,
                trending_run_id=run.id,
                rank=rank,
                stars=item["stars"],
                forks=item["forks"],
                stars_gained=item["stars_gained"],
                description=item["description"],
                primary_language=item["primary_language"],
            )
        )

    collection = FeaturedCollection(
        slug="beginner-friendly-ai",
        title="适合初学者的 AI 项目",
        description="从热门项目中挑选出更容易上手、学习价值明确的项目。",
        curation_prompt="Select beginner-friendly AI repositories with clear docs and learning value.",
        model_name="manual-seed",
    )
    db.add(collection)
    db.flush()

    reasons = [
        "生态成熟，适合学习 RAG、Agent 和 LLM 应用的基础概念。",
        "界面完整，适合理解 AI 产品如何组织模型、会话和设置。",
        "本地运行路径清晰，适合入门了解模型部署和开发者工具。",
    ]
    for rank, repository in enumerate(repositories, start=1):
        db.add(
            FeaturedRepository(
                collection_id=collection.id,
                repository_id=repository.id,
                rank=rank,
                reason=reasons[rank - 1],
                beginner_score=4,
                learning_value_score=5,
            )
        )

    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    main()
