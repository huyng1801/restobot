# 📝 Quick Deployment Guide - RestoBot to VPS

## Prerequisites
✅ Docker setup complete (already done!)
✅ GitHub account 
✅ VPS with Ubuntu/Debian
✅ SSH access to VPS

---

## Step 1: Prepare Code Locally (Your Machine)

### 1.1 Initialize Git (if not already done)
```bash
cd restobot
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
git add .
git commit -m "Initial commit: Docker setup with frontend, backend, Rasa, and PostgreSQL"
```

### 1.2 Add GitHub remote
```bash
git remote add origin https://github.com/huyng1801/restobot.git
git branch -M main
git push -u origin main
```

**Note**: You may need to create a GitHub Personal Access Token (PAT) if using HTTPS.
Instead of password, use: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2: Deploy to VPS

### 2.1 SSH into VPS
```bash
ssh root@103.56.160.107
# Password: MsWwkU9CTf6!r!^o(-!Q
```

### 2.2 Download and run deployment script
```bash
cd /var/www
wget https://raw.githubusercontent.com/huyng1801/restobot/main/deploy.sh
chmod +x deploy.sh
sudo bash deploy.sh
```

**Or manually:**
```bash
cd /var/www
git clone https://github.com/huyng1801/restobot.git
cd restobot
cp .env.example .env
# Edit .env with production values
docker-compose build
docker-compose up -d
```

### 2.3 Configure environment
```bash
nano .env

# Update these values:
DB_PASSWORD=VeryStrongPassword123!@#
SECRET_KEY=your-very-long-32-character-secret-key-here
DEBUG=false

# Save and exit (Ctrl+X, then Y, then Enter)
```

### 2.4 Restart services with new environment
```bash
docker-compose restart
```

---

## Step 3: Verify Deployment

```bash
# Check if all containers are running
docker-compose ps

# View logs (should see no errors)
docker-compose logs

# Test API
curl http://localhost:8000/health

# Or from your local machine
curl http://103.56.160.107:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "RestoBot API"}
```

---

## Step 4: Setup Domain (Optional)

### 4.1 Point domain to VPS IP
In your domain registrar's DNS settings:
```
A record: @ → 103.56.160.107
CNAME: www → @
```

### 4.2 Install SSL certificate
```bash
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (replace your-domain.com)
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# This creates certificates at:
# /etc/letsencrypt/live/your-domain.com/
```

### 4.3 Update nginx.conf with SSL
Edit `nginx.conf` in your local repo:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 4.4 Push changes and redeploy
```bash
# On your local machine
git add nginx.conf
git commit -m "Add SSL configuration"
git push origin main

# On VPS
cd /var/www/restobot
git pull origin main
docker-compose restart nginx
```

---

## Step 5: Ongoing Maintenance

### Update code from GitHub
```bash
cd /var/www/restobot
git pull origin main
docker-compose build
docker-compose up -d
```

Or use the provided update script:
```bash
bash update.sh
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f rasa
docker-compose logs -f postgres
```

### Backup database
```bash
docker-compose exec postgres pg_dump -U postgres restobot_db > backup.sql
```

### Restore database
```bash
docker-compose exec -T postgres psql -U postgres restobot_db < backup.sql
```

---

## Troubleshooting

### Port issues
```bash
# Check what's listening on port 80
sudo netstat -tlnp | grep :80

# Or use
sudo lsof -i :80
```

### Container won't start
```bash
# Check logs
docker-compose logs api

# Rebuild without cache
docker-compose build --no-cache
```

### Database connection error
```bash
# Check database status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### SSL certificate renewal (automated)
```bash
# Create cron job
sudo crontab -e

# Add this line:
0 0 1 * * certbot renew --quiet --post-hook "docker-compose -f /var/www/restobot/docker-compose.yml restart nginx"
```

---

## Security Checklist

- [ ] Changed `SECRET_KEY` in .env (32+ chars)
- [ ] Changed `DB_PASSWORD` to strong password
- [ ] Set `DEBUG=false`
- [ ] Setup firewall rules
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```
- [ ] Setup SSL certificate
- [ ] Configured domain DNS
- [ ] Tested all endpoints
- [ ] Backed up database

---

## Access Your Application

After deployment:

| Service | URL |
|---------|-----|
| Frontend | http://103.56.160.107 or http://your-domain.com |
| API | http://103.56.160.107:8000 |
| API Docs | http://103.56.160.107:8000/docs |
| Rasa | http://103.56.160.107:5005 |

---

## Useful VPS Commands

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Monitor processes
top
# or
htop

# Check network connections
netstat -tlnp

# View system logs
journalctl -u docker -f

# Restart a specific service
docker-compose restart api
```

---

## Still Need Help?

1. Check logs: `docker-compose logs -f`
2. Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
3. Check service health: `docker-compose ps`
4. Test endpoints: `curl http://localhost:8000/health`

---

**Good luck with your deployment! 🚀**
