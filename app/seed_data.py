#!/usr/bin/env python3
"""
🍽️ RestoBot API - Database Seed Data
Dữ liệu mẫu cho API service
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
        {"name": "Phở Bò Tái", "description": "Phở bò truyền thống với thịt bò tái, nước dùng được ninh từ xương bò trong 12 tiếng", "price": 85000, "category_id": cat_map["Món chính"].id, "image_url": "/images/pho_bo_tai.jpg", "is_available": True},
        {"name": "Bún Bò Huế", "description": "Bún bò Huế cay nồng đậm đà với thịt bò, chả cua, giò heo", "price": 90000, "category_id": cat_map["Món chính"].id, "image_url": "/images/bun_bo_hue.jpg", "is_available": True},
        {"name": "Cơm Tấm Sườn Nướng", "description": "Cơm tấm với sườn nướng thơm lừng, chả trứng, bì, kèm nước mắm chua ngọt", "price": 75000, "category_id": cat_map["Món chính"].id, "image_url": "/images/com_tam_suon.jpg", "is_available": True},
        {"name": "Bánh Mì Thịt Nướng", "description": "Bánh mì Việt Nam với thịt nướng, pate, rau thơm", "price": 35000, "category_id": cat_map["Món chính"].id, "image_url": "/images/banh_mi_thit_nuong.jpg", "is_available": True},
        
        # Món khai vị
        {"name": "Gỏi Cuốn Tôm Thịt", "description": "Gỏi cuốn tươi với tôm, thịt ba chỉ, bún tàu, rau thơm", "price": 45000, "category_id": cat_map["Món khai vị"].id, "image_url": "/images/goi_cuon.jpg", "is_available": True},
        {"name": "Nem Rán", "description": "Nem rán giòn rụm với nhân thịt, miến, nấm", "price": 50000, "category_id": cat_map["Món khai vị"].id, "image_url": "/images/nem_ran.jpg", "is_available": True},
        
        # Đồ uống
        {"name": "Cà Phê Sữa Đá", "description": "Cà phê phin truyền thống với sữa đặc", "price": 25000, "category_id": cat_map["Đồ uống"].id, "image_url": "/images/cafe_sua_da.jpg", "is_available": True},
        {"name": "Sinh Tố Xoài", "description": "Sinh tố xoài tươi mát với xoài Cát Chu", "price": 35000, "category_id": cat_map["Đồ uống"].id, "image_url": "/images/sinh_to_xoai.jpg", "is_available": True},
        
        # Tráng miệng
        {"name": "Chè Ba Màu", "description": "Chè truyền thống với đậu xanh, đậu đỏ, thạch lá cẩm", "price": 30000, "category_id": cat_map["Tráng miệng"].id, "image_url": "/images/che_ba_mau.jpg", "is_available": True},
        
        # Món chay
        {"name": "Phở Chay", "description": "Phở chay với nước dùng từ nấm hương, đậu hũ, rau củ", "price": 70000, "category_id": cat_map["Món chay"].id, "image_url": "/images/pho_chay.jpg", "is_available": True}
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
    """Tạo danh sách bàn ăn"""
    tables_data = []
    
    # Bàn tầng 1 (1-10)
    for i in range(1, 11):
        capacity = 4 if i <= 6 else 6  # Bàn 1-6 có 4 chỗ, bàn 7-10 có 6 chỗ
        tables_data.append({
            "table_number": str(i),
            "capacity": capacity,
            "location": "Tầng 1",
            "status": TableStatus.available
        })
    
    # Bàn tầng 2 - VIP (11-15)
    for i in range(11, 16):
        tables_data.append({
            "table_number": str(i),
            "capacity": 8,
            "location": "Tầng 2 - VIP",
            "status": TableStatus.available
        })
    
    tables = []
    for table_data in tables_data:
        table = Table(**table_data)
        db.add(table)
        tables.append(table)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(tables)} bàn ăn")
    return tables

def create_users(db: Session):
    """Tạo user mẫu"""
    users_data = [
        {
            "email": "admin@restobot.com",
            "username": "admin",
            "full_name": "Quản lý hệ thống",
            "hashed_password": get_password_hash("admin123"),
            "role": UserRole.admin,
            "phone": "0901234567",
            "is_active": True
        },
        {
            "email": "staff@restobot.com", 
            "username": "staff",
            "full_name": "Nhân viên phục vụ",
            "hashed_password": get_password_hash("staff123"),
            "role": UserRole.staff,
            "phone": "0901234568",
            "is_active": True
        },
        {
            "email": "customer@restobot.com",
            "username": "customer",
            "full_name": "Khách hàng mẫu",
            "hashed_password": get_password_hash("customer123"),
            "role": UserRole.customer,
            "phone": "0901234569",
            "is_active": True
        },
        {
            "email": "nguyenvan@gmail.com",
            "username": "nguyenvan",
            "full_name": "Nguyễn Văn A",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.customer,
            "phone": "0987654321",
            "is_active": True
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

def create_reservations(db: Session, users, tables):
    """Tạo đặt bàn mẫu"""
    
    reservations = []
    now = datetime.now()
    
    reservations_data = [
        {
            "customer_id": users[3].id,  # Nguyễn Văn A
            "table_id": tables[0].id,  # Bàn 1
            "reservation_datetime": now + timedelta(days=1, hours=12),  # Ngày mai 12h
            "party_size": 4,
            "status": ReservationStatus.confirmed,
            "special_requests": "Muốn chỗ ngồi gần cửa sổ"
        },
        {
            "customer_id": users[3].id,
            "table_id": tables[4].id,  # Bàn 5
            "reservation_datetime": now + timedelta(days=2, hours=19),  # Ngày kia 19h
            "party_size": 6,
            "status": ReservationStatus.pending,
            "special_requests": "Cần bàn rộng, có ghế cao cho trẻ em"
        },
        {
            "customer_id": users[2].id,  # Customer user
            "table_id": tables[10].id,  # Bàn VIP
            "reservation_datetime": now + timedelta(days=3, hours=18),
            "party_size": 8,
            "status": ReservationStatus.confirmed,
            "special_requests": "Tiệc sinh nhật, cần trang trí"
        },
        {
            "customer_id": users[3].id,
            "table_id": tables[1].id,  # Bàn 2
            "reservation_datetime": now + timedelta(hours=6),  # Hôm nay 6h tối
            "party_size": 2,
            "status": ReservationStatus.confirmed,
            "special_requests": None
        },
    ]
    
    for res_data in reservations_data:
        reservation = Reservation(**res_data)
        db.add(reservation)
        reservations.append(reservation)
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(reservations)} đặt bàn")
    return reservations

def create_orders(db: Session, users, tables, menu_items):
    """Tạo đơn hàng và chi tiết đơn hàng"""
    
    orders = []
    order_count = 1
    
    # Tạo các đơn hàng mẫu
    orders_data = [
        {
            "customer_id": users[3].id,  # Nguyễn Văn A
            "table_id": tables[0].id,
            "status": OrderStatus.completed,
            "payment_status": PaymentStatus.paid,
            "items": [
                {"menu_item_id": menu_items[0].id, "quantity": 2},  # 2x Phở Bò Tái
                {"menu_item_id": menu_items[6].id, "quantity": 2},  # 2x Cà phê sữa đá
            ]
        },
        {
            "customer_id": users[3].id,
            "table_id": tables[1].id,
            "status": OrderStatus.served,
            "payment_status": PaymentStatus.paid,
            "items": [
                {"menu_item_id": menu_items[1].id, "quantity": 1},  # 1x Bún Bò Huế
                {"menu_item_id": menu_items[4].id, "quantity": 1},  # 1x Gỏi cuốn
                {"menu_item_id": menu_items[9].id, "quantity": 1},  # 1x Chè ba màu
            ]
        },
        {
            "customer_id": users[2].id,  # Customer user
            "table_id": tables[2].id,
            "status": OrderStatus.ready,
            "payment_status": PaymentStatus.pending,
            "items": [
                {"menu_item_id": menu_items[2].id, "quantity": 2},  # 2x Cơm tấm sườn nướng
                {"menu_item_id": menu_items[7].id, "quantity": 2},  # 2x Sinh tố xoài
            ]
        },
        {
            "customer_id": None,  # Walk-in customer
            "table_id": tables[3].id,
            "status": OrderStatus.preparing,
            "payment_status": PaymentStatus.pending,
            "items": [
                {"menu_item_id": menu_items[3].id, "quantity": 3},  # 3x Bánh mì thịt nướng
                {"menu_item_id": menu_items[5].id, "quantity": 2},  # 2x Nem rán
            ]
        },
        {
            "customer_id": users[3].id,
            "table_id": tables[4].id,
            "status": OrderStatus.pending,
            "payment_status": PaymentStatus.pending,
            "items": [
                {"menu_item_id": menu_items[8].id, "quantity": 1},  # 1x Phở chay
                {"menu_item_id": menu_items[0].id, "quantity": 1},  # 1x Phở Bò Tái
                {"menu_item_id": menu_items[6].id, "quantity": 3},  # 3x Cà phê sữa đá
            ]
        }
    ]
    
    for order_data in orders_data:
        items_data = order_data.pop("items")
        
        # Tính tổng tiền
        total_amount = 0
        tax_amount = 0
        
        # Tạo order
        order = Order(
            order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-{order_count:04d}",
            customer_id=order_data["customer_id"],
            table_id=order_data["table_id"],
            status=order_data["status"],
            payment_status=order_data["payment_status"],
            total_amount=0,  # Sẽ cập nhật sau
            tax_amount=0,
            discount_amount=0,
            notes="Dữ liệu mẫu từ seed"
        )
        
        db.add(order)
        db.flush()  # Lấy ID của order vừa tạo
        
        # Tạo menu item lookup dictionary for performance
        menu_item_dict = {item.id: item for item in menu_items}
        
        # Tạo order items
        for item_data in items_data:
            menu_item = menu_item_dict[item_data["menu_item_id"]]
            quantity = item_data["quantity"]
            unit_price = menu_item.price
            item_total = unit_price * quantity
            total_amount += item_total
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data["menu_item_id"],
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total,
                special_instructions=None
            )
            db.add(order_item)
        
        # Cập nhật tổng tiền cho order (tính thuế 10%)
        tax_amount = total_amount * 0.1
        order.total_amount = total_amount + tax_amount
        order.tax_amount = tax_amount
        
        orders.append(order)
        order_count += 1
    
    db.commit()
    logger.info(f"✅ Đã tạo {len(orders)} đơn hàng với chi tiết")
    return orders

def seed_database(db: Session):
    """Seed toàn bộ database"""
    logger.info("🌱 Bắt đầu seed database...")
    
    # 1. Tạo danh mục
    categories = create_categories(db)
    
    # 2. Tạo món ăn
    menu_items = create_menu_items(db, categories)
    
    # 3. Tạo bàn ăn
    tables = create_tables(db)
    
    # 4. Tạo người dùng
    users = create_users(db)
    
    # 5. Tạo đặt bàn (Reservations)
    reservations = create_reservations(db, users, tables)
    
    # 6. Tạo đơn hàng (Orders) và chi tiết đơn hàng (OrderItems)
    orders = create_orders(db, users, tables, menu_items)
    
    logger.info("🎉 Seed database hoàn thành!")