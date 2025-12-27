# 🎯 Quick Reference - RestoBot Docker Setup

Tài liệu nhanh cho toàn bộ setup Docker của RestoBot

## 📦 Docker Files Created

| File | Mô tả |
|------|-------|
| **Dockerfile** | FastAPI backend container |
| **Dockerfile.rasa** | Rasa chatbot container |
| **restobot-frontend/Dockerfile** | React production build |
| **restobot-frontend/Dockerfile.dev** | React development (hot reload) |
| **docker-compose.yml** | Production orchestration |
| **docker-compose.dev.yml** | Development orchestration (hot reload) |
| **nginx.conf** | Reverse proxy & load balancer |

## 🚀 Quick Commands

### Development (Local)
```bash
# One-liner: Full stack with hot reload
docker-compose -f docker-compose.dev.yml up --build

# Access:
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
# Rasa: http://localhost:5005
```

### Production (VPS)
```bash
# One-liner: Full production stack
docker-compose build && docker-compose up -d

# Access via domain or IP
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f api
```

---

## 📋 Services & Ports

### Development
| Service | Port | URL |
|---------|------|-----|
| Frontend (React) | 3000 | http://localhost:3000 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Rasa | 5005 | http://localhost:5005 |
| PostgreSQL | 5432 | localhost:5432 |
| Nginx | 80 | http://localhost (optional) |

### Production (Via Nginx)
| Service | URL |
|---------|-----|
| Frontend | http://your-domain.com |
| API | http://your-domain.com/api/v1 |
| API Docs | http://your-domain.com/docs |
| Rasa | http://your-domain.com/rasa |

---

## 🔧 Configuration Files

### .env (Root)
```bash
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=restobot_db
API_PORT=8000
SECRET_KEY=your_secret_key_32_chars_min
RASA_PORT=5005
FRONTEND_PORT=3000
```

### restobot-frontend/.env
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_CHAT_API_URL=http://localhost:5005
REACT_APP_NAME=RestoBot
REACT_APP_VERSION=1.0.0
```

---

## 📁 Project Structure

```
restobot/
├── Dockerfile                    # FastAPI
├── Dockerfile.rasa              # Rasa
├── docker-compose.yml           # Prod
├── docker-compose.dev.yml       # Dev
├── nginx.conf                   # Proxy
├── .env.example                 # Template
├── requirements.txt             # Python deps
├── app/                         # FastAPI backend
├── rasa_bot/                    # Rasa chatbot
└── restobot-frontend/           # React frontend
    ├── Dockerfile              # Prod build
    ├── Dockerfile.dev          # Dev hot-reload
    ├── src/
    ├── public/
    └── package.json
```

---

## 🎯 Common Workflows

### First Time Setup
```bash
cd restobot
cp .env.example .env
cp restobot-frontend/.env.example restobot-frontend/.env
docker-compose -f docker-compose.dev.yml up --build
```

### Making Changes to Frontend
```bash
# Hot reload enabled - just edit and save
# http://localhost:3000 refreshes automatically
```

### Making Changes to Backend
```bash
# With --reload flag enabled
# Restart container if needed:
docker-compose -f docker-compose.dev.yml restart api
```

### Making Changes to Rasa
```bash
# Rebuild model:
docker-compose -f docker-compose.dev.yml exec rasa rasa train
docker-compose -f docker-compose.dev.yml restart rasa
```

### Deploying to VPS
```bash
# On VPS:
git clone <repo> restobot
cd restobot
cp .env.example .env
nano .env  # Edit with production values
docker-compose build
docker-compose up -d
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | `lsof -i :3000` (find process) then kill it |
| API not connecting | Check REACT_APP_API_URL in .env |
| DB connection error | Verify DB_PASSWORD and DATABASE_URL |
| Rasa model error | `docker-compose exec rasa rasa train` |
| Containers won't start | `docker-compose logs` (check error messages) |

---

## 📊 Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | React + TypeScript | 18 |
| Backend | FastAPI | 0.115.2 |
| Database | PostgreSQL | 15 |
| Chatbot | Rasa | 3.6.20 |
| Reverse Proxy | Nginx | Alpine |
| Python | Python | 3.9 |
| Node | Node.js | 18 |

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in .env (32+ chars)
- [ ] Change `DB_PASSWORD` in .env (strong password)
- [ ] Set `DEBUG=false` in production
- [ ] Configure CORS properly in app/main.py
- [ ] Use SSL/HTTPS in production
- [ ] Set environment-specific URLs in .env files
- [ ] Don't commit .env to git (use .env.example)

---

## 📚 Additional Guides

- **Detailed Deployment**: See `DEPLOYMENT.md`
- **Development Setup**: See `DEVELOPMENT.md`
- **Frontend Docs**: See `restobot-frontend/README.md`
- **API Documentation**: http://localhost:8000/docs (auto-generated)

---

## 🚀 Next Steps

1. **Read DEVELOPMENT.md** - For local development
2. **Read DEPLOYMENT.md** - For VPS deployment
3. **Read restobot-frontend/README.md** - Frontend documentation
4. **Check API docs** - http://localhost:8000/docs

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Status**: ✅ Production Ready
