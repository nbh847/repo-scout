from sqlalchemy import Engine, inspect, text


def ensure_repository_content_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    if "repositories" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"] for column in inspector.get_columns("repositories")
    }
    missing_columns = [
        column
        for column in ("summary_zh", "description_zh")
        if column not in existing_columns
    ]
    if not missing_columns:
        return

    with engine.begin() as connection:
        for column in missing_columns:
            connection.execute(
                text(f"ALTER TABLE repositories ADD COLUMN {column} TEXT")
            )
