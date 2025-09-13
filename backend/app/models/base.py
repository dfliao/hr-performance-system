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
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, onupdate=func.now())
    )
    
    class Config:
        from_attributes = True