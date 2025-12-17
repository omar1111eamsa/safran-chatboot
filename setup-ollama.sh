#!/bin/bash
# Script pour initialiser Ollama avec le modèle llama3.2:3b

set -e

echo "🤖 Initialisation d'Ollama..."
echo ""

# Attendre qu'Ollama soit prêt
echo "⏳ Attente du démarrage d'Ollama..."
sleep 10

# Vérifier si Ollama est accessible
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec hr-ollama ollama list > /dev/null 2>&1; then
        echo "✅ Ollama est prêt!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Tentative $RETRY_COUNT/$MAX_RETRIES..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Erreur: Ollama n'a pas démarré correctement"
    exit 1
fi

echo ""
echo "📥 Téléchargement du modèle llama3.2:3b..."
echo "⚠️  Cela peut prendre quelques minutes (~2 GB)..."
echo ""

# Télécharger le modèle
docker exec hr-ollama ollama pull llama3.2:3b

echo ""
echo "✅ Modèle téléchargé avec succès!"
echo ""

# Vérifier que le modèle est bien installé
echo "📋 Modèles disponibles:"
docker exec hr-ollama ollama list

echo ""
echo "🎉 Ollama est prêt à l'emploi!"
echo ""
echo "Pour tester Ollama manuellement:"
echo "  docker exec -it hr-ollama ollama run llama3.2:3b"
echo ""
