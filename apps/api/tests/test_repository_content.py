import sys
from pathlib import Path
import unittest

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base
from app.github_trending import TrendingRepository, ingest_trending_repositories
from app.migrations import ensure_repository_content_columns
from app.models import Repository
from app.repository_content import build_repository_chinese_content


class RepositoryContentMigrationTest(unittest.TestCase):
    def test_migration_adds_chinese_content_columns_to_existing_table(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE repositories ("
                    "id INTEGER PRIMARY KEY, "
                    "description TEXT"
                    ")"
                )
            )

        ensure_repository_content_columns(engine)
        ensure_repository_content_columns(engine)

        columns = {column["name"] for column in inspect(engine).get_columns("repositories")}
        engine.dispose()

        self.assertIn("summary_zh", columns)
        self.assertIn("description_zh", columns)


class RepositoryChineseContentTest(unittest.TestCase):
    def test_builds_chinese_summary_for_english_ai_repository(self) -> None:
        summary, description = build_repository_chinese_content(
            name="agent-kit",
            description="Build production AI agents with tool calling and retrieval.",
            primary_language="Python",
        )

        self.assertIn("agent-kit", summary)
        self.assertIn("AI Agent", summary)
        self.assertIn("Python", description)

    def test_preserves_existing_chinese_description(self) -> None:
        original = "一个用于构建本地知识库的开源工具。"

        summary, description = build_repository_chinese_content(
            name="knowledge-base",
            description=original,
            primary_language="TypeScript",
        )

        self.assertEqual(summary, original)
        self.assertIn(f"功能：{original}", description)
        self.assertIn("点评：", description)

    def test_describes_markitdown_function_and_adds_commentary(self) -> None:
        summary, description = build_repository_chinese_content(
            name="markitdown",
            description="Python tool for converting files and office documents to Markdown.",
            primary_language="Python",
        )

        self.assertIn("将文件和 Office 文档转换为 Markdown", summary)
        self.assertIn("文档预处理", summary)
        self.assertIn("功能：", description)
        self.assertIn("文档预处理", description)
        self.assertIn("点评：", description)
        self.assertIn("AI/RAG", description)

    def test_identifies_private_messaging_repository(self) -> None:
        summary, description = build_repository_chinese_content(
            name="simplex-chat",
            description="A private messaging network for mobile and desktop.",
            primary_language="Haskell",
        )

        self.assertIn("即时通信与隐私", summary)
        self.assertNotIn("开源项目的开源项目", summary)
        self.assertIn("Haskell", description)

    def test_ingestion_persists_chinese_content(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)

        with Session(engine) as db:
            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="example",
                        name="agent-kit",
                        url="https://github.com/example/agent-kit",
                        description="Build production AI agents.",
                        primary_language="Python",
                        stars=100,
                        forks=10,
                        stars_gained=20,
                    )
                ],
            )
            repository = db.query(Repository).one()

        engine.dispose()

        self.assertIn("AI Agent", repository.summary_zh)
        self.assertIn("Python", repository.description_zh)


if __name__ == "__main__":
    unittest.main()
