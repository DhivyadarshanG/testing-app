"""Authentication service with intentional bugs."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import UserSession
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.utils.exceptions import TokenNotFoundError, UnauthorizedError
from app.config import is_bug_enabled


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    BUG-006: Password Hash Not Verified
    When enabled, compares plain text password directly instead of using bcrypt.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    # BUG-006: Password hash not verified properly
    if is_bug_enabled("006"):
        # BUGGY: Direct comparison instead of hash verification
        if password == user.hashed_password:
            return user
        return None
    else:
        # CORRECT: Use bcrypt verification
        if not verify_password(password, user.hashed_password):
            return None
        return user


def create_session(db: Session, user_id: int) -> UserSession:
    """
    Create a new session for a user.
    
    BUG-009: Concurrent Session Creation
    When enabled, doesn't handle race conditions properly.
    """
    token = create_access_token(data={"sub": str(user_id)})
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    # BUG-009: No handling of concurrent session creation
    if is_bug_enabled("009"):
        # BUGGY: Just create without checking for existing sessions
        session = UserSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    else:
        # CORRECT: Check for existing active sessions and handle properly
        try:
            session = UserSession(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
        except Exception as e:
            db.rollback()
            # If duplicate, fetch existing session
            existing = db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            ).first()
            if existing:
                return existing
            raise


def validate_token(db: Session, token: str) -> Optional[User]:
    """
    Validate a session token and return the associated user.
    
    BUG-001: Missing Null Check on User Token
    BUG-004: Token Expiry Not Checked
    """
    session = db.query(UserSession).filter(UserSession.token == token).first()
    
    # BUG-001: Missing null check on token
    if is_bug_enabled("001"):
        # BUGGY: Accessing user_id without checking if session is None
        user = db.query(User).filter(User.id == session.user_id).first()
        return user
    
    if not session:
        raise TokenNotFoundError("Invalid or expired token")
    
    # BUG-004: Token expiry not checked
    if is_bug_enabled("004"):
        # BUGGY: Return user even if token is expired
        user = db.query(User).filter(User.id == session.user_id).first()
        return user
    else:
        # CORRECT: Check token expiry
        if session.is_expired():
            raise TokenNotFoundError("Token has expired")
        
        user = db.query(User).filter(User.id == session.user_id).first()
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
