import os
import uuid
import shutil
from typing import Optional, List
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import aiofiles

from ..core.config import settings


class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE  # in bytes
        self.allowed_image_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        self.allowed_video_types = {"video/mp4", "video/webm", "video/ogg"}
        self.allowed_document_types = {
            "application/pdf", "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain", "text/csv"
        }
        
        # Create upload directories if they don't exist
        self._create_upload_directories()
    
    def _create_upload_directories(self):
        """Create upload directories if they don't exist"""
        directories = [
            self.upload_dir / "images",
            self.upload_dir / "videos",
            self.upload_dir / "documents",
            self.upload_dir / "attachments",
            self.upload_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename while preserving extension"""
        file_extension = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    def _validate_file_size(self, file: UploadFile):
        """Validate file size"""
        if file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size / (1024*1024):.1f}MB"
            )
    
    def _validate_file_type(self, file: UploadFile, allowed_types: set):
        """Validate file type"""
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} is not allowed"
            )
    
    def _get_file_category(self, content_type: str) -> str:
        """Determine file category based on content type"""
        if content_type in self.allowed_image_types:
            return "images"
        elif content_type in self.allowed_video_types:
            return "videos"
        elif content_type in self.allowed_document_types:
            return "documents"
        else:
            return "attachments"
    
    async def upload_image(self, file: UploadFile, resize: Optional[tuple] = None) -> dict:
        """Upload and optionally resize image"""
        # Validate file
        self._validate_file_size(file)
        self._validate_file_type(file, self.allowed_image_types)
        
        # Generate filename and path
        filename = self._generate_filename(file.filename)
        file_path = self.upload_dir / "images" / filename
        
        try:
            # Save original file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Resize image if requested
            if resize:
                await self._resize_image(file_path, resize)
            
            # Generate URL
            file_url = f"/uploads/images/{filename}"
            
            return {
                "filename": filename,
                "original_filename": file.filename,
                "file_url": file_url,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type
            }
        
        except Exception as e:
            # Clean up file if upload failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
    
    async def _resize_image(self, file_path: Path, size: tuple):
        """Resize image to specified dimensions"""
        try:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Resize image maintaining aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(file_path, optimize=True, quality=85)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to resize image: {str(e)}"
            )
    
    async def upload_video(self, file: UploadFile) -> dict:
        """Upload video file"""
        # Validate file
        self._validate_file_size(file)
        self._validate_file_type(file, self.allowed_video_types)
        
        # Generate filename and path
        filename = self._generate_filename(file.filename)
        file_path = self.upload_dir / "videos" / filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate URL
            file_url = f"/uploads/videos/{filename}"
            
            return {
                "filename": filename,
                "original_filename": file.filename,
                "file_url": file_url,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type
            }
        
        except Exception as e:
            # Clean up file if upload failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload video: {str(e)}"
            )
    
    async def upload_document(self, file: UploadFile) -> dict:
        """Upload document file"""
        # Validate file
        self._validate_file_size(file)
        self._validate_file_type(file, self.allowed_document_types)
        
        # Generate filename and path
        filename = self._generate_filename(file.filename)
        file_path = self.upload_dir / "documents" / filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate URL
            file_url = f"/uploads/documents/{filename}"
            
            return {
                "filename": filename,
                "original_filename": file.filename,
                "file_url": file_url,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type
            }
        
        except Exception as e:
            # Clean up file if upload failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload document: {str(e)}"
            )
    
    async def upload_attachment(self, file: UploadFile) -> dict:
        """Upload any type of attachment"""
        # Validate file size only
        self._validate_file_size(file)
        
        # Generate filename and path
        filename = self._generate_filename(file.filename)
        file_path = self.upload_dir / "attachments" / filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate URL
            file_url = f"/uploads/attachments/{filename}"
            
            return {
                "filename": filename,
                "original_filename": file.filename,
                "file_url": file_url,
                "file_path": str(file_path),
                "file_size": len(content),
                "content_type": file.content_type
            }
        
        except Exception as e:
            # Clean up file if upload failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload attachment: {str(e)}"
            )
    
    async def upload_file(self, file: UploadFile, file_type: Optional[str] = None) -> dict:
        """Generic file upload method"""
        if file_type == "image":
            return await self.upload_image(file)
        elif file_type == "video":
            return await self.upload_video(file)
        elif file_type == "document":
            return await self.upload_document(file)
        else:
            # Auto-detect file type or use attachment
            if file.content_type in self.allowed_image_types:
                return await self.upload_image(file)
            elif file.content_type in self.allowed_video_types:
                return await self.upload_video(file)
            elif file.content_type in self.allowed_document_types:
                return await self.upload_document(file)
            else:
                return await self.upload_attachment(file)
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        try:
            # Convert relative URL to absolute path
            if file_path.startswith("/uploads/"):
                relative_path = file_path[9:]  # Remove '/uploads/' prefix
                absolute_path = self.upload_dir / relative_path
            else:
                absolute_path = Path(file_path)
            
            if absolute_path.exists() and absolute_path.is_file():
                absolute_path.unlink()
                return True
            
            return False
        
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            # Convert relative URL to absolute path
            if file_path.startswith("/uploads/"):
                relative_path = file_path[9:]  # Remove '/uploads/' prefix
                absolute_path = self.upload_dir / relative_path
            else:
                absolute_path = Path(file_path)
            
            if absolute_path.exists() and absolute_path.is_file():
                stat = absolute_path.stat()
                return {
                    "filename": absolute_path.name,
                    "file_path": str(absolute_path),
                    "file_size": stat.st_size,
                    "created_at": stat.st_ctime,
                    "modified_at": stat.st_mtime
                }
            
            return None
        
        except Exception:
            return None
    
    def list_files(self, directory: str = "", limit: int = 100) -> List[dict]:
        """List files in upload directory"""
        try:
            if directory:
                search_dir = self.upload_dir / directory
            else:
                search_dir = self.upload_dir
            
            if not search_dir.exists():
                return []
            
            files = []
            for file_path in search_dir.rglob("*"):
                if file_path.is_file() and len(files) < limit:
                    stat = file_path.stat()
                    relative_path = file_path.relative_to(self.upload_dir)
                    
                    files.append({
                        "filename": file_path.name,
                        "file_path": str(file_path),
                        "file_url": f"/uploads/{relative_path}",
                        "file_size": stat.st_size,
                        "created_at": stat.st_ctime,
                        "modified_at": stat.st_mtime
                    })
            
            return files
        
        except Exception:
            return []
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            temp_dir = self.upload_dir / "temp"
            if not temp_dir.exists():
                return
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
        
        except Exception:
            pass  # Silently fail for cleanup operations