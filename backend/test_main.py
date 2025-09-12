"""
Minimal test FastAPI app to verify basic functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HR Performance System - Test",
    description="Minimal test version",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HR Performance System Test API is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "hr-performance-backend-test",
        "version": "1.0.0"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "Test endpoint working",
        "data": {
            "test": True,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)