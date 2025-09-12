"""
Event model - Performance events with scoring
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from enum import Enum

from app.models.base import BaseModel


class EventSource(str, Enum):
    """Event source enumeration"""
    MANUAL = "manual"
    REDMINE = "redmine"
    N8N = "n8n"
    NOTE_STATION = "note"
    API = "api"


class EventStatus(str, Enum):
    """Event status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Event(BaseModel, table=True):
    """Performance event model"""
    
    __tablename__ = "events"
    
    # People
    user_id: int = Field(foreign_key="users.id", index=True)  # Person being evaluated
    reporter_id: int = Field(foreign_key="users.id", index=True)  # Person reporting the event
    
    # Organization Context
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id", index=True)
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id", index=True)
    
    # Rule and Scoring
    rule_id: int = Field(foreign_key="rules.id", index=True)
    original_score: float = Field(default=0.0)  # Original score from rule
    adjusted_score: Optional[float] = Field(default=None)  # Manager-adjusted score
    final_score: float = Field(default=0.0)  # Final calculated score
    adjustment_reason: Optional[str] = Field(default=None)
    
    # Event Details
    occurred_at: date = Field(index=True)  # When the event happened
    title: Optional[str] = Field(default=None, max_length=200)
    description: str = Field(max_length=1000)
    
    # Evidence and Documentation
    evidence_urls: Optional[List[str]] = Field(default=None, sa_column_kwargs={"type_": JSON})
    evidence_count: int = Field(default=0)
    
    # Source and Metadata
    source: EventSource = Field(default=EventSource.MANUAL)
    external_id: Optional[str] = Field(default=None, max_length=100, index=True)  # For integration tracking
    source_metadata: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"type_": JSON})
    
    # Workflow
    status: EventStatus = Field(default=EventStatus.PENDING)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    reviewed_at: Optional[datetime] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)
    
    # Performance Tracking
    is_locked: bool = Field(default=False)  # For period locking
    period_year: int = Field(index=True)
    period_month: int = Field(index=True)
    period_quarter: int = Field(index=True)
    
    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="events_received",
        sa_relationship_kwargs={"foreign_keys": "Event.user_id"}
    )
    reporter: Optional["User"] = Relationship(
        back_populates="events_reported", 
        sa_relationship_kwargs={"foreign_keys": "Event.reporter_id"}
    )
    reviewer: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Event.reviewed_by",
            "post_update": True
        }
    )
    department: Optional["Department"] = Relationship(back_populates="events")
    project: Optional["Project"] = Relationship(back_populates="events")
    rule: Optional["Rule"] = Relationship(back_populates="events")
    
    def __str__(self):
        return f"Event #{self.id}: {self.user.name if self.user else 'Unknown'} - {self.rule.name if self.rule else 'Unknown Rule'}"
    
    @property
    def is_positive(self) -> bool:
        """Check if event has positive score"""
        return self.final_score > 0
    
    @property
    def is_adjusted(self) -> bool:
        """Check if score was adjusted by manager"""
        return self.adjusted_score is not None and self.adjusted_score != self.original_score
    
    @property
    def needs_evidence(self) -> bool:
        """Check if event requires evidence"""
        return self.rule.evidence_required if self.rule else False
    
    @property
    def has_sufficient_evidence(self) -> bool:
        """Check if event has sufficient evidence"""
        if not self.needs_evidence:
            return True
        return self.evidence_count > 0
    
    @property
    def can_approve(self) -> bool:
        """Check if event can be approved"""
        return (
            self.status == EventStatus.PENDING and
            self.has_sufficient_evidence
        )
    
    @property
    def period_key(self) -> str:
        """Get period key for grouping"""
        return f"{self.period_year}-{self.period_month:02d}"
    
    @property
    def quarter_key(self) -> str:
        """Get quarter key for grouping"""
        return f"{self.period_year}-Q{self.period_quarter}"


class EventCreate(SQLModel):
    """Event creation schema"""
    user_id: int
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    rule_id: int
    occurred_at: date = Field(default_factory=lambda: datetime.now().date())
    title: Optional[str] = Field(default=None, max_length=200)
    description: str = Field(max_length=1000)
    evidence_urls: Optional[List[str]] = None
    source: EventSource = EventSource.MANUAL
    external_id: Optional[str] = Field(default=None, max_length=100)
    source_metadata: Optional[Dict[str, Any]] = None


class EventUpdate(SQLModel):
    """Event update schema"""
    user_id: Optional[int] = None
    department_id: Optional[int] = None
    project_id: Optional[int] = None
    rule_id: Optional[int] = None
    occurred_at: Optional[date] = None
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    evidence_urls: Optional[List[str]] = None
    adjusted_score: Optional[float] = None
    adjustment_reason: Optional[str] = None
    source_metadata: Optional[Dict[str, Any]] = None


class EventApproval(SQLModel):
    """Event approval schema"""
    status: EventStatus = Field(..., description="New status (approved/rejected)")
    review_notes: Optional[str] = Field(default=None, max_length=500)


class EventRead(SQLModel):
    """Event read schema"""
    id: int
    user_id: int
    reporter_id: int
    department_id: Optional[int]
    project_id: Optional[int]
    rule_id: int
    original_score: float
    adjusted_score: Optional[float]
    final_score: float
    adjustment_reason: Optional[str]
    occurred_at: date
    title: Optional[str]
    description: str
    evidence_urls: Optional[List[str]]
    evidence_count: int
    source: EventSource
    external_id: Optional[str]
    status: EventStatus
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    is_locked: bool
    period_year: int
    period_month: int
    period_quarter: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    user_name: Optional[str] = None
    user_employee_id: Optional[str] = None
    reporter_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    department_name: Optional[str] = None
    project_name: Optional[str] = None
    rule_name: Optional[str] = None
    rule_code: Optional[str] = None
    rule_category: Optional[str] = None
    
    # Computed properties
    is_positive: bool = False
    is_adjusted: bool = False
    needs_evidence: bool = False
    has_sufficient_evidence: bool = True
    can_approve: bool = False
    period_key: str = ""
    quarter_key: str = ""


class EventSummary(SQLModel):
    """Event summary for reports"""
    user_id: int
    user_name: str
    department_id: Optional[int]
    department_name: Optional[str]
    period_year: int
    period_month: int
    period_quarter: int
    
    total_events: int = 0
    positive_events: int = 0
    negative_events: int = 0
    pending_events: int = 0
    
    total_score: float = 0.0
    positive_score: float = 0.0
    negative_score: float = 0.0
    
    evidence_required_count: int = 0
    evidence_provided_count: int = 0