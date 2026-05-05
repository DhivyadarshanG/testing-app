"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.services import auth_service
from app.models.user import User
from app.utils.exceptions import TokenNotFoundError

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    username: str
    password: str


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    username: str
    is_admin: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str


class TokenValidation(BaseModel):
    """Token validation response."""
    valid: bool
    user: UserResponse | None = None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token.
    Uses BUG-001 and BUG-004 from auth_service.validate_token
    """
    try:
        user = auth_service.validate_token(db, token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return user
    except TokenNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = auth_service.create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    Uses BUG-006 from auth_service.authenticate_user
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create session (uses BUG-009)
    session = auth_service.create_session(db, user.id)
    
    return {
        "access_token": session.token,
        "token_type": "bearer"
    }


@router.get("/validate", response_model=TokenValidation)
def validate_token(current_user: User = Depends(get_current_user)):
    """
    Validate current token.
    Triggers BUG-001 and BUG-004 if enabled.
    """
    return {
        "valid": True,
        "user": current_user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

# Made with Bob
