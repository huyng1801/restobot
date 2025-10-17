from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.menu import Category, MenuItem
from app.schemas.menu import CategoryCreate, CategoryUpdate, MenuItemCreate, MenuItemUpdate


class CRUDCategory:
    def get(self, db: Session, id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Category]:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        return query.offset(skip).limit(limit).all()

    def get_multi_with_search(
        self, db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None, active_only: bool = True
    ) -> List[Category]:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))
        query = query.order_by(Category.name.asc())
        return query.offset(skip).limit(limit).all()

    def count_with_search(
        self, db: Session, search: Optional[str] = None, active_only: bool = True
    ) -> int:
        query = db.query(Category)
        if active_only:
            query = query.filter(Category.is_active == True)
        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))
        return query.count()

    def create(self, db: Session, obj_in: CategoryCreate) -> Category:
        db_obj = Category(
            name=obj_in.name,
            description=obj_in.description,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: Category, obj_in: CategoryUpdate
    ) -> Category:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Category:
        obj = db.query(Category).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDMenuItem:
    def get(self, db: Session, id: int) -> Optional[MenuItem]:
        return db.query(MenuItem).filter(MenuItem.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[MenuItem]:
        return db.query(MenuItem).filter(MenuItem.name == name).first()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        available_only: bool = True,
        category_id: Optional[int] = None,
        search_term: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_available: Optional[bool] = None
    ) -> List[MenuItem]:
        query = db.query(MenuItem)
        if available_only:
            query = query.filter(MenuItem.is_available == True)
        if category_id:
            query = query.filter(MenuItem.category_id == category_id)
        if search_term:
            query = query.filter(MenuItem.name.ilike(f"%{search_term}%"))
        if is_featured is not None:
            query = query.filter(MenuItem.is_featured == is_featured)
        if is_available is not None:
            query = query.filter(MenuItem.is_available == is_available)
        query = query.order_by(MenuItem.name.asc())
        return query.offset(skip).limit(limit).all()

    def get_count(
        self, 
        db: Session, 
        available_only: bool = True,
        category_id: Optional[int] = None,
        search_term: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_available: Optional[bool] = None
    ) -> int:
        query = db.query(MenuItem)
        if available_only:
            query = query.filter(MenuItem.is_available == True)
        if category_id:
            query = query.filter(MenuItem.category_id == category_id)
        if search_term:
            query = query.filter(MenuItem.name.ilike(f"%{search_term}%"))
        if is_featured is not None:
            query = query.filter(MenuItem.is_featured == is_featured)
        if is_available is not None:
            query = query.filter(MenuItem.is_available == is_available)
        return query.count()

    def get_featured(self, db: Session) -> List[MenuItem]:
        return db.query(MenuItem).filter(
            MenuItem.is_featured == True,
            MenuItem.is_available == True
        ).all()

    def search_by_name(self, db: Session, search_term: str) -> List[MenuItem]:
        return db.query(MenuItem).filter(
            MenuItem.name.ilike(f"%{search_term}%"),
            MenuItem.is_available == True
        ).all()

    def create(self, db: Session, obj_in: MenuItemCreate) -> MenuItem:
        db_obj = MenuItem(
            name=obj_in.name,
            description=obj_in.description,
            price=obj_in.price,
            image_url=obj_in.image_url,
            is_available=obj_in.is_available,
            is_featured=obj_in.is_featured,
            preparation_time=obj_in.preparation_time,
            category_id=obj_in.category_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: MenuItem, obj_in: MenuItemUpdate
    ) -> MenuItem:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> MenuItem:
        obj = db.query(MenuItem).get(id)
        db.delete(obj)
        db.commit()
        return obj


category = CRUDCategory()
menu_item = CRUDMenuItem()