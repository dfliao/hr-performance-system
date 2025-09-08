"""
Authentication endpoints
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_user_token
from app.models import User, UserRead
from app.services.auth import authenticate_user, get_current_user

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Login with username and password
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號已被停用",
        )
    
    # Create access token
    access_token = create_user_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        department_id=user.department_id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserRead.from_orm(user)
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    """
    Logout current user
    """
    # In a more sophisticated setup, you might want to blacklist the token
    # For now, we just return success - the frontend will remove the token
    return {"message": "登出成功"}


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user information
    """
    return current_user


@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Refresh access token
    """
    # Create new access token
    access_token = create_user_token(
        user_id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        department_id=current_user.department_id
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserRead.from_orm(current_user)
    }


@router.post("/change-password")
async def change_password(
    current_password: str = Form(),
    new_password: str = Form(),
    confirm_password: str = Form(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    Change user password
    """
    # This would typically verify the current password and update to new password
    # For LDAP users, this might need to integrate with LDAP server
    # For now, return a placeholder response
    
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密碼與確認密碼不符"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密碼長度至少需要 6 個字符"
        )
    
    # TODO: Implement password change logic with LDAP
    # This would require LDAP admin permissions or user self-service
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="密碼變更功能尚未實作，請聯繫 IT 部門"
    )


@router.patch("/profile", response_model=UserRead)
async def update_profile(
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Update user profile
    """
    # Update allowed fields
    if name:
        current_user.name = name
    if email:
        current_user.email = email  
    if phone:
        current_user.phone = phone
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/avatar")
async def upload_avatar(
    current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    """
    Upload user avatar
    """
    # TODO: Implement avatar upload to Synology Drive
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="頭像上傳功能尚未實作"
    )