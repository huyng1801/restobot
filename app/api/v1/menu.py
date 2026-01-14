from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.menu import category as category_crud, menu_item as menu_item_crud
from app.schemas.menu import (
    Category, CategoryCreate, CategoryUpdate, CategoryWithItems,
    MenuItem, MenuItemCreate, MenuItemUpdate, PaginatedMenuResponse, PaginatedCategoryResponse
)
from app.api.deps import get_current_staff_user, get_current_user_optional

router = APIRouter()


# Category endpoints
@router.get("/categories/", response_model=PaginatedCategoryResponse)
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None, description="Search query"),
    active_only: bool = Query(True, description="Filter only active categories"),
    # current_user = Depends(get_current_user_optional),  # Tạm disable auth
) -> Any:
    """
    Retrieve categories with pagination and search.
    """
    categories = category_crud.get_multi_with_search(
        db, skip=skip, limit=limit, search=q, active_only=active_only
    )
    total = category_crud.count_with_search(db, search=q, active_only=active_only)
    
    return PaginatedCategoryResponse(
        items=categories,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/categories/with-items", response_model=List[CategoryWithItems])
def read_categories_with_items(
    db: Session = Depends(get_db),
    # current_user = Depends(get_current_user_optional),  # Tạm disable auth
) -> Any:
    """
    Retrieve categories with their menu items.
    """
    categories = category_crud.get_multi(db, active_only=True)
    return categories


@router.post("/categories/", response_model=Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Create new category (Staff+ only).
    """
    # Check if category with same name exists
    existing_category = category_crud.get_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists"
        )
    
    category = category_crud.create(db, obj_in=category_in)
    return category


@router.get("/categories/{category_id}", response_model=Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Get category by ID.
    """
    category = category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update category (Staff+ only).
    """
    category = category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if new name conflicts with existing category
    if category_in.name and category_in.name != category.name:
        existing_category = category_crud.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail="Category with this name already exists"
            )
    
    category = category_crud.update(db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/categories/{category_id}", response_model=Category)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Delete category (Staff+ only).
    """
    category = category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has menu items
    items = menu_item_crud.get_multi(db, category_id=category_id, available_only=False)
    if items:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with existing menu items"
        )
    
    category = category_crud.delete(db, id=category_id)
    return category


# Menu Item endpoints
@router.get("/items/", response_model=PaginatedMenuResponse)
def read_menu_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    available_only: bool = Query(True, description="Filter only available items"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    q: Optional[str] = Query(None, description="Search term for item name"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    is_available: Optional[bool] = Query(None, description="Filter by availability status"),
    # current_user = Depends(get_current_user_optional),  # Tạm disable auth
) -> Any:
    """
    Retrieve menu items with pagination and search.
    """
    # Get total count with filters applied
    total = menu_item_crud.get_count(
        db, available_only=available_only, category_id=category_id, search_term=q,
        is_featured=is_featured, is_available=is_available
    )
    
    # Get items with pagination
    items = menu_item_crud.get_multi(
        db, skip=skip, limit=limit, 
        available_only=available_only, 
        category_id=category_id,
        search_term=q,
        is_featured=is_featured,
        is_available=is_available
    )
    
    # Calculate pagination info
    pages = (total + limit - 1) // limit if limit > 0 else 1
    page = skip // limit if limit > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages
    }


@router.get("/items/featured", response_model=List[MenuItem])
def read_featured_items(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Retrieve featured menu items.
    """
    items = menu_item_crud.get_featured(db)
    return items

@router.post("/items/", response_model=MenuItem)
def create_menu_item(
    *,
    db: Session = Depends(get_db),
    item_in: MenuItemCreate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Create new menu item (Staff+ only).
    """
    # Check if category exists
    category = category_crud.get(db, id=item_in.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    # Check if item with same name exists
    existing_item = menu_item_crud.get_by_name(db, name=item_in.name)
    if existing_item:
        raise HTTPException(
            status_code=400,
            detail="Menu item with this name already exists"
        )
    
    item = menu_item_crud.create(db, obj_in=item_in)
    return item


@router.get("/items/{item_id}", response_model=MenuItem)
def read_menu_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user = Depends(get_current_user_optional),
) -> Any:
    """
    Get menu item by ID.
    """
    item = menu_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item


@router.put("/items/{item_id}", response_model=MenuItem)
def update_menu_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: MenuItemUpdate,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Update menu item (Staff+ only).
    """
    item = menu_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check if category exists (if being updated)
    if item_in.category_id and item_in.category_id != item.category_id:
        category = category_crud.get(db, id=item_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Check if new name conflicts with existing item
    if item_in.name and item_in.name != item.name:
        existing_item = menu_item_crud.get_by_name(db, name=item_in.name)
        if existing_item:
            raise HTTPException(
                status_code=400,
                detail="Menu item with this name already exists"
            )
    
    item = menu_item_crud.update(db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/items/{item_id}", response_model=MenuItem)
def delete_menu_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user = Depends(get_current_staff_user),
) -> Any:
    """
    Delete menu item (Staff+ only).
    """
    item = menu_item_crud.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    item = menu_item_crud.delete(db, id=item_id)
    return item