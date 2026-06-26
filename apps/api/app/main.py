from datetime import UTC, datetime
import json
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine, get_db
from .curation import curate_featured_collections
from .github_trending import VALID_PERIODS, ingest_github_trending
from .models import FeaturedCollection, FeaturedRepository, Repository, RepositorySnapshot, TrendingRun
from .scheduler import TrendingIngestionScheduler, trending_ingestion_lock
from .schemas import (
    FeaturedCollectionOut,
    HealthOut,
    RepositoryDetailOut,
    RepositoryOut,
    TrendingRepositoryOut,
    TrendingRunOut,
)
from .seed import seed_database


app = FastAPI(title="Repo Scout API", version="0.1.0")
trending_scheduler: TrendingIngestionScheduler | None = None


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    start_trending_scheduler_from_env()


@app.on_event("shutdown")
def shutdown() -> None:
    if trending_scheduler:
        trending_scheduler.stop()


def start_trending_scheduler_from_env() -> None:
    global trending_scheduler
    if os.getenv("REPO_SCOUT_TRENDING_SCHEDULER_ENABLED") != "1":
        return

    trending_scheduler = TrendingIngestionScheduler(
        interval_seconds=int(os.getenv("REPO_SCOUT_TRENDING_INTERVAL_SECONDS", str(24 * 60 * 60))),
        period=os.getenv("REPO_SCOUT_TRENDING_PERIOD", "daily"),
        language=os.getenv("REPO_SCOUT_TRENDING_LANGUAGE") or None,
        limit=int(os.getenv("REPO_SCOUT_TRENDING_LIMIT", "20")),
    )
    trending_scheduler.start()


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


def trending_run_out(run: TrendingRun) -> TrendingRunOut:
    return TrendingRunOut(
        id=run.id,
        source=run.source,
        period=run.period,
        language=run.language,
        status=run.status,
        started_at=run.started_at,
        finished_at=run.finished_at,
        error_message=run.error_message,
    )


def is_local_request(request: Request | None) -> bool:
    if request is None or request.client is None:
        return True
    return request.client.host in {"127.0.0.1", "::1", "localhost"}


def authorize_admin_request(
    request: Request | None,
    admin_token: str | None,
    authorization: str | None,
) -> None:
    if is_local_request(request):
        return

    expected_token = os.getenv("REPO_SCOUT_ADMIN_TOKEN")
    bearer_token = None
    if isinstance(authorization, str) and authorization.lower().startswith("bearer "):
        bearer_token = authorization[7:].strip()

    submitted_admin_token = admin_token if isinstance(admin_token, str) else None
    if expected_token and expected_token in {submitted_admin_token, bearer_token}:
        return

    raise HTTPException(status_code=403, detail="Admin token required")


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(status="ok", checked_at=datetime.now(UTC))


@app.post("/api/admin/ingest/trending", response_model=TrendingRunOut)
def trigger_github_trending_ingest(
    request: Request,
    period: str = Query(default="daily"),
    language: str | None = Query(default=None, max_length=80),
    limit: int | None = Query(default=20, ge=1, le=100),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> TrendingRunOut:
    authorize_admin_request(request, admin_token, authorization)
    if period not in VALID_PERIODS:
        raise HTTPException(status_code=422, detail=f"Unsupported GitHub Trending period: {period}")

    if not trending_ingestion_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="GitHub Trending ingestion is already running")

    try:
        run = ingest_github_trending(db, period=period, language=language, limit=limit)
        return trending_run_out(run)
    finally:
        trending_ingestion_lock.release()


@app.get("/api/repositories/trending", response_model=list[TrendingRepositoryOut])
def trending_repositories(
    limit: int = Query(default=20, ge=1, le=100),
    period: str | None = None,
    language: str | None = None,
    db: Session = Depends(get_db),
) -> list[TrendingRepositoryOut]:
    if period is not None and period not in VALID_PERIODS:
        raise HTTPException(status_code=422, detail=f"Unsupported GitHub Trending period: {period}")

    run_query = select(TrendingRun).where(
        TrendingRun.source == "github_trending",
        TrendingRun.status == "success",
    )
    if period is not None:
        run_query = run_query.where(TrendingRun.period == period)
    if language and language.strip():
        run_query = run_query.where(func.lower(TrendingRun.language) == language.strip().lower())

    latest_run = db.scalar(
        run_query
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
    language: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RepositoryOut]:
    query = select(Repository)
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.where(
            or_(
                Repository.full_name.like(term),
                Repository.description.like(term),
                Repository.primary_language.like(term),
                Repository.topics_json.like(term),
            )
        )
    if language and language.strip():
        query = query.where(func.lower(Repository.primary_language) == language.strip().lower())
    query = query.order_by(desc(Repository.stars)).limit(limit)
    return [repository_out(repository) for repository in db.scalars(query)]


@app.get("/api/repositories/languages", response_model=list[str])
def repository_languages(db: Session = Depends(get_db)) -> list[str]:
    rows = db.execute(
        select(Repository.primary_language, func.count(Repository.id))
        .where(Repository.primary_language.is_not(None), Repository.primary_language != "")
        .group_by(Repository.primary_language)
        .order_by(desc(func.count(Repository.id)), Repository.primary_language.asc())
    ).all()
    return [language for language, _count in rows]


@app.get("/api/repositories/{owner}/{name}", response_model=RepositoryDetailOut)
def get_repository(owner: str, name: str, db: Session = Depends(get_db)) -> RepositoryDetailOut:
    repository = db.scalar(
        select(Repository).where(Repository.owner == owner, Repository.name == name)
    )
    if repository is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    featured_row = db.execute(
        select(FeaturedRepository, FeaturedCollection)
        .join(FeaturedCollection, FeaturedCollection.id == FeaturedRepository.collection_id)
        .where(FeaturedRepository.repository_id == repository.id)
        .order_by(FeaturedRepository.rank.asc(), FeaturedRepository.id.asc())
        .limit(1)
    ).first()
    featured_data = {}
    if featured_row is not None:
        featured, collection = featured_row
        featured_data = {
            "featured_reason": featured.reason,
            "featured_collection_slug": collection.slug,
            "featured_collection_title": collection.title,
            "beginner_score": featured.beginner_score,
            "learning_value_score": featured.learning_value_score,
        }
    snapshots = db.scalars(
        select(RepositorySnapshot)
        .join(TrendingRun, TrendingRun.id == RepositorySnapshot.trending_run_id)
        .where(RepositorySnapshot.repository_id == repository.id)
        .order_by(desc(TrendingRun.finished_at), desc(TrendingRun.id), desc(RepositorySnapshot.id))
        .limit(2)
    ).all()
    trend_delta_stars = None
    if len(snapshots) >= 2:
        trend_delta_stars = snapshots[0].stars - snapshots[1].stars

    return RepositoryDetailOut(
        **repository_out(repository).model_dump(),
        **featured_data,
        trend_delta_stars=trend_delta_stars,
        trend_snapshot_count=len(snapshots),
    )


@app.get("/api/featured", response_model=list[FeaturedCollectionOut])
def featured_collections(db: Session = Depends(get_db)) -> list[FeaturedCollectionOut]:
    collections = db.scalars(select(FeaturedCollection).order_by(FeaturedCollection.created_at)).all()
    return [featured_collection_out(collection, db) for collection in collections]


def featured_collection_out(collection: FeaturedCollection, db: Session) -> FeaturedCollectionOut:
    rows = db.execute(
        select(FeaturedRepository, Repository)
        .join(Repository, Repository.id == FeaturedRepository.repository_id)
        .where(FeaturedRepository.collection_id == collection.id)
        .order_by(FeaturedRepository.rank.asc())
    ).all()
    return FeaturedCollectionOut(
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


@app.get("/api/featured/{slug}", response_model=FeaturedCollectionOut)
def featured_collection(slug: str, db: Session = Depends(get_db)) -> FeaturedCollectionOut:
    collection = db.scalar(select(FeaturedCollection).where(FeaturedCollection.slug == slug))
    if collection is None:
        raise HTTPException(status_code=404, detail="Featured collection not found")
    return featured_collection_out(collection, db)


@app.post("/api/admin/curate", response_model=list[FeaturedCollectionOut])
def trigger_featured_curation(
    request: Request,
    limit: int = Query(default=5, ge=1, le=20),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> list[FeaturedCollectionOut]:
    authorize_admin_request(request, admin_token, authorization)
    curate_featured_collections(db, limit=limit)
    return featured_collections(db=db)
