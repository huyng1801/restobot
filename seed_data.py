#!/usr/bin/env python3
"""
🍽️ RestoBot - Database Seed Data
Dữ liệu mẫu cho SQLAlchemy models và PostgreSQL migration
"""

from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.menu import Category, MenuItem
from app.models.table import Table, TableStatus
from app.models.order import Order, OrderItem, Reservation, OrderStatus, PaymentStatus, ReservationStatus
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_categories(db: Session):
    """Tạo danh mục thực đơn"""
    categories_data = [
        {
            "name": "Món chính",
            "description": "Các món ăn chính truyền thống Việt Nam như phở, bún, cơm"
        },
        {
            "name": "Món khai vị", 
            "description": "Các món ăn nhẹ khai vị trước bữa chính"
        },
        {
            "name": "Đồ uống",
            "description": "Nước uống, cà phê, trà và các loại sinh tố"
        },
        {
            "name": "Tráng miệng",
            "description": "Các món tráng miệng và chè ngọt"
        },
        {
            "name": "Món chay",
            "description": "Thực đơn dành cho người ăn chay"
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)
        categories.append(category)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(categories)} danh mục thực đơn")
    return categories

def create_menu_items(db: Session, categories):
    """Tạo món ăn cho từng danh mục"""
    
    # Lấy categories theo tên
    cat_map = {cat.name: cat for cat in categories}
    
    menu_items_data = [
        # Món chính
        {
            "name": "Phở Bò Tái",
            "description": "Phở bò truyền thống với thịt bò tái, nước dùng được ninh từ xương bò trong nhiều giờ",
            "price": 85000,
            "category": cat_map["Món chính"],
            "preparation_time": 15,
            "is_featured": True,
            "image_url": "/images/pho-bo-tai.jpg"
        },
        {
            "name": "Phở Gà",
            "description": "Phở gà thanh đạm với thịt gà tươi và nước dùng trong vắt",
            "price": 75000,
            "category": cat_map["Món chính"],
            "preparation_time": 12,
            "image_url": "/images/pho-ga.jpg"
        },
        {
            "name": "Bún Bò Huế",
            "description": "Bún bò Huế cay nồng đặc trưng với thịt bò, chả cua và mắm ruốc",
            "price": 90000,
            "category": cat_map["Món chính"],
            "preparation_time": 18,
            "is_featured": True,
            "image_url": "/images/bun-bo-hue.jpg"
        },
        {
            "name": "Cơm Tấm Sườn Nướng",
            "description": "Cơm tấm với sườn nướng thơm phức, chả trứng và bì",
            "price": 95000,
            "category": cat_map["Món chính"],
            "preparation_time": 20,
            "image_url": "/images/com-tam-suon-nuong.jpg"
        },
        {
            "name": "Bánh Mì Pate",
            "description": "Bánh mì giòn với pate, thịt nguội, dưa chua và rau thơm",
            "price": 25000,
            "category": cat_map["Món chính"],
            "preparation_time": 5,
            "image_url": "/images/banh-mi-pate.jpg"
        },
        
        # Món khai vị
        {
            "name": "Gỏi Cuốn",
            "description": "Gỏi cuốn tươi với tôm, thịt luộc, rau sống và bánh tráng",
            "price": 45000,
            "category": cat_map["Món khai vị"],
            "preparation_time": 8,
            "image_url": "/images/goi-cuon.jpg"
        },
        {
            "name": "Chả Giò",
            "description": "Chả giò giòn rụm với nhân thịt, tôm và miến",
            "price": 55000,
            "category": cat_map["Món khai vị"],
            "preparation_time": 15,
            "image_url": "/images/cha-gio.jpg"
        },
        {
            "name": "Nem Nướng",
            "description": "Nem nướng thơm ngon ăn kèm bánh tráng và rau sống",
            "price": 60000,
            "category": cat_map["Món khai vị"],
            "preparation_time": 12,
            "image_url": "/images/nem-nuong.jpg"
        },
        
        # Đồ uống
        {
            "name": "Cà Phê Sữa Đá",
            "description": "Cà phê phin truyền thống với sữa đặc và đá",
            "price": 35000,
            "category": cat_map["Đồ uống"],
            "preparation_time": 8,
            "is_featured": True,
            "image_url": "/images/ca-phe-sua-da.jpg"
        },
        {
            "name": "Trà Đá",
            "description": "Trà đá truyền thống mát lạnh",
            "price": 15000,
            "category": cat_map["Đồ uống"],
            "preparation_time": 2,
            "image_url": "/images/tra-da.jpg"
        },
        {
            "name": "Sinh Tố Xoài",
            "description": "Sinh tố xoài ngọt mát với sữa và đá",
            "price": 45000,
            "category": cat_map["Đồ uống"],
            "preparation_time": 5,
            "image_url": "/images/sinh-to-xoai.jpg"
        },
        {
            "name": "Nước Mía",
            "description": "Nước mía tươi mát, ngọt tự nhiên",
            "price": 20000,
            "category": cat_map["Đồ uống"],
            "preparation_time": 3,
            "image_url": "/images/nuoc-mia.jpg"
        },
        
        # Tráng miệng
        {
            "name": "Chè Ba Màu",
            "description": "Chè ba màu với đậu xanh, đậu đỏ và thạch",
            "price": 30000,
            "category": cat_map["Tráng miệng"],
            "preparation_time": 10,
            "image_url": "/images/che-ba-mau.jpg"
        },
        {
            "name": "Bánh Flan",
            "description": "Bánh flan mềm mịn với caramen đắng ngọt",
            "price": 25000,
            "category": cat_map["Tráng miệng"],
            "preparation_time": 5,
            "image_url": "/images/banh-flan.jpg"
        },
        
        # Món chay
        {
            "name": "Phở Chay",
            "description": "Phở chay với nấm, đậu hũ và rau củ tươi ngon",
            "price": 70000,
            "category": cat_map["Món chay"],
            "preparation_time": 15,
            "image_url": "/images/pho-chay.jpg"
        }
    ]
    
    menu_items = []
    for item_data in menu_items_data:
        menu_item = MenuItem(**item_data)
        db.add(menu_item)
        menu_items.append(menu_item)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(menu_items)} món ăn")
    return menu_items

def create_tables(db: Session):
    """Tạo bàn ăn"""
    tables_data = [
        # Tầng 1 - Khu vực chính
        {"table_number": "T01", "capacity": 2, "location": "Tầng 1 - Cửa sổ", "status": TableStatus.available},
        {"table_number": "T02", "capacity": 2, "location": "Tầng 1 - Cửa sổ", "status": TableStatus.occupied},
        {"table_number": "T03", "capacity": 4, "location": "Tầng 1 - Trung tâm", "status": TableStatus.available},
        {"table_number": "T04", "capacity": 4, "location": "Tầng 1 - Trung tâm", "status": TableStatus.reserved},
        {"table_number": "T05", "capacity": 6, "location": "Tầng 1 - Sân vườn", "status": TableStatus.available},
        {"table_number": "T06", "capacity": 6, "location": "Tầng 1 - Sân vườn", "status": TableStatus.occupied},
        
        # Tầng 2 - Khu vực yên tĩnh
        {"table_number": "T07", "capacity": 2, "location": "Tầng 2 - Ban công", "status": TableStatus.available},
        {"table_number": "T08", "capacity": 4, "location": "Tầng 2 - Phòng riêng", "status": TableStatus.available},
        {"table_number": "T09", "capacity": 8, "location": "Tầng 2 - Phòng họp", "status": TableStatus.reserved},
        {"table_number": "T10", "capacity": 10, "location": "Tầng 2 - Phòng tiệc", "status": TableStatus.available},
        
        # Khu VIP
        {"table_number": "VIP01", "capacity": 4, "location": "VIP - Phòng riêng 1", "status": TableStatus.available},
        {"table_number": "VIP02", "capacity": 6, "location": "VIP - Phòng riêng 2", "status": TableStatus.occupied},
        {"table_number": "VIP03", "capacity": 12, "location": "VIP - Phòng lớn", "status": TableStatus.available},
        
        # Quầy bar
        {"table_number": "BAR01", "capacity": 1, "location": "Quầy bar", "status": TableStatus.available},
        {"table_number": "BAR02", "capacity": 1, "location": "Quầy bar", "status": TableStatus.occupied},
    ]
    
    tables = []
    for table_data in tables_data:
        table = Table(**table_data)
        db.add(table)
        tables.append(table)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(tables)} bàn ăn")
    return tables

def create_users(db: Session):
    """Tạo người dùng hệ thống"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@restobot.vn",
            "full_name": "Quản trị viên hệ thống",
            "phone": "0901234567",
            "role": UserRole.admin,
            "hashed_password": get_password_hash("admin123")
        },
        {
            "username": "manager001",
            "email": "manager@restobot.vn",
            "full_name": "Nguyễn Văn Quản Lý",
            "phone": "0902345678",
            "role": UserRole.manager,
            "hashed_password": get_password_hash("manager123")
        },
        {
            "username": "staff001",
            "email": "nhanvien1@restobot.vn",
            "full_name": "Trần Thị Nhân Viên",
            "phone": "0903456789",
            "role": UserRole.staff,
            "hashed_password": get_password_hash("staff123")
        },
        {
            "username": "staff002",
            "email": "nhanvien2@restobot.vn",
            "full_name": "Lê Văn Phục Vụ",
            "phone": "0904567890",
            "role": UserRole.staff,
            "hashed_password": get_password_hash("staff123")
        },
        {
            "username": "customer001",
            "email": "khachhang1@gmail.com",
            "full_name": "Hoàng Thị Khách Hàng",
            "phone": "0905678901",
            "role": UserRole.customer,
            "hashed_password": get_password_hash("customer123")
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(users)} người dùng")
    return users

def create_sample_orders(db: Session, users, tables, menu_items):
    """Tạo đơn hàng mẫu"""
    # Tìm customer và staff
    customer = next((u for u in users if u.role == UserRole.customer), None)
    staff = next((u for u in users if u.role == UserRole.staff), None)
    
    if not customer or not staff:
        logger.warning("⚠️ Không tìm thấy customer hoặc staff để tạo đơn hàng mẫu")
        return []
    
    # Tìm bàn và món ăn
    occupied_table = next((t for t in tables if t.status == TableStatus.occupied), None)
    if not occupied_table or not menu_items:
        logger.warning("⚠️ Không tìm thấy bàn hoặc món ăn để tạo đơn hàng")
        return []
    
    # Tạo đơn hàng mẫu
    order = Order(
        order_number="ORD-20241010-001",
        customer_id=customer.id,
        table_id=occupied_table.id,
        status=OrderStatus.preparing,
        payment_status=PaymentStatus.pending,
        notes="Không hành lá trong phở"
    )
    db.add(order)
    db.commit()
    
    # Thêm món vào đơn hàng
    order_items = []
    
    # Phở bò tái x2
    pho_bo = next((item for item in menu_items if "Phở Bò" in item.name), None)
    if pho_bo:
        order_item1 = OrderItem(
            order_id=order.id,
            menu_item_id=pho_bo.id,
            quantity=2,
            unit_price=pho_bo.price,
            total_price=2 * pho_bo.price
        )
        order_items.append(order_item1)
        db.add(order_item1)
    
    # Cà phê sữa đá x2
    ca_phe = next((item for item in menu_items if "Cà Phê" in item.name), None)
    if ca_phe:
        order_item2 = OrderItem(
            order_id=order.id,
            menu_item_id=ca_phe.id,
            quantity=2,
            unit_price=ca_phe.price,
            total_price=2 * ca_phe.price
        )
        order_items.append(order_item2)
        db.add(order_item2)
    
    # Tính tổng tiền
    total = sum(item.quantity * item.unit_price for item in order_items)
    tax = total * 0.1  # VAT 10%
    
    order.total_amount = total + tax
    order.tax_amount = tax
    
    db.commit()
    logger.info(f"✅ Đã tạo đơn hàng mẫu với {len(order_items)} món")
    return [order]

def create_sample_reservations(db: Session, users, tables):
    """Tạo đặt bàn mẫu"""
    customer = next((u for u in users if u.role == UserRole.customer), None)
    reserved_table = next((t for t in tables if t.status == TableStatus.reserved), None)
    
    if not customer or not reserved_table:
        logger.warning("⚠️ Không tìm thấy customer hoặc bàn để tạo reservation")
        return []
    
    reservation = Reservation(
        customer_id=customer.id,
        table_id=reserved_table.id,
        reservation_date=datetime.now() + timedelta(hours=2),
        party_size=4,
        status=ReservationStatus.confirmed,
        special_requests="Sinh nhật, cần bánh kem",
        notes="Khách VIP"
    )
    
    db.add(reservation)
    db.commit()
    logger.info("✅ Đã tạo reservation mẫu")
    return [reservation]

def seed_database(db: Session):
    """Chạy toàn bộ seed data"""
    logger.info("🌱 Bắt đầu seed database...")
    
    try:
        # Tạo dữ liệu theo thứ tự dependencies
        categories = create_categories(db)
        menu_items = create_menu_items(db, categories)
        tables = create_tables(db)
        users = create_users(db)
        orders = create_sample_orders(db, users, tables, menu_items)
        reservations = create_sample_reservations(db, users, tables)
        
        logger.info("🎉 Seed database hoàn thành!")
        logger.info(f"📊 Tổng kết: {len(categories)} categories, {len(menu_items)} menu items, {len(tables)} tables, {len(users)} users, {len(orders)} orders, {len(reservations)} reservations")
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi seed database: {e}")
        db.rollback()
        raise

if __name__ == "__main__":
    # Script để chạy seed data trực tiếp
    from app.core.database import get_db, engine
    from app.models import Base
    
    # Tạo tables
    Base.metadata.create_all(bind=engine)
    
    # Seed data
    db = next(get_db())
    seed_database(db)
    db.close()