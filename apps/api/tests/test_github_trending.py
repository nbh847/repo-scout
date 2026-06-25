import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base
from app.github_trending import (
    TrendingRepository,
    build_trending_url,
    ingest_trending_repositories,
    parse_count,
    parse_stars_gained,
    parse_trending_html,
    resolve_ca_file,
)
from app.main import trigger_github_trending_ingest, trending_repositories
from app.models import Repository, RepositorySnapshot, TrendingRun
from app.scheduler import TrendingIngestionScheduler, trending_ingestion_lock


TRENDING_HTML = """
<main>
  <article class="Box-row">
    <h2 class="h3 lh-condensed">
      <a href="/owner-one/project-one">
        owner-one / project-one
      </a>
    </h2>
    <p class="col-9 color-fg-muted my-1 pr-4">
      First test repository.
    </p>
    <span itemprop="programmingLanguage">Python</span>
    <a href="/owner-one/project-one/stargazers">1,234</a>
    <a href="/owner-one/project-one/forks">56</a>
    <span class="d-inline-block float-sm-right">
      78 stars today
    </span>
  </article>
  <article class="Box-row">
    <h2 class="h3 lh-condensed">
      <a href="/owner-two/project-two">
        owner-two / project-two
      </a>
    </h2>
    <p class="col-9 color-fg-muted my-1 pr-4"></p>
    <a href="/owner-two/project-two/stargazers">2.5k</a>
    <a href="/owner-two/project-two/forks">1.1k</a>
    <span class="d-inline-block float-sm-right">
      120 stars this week
    </span>
  </article>
</main>
"""


class GitHubTrendingParserTest(unittest.TestCase):
    def test_build_trending_url_uses_period_and_optional_language(self) -> None:
        self.assertEqual(
            build_trending_url(period="weekly", language="python"),
            "https://github.com/trending/python?since=weekly",
        )
        self.assertEqual(
            build_trending_url(period="daily", language=None),
            "https://github.com/trending?since=daily",
        )

    def test_parse_count_normalizes_commas_and_suffixes(self) -> None:
        self.assertEqual(parse_count("1,234"), 1234)
        self.assertEqual(parse_count("2.5k"), 2500)
        self.assertEqual(parse_count(""), 0)

    def test_parse_stars_gained_reads_first_number(self) -> None:
        self.assertEqual(parse_stars_gained("78 stars today"), 78)
        self.assertEqual(parse_stars_gained("1,234 stars this month"), 1234)
        self.assertEqual(parse_stars_gained("Built by 4 contributors"), 0)

    def test_parse_trending_html_extracts_repository_cards(self) -> None:
        repositories = parse_trending_html(TRENDING_HTML)

        self.assertEqual(len(repositories), 2)
        self.assertEqual(repositories[0].rank, 1)
        self.assertEqual(repositories[0].owner, "owner-one")
        self.assertEqual(repositories[0].name, "project-one")
        self.assertEqual(repositories[0].url, "https://github.com/owner-one/project-one")
        self.assertEqual(repositories[0].description, "First test repository.")
        self.assertEqual(repositories[0].primary_language, "Python")
        self.assertEqual(repositories[0].stars, 1234)
        self.assertEqual(repositories[0].forks, 56)
        self.assertEqual(repositories[0].stars_gained, 78)
        self.assertIsNone(repositories[1].description)
        self.assertIsNone(repositories[1].primary_language)
        self.assertEqual(repositories[1].stars, 2500)
        self.assertEqual(repositories[1].forks, 1100)

    def test_parse_trending_html_uses_beautifulsoup(self) -> None:
        with patch("app.github_trending.BeautifulSoup", wraps=BeautifulSoup) as parser:
            parse_trending_html(TRENDING_HTML)

        parser.assert_called_once_with(TRENDING_HTML, "html.parser")


class GitHubTrendingIngestionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def test_ingest_trending_repositories_creates_run_repositories_and_snapshots(self) -> None:
        items = [
            TrendingRepository(
                rank=1,
                owner="owner-one",
                name="project-one",
                url="https://github.com/owner-one/project-one",
                description="First test repository.",
                primary_language="Python",
                stars=1234,
                forks=56,
                stars_gained=78,
            ),
            TrendingRepository(
                rank=2,
                owner="owner-two",
                name="project-two",
                url="https://github.com/owner-two/project-two",
                description=None,
                primary_language=None,
                stars=2500,
                forks=1100,
                stars_gained=120,
            ),
        ]

        with Session(self.engine) as db:
            run = ingest_trending_repositories(
                db,
                items,
                period="weekly",
                language="python",
            )

            repositories = db.scalars(select(Repository).order_by(Repository.full_name)).all()
            snapshots = db.scalars(
                select(RepositorySnapshot).order_by(RepositorySnapshot.rank)
            ).all()
            stored_run = db.get(TrendingRun, run.id)

        self.assertEqual(stored_run.status, "success")
        self.assertEqual(stored_run.period, "weekly")
        self.assertEqual(stored_run.language, "python")
        self.assertEqual(stored_run.error_message, None)
        self.assertIsNotNone(stored_run.finished_at)
        self.assertEqual([repository.full_name for repository in repositories], [
            "owner-one/project-one",
            "owner-two/project-two",
        ])
        self.assertEqual(repositories[0].description, "First test repository.")
        self.assertEqual(repositories[0].stars, 1234)
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(snapshots[0].rank, 1)
        self.assertEqual(snapshots[0].stars_gained, 78)
        self.assertEqual(snapshots[1].rank, 2)

    def test_ingest_trending_repositories_updates_existing_repository(self) -> None:
        with Session(self.engine) as db:
            db.add(
                Repository(
                    owner="owner-one",
                    name="project-one",
                    full_name="owner-one/project-one",
                    url="https://github.com/owner-one/project-one",
                    description="Old description.",
                    primary_language="Python",
                    stars=100,
                    forks=10,
                )
            )
            db.commit()

            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="owner-one",
                        name="project-one",
                        url="https://github.com/owner-one/project-one",
                        description="New description.",
                        primary_language="Python",
                        stars=150,
                        forks=12,
                        stars_gained=50,
                    )
                ],
                period="daily",
                language=None,
            )

            repository_count = len(db.scalars(select(Repository)).all())
            repository = db.scalar(
                select(Repository).where(Repository.full_name == "owner-one/project-one")
            )
            snapshot_count = len(db.scalars(select(RepositorySnapshot)).all())

        self.assertEqual(repository_count, 1)
        self.assertEqual(repository.description, "New description.")
        self.assertEqual(repository.stars, 150)
        self.assertEqual(repository.forks, 12)
        self.assertEqual(snapshot_count, 1)

    def test_trending_repositories_returns_latest_successful_run_only(self) -> None:
        with Session(self.engine) as db:
            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="old-owner",
                        name="old-project",
                        url="https://github.com/old-owner/old-project",
                        description="Old run repository.",
                        primary_language="Python",
                        stars=100,
                        forks=10,
                        stars_gained=5,
                    )
                ],
                period="daily",
                language=None,
            )
            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="new-owner",
                        name="new-project",
                        url="https://github.com/new-owner/new-project",
                        description="Newest run first repository.",
                        primary_language="TypeScript",
                        stars=200,
                        forks=20,
                        stars_gained=15,
                    ),
                    TrendingRepository(
                        rank=2,
                        owner="second-owner",
                        name="second-project",
                        url="https://github.com/second-owner/second-project",
                        description="Newest run second repository.",
                        primary_language="Go",
                        stars=150,
                        forks=15,
                        stars_gained=10,
                    ),
                ],
                period="daily",
                language=None,
            )

            repositories = trending_repositories(limit=10, db=db)

        self.assertEqual(
            [repository.full_name for repository in repositories],
            ["new-owner/new-project", "second-owner/second-project"],
        )
        self.assertEqual([repository.rank for repository in repositories], [1, 2])


class GitHubTrendingAdminEndpointTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)

    def test_trigger_github_trending_ingest_reuses_ingestion_service(self) -> None:
        with Session(self.engine) as db:
            expected_run = TrendingRun(
                id=42,
                source="github_trending",
                period="weekly",
                language="python",
                status="success",
            )
            with patch("app.main.ingest_github_trending", return_value=expected_run) as ingest:
                result = trigger_github_trending_ingest(
                    period="weekly",
                    language="python",
                    limit=5,
                    request=None,
                    admin_token=None,
                    db=db,
                )

        ingest.assert_called_once_with(db, period="weekly", language="python", limit=5)
        self.assertEqual(result.id, 42)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.period, "weekly")
        self.assertEqual(result.language, "python")

    def test_trigger_github_trending_ingest_rejects_non_local_request_without_token(self) -> None:
        request = SimpleNamespace(
            client=SimpleNamespace(host="203.0.113.10"),
            headers={},
        )

        with Session(self.engine) as db:
            with self.assertRaises(HTTPException) as error:
                trigger_github_trending_ingest(
                    request=request,
                    admin_token=None,
                    db=db,
                )

        self.assertEqual(error.exception.status_code, 403)

    def test_trigger_github_trending_ingest_rejects_concurrent_run(self) -> None:
        acquired = trending_ingestion_lock.acquire(blocking=False)
        self.assertTrue(acquired)
        try:
            with Session(self.engine) as db:
                with self.assertRaises(HTTPException) as error:
                    trigger_github_trending_ingest(
                        period="daily",
                        language=None,
                        limit=5,
                        request=None,
                        admin_token=None,
                        db=db,
                    )
        finally:
            trending_ingestion_lock.release()

        self.assertEqual(error.exception.status_code, 409)


class GitHubTrendingSchedulerTest(unittest.TestCase):
    def test_scheduler_skips_tick_when_previous_run_is_active(self) -> None:
        calls = 0
        scheduler = TrendingIngestionScheduler(
            session_factory=lambda: SimpleNamespace(close=lambda: None),
            ingest=lambda db, period, language, limit: None,
            interval_seconds=60,
        )
        scheduler._running = True

        def ingest(db: object, period: str, language: str | None, limit: int | None) -> None:
            nonlocal calls
            calls += 1

        scheduler.ingest = ingest
        scheduler.run_once()

        self.assertEqual(calls, 0)


class GitHubTrendingFetchEnvironmentTest(unittest.TestCase):
    def test_resolve_ca_file_uses_system_cert_when_python_default_is_missing(self) -> None:
        with (
            patch(
                "app.github_trending.ssl.get_default_verify_paths",
                return_value=SimpleNamespace(cafile=None),
            ),
            patch("app.github_trending.Path.is_file", return_value=True),
        ):
            self.assertEqual(resolve_ca_file(), "/etc/ssl/cert.pem")

    def test_resolve_ca_file_uses_python_default_when_available(self) -> None:
        with patch(
            "app.github_trending.ssl.get_default_verify_paths",
            return_value=SimpleNamespace(cafile="/python/cert.pem"),
        ):
            self.assertIsNone(resolve_ca_file())


if __name__ == "__main__":
    unittest.main()
