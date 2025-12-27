#!/usr/bin/env bash

# 🎯 RestoBot Deployment Checklist
# Copy and follow each step in order

echo "════════════════════════════════════════════════════════"
echo "🎯 RestoBot Deployment Checklist"
echo "════════════════════════════════════════════════════════"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}PART 1: Prepare Code Locally (Your Machine)${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Step 1.1: Open Terminal and navigate to project"
echo "  Command: cd d:\\Outsourcing\\Python\\Web\\RestoBot"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.2: Configure Git"
echo "  Commands:"
echo "    git config --global user.email \"your-email@gmail.com\""
echo "    git config --global user.name \"Your Name\""
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.3: Add all files to Git"
echo "  Command: git add ."
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.4: Commit changes"
echo "  Command: git commit -m \"feat: Add Docker setup for production\""
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.5: Connect to GitHub"
echo "  Command: git remote add origin https://github.com/huyng1801/restobot.git"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.6: Set main branch"
echo "  Command: git branch -M main"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 1.7: Push to GitHub"
echo "  Command: git push -u origin main"
echo "  When prompted for password, use GitHub Personal Access Token"
echo "  Get it from: https://github.com/settings/tokens"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo -e "${GREEN}✓ Part 1 Complete: Code pushed to GitHub${NC}"
echo ""

echo -e "${BLUE}PART 2: SSH to VPS and Deploy${NC}"
echo "════════════════════════════════════════════════════════"
echo ""

echo "Step 2.1: Open new Terminal/PowerShell"
echo "  Command: ssh root@103.56.160.107"
echo "  Password: MsWwkU9CTf6!r!^o(-!Q"
read -p "Connected? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.2: Navigate to web directory"
echo "  Command: cd /var/www"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.3: Clone your repository"
echo "  Command: git clone https://github.com/huyng1801/restobot.git"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.4: Navigate to project"
echo "  Command: cd restobot"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.5: Create environment file"
echo "  Command: cp .env.example .env"
echo "  Then: nano .env"
echo "  Edit: Change DB_PASSWORD, SECRET_KEY, set DEBUG=false"
echo "  Save: Ctrl+X, Y, Enter"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.6: Create frontend environment file"
echo "  Command: nano restobot-frontend/.env"
echo "  Update API URLs with your VPS IP (103.56.160.107)"
echo "  Save: Ctrl+X, Y, Enter"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.7: Build Docker images (takes 5-10 minutes)"
echo "  Command: docker-compose build"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.8: Start containers"
echo "  Command: docker-compose up -d"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo "Step 2.9: Check status"
echo "  Command: docker-compose ps"
echo "  All containers should show 'Up'"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo -e "${GREEN}✓ Part 2 Complete: Deployed to VPS${NC}"
echo ""

echo -e "${BLUE}PART 3: Verify Deployment${NC}"
echo "════════════════════════════════════════════════════════"
echo ""

echo "Step 3.1: Check API health"
echo "  Command: curl http://localhost:8000/health"
read -p "Did it return success? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then 
    echo -e "${RED}Something went wrong. Check logs: docker-compose logs${NC}"
fi

echo "Step 3.2: View logs (optional)"
echo "  Command: docker-compose logs"
echo "  Exit: Ctrl+C"
read -p "Done? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi

echo -e "${GREEN}✓ Part 3 Complete: Deployment Verified${NC}"
echo ""

echo "════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ ALL STEPS COMPLETE!${NC}"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📍 Your application is now live!"
echo ""
echo "Access from your browser:"
echo "  🌐 Frontend: http://103.56.160.107"
echo "  📚 API Docs: http://103.56.160.107:8000/docs"
echo "  🤖 Rasa: http://103.56.160.107:5005"
echo ""
echo "📖 Useful Documentation:"
echo "  - GITHUB_TO_VPS.md - Detailed step-by-step guide"
echo "  - QUICK_DEPLOY.md - Quick reference"
echo "  - DEPLOYMENT.md - Production deployment guide"
echo "  - DEVELOPMENT.md - Local development guide"
echo ""
echo "📋 Next Steps:"
echo "  1. Test your application"
echo "  2. Setup custom domain (if you have one)"
echo "  3. Setup SSL certificate (optional but recommended)"
echo "  4. Configure backups"
echo "  5. Monitor logs regularly"
echo ""
echo "🆘 Issues?"
echo "  Check: docker-compose logs"
echo "  Read: GITHUB_TO_VPS.md Troubleshooting section"
echo ""
echo "════════════════════════════════════════════════════════"
