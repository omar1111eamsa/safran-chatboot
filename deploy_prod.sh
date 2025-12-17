#!/bin/bash

# HR Chatbot - Production Deployment Script
# This script is designed for FRESH INSTALLATIONS.
# It prioritizes PULLING images from Docker Hub instead of building locally.

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== HR Chatbot PRODUCTION Deployment ===${NC}"

# 1. Pull Latest Images
echo -e "\n${YELLOW}[1/4] Pulling latest images from Docker Hub...${NC}"
docker compose pull
# Note: This will pull 'serini/safran-backend-api:v3.0' and frontend equivalent

# 2. Start Services
echo -e "\n${YELLOW}[2/4] Starting services...${NC}"
docker compose up -d --no-build
# --no-build ensures we use the pulled images

echo -e "${GREEN}Services started. Waiting for health checks...${NC}"

# Health Check Function
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

wait_for_service "ldap"
wait_for_service "ollama"
wait_for_service "backend"

# 3. Initialize Data
echo -e "\n${YELLOW}[3/4] Initializing LDAP Data...${NC}"
./setup-ldap.sh

# 4. Initialize AI Model
echo -e "\n${YELLOW}[4/4] Downloading AI Model...${NC}"
./setup-ollama.sh

echo -e "\n${GREEN}=== Production Deployment Complete! ===${NC}"
echo -e "Application is running on: ${BLUE}http://localhost:5173${NC}"
