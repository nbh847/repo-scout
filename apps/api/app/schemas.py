from datetime import datetime

from pydantic import BaseModel


class RepositoryOut(BaseModel):
    owner: str
    name: str
    full_name: str
    url: str
    description: str | None
    primary_language: str | None
    topics: list[str]
    stars: int
    forks: int


class TrendingRepositoryOut(RepositoryOut):
    rank: int
    stars_gained: int


class RepositoryDetailOut(RepositoryOut):
    featured_reason: str | None = None
    beginner_score: int | None = None
    learning_value_score: int | None = None
    trend_delta_stars: int | None = None
    trend_snapshot_count: int = 0


class FeaturedRepositoryOut(RepositoryOut):
    rank: int
    reason: str
    beginner_score: int
    learning_value_score: int


class FeaturedCollectionOut(BaseModel):
    slug: str
    title: str
    description: str | None
    repositories: list[FeaturedRepositoryOut]


class HealthOut(BaseModel):
    status: str
    checked_at: datetime


class TrendingRunOut(BaseModel):
    id: int
    source: str
    period: str
    language: str | None
    status: str
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
