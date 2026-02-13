from __future__ import annotations

from dotenv import load_dotenv
from fastmcp import FastMCP

from app.config import Settings, get_settings
from app.logging import configure_logging
from app.tools.greetings import greet
from app.tools.neo4j import neo4j_health, neo4j_query


def create_app(settings: Settings) -> FastMCP:
    app = FastMCP(settings.app_name)
    app.tool(greet)
    app.tool(neo4j_health)
    app.tool(neo4j_query)
    return app


def main() -> None:
    load_dotenv()
    settings = get_settings()
    configure_logging(settings.log_level)
    app = create_app(settings)
    app.run(
        transport="streamable-http",
        host=settings.host,
        port=settings.port,
        path="/mcp",
        stateless_http=True,
    )


if __name__ == "__main__":
    main()
