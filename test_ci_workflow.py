import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🐙 PRASHANTH HOSPITALS — GITHUB ACTIONS CI WORKFLOW AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    ci_path = repo_dir / ".github" / "workflows" / "resilience-ci.yml"

    assert ci_path.exists(), ".github/workflows/resilience-ci.yml missing!"

    with open(ci_path, "r", encoding="utf-8") as f:
        ci_text = f.read()

    # 1. Audit Workflow Triggers
    print("\n1️⃣  Auditing GitHub Action Event Triggers (push & pull_request)...")
    assert "push:" in ci_text and "pull_request:" in ci_text, "Push/PR triggers missing!"
    assert "main" in ci_text, "Target main branch trigger missing!"
    log("Push and Pull Request triggers on 'main' branch verified.", "SUCCESS")

    # 2. Audit Automated Resilience & Stress Test Execution
    print("\n2️⃣  Auditing Automated Resilience Test Suite Execution (test_audio_resilience_stress.py)...")
    assert "test_audio_resilience_stress.py" in ci_text, "test_audio_resilience_stress.py execution step missing!"
    log("Audio stream resilience & socket exception test suite registered in CI pipeline.", "SUCCESS")

    # 3. Audit Full Test Matrix Coverage
    print("\n3️⃣  Auditing Complete Integration Test Matrix Coverage...")
    test_scripts = [
        "test_e2e_endpoints.py",
        "test_ingestion_e2e.py",
        "test_fcr_routing_load.py",
        "test_branch_matrix_analytics.py",
        "test_ui_form_validation_fcr.py",
        "test_db_connection_pooling.py",
        "test_environment_config.py",
        "test_backend_dockerfile.py",
        "test_frontend_dockerfile.py",
        "test_docker_compose.py",
        "test_nginx_ssl_config.py"
    ]
    for script in test_scripts:
        assert script in ci_text, f"Test script {script} missing from CI pipeline!"
    log(f"All {len(test_scripts)} integration test suites registered in CI pipeline.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ GITHUB ACTIONS CI WORKFLOW AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
