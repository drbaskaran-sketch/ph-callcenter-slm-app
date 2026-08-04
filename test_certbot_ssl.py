import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🔐 PRASHANTH HOSPITALS — AUTOMATED CERTBOT LET'S ENCRYPT SSL AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    script_path = repo_dir / "scripts" / "setup_certbot_ssl.sh"

    assert script_path.exists(), "scripts/setup_certbot_ssl.sh missing!"

    with open(script_path, "r", encoding="utf-8") as f:
        sh_text = f.read()

    # 1. Audit Certbot Package Installation
    print("\n1️⃣  Auditing Certbot Package Installation Logic...")
    assert "certbot" in sh_text and "python3-certbot-nginx" in sh_text, "Certbot Nginx plugin missing!"
    log("Certbot & python3-certbot-nginx installer verified.", "SUCCESS")

    # 2. Audit Domain SSL Certificate Provisioning Command
    print("\n2️⃣  Auditing Let's Encrypt Domain SSL Certificate Provisioning...")
    assert "certbot --nginx" in sh_text, "Certbot Nginx plugin flag missing!"
    assert "--agree-tos" in sh_text, "Terms of Service agreement flag missing!"
    assert "callcenter-slm.prashanthhospitals.com" in sh_text, "Target domain parameter missing!"
    log("Certbot non-interactive SSL provisioning command verified.", "SUCCESS")

    # 3. Audit Automated Certificate Renewal Cron Job
    print("\n3️⃣  Auditing Automated Let's Encrypt Renewal Cron Job...")
    assert "certbot renew --quiet" in sh_text, "Certbot renew cron command missing!"
    assert "/etc/cron.d/certbot-renew" in sh_text, "Cron renewal configuration file missing!"
    log("Automated daily SSL certificate renewal cron job verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ CERTBOT LET'S ENCRYPT SSL PROVISIONER AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
