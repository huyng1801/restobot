from typing import Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.order import order as order_crud, reservation as reservation_crud
from app.schemas.order import (
    Order, OrderCreate, OrderUpdate,
    Reservation, ReservationCreate, ReservationUpdate,
    OrderSummary
)
from app.models.order import OrderStatus, PaymentStatus, ReservationStatus
from app.api.deps import get_current_user, get_current_staff_user, get_current_user_optional

router = APIRouter()


# Reservation endpoints
@router.get("/reservations/", response_model=List[Reservation])
def read_reservations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ReservationStatus] = Query(None, description="Filter by status"),
    date_filter: Optional[date] = Query(None, description="Filter by date"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Retrieve reservations (Staff+ only).
    """
    reservations = reservation_crud.get_multi(
        db, skip=skip, limit=limit, 
        status=status, 
        date_filter=date_filter
    )
    return reservations


@router.get("/reservations/my", response_model=List[Reservation])
def read_my_reservations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve current user's reservations.
    """
    reservations = reservation_crud.get_multi(
        db, skip=skip, limit=limit, 
        customer_id=current_user.id
    )
    return reservations


@router.post("/reservations/", response_model=Reservation)
def create_reservation(
    *,
    db: Session = Depends(get_db),
    reservation_in: ReservationCreate,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Create new reservation.
    """
    # If user is authenticated, use their ID
    if current_user:
        reservation_in.customer_id = current_user.id
    
    # Check if table exists and has sufficient capacity
    from app.crud.table import table as table_crud
    table = table_crud.get(db, id=reservation_in.table_id)
    if not table:
        raise HTTPException(status_code=400, detail="Table not found")
    
    if table.capacity < reservation_in.party_size:
        raise HTTPException(
            status_code=400, 
            detail=f"Table capacity ({table.capacity}) is insufficient for party size ({reservation_in.party_size})"
        )
    
    # Check for conflicting reservations (same table, overlapping time)
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
            status_code=400,
            detail="Table is already reserved for this time slot"
        )
    
    reservation = reservation_crud.create(db, obj_in=reservation_in)
    return reservation


@router.get("/reservations/{reservation_id}", response_model=Reservation)
def read_reservation(
    *,
    db: Session = Depends(get_db),
    reservation_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get reservation by ID.
    """
    reservation = reservation_crud.get(db, id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Users can only see their own reservations unless they are staff+
    from app.models.user import UserRole
    if (current_user.role == UserRole.customer and 
        reservation.customer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return reservation


@router.put("/reservations/{reservation_id}", response_model=Reservation)
def update_reservation(
    *,
    db: Session = Depends(get_db),
    reservation_id: int,
    reservation_in: ReservationUpdate,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Update reservation.
    """
    reservation = reservation_crud.get(db, id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Users can only modify their own reservations unless they are staff+
    from app.models.user import UserRole
    if (current_user.role == UserRole.customer and 
        reservation.customer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Customers cannot change status, only staff can
    if (current_user.role == UserRole.customer and 
        hasattr(reservation_in, 'status') and reservation_in.status is not None):
        reservation_in.status = None
    
    reservation = reservation_crud.update(db, db_obj=reservation, obj_in=reservation_in)
    return reservation


@router.delete("/reservations/{reservation_id}", response_model=Reservation)
def cancel_reservation(
    *,
    db: Session = Depends(get_db),
    reservation_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Cancel reservation.
    """
    reservation = reservation_crud.get(db, id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Users can only cancel their own reservations unless they are staff+
    from app.models.user import UserRole
    if (current_user.role == UserRole.customer and 
        reservation.customer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update status to cancelled instead of deleting
    from app.schemas.order import ReservationUpdate
    reservation_update = ReservationUpdate(status=ReservationStatus.cancelled)
    reservation = reservation_crud.update(db, db_obj=reservation, obj_in=reservation_update)
    return reservation


# Order endpoints
@router.get("/orders/", response_model=List[Order])
def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    date_filter: Optional[date] = Query(None, description="Filter by date"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Retrieve orders (Staff+ only).
    """
    orders = order_crud.get_multi(
        db, skip=skip, limit=limit, 
        status=status, 
        date_filter=date_filter
    )
    return orders


@router.get("/orders/my", response_model=List[Order])
def read_my_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve current user's orders.
    """
    orders = order_crud.get_multi(
        db, skip=skip, limit=limit, 
        customer_id=current_user.id
    )
    return orders


@router.post("/orders/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Create new order.
    """
    # If user is authenticated, use their ID
    if current_user:
        order_in.customer_id = current_user.id
    
    # Validate that all menu items exist and are available
    from app.crud.menu import menu_item as menu_item_crud
    for item in order_in.order_items:
        menu_item = menu_item_crud.get(db, id=item.menu_item_id)
        if not menu_item:
            raise HTTPException(
                status_code=400, 
                detail=f"Menu item {item.menu_item_id} not found"
            )
        if not menu_item.is_available:
            raise HTTPException(
                status_code=400, 
                detail=f"Menu item '{menu_item.name}' is not available"
            )
    
    order = order_crud.create(db, obj_in=order_in)
    return order


@router.get("/orders/{order_id}", response_model=Order)
def read_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get order by ID.
    """
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Users can only see their own orders unless they are staff+
    from app.models.user import UserRole
    if (current_user.role == UserRole.customer and 
        order.customer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order


@router.put("/orders/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update order (Staff+ only).
    """
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = order_crud.update(db, db_obj=order, obj_in=order_in)
    return order


@router.get("/summary/daily", response_model=OrderSummary)
def get_daily_summary(
    *,
    db: Session = Depends(get_db),
    target_date: Optional[date] = Query(None, description="Date to get summary for (default: today)"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get daily order summary (Staff+ only).
    """
    summary = order_crud.get_daily_summary(db, target_date=target_date)
    return summary