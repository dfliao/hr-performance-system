"""
Score model - Calculated performance scores (cached results)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON

from app.models.base import BaseModel


class Score(BaseModel, table=True):
    """Calculated performance score for caching and reporting"""
    
    __tablename__ = "scores"
    
    # User and Period
    user_id: int = Field(foreign_key="users.id", index=True)
    period_id: int = Field(foreign_key="periods.id", index=True)
    
    # Period Info (denormalized for performance)
    period_year: int = Field(index=True)
    period_month: Optional[int] = Field(default=None, index=True)
    period_quarter: Optional[int] = Field(default=None, index=True)
    period_type: str = Field(max_length=20, index=True)  # monthly/quarterly/yearly
    
    # Department Info (denormalized)
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id", index=True)
    
    # Scores
    total_score: float = Field(default=0.0, index=True)
    positive_score: float = Field(default=0.0)
    negative_score: float = Field(default=0.0)
    adjusted_score: float = Field(default=0.0)  # Total manager adjustments
    
    # Event Statistics
    total_events: int = Field(default=0)
    positive_events: int = Field(default=0)
    negative_events: int = Field(default=0)
    pending_events: int = Field(default=0)
    
    # Rule Breakdown
    rule_breakdown: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column_kwargs={"type_": JSON},
        description="Breakdown by rule categories and individual rules"
    )
    
    # Rankings
    rank_department: Optional[int] = Field(default=None, index=True)
    rank_company: Optional[int] = Field(default=None, index=True)
    percentile_department: Optional[float] = Field(default=None)
    percentile_company: Optional[float] = Field(default=None)
    
    # Comparison with Previous Period
    previous_total_score: Optional[float] = Field(default=None)
    score_change: Optional[float] = Field(default=None)
    score_change_percent: Optional[float] = Field(default=None)
    
    # Metadata
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    events_computed_count: int = Field(default=0)  # Number of events included in calculation
    computation_version: str = Field(default="1.0", max_length=10)  # For tracking calculation changes
    
    # Flags
    is_locked: bool = Field(default=False)  # Period locked
    has_adjustments: bool = Field(default=False)  # Has manager adjustments
    needs_recalculation: bool = Field(default=False)  # Needs recalculation due to rule changes
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="scores")
    period: Optional["Period"] = Relationship()
    department: Optional["Department"] = Relationship()
    
    def __str__(self):
        period_str = f"{self.period_year}"
        if self.period_month:
            period_str += f"-{self.period_month:02d}"
        elif self.period_quarter:
            period_str += f"-Q{self.period_quarter}"
        
        return f"{self.user.name if self.user else 'Unknown'} - {period_str}: {self.total_score}"
    
    @property
    def score_grade(self) -> str:
        """Get score grade based on total score"""
        if self.total_score >= 90:
            return "A+"
        elif self.total_score >= 80:
            return "A"
        elif self.total_score >= 70:
            return "B+"
        elif self.total_score >= 60:
            return "B"
        elif self.total_score >= 50:
            return "C+"
        elif self.total_score >= 40:
            return "C"
        else:
            return "D"
    
    @property
    def is_improvement(self) -> Optional[bool]:
        """Check if score improved from previous period"""
        if self.score_change is None:
            return None
        return self.score_change > 0
    
    @property
    def performance_trend(self) -> str:
        """Get performance trend indicator"""
        if self.score_change is None:
            return "new"
        elif self.score_change > 5:
            return "improving"
        elif self.score_change < -5:
            return "declining"
        else:
            return "stable"
    
    @property
    def positive_ratio(self) -> float:
        """Get ratio of positive events"""
        if self.total_events == 0:
            return 0.0
        return self.positive_events / self.total_events
    
    @property
    def period_key(self) -> str:
        """Get period key for grouping"""
        if self.period_month:
            return f"{self.period_year}-{self.period_month:02d}"
        elif self.period_quarter:
            return f"{self.period_year}-Q{self.period_quarter}"
        else:
            return str(self.period_year)


class ScoreCreate(SQLModel):
    """Score creation schema"""
    user_id: int
    period_id: int
    period_year: int
    period_month: Optional[int] = None
    period_quarter: Optional[int] = None
    period_type: str = Field(max_length=20)
    department_id: Optional[int] = None
    total_score: float = Field(default=0.0)
    positive_score: float = Field(default=0.0)
    negative_score: float = Field(default=0.0)
    adjusted_score: float = Field(default=0.0)
    total_events: int = Field(default=0)
    positive_events: int = Field(default=0)
    negative_events: int = Field(default=0)
    pending_events: int = Field(default=0)
    rule_breakdown: Optional[Dict[str, Any]] = None
    events_computed_count: int = Field(default=0)


class ScoreUpdate(SQLModel):
    """Score update schema"""
    total_score: Optional[float] = None
    positive_score: Optional[float] = None
    negative_score: Optional[float] = None
    adjusted_score: Optional[float] = None
    total_events: Optional[int] = None
    positive_events: Optional[int] = None
    negative_events: Optional[int] = None
    pending_events: Optional[int] = None
    rule_breakdown: Optional[Dict[str, Any]] = None
    rank_department: Optional[int] = None
    rank_company: Optional[int] = None
    percentile_department: Optional[float] = None
    percentile_company: Optional[float] = None
    previous_total_score: Optional[float] = None
    score_change: Optional[float] = None
    score_change_percent: Optional[float] = None
    events_computed_count: Optional[int] = None
    has_adjustments: Optional[bool] = None
    needs_recalculation: Optional[bool] = None


class ScoreRead(SQLModel):
    """Score read schema"""
    id: int
    user_id: int
    period_id: int
    period_year: int
    period_month: Optional[int]
    period_quarter: Optional[int]
    period_type: str
    department_id: Optional[int]
    total_score: float
    positive_score: float
    negative_score: float
    adjusted_score: float
    total_events: int
    positive_events: int
    negative_events: int
    pending_events: int
    rule_breakdown: Optional[Dict[str, Any]]
    rank_department: Optional[int]
    rank_company: Optional[int]
    percentile_department: Optional[float]
    percentile_company: Optional[float]
    previous_total_score: Optional[float]
    score_change: Optional[float]
    score_change_percent: Optional[float]
    computed_at: datetime
    events_computed_count: int
    computation_version: str
    is_locked: bool
    has_adjustments: bool
    needs_recalculation: bool
    
    # Related data
    user_name: Optional[str] = None
    user_employee_id: Optional[str] = None
    department_name: Optional[str] = None
    period_name: Optional[str] = None
    
    # Computed properties
    score_grade: str = ""
    is_improvement: Optional[bool] = None
    performance_trend: str = ""
    positive_ratio: float = 0.0
    period_key: str = ""


class ScoreRanking(SQLModel):
    """Score ranking for leaderboards"""
    user_id: int
    user_name: str
    user_employee_id: Optional[str]
    department_id: Optional[int]
    department_name: Optional[str]
    total_score: float
    rank: int
    percentile: Optional[float]
    score_change: Optional[float]
    performance_trend: str
    
    # Additional metrics
    total_events: int = 0
    positive_events: int = 0
    negative_events: int = 0
    positive_ratio: float = 0.0


class DepartmentScore(SQLModel):
    """Department aggregate score"""
    department_id: int
    department_name: str
    period_year: int
    period_month: Optional[int] = None
    period_quarter: Optional[int] = None
    
    # Aggregate metrics
    user_count: int = 0
    avg_score: float = 0.0
    max_score: float = 0.0
    min_score: float = 0.0
    total_events: int = 0
    total_positive_events: int = 0
    total_negative_events: int = 0
    
    # Rankings
    department_rank: Optional[int] = None
    
    # Top performers
    top_performer_id: Optional[int] = None
    top_performer_name: Optional[str] = None
    top_performer_score: Optional[float] = None