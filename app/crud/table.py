from sqlalchemy.orm import Session
from typing import Optional, List
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
        self, db: Session, min_capacity: Optional[int] = None
    ) -> List[Table]:
        query = db.query(Table).filter(
            Table.status == TableStatus.available,
            Table.is_active == True
        )
        if min_capacity:
            query = query.filter(Table.capacity >= min_capacity)
        return query.all()

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