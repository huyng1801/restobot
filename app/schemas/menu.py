from __future__ import annotations
from pydantic import BaseModel, validator
from typing import Optional, List, Any
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Category(CategoryInDBBase):
    pass


class CategoryWithItems(CategoryInDBBase):
    menu_items: List[Any] = []  # Use Any to avoid circular reference


class PaginatedCategoryResponse(BaseModel):
    items: List[Category]
    total: int
    skip: int
    limit: int


# Menu Item Schemas
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: bool = True
    is_featured: bool = False
    preparation_time: Optional[int] = None
    category_id: int

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('preparation_time')
    def validate_preparation_time(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Preparation time must be greater than 0')
        return v


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None
    preparation_time: Optional[int] = None
    category_id: Optional[int] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('preparation_time')
    def validate_preparation_time(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Preparation time must be greater than 0')
        return v


class MenuItemInDBBase(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class MenuItem(MenuItemInDBBase):
    category: Any  # Use Any to avoid circular reference


class MenuItemSimple(MenuItemInDBBase):
    """MenuItem without category details to avoid circular import"""
    pass


# Paginated Response Schemas
class PaginatedMenuResponse(BaseModel):
    items: List[MenuItem]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        orm_mode = True


# Update forward references for Pydantic v1 compatibility
try:
    # Pydantic v2
    CategoryWithItems.model_rebuild()
    MenuItem.model_rebuild()
    PaginatedMenuResponse.model_rebuild()
except AttributeError:
    # Pydantic v1 - use update_forward_refs()
    try:
        CategoryWithItems.update_forward_refs()
        MenuItem.update_forward_refs()
        PaginatedMenuResponse.update_forward_refs()
    except NameError:
        # Forward references will be resolved when all classes are defined
        pass