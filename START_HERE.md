# 🎯 Start Here - RestoBot Docker Guide

Bạn đã có đầy đủ setup Docker! Chọn đường đi của bạn:

---

## 🚀 Chạy Trên Local (Phát Triển)

Nếu bạn muốn **phát triển** project trên máy local:

```bash
cd restobot
cp .env.example .env
cp restobot-frontend/.env.example restobot-frontend/.env
docker-compose -f docker-compose.dev.yml up --build
```

**Truy cập:**
- Frontend: http://localhost:3000
- API: http://localhost:8000/docs  
- Rasa: http://localhost:5005

📖 **Read**: [DEVELOPMENT.md](DEVELOPMENT.md) - Hướng dẫn chi tiết phát triển

---

## 🌐 Deploy Lên VPS (Production)

Nếu bạn muốn **đẩy lên VPS**:

1. **SSH vào VPS:**
```bash
ssh user@your-vps-ip
cd /var/www/
git clone <your-repo> restobot
cd restobot
```

2. **Setup:**
```bash
cp .env.example .env
nano .env  # Chỉnh sửa password và SECRET_KEY
cp restobot-frontend/.env.example restobot-frontend/.env
nano restobot-frontend/.env  # Chỉnh sửa API URLs
```

3. **Deploy:**
```bash
docker-compose build
docker-compose up -d
```

4. **Truy cập:**
- http://your-vps-ip (Frontend)
- http://your-vps-ip/docs (API Docs)

📖 **Read**: [DEPLOYMENT.md](DEPLOYMENT.md) - Hướng dẫn đầy đủ triển khai VPS

---

## 📚 Documentation Map

```
START_HERE.md  ← You are here!
│
├─► DEVELOPMENT.md (Phát triển local)
│   ├─ Setup services riêng
│   ├─ Debugging
│   ├─ API testing
│   └─ Common workflows
│
├─► DEPLOYMENT.md (VPS production)
│   ├─ Docker Compose orchestration
│   ├─ SSL/HTTPS setup
│   ├─ Database backup
│   ├─ Monitoring
│   └─ Troubleshooting
│
├─► DOCKER_SETUP.md (Quick reference)
│   ├─ File list
│   ├─ Commands
│   └─ Architecture
│
├─► SETUP_COMPLETE.md (Setup summary)
│   ├─ What's included
│   ├─ Features
│   └─ Next steps
│
└─► restobot-frontend/README.md (Frontend docs)
    ├─ Features
    ├─ Project structure
    └─ API integration
```

---

## 🗂️ Created Files Overview

### Docker Configuration (10 files)
✅ Dockerfile (FastAPI backend)  
✅ Dockerfile.rasa (Rasa chatbot)  
✅ restobot-frontend/Dockerfile (React production)  
✅ restobot-frontend/Dockerfile.dev (React dev)  
✅ docker-compose.yml (Production setup)  
✅ docker-compose.dev.yml (Development setup)  
✅ nginx.conf (Reverse proxy)  
✅ .dockerignore (Backend optimization)  
✅ restobot-frontend/.dockerignore (Frontend optimization)  
✅ requirements.txt (Updated with fixed versions)  

### Environment Templates (2 files)
✅ .env.example (Backend config)  
✅ restobot-frontend/.env.example (Frontend config)  

### Documentation (4 files)
✅ DEPLOYMENT.md (550+ lines, complete guide)  
✅ DEVELOPMENT.md (400+ lines, dev guide)  
✅ DOCKER_SETUP.md (Quick reference)  
✅ SETUP_COMPLETE.md (Summary)  

---

## ⚡ Quick Commands

### Development
```bash
# Start all services with hot reload
docker-compose -f docker-compose.dev.yml up --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop all
docker-compose -f docker-compose.dev.yml down
```

### Production  
```bash
# Build and start
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

---

## 🎯 Next 5 Minutes

Choose one:

### 👤 I want to **develop locally**
1. Read: [DEVELOPMENT.md](DEVELOPMENT.md)
2. Run: `docker-compose -f docker-compose.dev.yml up --build`
3. Open: http://localhost:3000

### 🚀 I want to **deploy to VPS**
1. Read: [DEPLOYMENT.md](DEPLOYMENT.md)
2. SSH to VPS and clone repo
3. Follow deployment steps in guide

### ❓ I want to **understand the setup**
1. Read: [DOCKER_SETUP.md](DOCKER_SETUP.md)
2. Read: [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
3. Browse created Docker files

---

## 🏗️ Architecture

```
Frontend (React 3000)
    ↓
Nginx (80/443)
    ↓
├─ API (FastAPI 8000)
├─ Rasa (5005)
└─ Database (PostgreSQL 5432)
```

---

## 📊 Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Frontend | React 18 + TypeScript | 3000 |
| Backend API | FastAPI | 8000 |
| NLP/Chatbot | Rasa 3.6 | 5005 |
| Database | PostgreSQL 15 | 5432 |
| Reverse Proxy | Nginx | 80/443 |

---

## ✅ What's Ready

✅ **Full Docker Setup**  
✅ **Development Mode** (hot reload)  
✅ **Production Mode** (optimized)  
✅ **Reverse Proxy** (Nginx)  
✅ **SSL/HTTPS** (configured)  
✅ **Database** (PostgreSQL)  
✅ **Complete Docs** (550+ pages)  
✅ **Environment Templates**  
✅ **Health Checks**  
✅ **Security** (non-root, secrets)  

---

## 🚫 Before Production

**Must do:**
- [ ] Change `SECRET_KEY` in .env
- [ ] Change `DB_PASSWORD` to strong password
- [ ] Set `DEBUG=false`
- [ ] Update API URLs in frontend .env
- [ ] Test all services run
- [ ] Check logs for errors

**Should do:**
- [ ] Setup SSL certificate
- [ ] Configure domain DNS
- [ ] Setup firewall rules
- [ ] Configure backups
- [ ] Setup monitoring

---

## 📞 Getting Help

1. **Check docs first**: [DEVELOPMENT.md](DEVELOPMENT.md) or [DEPLOYMENT.md](DEPLOYMENT.md)
2. **View logs**: `docker-compose logs -f <service>`
3. **Check issues**: Look in guide troubleshooting section
4. **Manual setup**: See [DEVELOPMENT.md](DEVELOPMENT.md) for running services individually

---

## 🎓 Learning Resources

- **Docker**: https://docs.docker.com/get-started/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Rasa**: https://rasa.com/docs/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

## 🎉 You're Ready!

**Everything is set up.** Choose your next step above!

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: December 2024  

Still confused? → Start with [DEVELOPMENT.md](DEVELOPMENT.md) if you want to develop locally, or [DEPLOYMENT.md](DEPLOYMENT.md) if you want to deploy to VPS.
