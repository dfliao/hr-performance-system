"""
Simplified HR Performance System Backend
Step by step implementation - starting with basic database connection
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# Simple User model without inheritance issues
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True) 
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

# Database setup
DATABASE_URL = "mysql+pymysql://hr_user:hr_password_2024@192.168.0.222:3306/hr_performance?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL logging for debugging
    pool_pre_ping=True,
    pool_recycle=3600
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI(
    title="HR Performance System - Simple",
    description="Simplified version with basic functionality",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    """Initialize database on startup"""
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "HR Performance System - Simple Version"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "hr-performance-backend-simple",
        "version": "1.0.0",
        "database": "connected"
    }

@app.get("/api/v1/users", response_model=List[UserRead])
def get_users(session: Session = Depends(get_session)):
    """Get all users"""
    statement = select(User)
    users = session.exec(statement).all()
    return users

@app.post("/api/v1/users", response_model=UserRead)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """Create a new user"""
    
    # Check if user already exists
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user

@app.get("/api/v1/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Get user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/v1/test/db")
def test_database(session: Session = Depends(get_session)):
    """Test database connection"""
    try:
        # Try to count users
        statement = select(User)
        users = session.exec(statement).all()
        return {
            "status": "success",
            "message": "Database connection working",
            "user_count": len(users),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)