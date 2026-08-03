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

## 3. Hospital Branches & Routing Matrix
1. **Kolathur** (Primary Call Center Hub & Multispecialty Hospital)
2. **Chetpet** (Multispecialty Hospital)
3. **Velachery** (Multispecialty Hospital)
4. **Gummidipoondi** (Multispecialty Hospital)
5. **Guduvanchery** (Upcoming Branch)
6. **Navalur** (Upcoming Branch)
7. **IVF Clinics Network** (Fertility Specialty Centers)

## 4. Backend Service & Push Pipeline
* **FastAPI Service**: Provides JWT authentication, enquiry lifecycle management, recording proxy, and FCM push notifications.
* **Database**: PostgreSQL with Alembic migrations.
* **Push Gateway**: Firebase Cloud Messaging (FCM) + Redis Celery Workers.
