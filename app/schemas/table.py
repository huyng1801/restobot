from __future__ import annotations
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.models.table import TableStatus


class TableBase(BaseModel):
    table_number: str
    capacity: int
    status: TableStatus = TableStatus.available
    location: Optional[str] = None
    is_active: bool = True

    @validator('capacity')
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[TableStatus] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('capacity')
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Capacity must be greater than 0')
        return v


class TableInDBBase(TableBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Table(TableInDBBase):
    pass


class TableStatusUpdate(BaseModel):
    status: TableStatus
