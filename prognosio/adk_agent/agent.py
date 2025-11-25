import os
import requests
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from pydantic import BaseModel
from typing import List, Optional

# --- CONFIGURATION ---
# This loads the URL of your Cloud Run Service from the .env file
API_URL = os.environ.get("PROGNOSIO_API_URL")

# --- DATA MODELS (Must match Cloud Run API Schema) ---

class InventoryResult(BaseModel):
    item_id: str
    name: str
    stock: int
    location: str
    reorder_point: int
    status: str

class RiskResult(BaseModel):
    equipment_id: str
    name: str
    risk_score: int
    last_inspection: str
    recommendation: str

# --- TOOL FUNCTIONS (Connecting to Cloud Run) ---

def _handle_api_request(endpoint: str, params: dict = None, json_data: dict = None, method: str = "GET"):
    """Helper to handle API calls and error catching."""
    if not API_URL:
        return {"error": "Configuration Error: PROGNOSIO_API_URL is missing in .env file."}
    
    url = f"{API_URL.rstrip('/')}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=10)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to PrognosIO API: {str(e)}"}

def get_inventory_status_tool(item_id: str) -> InventoryResult:
    """
    Retrieves the current stock level, location, and status for a specific inventory part number (e.g., PN-123).
    Use this when the user asks about specific parts or stock availability.
    """
    data = _handle_api_request(f"/inventory/{item_id}")
    
    if "error" in data:
        return data # Return the error dict to the model so it can explain it
        
    return InventoryResult(**data)

def check_high_risk_equipment_tool(threshold: int = 70) -> List[RiskResult]:
    """
    Retrieves a list of equipment with a risk score above a specific threshold (0-100).
    Use this to identify machines that might fail soon. Default threshold is 70 if not specified.
    """
    data = _handle_api_request("/risks", params={"threshold": threshold})
    
    if isinstance(data, dict) and "error" in data:
        return [data] # Return error as a list item
        
    return [RiskResult(**item) for item in data]

def log_maintenance_event_tool(equipment_id: str, log_entry: str) -> dict:
    """
    Logs a maintenance action or inspection note for a specific equipment ID (e.g., EQ-001).
    Use this when the user says they fixed something, inspected something, or want to record a note.
    """
    payload = {"equipment_id": equipment_id, "log_entry": log_entry}
    return _handle_api_request("/log_maintenance", json_data=payload, method="POST")

# --- AGENT DEFINITION ---

# We define the agent with a specific model and the tools we created above.
root_agent = Agent(
    model="gemini-2.5-flash-preview-09-2025", 
    name="PrognosIO_Agent",
    instruction="""
    You are the PrognosIO Operations Assistant.
    Your goal is to help warehouse managers and technicians by retrieving real-time data from the facility system.

    RULES:
    1. ALWAYS check the available tools before answering. Do not guess inventory levels or risk scores.
    2. If a user asks about "stock" or "inventory" for a specific item, use 'get_inventory_status_tool'.
    3. If a user asks about "risks", "alerts", or "broken machines", use 'check_high_risk_equipment_tool'.
    4. If a user says they "fixed", "checked", or "repaired" something, use 'log_maintenance_event_tool' to save that record.
    5. If a tool returns an error (like "API URL missing"), explain to the user that the system is currently offline.
    
    Be concise, professional, and helpful.
    """,
    tools=[
        FunctionTool(func=get_inventory_status_tool),
        FunctionTool(func=check_high_risk_equipment_tool),
        FunctionTool(func=log_maintenance_event_tool),
    ]
)