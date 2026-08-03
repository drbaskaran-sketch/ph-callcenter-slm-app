from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Prashanth Hospitals Call Center & SLM API",
    version="1.0.0",
    description="Backend API for XTEND DB2 Sync, Multi-Branch Routing, and SLM Mobile App"
)

# Prashanth Hospitals Branch Master
BRANCHES = [
    {"id": "b1", "code": "KOL", "name": "Kolathur (Call Center Hub)", "type": "HOSPITAL", "status": "ACTIVE"},
    {"id": "b2", "code": "CHP", "name": "Chetpet", "type": "HOSPITAL", "status": "ACTIVE"},
    {"id": "b3", "code": "VEL", "name": "Velachery", "type": "HOSPITAL", "status": "ACTIVE"},
    {"id": "b4", "code": "GUM", "name": "Gummidipoondi", "type": "HOSPITAL", "status": "ACTIVE"},
    {"id": "b5", "code": "GUD", "name": "Guduvanchery", "type": "HOSPITAL", "status": "UPCOMING"},
    {"id": "b6", "code": "NAV", "name": "Navalur", "type": "HOSPITAL", "status": "UPCOMING"},
    {"id": "b7", "code": "IVF", "name": "IVF Clinics Network", "type": "FERTILITY", "status": "ACTIVE"},
]

@app.get("/")
def read_root():
    return {
        "organization": "Prashanth Hospitals",
        "tagline": "WE CARE FOR U",
        "service": "Call Center SLM Mobile App API",
        "status": "Operational"
    }

@app.get("/api/v1/branches")
def get_branches():
    return {"branches": BRANCHES}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
