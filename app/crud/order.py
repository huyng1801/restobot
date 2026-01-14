from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, date
from app.models.order import Order, OrderItem, Reservation, OrderStatus, PaymentStatus, ReservationStatus
from app.models.menu import MenuItem
from app.models.user import User, UserRole
from app.models.table import Table, TableStatus
from app.schemas.order import (
    OrderCreate, OrderUpdate, 
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
            query = query.filter(func.date(Reservation.reservation_datetime) == date_filter)
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
                Reservation.reservation_datetime >= start_date,
                Reservation.reservation_datetime <= end_date,
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
            reservation_datetime=obj_in.reservation_date,
            party_size=obj_in.party_size,
            special_requests=obj_in.special_requests,
            notes=obj_in.notes,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update table status after creating reservation
        self._update_table_status_for_reservation(db, db_obj.id)
        
        return db_obj
        
    def update(
        self, db: Session, db_obj: Reservation, obj_in: ReservationUpdate
    ) -> Reservation:
        update_data = obj_in.dict(exclude_unset=True)
        # Map reservation_date to reservation_datetime for database field
        if 'reservation_date' in update_data:
            update_data['reservation_datetime'] = update_data.pop('reservation_date')
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # Update table status after updating reservation
        self._update_table_status_for_reservation(db, db_obj.id)
        
        return db_obj
        
    def _update_table_status_for_reservation(self, db: Session, reservation_id: int) -> None:
        """Helper method to update table status when reservation changes"""
        try:
            from app.services.table_status_manager import create_table_status_manager
            status_manager = create_table_status_manager(db)
            status_manager.update_table_status_for_reservation(reservation_id)
        except Exception as e:
            # Log error but don't fail the main operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update table status for reservation {reservation_id}: {e}")
    def get_multi_with_details(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ReservationStatus] = None,
        date_filter: Optional[date] = None
    ) -> List[dict]:
        """Get reservations with customer and table details"""
        # Build base query with joins
        query = db.query(
            Reservation,
            User.full_name.label('customer_name'),
            User.email.label('customer_email'),
            User.phone.label('customer_phone'),
            Table.table_number.label('table_number'),
            Table.capacity.label('table_capacity'),
            Table.location.label('table_location')
        ).outerjoin(User, Reservation.customer_id == User.id)\
         .outerjoin(Table, Reservation.table_id == Table.id)
        # Apply filters
        if status:
            query = query.filter(Reservation.status == status)
        if date_filter:
            query = query.filter(func.date(Reservation.reservation_datetime) == date_filter)
        results = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
        # Convert to dict format
        reservations_with_details = []
        for reservation, customer_name, customer_email, customer_phone, table_number, table_capacity, table_location in results:
            reservation_dict = {
                "id": reservation.id,
                "customer_id": reservation.customer_id,
                "table_id": reservation.table_id,
                "reservation_date": reservation.reservation_datetime,  # Map DB field to API field
                "party_size": reservation.party_size,
                "status": reservation.status,
                "special_requests": reservation.special_requests,
                "notes": reservation.notes,
                "created_at": reservation.created_at,
                "updated_at": reservation.updated_at,
                # Customer details
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                # Table details
                "table_number": table_number,
                "table_capacity": table_capacity,
                "table_location": table_location
            }
            reservations_with_details.append(reservation_dict)
        return reservations_with_details
    def get_count_with_details(
        self, 
        db: Session, 
        status: Optional[ReservationStatus] = None,
        date_filter: Optional[date] = None
    ) -> int:
        """Get count of reservations with filters applied"""
        query = db.query(Reservation)\
            .outerjoin(User, Reservation.customer_id == User.id)\
            .outerjoin(Table, Reservation.table_id == Table.id)
        # Apply same filters as get_multi_with_details
        if status:
            query = query.filter(Reservation.status == status)
        if date_filter:
            query = query.filter(func.date(Reservation.reservation_datetime) == date_filter)
        return query.count()
    def get_my_reservations_with_details(
        self, 
        db: Session, 
        customer_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[dict]:
        """Get user's reservations with customer and table details"""
        # Build base query with joins and filter by customer
        query = db.query(
            Reservation,
            User.full_name.label('customer_name'),
            User.email.label('customer_email'),
            User.phone.label('customer_phone'),
            Table.table_number.label('table_number'),
            Table.capacity.label('table_capacity'),
            Table.location.label('table_location')
        ).outerjoin(User, Reservation.customer_id == User.id)\
         .outerjoin(Table, Reservation.table_id == Table.id)\
         .filter(Reservation.customer_id == customer_id)
        results = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
        # Convert to dict format
        reservations_with_details = []
        for reservation, customer_name, customer_email, customer_phone, table_number, table_capacity, table_location in results:
            reservation_dict = {
                "id": reservation.id,
                "customer_id": reservation.customer_id,
                "table_id": reservation.table_id,
                "reservation_date": reservation.reservation_datetime,  # Map DB field to API field
                "party_size": reservation.party_size,
                "status": reservation.status,
                "special_requests": reservation.special_requests,
                "notes": reservation.notes,
                "created_at": reservation.created_at,
                "updated_at": reservation.updated_at,
                # Customer details
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                # Table details
                "table_number": table_number,
                "table_capacity": table_capacity,
                "table_location": table_location
            }
            reservations_with_details.append(reservation_dict)
        return reservations_with_details
    def get_with_details(self, db: Session, reservation_id: int) -> Optional[dict]:
        """Get single reservation with full details"""
        # Get reservation with customer and table info
        result = db.query(
            Reservation,
            User.full_name.label('customer_name'),
            User.email.label('customer_email'),
            User.phone.label('customer_phone'),
            Table.table_number.label('table_number'),
            Table.capacity.label('table_capacity'),
            Table.location.label('table_location')
        ).outerjoin(User, Reservation.customer_id == User.id)\
         .outerjoin(Table, Reservation.table_id == Table.id)\
         .filter(Reservation.id == reservation_id).first()
        if not result:
            return None
        reservation, customer_name, customer_email, customer_phone, table_number, table_capacity, table_location = result
        return {
            "id": reservation.id,
            "customer_id": reservation.customer_id,
            "table_id": reservation.table_id,
            "reservation_date": reservation.reservation_datetime,  # Map DB field to API field
            "party_size": reservation.party_size,
            "status": reservation.status,
            "special_requests": reservation.special_requests,
            "notes": reservation.notes,
            "created_at": reservation.created_at,
            "updated_at": reservation.updated_at,
            # Customer details
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            # Table details
            "table_number": table_number,
            "table_capacity": table_capacity,
            "table_location": table_location
        }
    def delete(self, db: Session, id: int) -> Reservation:
        obj = db.query(Reservation).get(id)
        db.delete(obj)
        db.commit()
        return obj
class CRUDOrder:
    def get(self, db: Session, id: int) -> Optional[Order]:
        from sqlalchemy.orm import joinedload
        return db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(Order.id == id).first()
    def update_order_total(self, db: Session, order_id: int) -> Optional[Order]:
        """Update order total amount based on order items"""
        order = self.get(db, id=order_id)
        if not order:
            return None
        # Calculate total from order items
        total = db.query(func.sum(OrderItem.subtotal)).filter(OrderItem.order_id == order_id).scalar() or 0
        order.total_amount = total
        db.commit()
        db.refresh(order)
        return order
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
    def get_multi_with_details(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        customer_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        date_filter: Optional[date] = None,
        search: Optional[str] = None
    ) -> List[dict]:
        """Get orders with customer and table details"""
        # Build base query with joins
        query = db.query(
            Order,
            User.full_name.label('customer_name'),
            User.email.label('customer_email'),
            Table.table_number.label('table_number')
        ).outerjoin(User, Order.customer_id == User.id)\
         .outerjoin(Table, Order.table_id == Table.id)
        # Apply filters
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if status:
            query = query.filter(Order.status == status)
        if date_filter:
            query = query.filter(func.date(Order.created_at) == date_filter)
        if search:
            query = query.filter(
                Order.order_number.ilike(f"%{search}%") |
                User.full_name.ilike(f"%{search}%") |
                User.email.ilike(f"%{search}%") |
                Table.table_number.ilike(f"%{search}%")
            )
        results = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        # Convert to dict format
        orders_with_details = []
        for order, customer_name, customer_email, table_number in results:
            order_dict = {
                "id": order.id,
                "order_number": order.order_number,
                "customer_id": order.customer_id,
                "table_id": order.table_id,
                "status": order.status,
                "payment_status": order.payment_status,
                "total_amount": order.total_amount,
                "tax_amount": order.tax_amount,
                "discount_amount": order.discount_amount,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "table_number": table_number,
                "order_items": []  # Will be populated separately if needed
            }
            orders_with_details.append(order_dict)
        return orders_with_details
    def get_count_with_details(
        self, 
        db: Session, 
        customer_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        date_filter: Optional[date] = None,
        search: Optional[str] = None
    ) -> int:
        """Get count of orders with filters applied"""
        # Build base query with joins
        query = db.query(Order)\
            .outerjoin(User, Order.customer_id == User.id)\
            .outerjoin(Table, Order.table_id == Table.id)
        # Apply same filters as get_multi_with_details
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        if status:
            query = query.filter(Order.status == status)
        if date_filter:
            query = query.filter(func.date(Order.created_at) == date_filter)
        if search:
            query = query.filter(
                Order.order_number.ilike(f"%{search}%") |
                User.full_name.ilike(f"%{search}%") |
                User.email.ilike(f"%{search}%") |
                Table.table_number.ilike(f"%{search}%")
            )
        return query.count()
    def create(self, db: Session, obj_in: OrderCreate) -> Order:
        # Generate unique order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        print(f"🔍 Debug CRUD: Creating order with customer_id={obj_in.customer_id}, table_id={obj_in.table_id}")
        print(f"🔍 Debug CRUD: Order items count: {len(obj_in.order_items)}")
        db_obj = Order(
            order_number=order_number,
            customer_id=obj_in.customer_id,
            table_id=obj_in.table_id,
            notes=obj_in.notes,
        )
        db.add(db_obj)
        db.flush()  # To get the order ID
        print(f"✅ Order flushed with ID: {db_obj.id}")
        # Add order items
        total_amount = 0.0
        for i, item in enumerate(obj_in.order_items):
            # Handle both dict and object formats
            menu_item_id = item.get('menu_item_id') if isinstance(item, dict) else item.menu_item_id
            quantity = item.get('quantity') if isinstance(item, dict) else item.quantity
            special_instructions = item.get('special_instructions', '') if isinstance(item, dict) else (item.special_instructions or '')
            print(f"🔍 Debug CRUD: Processing item {i+1}: menu_item_id={menu_item_id}, quantity={quantity}")
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                db.rollback()
                raise ValueError(f"Menu item {menu_item_id} not found in database")
            print(f"✅ Found menu item: {menu_item.name} (price: {menu_item.price})")
            item_total = menu_item.price * quantity
            total_amount += item_total
            order_item = OrderItem(
                order_id=db_obj.id,
                menu_item_id=menu_item_id,
                quantity=quantity,
                unit_price=menu_item.price,
                total_price=item_total,
                special_instructions=special_instructions,
            )
            db.add(order_item)
            print(f"✅ Order item added: {menu_item.name} x{quantity} = {item_total}")
        # Calculate tax (10% for example)
        tax_amount = total_amount * 0.1
        db_obj.total_amount = total_amount
        db_obj.tax_amount = tax_amount
        print(f"🔍 Debug CRUD: Total amount={total_amount}, tax={tax_amount}")
        db.commit()
        db.refresh(db_obj)
        print(f"✅ Order committed: {order_number}")
        return db_obj
    def update(self, db: Session, db_obj: Order, obj_in: OrderUpdate) -> Order:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        # Automatically set payment_status to "paid" when order status is "completed"
        if update_data.get("status") == OrderStatus.completed:
            db_obj.payment_status = PaymentStatus.paid
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def delete(self, db: Session, id: int) -> Order:
        obj = db.query(Order).get(id)
        db.delete(obj)
        db.commit()
        return obj
    def get_with_details(self, db: Session, order_id: int) -> Optional[dict]:
        """Get single order with full details including order items"""
        # Get order with customer and table info
        result = db.query(
            Order,
            User.full_name.label('customer_name'),
            User.email.label('customer_email'),
            Table.table_number.label('table_number')
        ).outerjoin(User, Order.customer_id == User.id)\
         .outerjoin(Table, Order.table_id == Table.id)\
         .filter(Order.id == order_id).first()
        if not result:
            return None
        order, customer_name, customer_email, table_number = result
        # Get order items with menu item details
        order_items = db.query(
            OrderItem,
            MenuItem.name.label('item_name'),
            MenuItem.price.label('item_price'),
            MenuItem.image_url.label('item_image')
        ).join(MenuItem, OrderItem.menu_item_id == MenuItem.id)\
         .filter(OrderItem.order_id == order_id).all()
        items_data = []
        for order_item, item_name, item_price, item_image in order_items:
            items_data.append({
                "id": order_item.id,
                "menu_item_id": order_item.menu_item_id,
                "quantity": order_item.quantity,
                "unit_price": order_item.unit_price,
                "total_price": order_item.total_price,
                "special_instructions": order_item.special_instructions,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image
            })
        return {
            "id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "table_id": order.table_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": order.total_amount,
            "tax_amount": order.tax_amount,
            "discount_amount": order.discount_amount,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "table_number": table_number,
            "order_items": items_data
        }
    def get_dashboard_stats(self, db: Session) -> dict:
        """Get comprehensive dashboard statistics"""
        today = date.today()
        # Order statistics
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.pending).count()
        completed_orders = db.query(Order).filter(Order.status == OrderStatus.completed).count()
        # Revenue (completed orders only)
        revenue_result = db.query(func.sum(Order.total_amount)).filter(
            Order.status == OrderStatus.completed,
            func.date(Order.created_at) == today
        ).scalar()
        total_revenue = float(revenue_result) if revenue_result else 0.0
        # Table statistics
        total_tables = db.query(Table).count()
        available_tables = db.query(Table).filter(Table.status == TableStatus.available).count()
        occupied_tables = db.query(Table).filter(Table.status == TableStatus.occupied).count()
        reserved_tables = db.query(Table).filter(Table.status == TableStatus.reserved).count()
        # User statistics
        total_customers = db.query(User).filter(User.role == UserRole.customer).count()
        total_staff = db.query(User).filter(User.role.in_([UserRole.staff, UserRole.manager, UserRole.admin])).count()
        # Menu statistics
        total_menu_items = db.query(MenuItem).count()
        available_menu_items = db.query(MenuItem).filter(MenuItem.is_available == True).count()
        # Reservation statistics
        total_reservations = db.query(Reservation).count()
        pending_reservations = db.query(Reservation).filter(Reservation.status == ReservationStatus.pending).count()
        confirmed_reservations = db.query(Reservation).filter(Reservation.status == ReservationStatus.confirmed).count()
        # Recent orders (last 5)
        recent_orders = db.query(
            Order.id,
            Order.order_number,
            Order.status,
            Order.total_amount,
            Order.created_at,
            User.full_name.label('customer_name'),
            Table.table_number.label('table_number')
        ).outerjoin(User, Order.customer_id == User.id)\
         .outerjoin(Table, Order.table_id == Table.id)\
         .order_by(Order.created_at.desc())\
         .limit(5).all()
        recent_orders_data = []
        for order_data in recent_orders:
            recent_orders_data.append({
                'id': order_data.id,
                'order_number': order_data.order_number,
                'status': order_data.status,
                'total_amount': float(order_data.total_amount),
                'created_at': order_data.created_at.isoformat(),
                'customer_name': order_data.customer_name or 'Khách vãng lai',
                'table_number': order_data.table_number or 'N/A'
            })
        # Recent reservations (last 5)
        recent_reservations = db.query(
            Reservation.id,
            Reservation.reservation_datetimetime,
            Reservation.party_size,
            Reservation.status,
            User.full_name.label('customer_name'),
            Table.table_number.label('table_number')
        ).join(User, Reservation.customer_id == User.id)\
         .join(Table, Reservation.table_id == Table.id)\
         .order_by(Reservation.created_at.desc())\
         .limit(5).all()
        recent_reservations_data = []
        for res_data in recent_reservations:
            recent_reservations_data.append({
                'id': res_data.id,
                'reservation_datetime': res_data.reservation_datetimetime.isoformat(),
                'party_size': res_data.party_size,
                'status': res_data.status,
                'customer_name': res_data.customer_name,
                'table_number': res_data.table_number
            })
        # Popular menu items (most ordered)
        popular_items = db.query(
            MenuItem.id,
            MenuItem.name,
            MenuItem.price,
            func.sum(OrderItem.quantity).label('total_ordered')
        ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
         .group_by(MenuItem.id, MenuItem.name, MenuItem.price)\
         .order_by(func.sum(OrderItem.quantity).desc())\
         .limit(5).all()
        popular_items_data = []
        for item_data in popular_items:
            popular_items_data.append({
                'id': item_data.id,
                'name': item_data.name,
                'price': float(item_data.price),
                'total_ordered': item_data.total_ordered
            })
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'total_revenue': total_revenue,
            'total_tables': total_tables,
            'available_tables': available_tables,
            'occupied_tables': occupied_tables,
            'reserved_tables': reserved_tables,
            'total_customers': total_customers,
            'total_staff': total_staff,
            'total_menu_items': total_menu_items,
            'available_menu_items': available_menu_items,
            'total_reservations': total_reservations,
            'pending_reservations': pending_reservations,
            'confirmed_reservations': confirmed_reservations,
            'recent_orders': recent_orders_data,
            'recent_reservations': recent_reservations_data,
            'popular_items': popular_items_data
        }
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
