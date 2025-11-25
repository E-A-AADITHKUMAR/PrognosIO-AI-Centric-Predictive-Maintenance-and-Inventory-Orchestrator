from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn

# Initialize the FastAPI application
app = FastAPI(
    title="PrognosIO Tool API",
    description="API for Inventory and Predictive Maintenance Tools",
    version="1.0.0"
)

# --- SIMULATED DATA STORE (Data Layer) ---
# In a real production environment, you would replace these dictionaries 
# with database connections (e.g., using SQLAlchemy or google-cloud-bigquery).

# Inventory Data: Key = Part Number
INVENTORY_DATA = {
    "PN-123": {"name": "Hydraulic Pump", "stock": 4, "location": "Aisle 3", "reorder_point": 5},
    "PN-456": {"name": "Forklift Wheel", "stock": 15, "location": "Aisle 10", "reorder_point": 10},
    "PN-789": {"name": "Sensor Filter", "stock": 20, "location": "Shelf B2", "reorder_point": 20},
    "PN-101": {"name": "Conveyor Belt", "stock": 8, "location": "Aisle 4", "reorder_point": 5},
    "PN-999": {"name": "Control Module", "stock": 2, "location": "Secure Cage 1", "reorder_point": 2},
}

# Risk Data: Key = Equipment ID
# These scores would typically come from your Vertex AI Pipeline
RISK_DATA = {
    "EQ-001": {"name": "Forklift Alpha", "risk_score": 92, "last_inspection": "2025-11-20"},
    "EQ-002": {"name": "Crane Beta", "risk_score": 45, "last_inspection": "2025-11-15"},
    "EQ-003": {"name": "Conveyor Gamma", "risk_score": 78, "last_inspection": "2025-11-24"},
    "EQ-004": {"name": "CNC Mill", "risk_score": 21, "last_inspection": "2025-11-22"},
    "EQ-005": {"name": "Robotic Arm Z", "risk_score": 88, "last_inspection": "2025-10-30"},
}

# --- PYDANTIC MODELS (Data Validation & Schema) ---

class InventoryStatus(BaseModel):
    """Schema for returning inventory stock information."""
    item_id: str
    name: str
    stock: int
    location: str
    reorder_point: int
    status: str  # e.g., "In Stock", "Low Stock"

class RiskScore(BaseModel):
    """Schema for returning equipment risk predictions."""
    equipment_id: str
    name: str
    risk_score: int
    last_inspection: str
    recommendation: str

class MaintenanceLog(BaseModel):
    """Schema for receiving maintenance log data."""
    equipment_id: str
    log_entry: str
    timestamp: Optional[str] = None

# --- API ENDPOINTS (Tools for ADK Agent) ---

@app.get("/")
def root():
    """Health check endpoint to verify the service is running."""
    return {"status": "PrognosIO API is running", "version": "1.0.0"}

@app.get("/inventory/{item_id}", response_model=InventoryStatus)
def get_inventory_status_api(item_id: str):
    """
    Retrieves the current stock and location for a specific inventory part number.
    """
    # Normalize ID to uppercase
    clean_id = item_id.upper().strip()
    data = INVENTORY_DATA.get(clean_id)
    
    if data:
        # Determine status based on reorder point
        status = "Low Stock" if data['stock'] <= data['reorder_point'] else "In Stock"
        return InventoryStatus(item_id=clean_id, status=status, **data)
    
    # Return a structured "Not Found" object rather than a 404 error,
    # so the Agent can gracefully tell the user "I couldn't find that item."
    return InventoryStatus(
        item_id=clean_id, 
        name="Not Found", 
        stock=0, 
        location="Unknown", 
        reorder_point=0,
        status="Unknown"
    )

@app.get("/risks", response_model=List[RiskScore])
def get_high_risk_equipment_api(threshold: int = 70):
    """
    Retrieves a list of all equipment with a predictive failure risk score above a given threshold.
    """
    high_risk_equipment = []
    
    for eq_id, data in RISK_DATA.items():
        if data['risk_score'] >= threshold:
            # Generate a basic recommendation based on severity
            if data['risk_score'] >= 90:
                rec = "CRITICAL: Immediate shutdown and inspection required."
            else:
                rec = "WARNING: Schedule maintenance within 72 hours."
                
            high_risk_equipment.append(
                RiskScore(equipment_id=eq_id, recommendation=rec, **data)
            )
    
    return high_risk_equipment

@app.post("/log_maintenance")
def log_maintenance_event_api(log: MaintenanceLog):
    """
    Logs a maintenance activity entry for an equipment ID.
    """
    # In a real app, you would INSERT this data into Cloud SQL here.
    print(f"--- LOGGING TO DATABASE ---")
    print(f"Equipment: {log.equipment_id}")
    print(f"Action: {log.log_entry}")
    print(f"---------------------------")
    
    # Simulate a successful database transaction
    return {
        "status": "success", 
        "message": f"Maintenance log recorded for {log.equipment_id}.",
        "logged_data": log
    }

# --- SERVER ENTRY POINT ---
if __name__ == "__main__":
    # Cloud Run will define the PORT environment variable.
    # If running locally, it defaults to 8080.
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting PrognosIO API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
