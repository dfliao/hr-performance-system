"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
ALGORITHM = "HS256"


def create_access_token(data: Dict[Any, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_user_token(user_id: int, username: str, email: str, role: str, department_id: Optional[int] = None) -> str:
    """Create user JWT token with role and department info"""
    token_data = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "role": role,
        "department_id": department_id
    }
    return create_access_token(token_data)


class SecurityScopes:
    """Security scopes for role-based access control"""
    
    # System roles
    ADMIN = "admin"
    AUDITOR = "auditor"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    
    # Permissions
    EVENTS_CREATE = "events:create"
    EVENTS_READ = "events:read"
    EVENTS_UPDATE = "events:update"
    EVENTS_DELETE = "events:delete"
    EVENTS_APPROVE = "events:approve"
    
    REPORTS_READ = "reports:read"
    REPORTS_EXPORT = "reports:export"
    
    RULES_CREATE = "rules:create"
    RULES_READ = "rules:read"
    RULES_UPDATE = "rules:update"
    RULES_DELETE = "rules:delete"
    
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    
    AUDIT_READ = "audit:read"
    
    # Role permissions mapping
    ROLE_PERMISSIONS = {
        ADMIN: [
            EVENTS_CREATE, EVENTS_READ, EVENTS_UPDATE, EVENTS_DELETE, EVENTS_APPROVE,
            REPORTS_READ, REPORTS_EXPORT,
            RULES_CREATE, RULES_READ, RULES_UPDATE, RULES_DELETE,
            USERS_CREATE, USERS_READ, USERS_UPDATE, USERS_DELETE,
            AUDIT_READ
        ],
        AUDITOR: [
            EVENTS_READ,
            REPORTS_READ, REPORTS_EXPORT,
            RULES_READ,
            USERS_READ,
            AUDIT_READ
        ],
        MANAGER: [
            EVENTS_CREATE, EVENTS_READ, EVENTS_UPDATE, EVENTS_APPROVE,
            REPORTS_READ, REPORTS_EXPORT,
            RULES_READ,
            USERS_READ
        ],
        EMPLOYEE: [
            EVENTS_READ,  # Own events only
            REPORTS_READ  # Own reports only
        ]
    }
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        return permission in cls.ROLE_PERMISSIONS.get(role, [])
    
    @classmethod
    def get_role_permissions(cls, role: str) -> list:
        """Get all permissions for a role"""
        return cls.ROLE_PERMISSIONS.get(role, [])