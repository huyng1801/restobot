"""
Customer Arrival Tracking System for RestoBot
Theo dõi thời gian khách hàng đến so với reservation
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.order import Reservation, ReservationStatus
from app.models.table import Table, TableStatus
from app.services.table_status_manager import create_table_status_manager
import logging

logger = logging.getLogger(__name__)


class ArrivalStatus(str):
    """Arrival status constants"""
    EARLY = "early"
    ON_TIME = "on_time"
    LATE = "late"
    VERY_LATE = "very_late"
    NO_SHOW = "no_show"


class ArrivalRecord(BaseModel):
    """Customer arrival record"""
    reservation_id: int
    arrival_time: datetime
    reservation_time: datetime
    arrival_status: str
    minutes_difference: int
    table_id: int
    customer_name: str
    party_size: int


class CustomerArrivalTracker:
    """
    Tracker để quản lý việc khách hàng đến nhà hàng
    """

    def __init__(self, db: Session):
        self.db = db
        self.early_threshold_minutes = 15  # Arrive more than 15 min early
        self.on_time_window_minutes = 15   # Within 15 min of reservation
        self.late_threshold_minutes = 30   # More than 30 min late
        self.no_show_threshold_minutes = 60  # More than 60 min late = no-show

    def record_arrival(
        self, 
        reservation_id: int,
        actual_arrival_time: Optional[datetime] = None
    ) -> ArrivalRecord:
        """
        Record customer arrival and update reservation status
        """
        # Get reservation
        reservation = self.db.query(Reservation).filter(
            Reservation.id == reservation_id
        ).first()

        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        if reservation.status == ReservationStatus.cancelled:
            raise ValueError("Cannot record arrival for cancelled reservation")

        # Use current time if not specified
        if actual_arrival_time is None:
            actual_arrival_time = datetime.utcnow()

        # Calculate time difference
        reservation_time = reservation.reservation_datetime
        time_diff = (actual_arrival_time - reservation_time).total_seconds() / 60
        
        # Determine arrival status
        arrival_status = self._determine_arrival_status(time_diff)

        # Update reservation with arrival info
        reservation.actual_arrival_time = actual_arrival_time
        reservation.arrival_status = arrival_status
        
        # Update reservation status to confirmed if it was pending
        if reservation.status == ReservationStatus.pending:
            reservation.status = ReservationStatus.confirmed

        self.db.commit()
        self.db.refresh(reservation)

        # Update table status to occupied
        if reservation.table_id:
            status_manager = create_table_status_manager(self.db)
            status_manager.update_table_status_for_arrival(reservation.table_id)

        # Create arrival record
        arrival_record = ArrivalRecord(
            reservation_id=reservation.id,
            arrival_time=actual_arrival_time,
            reservation_time=reservation_time,
            arrival_status=arrival_status,
            minutes_difference=int(time_diff),
            table_id=reservation.table_id,
            customer_name=reservation.customer.full_name if reservation.customer else "Guest",
            party_size=reservation.party_size
        )

        logger.info(
            f"Customer arrival recorded: Reservation {reservation_id}, "
            f"Status: {arrival_status}, Time diff: {int(time_diff)} minutes"
        )

        return arrival_record

    def _determine_arrival_status(self, minutes_difference: float) -> str:
        """
        Determine arrival status based on time difference
        """
        if minutes_difference < -self.early_threshold_minutes:
            return ArrivalStatus.EARLY
        elif abs(minutes_difference) <= self.on_time_window_minutes:
            return ArrivalStatus.ON_TIME
        elif minutes_difference <= self.late_threshold_minutes:
            return ArrivalStatus.LATE
        elif minutes_difference <= self.no_show_threshold_minutes:
            return ArrivalStatus.VERY_LATE
        else:
            return ArrivalStatus.NO_SHOW

    def check_for_no_shows(self, threshold_minutes: int = 60) -> List[Reservation]:
        """
        Check for no-show reservations (customers who didn't arrive)
        """
        current_time = datetime.utcnow()
        threshold_time = current_time - timedelta(minutes=threshold_minutes)

        # Find confirmed reservations that are past due without arrival record
        no_show_reservations = self.db.query(Reservation).filter(
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reservation_datetime <= threshold_time,
            Reservation.actual_arrival_time.is_(None)
        ).all()

        # Update status to cancelled for no-shows
        for reservation in no_show_reservations:
            reservation.status = ReservationStatus.cancelled
            reservation.arrival_status = ArrivalStatus.NO_SHOW
            
            # Release table
            if reservation.table_id:
                table = self.db.query(Table).filter(Table.id == reservation.table_id).first()
                if table and table.status == TableStatus.reserved:
                    table.status = TableStatus.available

        if no_show_reservations:
            self.db.commit()
            logger.info(f"Marked {len(no_show_reservations)} reservations as no-show")

        return no_show_reservations

    def get_arrival_statistics(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Get arrival statistics for analysis
        """
        query = self.db.query(Reservation).filter(
            Reservation.actual_arrival_time.isnot(None)
        )

        if start_date:
            query = query.filter(Reservation.reservation_datetime >= start_date)
        if end_date:
            query = query.filter(Reservation.reservation_datetime <= end_date)

        arrivals = query.all()

        if not arrivals:
            return {
                "total_arrivals": 0,
                "early": 0,
                "on_time": 0,
                "late": 0,
                "very_late": 0,
                "no_show": 0,
                "average_difference_minutes": 0
            }

        # Count by status
        status_counts = {
            ArrivalStatus.EARLY: 0,
            ArrivalStatus.ON_TIME: 0,
            ArrivalStatus.LATE: 0,
            ArrivalStatus.VERY_LATE: 0,
            ArrivalStatus.NO_SHOW: 0
        }

        total_diff = 0
        for arrival in arrivals:
            status = arrival.arrival_status or ArrivalStatus.ON_TIME
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if arrival.actual_arrival_time and arrival.reservation_datetime:
                diff = (arrival.actual_arrival_time - arrival.reservation_datetime).total_seconds() / 60
                total_diff += diff

        avg_diff = total_diff / len(arrivals) if arrivals else 0

        return {
            "total_arrivals": len(arrivals),
            "early": status_counts[ArrivalStatus.EARLY],
            "on_time": status_counts[ArrivalStatus.ON_TIME],
            "late": status_counts[ArrivalStatus.LATE],
            "very_late": status_counts[ArrivalStatus.VERY_LATE],
            "no_show": status_counts[ArrivalStatus.NO_SHOW],
            "average_difference_minutes": round(avg_diff, 1)
        }

    def get_todays_arrivals(self) -> List[dict]:
        """
        Get today's arrival records
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        arrivals = self.db.query(Reservation).filter(
            Reservation.actual_arrival_time >= today_start,
            Reservation.actual_arrival_time < today_end
        ).order_by(Reservation.actual_arrival_time.desc()).all()

        return [
            {
                "reservation_id": arr.id,
                "customer_name": arr.customer.full_name if arr.customer else "Guest",
                "table_number": arr.table.table_number if arr.table else "N/A",
                "party_size": arr.party_size,
                "reservation_time": arr.reservation_datetime.isoformat(),
                "arrival_time": arr.actual_arrival_time.isoformat(),
                "arrival_status": arr.arrival_status,
                "minutes_difference": int(
                    (arr.actual_arrival_time - arr.reservation_datetime).total_seconds() / 60
                ) if arr.actual_arrival_time and arr.reservation_datetime else 0
            }
            for arr in arrivals
        ]

    def notify_upcoming_arrivals(self, minutes_ahead: int = 30) -> List[Reservation]:
        """
        Get reservations with upcoming arrival times (for notification)
        """
        current_time = datetime.utcnow()
        upcoming_time = current_time + timedelta(minutes=minutes_ahead)

        upcoming_reservations = self.db.query(Reservation).filter(
            Reservation.status == ReservationStatus.confirmed,
            Reservation.reservation_datetime >= current_time,
            Reservation.reservation_datetime <= upcoming_time,
            Reservation.actual_arrival_time.is_(None)
        ).all()

        return upcoming_reservations


def create_arrival_tracker(db: Session) -> CustomerArrivalTracker:
    """Factory function to create CustomerArrivalTracker"""
    return CustomerArrivalTracker(db)