from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger("xtend_service")

class XtendCallService:
    """Service to query live call records directly from xtend_replica.public.call_history"""

    @staticmethod
    def parse_call_id(call_id: str) -> Optional[int]:
        """Convert 'XTEND-158950' or '158950' to integer 158950"""
        if isinstance(call_id, int):
            return call_id
        if not call_id:
            return None
        cleaned = str(call_id).strip().upper()
        if cleaned.startswith("XTEND-"):
            cleaned = cleaned.replace("XTEND-", "")
        try:
            return int(cleaned)
        except ValueError:
            return None

    @staticmethod
    def list_calls(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        branch: Optional[str] = None,
        speciality: Optional[str] = None,
        status: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch live XTEND calls with optional filtering"""
        query_str = """
            SELECT 
                id,
                hguid,
                called_time,
                connected_time,
                disconnected_time,
                call_duration,
                phone,
                status,
                reason,
                disposition,
                name AS patient_name,
                patient_uhid,
                enquiry_type,
                patient_type,
                branch,
                speciality,
                doctor_name,
                appointment_date,
                transferred,
                transferred_to,
                recording_path,
                recording_exists,
                synced_at
            FROM public.call_history
            WHERE 1=1
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}

        if branch:
            query_str += " AND (branch ILIKE :branch OR branch IS NULL)"
            params["branch"] = f"%{branch}%"
        if speciality:
            query_str += " AND speciality ILIKE :speciality"
            params["speciality"] = f"%{speciality}%"
        if status:
            query_str += " AND status ILIKE :status"
            params["status"] = f"%{status}%"
        if phone:
            query_str += " AND phone ILIKE :phone"
            params["phone"] = f"%{phone}%"

        query_str += " ORDER BY id DESC LIMIT :limit OFFSET :offset"

        try:
            result = db.execute(text(query_str), params)
            rows = result.mappings().all()
            calls = []
            for row in rows:
                c = dict(row)
                c["formatted_id"] = f"XTEND-{c['id']}"
                if c.get("called_time"):
                    c["called_time"] = str(c["called_time"])
                if c.get("connected_time"):
                    c["connected_time"] = str(c["connected_time"])
                if c.get("disconnected_time"):
                    c["disconnected_time"] = str(c["disconnected_time"])
                if c.get("appointment_date"):
                    c["appointment_date"] = str(c["appointment_date"])
                if c.get("synced_at"):
                    c["synced_at"] = str(c["synced_at"])
                calls.append(c)
            return calls
        except Exception as e:
            logger.error(f"Error fetching calls from xtend_replica: {e}")
            return []

    @staticmethod
    def get_call(db: Session, call_id_str: str) -> Optional[Dict[str, Any]]:
        """Fetch single call record from xtend_replica by ID"""
        raw_id = XtendCallService.parse_call_id(call_id_str)
        if raw_id is None:
            return None

        query_str = """
            SELECT * FROM public.call_history WHERE id = :id LIMIT 1
        """
        try:
            result = db.execute(text(query_str), {"id": raw_id})
            row = result.mappings().first()
            if not row:
                return None
            c = dict(row)
            c["formatted_id"] = f"XTEND-{c['id']}"
            for k, v in c.items():
                if hasattr(v, "isoformat"):
                    c[k] = str(v)
            return c
        except Exception as e:
            logger.error(f"Error fetching call {call_id_str} from xtend_replica: {e}")
            return None
