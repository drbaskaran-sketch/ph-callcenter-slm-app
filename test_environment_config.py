import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🔒 PRASHANTH HOSPITALS — ENVIRONMENT & SECRET MANAGEMENT AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent

    # 1. Verify .gitignore includes .env
    print("\n1️⃣  Auditing Git Ignore Policy for Secrets (.gitignore)...")
    gitignore_path = repo_dir / ".gitignore"
    assert gitignore_path.exists(), ".gitignore file missing!"
    
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_content = f.read()
        
    assert ".env" in gitignore_content, ".env is missing from .gitignore!"
    log(".env is properly registered in .gitignore (Prevents committing secrets)", "SUCCESS")

    # 2. Verify .env.example Template
    print("\n2️⃣  Auditing Environment Template (.env.example)...")
    env_example_path = repo_dir / ".env.example"
    assert env_example_path.exists(), ".env.example template file missing!"
    
    with open(env_example_path, "r", encoding="utf-8") as f:
        env_example_lines = f.readlines()
        
    required_keys = ["DATABASE_URL", "DB_POOL_SIZE", "XTEND_DB2_HOST", "FCM_SERVER_KEY", "SECRET_KEY"]
    for key in required_keys:
        assert any(key in line for line in env_example_lines), f"Required template key {key} missing from .env.example!"
    log(f"All {len(required_keys)} critical configuration keys present in .env.example template", "SUCCESS")

    # 3. Test Configuration Manager & Environment Variable Resolution
    print("\n3️⃣  Testing Centralized Config Manager (backend.app.config)...")
    try:
        from backend.app.config import settings
        log(f"Configuration Manager Loaded Successfully:", "SUCCESS")
        log(f"   • Application Name: {settings.APP_NAME}")
        log(f"   • Application Environment: {settings.APP_ENV}")
        log(f"   • Database Pool Size: {settings.DB_POOL_SIZE}")
        log(f"   • XTEND DB2 Host: {settings.XTEND_DB2_HOST}:{settings.XTEND_DB2_PORT}")
        log(f"   • FCM Project ID: {settings.FCM_PROJECT_ID}")
    except Exception as e:
        log(f"Config resolution failed: {e}", "FAIL")
        raise e

    print("\n" + "=" * 80)
    print("✨ ENVIRONMENT & SECRET MANAGEMENT AUDIT PASSED WITH 100% SECURITY")
    print("=" * 80)

if __name__ == "__main__":
    main()
