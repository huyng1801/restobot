from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date

from app.core.database import get_db
from app.crud.table import table as table_crud
from app.crud.order import reservation as reservation_crud
from app.schemas.table import Table, TableCreate, TableUpdate, TableStatusUpdate
from app.schemas.order import ReservationCreate, ReservationWithDetails
from app.models.table import TableStatus
from app.api.deps import get_current_staff_user, get_current_user_optional
from app.core.business_hours import BusinessHours
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


class AvailabilityResponse(BaseModel):
    available: bool
    suggested_times: Optional[List[str]] = None
    available_tables: List[Table]


@router.get("/check-availability", response_model=AvailabilityResponse)
def check_table_availability(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    time: str = Query(..., description="Time in HH:MM format"), 
    guests: int = Query(..., description="Number of guests"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Check table availability for given date, time and number of guests.
    """
    try:
        # Parse date and time
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        time_obj = datetime.strptime(time, "%H:%M").time()
        reservation_datetime = datetime.combine(date_obj, time_obj)
        
        # Basic validation - check business hours only (skip advance booking rule for availability check)
        weekday = reservation_datetime.weekday()
        check_time = reservation_datetime.time()
        
        # Check if within business hours
        from app.core.business_hours import BusinessHours
        business_hours = BusinessHours.BUSINESS_HOURS.get(weekday, [])
        is_within_hours = False
        
        for start_time, end_time in business_hours:
            if start_time <= check_time <= end_time:
                is_within_hours = True
                break
        
        if not is_within_hours:
            suggested_times = ["10:00", "11:00", "12:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
            return AvailabilityResponse(
                available=False,
                suggested_times=suggested_times,
                available_tables=[]
            )
        
        # Check lunch break
        lunch_break = BusinessHours.LUNCH_BREAK.get(weekday)
        if lunch_break:
            break_start, break_end = lunch_break
            if break_start <= check_time <= break_end:
                suggested_times = ["10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30", 
                                 "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00", "21:30"]
                return AvailabilityResponse(
                    available=False,
                    suggested_times=suggested_times,
                    available_tables=[]
                )
        
        # Get available tables for the requested time
        available_tables = table_crud.get_available_tables(
            db, 
            min_capacity=guests,
            reservation_datetime=reservation_datetime,
            duration_hours=2
        )
        
        # If no tables available, suggest alternative times
        suggested_times = []
        if not available_tables:
            # Check availability for nearby time slots
            for offset_hours in [1, -1, 2, -2]:
                alt_datetime = reservation_datetime + timedelta(hours=offset_hours)
                is_valid_alt, _ = BusinessHours.validate_reservation_time(alt_datetime)
                if is_valid_alt:
                    alt_tables = table_crud.get_available_tables(
                        db, 
                        min_capacity=guests,
                        reservation_datetime=alt_datetime,
                        duration_hours=2
                    )
                    if alt_tables:
                        suggested_times.append(alt_datetime.strftime("%H:%M"))
                        if len(suggested_times) >= 4:  # Limit suggestions
                            break
        
        return AvailabilityResponse(
            available=bool(available_tables),
            suggested_times=suggested_times,
            available_tables=available_tables
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")


@router.post("/book", response_model=ReservationWithDetails)
def book_table(
    *,
    db: Session = Depends(get_db),
    reservation_in: ReservationCreate,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Book a table for a customer.
    """
    # If user is authenticated, use their ID
    if current_user:
        reservation_in.customer_id = current_user.id
    
    # Validate business hours
    is_valid, error_message = BusinessHours.validate_reservation_time(reservation_in.reservation_date)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Check if table exists and has sufficient capacity
    if reservation_in.table_id:
        table = table_crud.get(db, id=reservation_in.table_id)
        if not table:
            raise HTTPException(status_code=400, detail="Table not found")
        
        if table.capacity < reservation_in.party_size:
            raise HTTPException(
                status_code=400, 
                detail=f"Table capacity ({table.capacity}) is insufficient for party size ({reservation_in.party_size})"
            )
    else:
        # Auto-assign available table
        available_tables = table_crud.get_available_tables(
            db, 
            min_capacity=reservation_in.party_size,
            reservation_datetime=reservation_in.reservation_date,
            duration_hours=2
        )
        
        if not available_tables:
            raise HTTPException(
                status_code=409, 
                detail="No available tables for the requested time and party size"
            )
        
        # Assign the best fitting table (smallest capacity that fits)
        best_table = min(available_tables, key=lambda t: t.capacity)
        reservation_in.table_id = best_table.id
    
    # Check for conflicting reservations
    start_time = reservation_in.reservation_date
    end_time = datetime.combine(
        start_time.date(), 
        (datetime.combine(date.today(), start_time.time()) + timedelta(hours=2)).time()
    )
    
    conflicting_reservations = reservation_crud.get_by_date_range(
        db, start_date=start_time, end_date=end_time, table_id=reservation_in.table_id
    )
    
    if conflicting_reservations:
        raise HTTPException(
            status_code=409,
            detail="Table is already reserved for this time slot"
        )
    
    # Create reservation
    reservation = reservation_crud.create(db, obj_in=reservation_in)
    
    # Get full details for the created reservation
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation.id)
    
    return reservation_details


@router.post("/{table_id}/check-in", response_model=Table)
def customer_check_in(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    order_id: Optional[int] = None,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Mark customer check-in at table (updates status to occupied)
    """
    from app.services.table_status_manager import create_table_status_manager
    
    # Verify table exists
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Update table status for arrival
    status_manager = create_table_status_manager(db)
    updated_table = status_manager.update_table_status_for_arrival(table_id, order_id)
    
    if not updated_table:
        raise HTTPException(
            status_code=400, 
            detail="Cannot check in to this table - no valid reservation or order found"
        )
    
    return updated_table


@router.post("/{table_id}/check-out", response_model=Table)
def customer_check_out(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Mark customer check-out from table (updates status to cleaning)
    Staff+ only endpoint
    """
    from app.services.table_status_manager import create_table_status_manager
    
    # Verify table exists
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Update table status for departure
    status_manager = create_table_status_manager(db)
    updated_table = status_manager.update_table_status_for_departure(table_id)
    
    return updated_table


@router.post("/{table_id}/cleaning-complete", response_model=Table)
def complete_table_cleaning(
    *,
    db: Session = Depends(get_db),
    table_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Mark table cleaning as complete (Staff+ only)
    """
    from app.services.table_status_manager import create_table_status_manager
    
    # Verify table exists
    table = table_crud.get(db, id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if table.status != TableStatus.cleaning:
        raise HTTPException(
            status_code=400, 
            detail="Table is not in cleaning status"
        )
    
    # Complete cleaning and update status
    status_manager = create_table_status_manager(db)
    updated_table = status_manager.complete_table_cleaning(table_id)
    
    return updated_table


@router.post("/sync-statuses", response_model=List[Table])
def sync_all_table_statuses(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Sync all table statuses with current reservations and orders (Staff+ only)
    Useful for fixing inconsistent states
    """
    from app.services.table_status_manager import create_table_status_manager
    
    status_manager = create_table_status_manager(db)
    updated_tables = status_manager.sync_all_table_statuses()
    
    return updated_tables


@router.get("/status-summary")
def get_table_status_summary(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Get table status summary for dashboard
    """
    from app.services.table_status_manager import create_table_status_manager
    
    status_manager = create_table_status_manager(db)
    summary = status_manager.get_table_status_summary()
    
    return {
        "status_summary": summary,
        "timestamp": datetime.utcnow().isoformat()
    }