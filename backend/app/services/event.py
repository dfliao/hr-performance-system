"""
Event management service - Business logic for performance events
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, date
from sqlmodel import Session, select, and_
from fastapi import HTTPException, status

from app.models import (
    Event, EventCreate, EventUpdate, EventRead, EventApproval, EventStatus, EventSource,
    User, Rule, Department, Project, AuditLog, AuditAction, AuditEntityType
)
from app.services.audit import AuditService


class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    async def create_event(self, event_data: EventCreate, reporter: User) -> Event:
        """Create a new performance event"""
        
        # Validate user exists
        target_user = self.db.get(User, event_data.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目標使用者不存在"
            )
        
        # Validate rule exists
        rule = self.db.get(Rule, event_data.rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="規則不存在"
            )
        
        if not rule.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="規則已停用"
            )
        
        # Calculate period information
        occurred_date = event_data.occurred_at
        period_year = occurred_date.year
        period_month = occurred_date.month
        period_quarter = (occurred_date.month - 1) // 3 + 1
        
        # Calculate score
        original_score = rule.base_score * rule.weight
        
        # Determine department (use target user's department if not specified)
        department_id = event_data.department_id or target_user.department_id
        
        # Create event
        event = Event(
            user_id=event_data.user_id,
            reporter_id=reporter.id,
            department_id=department_id,
            project_id=event_data.project_id,
            rule_id=event_data.rule_id,
            original_score=original_score,
            final_score=original_score,
            occurred_at=occurred_date,
            title=event_data.title,
            description=event_data.description,
            evidence_urls=event_data.evidence_urls or [],
            evidence_count=len(event_data.evidence_urls or []),
            source=event_data.source,
            external_id=event_data.external_id,
            source_metadata=event_data.source_metadata,
            period_year=period_year,
            period_month=period_month,
            period_quarter=period_quarter,
            status=EventStatus.PENDING if reporter.role == "employee" else EventStatus.APPROVED
        )
        
        # Check if evidence is required but missing
        if rule.evidence_required and event.evidence_count == 0:
            if reporter.role == "employee":
                event.status = EventStatus.DRAFT
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="此規則需要提供證據檔案"
                )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Log audit trail
        await self.audit_service.log_action(
            actor=reporter,
            action=AuditAction.CREATE,
            entity_type=AuditEntityType.EVENT,
            entity_id=event.id,
            entity_name=f"Event #{event.id}",
            description=f"建立績效事件: {event.title or rule.name}"
        )
        
        return event

    async def update_event(self, event: Event, event_data: EventUpdate, user: User) -> Event:
        """Update an existing event"""
        
        old_values = {
            "title": event.title,
            "description": event.description,
            "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
            "evidence_urls": event.evidence_urls
        }
        
        # Update fields
        if event_data.title is not None:
            event.title = event_data.title
        
        if event_data.description is not None:
            event.description = event_data.description
        
        if event_data.occurred_at is not None:
            event.occurred_at = event_data.occurred_at
            # Recalculate period info
            event.period_year = event_data.occurred_at.year
            event.period_month = event_data.occurred_at.month
            event.period_quarter = (event_data.occurred_at.month - 1) // 3 + 1
        
        if event_data.evidence_urls is not None:
            event.evidence_urls = event_data.evidence_urls
            event.evidence_count = len(event_data.evidence_urls)
        
        if event_data.adjusted_score is not None and user.role in ["manager", "admin"]:
            event.adjusted_score = event_data.adjusted_score
            event.adjustment_reason = event_data.adjustment_reason
            event.final_score = event_data.adjusted_score
        
        if event_data.source_metadata is not None:
            event.source_metadata = event_data.source_metadata
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        new_values = {
            "title": event.title,
            "description": event.description,
            "occurred_at": event.occurred_at.isoformat() if event.occurred_at else None,
            "evidence_urls": event.evidence_urls
        }
        
        # Log audit trail
        await self.audit_service.log_action(
            actor=user,
            action=AuditAction.UPDATE,
            entity_type=AuditEntityType.EVENT,
            entity_id=event.id,
            entity_name=f"Event #{event.id}",
            old_values=old_values,
            new_values=new_values,
            description="更新績效事件"
        )
        
        return event

    async def approve_event(self, event: Event, approval_data: EventApproval, reviewer: User) -> Event:
        """Approve or reject an event"""
        
        old_status = event.status
        event.status = approval_data.status
        event.reviewed_by = reviewer.id
        event.reviewed_at = datetime.utcnow()
        event.review_notes = approval_data.review_notes
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Log audit trail
        action_description = "核准事件" if approval_data.status == EventStatus.APPROVED else "拒絕事件"
        await self.audit_service.log_action(
            actor=reviewer,
            action=AuditAction.APPROVE if approval_data.status == EventStatus.APPROVED else AuditAction.REJECT,
            entity_type=AuditEntityType.EVENT,
            entity_id=event.id,
            entity_name=f"Event #{event.id}",
            old_values={"status": old_status},
            new_values={"status": event.status},
            description=f"{action_description}: {approval_data.review_notes or 'No notes'}"
        )
        
        return event

    async def delete_event(self, event: Event, user: User) -> None:
        """Delete an event"""
        
        # Log audit trail before deletion
        await self.audit_service.log_action(
            actor=user,
            action=AuditAction.DELETE,
            entity_type=AuditEntityType.EVENT,
            entity_id=event.id,
            entity_name=f"Event #{event.id}",
            description="刪除績效事件"
        )
        
        self.db.delete(event)
        self.db.commit()

    def get_event_with_permission_check(self, event_id: int, user: User) -> Event:
        """Get event with permission check"""
        
        event = self.db.get(Event, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="事件不存在"
            )
        
        # Check permissions
        if user.role == "employee" and event.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="權限不足"
            )
        elif user.role == "manager" and event.department_id != user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="權限不足"
            )
        # Admins and auditors can access all events
        
        return event

    def to_read_model(self, event: Event) -> EventRead:
        """Convert Event to EventRead with additional data"""
        
        # Get related data
        user = self.db.get(User, event.user_id)
        reporter = self.db.get(User, event.reporter_id)
        reviewer = self.db.get(User, event.reviewed_by) if event.reviewed_by else None
        department = self.db.get(Department, event.department_id) if event.department_id else None
        project = self.db.get(Project, event.project_id) if event.project_id else None
        rule = self.db.get(Rule, event.rule_id)
        
        # Create EventRead model
        event_read = EventRead.from_orm(event)
        
        # Add related data
        event_read.user_name = user.name if user else None
        event_read.user_employee_id = user.employee_id if user else None
        event_read.reporter_name = reporter.name if reporter else None
        event_read.reviewer_name = reviewer.name if reviewer else None
        event_read.department_name = department.name if department else None
        event_read.project_name = project.name if project else None
        event_read.rule_name = rule.name if rule else None
        event_read.rule_code = rule.code if rule else None
        event_read.rule_category = rule.category if rule else None
        
        # Add computed properties
        event_read.is_positive = event.final_score > 0
        event_read.is_adjusted = event.adjusted_score is not None and event.adjusted_score != event.original_score
        event_read.needs_evidence = rule.evidence_required if rule else False
        event_read.has_sufficient_evidence = event.evidence_count > 0
        event_read.can_approve = (
            event.status == EventStatus.PENDING and
            event_read.has_sufficient_evidence
        )
        event_read.period_key = f"{event.period_year}-{event.period_month:02d}"
        event_read.quarter_key = f"{event.period_year}-Q{event.period_quarter}"
        
        return event_read

    async def get_events_summary(self, user: User, year: int, month: int) -> Dict[str, Any]:
        """Get events summary for a specific period"""
        
        # Build base query
        statement = select(Event).where(
            and_(
                Event.period_year == year,
                Event.period_month == month
            )
        )
        
        # Apply role-based filters
        if user.role == "employee":
            statement = statement.where(Event.user_id == user.id)
        elif user.role == "manager" and user.department_id:
            statement = statement.where(Event.department_id == user.department_id)
        
        events = self.db.exec(statement).all()
        
        # Calculate summary statistics
        total_events = len(events)
        approved_events = sum(1 for e in events if e.status == EventStatus.APPROVED)
        pending_events = sum(1 for e in events if e.status == EventStatus.PENDING)
        rejected_events = sum(1 for e in events if e.status == EventStatus.REJECTED)
        
        total_score = sum(e.final_score for e in events if e.status == EventStatus.APPROVED)
        positive_score = sum(e.final_score for e in events if e.status == EventStatus.APPROVED and e.final_score > 0)
        negative_score = sum(e.final_score for e in events if e.status == EventStatus.APPROVED and e.final_score < 0)
        
        positive_events = sum(1 for e in events if e.status == EventStatus.APPROVED and e.final_score > 0)
        negative_events = sum(1 for e in events if e.status == EventStatus.APPROVED and e.final_score < 0)
        
        return {
            "period": f"{year}-{month:02d}",
            "total_events": total_events,
            "approved_events": approved_events,
            "pending_events": pending_events,
            "rejected_events": rejected_events,
            "total_score": round(total_score, 2),
            "positive_score": round(positive_score, 2),
            "negative_score": round(negative_score, 2),
            "positive_events": positive_events,
            "negative_events": negative_events,
            "average_score": round(total_score / approved_events, 2) if approved_events > 0 else 0
        }