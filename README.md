# fast-mcp-server

# PRD: FastMCP Production-Ready Server

## 1. Purpose
Build a production-ready FastMCP server that is structured, configurable, testable, and ready for local, containerized, and Azure deployments. Include Neo4j connectivity as a tool and provide CI/CD scaffolding.

## 2. Goals
- Organize the project into a package-based structure.
- Provide environment-driven configuration (HOST/PORT, app name, Neo4j creds).
- Add structured logging (JSON).
- Add Neo4j tools: health check and query tool.
- Provide tests, Docker, Docker Compose, and Azure deployment templates.
- Provide CI workflow for tests and optional deployments.

## 3. Non-Goals
- Full production security hardening (secrets management, network policies).
- Domain-specific Neo4j schema or complex query library.
- Full monitoring/observability stack.

## 4. Target Environment
- Python 3.10.19
- FastMCP 2.14.5
- Neo4j 5.25.0
- Local dev on macOS, production on Azure (Container Apps or App Service)

## 5. Functional Requirements

### 5.1 Server
- Must start a FastMCP server with name from environment.
- Must bind to HOST and PORT from environment.
- MCP endpoint available at /mcp.

### 5.2 Tools
- greet(name: str) -> str returns "Hello, {name}!".
- neo4j_health() -> "ok" or "error" with exception string.
- neo4j_query(cypher: str, parameters: dict | None = None, limit: int = 50) -> list[dict]
  - Limit capped to 1..1000.
  - Return list of record dicts or [{"error": "..."}] on failure.

### 5.3 Configuration
- Read these variables:
  - APP_NAME
  - HOST
  - PORT
  - LOG_LEVEL
  - NEO4J_URI
  - NEO4J_USER
  - NEO4J_PASSWORD
- Provide .env.example template.

### 5.4 Logging
- Emit JSON logs to stdout.
- Include time (UTC ISO), level, logger, message, and exc_info when present.

### 5.5 Tests
- Basic unit test for greet tool.
- Run with pytest.

### 5.6 Docker and Compose
- Dockerfile for app container.
- docker-compose.yml with app and Neo4j services.
- App uses Neo4j container via bolt://neo4j:7687.

### 5.7 Azure Deployment
- Azure Container Apps template (containerapp.yaml).
- Script to deploy Container Apps.
- App Service startup script.
- App Service appsettings.json template.
- Script to deploy App Service.
- GitHub Actions workflow for CI and optional deploy.

### 5.8 GitHub Secrets (Deploy)
Required for CI deploy jobs:
- AZURE_CREDENTIALS (service principal JSON)
- AZURE_RG
- AZURE_LOCATION
- ACR_LOGIN_SERVER
- ACR_USERNAME
- ACR_PASSWORD

App Service only:
- APP_SERVICE_NAME

Container Apps only:
- ACA_ENV
- ACA_APP_NAME

## 6. Project Structure
.
├─ app/
│ ├─ __init__.py
│ ├─ config.py
│ ├─ logging.py
│ ├─ main.py
│ └─ tools/
│ ├─ __init__.py
│ ├─ greetings.py
│ └─ neo4j.py
├─ tests/
│ └─ test_greetings.py
├─ requirements/
│ ├─ base.txt
│ └─ dev.txt
├─ .env.example
├─ Dockerfile
├─ docker-compose.yml
├─ startup.sh
├─ requirements.txt
├─ server.py
├─ azure/
│ ├─ appsettings.json
│ └─ containerapp.yaml
├─ scripts/
│ ├─ deploy_aca.sh
│ └─ deploy_appservice.sh
└─ .github/
└─ workflows/
└─ ci-deploy.yml


## 6.1 Quick Start

Local:
1. Create a .env file from .env.example and adjust values as needed.
2. Install deps: pip install -r requirements/dev.txt
3. Run tests: pytest
4. Start server: python -m app.main
5. Open: http://127.0.0.1:8000/mcp

Docker:
1. Build and run: docker compose up --build
2. Open: http://127.0.0.1:8000/mcp
3. Neo4j browser: http://127.0.0.1:7474

Azure App Service (manual):
1. Set required environment variables and secrets for ACR.
2. Run: bash scripts/deploy_appservice.sh

Neo4j env vars (required for Neo4j tools):
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD

MCP client headers (stateless streamable-http):
- Accept: application/json, text/event-stream
- Content-Type: application/json

Postman import (stateless collection):
```json
{
  "info": {
    "name": "FastMCP Neo4j (Stateless)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "neo4j_health",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Accept", "value": "application/json, text/event-stream" },
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": \"h1\",\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"neo4j_health\",\n    \"arguments\": {}\n  }\n}"
        },
        "url": {
          "raw": "http://{{host}}:{{port}}/mcp",
          "protocol": "http",
          "host": ["{{host}}"],
          "port": "{{port}}",
          "path": ["mcp"]
        }
      }
    },
    {
      "name": "neo4j_query",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Accept", "value": "application/json, text/event-stream" },
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"jsonrpc\": \"2.0\",\n  \"id\": \"q1\",\n  \"method\": \"tools/call\",\n  \"params\": {\n    \"name\": \"neo4j_query\",\n    \"arguments\": {\n      \"cypher\": \"MATCH (n) RETURN n LIMIT 5\",\n      \"parameters\": {}\n    }\n  }\n}"
        },
        "url": {
          "raw": "http://{{host}}:{{port}}/mcp",
          "protocol": "http",
          "host": ["{{host}}"],
          "port": "{{port}}",
          "path": ["mcp"]
        }
      }
    }
  ],
  "variable": [
    { "key": "host", "value": "127.0.0.1" },
    { "key": "port", "value": "8000" }
  ]
}
```

## 7. Architecture

### 7.1 Component Diagram (ASCII)

flowchart TB
  App["FastMCP App<br/>app/main.py<br/>tools/*.py<br/>config.py<br/>logging.py"]
  Neo4j["Neo4j DB<br/>bolt://host:7687"]
  MCP["/mcp endpoint"]

  App <---> Neo4j
  App --> MCP

### 7.2 Runtime Flow (ASCII)
Start 
    -> load Settings 
    -> configure JSON logging 
    -> create FastMCP
    -> register tools 
    -> run(host, port)


### 7.3 Deployment Diagram (ASCII)
Local:
Developer -> Python -> FastMCP -> /mcp

Docker:
Developer -> Docker -> Container (FastMCP) -> Neo4j container

Azure Container Apps:
GitHub Actions -> ACA -> Container (FastMCP)

Azure App Service:
GitHub Actions -> App Service -> startup.sh -> FastMCP


## 8. Detailed Implementation Requirements

### 8.1 app/config.py
- Dataclass Settings with env defaults.
- get_settings() returns Settings.

### 8.2 app/logging.py
- JsonFormatter with ensure_ascii=True.
- configure_logging(level) sets root handler and level.

### 8.3 app/main.py
- create_app(settings) returns FastMCP with tools registered.
- main() loads settings and runs with host/port.

### 8.4 app/tools/neo4j.py
- Use neo4j.GraphDatabase.driver with cached driver.
- Health check uses "RETURN 1 AS ok".
- Query returns list of dicts, handles errors.

### 8.5 server.py
- Calls app.main.main for compatibility.

## 9. Security and Config
- No secrets stored in repo.
- .env.example is safe default.
- Azure app settings used to provide secrets in production.

## 10. Operational Considerations
- Logging is JSON for ingestion into Azure logging.
- Neo4j connectivity errors should not crash server on startup.
- Neo4j query tool is minimal and should be restricted in production.

## 11. Risks and Mitigations
- Unbounded queries: enforce limit cap.
- Credentials leakage: avoid committing .env, use Azure settings.
- Availability: allow container restarts via Azure.

## 12. Testing Plan
- Unit test for greet tool.
- Optional: add integration tests for Neo4j in docker-compose.

## 13. Acceptance Criteria
- Server runs with env HOST/PORT.
- /mcp endpoint responds.
- greet tool returns correct string.
- neo4j_health returns "ok" when DB reachable.
- neo4j_query returns rows for valid queries.
- docker-compose brings up app + neo4j.
- CI runs pytest.
- Azure templates and scripts are present.

## 14. Milestones
1. Restructure project and add config/logging/tools.
2. Add tests and split requirements.
3. Add Docker and Compose.
4. Add Azure templates and scripts.
5. Add CI workflow.

## 15. Open Questions
- Final Neo4j schema and query patterns.
- Azure target: Container Apps vs App Service primary.
- Secrets management strategy (Key Vault, etc.).