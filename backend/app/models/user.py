"""
User model - LDAP synchronized user data
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

from app.models.base import BaseModel


class UserStatus(str, Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    AUDITOR = "auditor"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(BaseModel, table=True):
    """User model with LDAP synchronization"""
    
    __tablename__ = "users"
    
    # LDAP Fields
    ldap_uid: str = Field(unique=True, index=True, max_length=50)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(max_length=100)
    display_name: Optional[str] = Field(default=None, max_length=100)
    
    # Organization
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    title: Optional[str] = Field(default=None, max_length=100)
    employee_id: Optional[str] = Field(default=None, max_length=20, index=True)
    
    # Status and Role
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    
    # LDAP Sync
    last_ldap_sync: Optional[datetime] = Field(default=None)
    ldap_dn: Optional[str] = Field(default=None, max_length=255)
    
    # Additional Info
    phone: Optional[str] = Field(default=None, max_length=20)
    avatar_url: Optional[str] = Field(default=None, max_length=255)
    
    # Relationships
    department: Optional["Department"] = Relationship(back_populates="users")
    events_reported: List["Event"] = Relationship(
        back_populates="reporter",
        sa_relationship_kwargs={"foreign_keys": "Event.reporter_id"}
    )
    events_received: List["Event"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Event.user_id"}
    )
    scores: List["Score"] = Relationship(back_populates="user")
    audit_logs: List["AuditLog"] = Relationship(back_populates="actor")
    
    def __str__(self):
        return f"{self.name} ({self.username})"
    
    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_manager(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


class UserCreate(SQLModel):
    """User creation schema"""
    ldap_uid: str = Field(max_length=50)
    username: str = Field(max_length=50)
    email: str = Field(max_length=100)
    name: str = Field(max_length=100)
    department_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=100)
    employee_id: Optional[str] = Field(default=None, max_length=20)
    role: UserRole = UserRole.EMPLOYEE
    phone: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(SQLModel):
    """User update schema"""
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    department_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=100)
    employee_id: Optional[str] = Field(default=None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    phone: Optional[str] = Field(default=None, max_length=20)


class UserRead(SQLModel):
    """User read schema"""
    id: int
    ldap_uid: str
    username: str
    email: str
    name: str
    display_name: Optional[str]
    department_id: Optional[int]
    title: Optional[str]
    employee_id: Optional[str]
    status: UserStatus
    role: UserRole
    phone: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]