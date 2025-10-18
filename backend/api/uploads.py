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
from services.web3_service import initialize_web3_service
from core.config import settings
from core.logging import get_logger

router = APIRouter(prefix="/upload", tags=["uploads"])
logger = get_logger(__name__)

# Mock database for demonstration
upload_sessions = {}

# Store for agent communication
bureau_instance: Optional[Bureau] = None

async def initialize_bureau():
    """Initialize the Bureau with all agents"""
    global bureau_instance
    if bureau_instance is None:
        bureau_instance = Bureau(port=8001)
        
        # Add all agents to Bureau
        try:
            from agents.user_agent import user_agent
            bureau_instance.add(user_agent)
            logger.info("Added user_agent to Bureau")
        except Exception as e:
            logger.warning(f"Could not add user_agent: {e}")
        
        try:
            bureau_instance.add(verifier_agent)
            logger.info("Added verifier_agent to Bureau")
        except Exception as e:
            logger.warning(f"Could not add verifier_agent: {e}")
        
        try:
            from agents.reasoner_agent import reasoner_agent
            bureau_instance.add(reasoner_agent)
            logger.info("Added reasoner_agent to Bureau")
        except Exception as e:
            logger.warning(f"Could not add reasoner_agent: {e}")
        
        try:
            from agents.minting_agent import minting_agent
            bureau_instance.add(minting_agent)
            logger.info("Added minting_agent to Bureau")
        except Exception as e:
            logger.warning(f"Could not add minting_agent: {e}")
        
        # Initialize Web3Service if configuration is available
        if settings.sepolia_rpc_url and settings.private_key:
            try:
                initialize_web3_service(settings.sepolia_rpc_url, settings.private_key)
                logger.info("✅ Web3Service initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Web3Service initialization failed: {e}")
        else:
            logger.warning("⚠️ Web3Service not initialized - missing RPC URL or private key")
        
        # Start bureau in background
        asyncio.create_task(bureau_instance.run_async())
        logger.info("Bureau initialized with all agents")

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
            
            # If tokens should be minted, trigger the minting agent
            if analysis_result['should_mint']:
                try:
                    from agents.minting_agent import minting_agent
                    
                    minting_request_data = {
                        "upload_id": upload_id,
                        "user_wallet": user_wallet,
                        "should_mint": analysis_result['should_mint'],
                        "token_amount": analysis_result['token_amount'],
                        "carbon_footprint": analysis_result['carbon_footprint'],
                        "impact_score": analysis_result['impact_score'],
                        "reasoning": analysis_result['reasoning'],
                        "document_type": upload_type,
                        "metadata": metadata,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    minting_message = ChatMessage(
                        content=[TextContent(
                            text=json.dumps(minting_request_data)
                        )]
                    )
                    
                    # Call the minting agent handler directly
                    from agents.minting_agent import handle_minting_request
                    
                    # Create a mock context
                    class MockContext:
                        async def send(self, recipient, message):
                            logger.info(f"📤 Mock response sent to {recipient}")
                    
                    mock_context = MockContext()
                    minting_response = await handle_minting_request(mock_context, "upload-api", minting_message)
                    logger.info(f"🪙 Minting request processed by Minting Agent for {analysis_result['token_amount']} tokens")
                    
                    # Store minting results in upload session
                    if hasattr(minting_response, 'content') and minting_response.content:
                        try:
                            minting_data = json.loads(minting_response.content[0].text)
                            upload_sessions[upload_id]["minting_results"] = minting_data.get("results", {})
                            upload_sessions[upload_id]["transaction_details"] = {
                                "eco_token_tx": minting_data.get("results", {}).get("eco_tokens", {}).get("tx_hash"),
                                "nft_tx": minting_data.get("results", {}).get("sustainability_nft", {}).get("tx_hash"),
                                "nft_token_id": minting_data.get("results", {}).get("sustainability_nft", {}).get("token_id"),
                                "proof_registry_tx": minting_data.get("results", {}).get("proof_registry", {}).get("tx_hash"),
                                "proof_id": minting_data.get("results", {}).get("proof_registry", {}).get("proof_id")
                            }
                        except Exception as e:
                            logger.error(f"Error parsing minting response: {e}")
                    
                except Exception as e:
                    logger.error(f"❌ Error sending to minting agent: {e}")

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
        
        # Add transaction details if minting was successful
        if "transaction_details" in upload_sessions[upload_id]:
            tx_details = upload_sessions[upload_id]["transaction_details"]
            response.update({
                "blockchain_transactions": {
                    "eco_token_minting": {
                        "tx_hash": tx_details.get("eco_token_tx"),
                        "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_details.get('eco_token_tx')}" if tx_details.get("eco_token_tx") else None,
                        "amount": analysis.get('token_amount', 0) if "analysis_result" in upload_sessions[upload_id] else 0
                    },
                    "nft_minting": {
                        "tx_hash": tx_details.get("nft_tx"),
                        "token_id": tx_details.get("nft_token_id"),
                        "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_details.get('nft_tx')}" if tx_details.get("nft_tx") else None,
                        "nft_contract": "0x17874E9d6e22bf8025Fe7473684e50f36472CCd2"
                    },
                    "proof_registration": {
                        "tx_hash": tx_details.get("proof_registry_tx"),
                        "proof_id": tx_details.get("proof_id"),
                        "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_details.get('proof_registry_tx')}" if tx_details.get("proof_registry_tx") else None,
                        "registry_contract": "0xc3f19798eC4aB47734209f99cAF63B6Fd9a04081"
                    }
                },
                "wallet_info": {
                    "user_wallet": user_wallet,
                    "wallet_explorer": f"https://sepolia.etherscan.io/address/{user_wallet}",
                    "eco_token_balance": f"https://sepolia.etherscan.io/token/0x6adB8BB5BB5Df5aB3596fc63dbAd51b092dee08f?a={user_wallet}",
                    "nft_collection": f"https://sepolia.etherscan.io/token/0x17874E9d6e22bf8025Fe7473684e50f36472CCd2?a={user_wallet}"
                }
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
