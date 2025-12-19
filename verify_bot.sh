#!/bin/bash
BASE_URL="http://localhost:8000/api"

APP_READY=0
for i in {1..30}; do
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        APP_READY=1
        break
    fi
    echo "Waiting for API..."
    sleep 2
done

if [ $APP_READY -eq 0 ]; then
    echo "❌ API not ready"
    exit 1
fi

check_answer() {
    USER=$1
    PASS=$2
    MSG=$3
    EXPECT=$4
    
    echo "Testing $USER..."
    TOKEN=$(curl -s -X POST $BASE_URL/auth/login -H "Content-Type: application/json" -d "{\"username\": \"$USER\", \"password\": \"$PASS\"}" | jq -r '.access_token')
    
    if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
        echo "❌ Login Failed for $USER"
        return
    fi
    
    RESPONSE=$(curl -s -X POST $BASE_URL/chat -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"message\": \"$MSG\"}")
    ANSWER=$(echo $RESPONSE | jq -r '.answer')
    
    # Clean up newlines for display
    DISPLAY_ANSWER=$(echo "$ANSWER" | tr '\n' ' ')
    
    echo "Q: $MSG"
    echo "A: $DISPLAY_ANSWER"
    
    if echo "$ANSWER" | grep -iq "$EXPECT"; then
        echo "✅ Verified"
    else
        echo "❌ Mismatch (Expected '$EXPECT')"
    fi
    echo "---"
}

echo "=== Testing Greetings (All Users) ==="
USERS=("alice" "bob" "charlie" "david" "emma" "frank")
STRICT_GREETING="Bonjour ! Je suis l'assistant RH virtuel de Serini. Comment puis-je vous aider ?"

for u in "${USERS[@]}"; do
    check_answer "$u" "password" "Bonjour" "$STRICT_GREETING"
done

echo "=== Testing RAG (Specific Users) ==="
check_answer "alice" "password" "Comment déclarer des heures supplémentaires ?" "Via le manager et le portail RH"
check_answer "bob" "password" "Comment poser un congé annuel ?" "La demande se fait via le portail RH"
check_answer "david" "password" "Ai-je accès à la cantine ?" "Oui les stagiaires y ont accès"
