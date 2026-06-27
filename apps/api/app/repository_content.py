import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Repository


CONTENT_PROFILES = (
    (
        ("convert", "conversion", "markdown", "office document"),
        "用于将文件和 Office 文档转换为 Markdown",
        "适合文档预处理、内容提取，以及为 AI/RAG 工作流准备结构化文本",
    ),
    (
        ("messaging", "chat", "private", "privacy", "ios", "android"),
        "用于构建注重即时通信与隐私保护的跨平台通信网络",
        "适合研究无中心身份标识的通信设计、隐私保护和多端客户端实现",
    ),
    (
        ("agent", "llm", "rag", "retrieval", "prompt", "model"),
        "用于构建 AI Agent 与大模型应用",
        "适合了解智能体编排、模型调用、工具使用和知识检索的工程实现",
    ),
    (
        ("database", "data", "storage", "analytics"),
        "用于处理、存储或分析数据",
        "适合研究数据建模、处理流程和性能优化方式",
    ),
    (
        ("security", "vulnerability", "scanner"),
        "用于安全检测、漏洞分析或风险防护",
        "适合了解安全工具的检测策略、规则组织和工程落地",
    ),
    (
        ("web", "frontend", "ui", "dashboard"),
        "用于构建 Web 应用或交互界面",
        "适合拆解前端架构、界面交互和 Web 产品工程实践",
    ),
    (
        ("cli", "sdk", "api", "framework", "library", "developer", "toolkit"),
        "用于支持软件开发、工具集成或工程自动化",
        "适合了解开发工具的接口设计、扩展机制和工程效率优化",
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
        return original, f"功能：{original}"

    searchable = f"{name} {original}".lower()
    function = "具体功能暂未完成中文归纳"
    commentary = ""
    for keywords, matched_function, matched_commentary in CONTENT_PROFILES:
        if any(keyword in searchable for keyword in keywords):
            function = matched_function
            commentary = matched_commentary
            break

    language = primary_language or "多种技术"
    summary = f"{function}。"
    description_zh = f"功能：{name} {function}，主要使用 {language} 开发。"
    if commentary:
        summary = f"{summary}{commentary}。"
        description_zh = f"{description_zh}点评：{commentary}。"
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
