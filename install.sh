#!/bin/bash

# HR Chatbot - Unified Installation Script
# This script handles:
# 1. Building and starting Docker services
# 2. Waiting for services to be ready
# 3. Initializing LDAP data
# 4. Downloading Ollama model

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== HR Chatbot Installation Script ===${NC}"

# 1. Build and Start Docker Services
echo -e "\n${YELLOW}[1/4] Building and starting Docker services...${NC}"
docker compose up -d --build

echo -e "${GREEN}Services started. Waiting for them to be healthy...${NC}"

# Function to check health
wait_for_service() {
    local service=$1
    local max_retries=30
    local count=0
    
    echo -n "Waiting for $service..."
    until [ "$(docker inspect -f '{{.State.Health.Status}}' "hr-$service" 2>/dev/null)" == "healthy" ]; do
        if [ $count -ge $max_retries ]; then
            echo -e "\n${RED}Timeout waiting for $service to be healthy.${NC}"
            exit 1
        fi
        sleep 2
        echo -n "."
        count=$((count+1))
    done
    echo -e " ${GREEN}OK${NC}"
}

# Wait for critical services
wait_for_service "ldap"
wait_for_service "ollama"
wait_for_service "backend"

# 2. Initialize LDAP
echo -e "\n${YELLOW}[2/4] Initializing LDAP users...${NC}"
./setup-ldap.sh

# 3. Initialize Ollama
echo -e "\n${YELLOW}[3/4] Downloading AI Model (this may take a while)...${NC}"
./setup-ollama.sh

# 4. Final Success Message
echo -e "\n${GREEN}=== Installation Complete! ===${NC}"
echo -e "Access the application at: ${BLUE}http://localhost:5173${NC}"
echo -e "Login with: ${BLUE}alice / password${NC}"
