#!/bin/bash
# =====================================================================
# PRASHANTH HOSPITALS — LOCAL CONTAINER BUILD & REGISTRY PUSH SCRIPT
# =====================================================================

REGISTRY=${1:-"ghcr.io/drbaskaran-sketch"}
TAG=${2:-"latest"}

BACKEND_IMAGE="$REGISTRY/ph-slm-backend:$TAG"
FRONTEND_IMAGE="$REGISTRY/ph-slm-frontend:$TAG"

echo "=========================================================================="
echo "🐳 BUILDING PRODUCTION DOCKER IMAGES"
echo "   • Target Registry: $REGISTRY"
echo "   • Tag: $TAG"
echo "=========================================================================="

echo -e "\n1️⃣  Building FastAPI Backend Container Image..."
docker build -t "$BACKEND_IMAGE" -f backend/Dockerfile .

echo -e "\n2️⃣  Building Vite React Frontend Container Image..."
docker build -t "$FRONTEND_IMAGE" -f frontend/Dockerfile .

echo -e "\n=========================================================================="
echo "✅ DOCKER IMAGES BUILT LOCALLY:"
docker images | grep "ph-slm"

echo -e "\n3️⃣  To push images to container registry, run:"
echo "   docker push $BACKEND_IMAGE"
echo "   docker push $FRONTEND_IMAGE"
echo "=========================================================================="
