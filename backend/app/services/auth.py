"""
Authentication service - LDAP integration and user management
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from jose import JWTError

from app.core.config import settings
from app.core.security import verify_token
from app.core.database import get_db
from app.models import User

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with LDAP and sync to local database
    """
    try:
        # TODO: Implement actual LDAP authentication
        # For now, we'll use a simple demo user for development
        
        # Demo user for development/testing
        if username == "admin" and password == "admin123":
            # Check if user exists in database
            statement = select(User).where(User.username == username)
            user = db.exec(statement).first()
            
            if not user:
                # Create demo admin user
                user = User(
                    ldap_uid="admin",
                    username="admin",
                    email="admin@gogopeaks.com",
                    name="系統管理員",
                    role="admin",
                    status="active",
                    employee_id="ADMIN001"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            return user
        
        # TODO: Real LDAP authentication implementation
        """
        Example LDAP authentication code:
        
        import ldap3
        
        try:
            server = ldap3.Server(settings.LDAP_SERVER)
            conn = ldap3.Connection(
                server,
                user=f"uid={username},{settings.LDAP_USER_BASE_DN}",
                password=password,
                authentication=ldap3.SIMPLE
            )
            
            if conn.bind():
                # Authentication successful, sync user data
                user_data = get_ldap_user_data(conn, username)
                user = sync_ldap_user(db, user_data)
                return user
            else:
                return None
                
        except Exception as e:
            print(f"LDAP authentication error: {e}")
            return None
        """
        
        return None
        
    except Exception as e:
        print(f"Authentication error: {e}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證身份",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    statement = select(User).where(User.id == int(user_id))
    user = db.exec(statement).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號已被停用"
        )
    
    return user


def sync_ldap_user(db: Session, ldap_data: dict) -> User:
    """
    Sync LDAP user data to local database
    """
    # Check if user exists
    statement = select(User).where(User.ldap_uid == ldap_data["uid"])
    user = db.exec(statement).first()
    
    if user:
        # Update existing user
        user.name = ldap_data.get("cn", user.name)
        user.email = ldap_data.get("mail", user.email)
        user.last_ldap_sync = datetime.now()
        # Update other fields as needed
    else:
        # Create new user
        user = User(
            ldap_uid=ldap_data["uid"],
            username=ldap_data["uid"],
            email=ldap_data.get("mail", ""),
            name=ldap_data.get("cn", ldap_data["uid"]),
            ldap_dn=ldap_data.get("dn", ""),
            status="active",
            role="employee",  # Default role
            last_ldap_sync=datetime.now()
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    return user


def get_ldap_user_data(connection, username: str) -> dict:
    """
    Get user data from LDAP server
    """
    # TODO: Implement LDAP user data retrieval
    """
    Example implementation:
    
    search_base = settings.LDAP_USER_BASE_DN
    search_filter = f"({settings.LDAP_USER_ID_ATTRIBUTE}={username})"
    attributes = [
        settings.LDAP_USER_NAME_ATTRIBUTE,
        settings.LDAP_USER_EMAIL_ATTRIBUTE,
        'departmentNumber',
        'title',
        'employeeID',
        'telephoneNumber'
    ]
    
    connection.search(search_base, search_filter, attributes=attributes)
    
    if connection.entries:
        entry = connection.entries[0]
        return {
            'dn': entry.entry_dn,
            'uid': username,
            'cn': str(entry[settings.LDAP_USER_NAME_ATTRIBUTE]),
            'mail': str(entry[settings.LDAP_USER_EMAIL_ATTRIBUTE]),
            'department': str(entry.departmentNumber) if entry.departmentNumber else None,
            'title': str(entry.title) if entry.title else None,
            'employeeID': str(entry.employeeID) if entry.employeeID else None,
            'phone': str(entry.telephoneNumber) if entry.telephoneNumber else None
        }
    
    return {}
    """
    return {}