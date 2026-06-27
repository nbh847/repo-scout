from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Repository(Base):
    __tablename__ = "repositories"
    __table_args__ = (
        UniqueConstraint("owner", "name", name="uq_repositories_owner_name"),
        Index("ix_repositories_full_name", "full_name"),
        Index("ix_repositories_primary_language", "primary_language"),
        Index("ix_repositories_stars", "stars"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(160))
    full_name: Mapped[str] = mapped_column(String(300), unique=True)
    url: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    summary_zh: Mapped[str | None] = mapped_column(Text)
    description_zh: Mapped[str | None] = mapped_column(Text)
    primary_language: Mapped[str | None] = mapped_column(String(80))
    topics_json: Mapped[str | None] = mapped_column(Text)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )

    snapshots: Mapped[list["RepositorySnapshot"]] = relationship(back_populates="repository")
    featured_items: Mapped[list["FeaturedRepository"]] = relationship(back_populates="repository")


class TrendingRun(Base):
    __tablename__ = "trending_runs"
    __table_args__ = (
        Index("ix_trending_runs_source_period_language", "source", "period", "language"),
        Index("ix_trending_runs_started_at", "started_at"),
        Index("ix_trending_runs_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(80), default="github_trending")
    period: Mapped[str] = mapped_column(String(20))
    language: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)

    snapshots: Mapped[list["RepositorySnapshot"]] = relationship(back_populates="trending_run")


class RepositorySnapshot(Base):
    __tablename__ = "repository_snapshots"
    __table_args__ = (
        UniqueConstraint("trending_run_id", "repository_id", name="uq_snapshots_run_repository"),
        Index("ix_snapshots_run_rank", "trending_run_id", "rank"),
        Index("ix_snapshots_repository_captured", "repository_id", "captured_at"),
        Index("ix_snapshots_stars_gained", "stars_gained"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    trending_run_id: Mapped[int] = mapped_column(ForeignKey("trending_runs.id"))
    rank: Mapped[int] = mapped_column(Integer)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    stars_gained: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    primary_language: Mapped[str | None] = mapped_column(String(80))
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    repository: Mapped[Repository] = relationship(back_populates="snapshots")
    trending_run: Mapped[TrendingRun] = relationship(back_populates="snapshots")


class FeaturedCollection(Base):
    __tablename__ = "featured_collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    curation_prompt: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )

    repositories: Mapped[list["FeaturedRepository"]] = relationship(back_populates="collection")


class FeaturedRepository(Base):
    __tablename__ = "featured_repositories"
    __table_args__ = (
        UniqueConstraint("collection_id", "repository_id", name="uq_featured_collection_repository"),
        Index("ix_featured_collection_rank", "collection_id", "rank"),
        Index("ix_featured_repository", "repository_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("featured_collections.id"))
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id"))
    rank: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    beginner_score: Mapped[int] = mapped_column(Integer)
    learning_value_score: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    collection: Mapped[FeaturedCollection] = relationship(back_populates="repositories")
    repository: Mapped[Repository] = relationship(back_populates="featured_items")
