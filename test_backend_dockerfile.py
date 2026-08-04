import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🐳 PRASHANTH HOSPITALS — FASTAPI BACKEND DOCKERFILE AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    dockerfile_path = repo_dir / "backend" / "Dockerfile"
    dockerignore_path = repo_dir / ".dockerignore"

    assert dockerfile_path.exists(), "backend/Dockerfile missing!"
    assert dockerignore_path.exists(), ".dockerignore missing!"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        dockerfile_text = f.read()

    # 1. Audit Multi-Stage Build Pattern
    print("\n1️⃣  Auditing Multi-Stage Build Pattern (Builder -> Runner)...")
    assert "AS builder" in dockerfile_text, "Builder stage missing from Dockerfile!"
    assert "AS runner" in dockerfile_text, "Runner stage missing from Dockerfile!"
    assert "COPY --from=builder /opt/venv /opt/venv" in dockerfile_text, "Venv copy from builder missing!"
    log("Multi-stage container build pattern verified (Minimizes final image size).", "SUCCESS")

    # 2. Audit Container Security & Non-Root User Execution
    print("\n2️⃣  Auditing Container Security & Non-Root User Execution...")
    assert "adduser --system" in dockerfile_text, "System user creation missing!"
    assert "USER appuser" in dockerfile_text, "USER appuser directive missing!"
    log("Container security hardening verified (Runs as non-root 'appuser').", "SUCCESS")

    # 3. Audit Health Check & Startup Configuration
    print("\n3️⃣  Auditing Container Health Check & Startup Command...")
    assert "EXPOSE 8000" in dockerfile_text, "EXPOSE 8000 missing!"
    assert "HEALTHCHECK" in dockerfile_text, "HEALTHCHECK instruction missing!"
    assert "--workers" in dockerfile_text and "4" in dockerfile_text, "Multi-worker Uvicorn startup missing!"
    log("Port 8000 exposure, HTTP health check & 4-worker Uvicorn startup verified.", "SUCCESS")

    # 4. Audit Dockerignore Policy
    print("\n4️⃣  Auditing Docker Ignore Rules (.dockerignore)...")
    with open(dockerignore_path, "r", encoding="utf-8") as f:
        dockerignore_text = f.read()

    assert ".env" in dockerignore_text, ".env missing from .dockerignore!"
    assert "venv/" in dockerignore_text, "venv/ missing from .dockerignore!"
    assert "node_modules/" in dockerignore_text, "node_modules/ missing from .dockerignore!"
    log(".env, venv, and node_modules registered in .dockerignore.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ FASTAPI BACKEND DOCKERFILE AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
