"""
Department model - Organizational hierarchy
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

from app.models.base import BaseModel


class Department(BaseModel, table=True):
    """Department model with hierarchical structure"""
    
    __tablename__ = "departments"
    
    # Basic Info
    name: str = Field(max_length=100, index=True)
    code: str = Field(unique=True, max_length=20, index=True)
    description: Optional[str] = Field(default=None, max_length=255)
    
    # Hierarchy
    parent_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    level: int = Field(default=0)  # Depth in hierarchy
    path: Optional[str] = Field(default=None, max_length=255)  # /root/dept1/subdept1
    
    # Manager
    manager_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Status
    is_active: bool = Field(default=True)
    
    # Contact Info
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    location: Optional[str] = Field(default=None, max_length=100)
    
    # Relationships
    parent: Optional["Department"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Department.id"}
    )
    children: List["Department"] = Relationship(back_populates="parent")
    users: List["User"] = Relationship(back_populates="department")
    manager: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Department.manager_user_id",
            "post_update": True
        }
    )
    projects: List["Project"] = Relationship(back_populates="department")
    events: List["Event"] = Relationship(back_populates="department")
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def full_path(self) -> str:
        """Get full department path"""
        if self.path:
            return self.path
        return self.name
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root department"""
        return self.parent_id is None
    
    @property
    def has_children(self) -> bool:
        """Check if department has sub-departments"""
        return len(self.children) > 0


class DepartmentCreate(SQLModel):
    """Department creation schema"""
    name: str = Field(max_length=100)
    code: str = Field(max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    parent_id: Optional[int] = None
    manager_user_id: Optional[int] = None
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    location: Optional[str] = Field(default=None, max_length=100)


class DepartmentUpdate(SQLModel):
    """Department update schema"""
    name: Optional[str] = Field(default=None, max_length=100)
    code: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None, max_length=255)
    parent_id: Optional[int] = None
    manager_user_id: Optional[int] = None
    is_active: Optional[bool] = None
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    location: Optional[str] = Field(default=None, max_length=100)


class DepartmentRead(SQLModel):
    """Department read schema"""
    id: int
    name: str
    code: str
    description: Optional[str]
    parent_id: Optional[int]
    level: int
    path: Optional[str]
    manager_user_id: Optional[int]
    is_active: bool
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    
    # Manager info
    manager_name: Optional[str] = None
    
    # Statistics
    user_count: int = 0
    child_count: int = 0