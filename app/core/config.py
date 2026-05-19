from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import Field, PrivateAttr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_postgres_url(url: str) -> tuple[str, str | None]:
    """Strip ?schema= from the URL (libpq/psycopg2 reject it) and return schema for search_path."""
    parsed = urlparse(url)
    if not parsed.scheme.startswith("postgres"):
        return url, None

    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    schema_name: str | None = None
    kept: list[tuple[str, str]] = []
    for key, value in pairs:
        if key.lower() == "schema":
            schema_name = value.strip() or None
            continue
        kept.append((key, value))

    new_query = urlencode(kept, doseq=True)
    cleaned = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ),
    )
    return cleaned, schema_name


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Student API"
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5434/fastapi",
        description=(
            "Postgres URL for psycopg2. A ?schema= query is removed from the URL "
            "and applied with search_path instead."
        ),
    )

    _pg_search_path: str | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def _normalize_database_url(self) -> Settings:
        url, schema = _normalize_postgres_url(self.DATABASE_URL)
        self.DATABASE_URL = url
        self._pg_search_path = schema
        return self

    @property
    def database_connect_args(self) -> dict:
        if self._pg_search_path:
            return {"options": f"-csearch_path={self._pg_search_path}"}
        return {}


settings = Settings()
