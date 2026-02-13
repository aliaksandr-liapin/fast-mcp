from __future__ import annotations

from functools import lru_cache
from typing import Any

from neo4j import Driver, GraphDatabase

from app.config import get_settings


@lru_cache(maxsize=1)
def _get_driver(uri: str, user: str, password: str) -> Driver | None:
    if not uri or not user or not password:
        return None
    return GraphDatabase.driver(uri, auth=(user, password))


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 1000:
        return 1000
    return limit


def neo4j_health() -> str:
    settings = get_settings()
    try:
        driver = _get_driver(
            settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
        )
        if driver is None:
            return "error: missing Neo4j configuration"
        with driver.session() as session:
            session.run("RETURN 1 AS ok").consume()
        return "ok"
    except Exception as exc:  # pragma: no cover - defensive
        return f"error: {exc}"


def neo4j_query(
    cypher: str, parameters: dict[str, Any] | None = None, limit: int = 50
) -> list[dict[str, Any]]:
    settings = get_settings()
    try:
        driver = _get_driver(
            settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
        )
        if driver is None:
            return [{"error": "missing Neo4j configuration"}]

        safe_limit = _clamp_limit(limit)
        cleaned = cypher.rstrip().rstrip(";")

        params = dict(parameters or {})
        params["limit"] = safe_limit
        if "LIMIT" in cleaned.upper():
            cypher_with_limit = f"CALL {{ {cleaned} }} RETURN * LIMIT $limit"
        else:
            cypher_with_limit = f"{cleaned} LIMIT $limit"

        with driver.session() as session:
            result = session.run(cypher_with_limit, params)
            return [_serialize_value(record.data()) for record in result]
    except Exception as exc:  # pragma: no cover - defensive
        return [{"error": str(exc)}]


def _serialize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_serialize_value(item) for item in value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:  # pragma: no cover - defensive
            return str(value)
    return value
