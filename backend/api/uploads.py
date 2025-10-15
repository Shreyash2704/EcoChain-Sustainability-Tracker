from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
import os
import base64
import json
import asyncio
from uagents import Bureau
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

from agents.verifier_agent import verifier_agent, get_upload_status
from services.lighthouse_service import get_lighthouse_service
from core.logging import get_logger

router = APIRouter(prefix="/upload", tags=["uploads"])
logger = get_logger(__name__)

# Mock database for demonstration
upload_sessions = {}

# Store for agent communication
bureau_instance: Optional[Bureau] = None

async def initialize_bureau():
    """Initialize the Bureau with verifier agent"""
    global bureau_instance
    if bureau_instance is None:
        bureau_instance = Bureau(port=8001)
        bureau_instance.add(verifier_agent)
        # Start bureau in background
        asyncio.create_task(bureau_instance.run_async())
        logger.info("Bureau initialized with verifier agent")

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    user_wallet: str = Form(...),
    metadata: Optional[str] = Form(None)
):
    """
    Upload a file for processing via verifier agent and return CID
    """
    try:
        # Initialize bureau if not already done
        await initialize_bureau()
        
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
        
        # Read file content
        file_content = await file.read()
        file_data_b64 = base64.b64encode(file_content).decode('utf-8')
        
        # Store file information
        upload_sessions[upload_id] = {
            "upload_id": upload_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_type": upload_type,
            "user_wallet": user_wallet,
            "metadata": metadata,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat(),
            "file_size": len(file_content)
        }
        
        # Prepare upload data for verifier agent
        upload_data = {
            "upload_id": upload_id,
            "file_data": file_data_b64,
            "filename": file.filename,
            "content_type": file.content_type,
            "upload_type": upload_type,
            "user_wallet": user_wallet,
            "metadata": metadata
        }
        
        # Send to verifier agent
        message = ChatMessage(
            content=[TextContent(
                text=json.dumps(upload_data)
            )]
        )
        
        # For now, simulate the verifier agent processing directly
        # In a real implementation, this would send to the verifier agent via Bureau
        logger.info(f"Processing upload via verifier agent simulation: {upload_id}")
        
        # Simulate verifier agent processing
        await asyncio.sleep(1)  # Simulate processing time
        
        # Generate mock CID
        mock_cid = f"QmMock{upload_id.replace('-', '')[:40]}"
        
        # Update upload status
        upload_sessions[upload_id].update({
            "status": "completed",
            "cid": mock_cid,
            "gateway_url": f"https://gateway.lighthouse.storage/ipfs/{mock_cid}",
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Simulate sending to reasoner agent
        try:
            # Import reasoner agent functions directly
            from agents.reasoner_agent import analyze_document_and_calculate_credits
            
            # Decode document content
            try:
                decoded_content = base64.b64decode(file_data_b64).decode('utf-8')
            except:
                decoded_content = file_data_b64
            
            # Run reasoner analysis
            logger.info(f"Running reasoner analysis for upload: {upload_id}")
            analysis_result = await analyze_document_and_calculate_credits(
                document_content=decoded_content,
                document_type=upload_type,
                metadata=metadata,
                user_wallet=user_wallet
            )
            
            # Update upload with analysis results
            upload_sessions[upload_id].update({
                "analysis_result": analysis_result,
                "should_mint": analysis_result['should_mint'],
                "token_amount": analysis_result['token_amount'],
                "reasoning": analysis_result['reasoning']
            })
            
            logger.info(f"Reasoner analysis completed: {analysis_result['should_mint']} - {analysis_result['token_amount']} tokens")
            
        except Exception as e:
            logger.error(f"Error in reasoner analysis: {e}")
            # Continue without analysis results
        
        # Prepare response
        response = {
            "upload_id": upload_id,
            "status": "completed",
            "message": "File uploaded successfully and analyzed",
            "filename": file.filename,
            "upload_type": upload_type,
            "cid": mock_cid,
            "gateway_url": f"https://gateway.lighthouse.storage/ipfs/{mock_cid}"
        }
        
        # Add analysis results if available
        if "analysis_result" in upload_sessions[upload_id]:
            analysis = upload_sessions[upload_id]["analysis_result"]
            response.update({
                "should_mint": analysis['should_mint'],
                "token_amount": analysis['token_amount'],
                "reasoning": analysis['reasoning'],
                "impact_score": analysis['impact_score']
            })
        
        return response
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/{upload_id}/status")
async def get_upload_status_endpoint(upload_id: str):
    """
    Get the processing status of an uploaded file from verifier agent
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = upload_sessions[upload_id]
    
    # For now, we're using simulated processing
    # The upload status is already updated in the upload endpoint
    # In a real implementation, this would check with the verifier agent
    
    # Prepare response
    response = {
        "upload_id": upload_id,
        "status": upload["status"],
        "filename": upload["filename"],
        "upload_type": upload["upload_type"],
        "created_at": upload["created_at"],
        "file_size": upload["file_size"]
    }
    
    # Add CID and gateway URL if available
    if "cid" in upload:
        response["cid"] = upload["cid"]
        response["gateway_url"] = upload["gateway_url"]
    
    if "completed_at" in upload:
        response["completed_at"] = upload["completed_at"]
    
    return response

@router.get("/{upload_id}/cid")
async def get_upload_cid(upload_id: str):
    """
    Get the CID (Content ID) for an uploaded file
    """
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload = upload_sessions[upload_id]
    
    # Check if upload is completed
    if upload["status"] != "completed":
        raise HTTPException(
            status_code=202, 
            detail="Upload still processing. Check status endpoint for updates."
        )
    
    if "cid" not in upload:
        raise HTTPException(
            status_code=500, 
            detail="CID not available for this upload"
        )
    
    return {
        "upload_id": upload_id,
        "cid": upload["cid"],
        "gateway_url": upload["gateway_url"],
        "filename": upload["filename"],
        "upload_type": upload["upload_type"],
        "completed_at": upload["completed_at"]
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
