#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_RG:?Set AZURE_RG}"
: "${AZURE_LOCATION:?Set AZURE_LOCATION}"
: "${APP_SERVICE_NAME:?Set APP_SERVICE_NAME}"
: "${ACR_LOGIN_SERVER:?Set ACR_LOGIN_SERVER}"
: "${ACR_USERNAME:?Set ACR_USERNAME}"
: "${ACR_PASSWORD:?Set ACR_PASSWORD}"

az group create --name "$AZURE_RG" --location "$AZURE_LOCATION"

az appservice plan create \
  --name "${APP_SERVICE_NAME}-plan" \
  --resource-group "$AZURE_RG" \
  --is-linux \
  --sku B1

az webapp create \
  --name "$APP_SERVICE_NAME" \
  --resource-group "$AZURE_RG" \
  --plan "${APP_SERVICE_NAME}-plan" \
  --deployment-container-image-name "$ACR_LOGIN_SERVER/fast-mcp-server:latest"

az webapp config container set \
  --name "$APP_SERVICE_NAME" \
  --resource-group "$AZURE_RG" \
  --docker-custom-image-name "$ACR_LOGIN_SERVER/fast-mcp-server:latest" \
  --docker-registry-server-url "https://$ACR_LOGIN_SERVER" \
  --docker-registry-server-user "$ACR_USERNAME" \
  --docker-registry-server-password "$ACR_PASSWORD"

az webapp config appsettings set \
  --name "$APP_SERVICE_NAME" \
  --resource-group "$AZURE_RG" \
  --settings @azure/appsettings.json

az webapp config set \
  --name "$APP_SERVICE_NAME" \
  --resource-group "$AZURE_RG" \
  --startup-file "startup.sh"
