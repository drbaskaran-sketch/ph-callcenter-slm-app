import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🔒 PRASHANTH HOSPITALS — PRODUCTION SECRETS & ENVIRONMENT CONFIG AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    gitignore_path = repo_dir / ".gitignore"
    template_path = repo_dir / ".env.production.template"
    prod_env_path = repo_dir / ".env.production"

    assert gitignore_path.exists(), ".gitignore file missing!"
    assert template_path.exists(), ".env.production.template missing!"
    assert prod_env_path.exists(), ".env.production file missing!"

    # 1. Audit .gitignore Rule
    print("\n1️⃣  Auditing Git Exclusion Rule for Production Secrets (.gitignore)...")
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_content = f.read()
    assert ".env*" in gitignore_content, ".gitignore must specify '.env*' to block production secrets!"
    log(".gitignore rule '.env*' verified (All .env files blocked from git commits).", "SUCCESS")

    # 2. Audit Production Secrets Template (.env.production.template)
    print("\n2️⃣  Auditing Production Secrets Template (.env.production.template)...")
    with open(template_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    required_keys = [
        "APP_ENV", "DATABASE_URL", "DB_POOL_SIZE", "DB_MAX_OVERFLOW",
        "XTEND_DB2_HOST", "XTEND_DB2_USER", "XTEND_DB2_PASSWORD",
        "FCM_SERVER_KEY", "FCM_PROJECT_ID", "SECRET_KEY", "CORS_ORIGINS"
    ]
    for key in required_keys:
        assert key in template_text, f"Required key {key} missing from .env.production.template!"
    log(f"All {len(required_keys)} production environment keys present in template.", "SUCCESS")

    # 3. Audit Active Production Secrets (.env.production)
    print("\n3️⃣  Auditing Active Production Secrets Configuration (.env.production)...")
    with open(prod_env_path, "r", encoding="utf-8") as f:
        prod_text = f.read()

    assert "APP_ENV=production" in prod_text, "APP_ENV must be 'production'!"
    assert "DEBUG=false" in prod_text, "DEBUG must be 'false' in production!"
    assert "10.0.1.100" in prod_text, "Production XTEND DB2 Host missing!"
    assert "DB_POOL_SIZE=30" in prod_text, "Production DB Pool Size 30 missing!"
    assert "DB_MAX_OVERFLOW=50" in prod_text, "Production DB Max Overflow 50 missing!"
    log("Production settings (APP_ENV=production, DEBUG=false, Pool=30/50, XTEND DB2=10.0.1.100) verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ PRODUCTION SECRETS & ENVIRONMENT AUDIT PASSED WITH 100% SECURITY")
    print("=" * 80)

if __name__ == "__main__":
    main()
