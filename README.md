# 🍽️ RestoBot - Restaurant Virtual Assistant

**Xây dựng trợ lý ảo thông minh cho nhà hàng**  
Building an Intelligent Virtual Assistant for Restaurants

## 📋 Thông tin đề tài
- **Tên tiếng Việt**: Xây dựng trợ lý ảo thông minh cho nhà hàng
- **Tên tiếng Anh**: Building an Intelligent Virtual Assistant for Restaurants
- **Từ khóa**: application, artificial intelligence, chatbot, machine learning, management system, NLP, retail, web app, software design

## 🚀 Quick Start - Cài đặt và chạy hệ thống

### 1. Cài đặt môi trường
```bash
# Clone repository
git clone https://github.com/your-repo/restobot.git
cd restobot

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu hình Database PostgreSQL (Tùy chọn)

#### A. Sử dụng SQLite (Mặc định - Đơn giản)
```bash
# Không cần cấu hình gì, hệ thống sẽ tự động sử dụng SQLite
python restobot.py
```

#### B. Sử dụng PostgreSQL (Production)
```bash
# 1. Cài đặt PostgreSQL
# 2. Tạo database
createdb restobot_db

# 3. Tạo file .env với thông tin database
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/restobot_db" > .env

# 4. Chạy migration và seed data
python migrate.py

# 5. Khởi động hệ thống
python restobot.py
```

### 3. Khởi động hệ thống

```bash
# Khởi động toàn bộ hệ thống (ALL-IN-ONE)
python restobot.py
```

**Hệ thống sẽ tự động khởi động:**
- ✅ FastAPI Backend: http://localhost:8000
- ✅ API Documentation: http://localhost:8000/docs  
- ✅ Rasa Chatbot: http://localhost:5005
- ✅ Chat Interface: Tự động mở browser

## 🏗️ Kiến trúc hệ thống

```
RestoBot/
├── 🌟 restobot.py              # All-in-One Launcher
├── 🌟 migrate.py               # Database Migration & Seed Data
├── � app/                     # FastAPI Backend
│   ├── api/v1/                 # API Routes
│   │   ├── auth.py            # Authentication
│   │   ├── menu.py            # Menu Management
│   │   ├── tables.py          # Table Management
│   │   ├── orders.py          # Order Management
│   │   └── users.py           # User Management
│   ├── models/                 # SQLAlchemy Models
│   ├── schemas/                # Pydantic Schemas
│   ├── crud/                   # Database Operations
│   └── core/                   # Config, Database, Security
├── 📁 rasa_bot/                # Rasa Chatbot
│   ├── data/                   # Training Data (Vietnamese)
│   ├── actions/                # Custom Actions
│   ├── models/                 # Trained Models
│   └── config.yml              # Rasa Configuration
└── 📁 requirements/            # Dependencies
```

## 🔧 Chức năng hệ thống

### Backend API Features
- **👥 Quản lý người dùng**: Đăng ký, đăng nhập, phân quyền (Admin/Staff/Customer)
- **🍽️ Quản lý thực đơn**: CRUD món ăn, danh mục, giá cả
- **🪑 Quản lý bàn ăn**: Đặt bàn, kiểm tra trạng thái, quản lý reservation
- **📦 Quản lý đơn hàng**: Tạo, cập nhật, theo dõi đơn hàng
- **🔐 Bảo mật**: JWT authentication với phân quyền đa cấp

### Vietnamese Chatbot Features
- **🗣️ Xử lý tiếng Việt**: Hiểu và phản hồi bằng tiếng Việt tự nhiên
- **🍽️ Tư vấn thực đơn**: Xem menu, hỏi giá, chi tiết món ăn
- **🪑 Đặt bàn thông minh**: Hỗ trợ đặt bàn qua hội thoại
- **📱 Gọi món**: Thêm món vào đơn hàng qua chat
- **ℹ️ Thông tin nhà hàng**: Giờ mở cửa, địa chỉ, liên hệ, khuyến mãi
- **🎯 Gợi ý món**: Món phổ biến, món đặc biệt

## 🛠️ Technology Stack

- **Backend**: Python 3.9+ với FastAPI (RESTful API hiệu suất cao)
- **Database**: PostgreSQL 14+ với SQLAlchemy ORM (hoặc SQLite cho development)
- **NLP & AI**: Rasa Framework (NLU + Core) cho Conversational AI
- **ML Libraries**: NLTK/SpaCy, Transformer models
- **Authentication**: JWT với phân quyền role-based
- **Deployment**: Docker & Docker Compose ready

## 📚 Hướng dẫn sử dụng

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Đăng nhập |
| `/api/users/` | GET/POST | Quản lý người dùng |
| `/api/menu/categories/` | GET | Danh sách danh mục |
| `/api/menu/items/` | GET | Danh sách món ăn |
| `/api/tables/` | GET | Quản lý bàn ăn |
| `/api/orders/` | GET/POST | Quản lý đơn hàng |

### Chatbot Commands (Tiếng Việt)
- **Chào hỏi**: "Xin chào", "Chào bạn"
- **Xem menu**: "Cho tôi xem thực đơn", "Có món gì"
- **Đặt bàn**: "Tôi muốn đặt bàn cho 4 người", "Đặt bàn tối nay 7 giờ"
- **Gọi món**: "Tôi muốn gọi phở bò", "Cho tôi 2 phần bò bít tết"
- **Hỏi thông tin**: "Nhà hàng mở cửa mấy giờ", "Địa chỉ ở đâu"

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Test menu API
curl http://localhost:8000/api/menu/categories/
```

### Test Vietnamese Chatbot
```bash
# Test qua API
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "Xin chào"}'
```

## 🔄 Development Workflow

### Thêm chức năng Backend
1. Tạo/sửa models trong `app/models/`
2. Tạo/sửa schemas trong `app/schemas/`
3. Tạo/sửa CRUD operations trong `app/crud/`
4. Tạo/sửa API routes trong `app/api/v1/`

### Cập nhật Chatbot
1. Thêm intents/entities vào `rasa_bot/data/nlu.yml`
2. Tạo stories trong `rasa_bot/data/stories.yml`
3. Thêm responses vào `rasa_bot/domain.yml`
4. Tạo custom actions trong `rasa_bot/actions/`
5. Train lại model: `cd rasa_bot && rasa train`

### Database Migration
```bash
# Tạo migration mới
python migrate.py --fresh

# Seed dữ liệu mẫu
python migrate.py
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build và chạy với Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Production setup
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-secret-key"

# Chạy migration
python migrate.py

# Khởi động
python restobot.py
```

## ⚡ Performance & Monitoring

- **Startup Time**: 30-60 seconds (Rasa model loading)
- **Memory Usage**: ~500MB (TensorFlow models)
- **Response Time**: ~200-500ms (Vietnamese NLP)
- **Concurrent Users**: Tested up to 10 simultaneous users

## 🛡️ Troubleshooting

### Common Issues
1. **Rasa không khởi động**: Chờ 2-3 phút để load model
2. **Database error**: Kiểm tra DATABASE_URL trong .env
3. **Port conflicts**: Đổi port trong config hoặc kill existing processes

### Logs & Monitoring
- **FastAPI logs**: Terminal output khi chạy restobot.py
- **Rasa logs**: `rasa_bot/` directory
- **Database logs**: SQLAlchemy output

## 📞 Support & Documentation

- **API Documentation**: http://localhost:8000/docs (tự động generate)
- **Rasa Training Guide**: Xem `rasa_bot/README.md`
- **Database Schema**: Xem `app/models/` directory

## 👥 Contributors

**Academic Project**: Xây dựng trợ lý ảo thông minh cho nhà hàng  
**University**: [Tên trường đại học]  
**Course**: [Tên môn học/khóa luận]  
**Tech Stack**: FastAPI + Rasa + Vietnamese NLP + PostgreSQL

---

© 2024 RestoBot Team - Academic Project License
├── app/                # FastAPI backend structure
│   ├── models/         # SQLAlchemy database models  
│   ├── api/            # API routes & endpoints
│   ├── core/           # Database, config, security
│   └── schemas/        # Pydantic data models
├── rasa_bot/           # Vietnamese conversational AI
│   ├── data/           # Vietnamese NLU training data
│   ├── actions/        # Custom chatbot actions
│   └── models/         # Trained AI models
├── migrate.py          # Database migration script
├── seed_data.py        # Sample Vietnamese restaurant data
└── requirements.txt    # Production dependencies
```

## 🔧 Features

### Backend API
- **Restaurant Management**: Complete CRUD operations
- **Menu System**: Vietnamese dishes with categories
- **Table Booking**: Real-time availability tracking
- **Order Management**: Kitchen orders với Vietnamese workflow
- **User Authentication**: Role-based access (Admin/Staff/Customer)

### Vietnamese Chatbot
- **Natural Language**: Vietnamese conversation understanding
- **Restaurant Queries**: Menu, prices, availability
- **Table Booking**: Conversational reservation system
- **Multi-turn Dialogues**: Context-aware responses

### System Integration
- **Automatic Startup**: Coordinated service launching
- **Health Monitoring**: Service status checking
- **Error Recovery**: Graceful failure handling
- **Performance**: Optimized for Vietnamese NLP

## � Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **FastAPI Backend** | http://localhost:8000 | Restaurant API |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Rasa Chatbot** | http://localhost:5005 | Vietnamese NLP API |
| **Chat Interface** | `chat_interface.html` | Web chat UI |

## ⚙️ Configuration

### Environment Variables
```bash
# Tự động set trong restobot.py
SQLALCHEMY_WARN_20=0             # SQLAlchemy warnings off
SQLALCHEMY_SILENCE_UBER_WARNING=1 # Uber warning off  
PYDANTIC_V1=1                    # Rasa compatibility
DATABASE_URL=sqlite:///./test.db # Default database
```

### Custom Configuration
Tạo file `.env` cho tùy chỉnh:
```bash
DATABASE_URL=postgresql://user:pass@localhost/restobot
SECRET_KEY=your-secret-key
RASA_MODEL_PATH=./rasa_bot/models
```

## 🧪 Testing

```bash
# Kiểm tra hệ thống nhanh
python -c "import requests; print('✅' if requests.get('http://localhost:8000/health').status_code == 200 else '❌')"

# Test Vietnamese chatbot
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "Xin chào"}'
```

## 📚 Documentation

- **API Reference**: http://localhost:8000/docs (auto-generated)
- **Database Setup**: `DATABASE_SETUP.md` (for PostgreSQL)
- **Rasa Configuration**: `rasa_bot/README.md`

## 🔄 Development Workflow

### Add New Features
1. **Backend**: Modify files in `app/` directory
2. **AI Training**: Update `rasa_bot/data/` với Vietnamese data
3. **Testing**: Run `python restobot.py` to test integration

### Database Development
1. **Models**: Update SQLAlchemy models in `app/models/`
2. **Migration**: Run `python migrate.py --fresh`
3. **Seed Data**: Update `seed_data.py` với Vietnamese data

### Production Deployment
- **Single File**: `restobot.py` chứa toàn bộ logic
- **Dependencies**: `requirements.txt` đã optimized
- **Environment**: Set environment variables for production

## ⚡ Performance Notes

- **Startup Time**: 30-60 seconds (Rasa model loading)
- **Memory Usage**: ~500MB (TensorFlow models)
- **Response Time**: ~200-500ms (Vietnamese NLP)
- **Concurrent Users**: Tested up to 10 simultaneous users

## 🛡️ Known Issues & Solutions

### Fixed Issues ✅
- **SQLAlchemy Warnings**: Suppressed in code
- **Pydantic Conflicts**: Compatibility mode enabled
- **Rasa Startup**: Automatic model loading with retry logic

### Monitoring
- **Service Health**: Auto-checks during startup
- **Error Logging**: Detailed logs in terminal
- **Recovery**: Automatic restart on failure

## 📞 Support

**FastAPI**: Always ready immediately  
**Rasa**: Requires 2-3 minutes for TensorFlow model loading  
**Status Check**: Monitor terminal output for detailed status

---

**Academic Project**: Vietnamese Restaurant Virtual Assistant  
**Tech Stack**: FastAPI + Rasa + Vietnamese NLP + SQLAlchemy  
**Deployment**: Production-ready single-command setup