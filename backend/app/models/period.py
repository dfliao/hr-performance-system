"""
Period model - Scoring calculation periods
"""

from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

from app.models.base import BaseModel


class PeriodType(str, Enum):
    """Period type enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Period(BaseModel, table=True):
    """Scoring calculation period"""
    
    __tablename__ = "periods"
    
    # Period Definition
    type: PeriodType = Field(index=True)
    year: int = Field(index=True)
    month: Optional[int] = Field(default=None, index=True)  # For monthly periods
    quarter: Optional[int] = Field(default=None, index=True)  # For quarterly periods
    
    # Date Range
    start_date: date = Field(index=True)
    end_date: date = Field(index=True)
    
    # Status
    is_locked: bool = Field(default=False)
    locked_by: Optional[int] = Field(default=None, foreign_key="users.id")
    locked_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    name: str = Field(max_length=50)  # e.g., "2024-01", "2024-Q1", "2024"
    description: Optional[str] = Field(default=None)
    
    def __str__(self):
        return self.name
    
    @property
    def is_current(self) -> bool:
        """Check if this period is current"""
        today = datetime.now().date()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_past(self) -> bool:
        """Check if this period is in the past"""
        today = datetime.now().date()
        return self.end_date < today
    
    @property
    def is_future(self) -> bool:
        """Check if this period is in the future"""
        today = datetime.now().date()
        return self.start_date > today
    
    @classmethod
    def generate_monthly_period(cls, year: int, month: int) -> "Period":
        """Generate a monthly period"""
        from calendar import monthrange
        
        start_date = date(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = date(year, month, last_day)
        
        return cls(
            type=PeriodType.MONTHLY,
            year=year,
            month=month,
            start_date=start_date,
            end_date=end_date,
            name=f"{year}-{month:02d}"
        )
    
    @classmethod
    def generate_quarterly_period(cls, year: int, quarter: int) -> "Period":
        """Generate a quarterly period"""
        quarter_months = {
            1: (1, 3),   # Q1: Jan-Mar
            2: (4, 6),   # Q2: Apr-Jun
            3: (7, 9),   # Q3: Jul-Sep
            4: (10, 12)  # Q4: Oct-Dec
        }
        
        start_month, end_month = quarter_months[quarter]
        start_date = date(year, start_month, 1)
        
        from calendar import monthrange
        _, last_day = monthrange(year, end_month)
        end_date = date(year, end_month, last_day)
        
        return cls(
            type=PeriodType.QUARTERLY,
            year=year,
            quarter=quarter,
            start_date=start_date,
            end_date=end_date,
            name=f"{year}-Q{quarter}"
        )
    
    @classmethod
    def generate_yearly_period(cls, year: int) -> "Period":
        """Generate a yearly period"""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        return cls(
            type=PeriodType.YEARLY,
            year=year,
            start_date=start_date,
            end_date=end_date,
            name=str(year)
        )


class PeriodCreate(SQLModel):
    """Period creation schema"""
    type: PeriodType
    year: int
    month: Optional[int] = None
    quarter: Optional[int] = None
    start_date: date
    end_date: date
    name: str = Field(max_length=50)
    description: Optional[str] = None


class PeriodUpdate(SQLModel):
    """Period update schema"""
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    is_locked: Optional[bool] = None


class PeriodRead(SQLModel):
    """Period read schema"""
    id: int
    type: PeriodType
    year: int
    month: Optional[int]
    quarter: Optional[int]
    start_date: date
    end_date: date
    is_locked: bool
    locked_by: Optional[int]
    locked_at: Optional[datetime]
    name: str
    description: Optional[str]
    created_at: datetime
    
    # Additional info
    locked_by_name: Optional[str] = None
    is_current: bool = False
    is_past: bool = False
    is_future: bool = False
    event_count: int = 0
    user_count: int = 0