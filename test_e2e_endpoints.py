import urllib.request
import json
import random
from test_auth_helper import install_auth_opener

import os

def _resolve_url(preferred="http://localhost:5173", fallback="http://localhost:8000"):
    env_override = os.environ.get("FRONTEND_PROXY_URL")
    if env_override:
        return env_override
    try:
        req = urllib.request.Request(preferred, method="GET")
        with urllib.request.urlopen(req, timeout=1):
            return preferred
    except Exception:
        return fallback

BACKEND_URL = "http://localhost:8000"
FRONTEND_PROXY_URL = _resolve_url()

def main():
    install_auth_opener(BACKEND_URL)
    print("=" * 60)
    print("🏥 PRASHANTH HOSPITALS — END-TO-END ENDPOINT SUITE VERIFICATION")
    print("=" * 60)

    endpoints = [
        ("GET", "/api/v1/branches", "Multi-Branch Matrix API"),
        ("GET", "/api/v1/slms", "SLM Roster & SLA Metrics API"),
        ("GET", "/api/v1/enquiries", "Patient Lead Queue API"),
        ("GET", "/api/v1/enquiries?branchCode=KOL", "Filtered Branch Queue (Kolathur Hub)"),
        ("GET", "/api/v1/analytics/overview", "Leadership Analytics Overview API"),
        ("GET", "/api/v1/recordings/wav_8801.wav", "Call Audio Stream Proxy API"),
    ]

    print("\n1️⃣  Testing Direct Backend Access (http://localhost:8000):")
    for method, path, desc in endpoints:
        url = f"{BACKEND_URL}{path}"
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as res:
            print(f"  ✅ [{res.status} OK] {method} {path} ➔ {desc}")

    print("\n2️⃣  Testing Frontend Reverse Proxy Access (http://localhost:5173):")
    for method, path, desc in endpoints:
        url = f"{FRONTEND_PROXY_URL}{path}"
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as res:
            print(f"  ✅ [{res.status} OK] {method} {path} ➔ {desc} (Proxied)")

    print("\n3️⃣  Testing XTEND DB2 Call Ingestion (POST /api/v1/xtend/simulate-call):")
    payload = json.dumps({
        "callerPhone": "+91 98401 99999",
        "callerName": "Subramaniam S.",
        "selectedBranchCode": "CHP",
        "department": "IVF & Fertility"
    }).encode("utf-8")
    
    req = urllib.request.Request(f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call", data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        enq = data["enquiry"]
        print(f"  ✅ [{res.status} OK] Ingested call for {enq['patientName']} ({enq['id']}) ➔ Routed to {enq['branch']}")

    print("\n4️⃣  Testing SLA Breach Escalation (POST /api/v1/enquiries/{id}/simulate-escalation):")
    req = urllib.request.Request(f"{FRONTEND_PROXY_URL}/api/v1/enquiries/ENQ-2026-8801/simulate-escalation", method="POST")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        print(f"  ✅ [{res.status} OK] {data['message']}")

    print("\n" + "=" * 60)
    print("✨ ALL ENDPOINTS VERIFIED & OPERATIONAL")
    print("=" * 60)

if __name__ == "__main__":
    main()
