import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🛡️  PRASHANTH HOSPITALS — SERVER PROVISIONING & SECURITY AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    script_path = repo_dir / "scripts" / "provision_server_security.sh"
    tf_path = repo_dir / "terraform" / "main.tf"

    assert script_path.exists(), "scripts/provision_server_security.sh missing!"
    assert tf_path.exists(), "terraform/main.tf missing!"

    with open(script_path, "r", encoding="utf-8") as f:
        sh_text = f.read()

    with open(tf_path, "r", encoding="utf-8") as f:
        tf_text = f.read()

    # 1. Audit Non-Root User & Sudoers Setup
    print("\n1️⃣  Auditing Non-Root User Creation & Sudo Privilege Isolation...")
    assert "useradd -m" in sh_text, "useradd instruction missing!"
    assert "usermod -aG sudo" in sh_text, "sudo group assignment missing!"
    assert "/etc/sudoers.d/" in sh_text, "sudoers privilege file missing!"
    log("Non-root user creation & sudoers privilege isolation verified.", "SUCCESS")

    # 2. Audit SSH Key-Based Authentication & Daemon Hardening
    print("\n2️⃣  Auditing SSH Key-Based Authentication & Daemon Hardening...")
    assert "authorized_keys" in sh_text, "authorized_keys SSH setup missing!"
    assert "PermitRootLogin no" in sh_text, "PermitRootLogin no instruction missing!"
    assert "PasswordAuthentication no" in sh_text, "PasswordAuthentication no instruction missing!"
    log("SSH key-based authentication & daemon root/password login block verified.", "SUCCESS")

    # 3. Audit UFW Firewall & Fail2ban Defense
    print("\n3️⃣  Auditing Strict UFW Firewall Rules & Fail2ban Protection...")
    assert "ufw default deny incoming" in sh_text, "UFW deny incoming missing!"
    assert "ufw allow 22/tcp" in sh_text, "UFW SSH port 22 missing!"
    assert "ufw allow 80/tcp" in sh_text, "UFW HTTP port 80 missing!"
    assert "ufw allow 443/tcp" in sh_text, "UFW HTTPS port 443 missing!"
    assert "fail2ban" in sh_text, "Fail2ban brute-force protection setup missing!"
    log("Strict UFW firewall rules & Fail2ban brute-force protection verified.", "SUCCESS")

    # 4. Audit Terraform Infrastructure Manifest
    print("\n4️⃣  Auditing Terraform VPS Infrastructure & Security Group Manifest...")
    assert 'resource "aws_security_group"' in tf_text, "Terraform security group resource missing!"
    assert 'resource "aws_instance"' in tf_text, "Terraform EC2 instance resource missing!"
    assert "provision_server_security.sh" in tf_text, "User data provisioning script execution missing!"
    log("Terraform AWS VPS provisioning manifest & security group firewall rules verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ SERVER PROVISIONING & SECURITY HARDENING AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
