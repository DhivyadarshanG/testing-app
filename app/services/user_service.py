"""User service with production-grade bugs."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.exceptions import UserNotFoundError, raise_forbidden


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int, current_user: User) -> bool:
    """
    Delete a user.
    
    BUG: Missing permission check - any user can delete any user
    """
    user = get_user(db, user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    
    # BUG: No permission check - should verify current_user is admin or deleting self
    db.delete(user)
    db.commit()
    return True


def update_user(db: Session, user_id: int, email: Optional[str] = None, 
                username: Optional[str] = None) -> User:
    """Update user information."""
    user = get_user(db, user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    
    if email:
        user.email = email
    if username:
        user.username = username
    
    db.commit()
    db.refresh(user)
    return user

# Made with Bob
