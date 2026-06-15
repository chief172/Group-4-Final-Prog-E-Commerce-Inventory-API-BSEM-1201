from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.auth_bearer import JWTBearer

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    
    - **username**: Unique display name (3-50 characters)
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 6 characters
    - **role**: Optional - 'admin' or 'customer' (default: 'customer')
    """
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user with the role from request
    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,  # ← Use the role from request
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login user and return JWT access token.
    
    - **email**: Registered email address
    - **password**: Account password
    
    Returns JWT token for authenticated requests.
    """
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact support."
        )
    
    # Create access token with user info
    access_token = create_access_token({
        "sub": db_user.email,
        "role": db_user.role,
        "user_id": db_user.id,
        "username": db_user.username
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "role": db_user.role,
            "is_active": db_user.is_active
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token_data: dict = Depends(JWTBearer()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    
    email = token_data.get("sub")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/logout")
async def logout(token_data: dict = Depends(JWTBearer())):
    """
    Logout user (client-side token removal).
    
    Note: JWT tokens are stateless. Client should discard the token.
    """
    return {
        "message": "Successfully logged out",
        "instruction": "Please remove the token from client storage"
    }