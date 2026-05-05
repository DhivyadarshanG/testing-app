"""User service with intentional bugs."""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.exceptions import UserNotFoundError, UnauthorizedError, raise_forbidden
from app.config import is_bug_enabled


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
    
    BUG-005: Missing Permission Check on Delete
    When enabled, any authenticated user can delete any user.
    """
    user = get_user(db, user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    
    # BUG-005: Missing permission check
    if is_bug_enabled("005"):
        # BUGGY: No permission check - any user can delete any user
        db.delete(user)
        db.commit()
        return True
    else:
        # CORRECT: Check if user is deleting themselves or is admin
        if current_user.id != user_id and not current_user.is_admin:
            raise_forbidden("You don't have permission to delete this user")
        
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
