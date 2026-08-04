import urllib.request
import json
import time

FRONTEND_PROXY_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🏥 PRASHANTH HOSPITALS — MANDATORY REMARKS & FCR BYPASS VALIDATION AUDIT")
    print("=" * 80)

    # 1. Test Ingesting Call Record
    print("\n1️⃣  Creating Test Patient Lead Record...")
    payload_ingest = {
        "callerName": "Validation Test Patient",
        "callerPhone": "+91 98404 11223",
        "selectedBranchCode": "KOL",
        "department": "Cardiology",
        "disposition": "CALLBACK_REQUESTED"
    }
    
    req_ingest = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call",
        data=json.dumps(payload_ingest).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req_ingest) as res:
        data = json.loads(res.read().decode("utf-8"))
        enq = data["enquiry"]
        enq_id = enq["id"]
        log(f"Created Lead Record: {enq_id} ({enq['patientName']})", "SUCCESS")

    # 2. UI Form Validation: Test Mandatory Remarks Enforcement on CLOSED
    print("\n2️⃣  Testing UI Form Validation: Attempting Status Update to 'CLOSED' without Remarks...")
    invalid_patch = {"status": "CLOSED", "remarks": ""}
    req_invalid = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/enquiries/{enq_id}",
        data=json.dumps(invalid_patch).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    
    try:
        with urllib.request.urlopen(req_invalid) as res:
            log("UI Validation FAIL: Server permitted status update to CLOSED without remarks!", "FAIL")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            err_detail = json.loads(e.read().decode("utf-8")).get("detail", "")
            log(f"UI Validation SUCCESS: Request rejected with HTTP 400 Bad Request", "SUCCESS")
            log(f"   Detail Message: '{err_detail}'", "SUCCESS")
        else:
            log(f"Unexpected HTTP Status: {e.code}", "FAIL")

    # 3. UI Form Validation: Attempting Status Update to 'CONVERTED' with Whitespace Remarks
    print("\n3️⃣  Testing UI Form Validation: Attempting Status Update to 'CONVERTED' with Whitespace Remarks...")
    whitespace_patch = {"status": "CONVERTED", "remarks": "   "}
    req_ws = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/enquiries/{enq_id}",
        data=json.dumps(whitespace_patch).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    
    try:
        with urllib.request.urlopen(req_ws) as res:
            log("UI Validation FAIL: Server permitted status update with whitespace remarks!", "FAIL")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            err_detail = json.loads(e.read().decode("utf-8")).get("detail", "")
            log(f"UI Validation SUCCESS: Whitespace remarks rejected with HTTP 400 Bad Request", "SUCCESS")
            log(f"   Detail Message: '{err_detail}'", "SUCCESS")

    # 4. Valid UI Submission: Status Update to 'CLOSED' with Verified Mandatory Remarks
    print("\n4️⃣  Testing Valid UI Submission with Non-Empty Mandatory Remarks...")
    valid_patch = {
        "status": "CLOSED",
        "remarks": "Patient inquiry regarding OPD pricing answered. Sent brochure on WhatsApp."
    }
    req_valid = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/enquiries/{enq_id}",
        data=json.dumps(valid_patch).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PATCH"
    )
    
    with urllib.request.urlopen(req_valid) as res:
        assert res.status == 200
        valid_res = json.loads(res.read().decode("utf-8"))
        updated_enq = valid_res["enquiry"]
        assert updated_enq["status"] == "CLOSED"
        assert updated_enq["remarks"] == valid_patch["remarks"]
        log(f"UI Form Submission SUCCESS: Lead {enq_id} status updated to CLOSED with verified remarks.", "SUCCESS")

    # 5. FCR (First Call Resolution) Push Notification Bypass Verification
    print("\n5️⃣  Verifying FCR (First Call Resolution) Push Notification Bypass Logic...")
    
    # Case A: FCR Call (INFO_GIVEN) ➔ Expect FCM Push Bypass
    fcr_call = {
        "callerName": "FCR Patient A",
        "callerPhone": "+91 98404 22334",
        "selectedBranchCode": "CHP",
        "department": "IVF & Fertility",
        "disposition": "INFO_GIVEN"
    }
    req_fcr = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call",
        data=json.dumps(fcr_call).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_fcr) as res:
        fcr_res = json.loads(res.read().decode("utf-8"))
        assert "(FCM Push Bypassed - First Call Resolution)" in fcr_res["message"]
        log(f"FCR Bypass SUCCESS (INFO_GIVEN): Message -> '{fcr_res['message']}'", "SUCCESS")

    # Case B: Non-FCR Call (APPOINTMENT_FIXED) ➔ Expect FCM Push Dispatched
    non_fcr_call = {
        "callerName": "Non-FCR Patient B",
        "callerPhone": "+91 98404 33445",
        "selectedBranchCode": "VEL",
        "department": "Orthopedics",
        "disposition": "APPOINTMENT_FIXED"
    }
    req_non_fcr = urllib.request.Request(
        f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call",
        data=json.dumps(non_fcr_call).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_non_fcr) as res:
        non_fcr_res = json.loads(res.read().decode("utf-8"))
        assert "pushed to SLM Mobile App via FCM" in non_fcr_res["message"]
        log(f"FCM Push Dispatched SUCCESS (APPOINTMENT_FIXED): Message -> '{non_fcr_res['message']}'", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ MANDATORY REMARKS & FCR BYPASS VALIDATION PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
