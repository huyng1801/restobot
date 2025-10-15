# Import all schemas here
from .user import User, UserCreate, UserUpdate, UserLogin, Token, TokenData
from .menu import Category, CategoryCreate, CategoryUpdate, CategoryWithItems, MenuItem, MenuItemCreate, MenuItemUpdate, MenuItemSimple
from .table import Table, TableCreate, TableUpdate, TableStatusUpdate
from .order import Order, OrderCreate, OrderUpdate, OrderItem, OrderItemCreate, OrderItemUpdate, Reservation, ReservationCreate, ReservationUpdate, OrderSummary

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate", "UserLogin", "Token", "TokenData",
    # Menu schemas
    "Category", "CategoryCreate", "CategoryUpdate", "CategoryWithItems",
    "MenuItem", "MenuItemCreate", "MenuItemUpdate", "MenuItemSimple",
    # Table schemas
    "Table", "TableCreate", "TableUpdate", "TableStatusUpdate",
    # Order schemas
    "Order", "OrderCreate", "OrderUpdate", "OrderItem", "OrderItemCreate", "OrderItemUpdate",
    "Reservation", "ReservationCreate", "ReservationUpdate", "OrderSummary"
]