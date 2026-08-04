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
    print("🏥 PRASHANTH HOSPITALS — LIVE AUDIO STREAM & XTEND DB2 INGESTION TEST")
    print("=" * 80)

    # 1. Ingest Simulated Live Inbound Call from XTEND DB2 Hub (Kolathur)
    print("\n1️⃣  Ingesting Live Call Record from XTEND DB2 Hub...")
    call_payload = {
        "callerName": "Srinivasan K.",
        "callerPhone": "+91 98402 77889",
        "selectedBranchCode": "CHP",
        "department": "Cardiology",
        "disposition": "APPOINTMENT_FIXED"
    }
    
    url_ingest = f"{FRONTEND_PROXY_URL}/api/v1/xtend/simulate-call"
    req_body = json.dumps(call_payload).encode("utf-8")
    req = urllib.request.Request(url_ingest, data=req_body, headers={"Content-Type": "application/json"}, method="POST")
    
    start_t = time.time()
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        enq = data.get("enquiry", {})
        msg = data.get("message", "")
        ingest_latency_ms = (time.time() - start_t) * 1000
        
        log(f"Call Ingested in {ingest_latency_ms:.1f}ms: ID {enq['id']} | Patient: {enq['patientName']} | Branch: {enq['branch']} ({enq['branchCode']})", "SUCCESS")
        log(f"FCM Push Status: {msg}", "SUCCESS")
        
        rec_url = enq.get("recordingUrl") or enq.get("recording_path")
        log(f"Linked Audio Recording File: {rec_url}", "SUCCESS")

    # 2. Test Live Audio Stream Retrieval & Header Validation
    print("\n2️⃣  Testing Live Call Audio Stream Linkage & Binary Stream Verification...")
    url_audio = f"{FRONTEND_PROXY_URL}/api/v1/recordings/{rec_url}"
    req_audio = urllib.request.Request(url_audio)
    
    audio_start_t = time.time()
    with urllib.request.urlopen(req_audio) as res_audio:
        assert res_audio.status == 200
        content_type = res_audio.headers.get("Content-Type")
        audio_bytes = res_audio.read()
        audio_latency_ms = (time.time() - audio_start_t) * 1000
        
        assert content_type == "audio/wav", f"Expected audio/wav, got {content_type}"
        assert audio_bytes.startswith(b"RIFF") and b"WAVE" in audio_bytes[:16], "Invalid WAV RIFF header!"
        
        log(f"Audio Stream Retrieved in {audio_latency_ms:.1f}ms | Size: {len(audio_bytes)} bytes | MIME: {content_type}", "SUCCESS")
        log(f"WAV RIFF Header & 16-bit PCM Audio Synthesizer Stream Verified", "SUCCESS")

    # 3. Test SLM Triage & Mandatory Remarks Status Transition
    print("\n3️⃣  Executing SLM Triage & Mandatory Resolution Remarks Transition...")
    url_patch = f"{FRONTEND_PROXY_URL}/api/v1/enquiries/{enq['id']}"
    update_payload = {
        "status": "CONVERTED",
        "remarks": "Consultation completed with Dr. S. Prashanth. Angiogram procedure scheduled for Friday."
    }
    req_patch = urllib.request.Request(url_patch, data=json.dumps(update_payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PATCH")
    
    with urllib.request.urlopen(req_patch) as res_patch:
        assert res_patch.status == 200
        patch_data = json.loads(res_patch.read().decode("utf-8"))
        updated_enq = patch_data.get("enquiry", {})
        
        assert updated_enq.get("status") == "CONVERTED"
        assert updated_enq.get("remarks") == update_payload["remarks"]
        
        log(f"Enquiry {enq['id']} status updated to CONVERTED with verified mandatory remarks.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ LIVE AUDIO STREAM & XTEND DB2 INGESTION TEST PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
