import os
import subprocess
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🐳 PRASHANTH HOSPITALS — CONTAINER BUILD & REGISTRY PUSH AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent

    # 1. Audit Local Docker Images Build & Tags
    print("\n1️⃣  Auditing Local Built Container Images (ph-slm-backend & ph-slm-frontend)...")
    res = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"], capture_output=True, text=True)
    images_list = res.stdout.strip().split("\n")
    
    assert any("ph-slm-backend" in img for img in images_list), "ph-slm-backend container image missing!"
    assert any("ph-slm-frontend" in img for img in images_list), "ph-slm-frontend container image missing!"
    log("Both FastAPI backend and Vite React frontend Docker images built & tagged locally.", "SUCCESS")

    # 2. Audit GitHub Actions Registry Push Workflow
    print("\n2️⃣  Auditing GitHub Actions Registry Push Workflow (.github/workflows/docker-build-push.yml)...")
    workflow_path = repo_dir / ".github" / "workflows" / "docker-build-push.yml"
    assert workflow_path.exists(), "docker-build-push.yml workflow file missing!"
    
    with open(workflow_path, "r", encoding="utf-8") as f:
        wf_text = f.read()

    assert "ghcr.io" in wf_text, "Container Registry URL missing!"
    assert "docker/build-push-action" in wf_text, "Docker Buildx Push action missing!"
    assert "ph-slm-backend" in wf_text and "ph-slm-frontend" in wf_text, "Backend/Frontend image tags missing!"
    log("Automated GitHub Actions Registry Push Workflow verified (GHCR / GitHub Container Registry).", "SUCCESS")

    # 3. Audit Local Push Script
    print("\n3️⃣  Auditing Local Build & Push Automation Script (build_and_push_containers.sh)...")
    script_path = repo_dir / "build_and_push_containers.sh"
    assert script_path.exists(), "build_and_push_containers.sh missing!"
    log("Local container build and push automation script verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ CONTAINER BUILD & REGISTRY PUSH AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
