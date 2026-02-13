from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str
    host: str
    port: int
    log_level: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "fast-mcp-server"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=_get_int_env("PORT", 8000),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        neo4j_uri=os.getenv("NEO4J_URI", ""),
        neo4j_user=os.getenv("NEO4J_USER", ""),
        neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
    )
