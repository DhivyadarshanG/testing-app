"""Authentication service with production-grade bugs."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import UserSession
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.exceptions import TokenNotFoundError, UnauthorizedError


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    BUG: Password comparison is done incorrectly - compares plain text with hash
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    # BUG: Direct string comparison instead of using bcrypt verify
    if password == user.hashed_password:
        return user
    return None


def create_session(db: Session, user_id: int) -> UserSession:
    """
    Create a new session for a user.
    
    BUG: No handling for concurrent session creation - can create duplicates
    """
    token = create_access_token(data={"sub": str(user_id)})
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    # BUG: No try-catch for IntegrityError on duplicate sessions
    session = UserSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    def create_session(self, user_id: int) -> Session:
        session = Session(user_id=user_id)
        db.add(session)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return self.create_session(user_id)  # retry
        return session


def validate_token(db: Session, token: str) -> Optional[User]:
    """
    Validate a session token and return the associated user.
    
    BUG 1: Missing null check - crashes if token not found
    BUG 2: Token expiry not checked - accepts expired tokens
    """
    session = db.query(UserSession).filter(UserSession.token == token).first()
    
    # BUG 1: Accessing session.user_id without checking if session is None
    user = db.query(User).filter(User.id == session.user_id).first()
    
    # BUG 2: Not checking if token is expired
    return user


def create_user(db: Session, email: str, username: str, password: str, is_admin: bool = False) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Made with Bob
