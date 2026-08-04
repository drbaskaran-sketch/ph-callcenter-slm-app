from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import random
import io
import wave
import math

app = FastAPI(
    title="Prashanth Hospitals Call Center & SLM API",
    version="1.1.0",
    description="Backend API with FCR Notification Bypass, Nullable Voice Paths, Multi-Branch Routing, SLA Governance, and SLM Mobile App"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY DATA STORES ---

BRANCHES = [
    {"id": "b1", "code": "KOL", "name": "Kolathur (Call Center Hub)", "city": "Chennai North", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 142},
    {"id": "b2", "code": "CHP", "name": "Chetpet", "city": "Central Chennai", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 98},
    {"id": "b3", "code": "VEL", "name": "Velachery", "city": "Chennai South", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 115},
    {"id": "b4", "code": "GUM", "name": "Gummidipoondi", "city": "Tiruvallur Suburbs", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 46},
    {"id": "b5", "code": "GUD", "name": "Guduvanchery", "city": "Chennai South Suburbs", "type": "HOSPITAL", "status": "UPCOMING", "leadsToday": 0},
    {"id": "b6", "code": "NAV", "name": "Navalur", "city": "OMR IT Corridor", "type": "HOSPITAL", "status": "UPCOMING", "leadsToday": 0},
    {"id": "b7", "code": "IVF", "name": "IVF Clinics Network", "city": "Multi-location", "type": "FERTILITY", "status": "ACTIVE", "leadsToday": 54},
]

SLMS = [
    {"id": "slm-101", "name": "Vijay Kumar", "department": "Cardiology", "branchCode": "KOL", "phone": "+91 98400 11111", "activeLeads": 8, "avgTatMins": 8.4, "status": "ON_DUTY", "score": 96.5},
    {"id": "slm-102", "name": "Anitha Ramesh", "department": "IVF & Fertility", "branchCode": "CHP", "phone": "+91 94440 22222", "activeLeads": 6, "avgTatMins": 6.2, "status": "ON_DUTY", "score": 98.0},
    {"id": "slm-103", "name": "Suresh Babu", "department": "Orthopedics", "branchCode": "VEL", "phone": "+91 98840 33333", "activeLeads": 11, "avgTatMins": 11.1, "status": "ON_DUTY", "score": 91.2},
    {"id": "slm-104", "name": "Priya Dharshini", "department": "Obstetrics & Gynecology", "branchCode": "GUM", "phone": "+91 97900 44444", "activeLeads": 4, "avgTatMins": 7.5, "status": "ON_DUTY", "score": 94.8},
    {"id": "slm-105", "name": "Rajesh Kannan", "department": "Nephrology & Urology", "branchCode": "KOL", "phone": "+91 98410 55555", "activeLeads": 7, "avgTatMins": 14.2, "status": "ON_DUTY", "score": 88.0},
]

ENQUIRIES = [
    {
        "id": "ENQ-2026-8801",
        "patientName": "Karthik Raja",
        "phone": "+91 98401 54321",
        "age": 48,
        "gender": "Male",
        "branch": "Kolathur (Call Center Hub)",
        "branchCode": "KOL",
        "department": "Cardiology",
        "doctorName": "Dr. S. Prashanth, Sr. Cardiologist",
        "enquiryType": "Coronary Angiogram Inquiry",
        "disposition": "APPOINTMENT_FIXED",
        "priority": "HIGH",
        "status": "SURGERY_FIXED",
        "assignedSLM": "Vijay Kumar (SLM Cardio)",
        "slmId": "slm-101",
        "timeAgo": "12 mins ago",
        "audioDuration": "2m 14s",
        "recordingUrl": "wav_8801.wav",
        "recording_path": "wav_8801.wav",
        "notes": "Patient reports mild exertional chest pain. Discussed Dr. Prashanth's Thursday OT slot. Fixed procedure appointment for Thursday 10:00 AM.",
        "remarks": "Fixed procedure appointment for Thursday 10:00 AM.",
        "nextFollowup": "2026-08-06 09:00 AM",
        "createdAt": "2026-08-04T05:33:00Z",
        "slaBreached": False,
        "escalatedToBranchHead": False
    },
    {
        "id": "ENQ-2026-8802",
        "patientName": "Meenakshi Sundaram",
        "phone": "+91 94440 12890",
        "age": 34,
        "gender": "Female",
        "branch": "Chetpet",
        "branchCode": "CHP",
        "department": "IVF & Fertility",
        "doctorName": "Dr. Geetha Haripriya, Lead Fertility Specialist",
        "enquiryType": "IVF Treatment Consultation",
        "disposition": "APPOINTMENT_FIXED",
        "priority": "URGENT",
        "status": "APPOINTMENT_CONFIRMED",
        "assignedSLM": "Anitha Ramesh (SLM Fertility)",
        "slmId": "slm-102",
        "timeAgo": "28 mins ago",
        "audioDuration": "4m 05s",
        "recordingUrl": "wav_8802.wav",
        "recording_path": "wav_8802.wav",
        "notes": "Enquired about 3rd cycle package tariffs. Scheduled in-person counseling at Chetpet IVF clinic on Friday 11:30 AM.",
        "remarks": "Scheduled in-person counseling at Chetpet IVF clinic.",
        "nextFollowup": "2026-08-05 04:00 PM",
        "createdAt": "2026-08-04T05:17:00Z",
        "slaBreached": False,
        "escalatedToBranchHead": False
    },
    {
        "id": "ENQ-2026-8803",
        "patientName": "Subramanian V.",
        "phone": "+91 98840 98765",
        "age": 62,
        "gender": "Male",
        "branch": "Velachery",
        "branchCode": "VEL",
        "department": "Orthopedics",
        "doctorName": "Dr. R. Balaji, Knee Replacement Specialist",
        "enquiryType": "Bilateral Knee Replacement Surgery",
        "disposition": "CALLBACK_REQUESTED",
        "priority": "HIGH",
        "status": "DOCTOR_CONSULTED",
        "assignedSLM": "Suresh Babu (SLM Ortho)",
        "slmId": "slm-103",
        "timeAgo": "45 mins ago",
        "audioDuration": "3m 40s",
        "recordingUrl": "wav_8803.wav",
        "recording_path": "wav_8803.wav",
        "notes": "Reviewed X-ray scans with Dr. Balaji. Shared surgical package cost estimate. Patient discussing insurance coverage with family.",
        "remarks": "Patient discussing insurance coverage with family.",
        "nextFollowup": "2026-08-04 11:00 AM",
        "createdAt": "2026-08-04T05:00:00Z",
        "slaBreached": False,
        "escalatedToBranchHead": False
    },
    {
        "id": "ENQ-2026-8804",
        "patientName": "Deepa Lakshmi",
        "phone": "+91 97900 11223",
        "age": 29,
        "gender": "Female",
        "branch": "Gummidipoondi",
        "branchCode": "GUM",
        "department": "Obstetrics & Gynecology",
        "doctorName": "Dr. N. Kausalya, Sr. Gynecologist",
        "enquiryType": "Maternity Package & Delivery",
        "disposition": "INFO_GIVEN",
        "priority": "MEDIUM",
        "status": "CONTACTED",
        "assignedSLM": "Priya Dharshini (SLM Gynae)",
        "slmId": "slm-104",
        "timeAgo": "1 hour ago",
        "audioDuration": "1m 55s",
        "recordingUrl": "wav_8804.wav",
        "recording_path": None,
        "notes": "Spoke with patient regarding luxury suite room booking. Sent hospital brochure on WhatsApp.",
        "remarks": "Sent hospital brochure on WhatsApp.",
        "nextFollowup": "2026-08-04 03:00 PM",
        "createdAt": "2026-08-04T04:45:00Z",
        "slaBreached": True,
        "escalatedToBranchHead": True
    }
]

# --- PYDANTIC SCHEMAS ---

class BranchCreateSchema(BaseModel):
    code: str = Field(..., example="GUD")
    name: str = Field(..., example="Guduvanchery Branch")
    city: str = Field(..., example="Chennai South Suburbs")
    type: str = Field("HOSPITAL", example="HOSPITAL")
    status: str = Field("ACTIVE", example="ACTIVE")

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

class EnquiryUpdateSchema(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None
    priority: Optional[str] = None
    nextFollowup: Optional[str] = None
    assignedSLM: Optional[str] = None

class XtendCallSimulationSchema(BaseModel):
    callerPhone: Optional[str] = None
    callerName: Optional[str] = None
    selectedBranchCode: Optional[str] = None
    department: Optional[str] = None
    disposition: Optional[str] = None

# Helper function to simulate FCM Push Notification (Bypassed for First Call Resolution / FCR)
def send_fcm_notification(enquiry_id: str, assigned_slm: str, title: str, body: str, disposition: str = None):
    if disposition in ["INFO_GIVEN", "COMPLAINT_RESOLVED"]:
        print(f"--> [FCR BYPASS] No push notification sent to SLM for Enquiry [{enquiry_id}] (First Call Resolution: {disposition}).")
        return False
    print(f"--> [FCM PUSH SENT] to SLM [{assigned_slm}] for Enquiry [{enquiry_id}]: {title}")
    return True

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {
        "organization": "Prashanth Hospitals",
        "tagline": "WE CARE FOR U",
        "service": "Call Center & SLM Mobile Platform API",
        "version": "1.1.0",
        "status": "Operational",
        "xtendDb2Hub": "Kolathur Call Center Central Hub",
        "activeEnquiriesCount": len(ENQUIRIES)
    }

# 1. BRANCHES
@app.get("/api/v1/branches")
def get_branches():
    return {"branches": BRANCHES, "total": len(BRANCHES)}

@app.post("/api/v1/branches")
def create_branch(payload: BranchCreateSchema):
    for b in BRANCHES:
        if b["code"].upper() == payload.code.upper():
            raise HTTPException(status_code=400, detail=f"Branch code {payload.code} already exists.")
    
    new_branch = {
        "id": f"b{len(BRANCHES)+1}",
        "code": payload.code.upper(),
        "name": payload.name,
        "city": payload.city,
        "type": payload.type,
        "status": payload.status,
        "leadsToday": 0
    }
    BRANCHES.append(new_branch)
    return {"message": "Branch created successfully", "branch": new_branch}

# 2. SERVICE LINE MANAGERS (SLMs)
@app.get("/api/v1/slms")
def get_slms():
    return {"slms": SLMS, "total": len(SLMS)}

# 3. ENQUIRIES & LEAD MANAGEMENT
@app.get("/api/v1/enquiries")
def get_enquiries(
    branchCode: Optional[str] = Query(None, description="Filter by branch code like KOL, CHP, VEL"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority URGENT/HIGH/MEDIUM"),
    search: Optional[str] = Query(None, description="Search patient name or phone")
):
    results = ENQUIRIES
    if branchCode:
        results = [e for e in results if e.get("branchCode", "").upper() == branchCode.upper()]
    if status:
        results = [e for e in results if e.get("status", "").upper() == status.upper()]
    if priority:
        results = [e for e in results if e.get("priority", "").upper() == priority.upper()]
    if search:
        q = search.lower()
        results = [e for e in results if q in e.get("patientName", "").lower() or q in e.get("phone", "").lower()]
    
    return {"enquiries": results, "total": len(results)}

@app.get("/api/v1/enquiries/{enquiry_id}")
def get_enquiry_by_id(enquiry_id: str):
    for enq in ENQUIRIES:
        if enq["id"] == enquiry_id:
            return {"enquiry": enq}
    raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")

@app.post("/api/v1/enquiries", status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate):
    # Mandatory Remarks Check when status is CLOSED or CONVERTED
    if payload.status in ["CLOSED", "CONVERTED"] and not payload.remarks:
        raise HTTPException(
            status_code=400,
            detail="Mandatory remarks required when creating enquiry with status CLOSED or CONVERTED."
        )

    enquiry_id = f"ENQ-2026-{random.randint(8800, 9999)}"
    matched_branch = next((b["name"] for b in BRANCHES if b["code"] == payload.branch_code.upper()), "Kolathur (Call Center Hub)")
    
    new_enquiry = {
        "id": enquiry_id,
        "patientName": payload.patient_name,
        "phone": payload.phone,
        "age": 42,
        "gender": "Unknown",
        "branch": matched_branch,
        "branchCode": payload.branch_code.upper(),
        "department": payload.department,
        "doctorName": "On-Duty Specialist",
        "enquiryType": payload.enquiry_type,
        "disposition": payload.disposition,
        "priority": "HIGH",
        "status": payload.status,
        "assignedSLM": payload.assigned_slm or "Auto-Routed SLM",
        "slmId": "slm-101",
        "timeAgo": "Just now",
        "audioDuration": "1m 30s" if payload.recording_path else "No audio recording",
        "recordingUrl": payload.recording_path,
        "recording_path": payload.recording_path,
        "notes": payload.remarks or "Newly created enquiry from XTEND DB2 sync.",
        "remarks": payload.remarks,
        "nextFollowup": "Tomorrow 10:00 AM",
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "slaBreached": False,
        "escalatedToBranchHead": False
    }

    ENQUIRIES.insert(0, new_enquiry)
    send_fcm_notification(enquiry_id, new_enquiry["assignedSLM"], "New Hospital Enquiry", f"Enquiry for {payload.patient_name}", payload.disposition)

    return {"message": "Enquiry created successfully", "enquiry": new_enquiry}

@app.post("/api/v1/xtend/simulate-call")
def simulate_xtend_call(payload: XtendCallSimulationSchema):
    new_id = f"ENQ-2026-{random.randint(8800, 9999)}"
    branch_code = payload.selectedBranchCode or random.choice(["KOL", "CHP", "VEL", "GUM", "IVF"])
    matched_branch = next((b["name"] for b in BRANCHES if b["code"] == branch_code), "Kolathur (Call Center Hub)")
    dept = payload.department or random.choice(["Cardiology", "IVF & Fertility", "Orthopedics", "Obstetrics & Gynecology"])
    
    assigned_slm = next((f"{s['name']} (SLM {s['department']})" for s in SLMS if s["branchCode"] == branch_code), "Vijay Kumar (SLM Cardio)")
    slm_obj = next((s for s in SLMS if s["branchCode"] == branch_code), SLMS[0])
    
    disposition = payload.disposition or "CALLBACK_REQUESTED"

    simulated = {
        "id": new_id,
        "patientName": payload.callerName or f"Patient {random.randint(100, 999)}",
        "phone": payload.callerPhone or f"+91 98401 {random.randint(10000, 99999)}",
        "age": random.randint(25, 75),
        "gender": random.choice(["Male", "Female"]),
        "branch": matched_branch,
        "branchCode": branch_code,
        "department": dept,
        "doctorName": "Duty Consultant Doctor",
        "enquiryType": f"{dept} General Enquiry",
        "disposition": disposition,
        "priority": random.choice(["URGENT", "HIGH", "MEDIUM"]),
        "status": "NEW",
        "assignedSLM": assigned_slm,
        "slmId": slm_obj["id"],
        "timeAgo": "Just now",
        "audioDuration": "2m 10s",
        "recordingUrl": "wav_8801.wav",
        "recording_path": "wav_8801.wav",
        "notes": f"Inbound call captured from XTEND DB2 at Kolathur Call Center Hub. Routed to {matched_branch} {dept}.",
        "remarks": None,
        "nextFollowup": (datetime.utcnow() + timedelta(hours=2)).strftime("%Y-%m-%d %I:%M %p"),
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "slaBreached": False,
        "escalatedToBranchHead": False
    }

    ENQUIRIES.insert(0, simulated)
    pushed = send_fcm_notification(new_id, assigned_slm, "XTEND Call Ingested", f"New call for {simulated['patientName']}", disposition)
    
    msg = "XTEND Call record ingested into PostgreSQL"
    if pushed:
        msg += " & pushed to SLM Mobile App via FCM"
    else:
        msg += " (FCM Push Bypassed - First Call Resolution)"

    return {
        "message": msg,
        "enquiry": simulated
    }

@app.patch("/api/v1/enquiries/{enquiry_id}")
def update_enquiry(enquiry_id: str, payload: EnquiryUpdateSchema):
    for enq in ENQUIRIES:
        if enq["id"] == enquiry_id:
            if payload.status:
                # Mandatory Remarks check for CLOSED or CONVERTED
                if payload.status in ["CLOSED", "CONVERTED"]:
                    submitted_remarks = payload.remarks if payload.remarks is not None else payload.notes
                    if not submitted_remarks or not submitted_remarks.strip():
                        raise HTTPException(
                            status_code=400,
                            detail=f"Mandatory resolution remarks required to update status to {payload.status}."
                        )
                enq["status"] = payload.status
            if payload.notes:
                enq["notes"] = payload.notes
            if payload.remarks:
                enq["remarks"] = payload.remarks
            if payload.priority:
                enq["priority"] = payload.priority
            if payload.nextFollowup:
                enq["nextFollowup"] = payload.nextFollowup
            if payload.assignedSLM:
                enq["assignedSLM"] = payload.assignedSLM
            return {"message": "Enquiry updated successfully", "enquiry": enq}
            
    raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")

@app.post("/api/v1/enquiries/{enquiry_id}/simulate-escalation")
def simulate_sla_escalation(enquiry_id: str):
    for enq in ENQUIRIES:
        if enq["id"] == enquiry_id:
            enq["slaBreached"] = True
            enq["escalatedToBranchHead"] = True
            return {
                "message": f"SLA Breach detected for {enquiry_id}! Escalated to Branch Head and Operations Director.",
                "enquiry": enq
            }
    raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")

# 4. LEADERSHIP ANALYTICS
@app.get("/api/v1/analytics/overview")
def get_analytics_overview():
    total_inquiries = 457
    avg_tat = 9.2
    surgeries = 127
    conversion = "27%"
    sla_breaches = len([e for e in ENQUIRIES if e.get("slaBreached")])
    
    return {
        "totalInquiriesToday": total_inquiries,
        "avgFirstResponseTatMins": avg_tat,
        "surgeriesAndSlotsFixed": surgeries,
        "conversionRate": conversion,
        "slaBreachAlerts": sla_breaches,
        "branchesCount": len(BRANCHES),
        "activeSlmsCount": len(SLMS)
    }

# 5. CALL RECORDING AUDIO PROXY (Generates real WAV audio stream on-the-fly)
@app.get("/api/v1/recordings/{filename}")
def get_call_audio(filename: str):
    sample_rate = 8000
    duration_secs = 3.0
    num_samples = int(sample_rate * duration_secs)
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            # Generate dual-tone hospital call sound (440Hz + 880Hz)
            t = i / sample_rate
            val = int(10000 * (math.sin(2 * math.pi * 440 * t) + 0.5 * math.sin(2 * math.pi * 880 * t)))
            val = max(-32768, min(32767, val))
            frames.extend(val.to_bytes(2, byteorder='little', signed=True))
            
        wav_file.writeframes(frames)
        
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="audio/wav")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
