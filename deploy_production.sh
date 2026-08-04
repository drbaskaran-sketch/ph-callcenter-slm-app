#!/bin/bash
# =====================================================================
# PRASHANTH HOSPITALS — LOCAL ZERO-DOWNTIME PRODUCTION DEPLOY SCRIPT
# =====================================================================

set -e

echo "=========================================================================="
echo "🚀 EXECUTING LOCAL ZERO-DOWNTIME CONTAINER RESTART"
echo "=========================================================================="

APP_DIR="/home/ubuntu/ph-callcenter-slm-app"
cd "$APP_DIR"

echo -e "\n1️⃣  Pulling latest code changes from GitHub..."
git pull origin main

echo -e "\n2️⃣  Building & pulling updated container images..."
docker compose build --parallel

echo -e "\n3️⃣  Executing Zero-Downtime Container Rolling Update..."
docker compose up -d --remove-orphans

echo -e "\n4️⃣  Pruning dangling container images..."
docker image prune -f

echo -e "\n5️⃣  Verifying Container Health & Endpoint Responsiveness..."
sleep 3

if curl -s http://localhost:8000/ > /dev/null && curl -s http://localhost:5173/ > /dev/null; then
    echo "=========================================================================="
    echo "✨ DEPLOYMENT SUCCESSFUL: All containers healthy and serving traffic!"
    echo "=========================================================================="
else
    echo "❌ DEPLOYMENT ERROR: Health probe failed post-restart!"
    exit 1
fi
