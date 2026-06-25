from datetime import UTC, datetime
import json

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .models import FeaturedCollection, FeaturedRepository, Repository, RepositorySnapshot
from .schemas import FeaturedCollectionOut, HealthOut, RepositoryOut, TrendingRepositoryOut
from .seed import seed_database


app = FastAPI(title="Repo Scout API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)


def parse_topics(topics_json: str | None) -> list[str]:
    if not topics_json:
        return []
    try:
        value = json.loads(topics_json)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def repository_out(repository: Repository) -> RepositoryOut:
    return RepositoryOut(
        owner=repository.owner,
        name=repository.name,
        full_name=repository.full_name,
        url=repository.url,
        description=repository.description,
        primary_language=repository.primary_language,
        topics=parse_topics(repository.topics_json),
        stars=repository.stars,
        forks=repository.forks,
    )


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", checked_at=datetime.now(UTC))


@app.get("/api/repositories/trending", response_model=list[TrendingRepositoryOut])
def trending_repositories(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[TrendingRepositoryOut]:
    rows = db.execute(
        select(RepositorySnapshot, Repository)
        .join(Repository, Repository.id == RepositorySnapshot.repository_id)
        .order_by(RepositorySnapshot.rank.asc())
        .limit(limit)
    ).all()

    return [
        TrendingRepositoryOut(
            **repository_out(repository).model_dump(),
            rank=snapshot.rank,
            stars_gained=snapshot.stars_gained,
        )
        for snapshot, repository in rows
    ]


@app.get("/api/repositories/search", response_model=list[RepositoryOut])
def search_repositories(
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RepositoryOut]:
    query = select(Repository).order_by(desc(Repository.stars)).limit(limit)
    if q.strip():
        term = f"%{q.strip()}%"
        query = (
            select(Repository)
            .where(
                or_(
                    Repository.full_name.like(term),
                    Repository.description.like(term),
                    Repository.primary_language.like(term),
                    Repository.topics_json.like(term),
                )
            )
            .order_by(desc(Repository.stars))
            .limit(limit)
        )
    return [repository_out(repository) for repository in db.scalars(query)]


@app.get("/api/repositories/{owner}/{name}", response_model=RepositoryOut)
def get_repository(owner: str, name: str, db: Session = Depends(get_db)) -> RepositoryOut:
    repository = db.scalar(
        select(Repository).where(Repository.owner == owner, Repository.name == name)
    )
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repository_out(repository)


@app.get("/api/featured", response_model=list[FeaturedCollectionOut])
def featured_collections(db: Session = Depends(get_db)) -> list[FeaturedCollectionOut]:
    collections = db.scalars(select(FeaturedCollection).order_by(FeaturedCollection.created_at)).all()
    result: list[FeaturedCollectionOut] = []

    for collection in collections:
        rows = db.execute(
            select(FeaturedRepository, Repository)
            .join(Repository, Repository.id == FeaturedRepository.repository_id)
            .where(FeaturedRepository.collection_id == collection.id)
            .order_by(FeaturedRepository.rank.asc())
        ).all()
        result.append(
            FeaturedCollectionOut(
                slug=collection.slug,
                title=collection.title,
                description=collection.description,
                repositories=[
                    {
                        **repository_out(repository).model_dump(),
                        "rank": featured.rank,
                        "reason": featured.reason,
                        "beginner_score": featured.beginner_score,
                        "learning_value_score": featured.learning_value_score,
                    }
                    for featured, repository in rows
                ],
            )
        )

    return result
