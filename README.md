# 🍽️ RestoBot - Restaurant Virtual Assistant

**Xây dựng trợ lý ảo thông minh cho nhà hàng**  
Building an Intelligent Virtual Assistant for Restaurants

## 📋 Thông tin đề tài
- **Tên tiếng Việt**: Xây dựng trợ lý ảo thông minh cho nhà hàng
- **Tên tiếng Anh**: Building an Intelligent Virtual Assistant for Restaurants
- **Từ khóa**: application, artificial intelligence, chatbot, machine learning, management system, NLP, retail, web app, software design

## 🚀 Quick Start - Docker Deployment

### Yêu cầu
- Docker & Docker Compose
- Port 3000, 5005, 5055, 8000, 5432 sẵn có

### Chạy hệ thống

```bash
# 1. Clone repository
git clone https://github.com/your-repo/restobot.git
cd restobot

# 2. Build và khởi động tất cả services
docker-compose build --no-cache
docker-compose up -d

# 3. Kiểm tra trạng thái
docker-compose ps

# 4. Xem log
docker-compose logs -f
```

**Truy cập ứng dụng:**
- 🌐 Frontend: http://103.56.160.107:3000 (hoặc localhost:3000)
- 📚 API Docs: http://103.56.160.107:8000/docs (hoặc localhost:8000/docs)
- 🤖 Rasa API: http://103.56.160.107:5005 (hoặc localhost:5005)
- 🎯 Nginx Proxy: http://103.56.160.107 (hoặc localhost:80)

## 🏗️ Kiến trúc Microservices

```
RestoBot/
├── docker-compose.yml        # Orchestration tất cả services
├── nginx.conf                # Reverse proxy configuration
├── .dockerignore              # Docker build ignore rules
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
│
├── app/                       # 🔵 FastAPI Backend Service
│   ├── Dockerfile             
│   ├── requirements.txt        
│   ├── main.py                
│   ├── migrate.py             
│   ├── seed_data.py           
│   ├── api/v1/                
│   ├── models/                
│   ├── schemas/               
│   ├── crud/                  
│   └── core/                  
│
├── rasa_bot/                  # 🤖 Rasa NLP Service
│   ├── Dockerfile             
│   ├── requirements.txt        
│   ├── config.yml             
│   ├── domain.yml             
│   ├── endpoints.yml          
│   ├── data/                  
│   ├── models/                
│   ├── actions/               
│   └── README.md              
│
└── restobot-frontend/         # 🎨 React Frontend Service
    ├── Dockerfile             
    ├── package.json           
    ├── tsconfig.json          
    ├── public/                
    ├── src/                   
    └── build/                 
```

## 🔧 Services & Ports

| Service | Port | Type | Description |
|---------|------|------|-------------|
| **PostgreSQL** | 5432 | Database | Restaurant data |
| **FastAPI Backend** | 8000 | REST API | Business logic |
| **Rasa Actions** | 5055 | gRPC | Custom actions |
| **Rasa Server** | 5005 | HTTP/REST | Vietnamese NLP |
| **React Frontend** | 3000 | Web UI | Customer interface |
| **Nginx Proxy** | 80 | Reverse Proxy | Load balancing |

## 📚 Service Details

### 🔵 Backend API Service (app/)

**Auto-runs on startup:**
- Database migration via `app/migrate.py`
- Data seeding via `app/seed_data.py`
- FastAPI server on port 8000

**Default users:**
- Admin: admin@restobot.com / admin123
- Staff: staff@restobot.com / staff123
- Customer: customer@restobot.com / customer123

### 🤖 Rasa Bot Service (rasa_bot/)

**Components:**
- **Rasa Server** (port 5005): NLU + Dialog
- **Rasa Actions** (port 5055): Custom actions

**Features:**
- Vietnamese NLP
- Intent classification
- Entity extraction
- Multi-turn dialogs

### 🎨 React Frontend (restobot-frontend/)

**Features:**
- Chat interface
- Menu browsing
- Table booking
- Order management
- Admin dashboard
- Authentication

## 🔄 Docker Commands

```bash
# Build all
docker-compose build --no-cache

# Start all
docker-compose up -d

# Stop all
docker-compose down

# View logs
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f rasa
docker-compose logs -f frontend

# Rebuild service
docker-compose up -d --build api

# Run command in service
docker-compose exec api python migrate.py
docker-compose exec rasa rasa train
```

## 🗄️ Database

**PostgreSQL** (auto-created by docker-compose)

**Credentials:**
- User: postgres
- Password: password
- Database: restobot_db
- Port: 5432

**Auto-setup:**
1. Table creation from models
2. Data seeding with Vietnamese data
3. Sample users & menu items

## 🧪 Testing

### Test API
```bash
curl http://103.56.160.107:8000/health
curl http://103.56.160.107:8000/api/v1/menu/categories/
```

### Test Rasa
```bash
curl -X POST http://103.56.160.107:5005/model/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Xin chào"}'
```

### Test Frontend
```bash
http://103.56.160.107:3000
```

## 🔐 Default Credentials

- **Admin**: admin@restobot.com / admin123
- **Staff**: staff@restobot.com / staff123
- **Customer**: customer@restobot.com / customer123

⚠️ Change passwords in production!

## 🔧 Configuration

In `docker-compose.yml`:

```yaml
DB_USER: postgres
DB_PASSWORD: password
DB_NAME: restobot_db
SECRET_KEY: your-secret-key-change-in-production
API_PORT: 8000
RASA_PORT: 5005
FRONTEND_PORT: 3000
```

## 🚨 Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs <service-name>

# Check ports
lsof -i :<port>  # macOS/Linux
```

### Rasa loading slow
- Wait 2-3 minutes for TensorFlow model load
- Check: `docker-compose logs -f rasa`

### Database errors
```bash
# Check PostgreSQL
docker-compose ps postgres

# Verify connection
docker-compose exec postgres psql -U postgres -d restobot_db
```

### Frontend can't connect API
- Verify API: `curl http://103.56.160.107:8000/health`
- Check docker-compose.yml for URLs
- Check logs: `docker-compose logs frontend`

## 📊 Performance

- **Startup**: 30-60 seconds (Rasa model load)
- **Memory**: ~800MB-1GB
- **Concurrent Users**: 10-50 (depends on VPS)
- **Response Time**: 
  - API: ~50-100ms
  - Rasa: ~200-500ms (Vietnamese NLP)

## 🔄 Development

### Backend Changes
```bash
docker-compose up -d --build api
docker-compose exec api python migrate.py  # if changed models
```

### Chatbot Training
```bash
# Edit rasa_bot/data/
docker-compose exec rasa rasa train
docker-compose restart rasa
```

### Frontend Changes
```bash
# Edit restobot-frontend/src/
docker-compose restart frontend
```

## 📦 Deployment

### Requirements
- Docker & Docker Compose
- Ports 80, 3000, 5005, 5055, 8000, 5432 available
- 2GB+ RAM
- 10GB+ disk

### Production
```bash
export SECRET_KEY="strong-key"
export DB_PASSWORD="strong-password"

docker-compose build
docker-compose -f docker-compose.yml up -d
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U postgres restobot_db > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d restobot_db
```

## 🔗 Service Communication

**Internal URLs (Docker DNS):**
- API: http://api:8000
- Rasa: http://rasa:5005
- Rasa Actions: http://rasa-actions:5055
- Database: postgresql://postgres@postgres:5432/restobot_db

## 📚 Documentation

- **API**: http://103.56.160.107:8000/docs (Swagger UI)
- **ReDoc**: http://103.56.160.107:8000/redoc
- **Rasa**: `rasa_bot/README.md`
- **Frontend**: `restobot-frontend/README.md`

## 👥 Project Info

**Academic Project**: Intelligent Virtual Assistant for Restaurants  
**Tech Stack**: FastAPI + Rasa + React + PostgreSQL  
**Deployment**: Docker Microservices  

---

**Version**: 2.0.0 (Microservices with Docker)  
**Last Updated**: December 28, 2025