#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_RG:?Set AZURE_RG}"
: "${AZURE_LOCATION:?Set AZURE_LOCATION}"
: "${ACA_ENV:?Set ACA_ENV}"
: "${ACA_APP_NAME:?Set ACA_APP_NAME}"
: "${ACR_LOGIN_SERVER:?Set ACR_LOGIN_SERVER}"
: "${ACR_USERNAME:?Set ACR_USERNAME}"
: "${ACR_PASSWORD:?Set ACR_PASSWORD}"

az group create --name "$AZURE_RG" --location "$AZURE_LOCATION"

az containerapp env create \
  --name "$ACA_ENV" \
  --resource-group "$AZURE_RG" \
  --location "$AZURE_LOCATION"

az containerapp create \
  --name "$ACA_APP_NAME" \
  --resource-group "$AZURE_RG" \
  --environment "$ACA_ENV" \
  --image "$ACR_LOGIN_SERVER/fast-mcp-server:latest" \
  --ingress external \
  --target-port 8000 \
  --registry-server "$ACR_LOGIN_SERVER" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --env-vars \
      APP_NAME=fast-mcp-server \
      HOST=0.0.0.0 \
      PORT=8000 \
      LOG_LEVEL=INFO \
      NEO4J_URI=bolt://<host>:7687 \
      NEO4J_USER=neo4j \
      NEO4J_PASSWORD=<password>
