from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class TableStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"
    
class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    status = Column(SQLEnum(TableStatus), default=TableStatus.available, nullable=False)
    location = Column(String, nullable=True)  # e.g., "Window side", "VIP area"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reservations = relationship("Reservation", back_populates="table")
    orders = relationship("Order", back_populates="table")