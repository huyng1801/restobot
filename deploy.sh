#!/bin/bash

# RestoBot Docker Deployment Script for Linux VPS
# This script automates the deployment process

set -e  # Exit on error

echo "=========================================="
echo "🚀 RestoBot Docker Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   echo "Run with: sudo bash deploy.sh"
   exit 1
fi

echo -e "${YELLOW}Step 1: Installing Docker and Docker Compose...${NC}"

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

echo -e "${GREEN}✓ Docker installed successfully${NC}"

# Add current user to docker group
echo -e "${YELLOW}Step 2: Configuring Docker permissions...${NC}"
usermod -aG docker $(whoami)
newgrp docker

echo -e "${GREEN}✓ Docker configured${NC}"

echo -e "${YELLOW}Step 3: Installing additional tools...${NC}"

# Install Git
apt-get install -y git

# Install certbot for SSL (optional but recommended)
apt-get install -y certbot python3-certbot-nginx

# Install htop for monitoring
apt-get install -y htop

echo -e "${GREEN}✓ Additional tools installed${NC}"

echo -e "${YELLOW}Step 4: Cloning RestoBot repository...${NC}"

# Create deployment directory
mkdir -p /var/www/
cd /var/www/

# Check if already cloned
if [ -d "restobot" ]; then
    echo "RestoBot already exists, pulling latest changes..."
    cd restobot
    git pull origin main
else
    echo "Cloning RestoBot repository..."
    git clone https://github.com/huyng1801/restobot.git
    cd restobot
fi

echo -e "${GREEN}✓ Repository ready${NC}"

echo -e "${YELLOW}Step 5: Setting up environment files...${NC}"

# Create .env from template
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Created .env file - Please edit with production values:${NC}"
    echo "   nano .env"
    echo "   - Change DB_PASSWORD to a strong password"
    echo "   - Change SECRET_KEY to a random 32+ character string"
    echo "   - Set DEBUG=false"
else
    echo "✓ .env already exists"
fi

# Create frontend .env
if [ ! -f "restobot-frontend/.env" ]; then
    cp restobot-frontend/.env.example restobot-frontend/.env
    echo -e "${YELLOW}⚠️  Created frontend .env - Update API URLs if needed${NC}"
    echo "   nano restobot-frontend/.env"
else
    echo "✓ Frontend .env already exists"
fi

echo -e "${GREEN}✓ Environment files configured${NC}"

echo -e "${YELLOW}Step 6: Building Docker images...${NC}"

# Build images
docker-compose build

echo -e "${GREEN}✓ Docker images built${NC}"

echo -e "${YELLOW}Step 7: Starting services...${NC}"

# Start containers
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start (30 seconds)..."
sleep 30

echo -e "${GREEN}✓ Services started${NC}"

echo -e "${YELLOW}Step 8: Verifying deployment...${NC}"

# Check if containers are running
if docker-compose ps | grep -q "restobot_api.*Up"; then
    echo -e "${GREEN}✓ API container is running${NC}"
else
    echo -e "${RED}✗ API container failed to start${NC}"
fi

if docker-compose ps | grep -q "restobot_frontend.*Up"; then
    echo -e "${GREEN}✓ Frontend container is running${NC}"
else
    echo -e "${RED}✗ Frontend container failed to start${NC}"
fi

if docker-compose ps | grep -q "restobot_postgres.*Up"; then
    echo -e "${GREEN}✓ Database container is running${NC}"
else
    echo -e "${RED}✗ Database container failed to start${NC}"
fi

if docker-compose ps | grep -q "restobot_rasa.*Up"; then
    echo -e "${GREEN}✓ Rasa container is running${NC}"
else
    echo -e "${RED}✗ Rasa container failed to start${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://$(hostname -I | awk '{print $1}')"
echo "   API Docs: http://$(hostname -I | awk '{print $1}')/docs"
echo "   Rasa: http://$(hostname -I | awk '{print $1}')/rasa"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   View specific service: docker-compose logs -f api"
echo "   Restart services: docker-compose restart"
echo "   Stop services: docker-compose stop"
echo "   Start services: docker-compose start"
echo ""
echo "🔒 Optional SSL setup (if you have a domain):"
echo "   sudo certbot certonly --standalone -d your-domain.com"
echo ""
echo "⚠️  Remember to:"
echo "   1. Edit .env with strong passwords"
echo "   2. Configure your domain DNS"
echo "   3. Setup SSL certificate"
echo "   4. Configure firewall (ufw)"
echo "=========================================="
