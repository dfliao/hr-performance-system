"""
File management service - Handle evidence file uploads
"""

import os
import uuid
import aiofiles
from typing import List
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings


class FileService:
    def __init__(self):
        self.upload_path = Path(settings.SYNOLOGY_DRIVE_PATH)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_FILE_EXTENSIONS
        
        # Ensure upload directory exists
        self.upload_path.mkdir(parents=True, exist_ok=True)

    def is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        return extension in self.allowed_extensions

    def generate_unique_filename(self, original_filename: str, event_id: int, user_id: int) -> str:
        """Generate unique filename for evidence file"""
        file_extension = original_filename.lower().split('.')[-1]
        unique_id = str(uuid.uuid4())[:8]
        
        return f"event_{event_id}_user_{user_id}_{unique_id}.{file_extension}"

    async def upload_evidence_file(self, file: UploadFile, event_id: int, user_id: int) -> str:
        """Upload evidence file to Synology Drive"""
        
        if not self.is_allowed_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支援的檔案類型: {file.filename}"
            )
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename, event_id, user_id)
        
        # Create event-specific directory
        event_dir = self.upload_path / f"event_{event_id}"
        event_dir.mkdir(exist_ok=True)
        
        # Full file path
        file_path = event_dir / unique_filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Return relative URL for database storage
            relative_path = f"event_{event_id}/{unique_filename}"
            return f"{settings.SYNOLOGY_DRIVE_URL}/hr-evidence/{relative_path}"
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"檔案上傳失敗: {str(e)}"
            )

    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from storage"""
        try:
            # Extract relative path from URL
            if settings.SYNOLOGY_DRIVE_URL in file_path:
                relative_path = file_path.replace(f"{settings.SYNOLOGY_DRIVE_URL}/hr-evidence/", "")
                full_path = self.upload_path / relative_path
                
                if full_path.exists():
                    os.remove(full_path)
                    return True
            
            return False
        except Exception:
            return False

    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        try:
            if settings.SYNOLOGY_DRIVE_URL in file_path:
                relative_path = file_path.replace(f"{settings.SYNOLOGY_DRIVE_URL}/hr-evidence/", "")
                full_path = self.upload_path / relative_path
                
                if full_path.exists():
                    stat = full_path.stat()
                    return {
                        "filename": full_path.name,
                        "size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "modified_at": stat.st_mtime,
                        "exists": True
                    }
            
            return {"exists": False}
        except Exception:
            return {"exists": False}