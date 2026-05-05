"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.services import user_service
from app.models.user import User
from app.routers.auth import get_current_user
from app.utils.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    """User update schema."""
    email: EmailStr | None = None
    username: str | None = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users (requires authentication)."""
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user information."""
    try:
        user = user_service.update_user(
            db=db,
            user_id=user_id,
            email=user_data.email,
            username=user_data.username
        )
        return user
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user.
    Triggers BUG-005 if enabled (missing permission check).
    """
    try:
        user_service.delete_user(db, user_id, current_user)
        return None
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Made with Bob
