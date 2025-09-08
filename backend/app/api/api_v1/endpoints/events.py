"""
Event management endpoints - Complete implementation
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlmodel import Session, select, and_, or_

from app.core.database import get_db
from app.models import (
    Event, EventCreate, EventUpdate, EventRead, EventApproval, EventStatus,
    User, Rule, Department, Project, AuditLog, AuditAction, AuditEntityType
)
from app.services.auth import get_current_user
from app.services.event import EventService
from app.services.file import FileService

router = APIRouter()


@router.get("/", response_model=List[EventRead])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[EventStatus] = None,
    user_id: Optional[int] = None,
    department_id: Optional[int] = None,
    project_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[EventRead]:
    """
    Get events list with filtering and pagination
    """
    statement = select(Event)
    
    # Apply role-based filters
    if current_user.role == "employee":
        # Employees can only see their own events
        statement = statement.where(Event.user_id == current_user.id)
    elif current_user.role == "manager":
        # Managers can see events in their department
        if current_user.department_id:
            statement = statement.where(Event.department_id == current_user.department_id)
    # Admins and auditors can see all events
    
    # Apply additional filters
    if status_filter:
        statement = statement.where(Event.status == status_filter)
    
    if user_id and current_user.role in ["admin", "auditor", "manager"]:
        statement = statement.where(Event.user_id == user_id)
    
    if department_id and current_user.role in ["admin", "auditor"]:
        statement = statement.where(Event.department_id == department_id)
    
    if project_id:
        statement = statement.where(Event.project_id == project_id)
    
    if date_from:
        statement = statement.where(Event.occurred_at >= date_from)
    
    if date_to:
        statement = statement.where(Event.occurred_at <= date_to)
    
    if search:
        statement = statement.where(
            or_(
                Event.title.contains(search),
                Event.description.contains(search)
            )
        )
    
    # Order by most recent first
    statement = statement.order_by(Event.created_at.desc())
    statement = statement.offset(skip).limit(limit)
    
    events = db.exec(statement).all()
    
    # Convert to EventRead with additional data
    event_service = EventService(db)
    return [event_service.to_read_model(event) for event in events]


@router.post("/", response_model=EventRead)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EventRead:
    """
    Create new performance event
    """
    # Check permissions
    if current_user.role == "employee" and event_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="員工只能為自己建立事件"
        )
    
    event_service = EventService(db)
    event = await event_service.create_event(event_data, current_user)
    
    return event_service.to_read_model(event)


@router.get("/{event_id}", response_model=EventRead)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EventRead:
    """
    Get event by ID with permission check
    """
    event_service = EventService(db)
    event = event_service.get_event_with_permission_check(event_id, current_user)
    
    return event_service.to_read_model(event)


@router.patch("/{event_id}", response_model=EventRead)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EventRead:
    """
    Update event (only if not locked and has permission)
    """
    event_service = EventService(db)
    event = event_service.get_event_with_permission_check(event_id, current_user)
    
    # Check if event can be modified
    if event.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="事件已鎖定，無法修改"
        )
    
    if event.status == EventStatus.APPROVED and current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已核准的事件無法修改"
        )
    
    updated_event = await event_service.update_event(event, event_data, current_user)
    return event_service.to_read_model(updated_event)


@router.post("/{event_id}/approve", response_model=EventRead)
async def approve_event(
    event_id: int,
    approval_data: EventApproval,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> EventRead:
    """
    Approve or reject event (manager/admin only)
    """
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足，無法審核事件"
        )
    
    event_service = EventService(db)
    event = event_service.get_event_with_permission_check(event_id, current_user)
    
    if event.status != EventStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能審核待審核狀態的事件"
        )
    
    approved_event = await event_service.approve_event(event, approval_data, current_user)
    return event_service.to_read_model(approved_event)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete event (admin only, or creator if still draft)
    """
    event_service = EventService(db)
    event = event_service.get_event_with_permission_check(event_id, current_user)
    
    # Check deletion permissions
    if current_user.role != "admin":
        if event.reporter_id != current_user.id or event.status != EventStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能刪除自己建立的草稿事件"
            )
    
    if event.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="事件已鎖定，無法刪除"
        )
    
    await event_service.delete_event(event, current_user)
    
    return {"message": "事件已刪除"}


@router.post("/{event_id}/evidence")
async def upload_evidence(
    event_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Upload evidence files for event
    """
    event_service = EventService(db)
    event = event_service.get_event_with_permission_check(event_id, current_user)
    
    if event.status == EventStatus.APPROVED and current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已核准的事件無法新增證據檔案"
        )
    
    file_service = FileService()
    uploaded_urls = []
    
    for file in files:
        # Validate file
        if not file_service.is_allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支援的檔案類型: {file.filename}"
            )
        
        if file.size > file_service.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"檔案過大: {file.filename}"
            )
        
        # Upload file
        file_url = await file_service.upload_evidence_file(file, event_id, current_user.id)
        uploaded_urls.append(file_url)
    
    # Update event with new evidence URLs
    current_evidence = event.evidence_urls or []
    event.evidence_urls = current_evidence + uploaded_urls
    event.evidence_count = len(event.evidence_urls)
    
    db.add(event)
    db.commit()
    
    return {
        "message": f"已上傳 {len(uploaded_urls)} 個檔案",
        "uploaded_files": uploaded_urls
    }


@router.get("/stats/summary")
async def get_events_summary(
    period: Optional[str] = Query(None, description="YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get events summary statistics
    """
    event_service = EventService(db)
    
    # Default to current month if no period specified
    if not period:
        period = datetime.now().strftime("%Y-%m")
    
    try:
        year, month = map(int, period.split("-"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="期間格式錯誤，請使用 YYYY-MM 格式"
        )
    
    summary = await event_service.get_events_summary(current_user, year, month)
    
    return summary