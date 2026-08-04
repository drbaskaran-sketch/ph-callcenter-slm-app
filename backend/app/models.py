from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

try:
    from .database import db_manager
except ImportError:
    from database import db_manager

Base = db_manager.Base


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
