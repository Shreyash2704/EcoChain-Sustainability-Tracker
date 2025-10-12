from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import os

router = APIRouter(prefix="/upload", tags=["uploads"])

# Mock database for demonstration
upload_sessions = {}

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    user_wallet: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload a file for processing (e.g., sustainability documents, carbon footprint data)
    """
    try:
        # Generate upload ID
        upload_id = str(uuid.uuid4())
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "application/pdf", "text/csv", "application/json"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not supported. Allowed types: {allowed_types}"
            )
        
        # Validate upload type
        allowed_upload_types = ["sustainability_document", "carbon_footprint", "certification", "proof_of_impact"]
        if upload_type not in allowed_upload_types:
            raise HTTPException(
                status_code=400,
                detail=f"Upload type {upload_type} not supported. Allowed types: {allowed_upload_types}"
            )
        
        # Store file information
        upload_sessions[upload_id] = {
            "upload_id": upload_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_type": upload_type,
            "user_wallet": user_wallet,
            "metadata": metadata,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat(),
            "file_size": file.size if hasattr(file, 'size') else 0
        }
        
        # TODO: In a real implementation, save the file to storage
        # For now, we'll just simulate the upload
        
        return {
            "upload_id": upload_id,
            "status": "uploaded",
            "message": "File uploaded successfully",
            "filename": file.filename,
            "upload_type": upload_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{upload_id}/status")
async def get_upload_status(upload_id: str):
    """
    Get the processing status of an uploaded file
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = upload_sessions[upload_id]
    
    # Simulate processing status updates
    processing_stages = ["uploaded", "processing", "analyzing", "verified", "completed"]
    current_stage = upload["status"]
    
    # Mock processing progression
    if current_stage == "uploaded":
        upload["status"] = "processing"
    elif current_stage == "processing":
        upload["status"] = "analyzing"
    elif current_stage == "analyzing":
        upload["status"] = "verified"
    elif current_stage == "verified":
        upload["status"] = "completed"
    
    return {
        "upload_id": upload_id,
        "status": upload["status"],
        "filename": upload["filename"],
        "upload_type": upload["upload_type"],
        "created_at": upload["created_at"],
        "progress": f"{processing_stages.index(upload['status']) + 1}/{len(processing_stages)}"
    }

@router.get("/")
async def list_user_uploads(user_wallet: str):
    """
    List all uploads for a specific user
    """
    user_uploads = [
        upload for upload in upload_sessions.values() 
        if upload["user_wallet"] == user_wallet
    ]
    
    return {
        "user_wallet": user_wallet,
        "uploads": user_uploads,
        "total_count": len(user_uploads)
    }

@router.delete("/{upload_id}")
async def delete_upload(upload_id: str):
    """
    Delete an uploaded file
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    del upload_sessions[upload_id]
    
    return {
        "upload_id": upload_id,
        "status": "deleted",
        "message": "Upload deleted successfully"
    }
