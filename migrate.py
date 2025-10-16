#!/usr/bin/env python3
"""
🍽️ RestoBot - Database Migration & Setup Script
Thiết lập database PostgreSQL/SQLite và seed dữ liệu mẫu cho nhà hàng

Usage:
    python migrate.py           # Setup database với dữ liệu mẫu
    python migrate.py --fresh   # Xóa và tạo lại database từ đầu
    python migrate.py --info    # Hiển thị thông tin database
"""

import os
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging

# Add app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, get_db, engine
from app.models.user import User
from app.models.menu import Category, MenuItem  
from app.models.table import Table
from app.models.order import Order, OrderItem, Reservation
from seed_data import seed_database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Kiểm tra kết nối database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Kết nối PostgreSQL thành công: {version}")
            return True
    except OperationalError as e:
        logger.error(f"❌ Không thể kết nối database: {e}")
        return False

def create_database_tables():
    """Tạo tất cả tables từ SQLAlchemy models"""
    try:
        logger.info("🔨 Đang tạo database tables...")
        
        # Import tất cả models để đảm bảo chúng được đăng ký
        from app.models import user, menu, table, order
        
        # Tạo tất cả tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Đã tạo tất cả database tables")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi tạo tables: {e}")
        return False

def drop_all_tables():
    """Xóa tất cả tables (cẩn thận!)"""
    try:
        logger.warning("⚠️ Đang xóa tất cả tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Đã xóa tất cả tables")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi khi xóa tables: {e}")
        return False

def check_tables_exist():
    """Kiểm tra xem tables đã tồn tại chưa"""
    try:
        with engine.connect() as conn:
            # Kiểm tra một số tables chính
            tables_to_check = ['users', 'categories', 'menu_items', 'tables', 'orders']
            existing_tables = []
            
            for table_name in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table_name}'
                    );
                """))
                exists = result.fetchone()[0]
                if exists:
                    existing_tables.append(table_name)
            
            logger.info(f"📋 Tables hiện có: {existing_tables}")
            return len(existing_tables) == len(tables_to_check)
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi kiểm tra tables: {e}")
        return False

def run_migrations(fresh_install=False):
    """Chạy migration process"""
    logger.info("🚀 Bắt đầu database migration...")
    
    # 1. Kiểm tra kết nối database
    if not check_database_connection():
        logger.error("❌ Migration thất bại: Không thể kết nối database")
        return False
    
    # 2. Xóa tables cũ nếu fresh install
    if fresh_install:
        logger.warning("🔄 Fresh install - đang xóa dữ liệu cũ...")
        drop_all_tables()
    
    # 3. Tạo tables
    if not create_database_tables():
        logger.error("❌ Migration thất bại: Không thể tạo tables")
        return False
    
    # 4. Kiểm tra tables đã được tạo
    if not check_tables_exist():
        logger.error("❌ Migration thất bại: Tables chưa được tạo đầy đủ")
        return False
    
    # 5. Seed dữ liệu
    try:
        logger.info("🌱 Đang seed dữ liệu...")
        db = next(get_db())
        seed_database(db)
        db.close()
        logger.info("✅ Seed dữ liệu thành công")
    except Exception as e:
        logger.error(f"❌ Lỗi khi seed dữ liệu: {e}")
        return False
    
    logger.info("🎉 Migration hoàn thành thành công!")
    return True

def show_database_info():
    """Hiển thị thông tin database"""
    try:
        with engine.connect() as conn:
            # Thông tin database
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            
            logger.info("📊 THÔNG TIN DATABASE")
            logger.info(f"   Database: {db_info[0]}")
            logger.info(f"   User: {db_info[1]}")
            
            # Đếm records trong từng table
            tables_info = [
                ('users', 'Người dùng'),
                ('categories', 'Danh mục'),
                ('menu_items', 'Món ăn'),
                ('tables', 'Bàn ăn'),
                ('orders', 'Đơn hàng'),
                ('order_items', 'Chi tiết đơn hàng'),
                ('reservations', 'Đặt bàn')
            ]
            
            logger.info("📋 SỐ LƯỢNG RECORDS:")
            for table_name, description in tables_info:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    logger.info(f"   {description}: {count}")
                except Exception:
                    logger.info(f"   {description}: N/A")
                    
    except Exception as e:
        logger.error(f"❌ Lỗi khi lấy thông tin database: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='🍽️ RestoBot Database Migration & Setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python migrate.py              # Setup database với dữ liệu mẫu
    python migrate.py --fresh      # Xóa và tạo lại database từ đầu  
    python migrate.py --info       # Hiển thị thông tin database
    python migrate.py --check      # Chỉ kiểm tra kết nối

Note: 
    - Nếu chưa có .env file, script sẽ sử dụng SQLite
    - Để dùng PostgreSQL, tạo file .env với DATABASE_URL
    """
    )
    
    parser.add_argument('--fresh', action='store_true', 
                       help='Fresh install - xóa dữ liệu cũ và tạo lại từ đầu')
    parser.add_argument('--info', action='store_true', 
                       help='Hiển thị thông tin database hiện tại')
    parser.add_argument('--check', action='store_true', 
                       help='Chỉ kiểm tra kết nối database')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🍽️  RESTOBOT - Database Migration & Setup")
    print("📊 Building an Intelligent Virtual Assistant for Restaurants")
    print("=" * 60)
    
    if args.info:
        show_database_info()
    elif args.check:
        print("🔍 Kiểm tra kết nối database...")
        if check_database_connection():
            check_tables_exist()
        else:
            print("💡 Hướng dẫn:")
            print("   1. Cài đặt PostgreSQL và tạo database")
            print("   2. Tạo file .env với DATABASE_URL")
            print("   3. Chạy lại script này")
    else:
        print("🚀 Đang setup database...")
        success = run_migrations(fresh_install=args.fresh)
        if success:
            print("\n" + "=" * 60)
            show_database_info()
            print("✅ Database setup hoàn thành!")
            print("💡 Bây giờ có thể chạy: python restobot.py")
            print("=" * 60)
        else:
            print("❌ Database setup thất bại!")
            print("💡 Kiểm tra kết nối và thử lại")
            sys.exit(1)

if __name__ == "__main__":
    main()