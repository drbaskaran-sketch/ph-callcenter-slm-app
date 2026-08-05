import urllib.request
import json
import time
from test_auth_helper import install_auth_opener

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    base_backend = "http://localhost:8000"
    base_frontend = "http://localhost:5173"
    install_auth_opener(base_backend)

    print("=" * 80)
    print("🏥 PRASHANTH HOSPITALS — LIVE HEALTH & XTEND DB2 API AUDIT")
    print("=" * 80)

    # 1. Audit Live DB Connection Pool & XTEND DB2 Hub Connection
    print("\n1️⃣  Auditing Operational DB Connection Pool & XTEND DB2 Hub Status...")
    req = urllib.request.Request(f"{base_backend}/api/v1/db/pool-status")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        pool_data = json.loads(res.read().decode('utf-8'))
        log(f"Pool Class: {pool_data.get('pool_class')}", "INFO")
        log(f"Pool Size: {pool_data.get('pool_size')} | Checked In: {pool_data.get('checked_in')} | Checked Out: {pool_data.get('checked_out')} | Overflow: {pool_data.get('overflow')}", "INFO")
        assert "Healthy" in pool_data.get("status", ""), "Connection pool unhealthy!"
        log(f"Database Connection Pool Status: {pool_data.get('status')}", "SUCCESS")

    # 2. Audit Public REST API Endpoints via Backend Container
    print("\n2️⃣  Auditing Public REST API Endpoints via FastAPI Container (port 8000)...")
    endpoints = [
        ("/api/v1/branches", "Multi-Branch Matrix API"),
        ("/api/v1/slms", "SLM Roster & SLA Metrics API"),
        ("/api/v1/enquiries", "Patient Lead Queue API"),
        ("/api/v1/analytics/overview", "Leadership Analytics Overview API")
    ]
    for path, name in endpoints:
        req = urllib.request.Request(f"{base_backend}{path}")
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            data = json.loads(res.read().decode('utf-8'))
            log(f"[200 OK] {name} ➔ Returned {len(data) if isinstance(data, list) else 'structured'} items.", "SUCCESS")

    # 3. Audit Live Call Audio Streaming Proxy API
    print("\n3️⃣  Auditing Live Call Audio Streaming Proxy API...")
    req = urllib.request.Request(f"{base_backend}/api/v1/recordings/wav_8801.wav")
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        assert res.headers.get("Content-Type") == "audio/wav"
        content_len = len(res.read())
        log(f"[200 OK] Live Call WAV Stream ➔ Streaming {content_len / (1024*1024):.2f} MB audio binary.", "SUCCESS")

    # 4. Audit Nginx Frontend Reverse Proxy (port 5173)
    print("\n4️⃣  Auditing Nginx Reverse Proxy Web Server (port 5173)...")
    for path, name in endpoints:
        req = urllib.request.Request(f"{base_frontend}{path}")
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            log(f"[200 OK] Nginx Reverse Proxy {name} ➔ {path}", "SUCCESS")

    # 5. Audit Real-time XTEND DB2 Call Ingestion
    print("\n5️⃣  Auditing Real-time Patient Call Ingestion & Regional Branch Matrix Routing...")
    payload = json.dumps({
        "callerPhone": "+919876543210",
        "callerName": "Deepak Raj",
        "region": "Velachery",
        "department": "Orthopedics",
        "audioFile": "wav_8801.wav"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base_backend}/api/v1/xtend/simulate-call", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        result = json.loads(res.read().decode('utf-8'))
        enq = result['enquiry']
        log(f"[200 OK] Patient Lead Ingested: {enq['patientName']} ({enq['id']}) ➔ Routed to {enq['branchCode']} branch.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ LIVE HEALTH & XTEND DB2 API AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
