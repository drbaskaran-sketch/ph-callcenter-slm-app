import os
from pathlib import Path

def log(msg, status="INFO"):
    symbol = "ℹ️" if status == "INFO" else ("✅" if status == "SUCCESS" else "❌")
    print(f"{symbol} [{status}] {msg}")

def main():
    print("=" * 80)
    print("🐳 PRASHANTH HOSPITALS — VITE REACT FRONTEND DOCKERFILE AUDIT")
    print("=" * 80)

    repo_dir = Path(__file__).resolve().parent
    dockerfile_path = repo_dir / "frontend" / "Dockerfile"
    nginx_conf_path = repo_dir / "frontend" / "nginx.docker.conf"

    assert dockerfile_path.exists(), "frontend/Dockerfile missing!"
    assert nginx_conf_path.exists(), "frontend/nginx.docker.conf missing!"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        dockerfile_text = f.read()

    with open(nginx_conf_path, "r", encoding="utf-8") as f:
        nginx_conf_text = f.read()

    # 1. Audit Multi-Stage Build Pattern
    print("\n1️⃣  Auditing Multi-Stage Node -> Nginx Build Pattern...")
    assert "AS builder" in dockerfile_text and "node:20-alpine" in dockerfile_text, "Node builder stage missing!"
    assert "AS runner" in dockerfile_text and "nginx:alpine" in dockerfile_text, "Nginx runner stage missing!"
    assert "COPY --from=builder /app/dist /usr/share/nginx/html" in dockerfile_text, "Static build asset copy missing!"
    log("Multi-stage Node.js to Nginx build pattern verified.", "SUCCESS")

    # 2. Audit Nginx Docker Configuration Rules
    print("\n2️⃣  Auditing Nginx Container Configuration & Proxy Rules...")
    assert "try_files $uri $uri/ /index.html;" in nginx_conf_text, "SPA index.html fallback missing!"
    assert "proxy_pass http://ph-backend:8000;" in nginx_conf_text, "Backend container proxy_pass missing!"
    assert "gzip on;" in nginx_conf_text, "Gzip asset compression missing!"
    log("SPA routing fallback, gzip compression, and API proxying rules verified.", "SUCCESS")

    # 3. Audit Health Check & Startup Command
    print("\n3️⃣  Auditing Container Health Check & Startup Command...")
    assert "EXPOSE 80" in dockerfile_text, "EXPOSE 80 missing!"
    assert "HEALTHCHECK" in dockerfile_text, "HEALTHCHECK instruction missing!"
    assert 'CMD ["nginx", "-g", "daemon off;"]' in dockerfile_text, "Nginx daemon off startup missing!"
    log("Port 80 exposure, HTTP health check & Nginx daemon off startup verified.", "SUCCESS")

    print("\n" + "=" * 80)
    print("✨ VITE REACT FRONTEND DOCKERFILE AUDIT PASSED WITH 100% SUCCESS")
    print("=" * 80)

if __name__ == "__main__":
    main()
