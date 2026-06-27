from dataclasses import dataclass
import json
import os
import re
from urllib import request

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .migrations import ensure_repository_content_columns
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


@dataclass(frozen=True)
class ModelSummaryConfig:
    base_url: str
    api_key: str
    model: str


def load_model_summary_config() -> ModelSummaryConfig | None:
    base_url = os.getenv("REPO_SCOUT_OPENAI_BASE_URL", "").strip()
    api_key = os.getenv("REPO_SCOUT_OPENAI_API_KEY", "").strip()
    model = os.getenv("REPO_SCOUT_OPENAI_MODEL", "").strip()
    if not all((base_url, api_key, model)):
        return None
    return ModelSummaryConfig(base_url=base_url, api_key=api_key, model=model)


def request_model_summary(
    config: ModelSummaryConfig,
    name: str,
    description: str,
    primary_language: str | None,
) -> str:
    prompt = (
        "请根据以下 GitHub 仓库信息，只返回一句事实性的中文功能描述，不要点评，"
        "不要使用 Markdown，也不要补充无法从输入确认的信息。\n"
        f"仓库名：{name}\n"
        f"英文简介：{description}\n"
        f"主要语言：{primary_language or '未知'}"
    )
    payload = json.dumps(
        {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "thinking": {"type": "disabled"},
            "temperature": 0.2,
            "max_tokens": 120,
        }
    ).encode("utf-8")
    model_request = request.Request(
        f"{config.base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(model_request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"].strip()


def generate_model_summary(
    name: str,
    description: str,
    primary_language: str | None,
) -> str | None:
    config = load_model_summary_config()
    if config is None:
        return None
    try:
        summary = request_model_summary(
            config,
            name=name,
            description=description,
            primary_language=primary_language,
        )
        if not summary or not contains_chinese(summary):
            return None
    except Exception:
        return None
    return summary


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
    if not original:
        summary = "暂无项目简介，无法归纳具体功能。"
        return summary, f"功能：{summary}"

    searchable = f"{name} {original}".lower()
    for keywords, matched_function, matched_commentary in CONTENT_PROFILES:
        if any(keyword in searchable for keyword in keywords):
            function = matched_function
            commentary = matched_commentary
            break
    else:
        summary = generate_model_summary(name, original, primary_language) or original
        return summary, f"功能：{summary}"

    language = primary_language or "多种技术"
    summary = f"{function}。"
    description_zh = f"功能：{name} {function}，主要使用 {language} 开发。"
    if commentary:
        summary = f"{summary}{commentary}。"
        description_zh = f"{description_zh}点评：{commentary}。"
    return summary, description_zh


def backfill_repository_chinese_content(db: Session, force: bool = False) -> int:
    statement = select(Repository)
    if not force:
        statement = statement.where(
            (Repository.summary_zh.is_(None))
            | (Repository.summary_zh == "")
            | (Repository.description_zh.is_(None))
            | (Repository.description_zh == "")
        )
    repositories = db.scalars(statement).all()
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


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_repository_content_columns(engine)
    with SessionLocal() as db:
        count = backfill_repository_chinese_content(db, force=True)
    print(f"Backfilled Chinese content for {count} repositories.")


if __name__ == "__main__":
    main()
