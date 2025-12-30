from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.user import user as user_crud
from app.schemas.user import User, UserUpdate
from app.api.deps import get_current_user, get_current_manager_user, get_current_admin_user
from app.models.user import UserRole

router = APIRouter()


@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update own user.
    """
    # Users cannot change their own role
    if hasattr(user_in, 'role') and user_in.role is not None:
        user_in.role = None
    
    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_manager_user),
) -> Any:
    """
    Retrieve users (Manager+ only).
    """
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_manager_user),
) -> Any:
    """
    Get a specific user by id (Manager+ only).
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Update a user (Admin only).
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Only admin can change roles
    if hasattr(user_in, 'role') and user_in.role is not None:
        if current_user.role != UserRole.admin:
            user_in.role = None
    
    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Delete a user (Admin only).
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Don't allow deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )
    
    user = user_crud.delete(db, id=user_id)
    return user


@router.get("/staff/list", response_model=List[User])
def get_staff_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager_user),
) -> Any:
    """
    Get all staff users (Manager+ only).
    """
    staff_users = user_crud.get_by_role(db, role=UserRole.staff.value)
    return staff_users


@router.post("/me/change-password")
def change_password(
    *,
    db: Session = Depends(get_db),
    password_in: dict,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Change current user's password.
    """
    current_password = password_in.get("current_password")
    new_password = password_in.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Both current_password and new_password are required"
        )
    
    # Verify current password
    if not user_crud.authenticate(db, username=current_user.username, password=current_password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect current password"
        )
    
    # Validate new password length
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long"
        )
    
    # Update password
    user_crud.update_password(db, db_obj=current_user, new_password=new_password)
    
    return {"message": "Password changed successfully"}