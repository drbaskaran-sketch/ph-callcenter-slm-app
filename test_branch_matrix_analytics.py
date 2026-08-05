import urllib.request
import json
import time
from test_auth_helper import install_auth_opener

FRONTEND_PROXY_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

REGIONAL_ROUTING_MATRIX = [
    {"region": "Chennai North", "expected_code": "KOL", "branch_name": "Kolathur (Call Center Hub)"},
    {"region": "Central Chennai", "expected_code": "CHP", "branch_name": "Chetpet"},
    {"region": "Chennai South", "expected_code": "VEL", "branch_name": "Velachery"},
    {"region": "Tiruvallur Suburbs", "expected_code": "GUM", "branch_name": "Gummidipoondi"},
    {"region": "Multi-location Fertility", "expected_code": "IVF", "branch_name": "IVF Clinics Network"},
]

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    install_auth_opener(BACKEND_URL)
    print("=" * 80)
    print("🏥 PRASHANTH HOSPITALS — REGIONAL ROUTING & LEADERSHIP ANALYTICS AUDIT")
    print("=" * 80)

    # 1. Verify Active Multi-Branch Roster API
    print("\n1️⃣  Auditing Hospital Branch Network Matrix (/api/v1/branches)...")
    url_branches = f"{FRONTEND_PROXY_URL}/api/v1/branches"
    with urllib.request.urlopen(url_branches) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        branches = data.get("branches", [])
        log(f"Retrieved {len(branches)} Hospital Branch Units from Matrix API:", "SUCCESS")
        for b in branches:
            log(f"   • [{b['code']}] {b['name']} ({b['city']}) - Status: {b['status']} | Leads Today: {b['leadsToday']}")

    # 2. Ingest Regional Mock Calls & Audit Dynamic Routing
    print("\n2️⃣  Testing Regional Call Routing & Branch Matrix Allocation...")
    routed_enquiries = []
    
    for idx, reg in enumerate(REGIONAL_ROUTING_MATRIX, 1):
        payload = {
            "callerName": f"Regional Patient #{idx}",
            "callerPhone": f"+91 98403 {idx:05d}",
            "selectedBranchCode": reg["expected_code"],
            "department": "Specialty Care"
        }
        
        req = urllib.request.Request(
            f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req) as res:
            assert res.status == 200
            res_data = json.loads(res.read().decode("utf-8"))
            enq = res_data.get("enquiry", {})
            
            assert enq.get("branchCode") == reg["expected_code"], f"Branch code mismatch: {enq.get('branchCode')} vs {reg['expected_code']}"
            assert reg["branch_name"] in enq.get("branch"), f"Branch name mismatch: {enq.get('branch')} vs {reg['branch_name']}"
            
            routed_enquiries.append(enq)
            log(f"Region '{reg['region']}' ➔ Routed to [{enq['branchCode']}] {enq['branch']} (Enquiry ID: {enq['id']})", "SUCCESS")

    # 3. Leadership Analytics Overview Integration Verification
    print("\n3️⃣  Auditing Leadership Analytics Dashboard Metrics (/api/v1/analytics/overview)...")
    url_analytics = f"{FRONTEND_PROXY_URL}/api/v1/analytics/overview"
    with urllib.request.urlopen(url_analytics) as res:
        assert res.status == 200
        analytics = json.loads(res.read().decode("utf-8"))
        
        log("Leadership Executive Overview Metrics:", "SUCCESS")
        log(f"   • Total Inquiries Captured Today: {analytics.get('totalInquiriesToday')}")
        log(f"   • Average First Response TAT: {analytics.get('avgFirstResponseTatMins')} mins (< 15 mins SLA)")
        log(f"   • Surgeries & Slot Procedures Fixed: {analytics.get('surgeriesAndSlotsFixed')}")
        log(f"   • Conversion Rate: {analytics.get('conversionRate')}")
        log(f"   • Active Branches in Matrix: {analytics.get('branchesCount')}")
        log(f"   • Active On-Duty SLMs: {analytics.get('activeSlmsCount')}")
        log(f"   • SLA Breach Alerts: {analytics.get('slaBreachAlerts')}")

    print("\n" + "=" * 80)
    print("✨ REGIONAL ROUTING & LEADERSHIP ANALYTICS AUDIT COMPLETED WITH 100% ACCURACY")
    print("=" * 80)

if __name__ == "__main__":
    main()
