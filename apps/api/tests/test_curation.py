import os
import sys
from pathlib import Path
import unittest
from unittest import mock

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import curation
from app.curation import (
    curate_featured_collections,
    score_repository,
)
from app.database import Base
from app.github_trending import TrendingRepository, ingest_trending_repositories
from app.main import featured_collection, featured_collections, get_repository, trigger_featured_curation
from app.models import FeaturedCollection, FeaturedRepository, Repository


class CurationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.env_patcher = mock.patch.dict(
            os.environ,
            {
                "REPO_SCOUT_OPENAI_BASE_URL": "",
                "REPO_SCOUT_OPENAI_API_KEY": "",
                "REPO_SCOUT_OPENAI_MODEL": "",
            },
            clear=False,
        )
        self.env_patcher.start()
        self.addCleanup(self.env_patcher.stop)
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)

    def tearDown(self) -> None:
        self.engine.dispose()

    def seed_trending(self, db: Session) -> None:
        ingest_trending_repositories(
            db,
            [
                TrendingRepository(
                    rank=1,
                    owner="ai-owner",
                    name="agent-kit",
                    url="https://github.com/ai-owner/agent-kit",
                    description="Build LLM agents with retrieval and tool calling.",
                    primary_language="Python",
                    stars=12000,
                    forks=900,
                    stars_gained=320,
                ),
                TrendingRepository(
                    rank=2,
                    owner="tool-owner",
                    name="cli-helper",
                    url="https://github.com/tool-owner/cli-helper",
                    description="AI developer CLI toolkit for local model automation.",
                    primary_language="Go",
                    stars=9000,
                    forks=500,
                    stars_gained=180,
                ),
                TrendingRepository(
                    rank=3,
                    owner="site-owner",
                    name="landing-page",
                    url="https://github.com/site-owner/landing-page",
                    description="Static marketing page template.",
                    primary_language="CSS",
                    stars=5000,
                    forks=200,
                    stars_gained=20,
                ),
            ],
            period="daily",
            language=None,
        )

    def test_score_repository_prefers_ai_learning_projects(self) -> None:
        ai_repository = Repository(
            owner="ai-owner",
            name="agent-kit",
            full_name="ai-owner/agent-kit",
            url="https://github.com/ai-owner/agent-kit",
            description="Build LLM agents with retrieval and tool calling.",
            primary_language="Python",
            stars=12000,
            forks=900,
        )
        css_repository = Repository(
            owner="site-owner",
            name="landing-page",
            full_name="site-owner/landing-page",
            url="https://github.com/site-owner/landing-page",
            description="Static marketing page template.",
            primary_language="CSS",
            stars=5000,
            forks=200,
        )

        ai_score = score_repository(ai_repository, stars_gained=320)
        css_score = score_repository(css_repository, stars_gained=20)

        self.assertGreater(ai_score.total, css_score.total)
        self.assertGreaterEqual(ai_score.ai_relevance, 4)
        self.assertGreaterEqual(ai_score.learning_value, 4)

    def test_curate_featured_collections_persists_ranked_template_results(self) -> None:
        with Session(self.engine) as db:
            self.seed_trending(db)

            collections = curate_featured_collections(db, limit=2)
            api_collections = featured_collections(db=db)

            stored_collection = db.scalar(
                select(FeaturedCollection).where(FeaturedCollection.slug == "beginner-friendly-ai")
            )
            featured_rows = db.scalars(
                select(FeaturedRepository).where(
                    FeaturedRepository.collection_id == stored_collection.id
                )
            ).all()

        self.assertEqual([collection.slug for collection in collections], [
            "beginner-friendly-ai",
            "ai-agent-projects",
            "llm-tools",
            "notable-developer-tools",
        ])
        self.assertEqual(stored_collection.model_name, "local-template")
        self.assertEqual([row.rank for row in featured_rows], [1, 2])
        self.assertIn("agent-kit", featured_rows[0].reason)
        self.assertEqual(api_collections[0].repositories[0].full_name, "ai-owner/agent-kit")

    def test_curate_featured_collections_replaces_existing_rows_without_duplicates(self) -> None:
        with Session(self.engine) as db:
            self.seed_trending(db)

            curate_featured_collections(db, limit=2)
            curate_featured_collections(db, limit=2)

            collections = db.scalars(select(FeaturedCollection)).all()
            featured_rows = db.scalars(select(FeaturedRepository)).all()

        self.assertEqual(len(collections), 4)
        self.assertEqual(len(featured_rows), 8)

    def test_curate_featured_collections_uses_model_reason_when_configured(self) -> None:
        model_reason = "agent-kit 适合用来观察 Agent 工具调用和检索增强的工程实现。"
        env = {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://model.example/v1",
            "REPO_SCOUT_OPENAI_API_KEY": "test-key",
            "REPO_SCOUT_OPENAI_MODEL": "reason-model",
        }

        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch.object(
                curation,
                "request_model_reason",
                return_value=model_reason,
            ) as request_reason:
                with Session(self.engine) as db:
                    self.seed_trending(db)

                    curate_featured_collections(db, limit=1)
                    stored_collection = db.scalar(
                        select(FeaturedCollection).where(
                            FeaturedCollection.slug == "beginner-friendly-ai"
                        )
                    )
                    featured_row = db.scalar(
                        select(FeaturedRepository).where(
                            FeaturedRepository.collection_id == stored_collection.id
                        )
                    )

        self.assertEqual(stored_collection.model_name, "reason-model")
        self.assertEqual(featured_row.reason, model_reason)
        request_reason.assert_called()

    def test_curate_featured_collections_falls_back_to_template_when_model_fails(self) -> None:
        env = {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://model.example/v1",
            "REPO_SCOUT_OPENAI_API_KEY": "test-key",
            "REPO_SCOUT_OPENAI_MODEL": "reason-model",
        }

        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch.object(
                curation,
                "request_model_reason",
                side_effect=RuntimeError("boom"),
            ):
                with Session(self.engine) as db:
                    self.seed_trending(db)

                    curate_featured_collections(db, limit=1)
                    stored_collection = db.scalar(
                        select(FeaturedCollection).where(
                            FeaturedCollection.slug == "beginner-friendly-ai"
                        )
                    )
                    featured_row = db.scalar(
                        select(FeaturedRepository).where(
                            FeaturedRepository.collection_id == stored_collection.id
                        )
                    )

        self.assertEqual(stored_collection.model_name, "reason-model")
        self.assertIn("agent-kit", featured_row.reason)

    def test_trigger_featured_curation_returns_api_output(self) -> None:
        with Session(self.engine) as db:
            self.seed_trending(db)

            result = trigger_featured_curation(
                limit=2,
                request=None,
                admin_token=None,
                db=db,
            )

        self.assertEqual(result[0].slug, "beginner-friendly-ai")
        self.assertEqual(result[0].repositories[0].full_name, "ai-owner/agent-kit")

    def test_featured_collection_returns_one_collection_by_slug(self) -> None:
        with Session(self.engine) as db:
            self.seed_trending(db)
            curate_featured_collections(db, limit=2)

            result = featured_collection(slug="beginner-friendly-ai", db=db)

        self.assertEqual(result.slug, "beginner-friendly-ai")
        self.assertEqual(result.repositories[0].full_name, "ai-owner/agent-kit")

    def test_repository_detail_includes_featured_reason_when_curated(self) -> None:
        with Session(self.engine) as db:
            self.seed_trending(db)
            curate_featured_collections(db, limit=2)

            result = get_repository(owner="ai-owner", name="agent-kit", db=db)

        self.assertIn("agent-kit", result.featured_reason)
        self.assertEqual(result.featured_collection_slug, "beginner-friendly-ai")
        self.assertEqual(result.featured_collection_title, "适合初学者的 AI 项目")
        self.assertGreaterEqual(result.beginner_score, 4)
        self.assertGreaterEqual(result.learning_value_score, 4)

    def test_repository_detail_includes_star_trend_between_latest_snapshots(self) -> None:
        with Session(self.engine) as db:
            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="trend-owner",
                        name="trend-project",
                        url="https://github.com/trend-owner/trend-project",
                        description="Trend test repository.",
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
                        owner="trend-owner",
                        name="trend-project",
                        url="https://github.com/trend-owner/trend-project",
                        description="Trend test repository.",
                        primary_language="Python",
                        stars=155,
                        forks=12,
                        stars_gained=20,
                    )
                ],
                period="daily",
                language=None,
            )

            result = get_repository(owner="trend-owner", name="trend-project", db=db)

        self.assertEqual(result.trend_delta_stars, 55)
        self.assertEqual(result.trend_snapshot_count, 2)


if __name__ == "__main__":
    unittest.main()
