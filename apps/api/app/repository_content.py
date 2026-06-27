import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Repository


CONTENT_CATEGORIES = (
    (
        ("messaging", "chat", "private", "privacy", "ios", "android"),
        "即时通信与隐私",
        "跨平台通信、隐私保护和客户端设计",
    ),
    (
        ("agent", "llm", "rag", "retrieval", "prompt", "model"),
        "AI Agent 与大模型应用",
        "智能体、模型调用和知识检索",
    ),
    (
        ("cli", "sdk", "api", "framework", "library", "developer", "toolkit"),
        "开发工具",
        "开发流程、工具集成和工程效率",
    ),
    (
        ("database", "data", "storage", "analytics"),
        "数据处理",
        "数据存储、处理和分析",
    ),
    (
        ("web", "frontend", "ui", "dashboard"),
        "Web 应用",
        "Web 产品构建和界面交互",
    ),
    (
        ("security", "vulnerability", "scanner"),
        "安全工具",
        "安全检测、分析和防护",
    ),
)


def contains_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def build_repository_chinese_content(
    name: str,
    description: str | None,
    primary_language: str | None,
) -> tuple[str, str]:
    original = (description or "").strip()
    if original and contains_chinese(original):
        return original, original

    searchable = f"{name} {original}".lower()
    category = "通用软件"
    focus = "项目的核心能力、实现方式和使用场景"
    for keywords, matched_category, matched_focus in CONTENT_CATEGORIES:
        if any(keyword in searchable for keyword in keywords):
            category = matched_category
            focus = matched_focus
            break

    language = primary_language or "多种技术"
    summary = f"{name} 是一个面向{category}的开源项目，适合了解{focus}。"
    description_zh = (
        f"{name} 主要使用 {language} 开发，聚焦{focus}。"
        "可结合下方原始说明进一步了解项目的具体能力和使用方式。"
    )
    return summary, description_zh


def backfill_repository_chinese_content(db: Session) -> int:
    repositories = db.scalars(select(Repository)).all()
    for repository in repositories:
        summary, description = build_repository_chinese_content(
            repository.name,
            repository.description,
            repository.primary_language,
        )
        repository.summary_zh = summary
        repository.description_zh = description
    if repositories:
        db.commit()
    return len(repositories)
