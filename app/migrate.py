#!/usr/bin/env python3
"""
🍽️ RestoBot API - Database Migration Script
Run migrations for API service in Docker environment
"""
import sys
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import Base, get_db, engine
from models.user import User
from models.menu import Category, MenuItem  
from models.table import Table
from models.order import Order, OrderItem, Reservation

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