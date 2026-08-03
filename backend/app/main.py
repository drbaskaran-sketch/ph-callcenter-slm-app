from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Prashanth Hospitals Call Center & SLM API",
    version="1.1.0",
    description="Backend API with FCR Notification Bypass, Nullable Voice Paths, and Mandatory Remarks Validation"
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

# In-memory DB store for demonstration
ENQUIRIES_DB = []

# Pydantic Schemas
class EnquiryCreate(BaseModel):
    patient_name: str
    phone: str
    branch_code: str
    department: str
    enquiry_type: str  # GENERAL_PRICING, PACKAGE_INFO, INFO_REQUEST, DOCTOR_APPOINTMENT, SURGERY_INQUIRY, COMPLAINT
    disposition: str    # INFO_GIVEN, COMPLAINT_RESOLVED, APPOINTMENT_FIXED, CALLBACK_REQUESTED
    status: str = "NEW" # NEW, ASSIGNED, CONTACTED, DOCTOR_CONSULTED, SURGERY_FIXED, CONVERTED, CLOSED
    assigned_slm: Optional[str] = None
    recording_path: Optional[str] = None  # Nullable Voice Path from XTEND DB2
    remarks: Optional[str] = None         # Mandatory when status is CLOSED or CONVERTED

class StatusUpdate(BaseModel):
    status: str
    remarks: str  # Mandatory remarks for closing/archiving

# Helper function to simulate FCM Push Notification
def send_fcm_notification(enquiry_id: str, assigned_slm: str, title: str, body: str):
    print(f"--> FCM PUSH SENT to SLM [{assigned_slm}] for Enquiry [{enquiry_id}]: {title}")
    return True

@app.get("/")
def read_root():
    return {
        "organization": "Prashanth Hospitals",
        "tagline": "WE CARE FOR U",
        "service": "Call Center & SLM Mobile Platform API",
        "version": "1.1.0",
        "status": "Operational"
    }

@app.get("/api/v1/branches")
def get_branches():
    return {"branches": BRANCHES}

@app.post("/api/v1/enquiries", status_code=status.HTTP_201_CREATED)
def create_enquiry(enquiry: EnquiryCreate):
    # Rule 1: Mandatory Remarks Validation for CLOSED or CONVERTED status (FCR / Archive)
    resolved_statuses = ["CLOSED", "CONVERTED"]
    if enquiry.status in resolved_statuses and (not enquiry.remarks or not enquiry.remarks.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory 'remarks' field is required before saving or archiving an enquiry as CLOSED or CONVERTED."
        )

    enquiry_id = f"ENQ-2026-{len(ENQUIRIES_DB) + 9001}"
    record = {
        "id": enquiry_id,
        "patient_name": enquiry.patient_name,
        "phone": enquiry.phone,
        "branch_code": enquiry.branch_code,
        "department": enquiry.department,
        "enquiry_type": enquiry.enquiry_type,
        "disposition": enquiry.disposition,
        "status": enquiry.status,
        "assigned_slm": enquiry.assigned_slm,
        "recording_path": enquiry.recording_path, # Nullable: defaults to None if XTEND audio delayed
        "remarks": enquiry.remarks,
        "created_at": datetime.now().isoformat(),
        "fcm_notification_sent": False,
        "notification_status": "NONE"
    }

    # Rule 2: First-Contact Resolution (FCR) Push Notification Bypass Check
    if enquiry.status in resolved_statuses:
        # FCR Bypass: Agent resolved on call immediately. Suppress FCM push to SLM app.
        record["fcm_notification_sent"] = False
        record["notification_status"] = "SUPPRESSED_FCR_BYPASS"
    else:
        # Active lead assigned to SLM: Trigger FCM push alert
        if enquiry.assigned_slm:
            send_fcm_notification(
                enquiry_id=enquiry_id,
                assigned_slm=enquiry.assigned_slm,
                title=f"New Patient Lead: {enquiry.enquiry_type}",
                body=f"Patient {enquiry.patient_name} in {enquiry.department} ({enquiry.branch_code})"
            )
            record["fcm_notification_sent"] = True
            record["notification_status"] = "DISPATCHED"

    ENQUIRIES_DB.append(record)
    return {"message": "Enquiry processed successfully", "enquiry": record}

@app.patch("/api/v1/enquiries/{enquiry_id}/status")
def update_enquiry_status(enquiry_id: str, update: StatusUpdate):
    # Rule 3: Mandatory Closing Remarks Validation on Status Update
    resolved_statuses = ["CLOSED", "CONVERTED"]
    if update.status in resolved_statuses and (not update.remarks or not update.remarks.strip()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mandatory 'remarks' field is required before updating status to CLOSED or CONVERTED."
        )

    for record in ENQUIRIES_DB:
        if record["id"] == enquiry_id:
            record["status"] = update.status
            record["remarks"] = update.remarks
            record["updated_at"] = datetime.now().isoformat()
            return {"message": f"Enquiry {enquiry_id} status updated to {update.status}", "enquiry": record}
            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")

@app.get("/api/v1/enquiries")
def list_enquiries():
    return {"count": len(ENQUIRIES_DB), "enquiries": ENQUIRIES_DB}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
