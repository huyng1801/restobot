"""
Table Status Manager for RestoBot
Quản lý trạng thái bàn tự động dựa trên reservation và order
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.table import Table, TableStatus
from app.models.order import Reservation, ReservationStatus, Order, OrderStatus
from app.crud.table import table as table_crud
import logging

logger = logging.getLogger(__name__)

class TableStatusManager:
    """
    Manager để xử lý trạng thái bàn tự động
    """

    def __init__(self, db: Session):
        self.db = db

    def update_table_status_for_reservation(self, reservation_id: int) -> Optional[Table]:
        """
        Update table status khi có reservation mới hoặc thay đổi
        """
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            logger.warning(f"Reservation {reservation_id} not found")
            return None

        table = reservation.table
        if not table:
            logger.warning(f"Table for reservation {reservation_id} not found")
            return None

        # Determine new status based on reservation status
        if reservation.status == ReservationStatus.confirmed:
            new_status = TableStatus.reserved
        elif reservation.status == ReservationStatus.cancelled:
            # Check if table should go back to available or has other reservations
            new_status = self._determine_table_status_after_cancellation(table.id)
        else:
            # For pending reservations, keep current status unless it should be reserved
            current_time = datetime.utcnow()
            if (reservation.reservation_datetime <= current_time + timedelta(minutes=30) and
                reservation.reservation_datetime >= current_time - timedelta(minutes=15)):
                new_status = TableStatus.reserved
            else:
                new_status = table.status

        return self._update_table_status(table.id, new_status)

    def update_table_status_for_arrival(self, table_id: int, order_id: Optional[int] = None) -> Optional[Table]:
        """
        Update table status khi khách hàng đến và ngồi
        """
        # Check if there's an active order for this table
        if order_id:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if order and order.status in [OrderStatus.pending, OrderStatus.confirmed]:
                return self._update_table_status(table_id, TableStatus.occupied)
        
        # Check for any active reservations
        current_time = datetime.utcnow()
        active_reservation = self.db.query(Reservation).filter(
            Reservation.table_id == table_id,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reservation_datetime <= current_time + timedelta(minutes=30),
            Reservation.estimated_end_time >= current_time
        ).first()

        if active_reservation:
            return self._update_table_status(table_id, TableStatus.occupied)
        
        return None

    def update_table_status_for_departure(self, table_id: int) -> Optional[Table]:
        """
        Update table status khi khách hàng rời đi
        """
        # Mark table as cleaning first
        table = self._update_table_status(table_id, TableStatus.cleaning)
        
        # After cleaning (simulate with a few seconds), check for next reservation
        next_status = self._determine_next_table_status(table_id)
        
        return self._update_table_status(table_id, next_status)

    def complete_table_cleaning(self, table_id: int) -> Optional[Table]:
        """
        Mark table cleaning as complete and update to next appropriate status
        """
        next_status = self._determine_next_table_status(table_id)
        return self._update_table_status(table_id, next_status)

    def _determine_table_status_after_cancellation(self, table_id: int) -> TableStatus:
        """
        Determine table status after a reservation is cancelled
        """
        current_time = datetime.utcnow()
        
        # Check for other active reservations
        other_reservations = self.db.query(Reservation).filter(
            Reservation.table_id == table_id,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.estimated_end_time >= current_time
        ).count()

        if other_reservations > 0:
            return TableStatus.reserved
        
        # Check for active orders (customers currently at table)
        active_orders = self.db.query(Order).filter(
            Order.table_id == table_id,
            Order.status.in_([OrderStatus.pending, OrderStatus.confirmed, OrderStatus.ready])
        ).count()

        if active_orders > 0:
            return TableStatus.occupied
        
        return TableStatus.available

    def _determine_next_table_status(self, table_id: int) -> TableStatus:
        """
        Determine next table status based on upcoming reservations
        """
        current_time = datetime.utcnow()
        
        # Check for upcoming reservations within next 30 minutes
        upcoming_reservation = self.db.query(Reservation).filter(
            Reservation.table_id == table_id,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reservation_datetime <= current_time + timedelta(minutes=30),
            Reservation.reservation_datetime >= current_time
        ).first()

        if upcoming_reservation:
            return TableStatus.reserved
        
        return TableStatus.available

    def _update_table_status(self, table_id: int, new_status: TableStatus) -> Optional[Table]:
        """
        Internal method to update table status
        """
        table = table_crud.update_status(self.db, table_id, new_status)
        if table:
            logger.info(f"Table {table.table_number} status updated to {new_status}")
        return table

    def sync_all_table_statuses(self) -> List[Table]:
        """
        Sync all table statuses with current reservations and orders
        Useful for fixing inconsistent states
        """
        updated_tables = []
        current_time = datetime.utcnow()
        
        # Get all active tables
        all_tables = self.db.query(Table).filter(Table.is_active == True).all()
        
        for table in all_tables:
            # Determine correct status based on current state
            correct_status = self._calculate_correct_table_status(table.id, current_time)
            
            if table.status != correct_status:
                updated_table = self._update_table_status(table.id, correct_status)
                if updated_table:
                    updated_tables.append(updated_table)
        
        return updated_tables

    def _calculate_correct_table_status(self, table_id: int, current_time: datetime) -> TableStatus:
        """
        Calculate what the table status should be based on current reservations and orders
        """
        # Check for active orders (customers currently dining)
        active_orders = self.db.query(Order).filter(
            Order.table_id == table_id,
            Order.status.in_([OrderStatus.pending, OrderStatus.confirmed, OrderStatus.ready, OrderStatus.served])
        ).count()

        if active_orders > 0:
            return TableStatus.occupied
        
        # Check for active reservations
        active_reservation = self.db.query(Reservation).filter(
            Reservation.table_id == table_id,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reservation_datetime <= current_time + timedelta(minutes=30),
            Reservation.estimated_end_time >= current_time
        ).count()

        if active_reservation > 0:
            return TableStatus.reserved
        
        # Check if table is in maintenance mode (manual override)
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if table and table.status == TableStatus.maintenance:
            return TableStatus.maintenance
        
        return TableStatus.available

    def get_table_status_summary(self) -> dict:
        """
        Get summary of table statuses for dashboard
        """
        summary = {}
        for status in TableStatus:
            count = self.db.query(Table).filter(
                Table.status == status,
                Table.is_active == True
            ).count()
            summary[status.value] = count
        
        return summary


def create_table_status_manager(db: Session) -> TableStatusManager:
    """Factory function to create TableStatusManager"""
    return TableStatusManager(db)