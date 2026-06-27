import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import MagicMock, patch, sentinel
from urllib.error import URLError

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import repository_content
from app.database import Base
from app.github_trending import TrendingRepository, ingest_trending_repositories
from app.migrations import ensure_repository_content_columns
from app.models import Repository
from app.repository_content import (
    backfill_repository_chinese_content,
    build_repository_chinese_content,
)


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
    def test_main_forces_repository_content_backfill_and_reports_count(self) -> None:
        db = MagicMock()
        session_context = MagicMock()
        session_context.__enter__.return_value = db
        output = io.StringIO()
        calls = []

        with (
            patch(
                "app.repository_content.Base.metadata.create_all",
                side_effect=lambda **kwargs: calls.append("create_all"),
            ) as create_all,
            patch.object(repository_content, "engine", sentinel.engine),
            patch.object(
                repository_content,
                "ensure_repository_content_columns",
                side_effect=lambda engine: calls.append("migrate"),
            ) as migrate,
            patch.object(
                repository_content,
                "SessionLocal",
                side_effect=lambda: (calls.append("session"), session_context)[1],
            ) as session_local,
            patch.object(
                repository_content,
                "backfill_repository_chinese_content",
                return_value=3,
            ) as backfill,
            redirect_stdout(output),
        ):
            repository_content.main()

        create_all.assert_called_once_with(bind=sentinel.engine)
        migrate.assert_called_once_with(sentinel.engine)
        session_local.assert_called_once_with()
        self.assertEqual(calls, ["create_all", "migrate", "session"])
        backfill.assert_called_once_with(db, force=True)
        self.assertEqual(
            output.getvalue(),
            "Backfilled Chinese content for 3 repositories.\n",
        )

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_uses_glm_for_unmatched_english_description(self, urlopen) -> None:
        response = MagicMock()
        response.read.return_value = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": "用于在 Mac 上通过轻量虚拟机创建和运行 Linux 容器。"
                        }
                    }
                ]
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        summary, description = build_repository_chinese_content(
            name="lima",
            description="Linux virtual machines, typically on macOS, for running containers.",
            primary_language="Go",
        )

        self.assertEqual(
            summary,
            "用于在 Mac 上通过轻量虚拟机创建和运行 Linux 容器。",
        )
        self.assertEqual(
            description,
            "功能：用于在 Mac 上通过轻量虚拟机创建和运行 Linux 容器。",
        )
        sent_request = urlopen.call_args.args[0]
        self.assertEqual(
            sent_request.full_url,
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        )
        payload = json.loads(sent_request.data)
        self.assertEqual(payload["model"], "glm-4.7")
        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(payload["max_tokens"], 120)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 20)

    @patch.dict("os.environ", {}, clear=True)
    @patch("app.repository_content.request.urlopen")
    def test_falls_back_to_original_description_without_model_config(
        self, urlopen
    ) -> None:
        original = "An experimental project."

        summary, description = build_repository_chinese_content(
            name="unknown-project",
            description=original,
            primary_language="Rust",
        )

        self.assertEqual(summary, original)
        self.assertEqual(description, f"功能：{original}")
        urlopen.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch(
        "app.repository_content.request.urlopen",
        side_effect=URLError("network unavailable"),
    )
    def test_falls_back_to_original_description_when_model_request_fails(
        self, urlopen
    ) -> None:
        original = "An experimental project."

        summary, description = build_repository_chinese_content(
            name="unknown-project",
            description=original,
            primary_language="Rust",
        )

        self.assertEqual(summary, original)
        self.assertEqual(description, f"功能：{original}")
        urlopen.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_falls_back_when_model_response_is_incomplete(self, urlopen) -> None:
        response = MagicMock()
        response.read.side_effect = IncompleteRead(b'{"choices":', 100)
        urlopen.return_value.__enter__.return_value = response
        original = "An experimental project."

        summary, description = build_repository_chinese_content(
            name="unknown-project",
            description=original,
            primary_language="Rust",
        )

        self.assertEqual(summary, original)
        self.assertEqual(description, f"功能：{original}")
        urlopen.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    @patch("app.repository_content.request.urlopen")
    def test_uses_honest_summary_for_empty_description(self, urlopen) -> None:
        summary, description = build_repository_chinese_content(
            name="unknown-project",
            description=None,
            primary_language="Rust",
        )

        self.assertEqual(summary, "暂无项目简介，无法归纳具体功能。")
        self.assertEqual(description, "功能：暂无项目简介，无法归纳具体功能。")
        urlopen.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_does_not_call_model_for_chinese_description(self, urlopen) -> None:
        build_repository_chinese_content(
            name="knowledge-base",
            description="一个用于构建本地知识库的开源工具。",
            primary_language="TypeScript",
        )

        urlopen.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_prefers_model_summary_over_profile_match_when_configured(
        self, urlopen
    ) -> None:
        response = MagicMock()
        response.read.return_value = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": "用于构建可生产的 AI Agent 应用，支持工具调用与检索增强。"
                        }
                    }
                ]
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response

        summary, description = build_repository_chinese_content(
            name="agent-kit",
            description="Build production AI agents with tool calling and retrieval.",
            primary_language="Python",
        )

        self.assertEqual(
            summary,
            "用于构建可生产的 AI Agent 应用，支持工具调用与检索增强。",
        )
        self.assertEqual(
            description,
            "功能：用于构建可生产的 AI Agent 应用，支持工具调用与检索增强。",
        )
        urlopen.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch(
        "app.repository_content.request.urlopen",
        side_effect=URLError("network unavailable"),
    )
    def test_falls_back_to_profile_when_model_fails_for_matched_description(
        self, urlopen
    ) -> None:
        summary, description = build_repository_chinese_content(
            name="agent-kit",
            description="Build production AI agents with tool calling and retrieval.",
            primary_language="Python",
        )

        self.assertIn("AI Agent", summary)
        self.assertIn("Python", description)
        urlopen.assert_called_once()

    def test_builds_chinese_summary_for_english_ai_repository(self) -> None:
        summary, description = build_repository_chinese_content(
            name="agent-kit",
            description="Build production AI agents with tool calling and retrieval.",
            primary_language="Python",
        )

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
        self.assertNotIn("点评：", description)

    def test_describes_markitdown_function_and_adds_commentary(self) -> None:
        summary, description = build_repository_chinese_content(
            name="markitdown",
            description="Python tool for converting files and office documents to Markdown.",
            primary_language="Python",
        )

        self.assertIn("将文件和 Office 文档转换为 Markdown", summary)
        self.assertIn("文档预处理", summary)
        self.assertNotIn("是一个开源项目", summary)
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

    def test_omits_generic_commentary_when_function_is_unknown(self) -> None:
        summary, description = build_repository_chinese_content(
            name="unknown-project",
            description="An experimental project.",
            primary_language="Rust",
        )

        self.assertNotIn("集成成本与学习价值", summary)
        self.assertNotIn("集成成本与学习价值", description)
        self.assertNotIn("点评：", description)

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_ingestion_persists_model_generated_chinese_content(
        self, urlopen
    ) -> None:
        response = MagicMock()
        response.read.return_value = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": "用于验证模型摘要能够持久化到数据库的独特项目。"
                        }
                    }
                ]
            }
        ).encode()
        urlopen.return_value.__enter__.return_value = response
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)

        with Session(engine) as db:
            ingest_trending_repositories(
                db,
                [
                    TrendingRepository(
                        rank=1,
                        owner="example",
                        name="unmatched-repository",
                        url="https://github.com/example/unmatched-repository",
                        description="An experimental project.",
                        primary_language="Rust",
                        stars=100,
                        forks=10,
                        stars_gained=20,
                    )
                ],
            )
            repository = db.query(Repository).one()

        engine.dispose()

        self.assertEqual(
            repository.summary_zh,
            "用于验证模型摘要能够持久化到数据库的独特项目。",
        )
        self.assertEqual(
            repository.description_zh,
            "功能：用于验证模型摘要能够持久化到数据库的独特项目。",
        )

    @patch.dict(
        "os.environ",
        {
            "REPO_SCOUT_OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "REPO_SCOUT_OPENAI_API_KEY": "test-api-key",
            "REPO_SCOUT_OPENAI_MODEL": "glm-4.7",
        },
        clear=True,
    )
    @patch("app.repository_content.request.urlopen")
    def test_backfill_skips_repository_with_complete_chinese_content(
        self, urlopen
    ) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)

        with Session(engine) as db:
            repository = Repository(
                owner="example",
                name="complete-repository",
                full_name="example/complete-repository",
                url="https://github.com/example/complete-repository",
                description="An experimental project.",
                summary_zh="已有中文摘要。",
                description_zh="功能：已有中文摘要。",
            )
            db.add(repository)
            db.commit()

            updated = backfill_repository_chinese_content(db)
            db.refresh(repository)

            self.assertEqual(updated, 0)
            self.assertEqual(repository.summary_zh, "已有中文摘要。")
            self.assertEqual(repository.description_zh, "功能：已有中文摘要。")

        engine.dispose()
        urlopen.assert_not_called()

    @patch(
        "app.repository_content.build_repository_chinese_content",
        return_value=("新的中文摘要。", "功能：新的中文详情。"),
    )
    def test_force_backfill_overwrites_and_persists_existing_content(
        self, build_content
    ) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)

        with Session(engine) as db:
            db.add(
                Repository(
                    owner="example",
                    name="existing-repository",
                    full_name="example/existing-repository",
                    url="https://github.com/example/existing-repository",
                    description="An experimental project.",
                    summary_zh="旧的中文摘要。",
                    description_zh="功能：旧的中文详情。",
                )
            )
            db.commit()

            updated = backfill_repository_chinese_content(db, force=True)

        with Session(engine) as db:
            repository = db.query(Repository).one()
            self.assertEqual(updated, 1)
            self.assertEqual(repository.summary_zh, "新的中文摘要。")
            self.assertEqual(repository.description_zh, "功能：新的中文详情。")

        engine.dispose()
        build_content.assert_called_once_with(
            "existing-repository",
            "An experimental project.",
            None,
        )


if __name__ == "__main__":
    unittest.main()
