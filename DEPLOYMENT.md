# 🚀 Docker Deployment Guide - RestoBot

## 📋 Yêu cầu trước triển khai

Trên VPS của bạn cần cài đặt:
- **Docker** (>= 20.10)
- **Docker Compose** (>= 1.29)
- **Git** (để clone repository)

### Cài đặt trên Ubuntu/Debian:

```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Xác minh cài đặt
docker --version
docker-compose --version
```

---

## 🏗️ Project Structure Overview

```
restobot/
├── app/                          # FastAPI Backend
├── rasa_bot/                     # Rasa NLP Chatbot
├── restobot-frontend/            # React Frontend
│   ├── src/
│   ├── public/
│   ├── Dockerfile               # Production build
│   ├── Dockerfile.dev           # Development with hot reload
│   └── package.json
├── Dockerfile                    # FastAPI Dockerfile
├── Dockerfile.rasa              # Rasa Dockerfile
├── docker-compose.yml           # Production orchestration
├── docker-compose.dev.yml       # Development orchestration
├── nginx.conf                   # Reverse proxy config
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment template
```

---

## � Bước 0: Chạy trên Local (Development)

Để phát triển và test trước khi deploy lên VPS:

### 0.1 Setup môi trường
```bash
# Clone hoặc navigate đến folder
cd restobot

# Tạo .env
cp .env.example .env

# (Optional) Chỉnh sửa .env nếu cần
nano .env
```

### 0.2 Chạy với Docker Compose (Development)
```bash
# Chạy toàn bộ stack với hot reload
docker-compose -f docker-compose.dev.yml up --build

# Hoặc chạy trong background
docker-compose -f docker-compose.dev.yml up -d --build
```

### 0.3 Truy cập ứng dụng
- **Frontend**: http://localhost:3000 (React - hot reload enabled)
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Rasa**: http://localhost:5005
- **PostgreSQL**: localhost:5432

### 0.4 Xem logs
```bash
# Tất cả services
docker-compose -f docker-compose.dev.yml logs -f

# Một service cụ thể
docker-compose -f docker-compose.dev.yml logs -f frontend
docker-compose -f docker-compose.dev.yml logs -f api
```

---

### 1.1 Clone và chuẩn bị code
```bash
# Clone repository của bạn
git clone <your-repo-url> restobot
cd restobot

# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa .env với thông tin của bạn
nano .env
```

### 1.2 Kiểm tra cấu trúc folder
```
restobot/
├── Dockerfile                    # FastAPI backend
├── Dockerfile.rasa             # Rasa bot
├── docker-compose.yml          # Orchestration
├── .dockerignore               # Docker build optimization
├── .env.example                # Environment template
├── nginx.conf                  # Reverse proxy config
├── requirements.txt            # Python dependencies
├── app.py
├── app/
├── rasa_bot/
└── restobot-frontend/
```

### 1.3 Cập nhật requirements.txt
```bash
# Xóa scipy version cũ nếu có
pip install scipy==1.8.1 --upgrade
pip freeze > requirements.txt
```

---

## 📤 Bước 2: Push lên VPS

### 2.1 Thêm Docker files vào Git
```bash
git add Dockerfile Dockerfile.rasa docker-compose.yml nginx.conf .dockerignore .env.example

git commit -m "Add Docker configuration for production deployment"

git push origin main
```

### 2.2 SSH vào VPS của bạn
```bash
ssh user@your-vps-ip

# Hoặc nếu dùng SSH key
ssh -i /path/to/key.pem user@your-vps-ip
```

---

## 🐳 Bước 3: Triển khai trên VPS

### 3.1 Clone repository trên VPS
```bash
# Đăng nhập vào VPS
cd /var/www/
git clone <your-repo-url> restobot
cd restobot
```

### 3.2 Tạo file .env trên VPS
```bash
# Tạo từ template
cp .env.example .env

# Chỉnh sửa với các giá trị production
nano .env
```

**Ví dụ nội dung .env cho production:**
```bash
# Database Configuration
DB_USER=postgres
DB_PASSWORD=VerySecurePassword123!@#
DB_NAME=restobot_db
DB_PORT=5432

# API Configuration
API_PORT=8000
SECRET_KEY=your_very_long_and_secure_secret_key_at_least_32_chars_here!@#$%
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false

# Rasa Configuration
RASA_PORT=5005

# Frontend Configuration
FRONTEND_PORT=3000

# Application Settings
PROJECT_NAME=RestoBot
PROJECT_VERSION=1.0.0
HOST=0.0.0.0
```

### 3.3 Cấu hình Frontend
```bash
# Tạo .env cho frontend
cp restobot-frontend/.env.example restobot-frontend/.env

# Chỉnh sửa URLs (nếu có domain)
nano restobot-frontend/.env
```

**Ví dụ nội dung .env cho frontend production:**
```bash
# React App Environment Variables
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_CHAT_API_URL=https://your-domain.com/rasa
REACT_APP_NAME=RestoBot
REACT_APP_VERSION=1.0.0
REACT_APP_ENABLE_ANALYTICS=true
```

### 3.4 Tạo SSL certificate (nếu có domain)
```bash
# Sử dụng Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx -y

# Tạo certificate (thay your-domain.com bằng domain của bạn)
sudo certbot certonly --standalone -d your-domain.com

# Certificates sẽ lưu tại:
# /etc/letsencrypt/live/your-domain.com/
```

### 3.5 Build và chạy Docker containers
```bash
# Cấp quyền cho Docker (nếu cần)
sudo usermod -aG docker $USER
newgrp docker

# Build images
docker-compose build

# Chạy containers (background)
docker-compose up -d

# Xem logs
docker-compose logs -f

# Kiểm tra status
docker-compose ps
```

---

## ✅ Bước 4: Kiểm tra triển khai

```bash
# 1. Kiểm tra containers
docker-compose ps

# 2. Kiểm tra logs
docker-compose logs

# 3. Kiểm tra logs service cụ thể
docker-compose logs frontend   # React app logs
docker-compose logs api        # FastAPI logs
docker-compose logs rasa       # Rasa logs
docker-compose logs postgres   # Database logs
docker-compose logs nginx      # Proxy logs

# 4. Test API health
curl http://localhost:8000/health

# 5. Truy cập ứng dụng
# Frontend: http://your-vps-ip
# API Docs: http://your-vps-ip/docs
# Rasa: http://your-vps-ip/rasa
```

### Service URLs sau triển khai:
| Service | URL | Mô tả |
|---------|-----|-------|
| **Frontend** | http://your-vps-ip | React web app |
| **API** | http://your-vps-ip/api/v1 | RESTful API |
| **API Docs** | http://your-vps-ip/docs | Swagger UI |
| **Rasa** | http://your-vps-ip/rasa | Chatbot API |
| **Health** | http://your-vps-ip/health | Health check |

---

## 🌐 Bước 5: Cấu hình domain (nếu có)

### 5.1 Cập nhật nginx.conf
```bash
# Sửa server_name trong nginx.conf
nano nginx.conf

# Thay _;  thành your-domain.com
```

### 5.2 Nếu dùng SSL
```bash
# Cập nhật nginx.conf với SSL
# Thêm vào trong server block:

listen 443 ssl;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### 5.3 Restart Nginx
```bash
docker-compose restart nginx
```

---

## 📊 Các lệnh hữu ích

```bash
# Xem logs real-time
docker-compose logs -f api

# Kiểm tra một container cụ thể
docker-compose logs postgres

# Restart một service
docker-compose restart api

# Stop tất cả
docker-compose down

# Stop và xóa volumes (cẩn thận - sẽ mất data!)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Chỉ chạy một service
docker-compose up -d api

# Execute command trong container
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d restobot_db
```

---

## 🔒 Bảo mật

### Checklist bảo mật:
- [ ] Đổi `SECRET_KEY` trong .env (tối thiểu 32 ký tự, random)
- [ ] Đổi `DB_PASSWORD` thành mật khẩu mạnh
- [ ] Cấu hình tường lửa VPS (chỉ cho phép ports 22, 80, 443)
- [ ] Cập nhật `allow_origins` trong app/main.py (không phải `["*"]`)
- [ ] Bật SSL/HTTPS
- [ ] Thường xuyên cập nhật Docker images: `docker-compose pull`

### Cấu hình tường lửa:
```bash
# Ubuntu/Debian với ufw
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 🚨 Troubleshooting

### Containers không start
```bash
# Kiểm tra logs chi tiết
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Database connection error
```bash
# Kiểm tra PostgreSQL
docker-compose exec postgres psql -U postgres -d restobot_db

# Reset database (cẩn thận!)
docker-compose down -v
docker-compose up -d
```

### Port bị chiếm
```bash
# Kiểm tra port nào đang dùng port 8000
lsof -i :8000

# Hoặc thay đổi ports trong docker-compose.yml
```

---

## 📈 Mở rộng trong tương lai

### Cải tiến có thể áp dụng:
1. **Load Balancing**: Thêm nhiều API instances phía sau Nginx
2. **CI/CD**: Tự động deploy khi push code (GitHub Actions, GitLab CI)
3. **Monitoring**: Thêm Prometheus + Grafana
4. **Logging**: Thêm ELK Stack (Elasticsearch, Logstash, Kibana)
5. **Backup**: Cấu hình automated database backups
6. **CDN**: Sử dụng CloudFlare hoặc AWS CloudFront cho frontend

---

**Chúc bạn triển khai thành công!** 🎉
