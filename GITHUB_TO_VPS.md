# 🚀 Push to GitHub & Deploy to VPS - Step by Step

**Your Details:**
- GitHub: https://github.com/huyng1801/restobot
- VPS IP: 103.56.160.107
- VPS Password: MsWwkU9CTf6!r!^o(-!Q

---

## ✅ Step 1: Commit & Push to GitHub (On Your Local Machine)

### 1.1 Open Terminal/PowerShell and navigate to project
```bash
cd d:\Outsourcing\Python\Web\RestoBot
```

### 1.2 Initialize Git and configure
```bash
git config --global user.email "your-email@gmail.com"
git config --global user.name "Your Name"

# Check config
git config --global --list
```

### 1.3 Add all Docker files to Git
```bash
git add .
git status  # Review what's being added
```

### 1.4 Create initial commit
```bash
git commit -m "feat: Add Docker setup for production deployment

- Added Dockerfile for FastAPI backend
- Added Dockerfile for Rasa chatbot
- Added Dockerfile for React frontend
- Added docker-compose.yml for production
- Added docker-compose.dev.yml for development
- Added Nginx reverse proxy configuration
- Updated requirements.txt with fixed versions
- Added comprehensive deployment documentation"
```

### 1.5 Connect to GitHub repository
```bash
git remote add origin https://github.com/huyng1801/restobot.git
git branch -M main
```

### 1.6 Push to GitHub
```bash
git push -u origin main
```

**If asked for authentication:**
- **Username**: huyng1801
- **Password**: Use a GitHub Personal Access Token instead of password
  - Go to: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Select scopes: `repo` (full control of private repositories)
  - Copy the token and paste it when prompted

---

## ✅ Step 2: Deploy to VPS

### 2.1 Open Terminal/PowerShell and SSH to VPS
```bash
ssh root@103.56.160.107
```

When prompted for password, enter:
```
MsWwkU9CTf6!r!^o(-!Q
```

### 2.2 You should now be on the VPS terminal
```bash
# You'll see something like: root@vps-name:~#

# Navigate to deployment directory
cd /var/www
```

### 2.3 Clone your repository
```bash
git clone https://github.com/huyng1801/restobot.git
cd restobot
```

### 2.4 Create environment file with strong passwords
```bash
cp .env.example .env
nano .env
```

**In the nano editor, change these values:**
```
# Change these:
DB_PASSWORD=YourVeryStrongPassword123!@#$%
SECRET_KEY=GenerateARandomString32CharsMinimumHere12345
DEBUG=false
```

**How to edit in nano:**
1. Press `Ctrl+O` to find and replace
2. Find: `password` → Replace with your password
3. Find: `your-secret-key` → Replace with random string
4. Find: `DEBUG=true` → Replace with `DEBUG=false`
5. Press `Ctrl+X` to exit
6. Press `Y` to save
7. Press `Enter` to confirm filename

### 2.5 Create frontend environment file
```bash
nano restobot-frontend/.env
```

Update with your VPS IP or domain:
```
REACT_APP_API_URL=http://103.56.160.107:8000
REACT_APP_CHAT_API_URL=http://103.56.160.107:5005
```

Press `Ctrl+X`, `Y`, `Enter` to save

### 2.6 Install Docker (if not already installed)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Or run the provided script:
```bash
bash deploy.sh
```

### 2.7 Build and start Docker containers
```bash
docker-compose build
docker-compose up -d
```

**This will take 5-10 minutes as it downloads and builds all images**

### 2.8 Check if everything is running
```bash
docker-compose ps
```

You should see all containers with status "Up"

### 2.9 Verify deployment
```bash
# Check API health
curl http://localhost:8000/health

# View logs (should show no errors)
docker-compose logs

# Exit logs view: Ctrl+C
```

---

## ✅ Step 3: Access Your Application

### From your local machine:
```bash
# Frontend
http://103.56.160.107

# API Documentation
http://103.56.160.107:8000/docs

# Rasa Chatbot
http://103.56.160.107:5005
```

Or open in browser directly by entering these URLs

---

## ✅ Step 4: Optional - Setup Custom Domain

If you have a domain (e.g., restobot.example.com):

### 4.1 Point domain to your VPS IP
In your domain registrar:
```
Type: A
Name: @
Value: 103.56.160.107

Type: A
Name: www
Value: 103.56.160.107
```

### 4.2 Wait for DNS to propagate (5-30 minutes)
```bash
# Test if domain resolves
nslookup restobot.example.com
```

### 4.3 Setup SSL certificate on VPS
```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

sudo certbot certonly --standalone -d restobot.example.com -d www.restobot.example.com

# Follow the prompts and enter your email
```

### 4.4 Update nginx.conf with SSL
Edit on your local machine and push:
```bash
nano nginx.conf

# Uncomment SSL sections and add:
ssl_certificate /etc/letsencrypt/live/restobot.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/restobot.example.com/privkey.pem;
```

Push changes:
```bash
git add nginx.conf
git commit -m "Setup SSL for restobot.example.com"
git push origin main

# On VPS
cd /var/www/restobot
git pull origin main
docker-compose restart nginx
```

---

## ✅ Step 5: Maintenance

### View logs in real-time
```bash
# On VPS
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f rasa
```

### Update code after making changes locally
```bash
# On your local machine
git add .
git commit -m "Your changes description"
git push origin main

# On VPS
cd /var/www/restobot
git pull origin main
docker-compose build
docker-compose up -d
```

### Restart services
```bash
docker-compose restart
```

### Backup database
```bash
docker-compose exec postgres pg_dump -U postgres restobot_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### View service status
```bash
docker-compose ps
```

### Stop all services
```bash
docker-compose stop
```

### Start all services
```bash
docker-compose start
```

---

## ✅ Security Checklist

After deployment, complete these:

- [ ] Changed `SECRET_KEY` in .env to random 32+ chars
- [ ] Changed `DB_PASSWORD` to strong password
- [ ] Set `DEBUG=false` in .env
- [ ] Tested API at http://103.56.160.107:8000/docs
- [ ] Tested frontend at http://103.56.160.107
- [ ] Tested chatbot at http://103.56.160.107:5005
- [ ] Setup firewall (optional but recommended):
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```
- [ ] Backup database regularly
- [ ] Monitor disk space: `df -h`
- [ ] Monitor memory: `free -h`

---

## 🆘 Troubleshooting

### Can't push to GitHub
**Solution**: Use GitHub Personal Access Token instead of password
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Copy token and use as password

### SSH connection refused
**Solution**: Check IP and password
```bash
ssh -v root@103.56.160.107  # -v for verbose
```

### Docker not found on VPS
**Solution**: Install Docker first
```bash
bash deploy.sh  # This handles installation
```

### Containers won't start
```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill the process if needed
sudo kill -9 <PID>
```

### Can't access application
1. Make sure all containers are running: `docker-compose ps`
2. Check firewall: `sudo ufw status`
3. Check VPS IP: `hostname -I`
4. Test locally: `curl http://localhost:8000/health`

---

## 📞 Support Commands

```bash
# Get IP address of VPS
hostname -I

# Get current user
whoami

# Check which directory you're in
pwd

# List files
ls -la

# View file
cat nginx.conf

# Edit file
nano filename

# Exit VPS
exit

# Copy file from VPS to local
scp root@103.56.160.107:/var/www/restobot/backup.sql ./backup.sql
```

---

## 🎉 Done!

Your RestoBot application is now **live on VPS**! 

**Access:**
- Web App: http://103.56.160.107
- API Docs: http://103.56.160.107:8000/docs
- Chatbot API: http://103.56.160.107:5005

**Next steps:**
1. Test the application
2. Setup custom domain (if you have one)
3. Setup SSL certificate
4. Configure backups
5. Monitor application

Enjoy! 🚀
