#!/bin/bash
# Script pour pousser les images Docker sur Docker Hub
# Username: serini

set -e

echo "🐳 Push des images Docker sur Docker Hub (username: serini)"
echo ""

# Variables
DOCKER_USERNAME="serini"
BACKEND_IMAGE="safran-backend-api"
FRONTEND_IMAGE="safran-frontend-ui"
VERSION="latest"

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

# Tag et push backend
echo "🔖 Tag de l'image backend..."
docker tag ${BACKEND_IMAGE}:latest ${DOCKER_USERNAME}/${BACKEND_IMAGE}:${VERSION}
docker tag ${BACKEND_IMAGE}:latest ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v1.0

echo "⬆️  Push de l'image backend..."
docker push ${DOCKER_USERNAME}/${BACKEND_IMAGE}:${VERSION}
docker push ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v1.0

echo ""
echo "✅ Backend image poussée avec succès!"
echo "   - ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest"
echo "   - ${DOCKER_USERNAME}/${BACKEND_IMAGE}:v1.0"
echo ""

# Tag et push frontend
echo "🔖 Tag de l'image frontend..."
docker tag ${FRONTEND_IMAGE}:latest ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:${VERSION}
docker tag ${FRONTEND_IMAGE}:latest ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v1.0

echo "⬆️  Push de l'image frontend..."
docker push ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:${VERSION}
docker push ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v1.0

echo ""
echo "✅ Frontend image poussée avec succès!"
echo "   - ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest"
echo "   - ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:v1.0"
echo ""

echo "🎉 Toutes les images ont été poussées sur Docker Hub!"
echo ""
echo "📦 Images disponibles:"
echo "   docker pull ${DOCKER_USERNAME}/${BACKEND_IMAGE}:latest"
echo "   docker pull ${DOCKER_USERNAME}/${FRONTEND_IMAGE}:latest"
echo ""
