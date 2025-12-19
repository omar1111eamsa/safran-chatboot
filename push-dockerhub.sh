#!/bin/bash
# Script pour pousser les images Docker sur Docker Hub avec versioning
# Username: safran

set -e

echo "🐳 Push des images Docker sur Docker Hub (username: safran)"
echo ""

# Variables
DOCKER_USERNAME="safran"
BACKEND_IMAGE="safran-backend-api"
FRONTEND_IMAGE="safran-frontend-ui"

# Versions
VERSION_NEW="v2.0"  # Nouvelle version avec Ollama
VERSION_OLD="v1.0"  # Ancienne version (déjà sur Docker Hub)

# Vérifier si l'utilisateur est connecté à Docker Hub
echo "📝 Vérification de la connexion Docker Hub..."
if ! docker info | grep -q "Username: ${DOCKER_USERNAME}"; then
    echo "⚠️  Vous n'êtes pas connecté à Docker Hub."
    echo "Connexion à Docker Hub..."
    docker login -u ${DOCKER_USERNAME}
fi

echo ""
echo "✅ Connecté à Docker Hub"
echo ""

echo "📋 Résumé des versions:"
echo "  - v1.0: Version sans Ollama (déjà sur Docker Hub)"
echo "  - v2.0: Nouvelle version avec Ollama LLM"
echo ""

# Tag et push backend v2.0
echo "🔖 Tag de l'image backend (v2.0)..."
docker tag ${BACKEND_IMAGE}:latest ${DOCKER_USERNAME}/${BACKEND_IMAGE}:${VERSION_NEW}
docker tag ${BACKEND_IMAGE}:latest ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest

echo "⬆️  Push de l'image backend..."
docker push ${DOCKER_USERNAME}/${BACKEND_IMAGE}:${VERSION_NEW}
docker push ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest

echo ""
echo "✅ Backend image poussée avec succès!"
echo "   - ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest"
echo "   - ${DOCKER_USERNAME}/${BACKEND_IMAGE}:${VERSION_NEW}"
echo ""

# Tag et push frontend v2.0
echo "🔖 Tag de l'image frontend (v2.0)..."
docker tag ${FRONTEND_IMAGE}:latest ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:${VERSION_NEW}
docker tag ${FRONTEND_IMAGE}:latest ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest

echo "⬆️  Push de l'image frontend..."
docker push ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:${VERSION_NEW}
docker push ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest

echo ""
echo "✅ Frontend image poussée avec succès!"
echo "   - ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest"
echo "   - ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:${VERSION_NEW}"
echo ""

echo "🎉 Toutes les images ont été poussées sur Docker Hub!"
echo ""
echo "📦 Images disponibles:"
echo ""
echo "Version 2.0 (avec Ollama):"
echo "  docker pull ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v2.0"
echo "  docker pull ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v2.0"
echo ""
echo "Version 1.0 (sans Ollama - toujours disponible):"
echo "  docker pull ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v1.0"
echo "  docker pull ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v1.0"
echo ""
echo "Latest (pointe vers v2.0):"
echo "  docker pull ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest"
echo "  docker pull ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest"
echo ""
