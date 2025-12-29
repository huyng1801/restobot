#!/usr/bin/env python3
"""
🍽️ RestoBot API - Database Migration Script
Run migrations for API service in Docker environment
Run with: python -c "import sys; sys.path.insert(0, '/app'); exec(open('migrate.py').read())"
Or: python migrate.py from /app directory
"""
import sys
import os
import logging

# Setup path
if '/app' not in sys.path:
    sys.path.insert(0, '/app')
os.chdir('/app')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

try:
    from core.database import Base, engine
    from models.user import User
    from models.menu import Category, MenuItem  
    from models.table import Table
    from models.order import Order, OrderItem, Reservation
    from seed_data import seed_database
except ImportError as e:
    print(f"Import error: {e}")
    print(f"sys.path: {sys.path}")
    print(f"Current dir: {os.getcwd()}")
    raise

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Kiểm tra kết nối database"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✅ Kết nối database thành công")
            return True
    except OperationalError as e:
        logger.error(f"❌ Lỗi kết nối database: {e}")
        return False

def create_database_tables():
    """Tạo tất cả tables từ SQLAlchemy models"""
    try:
        logger.info("🔨 Tạo database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Import seed_data and run seeding
        sys.path.append('/app')
        from seed_data import seed_database
        
        # Get database session and seed data
        session = sessionmaker(bind=engine)()
        seed_database(session)
        session.close()
        
        logger.info("✅ Database tables đã được tạo và seed data thành công")
        return True
        
    except Exception as e:
        logger.error(f"❌ Lỗi tạo tables: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Bắt đầu API database migration...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("❌ Migration thất bại - không thể kết nối database")
        sys.exit(1)
    
    # Create tables and seed data
    if not create_database_tables():
        logger.error("❌ Migration thất bại - không thể tạo tables")
        sys.exit(1)
    
    logger.info("🎉 API Migration hoàn thành thành công!")

if __name__ == "__main__":
    main()