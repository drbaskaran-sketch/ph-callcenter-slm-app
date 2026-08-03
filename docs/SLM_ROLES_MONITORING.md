# Prashanth Hospitals — Service Line Manager (SLM) Governance Guide

## 1. Role Definition & Scope
Service Line Managers (SLMs) are Department Patient Managers responsible for attending to **ANY incoming user query** across all Prashanth Hospitals branches. This broad scope includes:
* General pricing & estimate requests
* Clinical package details & health checks
* Information requests & hospital guidance
* Doctor consultations, OPD slots, & surgical booking
* Patient feedback & complaint resolutions

## 2. Operational Workflows & Deviations

### A. Nullable Voice Paths
* Call Centre Agents are empowered to dispatch inquiries immediately to SLMs without waiting for audio processing.
* If the voice recording file path from XTEND DB2 (`XTEND.HISTORY_1`) is delayed or missing, `recording_path` defaults to `null` or blank.
* The SLM Mobile App handles null/blank `recording_path` fields gracefully, allowing text payloads to be triaged without delay.

### B. First-Contact Resolution (FCR) Notification Bypass
* If a Call Centre Agent resolves a simple inquiry immediately over the phone, they select a resolving disposition (e.g., `INFO_GIVEN`, `COMPLAINT_RESOLVED`).
* The enquiry status is saved as `CLOSED` or `CONVERTED` directly in the database.
* The system **suppresses Firebase Cloud Messaging (FCM) mobile push alerts** for FCR inquiries, completely bypassing the SLM's active queue.

### C. Mandatory Closing Remarks Rule
* Every enquiry moved out of the active workspace must have descriptive resolution text in the `remarks` field.
* This rule applies to both **Call Centre Agents** (for FCR inquiries) and **SLMs** (for completed follow-ups, booked slots, or closed queries).
* The API enforces `remarks` validation prior to saving and archiving any record as `CLOSED` or `CONVERTED`.

## 3. SLA Benchmark KPIs
* **First Response TAT**: < 15 Minutes (for assigned active leads)
* **First-Contact Resolution (FCR) Rate**: Target > 25% of total call center inquiries
* **Contact Rate**: > 85%
* **Follow-up Compliance**: > 92%
* **Appointment / Surgery Conversion**: > 60%

## 4. SLA Escalation Thresholds
* **15 Mins**: Mobile App Push Warning to SLM
* **30 Mins**: Alert Banner on Branch Head Dashboard
* **60 Mins**: Auto-reassign lead to backup SLM in department
