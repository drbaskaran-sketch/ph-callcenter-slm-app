# Prashanth Hospitals — Call Center & SLM Mobile App Platform (`ph-callcenter-slm-app`)

> **Tagline**: *"WE CARE FOR U"*  
> **Primary Call Center Hub**: Kolathur Branch (XTEND IBM DB2 Installed)  
> **Multi-Branch Operations**: Kolathur, Chetpet, Velachery, Gummidipoondi, Guduvanchery (Upcoming), Navalur (Upcoming), and IVF Clinics.

---

## 📌 Project Overview

`ph-callcenter-slm-app` is the enterprise hospital enquiry management, multi-branch routing, and **Service Line Manager (SLM) Mobile Application** platform designed for **Prashanth Hospitals**, Chennai.

It synchronizes call records near-real-time from **XTEND DB2** at the Kolathur Call Center hub into a PostgreSQL operational database and dispatches leads to department SLMs on Android/iOS mobile devices.

---

## 🏥 Hospital Branch Network

* **Call Center Ingestion Hub**: Kolathur Branch
* **Active Multispecialty Hospital Branches**:
  1. **Kolathur** (Chennai North)
  2. **Chetpet** (Central Chennai)
  3. **Velachery** (Chennai South)
  4. **Gummidipoondi** (Tiruvallur Suburbs)
* **Upcoming Branches (Opening Shortly)**:
  5. **Guduvanchery** (Chennai South Suburbs)
  6. **Navalur** (OMR / IT Corridor)
* **Specialty Expansion**:
  7. **IVF Clinics Network** (Fertility & Reproductive Medicine Centers)

---

## 🚀 Key Features

1. **XTEND DB2 Near-Real-Time Ingestion**: Replicates `XTEND.HISTORY_1` call logs every 5 seconds into PostgreSQL.
2. **SLM Mobile Application**:
   * Instant Push Notifications via Firebase Cloud Messaging (FCM).
   * Patient triage & one-touch phone/WhatsApp contact.
   * Doctor consultation & OPD/Surgery slot fixing.
   * In-App Call Recording Audio Stream playback.
   * Offline SQLite queue for hospital ICU/OT areas.
3. **Multi-Branch Auto-Routing**: Dynamic routing engine based on caller branch selection, medical department, and SLM shift availability.
4. **SLM Activity Monitoring & Governance**:
   * First Response TAT tracking (< 15 mins SLA).
   * Automated 3-tier SLA escalation matrix.
   * Call recording quality audit portal for Branch Heads.
   * Weighted SLM Monthly Performance Scorecard.

---

## 🛠️ Repository Structure

```
ph-callcenter-slm-app/
├── backend/                  # FastAPI Python backend & DB sync engine
│   ├── app/                  # Main FastAPI application & models
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + Vite Interactive Web & SLM Mobile Simulator
│   ├── src/
│   │   └── components/       # Dashboard & Mobile Simulator components
│   ├── package.json
│   └── vite.config.js
└── docs/                     # Architecture & Governance Documentation
    ├── ARCHITECTURE.md
    └── SLM_ROLES_MONITORING.md
```

---

## 💻 Local Setup & Execution

### 1. Frontend & Interactive Dashboard Simulator
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend FastAPI Service
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

*Developed for Prashanth Hospitals Leadership, Operations, and IT Teams.*

Production operators must follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The
current XTEND, HIS, FCM, SMS, and WhatsApp endpoints are simulation adapters and
require vendor connectors before they can be considered live integrations.
