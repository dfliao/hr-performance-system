"""
Rule Pack and Rule models - Configurable scoring rules
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum

from app.models.base import BaseModel


class RulePackScope(str, Enum):
    """Rule pack scope enumeration"""
    COMPANY = "company"
    DEPARTMENT = "department"
    ROLE = "role"


class RulePackStatus(str, Enum):
    """Rule pack status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class RuleDirection(str, Enum):
    """Rule direction enumeration"""
    POSITIVE = "positive"  # +
    NEGATIVE = "negative"  # -


class RulePack(BaseModel, table=True):
    """Rule pack for scoring configuration"""
    
    __tablename__ = "rule_packs"
    
    # Basic Info
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None)
    version: str = Field(max_length=20, default="1.0.0")
    
    # Scope and Target
    scope: RulePackScope = Field(default=RulePackScope.COMPANY)
    target_department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    target_role: Optional[str] = Field(default=None, max_length=50)
    
    # Status and Lifecycle
    status: RulePackStatus = Field(default=RulePackStatus.DRAFT)
    effective_from: date = Field(default_factory=lambda: datetime.now().date())
    effective_to: Optional[date] = Field(default=None)
    
    # Configuration
    json_schema: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": JSON})
    weight_config: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": JSON})
    
    # Metadata
    created_by: int = Field(foreign_key="users.id")
    approved_by: Optional[int] = Field(default=None, foreign_key="users.id")
    approved_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    creator: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "RulePack.created_by",
            "post_update": True
        }
    )
    approver: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "RulePack.approved_by",
            "post_update": True
        }
    )
    target_department: Optional["Department"] = Relationship()
    rules: List["Rule"] = Relationship(
        back_populates="rule_pack",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.scope})"
    
    @property
    def is_active(self) -> bool:
        """Check if rule pack is currently active"""
        if self.status != RulePackStatus.ACTIVE:
            return False
        
        today = datetime.now().date()
        if today < self.effective_from:
            return False
        
        if self.effective_to and today > self.effective_to:
            return False
        
        return True
    
    @property
    def rule_count(self) -> int:
        """Get number of rules in this pack"""
        return len(self.rules)


class Rule(BaseModel, table=True):
    """Individual scoring rule"""
    
    __tablename__ = "rules"
    
    # Pack Association
    rule_pack_id: int = Field(foreign_key="rule_packs.id", index=True)
    
    # Basic Info
    code: str = Field(max_length=50, index=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None)
    
    # Scoring
    direction: RuleDirection = Field(default=RuleDirection.POSITIVE)
    base_score: float = Field(default=0.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Limits and Constraints
    caps: Optional[float] = Field(default=None)  # Monthly cap per user
    min_score: Optional[float] = Field(default=None)
    max_score: Optional[float] = Field(default=None)
    
    # Requirements
    evidence_required: bool = Field(default=False)
    manager_approval_required: bool = Field(default=True)
    
    # Categorization
    category: Optional[str] = Field(default=None, max_length=50)
    tags: Optional[str] = Field(default=None)  # JSON string of tags
    
    # Status
    active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    
    # Relationships
    rule_pack: Optional["RulePack"] = Relationship(back_populates="rules")
    events: List["Event"] = Relationship(back_populates="rule")
    
    def __str__(self):
        direction_symbol = "+" if self.direction == RuleDirection.POSITIVE else "-"
        return f"{self.name} ({direction_symbol}{self.base_score})"
    
    @property
    def display_score(self) -> str:
        """Get formatted score display"""
        symbol = "+" if self.direction == RuleDirection.POSITIVE else "-"
        return f"{symbol}{abs(self.base_score)}"
    
    @property
    def tag_list(self) -> List[str]:
        """Get tags as list"""
        if not self.tags:
            return []
        try:
            import json
            return json.loads(self.tags)
        except:
            return []


class RulePackCreate(SQLModel):
    """Rule pack creation schema"""
    name: str = Field(max_length=100)
    description: Optional[str] = None
    scope: RulePackScope = RulePackScope.COMPANY
    target_department_id: Optional[int] = None
    target_role: Optional[str] = Field(default=None, max_length=50)
    effective_from: date = Field(default_factory=lambda: datetime.now().date())
    effective_to: Optional[date] = None
    weight_config: Optional[Dict[str, Any]] = None


class RulePackUpdate(SQLModel):
    """Rule pack update schema"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    target_department_id: Optional[int] = None
    target_role: Optional[str] = Field(default=None, max_length=50)
    status: Optional[RulePackStatus] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    weight_config: Optional[Dict[str, Any]] = None


class RuleCreate(SQLModel):
    """Rule creation schema"""
    rule_pack_id: int
    code: str = Field(max_length=50)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    direction: RuleDirection = RuleDirection.POSITIVE
    base_score: float = Field(default=0.0)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    caps: Optional[float] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    evidence_required: bool = Field(default=False)
    manager_approval_required: bool = Field(default=True)
    category: Optional[str] = Field(default=None, max_length=50)
    tags: Optional[str] = None


class RuleUpdate(SQLModel):
    """Rule update schema"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    direction: Optional[RuleDirection] = None
    base_score: Optional[float] = None
    weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    caps: Optional[float] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    evidence_required: Optional[bool] = None
    manager_approval_required: Optional[bool] = None
    category: Optional[str] = Field(default=None, max_length=50)
    tags: Optional[str] = None
    active: Optional[bool] = None
    sort_order: Optional[int] = None


class RulePackRead(SQLModel):
    """Rule pack read schema"""
    id: int
    name: str
    description: Optional[str]
    version: str
    scope: RulePackScope
    target_department_id: Optional[int]
    target_role: Optional[str]
    status: RulePackStatus
    effective_from: date
    effective_to: Optional[date]
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    
    # Additional info
    creator_name: Optional[str] = None
    approver_name: Optional[str] = None
    target_department_name: Optional[str] = None
    rule_count: int = 0
    is_active: bool = False


class RuleRead(SQLModel):
    """Rule read schema"""
    id: int
    rule_pack_id: int
    code: str
    name: str
    description: Optional[str]
    direction: RuleDirection
    base_score: float
    weight: float
    caps: Optional[float]
    min_score: Optional[float]
    max_score: Optional[float]
    evidence_required: bool
    manager_approval_required: bool
    category: Optional[str]
    tags: Optional[str]
    active: bool
    sort_order: int
    
    # Additional info
    display_score: str = ""
    tag_list: List[str] = []
    usage_count: int = 0