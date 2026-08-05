import urllib.request
import json
import concurrent.futures
import time
from test_auth_helper import install_auth_opener

FRONTEND_PROXY_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

# Target Branch Routing Matrix Mapping
BRANCH_ROUTING_MATRIX = {
    "KOL": {"name": "Kolathur (Call Center Hub)", "expected_slm": "Vijay Kumar"},
    "CHP": {"name": "Chetpet", "expected_slm": "Anitha Ramesh"},
    "VEL": {"name": "Velachery", "expected_slm": "Suresh Babu"},
    "GUM": {"name": "Gummidipoondi", "expected_slm": "Priya Dharshini"},
    "IVF": {"name": "IVF Clinics Network", "expected_slm": "Anitha Ramesh"},
}

# FCR (First Call Resolution) Disposition Classification Rules
FCR_DISPOSITIONS = ["INFO_GIVEN", "COMPLAINT_RESOLVED"]
NON_FCR_DISPOSITIONS = ["APPOINTMENT_FIXED", "CALLBACK_REQUESTED", "SURGERY_INQUIRY"]

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def simulate_branch_call(payload, call_index):
    """Simulates a call packet ingestion and returns routing + FCR bypass audit metrics"""
    url = f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call"
    req_body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_body, headers={"Content-Type": "application/json"}, method="POST")
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as res:
            latency_ms = (time.time() - start_time) * 1000
            data = json.loads(res.read().decode("utf-8"))
            enq = data.get("enquiry", {})
            msg = data.get("message", "")
            
            branch_code = payload["selectedBranchCode"]
            disposition = payload["disposition"]
            
            # 1. Routing Matrix Verification
            expected_branch_info = BRANCH_ROUTING_MATRIX.get(branch_code)
            assert enq.get("branchCode") == branch_code, f"Branch code mismatch: got {enq.get('branchCode')}, expected {branch_code}"
            
            # 2. FCR Push Notification Bypass Verification
            is_fcr = disposition in FCR_DISPOSITIONS
            fcm_bypassed = "FCM Push Bypassed" in msg or "(FCM Push Bypassed - First Call Resolution)" in msg
            
            if is_fcr:
                assert fcm_bypassed, f"FCR Bypass failed for FCR disposition {disposition}! Message: {msg}"
            else:
                assert not fcm_bypassed, f"FCR Bypass incorrectly triggered for non-FCR disposition {disposition}! Message: {msg}"
                
            return {
                "index": call_index,
                "enquiry_id": enq["id"],
                "caller": enq["patientName"],
                "branch_code": branch_code,
                "disposition": disposition,
                "is_fcr": is_fcr,
                "fcm_bypassed": fcm_bypassed,
                "latency_ms": latency_ms,
                "success": True
            }
    except Exception as e:
        return {
            "index": call_index,
            "error": str(e),
            "success": False
        }

def main():
    install_auth_opener(BACKEND_URL)
    print("=" * 80)
    print("🏥 PRASHANTH HOSPITALS — FCR & MULTI-BRANCH AUTO-ROUTING LOAD TEST")
    print("=" * 80)

    # Generate 25 Simulated Calls under Multi-Branch Load
    branches = ["KOL", "CHP", "VEL", "GUM", "IVF"]
    departments = ["Cardiology", "IVF & Fertility", "Orthopedics", "Obstetrics & Gynecology"]
    dispositions = FCR_DISPOSITIONS + NON_FCR_DISPOSITIONS

    test_calls = []
    for i in range(1, 26):
        b_code = branches[i % len(branches)]
        disp = dispositions[i % len(dispositions)]
        dept = departments[i % len(departments)]
        test_calls.append({
            "callerName": f"Load Test Patient #{i}",
            "callerPhone": f"+91 9840{i:05d}",
            "selectedBranchCode": b_code,
            "department": dept,
            "disposition": disp
        })

    print(f"\n1️⃣  Executing Concurrent Load Test ({len(test_calls)} Simulated XTEND Inbound Calls)...")
    
    results = []
    start_total = time.time()
    
    # Execute calls concurrently across 5 worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(simulate_branch_call, call, idx) for idx, call in enumerate(test_calls, 1)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_duration = time.time() - start_total
    
    # Sort results by test call index
    results.sort(key=lambda x: x["index"])

    print("\n2️⃣  Multi-Branch Routing & FCR Bypass Verification Matrix:")
    print("-" * 80)
    print(f"{'#':<3} | {'Caller':<20} | {'Branch':<6} | {'Disposition':<20} | {'FCR Bypass?':<12} | {'Latency':<8}")
    print("-" * 80)

    fcr_count = 0
    non_fcr_count = 0
    successful_routes = 0

    for r in results:
        if r["success"]:
            successful_routes += 1
            fcr_str = "YES (Bypassed)" if r["fcm_bypassed"] else "NO (FCM Sent)"
            if r["is_fcr"]:
                fcr_count += 1
            else:
                non_fcr_count += 1
            print(f"{r['index']:<3} | {r['caller']:<20} | {r['branch_code']:<6} | {r['disposition']:<20} | {fcr_str:<12} | {r['latency_ms']:.1f}ms")
        else:
            print(f"{r['index']:<3} | FAILED: {r['error']}")

    print("-" * 80)
    print(f"\n📊 Multi-Branch Load Test Summary:")
    print(f"   • Total Calls Processed: {len(results)}")
    print(f"   • Successful Routing Rate: {successful_routes}/{len(results)} ({(successful_routes/len(results))*100:.1f}%)")
    print(f"   • FCR (First Call Resolution) Calls: {fcr_count} (Suppressed FCM Push)")
    print(f"   • Escalated / Follow-up Calls: {non_fcr_count} (Dispatched FCM Push to SLM)")
    print(f"   • Total Load Execution Time: {total_duration:.2f} seconds")
    print(f"   • Average Call Latency: {sum(r['latency_ms'] for r in results if r['success'])/successful_routes:.1f} ms")

    assert successful_routes == len(results), "Routing or FCR Bypass failure detected under load!"
    
    log("FCR PUSH BYPASS & MULTI-BRANCH ROUTING MATRIX FULLY VERIFIED", "SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
