from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas.schemas import UserRegister, UserLogin, UserResponse, Token
from app.utils.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Validate input
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        is_verified=True  # Mark as verified after registration
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=access_token_expires
    )
    
    # Return both the user AND the token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    full_name: str = None,
    phone_number: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    if full_name:
        current_user.full_name = full_name
    
    if phone_number:
        # Check if phone number is already used
        existing = db.query(User).filter(
            User.phone_number == phone_number,
            User.id != current_user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use"
            )
        
        current_user.phone_number = phone_number
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    confirm_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect"
        )
    
    # Validate new password
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
@router.get("/google")
async def google_login():
    """
    Handle Google Auth Redirection
    URL: GET http://localhost:8000/api/auth/google
    """

    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    return RedirectResponse(url=google_auth_url)

@router.get("/github")
async def github_login():
    """
    Handle GitHub Auth Redirection
    URL: GET http://localhost:8000/api/auth/github
    """
    github_auth_url = "https://github.com/login/oauth/authorize"
    
    return RedirectResponse(url=github_auth_url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Step 2: Google redirects here with a 'code'
    URL: http://localhost:8000/api/auth/google/callback
    """
    # In a real app, you'd exchange 'code' for user info.
    # For your project demo, we can simulate a successful login:
    test_email = "google_user@gmail.com"
    user = db.query(User).filter(User.email == test_email).first()
    
    if not user:
        # Create a new user if they don't exist
        user = User(
            email=test_email,
            full_name="Google User",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create a JWT token for them
    access_token = create_access_token(data={"sub": user.email})
    
    # Redirect back to your React Frontend Dashboard with the token
    # We pass the token in the URL so React can grab it
    frontend_url = f"https://https://researchpaperpro.netlify.app/login?token={access_token}"
    return RedirectResponse(url=frontend_url)

@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """
    Step 2: GitHub redirects here
    URL: http://localhost:8000/api/auth/github/callback
    """
    # Similar logic for GitHub...
    # frontend_url = "http://localhost:5173/login?status=success"
    # In auth.py
    frontend_base = os.getenv("FRONTEND_URL", https://researchpaperpro.netlify.app)#"https://localhost:5173")
    frontend_url = f"{frontend_base}/login?token={access_token}"
    return RedirectResponse(url=frontend_url)
