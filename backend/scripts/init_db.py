#!/usr/bin/env python3
"""
Initialize database with Alembic migrations
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from alembic import command
from alembic.config import Config
from sqlmodel import create_engine
from app.core.config import settings
from app.models import *  # Import all models to register them

def run_migrations():
    """Run Alembic migrations"""
    print("🗄️ Initializing database with Alembic...")
    
    # Get alembic config
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Run migrations
        print("📊 Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

def check_database_connection():
    """Check if database connection is working"""
    print("🔍 Checking database connection...")
    
    try:
        engine = create_engine(str(settings.DATABASE_URL))
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def main():
    """Main initialization function"""
    print("🚀 Starting database initialization...")
    
    # Check database connection first
    if not check_database_connection():
        print("💡 Make sure PostgreSQL is running and the database exists")
        sys.exit(1)
    
    # Run migrations
    run_migrations()
    
    print("🎉 Database initialization completed!")
    print("💡 Run 'python scripts/create_sample_data.py' to create sample data")

if __name__ == "__main__":
    asyncio.run(main())