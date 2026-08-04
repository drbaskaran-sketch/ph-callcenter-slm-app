import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🌐 PRASHANTH HOSPITALS — NGINX REVERSE PROXY & SSL CONFIGURATION AUDIT")
    print("=" * 80)

    conf_path = Path(__file__).resolve().parent / "nginx" / "ph-slm-app.nginx.conf"
    assert conf_path.exists(), "Nginx config file missing!"

    with open(conf_path, "r", encoding="utf-8") as f:
        conf_text = f.read()

    # 1. Audit HTTP ➔ HTTPS Redirect
    print("\n1️⃣  Auditing HTTP (80) to HTTPS (443) 301 Redirect Policy...")
    assert "listen 80;" in conf_text, "HTTP port 80 listener missing!"
    assert "return 301 https://$host$request_uri;" in conf_text, "301 HTTPS redirect directive missing!"
    log("Port 80 to 443 301 HTTPS redirect policy verified.", "SUCCESS")

    # 2. Audit SSL / TLS Protocols & Security Headers
    print("\n2️⃣  Auditing TLS/SSL Protocols & Security Hardening Headers...")
    assert "listen 443 ssl http2;" in conf_text, "HTTPS port 443 listener missing!"
    assert "ssl_protocols TLSv1.2 TLSv1.3;" in conf_text, "Modern TLS v1.2/v1.3 protocols missing!"
    assert "Strict-Transport-Security" in conf_text, "HSTS security header missing!"
    assert "X-Frame-Options" in conf_text, "X-Frame-Options header missing!"
    assert "X-Content-Type-Options" in conf_text, "X-Content-Type-Options header missing!"
    log("TLS 1.2/1.3 protocol suite & HSTS security headers verified.", "SUCCESS")

    # 3. Audit Frontend Static Build Serving & SPA Fallback
    print("\n3️⃣  Auditing Frontend Static Build Serving (/frontend/dist)...")
    assert "/frontend/dist" in conf_text, "Frontend static dist directory root missing!"
    assert "try_files $uri $uri/ /index.html;" in conf_text, "SPA index.html fallback missing!"
    log("Vite React dist static file serving & SPA routing fallback verified.", "SUCCESS")

    # 4. Audit Backend API Proxy & Audio Streaming Rules
    print("\n4️⃣  Auditing Backend API Proxy (/api/*) & Unbuffered Audio Stream Proxy...")
    assert "location /api/ {" in conf_text, "API proxy location block missing!"
    assert "proxy_pass http://127.0.0.1:8000;" in conf_text, "FastAPI backend upstream proxy_pass missing!"
    assert "location /api/v1/recordings/ {" in conf_text, "Call audio streaming location missing!"
    assert "proxy_buffering off;" in conf_text, "Unbuffered audio streaming directive missing!"
    log("FastAPI reverse proxying & unbuffered audio stream proxy rules verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ NGINX REVERSE PROXY & SSL CONFIGURATION AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
