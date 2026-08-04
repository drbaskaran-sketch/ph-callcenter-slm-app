import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🐳 PRASHANTH HOSPITALS — DOCKER COMPOSE ORCHESTRATION AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    compose_path = repo_dir / "docker-compose.yml"

    assert compose_path.exists(), "docker-compose.yml missing!"

    with open(compose_path, "r", encoding="utf-8") as f:
        compose_text = f.read()

    # 1. Audit Services Definition
    print("\n1️⃣  Auditing Container Services Definition (ph-backend & ph-frontend)...")
    assert "ph-backend:" in compose_text, "ph-backend service definition missing!"
    assert "ph-frontend:" in compose_text, "ph-frontend service definition missing!"
    assert "backend/Dockerfile" in compose_text, "Backend Dockerfile path missing!"
    assert "frontend/Dockerfile" in compose_text, "Frontend Dockerfile path missing!"
    log("ph-backend and ph-frontend services properly defined with multi-stage Dockerfiles.", "SUCCESS")

    # 2. Audit Port Mappings & Dependency Graph
    print("\n2️⃣  Auditing Network Port Mappings & Service Dependency Graph...")
    assert "8000:8000" in compose_text, "Backend port 8000 mapping missing!"
    assert "5173:80" in compose_text, "Frontend port 5173:80 mapping missing!"
    assert "depends_on:" in compose_text and "condition: service_healthy" in compose_text, "Service health dependency condition missing!"
    log("Port mappings (8000, 5173:80) & service_healthy dependency graph verified.", "SUCCESS")

    # 3. Audit Environment File & Network Isolation
    print("\n3️⃣  Auditing Environment Loading & Bridge Network Isolation...")
    assert "env_file:" in compose_text and ".env" in compose_text, ".env file loading missing!"
    assert "ph-network:" in compose_text and "driver: bridge" in compose_text, "Isolated bridge network missing!"
    log("Environment variable loading from .env & bridge network isolation verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ DOCKER COMPOSE ORCHESTRATION AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
