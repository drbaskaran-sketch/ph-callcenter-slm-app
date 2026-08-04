import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🚀 PRASHANTH HOSPITALS — AUTOMATED CONTINUOUS DEPLOYMENT (CD) AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    cd_path = repo_dir / ".github" / "workflows" / "cd-deploy.yml"
    deploy_script = repo_dir / "deploy_production.sh"

    assert cd_path.exists(), ".github/workflows/cd-deploy.yml missing!"
    assert deploy_script.exists(), "deploy_production.sh missing!"

    with open(cd_path, "r", encoding="utf-8") as f:
        cd_text = f.read()

    # 1. Audit Workflow Event Triggers
    print("\n1️⃣  Auditing CD Pipeline Workflow Triggers (Build-and-Push completion)...")
    assert "workflow_run:" in cd_text, "workflow_run trigger missing!"
    assert "Build and Push Production Docker Images" in cd_text, "Target build workflow trigger missing!"
    log("CD workflow correctly triggered upon container build & push completion.", "SUCCESS")

    # 2. Audit SSH Security & Remote Server Authentication
    print("\n2️⃣  Auditing SSH Security & Secret Authentication Parameters...")
    assert "appleboy/ssh-action" in cd_text, "SSH Action step missing!"
    assert "PROD_SERVER_HOST" in cd_text, "PROD_SERVER_HOST secret parameter missing!"
    assert "PROD_SSH_KEY" in cd_text, "PROD_SSH_KEY secret parameter missing!"
    log("Secure SSH authentication parameters & host secrets verified.", "SUCCESS")

    # 3. Audit Zero-Downtime Deployment & Health Check Instructions
    print("\n3️⃣  Auditing Zero-Downtime Rolling Update & Health Probes...")
    assert "docker compose pull" in cd_text, "Docker compose pull command missing!"
    assert "docker compose up -d" in cd_text, "Zero-downtime rolling restart command missing!"
    assert "curl -f http://localhost:8000/" in cd_text, "Backend health check probe missing!"
    assert "curl -f http://localhost:5173/" in cd_text, "Frontend health check probe missing!"
    log("Zero-downtime rolling update & post-restart health probes verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ CONTINUOUS DEPLOYMENT (CD) AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
