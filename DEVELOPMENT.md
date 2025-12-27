# 💻 RestoBot Development Guide

Hướng dẫn chạy project RestoBot trên máy local để phát triển.

## 📋 Yêu cầu

- **Node.js** 18+ (cho React frontend)
- **Python** 3.9+ (đã cài đặt)
- **Docker & Docker Compose** (cho database + Rasa)
- **Git**

## 🚀 Quick Start (Using Docker)

### Option 1: Development với Docker (Recommended)

```bash
# 1. Clone hoặc navigate đến folder
cd restobot

# 2. Tạo .env
cp .env.example .env

# 3. Chạy stack với hot reload
docker-compose -f docker-compose.dev.yml up --build

# 4. Truy cập
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Rasa: http://localhost:5005
```

### Stop development stack
```bash
docker-compose -f docker-compose.dev.yml down
```

---

## 💡 Option 2: Chạy từng service riêng

### 2.1 Database (PostgreSQL trong Docker)

```bash
# Chỉ chạy database
docker-compose -f docker-compose.dev.yml up postgres -d

# Hoặc dùng SQLite (không cần Docker)
# Hệ thống sẽ tự động dùng SQLite nếu không có DATABASE_URL
```

### 2.2 Backend (FastAPI)

```bash
# 1. Cài dependencies
pip install -r requirements.txt

# 2. Setup database
python migrate.py

# 3. Chạy Uvicorn (development mode)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API sẽ chạy tại: http://localhost:8000
# Docs tại: http://localhost:8000/docs
```

### 2.3 Rasa Bot

```bash
# 1. Navigate đến Rasa directory
cd rasa_bot

# 2. Train model (lần đầu hoặc khi có data mới)
rasa train

# 3. Chạy Rasa server
rasa run --port 5005 --enable-api --cors "*"

# Hoặc chạy với actions server trong terminal khác:
# rasa run actions --port 5055
```

### 2.4 Frontend (React)

```bash
# 1. Navigate đến frontend
cd restobot-frontend

# 2. Cài dependencies
npm install

# 3. Tạo .env (nếu chưa có)
cp .env.example .env

# 4. Start development server
npm start

# Frontend sẽ mở tự động tại: http://localhost:3000
```

---

## 📁 Project Structure

```
restobot/
├── app/                         # FastAPI Backend
│   ├── api/v1/                 # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── menu.py
│   │   ├── tables.py
│   │   └── orders.py
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── crud/                   # Database operations
│   └── core/                   # Config, DB, Security
├── rasa_bot/                   # Rasa Chatbot
│   ├── data/                   # Training data (NLU, rules, stories)
│   ├── actions/                # Custom actions
│   ├── config.yml
│   └── domain.yml
├── restobot-frontend/          # React Frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── context/            # React Context
│   │   └── utils/              # Utilities
│   ├── public/
│   └── package.json
├── requirements.txt            # Python dependencies
└── migrate.py                  # Database migration
```

---

## 🔄 Development Workflow

### Thêm Backend Feature

```bash
# 1. Tạo model (app/models/)
# 2. Tạo schema (app/schemas/)
# 3. Tạo CRUD (app/crud/)
# 4. Tạo API route (app/api/v1/)
# 5. Test endpoint: http://localhost:8000/docs
```

### Thêm Frontend Feature

```bash
# 1. Tạo component (src/components/)
# 2. Thêm page (src/pages/) nếu cần
# 3. Tạo service call (src/services/)
# 4. Update state/context (src/context/)
# 5. Hot reload sẽ tự động update
```

### Cập nhật Chatbot

```bash
# 1. Thêm intents/entities (rasa_bot/data/nlu.yml)
# 2. Thêm stories (rasa_bot/data/stories.yml)
# 3. Cập nhật domain (rasa_bot/domain.yml)
# 4. Tạo custom actions (rasa_bot/actions/)
# 5. Train: cd rasa_bot && rasa train
# 6. Restart Rasa server
```

---

## 🧪 Testing

### Test API
```bash
# 1. Truy cập Swagger UI
# http://localhost:8000/docs

# 2. Hoặc dùng curl
curl http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Test Chatbot
```bash
# Test Vietnamese message
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "Xin chào"}'
```

### Test Frontend
```bash
# npm start sẽ tự động mở browser
# http://localhost:3000
```

---

## 🔗 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/auth/login` | Đăng nhập |
| POST | `/api/v1/auth/register` | Đăng ký |
| GET | `/api/v1/users/me` | Lấy thông tin user |
| GET | `/api/v1/menu/categories` | Danh sách thể loại |
| GET | `/api/v1/menu/items` | Danh sách menu |
| GET | `/api/v1/tables/` | Danh sách bàn |
| POST | `/api/v1/orders/` | Tạo đơn hàng |
| GET | `/api/v1/orders/` | Danh sách đơn hàng |

Xem đầy đủ tại: http://localhost:8000/docs

---

## 🐛 Debugging

### Backend Logs
```bash
# FastAPI logs (terminal chạy uvicorn)
# Hoặc xem file log nếu có setup logging
```

### Frontend Logs
```bash
# Browser console (F12)
# Terminal chạy npm start
```

### Rasa Logs
```bash
# Terminal chạy Rasa
# Hoặc file log tại rasa_bot/logs/
```

### Database
```bash
# Connect PostgreSQL
psql -U postgres -d restobot_db

# Hoặc SQLite
sqlite3 test.db
```

---

## 📦 Useful Commands

### Docker
```bash
# View logs
docker-compose -f docker-compose.dev.yml logs -f <service>

# Execute command in container
docker-compose -f docker-compose.dev.yml exec api bash
docker-compose -f docker-compose.dev.yml exec frontend sh

# Rebuild images
docker-compose -f docker-compose.dev.yml build --no-cache

# Stop all
docker-compose -f docker-compose.dev.yml down

# Clean everything (careful!)
docker-compose -f docker-compose.dev.yml down -v
```

### Python
```bash
# Install packages
pip install package_name

# Update requirements
pip freeze > requirements.txt

# Run migrations
python migrate.py

# Run seed data
python seed_data.py
```

### React
```bash
# Install dependencies
npm install

# Install a package
npm install package_name

# Build for production
npm run build

# Run tests
npm test
```

---

## 🆘 Common Issues

### Port already in use
```bash
# Kill process on port
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill -9
```

### Module not found (Frontend)
```bash
cd restobot-frontend
rm -rf node_modules package-lock.json
npm install
```

### Database connection error
```bash
# Check DATABASE_URL in .env
# Or make sure PostgreSQL is running:
docker-compose -f docker-compose.dev.yml ps postgres
```

### Rasa model training failed
```bash
cd rasa_bot
rm -rf models/
rasa train
```

---

## 📚 Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Rasa Docs**: https://rasa.com/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Happy Coding!** 🚀
