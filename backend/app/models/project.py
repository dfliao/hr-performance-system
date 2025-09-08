"""
Project model - Optional project mapping for Redmine integration
"""

from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

from app.models.base import BaseModel


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(BaseModel, table=True):
    """Project model with Redmine integration"""
    
    __tablename__ = "projects"
    
    # Basic Info
    code: str = Field(unique=True, max_length=20, index=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    
    # Department Association
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    
    # Redmine Integration
    redmine_project_id: Optional[int] = Field(default=None, index=True)
    redmine_identifier: Optional[str] = Field(default=None, max_length=50)
    
    # Project Timeline
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    
    # Status
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    priority: int = Field(default=1)  # 1=Low, 2=Normal, 3=High, 4=Urgent
    
    # Manager
    manager_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Metrics
    budget: Optional[float] = Field(default=None)
    progress: int = Field(default=0, ge=0, le=100)  # Percentage
    
    # Settings
    is_active: bool = Field(default=True)
    enable_performance_tracking: bool = Field(default=True)
    
    # Relationships
    department: Optional["Department"] = Relationship(back_populates="projects")
    manager: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Project.manager_user_id",
            "post_update": True
        }
    )
    events: List["Event"] = Relationship(back_populates="project")
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue"""
        if not self.end_date:
            return False
        return datetime.now().date() > self.end_date and self.status == ProjectStatus.ACTIVE
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Get days remaining for project completion"""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.now().date()
        return delta.days
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed"""
        return self.status == ProjectStatus.COMPLETED or self.progress >= 100


class ProjectCreate(SQLModel):
    """Project creation schema"""
    code: str = Field(max_length=20)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    department_id: Optional[int] = None
    redmine_project_id: Optional[int] = None
    redmine_identifier: Optional[str] = Field(default=None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    priority: int = Field(default=1, ge=1, le=4)
    manager_user_id: Optional[int] = None
    budget: Optional[float] = None


class ProjectUpdate(SQLModel):
    """Project update schema"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    department_id: Optional[int] = None
    redmine_project_id: Optional[int] = None
    redmine_identifier: Optional[str] = Field(default=None, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[int] = Field(default=None, ge=1, le=4)
    manager_user_id: Optional[int] = None
    budget: Optional[float] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    is_active: Optional[bool] = None
    enable_performance_tracking: Optional[bool] = None


class ProjectRead(SQLModel):
    """Project read schema"""
    id: int
    code: str
    name: str
    description: Optional[str]
    department_id: Optional[int]
    redmine_project_id: Optional[int]
    redmine_identifier: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: ProjectStatus
    priority: int
    manager_user_id: Optional[int]
    budget: Optional[float]
    progress: int
    is_active: bool
    enable_performance_tracking: bool
    
    # Additional info
    department_name: Optional[str] = None
    manager_name: Optional[str] = None
    days_remaining: Optional[int] = None
    is_overdue: bool = False
    event_count: int = 0