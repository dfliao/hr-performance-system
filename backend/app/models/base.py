"""
Base model with common fields
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import DateTime, func, Column


class BaseModel(SQLModel):
    """Base model with common fields"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: Optional[datetime] = Field(
        default=None
    )
    
    class Config:
        from_attributes = True