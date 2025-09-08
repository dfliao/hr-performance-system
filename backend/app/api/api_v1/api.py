"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, events, reports

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])