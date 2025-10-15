# 🍽️ RestoBot - Database Setup Guide

## Hướng dẫn thiết lập Database với PostgreSQL

### 📋 Prerequisites

1. **PostgreSQL 14+** đã được cài đặt
2. **Python 3.9+** 
3. **Dependencies** đã cài đặt: `pip install -r requirements.txt`

### 🚀 Setup Database

#### 1. Tạo Database PostgreSQL

```sql
-- Kết nối PostgreSQL và tạo database
CREATE DATABASE restobot_db;
CREATE USER restobot_user WITH PASSWORD 'restobot_password';
GRANT ALL PRIVILEGES ON DATABASE restobot_db TO restobot_user;
```

#### 2. Cấu hình Environment Variables

Tạo file `.env` với nội dung:

```bash
# Database Configuration
DATABASE_URL=postgresql://restobot_user:restobot_password@localhost/restobot_db

# Application Settings
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=True

# SQLAlchemy Settings
SQLALCHEMY_WARN_20=0
SQLALCHEMY_SILENCE_UBER_WARNING=1
PYDANTIC_V1=1
```

#### 3. Chạy Migration & Seed Data

```bash
# Migration đầy đủ với seed data
python migrate.py

# Hoặc fresh install (xóa dữ liệu cũ)
python migrate.py --fresh

# Chỉ kiểm tra kết nối
python migrate.py --check

# Xem thông tin database
python migrate.py --info
```

### 📊 Seed Data

Script `seed_data.py` sẽ tạo dữ liệu mẫu cho:

#### 👥 Users (5 users)
- **admin** / admin123 (Admin)
- **manager001** / manager123 (Manager) 
- **staff001** / staff123 (Staff)
- **staff002** / staff123 (Staff)
- **customer001** / customer123 (Customer)

#### 🍽️ Menu Categories (5 categories)
- Món chính
- Món khai vị
- Đồ uống
- Tráng miệng
- Món chay

#### 🥘 Menu Items (15 items)
- Phở Bò Tái, Phở Gà, Bún Bò Huế
- Cơm Tấm Sườn Nướng, Bánh Mì Pate
- Gỏi Cuốn, Chả Giò, Nem Nướng
- Cà Phê Sữa Đá, Trà Đá, Sinh Tố Xoài
- Chè Ba Màu, Bánh Flan
- Phở Chay

#### 🪑 Tables (15 tables)
- Tầng 1: T01-T06 (2-6 người)
- Tầng 2: T07-T10 (2-10 người) 
- VIP: VIP01-VIP03 (4-12 người)
- Bar: BAR01-BAR02 (1 người)

#### 📝 Sample Orders & Reservations
- 1 đơn hàng mẫu đang chuẩn bị
- 1 reservation mẫu đã confirm

### 🔧 Database Schema

```sql
-- Main Tables
users           -- Người dùng (customer, staff, manager, admin)
categories      -- Danh mục thực đơn
menu_items      -- Món ăn
tables          -- Bàn ăn
orders          -- Đơn hàng
order_items     -- Chi tiết đơn hàng
reservations    -- Đặt bàn

-- Relationships
menu_items -> categories (foreign key)
orders -> users (customer_id)
orders -> tables (table_id)
order_items -> orders (order_id)
order_items -> menu_items (menu_item_id)
reservations -> users (customer_id)
reservations -> tables (table_id)
```

### 🧪 Testing Database

```bash
# Kiểm tra kết nối database
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    print(f'Users count: {result.fetchone()[0]}')
"

# Test với FastAPI
python -c "
from app.core.database import get_db
from app.models.user import User
db = next(get_db())
users = db.query(User).all()
print(f'Found {len(users)} users')
for user in users:
    print(f'- {user.username} ({user.role})')
"
```

### 🔄 Migration Commands

```bash
# Fresh install - xóa toàn bộ dữ liệu và tạo lại
python migrate.py --fresh

# Chỉ kiểm tra database connection và tables
python migrate.py --check

# Hiển thị thông tin database hiện tại
python migrate.py --info

# Migration bình thường (giữ dữ liệu cũ nếu có)
python migrate.py
```

### 📁 File Structure

```
RestoBot/
├── migrate.py              # 🔄 Migration script chính
├── seed_data.py           # 🌱 Dữ liệu mẫu cho SQLAlchemy
├── restobot.py            # 🚀 All-in-One launcher (embedded data)
├── .env                   # ⚙️ Environment configuration
├── app/
│   ├── models/            # 🗄️ SQLAlchemy models
│   │   ├── user.py        # User, UserRole
│   │   ├── menu.py        # Category, MenuItem
│   │   ├── table.py       # Table, TableStatus
│   │   └── order.py       # Order, OrderItem, Reservation
│   └── core/
│       ├── database.py    # Database connection
│       └── security.py    # Password hashing
└── requirements.txt       # Dependencies
```

### ⚠️ Lưu ý quan trọng

1. **Embedded vs Database**: 
   - `restobot.py` sử dụng embedded data đơn giản cho demo
   - `migrate.py` + `seed_data.py` cho PostgreSQL database thật

2. **Environment**: Đảm bảo file `.env` có đúng database URL

3. **Fresh Install**: Sử dụng `--fresh` sẽ XÓA toàn bộ dữ liệu cũ

4. **Dependencies**: SQLAlchemy models cần import đúng thứ tự

### 🎯 Next Steps

Sau khi setup database xong:

1. **Phát triển API endpoints** kết nối với database thật
2. **Tích hợp authentication** với JWT
3. **Xây dựng ReactJS frontend** 
4. **Tối ưu Rasa chatbot** với database context
5. **Deployment** với Docker + PostgreSQL

---

**Liên hệ**: restobot.dev@university.edu.vn