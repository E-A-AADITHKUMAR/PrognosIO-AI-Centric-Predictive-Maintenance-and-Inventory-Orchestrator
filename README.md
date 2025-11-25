# PrognosIO: AI-Centric Predictive Maintenance and Inventory Orchestrator

## Overview

PrognosIO is an AI Agent system designed to revolutionize industrial asset and inventory management by shifting maintenance from reactive to predictive. Built on the Google Agent Development Kit (ADK) and Google Cloud Run, the system allows managers and technicians to interact with operational data, high-risk alerts (from a conceptual Vertex AI model), and log maintenance actions using simple natural language.

The core innovation is using the Gemini LLM via ADK to orchestrate calls to a custom, serverless API (hosted on Cloud Run), demonstrating a robust, production-ready AI solution.

## Key Use Cases

High-Risk Triage: Instantly query the system for equipment likely to fail (Risk Score > 70).

Inventory Check: Get real-time stock levels and location for critical parts (e.g., "Check stock for PN-123").

Maintenance Logging: Record actions taken directly via natural language (e.g., "Log that I replaced the motor on EQ-001").

## Architecture and Components

The system implements a strong separation of concerns, mapping directly to the GCP Reference Architecture:

## Architecture Layers

AI & Context (ADK Agent): This component (adk_agent/) orchestrates the entire flow. It uses Gemini's function calling capability to translate user intent (e.g., "Check stock") into specific API calls (Tools) required by the back-end system.

Application Layer (Cloud Run Microservice): The lightweight FastAPI API (cloud_run_api/) is the central integration point. It hosts the core tool endpoints (e.g., /inventory/{id}) that the ADK Agent executes. This is the glue between the AI and the data.

Data & Storage (Cloud SQL / BigQuery): This layer is simulated in the FastAPI code for the demo. In a production environment, Cloud SQL holds transactional data (Inventory and Risk Scores), while BigQuery stores high-volume sensor data (for ML training).

Processing (Vertex AI - Conceptual): Conceptually, this pipeline processes BigQuery data and updates the risk_score values that are retrieved by the API.

## Setup and Deployment Guide

### Prerequisites

GCP Project: A valid Google Cloud Project with billing enabled.

Tools: gcloud CLI installed and authenticated (or use Cloud Shell Editor).

API Key: A Gemini API Key from Google AI Studio.

Step 1: Clone and Configure

Unzip/Access: Ensure the prognosio folder is extracted in your local or Cloud Shell environment.

API Key: Open adk_agent/.env and replace the placeholder with your actual Gemini API Key.

Agent Prep: Install the necessary dependency for the agent's environment handling (python-dotenv must be added to adk_agent/requirements.txt).

# Ensure python-dotenv is included and install dependencies
pip install -r adk_agent/requirements.txt


Step 2: Deploy the Cloud Run API

Navigate to the API Source:

cd cloud_run_api


Run Deployment:

gcloud run deploy prognosio-api \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated


CRITICAL: Capture the URL. When deployment succeeds, copy the Service URL (e.g., https://prognosio-api-...a.run.app).

Step 3: Connect the Agent and Run

Update Config: Go back to adk_agent/.env and replace the placeholder URL with the live Service URL you copied in Step 2.

Run the Agent:

cd ../adk_agent  # Go back to the agent directory
python agent.py


## Sample Agent Prompts

The agent is now live and fully connected to your cloud service. Test its functionality with:

Check inventory status for PN-123.

Are there any pieces of equipment with a risk score over 75?

Log that I replaced the main motor on Crane Beta (EQ-002) today.

## Scoring Checklist and Artifacts

The project directly addresses all assessment criteria through the following deliverables:

Project Fulfillment Breakdown

Cloud Run Usage: The core microservice (prognosio-api) is containerized and deployed on Cloud Run, providing the REST endpoints for the ADK Agent's tools.

Artifacts: cloud_run_api/Dockerfile, deploy.sh

GCP Database Usage: The project demonstrates hybrid data storage needs, simulating both Cloud SQL (transactional inventory) and the architecture necessary for BigQuery (ML data source).

Artifacts: Data Simulation in cloud_run_api/main.py, Architecture Documentation.

Google's AI Usage: The ADK Agent utilizes the Gemini LLM for intelligent intent recognition and dynamic Function Calling to trigger the correct Cloud Run tools.

Artifacts: adk_agent/agent.py
