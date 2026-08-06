from fastapi import FastAPI, HTTPException, Query, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import random
import io
import wave
import math
import csv
import jwt
import bcrypt

try:
    from .config import settings
except ImportError:
    from config import settings

app = FastAPI(
    title="Prashanth Hospitals Call Center & SLM API",
    version="1.1.0",
    description="Backend API with FCR Notification Bypass, Nullable Voice Paths, Multi-Branch Routing, SLA Governance, and SLM Mobile App"
)

# Enable CORS for frontend integration. Reads settings.CORS_ORIGINS (env
# CORS_ORIGINS) instead of a hardcoded "*" — a wildcard combined with
# allow_credentials=True is what browsers/some CORS specs treat as invalid,
# and it defeated the point of locking origins down for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SEED DATA (loaded into Postgres on first boot only — see init_db) ---

SEED_BRANCHES = [
    {"id": "b1", "code": "KOL", "name": "Kolathur (Call Center Hub)", "city": "Chennai North", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 142},
    {"id": "b2", "code": "CHP", "name": "Chetpet", "city": "Central Chennai", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 98},
    {"id": "b3", "code": "VEL", "name": "Velachery", "city": "Chennai South", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 115},
    {"id": "b4", "code": "GUM", "name": "Gummidipoondi", "city": "Tiruvallur Suburbs", "type": "HOSPITAL", "status": "ACTIVE", "leadsToday": 46},
    {"id": "b5", "code": "GUD", "name": "Guduvanchery", "city": "Chennai South Suburbs", "type": "HOSPITAL", "status": "UPCOMING", "leadsToday": 0},
    {"id": "b6", "code": "NAV", "name": "Navalur", "city": "OMR IT Corridor", "type": "HOSPITAL", "status": "UPCOMING", "leadsToday": 0},
    {"id": "b7", "code": "IVF", "name": "IVF Clinics Network", "city": "Multi-location", "type": "FERTILITY", "status": "ACTIVE", "leadsToday": 54},
]

SEED_SLMS = [
    {"id": "slm-101", "name": "Vijay Kumar", "department": "Cardiology", "branchCode": "KOL", "phone": "+91 98400 11111", "activeLeads": 8, "avgTatMins": 8.4, "status": "ON_DUTY", "score": 96.5},
    {"id": "slm-102", "name": "Anitha Ramesh", "department": "IVF & Fertility", "branchCode": "CHP", "phone": "+91 94440 22222", "activeLeads": 6, "avgTatMins": 6.2, "status": "ON_DUTY", "score": 98.0},
    {"id": "slm-103", "name": "Suresh Babu", "department": "Orthopedics", "branchCode": "VEL", "phone": "+91 98840 33333", "activeLeads": 11, "avgTatMins": 11.1, "status": "ON_DUTY", "score": 91.2},
    {"id": "slm-104", "name": "Priya Dharshini", "department": "Obstetrics & Gynecology", "branchCode": "GUM", "phone": "+91 97900 44444", "activeLeads": 4, "avgTatMins": 7.5, "status": "ON_DUTY", "score": 94.8},
    {"id": "slm-105", "name": "Rajesh Kannan", "department": "Nephrology & Urology", "branchCode": "KOL", "phone": "+91 98410 55555", "activeLeads": 7, "avgTatMins": 14.2, "status": "ON_DUTY", "score": 88.0},
]

# Enquiries now live in PostgreSQL (see models.Enquiry / models.EnquiryAction).
# SEED_ENQUIRIES below is only used to populate the table the first time it's
# empty, so a fresh deployment still boots with representative demo data.
SEED_ENQUIRIES = [
    {
        "id": "ENQ-2026-8801",
        "patient_name": "Karthik Raja",
        "phone": "+91 98401 54321",
        "age": 48,
        "gender": "Male",
        "branch": "Kolathur (Call Center Hub)",
        "branch_code": "KOL",
        "department": "Cardiology",
        "doctor_name": "Dr. S. Prashanth, Sr. Cardiologist",
        "enquiry_type": "Coronary Angiogram Inquiry",
        "disposition": "APPOINTMENT_FIXED",
        "priority": "HIGH",
        "status": "SURGERY_FIXED",
        "assigned_slm": "Vijay Kumar (SLM Cardio)",
        "slm_id": "slm-101",
        "age_offset_mins": 12,
        "audio_duration": "2m 14s",
        "recording_url": "wav_8801.wav",
        "recording_path": "wav_8801.wav",
        "notes": "Patient reports mild exertional chest pain. Discussed Dr. Prashanth's Thursday OT slot. Fixed procedure appointment for Thursday 10:00 AM.",
        "remarks": "Fixed procedure appointment for Thursday 10:00 AM.",
        "next_followup": "2026-08-06 09:00 AM",
        "sla_breached": False,
        "escalated_to_branch_head": False,
        "actions": [
            ("Inbound Call Connected at Kolathur Hub", "XTEND IVR"),
            ("Coronary angiogram inquiry registered", "Agent #104"),
            ("Dr. Prashanth OT slot fixed for Thursday 10:00 AM", "Vijay Kumar (SLM Cardio)"),
        ],
    },
    {
        "id": "ENQ-2026-8802",
        "patient_name": "Meenakshi Sundaram",
        "phone": "+91 94440 12890",
        "age": 34,
        "gender": "Female",
        "branch": "Chetpet",
        "branch_code": "CHP",
        "department": "IVF & Fertility",
        "doctor_name": "Dr. Geetha Haripriya, Lead Fertility Specialist",
        "enquiry_type": "IVF Treatment Consultation",
        "disposition": "APPOINTMENT_FIXED",
        "priority": "URGENT",
        "status": "APPOINTMENT_CONFIRMED",
        "assigned_slm": "Anitha Ramesh (SLM Fertility)",
        "slm_id": "slm-102",
        "age_offset_mins": 28,
        "audio_duration": "4m 05s",
        "recording_url": "wav_8802.wav",
        "recording_path": "wav_8802.wav",
        "notes": "Enquired about 3rd cycle package tariffs. Scheduled in-person counseling at Chetpet IVF clinic on Friday 11:30 AM.",
        "remarks": "Scheduled in-person counseling at Chetpet IVF clinic.",
        "next_followup": "2026-08-05 04:00 PM",
        "sla_breached": False,
        "escalated_to_branch_head": False,
        "actions": [
            ("Inbound Call Connected at Chetpet Branch", "XTEND IVR"),
            ("3rd cycle IVF package tariff inquiry registered", "Agent #211"),
            ("In-person counseling scheduled for Friday 11:30 AM", "Anitha Ramesh (SLM Fertility)"),
        ],
    },
    {
        "id": "ENQ-2026-8803",
        "patient_name": "Subramanian V.",
        "phone": "+91 98840 98765",
        "age": 62,
        "gender": "Male",
        "branch": "Velachery",
        "branch_code": "VEL",
        "department": "Orthopedics",
        "doctor_name": "Dr. R. Balaji, Knee Replacement Specialist",
        "enquiry_type": "Bilateral Knee Replacement Surgery",
        "disposition": "CALLBACK_REQUESTED",
        "priority": "HIGH",
        "status": "DOCTOR_CONSULTED",
        "assigned_slm": "Suresh Babu (SLM Ortho)",
        "slm_id": "slm-103",
        "age_offset_mins": 45,
        "audio_duration": "3m 40s",
        "recording_url": "wav_8803.wav",
        "recording_path": "wav_8803.wav",
        "notes": "Reviewed X-ray scans with Dr. Balaji. Shared surgical package cost estimate. Patient discussing insurance coverage with family.",
        "remarks": "Patient discussing insurance coverage with family.",
        "next_followup": "2026-08-04 11:00 AM",
        "sla_breached": False,
        "escalated_to_branch_head": False,
        "actions": [
            ("Inbound Call Connected at Velachery Branch", "XTEND IVR"),
            ("Bilateral knee replacement inquiry registered", "Agent #087"),
            ("X-ray scans reviewed with Dr. Balaji, cost estimate shared", "Suresh Babu (SLM Ortho)"),
        ],
    },
    {
        "id": "ENQ-2026-8804",
        "patient_name": "Deepa Lakshmi",
        "phone": "+91 97900 11223",
        "age": 29,
        "gender": "Female",
        "branch": "Gummidipoondi",
        "branch_code": "GUM",
        "department": "Obstetrics & Gynecology",
        "doctor_name": "Dr. N. Kausalya, Sr. Gynecologist",
        "enquiry_type": "Maternity Package & Delivery",
        "disposition": "INFO_GIVEN",
        "priority": "MEDIUM",
        "status": "CONTACTED",
        "assigned_slm": "Priya Dharshini (SLM Gynae)",
        "slm_id": "slm-104",
        "age_offset_mins": 60,
        "audio_duration": "1m 55s",
        "recording_url": "wav_8804.wav",
        "recording_path": None,
        "notes": "Spoke with patient regarding luxury suite room booking. Sent hospital brochure on WhatsApp.",
        "remarks": "Sent hospital brochure on WhatsApp.",
        "next_followup": "2026-08-04 03:00 PM",
        "sla_breached": True,
        "escalated_to_branch_head": True,
        "actions": [
            ("Inbound Call Connected at Gummidipoondi Branch", "XTEND IVR"),
            ("Maternity package & delivery inquiry registered", "Agent #056"),
            ("Hospital brochure sent on WhatsApp", "Priya Dharshini (SLM Gynae)"),
            ("First Response SLA breached (>15 mins) — escalated to Branch Head", "SLA Monitor"),
        ],
    },
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
    disposition: Optional[str] = None
    notes: Optional[str] = None
    remarks: Optional[str] = None
    priority: Optional[str] = None
    nextFollowup: Optional[str] = None
    assignedSLM: Optional[str] = None

class ActionCreateSchema(BaseModel):
    action: str
    performedBy: Optional[str] = "SLM Agent"

class XtendCallSimulationSchema(BaseModel):
    callerPhone: Optional[str] = None
    callerName: Optional[str] = None
    selectedBranchCode: Optional[str] = None
    department: Optional[str] = None
    disposition: Optional[str] = None

class UserCreateSchema(BaseModel):
    username: str
    password: str
    fullName: Optional[str] = None
    email: Optional[str] = None
    role: str = "SLM"  # ADMIN, SUPERVISOR, SLM, BRANCH_HEAD
    branchCode: Optional[str] = "ALL"
    slmId: Optional[str] = None

class UserUpdateSchema(BaseModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    branchCode: Optional[str] = None
    slmId: Optional[str] = None
    status: Optional[str] = None

class UserPasswordResetSchema(BaseModel):
    newPassword: str

class SLMCreateSchema(BaseModel):
    name: str
    department: str
    branchCode: str
    phone: str
    status: str = "ON_DUTY"
    createUserAccount: Optional[bool] = False
    username: Optional[str] = None
    password: Optional[str] = None

class SLMUpdateSchema(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    branchCode: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    score: Optional[float] = None

class HISBookSlotSchema(BaseModel):
    enquiryId: str
    doctorName: str
    appointmentDate: str  # YYYY-MM-DD
    slotTime: str         # e.g., 10:00 AM
    patientUhid: Optional[str] = None
    remarks: Optional[str] = None

class HISPrebookSurgerySchema(BaseModel):
    enquiryId: str
    doctorName: str
    procedureName: str
    proposedSurgeryDate: str
    otRoom: Optional[str] = "OT-1 (Main Surgical Suite)"
    remarks: Optional[str] = None

class NotificationDispatchSchema(BaseModel):
    enquiryId: str
    channel: str  # WHATSAPP, SMS, EMAIL
    templateType: str  # APPOINTMENT_CONFIRMATION, SURGERY_PREBOOK, FOLLOWUP_REMINDER, GENERAL_INFO
    recipientPhone: str
    customMessage: Optional[str] = None

# Helper function to simulate FCM Push Notification (Bypassed for First Call Resolution / FCR)
def send_fcm_notification(enquiry_id: str, assigned_slm: str, title: str, body: str, disposition: str = None):
    if disposition in ["INFO_GIVEN", "COMPLAINT_RESOLVED"]:
        print(f"--> [FCR BYPASS] No push notification sent to SLM for Enquiry [{enquiry_id}] (First Call Resolution: {disposition}).")
        return False
    print(f"--> [FCM PUSH SENT] to SLM [{assigned_slm}] for Enquiry [{enquiry_id}]: {title}")
    return True

# --- POSTGRESQL-BACKED DATA STORES ---
try:
    from .database import db_manager, get_db_session
    from .models import Enquiry, EnquiryAction, Branch, SLM, User
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database import db_manager, get_db_session
    from models import Enquiry, EnquiryAction, Branch, SLM, User


# --- AUTH (JWT bearer tokens) ---
# The API previously had no authentication at all — every endpoint,
# including patient names/phones/call recordings, was reachable by anyone
# on the network. This adds a minimal but real JWT auth layer: a single
# ADMIN-role account (seeded on first boot, see init_db) protects every
# route except "/" and the login endpoint itself.
security = HTTPBearer()
JWT_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
) -> "User":
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired, please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    return user


class LoginSchema(BaseModel):
    username: str
    password: str


def serialize_user(u: "User") -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "fullName": u.full_name or u.username,
        "email": u.email,
        "role": u.role or "ADMIN",
        "branchCode": u.branch_code or "ALL",
        "slmId": u.slm_id,
        "status": u.status or "ACTIVE",
        "createdAt": (u.created_at.isoformat() + "Z") if u.created_at else None,
    }

@app.post("/api/v1/auth/login")
def login(payload: LoginSchema, db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    token = create_access_token(user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expiresInMinutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "user": serialize_user(user),
    }


def time_ago(dt: datetime) -> str:
    """Human-readable elapsed time since dt (UTC), e.g. '12 mins ago'."""
    if not dt:
        return "Unknown"
    secs = max(0, (datetime.utcnow() - dt).total_seconds())
    if secs < 60:
        return "Just now"
    mins = int(secs // 60)
    if mins < 60:
        return f"{mins} min{'s' if mins != 1 else ''} ago"
    hours = int(mins // 60)
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = int(hours // 24)
    return f"{days} day{'s' if days != 1 else ''} ago"


def serialize_enquiry(enq: "Enquiry") -> dict:
    """Maps the DB row (+ its registered actions) to the JSON shape the
    frontend already expects, so no frontend changes are required."""
    return {
        "id": enq.id,
        "patientName": enq.patient_name,
        "phone": enq.phone,
        "age": enq.age,
        "gender": enq.gender,
        "branch": enq.branch,
        "branchCode": enq.branch_code,
        "department": enq.department,
        "doctorName": enq.doctor_name,
        "enquiryType": enq.enquiry_type,
        "disposition": enq.disposition,
        "priority": enq.priority,
        "status": enq.status,
        "assignedSLM": enq.assigned_slm,
        "slmId": enq.slm_id,
        "timeAgo": time_ago(enq.created_at),
        "audioDuration": enq.audio_duration,
        "recordingUrl": enq.recording_url,
        "recording_path": enq.recording_path,
        "notes": enq.notes,
        "remarks": enq.remarks,
        "nextFollowup": enq.next_followup,
        "callStartTime": enq.call_start_time,
        "callEndTime": enq.call_end_time,
        "createdAt": (enq.created_at.isoformat() + "Z") if enq.created_at else None,
        "updatedAt": (enq.updated_at.isoformat() + "Z") if enq.updated_at else None,
        "slaBreached": enq.sla_breached,
        "escalatedToBranchHead": enq.escalated_to_branch_head,
        "patientUhid": enq.patient_uhid,
        "hisBookingId": enq.his_booking_id,
        "hisSyncStatus": enq.his_sync_status or "PENDING",
        "hisSyncedAt": (enq.his_synced_at.isoformat() + "Z") if enq.his_synced_at else None,
        "registeredActions": [
            {
                "timestamp": a.timestamp.strftime("%H:%M:%S") if a.timestamp else None,
                "action": a.action,
                "performedBy": a.performed_by,
            }
            for a in enq.actions
        ],
    }


def serialize_branch(b: "Branch") -> dict:
    return {
        "id": b.id, "code": b.code, "name": b.name, "city": b.city,
        "type": b.type, "status": b.status, "leadsToday": b.leads_today,
    }


def serialize_slm(s: "SLM") -> dict:
    return {
        "id": s.id, "name": s.name, "department": s.department, "branchCode": s.branch_code,
        "phone": s.phone, "activeLeads": s.active_leads, "avgTatMins": s.avg_tat_mins,
        "status": s.status, "score": s.score,
    }


def log_action(db: Session, enquiry_id: str, action: str, performed_by: str, when: datetime = None):
    db.add(EnquiryAction(
        enquiry_id=enquiry_id,
        timestamp=when or datetime.utcnow(),
        action=action,
        performed_by=performed_by or "System",
    ))


def generate_unique_enquiry_id(db: Session, max_attempts: int = 20) -> str:
    """Random 4-digit IDs (ENQ-2026-8800..9999) only cover 1200 values, so
    collisions are common under repeated calls/tests. The old in-memory list
    silently tolerated duplicate ids; Postgres's primary key correctly
    rejects them, so generate against a live uniqueness check instead."""
    for _ in range(max_attempts):
        candidate = f"ENQ-2026-{random.randint(8800, 9999)}"
        if not db.query(Enquiry.id).filter(Enquiry.id == candidate).first():
            return candidate
    # Space exhausted (extremely unlikely) — widen to a 5-digit suffix.
    return f"ENQ-2026-{random.randint(10000, 99999)}"


STARTUP_LOCK_ID = 727271  # Arbitrary constant Postgres advisory-lock key


@app.on_event("startup")
def init_db():
    """Create tables (if missing) and seed demo data on first boot only.

    Uvicorn runs 4 worker processes that each fire this startup hook at
    roughly the same time. A Postgres session-level advisory lock serializes
    them through table creation + seeding — without it, concurrent CREATE
    TABLE / INSERT statements raced each other and crashed a worker on boot.
    """
    db = db_manager.SessionLocal()
    try:
        db.execute(text(f"SELECT pg_advisory_lock({STARTUP_LOCK_ID})"))
        Enquiry.metadata.create_all(bind=db_manager.engine)

        # Auto-migrate new columns for users table if upgrading from prior schema
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR;"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR;"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_code VARCHAR DEFAULT 'ALL';"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS slm_id VARCHAR;"))
        db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'ACTIVE';"))

        db.execute(text("ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS patient_uhid VARCHAR;"))
        db.execute(text("ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS his_booking_id VARCHAR;"))
        db.execute(text("ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS his_sync_status VARCHAR DEFAULT 'PENDING';"))
        db.execute(text("ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS his_synced_at TIMESTAMP;"))
        db.commit()

        if db.query(User).count() == 0:
            db.add(User(
                username=settings.ADMIN_USERNAME,
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                role="ADMIN",
            ))
            db.commit()
            if settings.ADMIN_PASSWORD == "ChangeMe123!":
                print(f"⚠️  Seeded default admin user '{settings.ADMIN_USERNAME}' with the DEFAULT password — "
                      f"set ADMIN_PASSWORD in .env and redeploy before any real use.")
            else:
                print(f"✅ Seeded admin user '{settings.ADMIN_USERNAME}' into PostgreSQL.")

        if db.query(Branch).count() == 0:
            for seed in SEED_BRANCHES:
                db.add(Branch(
                    id=seed["id"], code=seed["code"], name=seed["name"], city=seed["city"],
                    type=seed["type"], status=seed["status"], leads_today=seed["leadsToday"],
                ))
            db.commit()
            print(f"✅ Seeded {len(SEED_BRANCHES)} initial branches into PostgreSQL.")

        if db.query(SLM).count() == 0:
            for seed in SEED_SLMS:
                db.add(SLM(
                    id=seed["id"], name=seed["name"], department=seed["department"],
                    branch_code=seed["branchCode"], phone=seed["phone"],
                    active_leads=seed["activeLeads"], avg_tat_mins=seed["avgTatMins"],
                    status=seed["status"], score=seed["score"],
                ))
            db.commit()
            print(f"✅ Seeded {len(SEED_SLMS)} initial SLMs into PostgreSQL.")

        if db.query(Enquiry).count() == 0:
            for seed in SEED_ENQUIRIES:
                created_at = datetime.utcnow() - timedelta(minutes=seed["age_offset_mins"])
                enq = Enquiry(
                    id=seed["id"],
                    patient_name=seed["patient_name"],
                    phone=seed["phone"],
                    age=seed["age"],
                    gender=seed["gender"],
                    branch=seed["branch"],
                    branch_code=seed["branch_code"],
                    department=seed["department"],
                    doctor_name=seed["doctor_name"],
                    enquiry_type=seed["enquiry_type"],
                    disposition=seed["disposition"],
                    priority=seed["priority"],
                    status=seed["status"],
                    assigned_slm=seed["assigned_slm"],
                    slm_id=seed["slm_id"],
                    audio_duration=seed["audio_duration"],
                    recording_url=seed["recording_url"],
                    recording_path=seed["recording_path"],
                    notes=seed["notes"],
                    remarks=seed["remarks"],
                    next_followup=seed["next_followup"],
                    call_start_time=created_at.strftime("%H:%M:%S"),
                    call_end_time=(created_at + timedelta(minutes=3)).strftime("%H:%M:%S"),
                    created_at=created_at,
                    updated_at=created_at,
                    sla_breached=seed["sla_breached"],
                    escalated_to_branch_head=seed["escalated_to_branch_head"],
                )
                db.add(enq)
                db.flush()
                action_time = created_at
                for action_text, performed_by in seed["actions"]:
                    log_action(db, seed["id"], action_text, performed_by, action_time)
                    action_time += timedelta(minutes=1)
            db.commit()
            print(f"✅ Seeded {len(SEED_ENQUIRIES)} initial enquiries into PostgreSQL.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.execute(text(f"SELECT pg_advisory_unlock({STARTUP_LOCK_ID})"))
        db.close()


# --- API ENDPOINTS ---

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.get("/")
def read_root(db: Session = Depends(get_db_session)):
    return {
        "organization": "Prashanth Hospitals",
        "tagline": "WE CARE FOR U",
        "service": "Call Center & SLM Mobile Platform API",
        "version": "1.1.0",
        "status": "Operational",
        "xtendDb2Hub": "Kolathur Call Center Central Hub",
        "activeEnquiriesCount": db.query(Enquiry).count()
    }

# 1. BRANCHES (PostgreSQL-backed — see models.Branch)
@app.get("/api/v1/db/pool-status")
def get_db_pool_status(_user: User = Depends(get_current_user)):
    return db_manager.get_pool_status()

@app.get("/api/v1/branches")
def get_branches(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    branches = db.query(Branch).order_by(Branch.id).all()
    return {"branches": [serialize_branch(b) for b in branches], "total": len(branches)}

@app.post("/api/v1/branches")
def create_branch(payload: BranchCreateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    if db.query(Branch).filter(func.upper(Branch.code) == payload.code.upper()).first():
        raise HTTPException(status_code=400, detail=f"Branch code {payload.code} already exists.")

    # Generate a "b<n>" id that doesn't collide with an existing row (a plain
    # count+1, like the old in-memory version used, can reuse an id after a
    # delete — e.g. delete b3 then add reissues b3 while b3's old data may
    # still be referenced elsewhere).
    existing_ids = {row[0] for row in db.query(Branch.id).all()}
    n = len(existing_ids) + 1
    while f"b{n}" in existing_ids:
        n += 1
    new_branch = Branch(
        id=f"b{n}",
        code=payload.code.upper(),
        name=payload.name,
        city=payload.city,
        type=payload.type,
        status=payload.status,
        leads_today=0,
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return {"message": "Branch created successfully", "branch": serialize_branch(new_branch)}

@app.delete("/api/v1/branches/{branch_id}")
def delete_branch(branch_id: str, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    branch = db.query(Branch).filter(
        (Branch.id == branch_id) | (func.upper(Branch.code) == branch_id.upper())
    ).first()
    if not branch:
        raise HTTPException(status_code=404, detail=f"Branch {branch_id} not found.")
    db.delete(branch)
    db.commit()
    return {"message": f"Branch {branch_id} deleted successfully"}


# 2. USER & PERMISSION MANAGEMENT (PostgreSQL-backed — see models.User)
@app.get("/api/v1/users")
def get_users(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    users = db.query(User).order_by(User.id).all()
    return {"users": [serialize_user(u) for u in users], "total": len(users)}

@app.post("/api/v1/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{payload.username}' is already taken.")
    
    new_user = User(
        username=payload.username,
        full_name=payload.fullName or payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role or "SLM",
        branch_code=payload.branchCode or "ALL",
        slm_id=payload.slmId,
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User account created successfully", "user": serialize_user(new_user)}

@app.put("/api/v1/users/{user_id}")
def update_user(user_id: int, payload: UserUpdateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    
    if payload.fullName is not None:
        target_user.full_name = payload.fullName
    if payload.email is not None:
        target_user.email = payload.email
    if payload.role is not None:
        target_user.role = payload.role
    if payload.branchCode is not None:
        target_user.branch_code = payload.branchCode
    if payload.slmId is not None:
        target_user.slm_id = payload.slmId
    if payload.status is not None:
        target_user.status = payload.status
    
    db.commit()
    db.refresh(target_user)
    return {"message": "User updated successfully", "user": serialize_user(target_user)}

@app.post("/api/v1/users/{user_id}/reset-password")
def reset_user_password(user_id: int, payload: UserPasswordResetSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    
    if not payload.newPassword or len(payload.newPassword.strip()) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    
    target_user.password_hash = hash_password(payload.newPassword)
    db.commit()
    return {"message": f"Password reset successfully for user {target_user.username}"}

@app.delete("/api/v1/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    if target_user.username == _user.username:
        raise HTTPException(status_code=400, detail="Cannot delete your own active session account.")
    
    db.delete(target_user)
    db.commit()
    return {"message": f"User {target_user.username} deleted successfully"}


# 3. SERVICE LINE MANAGERS (SLMs) (PostgreSQL-backed — see models.SLM)
@app.get("/api/v1/slms")
def get_slms(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slms = db.query(SLM).order_by(SLM.id).all()
    return {"slms": [serialize_slm(s) for s in slms], "total": len(slms)}

@app.post("/api/v1/slms", status_code=status.HTTP_201_CREATED)
def create_slm(payload: SLMCreateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slm_count = db.query(SLM).count()
    new_slm_id = f"slm-{100 + slm_count + 1}"
    
    new_slm = SLM(
        id=new_slm_id,
        name=payload.name,
        department=payload.department,
        branch_code=payload.branchCode.upper(),
        phone=payload.phone,
        status=payload.status or "ON_DUTY",
        active_leads=0,
        avg_tat_mins=0.0,
        score=95.0
    )
    db.add(new_slm)
    
    user_created = None
    if payload.createUserAccount and payload.username and payload.password:
        existing = db.query(User).filter(User.username == payload.username).first()
        if not existing:
            new_user = User(
                username=payload.username,
                full_name=payload.name,
                password_hash=hash_password(payload.password),
                role="SLM",
                branch_code=payload.branchCode.upper(),
                slm_id=new_slm_id,
                status="ACTIVE",
                created_at=datetime.utcnow()
            )
            db.add(new_user)
            user_created = payload.username
    
    db.commit()
    db.refresh(new_slm)
    return {
        "message": "SLM created successfully",
        "slm": serialize_slm(new_slm),
        "userCreated": user_created
    }

@app.put("/api/v1/slms/{slm_id}")
def update_slm(slm_id: str, payload: SLMUpdateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slm_row = db.query(SLM).filter(SLM.id == slm_id).first()
    if not slm_row:
        raise HTTPException(status_code=404, detail=f"SLM {slm_id} not found.")
    
    if payload.name is not None:
        slm_row.name = payload.name
    if payload.department is not None:
        slm_row.department = payload.department
    if payload.branchCode is not None:
        slm_row.branch_code = payload.branchCode.upper()
    if payload.phone is not None:
        slm_row.phone = payload.phone
    if payload.status is not None:
        slm_row.status = payload.status
    if payload.score is not None:
        slm_row.score = payload.score
    
    db.commit()
    db.refresh(slm_row)
    return {"message": "SLM updated successfully", "slm": serialize_slm(slm_row)}

@app.delete("/api/v1/slms/{slm_id}")
def delete_slm(slm_id: str, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slm_row = db.query(SLM).filter(SLM.id == slm_id).first()
    if not slm_row:
        raise HTTPException(status_code=404, detail=f"SLM {slm_id} not found.")
    
    db.delete(slm_row)
    db.commit()
    return {"message": f"SLM {slm_id} deleted successfully"}

# 3. ENQUIRIES & LEAD MANAGEMENT (PostgreSQL-backed — see models.Enquiry)
@app.get("/api/v1/enquiries")
def get_enquiries(
    branchCode: Optional[str] = Query(None, description="Filter by branch code like KOL, CHP, VEL"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority URGENT/HIGH/MEDIUM"),
    search: Optional[str] = Query(None, description="Search patient name or phone"),
    db: Session = Depends(get_db_session),
    _user: User = Depends(get_current_user)
):
    query = db.query(Enquiry)
    if branchCode:
        query = query.filter(func.upper(Enquiry.branch_code) == branchCode.upper())
    if status:
        query = query.filter(func.upper(Enquiry.status) == status.upper())
    if priority:
        query = query.filter(func.upper(Enquiry.priority) == priority.upper())
    if search:
        q = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Enquiry.patient_name).like(q) | func.lower(Enquiry.phone).like(q)
        )

    results = query.order_by(Enquiry.created_at.desc()).all()
    serialized = [serialize_enquiry(e) for e in results]
    return {"enquiries": serialized, "total": len(serialized)}

@app.get("/api/v1/enquiries/{enquiry_id}")
def get_enquiry_by_id(enquiry_id: str, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")
    return {"enquiry": serialize_enquiry(enq)}

@app.post("/api/v1/enquiries", status_code=status.HTTP_201_CREATED)
def create_enquiry(payload: EnquiryCreate, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    # Mandatory Remarks Check when status is CLOSED or CONVERTED
    if payload.status in ["CLOSED", "CONVERTED"] and not payload.remarks:
        raise HTTPException(
            status_code=400,
            detail="Mandatory remarks required when creating enquiry with status CLOSED or CONVERTED."
        )

    branch_row = db.query(Branch).filter(Branch.code == payload.branch_code.upper()).first()
    matched_branch = branch_row.name if branch_row else "Kolathur (Call Center Hub)"
    assigned_slm = payload.assigned_slm or "Auto-Routed SLM"
    now = datetime.utcnow()

    for attempt in range(5):
        enquiry_id = generate_unique_enquiry_id(db)
        new_enquiry = Enquiry(
            id=enquiry_id,
            patient_name=payload.patient_name,
            phone=payload.phone,
            age=42,
            gender="Unknown",
            branch=matched_branch,
            branch_code=payload.branch_code.upper(),
            department=payload.department,
            doctor_name="On-Duty Specialist",
            enquiry_type=payload.enquiry_type,
            disposition=payload.disposition,
            priority="HIGH",
            status=payload.status,
            assigned_slm=assigned_slm,
            slm_id="slm-101",
            audio_duration="1m 30s" if payload.recording_path else "No audio recording",
            recording_url=payload.recording_path,
            recording_path=payload.recording_path,
            notes=payload.remarks or "Newly created enquiry from XTEND DB2 sync.",
            remarks=payload.remarks,
            next_followup="Tomorrow 10:00 AM",
            call_start_time=now.strftime("%H:%M:%S"),
            created_at=now,
            updated_at=now,
            sla_breached=False,
            escalated_to_branch_head=False,
        )
        db.add(new_enquiry)
        try:
            db.flush()
            break
        except IntegrityError:
            db.rollback()  # Rare TOCTOU collision on the id — retry with a fresh one.
    else:
        raise HTTPException(status_code=500, detail="Failed to allocate a unique enquiry ID after multiple attempts.")

    log_action(db, enquiry_id, f"Enquiry created manually ({payload.enquiry_type})", assigned_slm, now)
    db.commit()
    db.refresh(new_enquiry)

    send_fcm_notification(enquiry_id, assigned_slm, "New Hospital Enquiry", f"Enquiry for {payload.patient_name}", payload.disposition)

    return {"message": "Enquiry created successfully", "enquiry": serialize_enquiry(new_enquiry)}

@app.post("/api/v1/xtend/simulate-call")
def simulate_xtend_call(payload: XtendCallSimulationSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    branch_code = payload.selectedBranchCode or random.choice(["KOL", "CHP", "VEL", "GUM", "IVF"])
    branch_row = db.query(Branch).filter(Branch.code == branch_code).first()
    matched_branch = branch_row.name if branch_row else "Kolathur (Call Center Hub)"
    dept = payload.department or random.choice(["Cardiology", "IVF & Fertility", "Orthopedics", "Obstetrics & Gynecology"])

    slm_obj = db.query(SLM).filter(SLM.branch_code == branch_code).first() or db.query(SLM).first()
    assigned_slm = f"{slm_obj.name} (SLM {slm_obj.department})" if slm_obj else "Vijay Kumar (SLM Cardio)"

    disposition = payload.disposition or "CALLBACK_REQUESTED"
    now = datetime.utcnow()
    patient_name = payload.callerName or f"Patient {random.randint(100, 999)}"

    for attempt in range(5):
        new_id = generate_unique_enquiry_id(db)
        simulated = Enquiry(
            id=new_id,
            patient_name=patient_name,
            phone=payload.callerPhone or f"+91 98401 {random.randint(10000, 99999)}",
            age=random.randint(25, 75),
            gender=random.choice(["Male", "Female"]),
            branch=matched_branch,
            branch_code=branch_code,
            department=dept,
            doctor_name="Duty Consultant Doctor",
            enquiry_type=f"{dept} General Enquiry",
            disposition=disposition,
            priority=random.choice(["URGENT", "HIGH", "MEDIUM"]),
            status="NEW",
            assigned_slm=assigned_slm,
            slm_id=slm_obj.id if slm_obj else "slm-101",
            audio_duration="2m 10s",
            recording_url="wav_8801.wav",
            recording_path="wav_8801.wav",
            notes=f"Inbound call captured from XTEND DB2 at Kolathur Call Center Hub. Routed to {matched_branch} {dept}.",
            remarks=None,
            next_followup=(now + timedelta(hours=2)).strftime("%Y-%m-%d %I:%M %p"),
            call_start_time=now.strftime("%H:%M:%S"),
            created_at=now,
            updated_at=now,
            sla_breached=False,
            escalated_to_branch_head=False,
        )
        db.add(simulated)
        try:
            db.flush()
            break
        except IntegrityError:
            db.rollback()  # Rare TOCTOU collision on the id — retry with a fresh one.
    else:
        raise HTTPException(status_code=500, detail="Failed to allocate a unique enquiry ID after multiple attempts.")

    log_action(db, new_id, "Inbound Call Connected via XTEND DB2 (Kolathur Hub)", "XTEND IVR", now)
    log_action(db, new_id, f"Call routed to {matched_branch} — {dept}", "Auto-Routing Engine", now)

    pushed = send_fcm_notification(new_id, assigned_slm, "XTEND Call Ingested", f"New call for {patient_name}", disposition)
    msg = "XTEND Call record ingested into PostgreSQL"
    if pushed:
        msg += " & pushed to SLM Mobile App via FCM"
        log_action(db, new_id, f"FCM Push dispatched to {assigned_slm}", "System", now)
    else:
        msg += " (FCM Push Bypassed - First Call Resolution)"
        log_action(db, new_id, "FCM Push bypassed — First Call Resolution", "System", now)

    db.commit()
    db.refresh(simulated)

    return {
        "message": msg,
        "enquiry": serialize_enquiry(simulated)
    }

@app.patch("/api/v1/enquiries/{enquiry_id}")
def update_enquiry(enquiry_id: str, payload: EnquiryUpdateSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")

    now = datetime.utcnow()
    performed_by = payload.assignedSLM or enq.assigned_slm

    if payload.status:
        # Mandatory Remarks check for CLOSED or CONVERTED
        if payload.status in ["CLOSED", "CONVERTED"]:
            submitted_remarks = payload.remarks if payload.remarks is not None else payload.notes
            if not submitted_remarks or not submitted_remarks.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Mandatory resolution remarks required to update status to {payload.status}."
                )
            enq.call_end_time = now.strftime("%H:%M:%S")
        enq.status = payload.status
        log_action(db, enquiry_id, f"Status updated to {payload.status}", performed_by, now)
    if payload.disposition:
        enq.disposition = payload.disposition
        log_action(db, enquiry_id, f"Disposition updated to {payload.disposition}", performed_by, now)
    if payload.notes:
        enq.notes = payload.notes
    if payload.remarks:
        enq.remarks = payload.remarks
        log_action(db, enquiry_id, "Resolution remarks registered", performed_by, now)
    if payload.priority:
        enq.priority = payload.priority
        log_action(db, enquiry_id, f"Priority changed to {payload.priority}", performed_by, now)
    if payload.nextFollowup:
        enq.next_followup = payload.nextFollowup
    if payload.assignedSLM:
        enq.assigned_slm = payload.assignedSLM
        log_action(db, enquiry_id, f"Reassigned to {payload.assignedSLM}", performed_by, now)

    enq.updated_at = now
    db.commit()
    db.refresh(enq)
    return {"message": "Enquiry updated successfully", "enquiry": serialize_enquiry(enq)}

@app.post("/api/v1/enquiries/{enquiry_id}/actions")
def add_enquiry_action(
    enquiry_id: str,
    payload: ActionCreateSchema,
    db: Session = Depends(get_db_session),
    _user: User = Depends(get_current_user)
):
    enq = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")

    now = datetime.utcnow()
    performed_by = payload.performedBy or enq.assigned_slm or "SLM Agent"
    log_action(db, enquiry_id, payload.action, performed_by, now)
    db.commit()
    db.refresh(enq)
    return {"message": "Action logged successfully", "enquiry": serialize_enquiry(enq)}

@app.post("/api/v1/enquiries/{enquiry_id}/simulate-escalation")
def simulate_enquiry_escalation(enquiry_id: str, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {enquiry_id} not found")
    enq.sla_breached = True
    enq.escalated_to_branch_head = True
    enq.updated_at = datetime.utcnow()
    log_action(db, enquiry_id, "FIRST RESPONSE SLA BREACH (>15 mins) — Escalated to Branch Head & Operations Director", "SLA Engine", enq.updated_at)
    db.commit()
    db.refresh(enq)
    return {"message": f"Simulated SLA breach & escalation for Enquiry {enquiry_id}", "enquiry": serialize_enquiry(enq)}

@app.post("/api/v1/sla/check-breaches")
def check_sla_breaches(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    active_enquiries = db.query(Enquiry).filter(Enquiry.status.in_(["NEW", "ASSIGNED"])).all()
    
    tier2_breaches = 0
    tier3_breaches = 0
    
    for enq in active_enquiries:
        age_mins = (now - enq.created_at).total_seconds() / 60.0
        if age_mins > 30:
            if not enq.sla_breached or not enq.escalated_to_branch_head:
                enq.sla_breached = True
                enq.escalated_to_branch_head = True
                enq.updated_at = now
                log_action(db, enq.id, "CRITICAL SLA BREACH (>30 mins) — Tier 3 Escalation to Operations Director & Group COO", "SLA Engine", now)
                tier3_breaches += 1
        elif age_mins > 15:
            if not enq.sla_breached:
                enq.sla_breached = True
                enq.escalated_to_branch_head = True
                enq.updated_at = now
                log_action(db, enq.id, "FIRST RESPONSE SLA BREACH (>15 mins) — Tier 2 Escalation to Branch Head", "SLA Engine", now)
                tier2_breaches += 1

    db.commit()
    return {
        "message": f"SLA Audit Complete. Evaluated {len(active_enquiries)} active leads.",
        "scanned": len(active_enquiries),
        "tier2Breaches": tier2_breaches,
        "tier3Breaches": tier3_breaches
    }

@app.get("/api/v1/sla/matrix")
def get_sla_matrix(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    all_enquiries = db.query(Enquiry).all()
    
    tier1_on_time = 0
    tier2_branch_head = 0
    tier3_director = 0
    
    for e in all_enquiries:
        age_mins = (now - e.created_at).total_seconds() / 60.0
        if e.sla_breached or age_mins > 30:
            tier3_director += 1
        elif age_mins > 15:
            tier2_branch_head += 1
        else:
            tier1_on_time += 1

    total = len(all_enquiries) or 1
    compliance_rate = round((tier1_on_time / total) * 100, 1)

    return {
        "totalEnquiries": total,
        "tier1OnTime": tier1_on_time,
        "tier2BranchHead": tier2_branch_head,
        "tier3Director": tier3_director,
        "slaComplianceRate": f"{compliance_rate}%",
        "targetSlaMins": 15
    }

@app.get("/api/v1/sla/scorecard")
def get_sla_scorecard(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slms = db.query(SLM).all()
    enquiries = db.query(Enquiry).all()
    
    scorecard = []
    for s in slms:
        slm_enqs = [e for e in enquiries if e.slm_id == s.id]
        total_handled = len(slm_enqs)
        converted = len([e for e in slm_enqs if e.status in ["SURGERY_FIXED", "APPOINTMENT_CONFIRMED", "CONVERTED", "CLOSED"]])
        conv_rate = (converted / total_handled * 100) if total_handled > 0 else 75.0
        
        breaches = len([e for e in slm_enqs if e.sla_breached])
        tat = s.avg_tat_mins or 8.0
        
        # Weighted Scoring Breakdown:
        # 40% TAT Compliance + 35% Conversion Rate + 15% FCR + 10% Audit Quality
        tat_score = max(0, min(40, (15 - tat) * 2.6 + 20))
        conv_score = (conv_rate / 100.0) * 35.0
        fcr_score = 14.0 if breaches == 0 else max(0, 14.0 - breaches * 3)
        quality_score = 9.5
        
        final_score = round(tat_score + conv_score + fcr_score + quality_score, 1)
        
        if final_score >= 95:
            grade = "A+ Outstanding"
        elif final_score >= 88:
            grade = "A Excellent"
        elif final_score >= 80:
            grade = "B Good"
        else:
            grade = "Needs Improvement"

        scorecard.append({
            "slmId": s.id,
            "name": s.name,
            "department": s.department,
            "branchCode": s.branch_code,
            "totalHandled": total_handled,
            "avgTatMins": tat,
            "conversionRate": f"{round(conv_rate, 1)}%",
            "slaBreaches": breaches,
            "score": final_score,
            "grade": grade,
            "status": s.status
        })

    scorecard.sort(key=lambda x: x["score"], reverse=True)
    return {"scorecard": scorecard, "total": len(scorecard)}

# 4. LEADERSHIP ANALYTICS
@app.get("/api/v1/analytics/overview")
def get_analytics_overview(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    total_inquiries = 457
    avg_tat = 9.2
    surgeries = 127
    conversion = "27%"
    sla_breaches = db.query(Enquiry).filter(Enquiry.sla_breached == True).count()

    return {
        "totalInquiriesToday": total_inquiries,
        "avgFirstResponseTatMins": avg_tat,
        "surgeriesAndSlotsFixed": surgeries,
        "conversionRate": conversion,
        "slaBreachAlerts": sla_breaches,
        "branchesCount": db.query(Branch).count(),
        "activeSlmsCount": db.query(SLM).filter(SLM.status == "ON_DUTY").count()
    }

@app.get("/api/v1/analytics/specialities")
def get_analytics_specialities(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    departments = ["Cardiology", "IVF & Fertility", "Orthopedics", "Obstetrics & Gynecology", "Nephrology & Urology", "Neurology", "General Surgery"]
    enquiries = db.query(Enquiry).all()
    
    dept_map = {}
    for d in departments:
        dept_map[d] = {
            "speciality": d,
            "totalInquiries": 0,
            "surgeriesAndAppointmentsFixed": 0,
            "pendingLeads": 0,
            "conversionRate": "0%",
            "avgTatMins": 8.5
        }
        
    for e in enquiries:
        dept = e.department or "General Surgery"
        if dept not in dept_map:
            dept_map[dept] = {
                "speciality": dept,
                "totalInquiries": 0,
                "surgeriesAndAppointmentsFixed": 0,
                "pendingLeads": 0,
                "conversionRate": "0%",
                "avgTatMins": 8.0
            }
        
        dept_map[dept]["totalInquiries"] += 1
        if e.status in ["SURGERY_FIXED", "APPOINTMENT_CONFIRMED", "CONVERTED", "CLOSED"]:
            dept_map[dept]["surgeriesAndAppointmentsFixed"] += 1
        elif e.status in ["NEW", "ASSIGNED", "CONTACTED"]:
            dept_map[dept]["pendingLeads"] += 1

    for dept, data in dept_map.items():
        tot = data["totalInquiries"]
        fix = data["surgeriesAndAppointmentsFixed"]
        rate = round((fix / tot * 100), 1) if tot > 0 else 0.0
        data["conversionRate"] = f"{rate}%"

    results = list(dept_map.values())
    results.sort(key=lambda x: x["totalInquiries"], reverse=True)
    return {"specialities": results, "total": len(results)}


@app.get("/api/v1/analytics/doctors")
def get_analytics_doctors(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enquiries = db.query(Enquiry).all()
    
    doc_map = {}
    for e in enquiries:
        doc = e.doctor_name or "Duty Consultant Doctor"
        if doc not in doc_map:
            doc_map[doc] = {
                "doctorName": doc,
                "department": e.department or "Multispecialty",
                "consultations": 0,
                "surgeriesFixed": 0,
                "conversionRate": "0%",
                "avgPatientTat": "7.8 mins"
            }
        doc_map[doc]["consultations"] += 1
        if e.status in ["SURGERY_FIXED", "APPOINTMENT_CONFIRMED", "CONVERTED"]:
            doc_map[doc]["surgeriesFixed"] += 1

    for doc, data in doc_map.items():
        tot = data["consultations"]
        fix = data["surgeriesFixed"]
        rate = round((fix / tot * 100), 1) if tot > 0 else 0.0
        data["conversionRate"] = f"{rate}%"

    results = list(doc_map.values())
    results.sort(key=lambda x: x["consultations"], reverse=True)
    return {"doctors": results, "total": len(results)}


@app.get("/api/v1/analytics/agents")
def get_analytics_agents(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    slms = db.query(SLM).all()
    enquiries = db.query(Enquiry).all()
    
    agent_map = {}
    for s in slms:
        agent_map[s.id] = {
            "slmId": s.id,
            "name": s.name,
            "department": s.department,
            "branchCode": s.branch_code,
            "callsHandled": 0,
            "conversions": 0,
            "conversionRate": "0%",
            "avgTatMins": s.avg_tat_mins or 7.5,
            "slaBreaches": 0,
            "score": s.score or 95.0,
            "status": s.status
        }
        
    for e in enquiries:
        slm_key = e.slm_id or "slm-101"
        if slm_key in agent_map:
            agent_map[slm_key]["callsHandled"] += 1
            if e.status in ["SURGERY_FIXED", "APPOINTMENT_CONFIRMED", "CONVERTED", "CLOSED"]:
                agent_map[slm_key]["conversions"] += 1
            if e.sla_breached:
                agent_map[slm_key]["slaBreaches"] += 1

    for slm_id, data in agent_map.items():
        tot = data["callsHandled"]
        conv = data["conversions"]
        rate = round((conv / tot * 100), 1) if tot > 0 else 0.0
        data["conversionRate"] = f"{rate}%"

    results = list(agent_map.values())
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"agents": results, "total": len(results)}

# 5. CALL RECORDING AUDIO PROXY (Generates real WAV audio stream on-the-fly)
@app.get("/api/v1/recordings/{filename}")
def get_call_audio(filename: str, _user: User = Depends(get_current_user)):
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

# 6. HIS (HOSPITAL INFORMATION SYSTEM) INTEGRATIONS
@app.get("/api/v1/his/slots")
def get_his_available_slots(doctorName: Optional[str] = None, branchCode: Optional[str] = None, _user: User = Depends(get_current_user)):
    slots = [
        {"slotTime": "09:30 AM", "status": "AVAILABLE", "doctorName": doctorName or "Dr. S. Prashanth", "room": "OPD-101"},
        {"slotTime": "10:30 AM", "status": "AVAILABLE", "doctorName": doctorName or "Dr. S. Prashanth", "room": "OPD-101"},
        {"slotTime": "11:15 AM", "status": "BOOKED", "doctorName": doctorName or "Dr. S. Prashanth", "room": "OPD-101"},
        {"slotTime": "02:00 PM", "status": "AVAILABLE", "doctorName": doctorName or "Dr. Geetha Haripriya", "room": "IVF-Suite-2"},
        {"slotTime": "03:45 PM", "status": "AVAILABLE", "doctorName": doctorName or "Dr. R. Balaji", "room": "OPD-204"},
        {"slotTime": "05:00 PM", "status": "AVAILABLE", "doctorName": doctorName or "Dr. G. V. Ayyappan", "room": "OPD-305"},
    ]
    return {"slots": slots, "total": len(slots)}

@app.post("/api/v1/his/book-appointment")
def his_book_appointment(payload: HISBookSlotSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == payload.enquiryId).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {payload.enquiryId} not found")
    
    now = datetime.utcnow()
    his_booking_id = f"HIS-OPD-{random.randint(8000, 9999)}"
    patient_uhid = payload.patientUhid or enq.patient_uhid or f"PH-UHID-2026-{random.randint(1000, 9999)}"
    
    enq.patient_uhid = patient_uhid
    enq.his_booking_id = his_booking_id
    enq.his_sync_status = "SYNCED"
    enq.his_synced_at = now
    enq.doctor_name = payload.doctorName
    enq.status = "APPOINTMENT_CONFIRMED"
    enq.disposition = "APPOINTMENT_FIXED"
    enq.remarks = payload.remarks or f"HIS OPD slot booked for {payload.appointmentDate} at {payload.slotTime} ({his_booking_id})"
    enq.updated_at = now
    
    log_action(db, payload.enquiryId, f"HIS OPD Appointment Booked: {payload.doctorName} on {payload.appointmentDate} {payload.slotTime} (Booking Ref: {his_booking_id}, UHID: {patient_uhid})", _user.username, now)
    
    db.commit()
    db.refresh(enq)
    return {
        "message": f"OPD Consultation Slot successfully booked in HIS (UHID: {patient_uhid})",
        "hisBookingId": his_booking_id,
        "patientUhid": patient_uhid,
        "enquiry": serialize_enquiry(enq)
    }

@app.post("/api/v1/his/prebook-surgery")
def his_prebook_surgery(payload: HISPrebookSurgerySchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == payload.enquiryId).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {payload.enquiryId} not found")
    
    now = datetime.utcnow()
    his_ot_booking = f"HIS-OT-{random.randint(7000, 8999)}"
    patient_uhid = enq.patient_uhid or f"PH-UHID-2026-{random.randint(1000, 9999)}"
    
    enq.patient_uhid = patient_uhid
    enq.his_booking_id = his_ot_booking
    enq.his_sync_status = "SYNCED"
    enq.his_synced_at = now
    enq.doctor_name = payload.doctorName
    enq.status = "SURGERY_FIXED"
    enq.disposition = "APPOINTMENT_FIXED"
    enq.remarks = payload.remarks or f"HIS Surgical OT pre-booked for {payload.proposedSurgeryDate} ({payload.procedureName} in {payload.otRoom})"
    enq.updated_at = now
    
    log_action(db, payload.enquiryId, f"HIS OT Surgery Pre-Booked: {payload.procedureName} under {payload.doctorName} on {payload.proposedSurgeryDate} (OT Ref: {his_ot_booking})", _user.username, now)
    
    db.commit()
    db.refresh(enq)
    return {
        "message": f"Surgical OT Slot successfully pre-booked in HIS (OT Ref: {his_ot_booking})",
        "hisBookingId": his_ot_booking,
        "patientUhid": patient_uhid,
        "enquiry": serialize_enquiry(enq)
    }

@app.get("/api/v1/his/patient-search")
def his_patient_search(search: str, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    records = [
        {"uhid": "PH-UHID-2026-8801", "patientName": "Karthik Raja", "phone": "+91 98401 54321", "gender": "Male", "age": 48, "bloodGroup": "O+ve", "lastVisit": "2026-07-20"},
        {"uhid": "PH-UHID-2026-8802", "patientName": "Meenakshi Sundaram", "phone": "+91 94440 12890", "gender": "Female", "age": 34, "bloodGroup": "B+ve", "lastVisit": "2026-07-28"},
        {"uhid": "PH-UHID-2026-8803", "patientName": "Subramanian V.", "phone": "+91 98840 98765", "gender": "Male", "age": 62, "bloodGroup": "A+ve", "lastVisit": "2026-07-15"},
    ]
    matched = [r for r in records if search.lower() in r["patientName"].lower() or search in r["phone"] or search.lower() in r["uhid"].lower()]
    return {"results": matched, "total": len(matched)}

# 7. NOTIFICATIONS & REPORT EXPORTS ENGINE
@app.get("/api/v1/notifications/templates")
def get_notification_templates(_user: User = Depends(get_current_user)):
    templates = [
        {
            "type": "APPOINTMENT_CONFIRMATION",
            "channel": "WHATSAPP",
            "title": "OPD Consultation Confirmation",
            "bodyTemplate": "Dear {patient_name}, your consultation with {doctor_name} at Prashanth Hospitals ({branch}) is confirmed for {appointment_time}. Ref: {booking_id}. UHID: {uhid}. WE CARE FOR U."
        },
        {
            "type": "SURGERY_PREBOOK",
            "channel": "WHATSAPP",
            "title": "OT Surgery Pre-booking Alert",
            "bodyTemplate": "Dear {patient_name}, your procedure ({procedure_name}) OT booking under {doctor_name} at Prashanth Hospitals ({branch}) is confirmed for {surgery_date}. OT Ref: {booking_id}. UHID: {uhid}."
        },
        {
            "type": "FOLLOWUP_REMINDER",
            "channel": "SMS",
            "title": "Follow-Up Consultation Reminder",
            "bodyTemplate": "Reminder: Dear {patient_name}, your follow-up consultation with Prashanth Hospitals {branch} is scheduled for {next_followup}. Contact +91 44 4000 5000."
        }
    ]
    return {"templates": templates}

@app.post("/api/v1/notifications/send")
def send_notification(payload: NotificationDispatchSchema, db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enq = db.query(Enquiry).filter(Enquiry.id == payload.enquiryId).first()
    if not enq:
        raise HTTPException(status_code=404, detail=f"Enquiry {payload.enquiryId} not found")

    now = datetime.utcnow()
    patient_name = enq.patient_name
    doctor_name = enq.doctor_name or "Duty Specialist"
    branch = enq.branch or "Kolathur"
    uhid = enq.patient_uhid or "PH-UHID-2026-TEMP"
    booking_id = enq.his_booking_id or "HIS-TEMP-101"

    if payload.templateType == "APPOINTMENT_CONFIRMATION":
        rendered_body = f"Dear {patient_name}, your consultation with {doctor_name} at Prashanth Hospitals ({branch}) is confirmed. Ref: {booking_id}. UHID: {uhid}. WE CARE FOR U."
    elif payload.templateType == "SURGERY_PREBOOK":
        rendered_body = f"Dear {patient_name}, your surgical procedure under {doctor_name} at Prashanth Hospitals ({branch}) is pre-booked. OT Ref: {booking_id}. UHID: {uhid}."
    else:
        rendered_body = payload.customMessage or f"Dear {patient_name}, thank you for contacting Prashanth Hospitals ({branch}). WE CARE FOR U."

    log_action(db, payload.enquiryId, f"Outbound {payload.channel} notification dispatched to {payload.recipientPhone} ({payload.templateType})", _user.username, now)
    db.commit()

    return {
        "message": f"{payload.channel} message successfully dispatched to {payload.recipientPhone} via Prashanth Hospitals Notification Gateway.",
        "dispatchId": f"NOTIF-{random.randint(9000, 9999)}",
        "channel": payload.channel,
        "recipient": payload.recipientPhone,
        "renderedBody": rendered_body
    }

@app.get("/api/v1/reports/export/csv")
def export_csv_report(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    enquiries = db.query(Enquiry).order_by(Enquiry.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Enquiry ID", "Patient Name", "Phone", "Age", "Gender", "Branch Code", "Branch Name",
        "Department", "Doctor Name", "Enquiry Type", "Disposition", "Priority", "Status",
        "Assigned SLM", "Audio Duration", "SLA Breached", "Escalated Branch Head",
        "Patient UHID", "HIS Booking ID", "HIS Sync Status", "Created At"
    ])
    
    for e in enquiries:
        writer.writerow([
            e.id, e.patient_name, e.phone, e.age, e.gender, e.branch_code, e.branch,
            e.department, e.doctor_name, e.enquiry_type, e.disposition, e.priority, e.status,
            e.assigned_slm, e.audio_duration, e.sla_breached, e.escalated_to_branch_head,
            e.patient_uhid, e.his_booking_id, e.his_sync_status,
            e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else ""
        ])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=prashanth_hosp_callcenter_report.csv"}
    )

@app.get("/api/v1/reports/export/summary")
def export_summary_report(db: Session = Depends(get_db_session), _user: User = Depends(get_current_user)):
    total_enquiries = db.query(Enquiry).count()
    branches_count = db.query(Branch).count()
    slms_count = db.query(SLM).count()
    sla_breaches = db.query(Enquiry).filter(Enquiry.sla_breached == True).count()
    his_synced = db.query(Enquiry).filter(Enquiry.his_sync_status == "SYNCED").count()
    
    return {
        "reportTitle": "Prashanth Hospitals Call Center & SLM Platform Executive Summary",
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "totalEnquiriesCaptured": total_enquiries,
        "activeBranches": branches_count,
        "activeSlmRoster": slms_count,
        "slaBreaches": sla_breaches,
        "hisSyncedBookings": his_synced,
        "overallConversionRate": "68.5%"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
