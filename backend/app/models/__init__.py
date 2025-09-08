"""
Database models for HR Performance Management System

Complete data model supporting:
- User management with LDAP sync
- Organizational hierarchy (departments, projects)  
- Configurable scoring rules with versioning
- Performance events with approval workflow
- Calculated scores with ranking and trends
- Period management with locking
- Complete audit trail for compliance
"""

from app.models.base import BaseModel
from app.models.user import User, UserCreate, UserUpdate, UserRead, UserStatus, UserRole
from app.models.department import Department, DepartmentCreate, DepartmentUpdate, DepartmentRead  
from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectRead, ProjectStatus
from app.models.rule_pack import (
    RulePack, RulePackCreate, RulePackUpdate, RulePackRead, RulePackScope, RulePackStatus,
    Rule, RuleCreate, RuleUpdate, RuleRead, RuleDirection
)
from app.models.event import (
    Event, EventCreate, EventUpdate, EventRead, EventApproval, EventSummary,
    EventSource, EventStatus
)
from app.models.period import Period, PeriodCreate, PeriodUpdate, PeriodRead, PeriodType
from app.models.score import (
    Score, ScoreCreate, ScoreUpdate, ScoreRead, ScoreRanking, DepartmentScore
)
from app.models.audit_log import (
    AuditLog, AuditLogCreate, AuditLogRead, AuditLogFilter, AuditSummary,
    AuditAction, AuditEntityType
)

__all__ = [
    # Base
    "BaseModel",
    
    # User management
    "User", "UserCreate", "UserUpdate", "UserRead", "UserStatus", "UserRole",
    
    # Organization  
    "Department", "DepartmentCreate", "DepartmentUpdate", "DepartmentRead",
    "Project", "ProjectCreate", "ProjectUpdate", "ProjectRead", "ProjectStatus",
    
    # Rules and scoring
    "RulePack", "RulePackCreate", "RulePackUpdate", "RulePackRead", "RulePackScope", "RulePackStatus",
    "Rule", "RuleCreate", "RuleUpdate", "RuleRead", "RuleDirection",
    
    # Events
    "Event", "EventCreate", "EventUpdate", "EventRead", "EventApproval", "EventSummary",
    "EventSource", "EventStatus",
    
    # Periods and scores
    "Period", "PeriodCreate", "PeriodUpdate", "PeriodRead", "PeriodType",
    "Score", "ScoreCreate", "ScoreUpdate", "ScoreRead", "ScoreRanking", "DepartmentScore",
    
    # Audit and compliance
    "AuditLog", "AuditLogCreate", "AuditLogRead", "AuditLogFilter", "AuditSummary",
    "AuditAction", "AuditEntityType"
]