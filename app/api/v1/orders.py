from typing import Any, List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.crud.order import order as order_crud, reservation as reservation_crud
from app.schemas.order import (
    Order, OrderCreate, OrderUpdate, OrderWithDetails,
    Reservation, ReservationCreate, ReservationUpdate, ReservationWithDetails,
    OrderSummary, DashboardStats, PaginatedReservationResponse, PaginatedOrderResponse
)
from app.models.order import OrderStatus, PaymentStatus, ReservationStatus
from app.api.deps import get_current_user, get_current_staff_user, get_current_user_optional

router = APIRouter()


# Reservation endpoints
@router.get("/reservations/", response_model=PaginatedReservationResponse)
def read_reservations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[ReservationStatus] = Query(None, description="Filter by status"),
    date_filter: Optional[date] = Query(None, description="Filter by date"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Retrieve reservations with pagination and optional filtering.
    """
    # Get total count with filters applied
    total = reservation_crud.get_count_with_details(
        db, status=status, date_filter=date_filter
    )
    
    # Get reservations with pagination
    reservations = reservation_crud.get_multi_with_details(
        db, skip=skip, limit=limit, 
        status=status, 
        date_filter=date_filter
    )
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit if limit > 0 else 1
    page = skip // limit if limit > 0 else 0
    
    return PaginatedReservationResponse(
        items=reservations,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/reservations/my", response_model=List[ReservationWithDetails])
def read_my_reservations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve current user's reservations with table details.
    """
    reservations = reservation_crud.get_my_reservations_with_details(
        db, customer_id=current_user.id, skip=skip, limit=limit
    )
    
    return reservations


@router.post("/reservations/", response_model=ReservationWithDetails)
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
    
    # Get full details for the created reservation
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation.id)
    
    return reservation_details


@router.get("/reservations/{reservation_id}", response_model=ReservationWithDetails)
def read_reservation(
    *,
    db: Session = Depends(get_db),
    reservation_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get reservation by ID with customer and table details.
    """
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation_id)
    if not reservation_details:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Users can only see their own reservations unless they are staff+
    from app.models.user import UserRole
    if (current_user.role == UserRole.customer and 
        reservation_details["customer_id"] != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return reservation_details


@router.put("/reservations/{reservation_id}", response_model=ReservationWithDetails)
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
    
    # Get full details for the updated reservation
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation.id)
    
    return reservation_details


@router.delete("/reservations/{reservation_id}", response_model=ReservationWithDetails)
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
    
    # Get full details for the cancelled reservation
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation.id)
    
    return reservation_details


@router.patch("/reservations/{reservation_id}/status", response_model=ReservationWithDetails)
def update_reservation_status(
    *,
    db: Session = Depends(get_db),
    reservation_id: int,
    status_data: dict,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update reservation status (Staff+ only).
    """
    from app.schemas.order import ReservationUpdate
    
    reservation = reservation_crud.get(db, id=reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    status = status_data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    reservation_update = ReservationUpdate(status=status)
    reservation = reservation_crud.update(db, db_obj=reservation, obj_in=reservation_update)
    
    # Get full details for the updated reservation
    reservation_details = reservation_crud.get_with_details(db, reservation_id=reservation.id)
    
    return reservation_details


# Order endpoints
@router.get("/orders/", response_model=PaginatedOrderResponse)
def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    date_filter: Optional[date] = Query(None, description="Filter by date"),
    search: Optional[str] = Query(None, description="Search by order number, customer name, or table number"),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Retrieve orders with pagination and customer/table details (Staff+ only).
    """
    # Get total count with filters applied
    total = order_crud.get_count_with_details(
        db, status=status, date_filter=date_filter, search=search
    )
    
    # Get orders with pagination
    orders = order_crud.get_multi_with_details(
        db, skip=skip, limit=limit, 
        status=status, 
        date_filter=date_filter,
        search=search
    )
    
    return PaginatedOrderResponse(
        items=orders,
        total=total,
        skip=skip,
        limit=limit
    )


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


@router.get("/orders/{order_id}/details")
def read_order_details(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get order details with customer, table, and menu items (Staff+ only).
    """
    order_details = order_crud.get_with_details(db, order_id=order_id)
    if not order_details:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order_details


@router.patch("/orders/{order_id}/status", response_model=Order)
def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status_data: dict,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update order status (Staff+ only).
    """
    from app.schemas.order import OrderUpdate
    
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    status = status_data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    order_update = OrderUpdate(status=status)
    order = order_crud.update(db, db_obj=order, obj_in=order_update)
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


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Get comprehensive dashboard statistics (Staff+ only).
    """
    stats = order_crud.get_dashboard_stats(db)
    return stats


@router.get("/analytics/bestsellers")
def get_bestseller_dishes(
    *,
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Number of bestseller dishes to return"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Get bestseller dishes based on order quantity in the specified period.
    """
    from app.models.order import OrderItem, Order as OrderModel
    from app.models.menu import MenuItem
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Query to get bestsellers
    bestsellers = (
        db.query(
            OrderItem.menu_item_id,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.count(OrderItem.id).label('order_count')
        )
        .join(OrderModel, OrderItem.order_id == OrderModel.id)
        .filter(
            OrderModel.created_at >= start_date,
            OrderModel.created_at <= end_date,
            OrderModel.status.in_([OrderStatus.COMPLETED, OrderStatus.PREPARING, OrderStatus.READY])
        )
        .group_by(OrderItem.menu_item_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )
    
    # Format response
    result = []
    for item in bestsellers:
        result.append({
            "menu_item_id": item.menu_item_id,
            "total_quantity": item.total_quantity,
            "order_count": item.order_count
        })
    
    return result


@router.post("/orders/{order_id}/items/")
def add_item_to_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    item_data: dict,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Add item to existing order.
    """
    from app.models.order import OrderItem
    from app.crud.menu import menu_item as menu_item_crud
    
    # Get order
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Users can only modify their own orders unless they are staff+
    from app.models.user import UserRole
    if (current_user and current_user.role == UserRole.customer and 
        order.customer_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Validate menu item
    menu_item_id = item_data.get("menu_item_id")
    quantity = item_data.get("quantity", 1)
    special_instructions = item_data.get("special_instructions", "")
    
    menu_item = menu_item_crud.get(db, id=menu_item_id)
    if not menu_item:
        raise HTTPException(status_code=400, detail="Menu item not found")
    if not menu_item.is_available:
        raise HTTPException(status_code=400, detail=f"Menu item '{menu_item.name}' is not available")
    
    # Check if item already exists in order
    existing_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.menu_item_id == menu_item_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        existing_item.subtotal = existing_item.quantity * existing_item.unit_price
        db.commit()
        db.refresh(existing_item)
        return {"message": "Item quantity updated", "item_id": existing_item.id}
    else:
        # Create new order item
        new_item = OrderItem(
            order_id=order_id,
            menu_item_id=menu_item_id,
            quantity=quantity,
            unit_price=menu_item.price,
            subtotal=menu_item.price * quantity,
            special_instructions=special_instructions
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        # Update order total
        order_crud.update_order_total(db, order_id=order_id)
        
        return {"message": "Item added successfully", "item_id": new_item.id}