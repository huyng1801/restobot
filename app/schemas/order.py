from __future__ import annotations
from pydantic import BaseModel, validator
from typing import Optional, List, Any
from datetime import datetime
from app.models.order import ReservationStatus, OrderStatus, PaymentStatus


# Reservation Schemas
class ReservationBase(BaseModel):
    table_id: int
    reservation_date: datetime
    party_size: int
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    @validator('party_size')
    def validate_party_size(cls, v):
        if v <= 0:
            raise ValueError('Party size must be greater than 0')
        return v


class ReservationCreate(ReservationBase):
    customer_id: Optional[int] = None  # Can be null for walk-in reservations


class ReservationUpdate(BaseModel):
    table_id: Optional[int] = None
    reservation_date: Optional[datetime] = None
    party_size: Optional[int] = None
    status: Optional[ReservationStatus] = None
    special_requests: Optional[str] = None
    notes: Optional[str] = None

    @validator('party_size')
    def validate_party_size(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Party size must be greater than 0')
        return v


class ReservationInDBBase(ReservationBase):
    id: int
    customer_id: Optional[int]
    status: ReservationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Reservation(ReservationInDBBase):
    pass


class ReservationWithDetails(ReservationInDBBase):
    # Customer information
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    
    # Table information
    table_number: Optional[str] = None
    table_capacity: Optional[int] = None
    table_location: Optional[str] = None


# Order Item Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    special_instructions: Optional[str] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    special_instructions: Optional[str] = None

    @validator('quantity')
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    total_price: float
    created_at: datetime

    class Config:
        orm_mode = True


class OrderItem(OrderItemInDBBase):
    pass


# Order Schemas
class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    order_items: List[Any] = []  # Use Any to avoid circular reference


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class OrderInDBBase(OrderBase):
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: float
    tax_amount: float
    discount_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Order(OrderInDBBase):
    order_items: List[Any] = []  # Use Any to avoid circular reference


class OrderWithDetails(OrderInDBBase):
    """Order with customer and table details for admin view"""
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    table_number: Optional[str] = None
    order_items: List[Any] = []


class OrderSummary(BaseModel):
    """Summary for dashboard/statistics"""
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_revenue: float


class DashboardStats(BaseModel):
    """Complete dashboard statistics"""
    # Orders
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_revenue: float
    
    # Tables
    total_tables: int
    available_tables: int
    occupied_tables: int
    reserved_tables: int
    
    # Users
    total_customers: int
    total_staff: int
    
    # Menu
    total_menu_items: int
    available_menu_items: int
    
    # Reservations
    total_reservations: int
    pending_reservations: int
    confirmed_reservations: int
    
    # Recent activity
    recent_orders: List[dict] = []
    recent_reservations: List[dict] = []
    popular_items: List[dict] = []

# Paginated Response Schemas
class PaginatedReservationResponse(BaseModel):
    items: List[ReservationWithDetails]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True

class PaginatedOrderResponse(BaseModel):
    items: List[OrderWithDetails]
    total: int
    skip: int
    limit: int

    class Config:
        orm_mode = True


# Update forward references for Pydantic v1 compatibility
try:
    # Pydantic v2
    OrderCreate.model_rebuild()
    Order.model_rebuild()
    OrderItem.model_rebuild()
    PaginatedReservationResponse.model_rebuild()
except AttributeError:
    # Pydantic v1 - use update_forward_refs()
    try:
        OrderCreate.update_forward_refs()
        Order.update_forward_refs()
        OrderItem.update_forward_refs()
        PaginatedReservationResponse.update_forward_refs()
    except NameError:
        # Forward references will be resolved when all classes are defined
        pass