# Prashanth Hospitals — Architecture Specification

## 1. Executive Blueprint
This document defines the production architecture for transforming the existing **XTEND DB2 Call History synchronization** at the **Kolathur Call Center Hub** into an enterprise hospital enquiry and communication platform.

## 2. Key Architecture Principles
* **call_history**: Raw synchronized XTEND call records from `XTEND.HISTORY_1` (DB2).
* **contacts**: Patient & caller identity resolution.
* **enquiries**: Business workflow, assignment engine, and branch ownership.
* **call_activities**: Call dispositions and agent notes.
* **followups**: Operational scheduled actions.
* **appointments**: OPD and surgical booking lifecycle.
* **messages**: SMS and WhatsApp communication history.

## 3. Workflow Rule Specifications

### A. Nullable Voice Paths (`recording_path`)
* In `enquiries` and `call_history`, `recording_path` is specified as `Optional[str] = None` (nullable).
* Call Centre Agents push text payloads immediately without blocking for DB2 audio file sync.
* The frontend/mobile app renders an "Audio Pending / Unavailable" indicator when `recording_path` is null.

### B. First-Contact Resolution (FCR) & FCM Push Suppression
* When an enquiry is created with status `CLOSED` or `CONVERTED` (e.g. disposition `INFO_GIVEN` or `COMPLAINT_RESOLVED`), the backend `send_fcm_notification` dispatch function is conditionally **suppressed**.
* The enquiry bypasses the SLM active queue entirely while remaining logged in database history for reporting.

### C. Mandatory Closing Remarks Validation
* Backend APIs validate that `remarks` is present, non-empty, and descriptive whenever an enquiry is updated or saved with a resolving status (`CLOSED` or `CONVERTED`).

### D. Broad SLM Query Handling Scope
* The `enquiry_type` taxonomy covers all patient queries: `GENERAL_PRICING`, `PACKAGE_INFO`, `INFO_REQUEST`, `DOCTOR_APPOINTMENT`, `SURGERY_INQUIRY`, and `COMPLAINT`.

## 4. Hospital Branches & Routing Matrix
1. **Kolathur** (Primary Call Center Hub & Multispecialty Hospital)
2. **Chetpet** (Multispecialty Hospital)
3. **Velachery** (Multispecialty Hospital)
4. **Gummidipoondi** (Multispecialty Hospital)
5. **Guduvanchery** (Upcoming Branch)
6. **Navalur** (Upcoming Branch)
7. **IVF Clinics Network** (Fertility Specialty Centers)

## 5. Backend Service & Push Pipeline
* **FastAPI Service**: Provides JWT authentication, enquiry lifecycle management, recording proxy, and conditional FCM push notifications.
* **Database**: PostgreSQL with Alembic migrations.
* **Push Gateway**: Firebase Cloud Messaging (FCM) + Redis Celery Workers.
