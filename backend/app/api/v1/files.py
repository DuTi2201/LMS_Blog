from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
import os

from ...services.file_service import FileService
from ..deps import get_current_user, get_active_user, get_file_service
from ...models.user import User, UserRole
from ...core.config import settings

router = APIRouter()


@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    resize_width: Optional[int] = Form(None),
    resize_height: Optional[int] = Form(None),
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Upload image file with optional resizing"""
    try:
        file_info = await file_service.upload_image(
            file=file,
            resize_width=resize_width,
            resize_height=resize_height
        )
        return {
            "message": "Image uploaded successfully",
            "file_info": file_info
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Upload video file"""
    try:
        file_info = await file_service.upload_video(file)
        return {
            "message": "Video uploaded successfully",
            "file_info": file_info
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload video: {str(e)}"
        )


@router.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Upload document file"""
    try:
        file_info = await file_service.upload_document(file)
        return {
            "message": "Document uploaded successfully",
            "file_info": file_info
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post("/upload/attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Upload general attachment file"""
    try:
        file_info = await file_service.upload_attachment(file)
        return {
            "message": "Attachment uploaded successfully",
            "file_info": file_info
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload attachment: {str(e)}"
        )


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Download file by path"""
    try:
        # Construct full file path
        full_path = os.path.join(settings.UPLOAD_DIR, file_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Get file info
        file_info = file_service.get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Return file response
        return FileResponse(
            path=full_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download file: {str(e)}"
        )


@router.get("/info/{file_path:path}")
def get_file_info(
    file_path: str,
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Get file information"""
    try:
        file_info = file_service.get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return file_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}"
        )


@router.delete("/delete/{file_path:path}")
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Delete file"""
    # Only admin users can delete files directly
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete files"
        )
    
    try:
        success = await file_service.delete_file(file_path)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or could not be deleted"
            )
        
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


@router.get("/list")
def list_files(
    directory: Optional[str] = None,
    file_type: Optional[str] = None,
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """List files in directory (Admin only)"""
    # Only admin users can list files
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to list files"
        )
    
    try:
        files = file_service.list_files(directory, file_type)
        return {
            "directory": directory or "root",
            "file_type": file_type,
            "files": files,
            "total": len(files)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.post("/cleanup-temp")
async def cleanup_temp_files(
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Clean up temporary files (Admin only)"""
    # Only admin users can cleanup temp files
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to cleanup temporary files"
        )
    
    try:
        cleaned_count = await file_service.cleanup_temp_files()
        return {
            "message": "Temporary files cleaned up successfully",
            "cleaned_files": cleaned_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup temporary files: {str(e)}"
        )


@router.get("/stats")
def get_file_stats(
    current_user: User = Depends(get_active_user),
    file_service: FileService = Depends(get_file_service)
):
    """Get file storage statistics (Admin only)"""
    # Only admin users can view file stats
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view file statistics"
        )
    
    try:
        # Calculate storage statistics
        upload_dir = settings.UPLOAD_DIR
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
        
        # Convert bytes to MB
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size_mb, 2),
            "upload_directory": upload_dir,
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file statistics: {str(e)}"
        )


@router.get("/health")
def check_file_service_health(
    file_service: FileService = Depends(get_file_service)
):
    """Check file service health"""
    try:
        # Check if upload directory exists and is writable
        upload_dir = settings.UPLOAD_DIR
        
        if not os.path.exists(upload_dir):
            return {
                "status": "unhealthy",
                "message": "Upload directory does not exist",
                "upload_dir": upload_dir
            }
        
        if not os.access(upload_dir, os.W_OK):
            return {
                "status": "unhealthy",
                "message": "Upload directory is not writable",
                "upload_dir": upload_dir
            }
        
        return {
            "status": "healthy",
            "message": "File service is operational",
            "upload_dir": upload_dir,
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"File service health check failed: {str(e)}"
        }