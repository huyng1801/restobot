#!/bin/bash

# RestoBot Update Script for Linux VPS
# Run this to pull latest code and restart services

set -e

cd /var/www/restobot

echo "🔄 Updating RestoBot..."

# Pull latest code
echo "Pulling latest changes from GitHub..."
git pull origin main

# Rebuild images if there are changes
echo "Rebuilding Docker images..."
docker-compose build

# Restart services
echo "Restarting services..."
docker-compose up -d

# Wait for services
sleep 10

# Check status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "✅ Update complete!"
echo "View logs: docker-compose logs -f"
