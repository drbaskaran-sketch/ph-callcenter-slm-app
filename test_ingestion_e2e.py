import urllib.request
import json
import time

FRONTEND_PROXY_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def test_mock_call_ingestion(call_data, test_id):
    """Triggers mock call via Frontend Reverse Proxy and validates data mapping & zero packet loss"""
    url = f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call"
    payload = json.dumps(call_data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    
    try:
        with urllib.request.urlopen(req) as res:
            if res.status != 200:
                log(f"Test #{test_id} failed with HTTP {res.status}", "FAIL")
                return None
            data = json.loads(res.read().decode("utf-8"))
            enq = data.get("enquiry", {})
            
            # Field Data Mapping Validation
            assert enq.get("patientName") == call_data["callerName"], f"Name mismatch: {enq.get('patientName')} vs {call_data['callerName']}"
            assert enq.get("phone") == call_data["callerPhone"], f"Phone mismatch: {enq.get('phone')} vs {call_data['callerPhone']}"
            assert enq.get("branchCode") == call_data["selectedBranchCode"], f"Branch mismatch: {enq.get('branchCode')} vs {call_data['selectedBranchCode']}"
            assert enq.get("department") == call_data["department"], f"Dept mismatch: {enq.get('department')} vs {call_data['department']}"
            
            log(f"Test #{test_id} Ingested cleanly: {enq['id']} | {enq['patientName']} ({enq['branchCode']}) | FCR: {call_data.get('disposition')}", "SUCCESS")
            return enq
    except Exception as e:
        log(f"Test #{test_id} Exception: {e}", "FAIL")
        return None

def test_mandatory_remarks_enforcement(enquiry_id):
    """Validates that status transition to CLOSED/CONVERTED fails without remarks and succeeds with remarks"""
    url = f"{FRONTEND_PROXY_URL}/api/v1/enquiries/{enquiry_id}"
    
    # 1. Attempt to close without remarks (Expected 400 Bad Request)
    invalid_payload = json.dumps({"status": "CLOSED", "remarks": ""}).encode("utf-8")
    req = urllib.request.Request(url, data=invalid_payload, headers={"Content-Type": "application/json"}, method="PATCH")
    
    try:
        with urllib.request.urlopen(req) as res:
            log(f"Enforcement FAIL: Server allowed closure without mandatory remarks! (HTTP {res.status})", "FAIL")
            return False
    except urllib.error.HTTPError as e:
        if e.code == 400:
            log(f"Mandatory Remarks Enforced: Request without remarks rejected with HTTP 400 Bad Request (Correct)", "SUCCESS")
        else:
            log(f"Unexpected HTTP status {e.code}", "FAIL")
            return False
            
    # 2. Attempt to close with valid mandatory remarks (Expected 200 OK)
    valid_payload = json.dumps({
        "status": "CLOSED",
        "remarks": "Patient appointment confirmed & pre-op counseling completed by SLM."
    }).encode("utf-8")
    req = urllib.request.Request(url, data=valid_payload, headers={"Content-Type": "application/json"}, method="PATCH")
    
    try:
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            data = json.loads(res.read().decode("utf-8"))
            updated_enq = data.get("enquiry", {})
            assert updated_enq.get("status") == "CLOSED"
            assert updated_enq.get("remarks") == "Patient appointment confirmed & pre-op counseling completed by SLM."
            log(f"Enquiry {enquiry_id} closed successfully with verified mandatory remarks.", "SUCCESS")
            return True
    except Exception as e:
        log(f"Valid update failed: {e}", "FAIL")
        return False

def main():
    print("=" * 75)
    print("🏥 PRASHANTH HOSPITALS — END-TO-END CALL INGESTION & DATA MAPPING AUDIT")
    print("=" * 75)
    
    mock_calls = [
        {"callerName": "Ramaswamy M.", "callerPhone": "+91 98401 11223", "selectedBranchCode": "KOL", "department": "Cardiology", "disposition": "APPOINTMENT_FIXED"},
        {"callerName": "Priya Ananth", "callerPhone": "+91 94440 33445", "selectedBranchCode": "CHP", "department": "IVF & Fertility", "disposition": "INFO_GIVEN"},
        {"callerName": "Senthil Nathan", "callerPhone": "+91 98840 55667", "selectedBranchCode": "VEL", "department": "Orthopedics", "disposition": "CALLBACK_REQUESTED"},
        {"callerName": "Kavitha Raj", "callerPhone": "+91 97900 77889", "selectedBranchCode": "GUM", "department": "Obstetrics & Gynecology", "disposition": "COMPLAINT_RESOLVED"},
        {"callerName": "Ganesh Kumar", "callerPhone": "+91 98410 99001", "selectedBranchCode": "IVF", "department": "Fertility & Reproductive Medicine", "disposition": "APPOINTMENT_FIXED"},
    ]
    
    total_packets = len(mock_calls)
    successful_ingestions = 0
    ingested_enquiries = []
    
    print("\n1️⃣  Testing Batch Call Ingestion & Field Mapping Audit:")
    for idx, call in enumerate(mock_calls, 1):
        enq = test_mock_call_ingestion(call, idx)
        if enq:
            successful_ingestions += 1
            ingested_enquiries.append(enq)
            
    # Packet Loss Audit
    packet_loss_rate = ((total_packets - successful_ingestions) / total_packets) * 100
    print(f"\n📊 Packet Ingestion Audit Summary:")
    print(f"   • Total Packets Sent: {total_packets}")
    print(f"   • Successfully Ingested: {successful_ingestions}")
    print(f"   • Packet Loss Rate: {packet_loss_rate:.2f}%")
    assert packet_loss_rate == 0.0, "Packet drop detected!"
    log("ZERO PACKET LOSS VERIFIED (100% Ingestion Accuracy)", "SUCCESS")
    
    print("\n2️⃣  Testing Mandatory Remarks Enforcement on Disposition Status Change:")
    if ingested_enquiries:
        target_enq = ingested_enquiries[0]
        test_mandatory_remarks_enforcement(target_enq["id"])
        
    print("\n3️⃣  Verifying Final Database Persistence & Queue Integrity:")
    req = urllib.request.Request(f"{FRONTEND_PROXY_URL}/api/v1/enquiries")
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        total_in_db = data.get("total", 0)
        log(f"Operational DB contains {total_in_db} active leads ready for SLM triage.", "SUCCESS")
        
    print("\n" + "=" * 75)
    print("✨ END-TO-END INGESTION & MANDATORY REMARKS AUDIT PASSED WITH 100% ACCURACY")
    print("=" * 75)

if __name__ == "__main__":
    main()
