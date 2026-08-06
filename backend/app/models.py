from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

try:
    from .database import db_manager
except ImportError:
    from database import db_manager

Base = db_manager.Base


class Branch(Base):
    """Hospital branch record. Previously an in-process list — a backend
    restart silently reverted any Add/Delete Branch action back to the
    hardcoded seed, which defeats the point of having Delete Branch at all."""
    __tablename__ = "branches"

    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String)
    type = Column(String, default="HOSPITAL")
    status = Column(String, default="ACTIVE")
    leads_today = Column(Integer, default=0)


class SLM(Base):
    """Service Line Manager roster record."""
    __tablename__ = "slms"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String)
    branch_code = Column(String, index=True)
    phone = Column(String)
    active_leads = Column(Integer, default=0)
    avg_tat_mins = Column(Float, default=0)
    status = Column(String, default="ON_DUTY")
    score = Column(Float, default=0)


class User(Base):
    """Login account for leadership dashboard, supervisors, and SLMs."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="ADMIN")  # ADMIN, SUPERVISOR, SLM, BRANCH_HEAD
    branch_code = Column(String, default="ALL", index=True)
    slm_id = Column(String, nullable=True, index=True)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)


class Enquiry(Base):
    """Operational PostgreSQL record for a patient lead / call enquiry.

    Replaces the previous in-process ENQUIRIES list — the in-memory store
    was invisible across the 4 uvicorn worker processes, causing a create
    on one worker to 404 on a subsequent read/update handled by another.
    """
    __tablename__ = "enquiries"

    id = Column(String, primary_key=True, index=True)
    patient_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    branch = Column(String)
    branch_code = Column(String, index=True)
    department = Column(String)
    doctor_name = Column(String)
    enquiry_type = Column(String)
    disposition = Column(String)
    priority = Column(String, index=True)
    status = Column(String, index=True)
    assigned_slm = Column(String)
    slm_id = Column(String)
    audio_duration = Column(String)
    recording_url = Column(String, nullable=True)
    recording_path = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)
    next_followup = Column(String, nullable=True)
    call_start_time = Column(String, nullable=True)
    call_end_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sla_breached = Column(Boolean, default=False)
    escalated_to_branch_head = Column(Boolean, default=False)

    # HIS (Hospital Information System) integration fields
    patient_uhid = Column(String, nullable=True, index=True)
    his_booking_id = Column(String, nullable=True, index=True)
    his_sync_status = Column(String, default="PENDING", index=True)  # PENDING, SYNCED, FAILED
    his_synced_at = Column(DateTime, nullable=True)

    actions = relationship(
        "EnquiryAction",
        back_populates="enquiry",
        cascade="all, delete-orphan",
        order_by="EnquiryAction.timestamp",
    )


class EnquiryAction(Base):
    """Registered action/audit-trail entry — one row per SLM action or
    system event on an enquiry, each with its own timestamp."""
    __tablename__ = "enquiry_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    enquiry_id = Column(String, ForeignKey("enquiries.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    performed_by = Column(String)

    enquiry = relationship("Enquiry", back_populates="actions")
