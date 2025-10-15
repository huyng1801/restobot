# 🍽️ RestoBot - Restaurant Virtual Assistant

**Trợ lý ảo thông minh cho nhà hàng Việt Nam**  
FastAPI Backend + Rasa Chatbot + Vietnamese NLP

## 🚀 Quick Start - Chỉ Một Lệnh

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Khởi động toàn bộ hệ thống (ALL-IN-ONE)
python restobot.py
```

**Hệ thống tự động khởi động:**
- ✅ FastAPI Backend: http://localhost:8000
- ✅ API Documentation: http://localhost:8000/docs  
- ✅ Rasa Chatbot: http://localhost:5005
- ✅ Chat Interface: Tự động mở browser

## 📊 Project Status

### ✅ Completed Features
- **Backend System**: FastAPI với SQLAlchemy models
- **Vietnamese AI**: Rasa chatbot hỗ trợ tiếng Việt
- **Authentication**: JWT token-based security
- **Restaurant Management**: Menu, tables, orders, reservations
- **All-in-One Deployment**: Single command startup
- **Error Handling**: SQLAlchemy warnings fixed

### 🔄 Development Mode Options

#### 1. Production Mode (Embedded Data)
```bash
python restobot.py          # Ready-to-use với dữ liệu mẫu
```

#### 2. Database Development Mode  
```bash
# Setup PostgreSQL database
python migrate.py --fresh   # Tạo database + seed data
python restobot.py          # Kết nối database thật
```

## �️ Architecture

```
RestoBot/
├── restobot.py         # 🌟 ALL-IN-ONE LAUNCHER
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