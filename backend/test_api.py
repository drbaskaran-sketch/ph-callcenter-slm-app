import urllib.request
import json
import random

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, path, data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    req_body = json.dumps(data).encode("utf-8") if data else None
    
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            content = response.read()
            try:
                text_body = content.decode("utf-8")
                res_json = json.loads(text_body)
                print(f"✅ [{status}] {method} {path} - {name}")
                print("   Response:", json.dumps(res_json, indent=2)[:250] + "...")
            except Exception:
                print(f"✅ [{status}] {method} {path} - {name} (Binary Audio WAV response: {len(content)} bytes)")
            return True
    except Exception as e:
        print(f"❌ {method} {path} - {name} failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🏥 PRASHANTH HOSPITALS — BACKEND API SUITE TEST")
    print("=" * 60)

    test_endpoint("Root Endpoint", "GET", "/")
    test_endpoint("Get All Branches", "GET", "/api/v1/branches")
    
    rnd_code = f"T{random.randint(10, 99)}"
    test_endpoint("Create New Branch Unit", "POST", "/api/v1/branches", {
        "code": rnd_code,
        "name": f"Expansion Unit {rnd_code}",
        "city": "Chennai",
        "type": "FERTILITY",
        "status": "ACTIVE"
    })
    
    test_endpoint("Get SLM Roster", "GET", "/api/v1/slms")
    test_endpoint("Get All Enquiries", "GET", "/api/v1/enquiries")
    test_endpoint("Filter Enquiries by Branch (KOL)", "GET", "/api/v1/enquiries?branchCode=KOL")
    test_endpoint("Simulate XTEND Call Ingestion (Kolathur Hub)", "POST", "/api/v1/xtend/simulate-call", {
        "callerPhone": "+91 99999 88888",
        "callerName": "Test Patient Vijay",
        "selectedBranchCode": "CHP",
        "department": "Cardiology"
    })
    test_endpoint("Update Enquiry Disposition Status", "PATCH", "/api/v1/enquiries/ENQ-2026-8801", {
        "status": "SURGERY_FIXED",
        "notes": "Automated verification test completed."
    })
    test_endpoint("Simulate SLA Escalation to Branch Head", "POST", "/api/v1/enquiries/ENQ-2026-8801/simulate-escalation")
    test_endpoint("Get Leadership Analytics Overview", "GET", "/api/v1/analytics/overview")
    test_endpoint("Get Call Recording Audio Stream", "GET", "/api/v1/recordings/wav_8801.wav")

if __name__ == "__main__":
    main()
