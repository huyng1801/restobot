"""
Database migration: Add arrival tracking fields to Reservation model
"""
from sqlalchemy import Column, DateTime, String
from app.core.database import engine
from app.models.order import Reservation
import logging

logger = logging.getLogger(__name__)


def upgrade():
    """Add arrival tracking fields"""
    from sqlalchemy import MetaData, Table
    
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Check if columns already exist
    reservations_table = metadata.tables.get('reservations')
    
    if reservations_table is not None:
        existing_columns = [col.name for col in reservations_table.columns]
        
        # Add actual_arrival_time column if it doesn't exist
        if 'actual_arrival_time' not in existing_columns:
            with engine.connect() as conn:
                conn.execute(
                    'ALTER TABLE reservations ADD COLUMN actual_arrival_time TIMESTAMP WITH TIME ZONE'
                )
                conn.commit()
                logger.info("Added actual_arrival_time column to reservations table")
        
        # Add arrival_status column if it doesn't exist  
        if 'arrival_status' not in existing_columns:
            with engine.connect() as conn:
                conn.execute(
                    'ALTER TABLE reservations ADD COLUMN arrival_status VARCHAR(50)'
                )
                conn.commit()
                logger.info("Added arrival_status column to reservations table")
        
        # Add reservation_datetime column if it doesn't exist (rename from reservation_date)
        if 'reservation_datetime' not in existing_columns and 'reservation_date' in existing_columns:
            with engine.connect() as conn:
                conn.execute(
                    'ALTER TABLE reservations RENAME COLUMN reservation_date TO reservation_datetime'
                )
                conn.commit()
                logger.info("Renamed reservation_date to reservation_datetime")
        
        # Add estimated_end_time column if it doesn't exist
        if 'estimated_end_time' not in existing_columns:
            with engine.connect() as conn:
                # Default to 2 hours after reservation time
                conn.execute(
                    '''
                    ALTER TABLE reservations 
                    ADD COLUMN estimated_end_time TIMESTAMP WITH TIME ZONE
                    '''
                )
                conn.commit()
                
                # Update existing records to have estimated_end_time = reservation_datetime + 2 hours
                conn.execute(
                    '''
                    UPDATE reservations 
                    SET estimated_end_time = reservation_datetime + INTERVAL '2 hours'
                    WHERE estimated_end_time IS NULL
                    '''
                )
                conn.commit()
                logger.info("Added estimated_end_time column to reservations table")
        
        logger.info("Migration completed successfully")
    else:
        logger.error("Reservations table not found")


def downgrade():
    """Remove arrival tracking fields"""
    with engine.connect() as conn:
        conn.execute('ALTER TABLE reservations DROP COLUMN IF EXISTS actual_arrival_time')
        conn.execute('ALTER TABLE reservations DROP COLUMN IF EXISTS arrival_status')
        conn.execute('ALTER TABLE reservations DROP COLUMN IF EXISTS estimated_end_time')
        conn.commit()
        logger.info("Downgrade completed - removed arrival tracking columns")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Running migration: Add arrival tracking fields...")
    upgrade()
    print("Migration completed!")