"""
Event management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_db
from app.models import Event, EventRead
from app.services.auth import get_current_user
from app.models import User

router = APIRouter()


@router.get("/", response_model=List[EventRead])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Event]:
    """
    Get events list
    """
    statement = select(Event)
    
    # Apply filters based on user role
    if current_user.role == "employee":
        # Employees can only see their own events
        statement = statement.where(Event.user_id == current_user.id)
    elif current_user.role == "manager":
        # Managers can see events in their department
        if current_user.department_id:
            statement = statement.where(Event.department_id == current_user.department_id)
    # Admins and auditors can see all events
    
    # Apply status filter
    if status_filter:
        statement = statement.where(Event.status == status_filter)
    
    statement = statement.offset(skip).limit(limit)
    events = db.exec(statement).all()
    return events


@router.get("/{event_id}", response_model=EventRead)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Event:
    """
    Get event by ID
    """
    statement = select(Event).where(Event.id == event_id)
    event = db.exec(statement).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="事件不存在"
        )
    
    # Check permissions
    if current_user.role == "employee" and event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足"
        )
    elif current_user.role == "manager" and event.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="權限不足"
        )
    
    return event