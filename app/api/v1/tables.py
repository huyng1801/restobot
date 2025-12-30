from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.table import table as table_crud
from app.schemas.table import Table, TableCreate, TableUpdate, TableStatusUpdate
from app.models.table import TableStatus
from app.api.deps import get_current_staff_user, get_current_user_optional
from pydantic import BaseModel

router = APIRouter()


class TablesResponse(BaseModel):
    tables: List[Table]
    total: int


@router.get("/", response_model=TablesResponse)
def read_tables(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(True, description="Filter only active tables"),
    status: Optional[TableStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by table number or location"),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Retrieve tables with pagination and search.
    """
    tables = table_crud.get_multi(
        db, skip=skip, limit=limit, 
        active_only=active_only, 
        status=status,
        search=search
    )
    total = table_crud.count(
        db, active_only=active_only, 
        status=status,
        search=search
    )
    return TablesResponse(tables=tables, total=total)


@router.get("/available", response_model=List[Table])
def read_available_tables(
    db: Session = Depends(get_db),
    min_capacity: Optional[int] = Query(None, description="Minimum capacity required"),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Retrieve available tables.
    """
    tables = table_crud.get_available_tables(db, min_capacity=min_capacity)
    return tables


@router.get("/by-status/{status}", response_model=List[Table])
def read_tables_by_status(
    *,
    db: Session = Depends(get_db),
    status: TableStatus,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get tables by status (Staff+ only).
    """
    tables = table_crud.get_by_status(db, status=status)
    return tables


@router.post("/", response_model=Table)
def create_table(
    *,
    db: Session = Depends(get_db),
    table_in: TableCreate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Create new table (Staff+ only).
    """
    # Check if table number already exists
    existing_table = table_crud.get_by_table_number(db, table_number=table_in.table_number)
    if existing_table:
        raise HTTPException(
            status_code=400,
            detail="Table with this number already exists"
        )
    
    table = table_crud.create(db, obj_in=table_in)
    return table


@router.get("/{table_id}", response_model=Table)
def read_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Get table by ID.
    """
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.put("/{table_id}", response_model=Table)
def update_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    table_in: TableUpdate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update table (Staff+ only).
    """
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Check if new table number conflicts with existing table
    if table_in.table_number and table_in.table_number != table.table_number:
        existing_table = table_crud.get_by_table_number(db, table_number=table_in.table_number)
        if existing_table:
            raise HTTPException(
                status_code=400,
                detail="Table with this number already exists"
            )
    
    table = table_crud.update(db, db_obj=table, obj_in=table_in)
    return table


@router.patch("/{table_id}/status", response_model=Table)
def update_table_status(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    status_update: TableStatusUpdate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update table status (Staff+ only).
    """
    table = table_crud.update_status(db, table_id=table_id, status=status_update.status)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.delete("/{table_id}", response_model=Table)
def delete_table(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Delete table (Staff+ only).
    """
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Check if table is currently occupied or reserved
    if table.status in [TableStatus.occupied, TableStatus.reserved]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete table that is currently occupied or reserved"
        )
    
    table = table_crud.delete(db, id=table_id)
    return table