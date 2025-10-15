from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, date
from app.models.order import Order, OrderItem, Reservation, OrderStatus, PaymentStatus, ReservationStatus
from app.models.menu import MenuItem
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderItemCreate, 
    ReservationCreate, ReservationUpdate, OrderSummary
)
import uuid


class CRUDReservation:
    def get(self, db: Session, id: int) -> Optional[Reservation]:
        return db.query(Reservation).filter(Reservation.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[ReservationStatus] = None,
        date_filter: Optional[date] = None
    ) -> List[Reservation]:
        query = db.query(Reservation)
        if customer_id:
            query = query.filter(Reservation.customer_id == customer_id)
        if status:
            query = query.filter(Reservation.status == status)
        if date_filter:
            query = query.filter(func.date(Reservation.reservation_date) == date_filter)
        return query.offset(skip).limit(limit).all()

    def get_by_date_range(
        self, 
        db: Session, 
        start_date: datetime, 
        end_date: datetime,
        table_id: Optional[int] = None
    ) -> List[Reservation]:
        query = db.query(Reservation).filter(
            and_(
                Reservation.reservation_date >= start_date,
                Reservation.reservation_date <= end_date,
                Reservation.status.in_([ReservationStatus.confirmed, ReservationStatus.pending])
            )
        )
        if table_id:
            query = query.filter(Reservation.table_id == table_id)
        return query.all()

    def create(self, db: Session, obj_in: ReservationCreate) -> Reservation:
        db_obj = Reservation(
            customer_id=obj_in.customer_id,
            table_id=obj_in.table_id,
            reservation_date=obj_in.reservation_date,
            party_size=obj_in.party_size,
            special_requests=obj_in.special_requests,
            notes=obj_in.notes,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: Reservation, obj_in: ReservationUpdate
    ) -> Reservation:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Reservation:
        obj = db.query(Reservation).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDOrder:
    def get(self, db: Session, id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == id).first()

    def get_by_order_number(self, db: Session, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        date_filter: Optional[date] = None
    ) -> List[Order]:
        query = db.query(Order)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if status:
            query = query.filter(Order.status == status)
        if date_filter:
            query = query.filter(func.date(Order.created_at) == date_filter)
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: OrderCreate) -> Order:
        # Generate unique order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        db_obj = Order(
            order_number=order_number,
            customer_id=obj_in.customer_id,
            table_id=obj_in.table_id,
            notes=obj_in.notes,
        )
        db.add(db_obj)
        db.flush()  # To get the order ID

        # Add order items
        total_amount = 0.0
        for item in obj_in.order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                item_total = menu_item.price * item.quantity
                total_amount += item_total
                
                order_item = OrderItem(
                    order_id=db_obj.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    unit_price=menu_item.price,
                    total_price=item_total,
                    special_instructions=item.special_instructions,
                )
                db.add(order_item)

        # Calculate tax (10% for example)
        tax_amount = total_amount * 0.1
        db_obj.total_amount = total_amount
        db_obj.tax_amount = tax_amount

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Order, obj_in: OrderUpdate) -> Order:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Order:
        obj = db.query(Order).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def get_daily_summary(self, db: Session, target_date: Optional[date] = None) -> OrderSummary:
        if not target_date:
            target_date = date.today()

        # Get orders for the specific date
        orders = db.query(Order).filter(func.date(Order.created_at) == target_date).all()
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.status == OrderStatus.pending])
        completed_orders = len([o for o in orders if o.status == OrderStatus.completed])
        total_revenue = sum([o.total_amount for o in orders if o.payment_status == PaymentStatus.paid])

        return OrderSummary(
            total_orders=total_orders,
            pending_orders=pending_orders,
            completed_orders=completed_orders,
            total_revenue=total_revenue
        )


class CRUDOrderItem:
    def get(self, db: Session, id: int) -> Optional[OrderItem]:
        return db.query(OrderItem).filter(OrderItem.id == id).first()

    def get_by_order(self, db: Session, order_id: int) -> List[OrderItem]:
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def delete(self, db: Session, id: int) -> OrderItem:
        obj = db.query(OrderItem).get(id)
        db.delete(obj)
        db.commit()
        return obj


reservation = CRUDReservation()
order = CRUDOrder()
order_item = CRUDOrderItem()