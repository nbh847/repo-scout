import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
import re
import ssl
from urllib.parse import quote
from urllib.request import Request, urlopen

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


class GitHubTrendingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.repositories: list[TrendingRepository] = []
        self._article: dict[str, str | None] | None = None
        self._in_heading = False
        self._capture: str | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        class_name = attributes.get("class", "")

        if tag == "article" and "Box-row" in class_name:
            self._article = {
                "repo_text": None,
                "repo_href": None,
                "description": None,
                "language": None,
                "stars": None,
                "forks": None,
                "stars_gained": None,
            }
            return

        if self._article is None:
            return

        if tag == "h2":
            self._in_heading = True
            return

        if tag == "a":
            href = attributes.get("href", "")
            if self._in_heading and _is_repository_href(href):
                self._article["repo_href"] = href
                self._start_capture("repo_text")
            elif href.endswith("/stargazers"):
                self._start_capture("stars")
            elif href.endswith("/forks"):
                self._start_capture("forks")
            return

        if tag == "p" and "col-9" in class_name:
            self._start_capture("description")
            return

        if tag == "span" and attributes.get("itemprop") == "programmingLanguage":
            self._start_capture("language")
            return

        if tag == "span" and "float-sm-right" in class_name:
            self._start_capture("stars_gained")

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture and tag in {"a", "p", "span"}:
            self._finish_capture()

        if tag == "h2":
            self._in_heading = False
            return

        if tag == "article" and self._article is not None:
            repository = self._build_repository()
            if repository is not None:
                self.repositories.append(repository)
            self._article = None

    def _start_capture(self, field: str) -> None:
        self._capture = field
        self._parts = []

    def _finish_capture(self) -> None:
        if self._article is not None and self._capture:
            text = " ".join(" ".join(self._parts).split())
            self._article[self._capture] = text or None
        self._capture = None
        self._parts = []

    def _build_repository(self) -> TrendingRepository | None:
        assert self._article is not None

        href = self._article["repo_href"]
        if not href:
            return None

        path_parts = href.strip("/").split("/")
        if len(path_parts) != 2:
            return None

        owner, name = path_parts
        return TrendingRepository(
            rank=len(self.repositories) + 1,
            owner=owner,
            name=name,
            url=f"https://github.com/{owner}/{name}",
            description=self._article["description"],
            primary_language=self._article["language"],
            stars=parse_count(self._article["stars"] or ""),
            forks=parse_count(self._article["forks"] or ""),
            stars_gained=parse_stars_gained(self._article["stars_gained"] or ""),
        )


def _is_repository_href(href: str) -> bool:
    return bool(re.fullmatch(r"/[^/\s]+/[^/\s]+", href))


def parse_trending_html(html: str) -> list[TrendingRepository]:
    parser = GitHubTrendingParser()
    parser.feed(html)
    return parser.repositories


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
