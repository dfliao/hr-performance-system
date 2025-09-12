"""
Audit Log model - Complete operation tracking for compliance
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum

from app.models.base import BaseModel


class AuditAction(str, Enum):
    """Audit action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"
    LOCK = "lock"
    UNLOCK = "unlock"
    CALCULATE = "calculate"


class AuditEntityType(str, Enum):
    """Audit entity type enumeration"""
    USER = "user"
    DEPARTMENT = "department"
    PROJECT = "project"
    RULE_PACK = "rule_pack"
    RULE = "rule"
    EVENT = "event"
    PERIOD = "period"
    SCORE = "score"
    REPORT = "report"
    FILE = "file"
    SYSTEM = "system"


class AuditLog(BaseModel, table=True):
    """Audit log for tracking all system operations"""
    
    __tablename__ = "audit_logs"
    
    # Actor Information
    actor_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    actor_username: Optional[str] = Field(default=None, max_length=50)
    actor_ip: Optional[str] = Field(default=None, max_length=45)  # IPv6 support
    actor_user_agent: Optional[str] = Field(default=None, max_length=500)
    
    # Action Details
    action: AuditAction = Field(index=True)
    entity_type: AuditEntityType = Field(index=True)
    entity_id: Optional[int] = Field(default=None, index=True)
    entity_name: Optional[str] = Field(default=None, max_length=200)
    
    # Change Details
    old_values: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column_kwargs={"type_": JSON},
        description="Previous values before change"
    )
    new_values: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column_kwargs={"type_": JSON}, 
        description="New values after change"
    )
    diff: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column_kwargs={"type_": JSON},
        description="Computed difference between old and new values"
    )
    
    # Context and Metadata
    description: Optional[str] = Field(default=None, max_length=500)
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column_kwargs={"type_": JSON},
        description="Additional context and metadata"
    )
    
    # Request Information
    request_method: Optional[str] = Field(default=None, max_length=10)  # GET, POST, etc.
    request_path: Optional[str] = Field(default=None, max_length=500)
    request_id: Optional[str] = Field(default=None, max_length=50, index=True)
    session_id: Optional[str] = Field(default=None, max_length=100, index=True)
    
    # Outcome
    success: bool = Field(default=True, index=True)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    
    # Performance
    execution_time_ms: Optional[int] = Field(default=None)
    
    # Risk Assessment
    risk_score: int = Field(default=0, ge=0, le=100)  # 0=Low, 100=Critical
    is_sensitive: bool = Field(default=False, index=True)
    requires_review: bool = Field(default=False, index=True)
    
    # Note: Using created_at from BaseModel as the timestamp
    
    # Relationships
    actor: Optional["User"] = Relationship(back_populates="audit_logs")
    
    def __str__(self):
        actor_str = self.actor_username or f"User#{self.actor_id}" or "System"
        return f"{actor_str} {self.action} {self.entity_type}#{self.entity_id} at {self.created_at}"
    
    @property
    def risk_level(self) -> str:
        """Get risk level based on risk score"""
        if self.risk_score >= 80:
            return "critical"
        elif self.risk_score >= 60:
            return "high"
        elif self.risk_score >= 40:
            return "medium"
        elif self.risk_score >= 20:
            return "low"
        else:
            return "minimal"
    
    @property
    def has_changes(self) -> bool:
        """Check if this audit log contains actual changes"""
        return bool(self.diff and len(self.diff) > 0)
    
    @property
    def affected_fields(self) -> list:
        """Get list of affected fields"""
        if not self.diff:
            return []
        return list(self.diff.keys())


class AuditLogCreate(SQLModel):
    """Audit log creation schema"""
    actor_id: Optional[int] = None
    actor_username: Optional[str] = Field(default=None, max_length=50)
    actor_ip: Optional[str] = Field(default=None, max_length=45)
    actor_user_agent: Optional[str] = Field(default=None, max_length=500)
    action: AuditAction
    entity_type: AuditEntityType
    entity_id: Optional[int] = None
    entity_name: Optional[str] = Field(default=None, max_length=200)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    diff: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(default=None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    request_method: Optional[str] = Field(default=None, max_length=10)
    request_path: Optional[str] = Field(default=None, max_length=500)
    request_id: Optional[str] = Field(default=None, max_length=50)
    session_id: Optional[str] = Field(default=None, max_length=100)
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    execution_time_ms: Optional[int] = None
    risk_score: int = Field(default=0, ge=0, le=100)
    is_sensitive: bool = Field(default=False)
    requires_review: bool = Field(default=False)


class AuditLogRead(SQLModel):
    """Audit log read schema"""
    id: int
    actor_id: Optional[int]
    actor_username: Optional[str]
    actor_ip: Optional[str]
    action: AuditAction
    entity_type: AuditEntityType
    entity_id: Optional[int]
    entity_name: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    diff: Optional[Dict[str, Any]]
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    request_method: Optional[str]
    request_path: Optional[str]
    request_id: Optional[str]
    session_id: Optional[str]
    success: bool
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    risk_score: int
    is_sensitive: bool
    requires_review: bool
    created_at: datetime
    
    # Related data
    actor_name: Optional[str] = None
    actor_email: Optional[str] = None
    
    # Computed properties
    risk_level: str = ""
    has_changes: bool = False
    affected_fields: list = []


class AuditLogFilter(SQLModel):
    """Audit log filter schema"""
    actor_id: Optional[int] = None
    actor_username: Optional[str] = None
    action: Optional[AuditAction] = None
    entity_type: Optional[AuditEntityType] = None
    entity_id: Optional[int] = None
    success: Optional[bool] = None
    is_sensitive: Optional[bool] = None
    requires_review: Optional[bool] = None
    risk_score_min: Optional[int] = Field(default=None, ge=0, le=100)
    risk_score_max: Optional[int] = Field(default=None, ge=0, le=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Pagination
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    
    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")  # asc or desc


class AuditSummary(SQLModel):
    """Audit summary for dashboards"""
    total_logs: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    sensitive_actions: int = 0
    actions_requiring_review: int = 0
    
    # By time period
    today_count: int = 0
    this_week_count: int = 0
    this_month_count: int = 0
    
    # By risk level
    critical_count: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    
    # By action type
    create_count: int = 0
    update_count: int = 0
    delete_count: int = 0
    login_count: int = 0
    export_count: int = 0
    
    # Top actors
    most_active_users: list = []
    most_frequent_actions: list = []
    most_affected_entities: list = []