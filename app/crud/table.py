from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.table import Table, TableStatus
from app.schemas.table import TableCreate, TableUpdate


class CRUDTable:
    def get(self, db: Session, id: int) -> Optional[Table]:
        return db.query(Table).filter(Table.id == id).first()

    def get_by_table_number(self, db: Session, table_number: str) -> Optional[Table]:
        return db.query(Table).filter(Table.table_number == table_number).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True,
        status: Optional[TableStatus] = None,
        search: Optional[str] = None
    ) -> List[Table]:
        query = db.query(Table)
        if active_only:
            query = query.filter(Table.is_active == True)
        if status:
            query = query.filter(Table.status == status)
        if search:
            query = query.filter(
                Table.table_number.ilike(f"%{search}%") |
                Table.location.ilike(f"%{search}%")
            )
        return query.offset(skip).limit(limit).all()

    def count(
        self, 
        db: Session, 
        active_only: bool = True,
        status: Optional[TableStatus] = None,
        search: Optional[str] = None
    ) -> int:
        query = db.query(Table)
        if active_only:
            query = query.filter(Table.is_active == True)
        if status:
            query = query.filter(Table.status == status)
        if search:
            query = query.filter(
                Table.table_number.ilike(f"%{search}%") |
                Table.location.ilike(f"%{search}%")
            )
        return query.count()

    def get_available_tables(
        self, db: Session, min_capacity: Optional[int] = None,
        reservation_datetime: Optional[datetime] = None,
        duration_hours: int = 2
    ) -> List[Table]:
        """Get available tables, optionally checking for reservation conflicts"""
        query = db.query(Table).filter(
            Table.status == TableStatus.available,
            Table.is_active == True
        )
        if min_capacity:
            query = query.filter(Table.capacity >= min_capacity)
            
        # If checking for specific reservation time, exclude tables with conflicts
        if reservation_datetime:
            from app.models.order import Reservation, ReservationStatus
            
            # Calculate time window (reservation + duration)
            end_time = reservation_datetime + timedelta(hours=duration_hours)
            
            # Find tables with conflicting reservations
            conflicting_reservations = db.query(Reservation.table_id).filter(
                and_(
                    Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed]),
                    or_(
                        # New reservation starts during existing reservation
                        and_(
                            Reservation.reservation_datetime <= reservation_datetime,
                            Reservation.estimated_end_time >= reservation_datetime
                        ),
                        # New reservation ends during existing reservation
                        and_(
                            Reservation.reservation_datetime <= end_time,
                            Reservation.estimated_end_time >= end_time
                        ),
                        # New reservation completely covers existing reservation
                        and_(
                            Reservation.reservation_datetime >= reservation_datetime,
                            Reservation.estimated_end_time <= end_time
                        )
                    )
                )
            ).subquery()
            
            # Exclude tables with conflicts
            query = query.filter(~Table.id.in_(conflicting_reservations))
            
        return query.all()

    def is_table_available_at_time(
        self, db: Session, table_id: int, 
        reservation_datetime: datetime, duration_hours: int = 2
    ) -> bool:
        """Check if specific table is available at given time"""
        table = self.get(db, table_id)
        if not table or table.status != TableStatus.available or not table.is_active:
            return False
            
        from app.models.order import Reservation, ReservationStatus
        
        end_time = reservation_datetime + timedelta(hours=duration_hours)
        
        conflicting_count = db.query(Reservation).filter(
            and_(
                Reservation.table_id == table_id,
                Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed]),
                or_(
                    and_(
                        Reservation.reservation_datetime <= reservation_datetime,
                        Reservation.estimated_end_time >= reservation_datetime
                    ),
                    and_(
                        Reservation.reservation_datetime <= end_time,
                        Reservation.estimated_end_time >= end_time
                    ),
                    and_(
                        Reservation.reservation_datetime >= reservation_datetime,
                        Reservation.estimated_end_time <= end_time
                    )
                )
            )
        ).count()
        
        return conflicting_count == 0

    def get_by_status(self, db: Session, status: TableStatus) -> List[Table]:
        return db.query(Table).filter(
            Table.status == status,
            Table.is_active == True
        ).all()

    def create(self, db: Session, obj_in: TableCreate) -> Table:
        db_obj = Table(
            table_number=obj_in.table_number,
            capacity=obj_in.capacity,
            status=obj_in.status,
            location=obj_in.location,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: Table, obj_in: TableUpdate
    ) -> Table:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self, db: Session, table_id: int, status: TableStatus
    ) -> Optional[Table]:
        db_obj = self.get(db, table_id)
        if db_obj:
            db_obj.status = status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Table:
        obj = db.query(Table).get(id)
        db.delete(obj)
        db.commit()
        return obj


table = CRUDTable()