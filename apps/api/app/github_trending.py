import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import re
import ssl
from urllib.parse import quote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Repository, RepositorySnapshot, TrendingRun


GITHUB_TRENDING_BASE_URL = "https://github.com/trending"
VALID_PERIODS = {"daily", "weekly", "monthly"}


@dataclass(frozen=True)
class TrendingRepository:
    rank: int
    owner: str
    name: str
    url: str
    description: str | None
    primary_language: str | None
    stars: int
    forks: int
    stars_gained: int


def build_trending_url(period: str = "daily", language: str | None = None) -> str:
    if period not in VALID_PERIODS:
        raise ValueError(f"Unsupported GitHub Trending period: {period}")

    path = GITHUB_TRENDING_BASE_URL
    if language and language.strip():
        path = f"{path}/{quote(language.strip())}"
    return f"{path}?since={period}"


def parse_count(value: str) -> int:
    normalized = value.strip().lower().replace(",", "")
    if not normalized:
        return 0

    match = re.search(r"(\d+(?:\.\d+)?)([km])?", normalized)
    if not match:
        return 0

    number = float(match.group(1))
    suffix = match.group(2)
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    return int(number)


def parse_stars_gained(value: str) -> int:
    if "star" not in value.lower():
        return 0
    return parse_count(value)


def _is_repository_href(href: str) -> bool:
    return bool(re.fullmatch(r"/[^/\s]+/[^/\s]+", href))


def _element_text(element: object | None) -> str | None:
    if element is None:
        return None

    text_getter = getattr(element, "get_text")
    text = " ".join(text_getter(" ", strip=True).split())
    return text or None


def parse_trending_html(html: str) -> list[TrendingRepository]:
    soup = BeautifulSoup(html, "html.parser")
    repositories: list[TrendingRepository] = []

    for article in soup.select("article.Box-row"):
        link = article.select_one("h2 a[href]")
        href = link.get("href", "") if link else ""
        if not isinstance(href, str) or not _is_repository_href(href):
            continue

        owner, name = href.strip("/").split("/")
        description = _element_text(article.select_one("p.col-9"))
        language = _element_text(article.select_one('span[itemprop="programmingLanguage"]'))
        stars = _element_text(article.select_one('a[href$="/stargazers"]'))
        forks = _element_text(article.select_one('a[href$="/forks"]'))
        stars_gained = _element_text(article.select_one("span.float-sm-right"))

        repositories.append(
            TrendingRepository(
                rank=len(repositories) + 1,
                owner=owner,
                name=name,
                url=f"https://github.com/{owner}/{name}",
                description=description,
                primary_language=language,
                stars=parse_count(stars or ""),
                forks=parse_count(forks or ""),
                stars_gained=parse_stars_gained(stars_gained or ""),
            )
        )

    return repositories


def fetch_trending_html(period: str = "daily", language: str | None = None) -> str:
    request = Request(
        build_trending_url(period=period, language=language),
        headers={
            "Accept": "text/html",
            "User-Agent": "RepoScout/0.1 (+https://github.com)",
        },
    )
    context = ssl.create_default_context(cafile=resolve_ca_file())
    with urlopen(request, timeout=30, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def resolve_ca_file() -> str | None:
    if ssl.get_default_verify_paths().cafile:
        return None

    system_ca_file = Path("/etc/ssl/cert.pem")
    if system_ca_file.is_file():
        return str(system_ca_file)
    return None


def ingest_trending_repositories(
    db: Session,
    repositories: list[TrendingRepository],
    period: str = "daily",
    language: str | None = None,
) -> TrendingRun:
    if period not in VALID_PERIODS:
        raise ValueError(f"Unsupported GitHub Trending period: {period}")

    now = utc_now()
    run = TrendingRun(
        source="github_trending",
        period=period,
        language=language,
        status="pending",
        started_at=now,
    )
    db.add(run)
    db.flush()

    try:
        for item in repositories:
            full_name = f"{item.owner}/{item.name}"
            repository = db.scalar(
                select(Repository).where(Repository.full_name == full_name)
            )
            if repository is None:
                repository = Repository(
                    owner=item.owner,
                    name=item.name,
                    full_name=full_name,
                    url=item.url,
                    description=item.description,
                    primary_language=item.primary_language,
                    topics_json=None,
                    stars=item.stars,
                    forks=item.forks,
                )
                db.add(repository)
                db.flush()
            else:
                repository.url = item.url
                repository.description = item.description
                repository.primary_language = item.primary_language
                repository.stars = item.stars
                repository.forks = item.forks

            db.add(
                RepositorySnapshot(
                    repository_id=repository.id,
                    trending_run_id=run.id,
                    rank=item.rank,
                    stars=item.stars,
                    forks=item.forks,
                    stars_gained=item.stars_gained,
                    description=item.description,
                    primary_language=item.primary_language,
                )
            )

        run.status = "success"
        run.finished_at = utc_now()
        db.commit()
        db.refresh(run)
        return run
    except Exception as error:
        run.status = "failed"
        run.finished_at = utc_now()
        run.error_message = str(error)
        db.commit()
        raise


def ingest_github_trending(
    db: Session,
    period: str = "daily",
    language: str | None = None,
    limit: int | None = None,
) -> TrendingRun:
    html = fetch_trending_html(period=period, language=language)
    repositories = parse_trending_html(html)
    if limit is not None:
        repositories = repositories[:limit]
    return ingest_trending_repositories(
        db,
        repositories,
        period=period,
        language=language,
    )


def utc_now() -> datetime:
    return datetime.now(UTC)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest GitHub Trending repositories.")
    parser.add_argument("--period", choices=sorted(VALID_PERIODS), default="daily")
    parser.add_argument("--language", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        run = ingest_github_trending(
            db,
            period=args.period,
            language=args.language,
            limit=args.limit,
        )
        print(f"Ingested GitHub Trending run {run.id} with status {run.status}.")


if __name__ == "__main__":
    main()
