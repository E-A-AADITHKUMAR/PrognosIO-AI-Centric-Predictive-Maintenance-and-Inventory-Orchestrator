#!/bin/bash

# --- Configuration ---
# Set these variables before running
PROJECT_ID="$(gcloud config get-value project)"
SERVICE_NAME="prognosio-api"
REGION="us-central1"
# ---------------------

echo "Starting deployment of PrognosIO API to Cloud Run in project: $PROJECT_ID"

# Navigate to the API source directory
cd cloud_run_api

# Deploy the service directly from source code
# This command automatically builds the container using the Dockerfile and deploys it.
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars PORT=8080 \
    --project $PROJECT_ID \
    --quiet

# Capture the deployed URL (critical for the ADK Agent)
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format "value(status.url)")

echo "=================================================================================="
echo "Deployment successful."
echo "API Endpoint URL: $SERVICE_URL"
echo "=================================================================================="
echo "ACTION REQUIRED: Update PROGNOSIO_API_URL in adk_agent/.env with the URL above."