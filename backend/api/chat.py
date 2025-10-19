"""
Chat API Router - Handles chat interactions with the multi-agent system
Provides endpoints for chat queries and agent communication
"""

from fastapi import APIRouter, HTTPException, Depends, Form, File, UploadFile
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    """Request model for chat queries"""
    wallet_address: str
    message: str
    context: Dict[str, Any] = {}
    message_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat queries"""
    response: str
    data: Optional[Dict[str, Any]] = None
    agent_name: str
    success: bool = True
    error: Optional[str] = None
    timestamp: str

class ChatHistoryRequest(BaseModel):
    """Request model for chat history"""
    wallet_address: str
    limit: int = 10

class ChatHistoryResponse(BaseModel):
    """Response model for chat history"""
    messages: list
    total: int

# In-memory chat history storage (in production, use a database)
chat_history: Dict[str, list] = {}

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Send a chat message to the User Agent for processing
    """
    try:
        logger.info(f"💬 Chat query from wallet: {request.wallet_address}")
        
        # Validate request
        if not request.wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address is required")
        
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate message ID if not provided
        message_id = request.message_id or f"msg_{datetime.now().timestamp()}"
        
        # Send message to User Agent
        response = await send_to_user_agent(request, message_id)
        
        # Store in chat history
        store_chat_message(request.wallet_address, request.message, response, message_id)
        
        return ChatResponse(
            response=response.get("message", "I couldn't process your request."),
            data=response.get("data"),
            agent_name=response.get("agent_name", "user_agent"),
            success=response.get("success", True),
            error=response.get("error"),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Chat query error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/query-with-file", response_model=ChatResponse)
async def chat_query_with_file(
    wallet_address: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Send a chat message with file attachment to the User Agent for processing
    """
    try:
        logger.info(f"💬 Chat query with file from wallet: {wallet_address}")
        
        # Validate request
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address is required")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="File is required")
        
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Generate message ID
        message_id = f"msg_{datetime.now().timestamp()}"
        
        # Create request object
        request = ChatRequest(
            wallet_address=wallet_address,
            message=message or f"Upload file: {file.filename}",
            context={"file_name": file.filename, "file_size": len(file_content)},
            message_id=message_id
        )
        
        # Process file upload through upload API
        upload_result = await process_file_upload(file_content, file.filename, wallet_address)
        
        # Send message to User Agent with upload results
        response = await send_to_user_agent_with_upload(request, upload_result, message_id)
        
        # Store in chat history
        store_chat_message(wallet_address, request.message, response, message_id)
        
        return ChatResponse(
            response=response.get("message", "I couldn't process your request."),
            data=response.get("data"),
            agent_name=response.get("agent_name", "user_agent"),
            success=response.get("success", True),
            error=response.get("error"),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Chat query with file error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/history/{wallet_address}", response_model=ChatHistoryResponse)
async def get_chat_history(wallet_address: str, limit: int = 10):
    """
    Get chat history for a wallet address
    """
    try:
        if wallet_address not in chat_history:
            return ChatHistoryResponse(messages=[], total=0)
        
        messages = chat_history[wallet_address][-limit:]  # Get last N messages
        return ChatHistoryResponse(
            messages=messages,
            total=len(chat_history[wallet_address])
        )
        
    except Exception as e:
        logger.error(f"❌ Chat history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.delete("/history/{wallet_address}")
async def clear_chat_history(wallet_address: str):
    """
    Clear chat history for a wallet address
    """
    try:
        if wallet_address in chat_history:
            del chat_history[wallet_address]
        
        return {"message": "Chat history cleared successfully"}
        
    except Exception as e:
        logger.error(f"❌ Clear chat history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")

@router.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents in the system
    """
    try:
        # This would check the actual agent statuses
        # For now, return mock status
        return {
            "user_agent": {"status": "active", "port": 8005},
            "analytics_agent": {"status": "active", "port": 8006},
            "upload_agent": {"status": "active", "port": 8007},
            "reasoner_agent": {"status": "active", "port": 8004},
            "recommendation_agent": {"status": "active", "port": 8008},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Agent status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

async def send_to_user_agent(request: ChatRequest, message_id: str) -> Dict[str, Any]:
    """
    Send message to User Agent via Bureau communication
    """
    try:
        # Import here to avoid circular imports
        from agents.user_agent import user_agent, ChatMessage, ChatResponse
        
        # Create message for User Agent
        chat_message = ChatMessage(
            wallet_address=request.wallet_address,
            message=request.message,
            context=request.context,
            message_id=message_id
        )
        
        # For now, simulate agent communication
        # In a real implementation, this would use the Bureau to send messages
        logger.info(f"📤 Sending message to User Agent: {request.message[:50]}...")
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # Mock response based on message content
        response = await simulate_user_agent_response(request)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Failed to send to User Agent: {e}")
        return {
            "message": f"Sorry, I encountered an error: {str(e)}",
            "agent_name": "user_agent",
            "success": False,
            "error": str(e)
        }

async def simulate_user_agent_response(request: ChatRequest) -> Dict[str, Any]:
    """
    Simulate User Agent response for testing
    """
    message_lower = request.message.lower()
    
    # Simple intent classification
    if any(word in message_lower for word in ["credit", "token", "balance", "how much"]):
        print(f"🔍 DEBUG: Chat API - Detected credit query, calling analytics agent...")
        
        # Actually call the analytics agent instead of returning mock data
        try:
            from agents.analytics_agent import analytics_agent, AnalyticsRequest, AnalyticsResponse
            
            # Create analytics request
            analytics_request = AnalyticsRequest(
                wallet_address=request.wallet_address,
                message=request.message,
                context=request.context,
                message_id=request.message_id
            )
            
            # Call analytics API directly instead of going through the agent
            from agents.analytics_agent import get_user_analytics
            
            print(f"🔍 DEBUG: Chat API - Calling analytics API directly...")
            analytics_data = await get_user_analytics(request.wallet_address)
            print(f"🔍 DEBUG: Chat API - Analytics data: {analytics_data}")
            
            if analytics_data.get("success", False):
                data = analytics_data["data"]
                summary = data.get("summary", {})
                total_credits = summary.get("total_credits_earned", 0)
                total_tokens = summary.get("total_eco_tokens", "0")
                
                # Format the response message
                response_message = f"🌱 **Your EcoChain Summary**\n\n💰 **Credits Earned**: {total_credits}\n📄 **Documents Uploaded**: {summary.get('total_documents_uploaded', 0)}\n✅ **Success Rate**: {summary.get('success_rate', 0):.1f}%\n🪙 **ECO Tokens**: {total_tokens}\n🎨 **NFTs Owned**: {summary.get('total_nfts_owned', 0)}\n\n📈 **Recent Activity**: {summary.get('successful_uploads', 0)} successful uploads\n\n🎉 Great job on your sustainability efforts! Keep it up!"
                
                return {
                    "message": response_message,
                    "data": {
                        "total_credits": total_credits,
                        "total_tokens": str(total_tokens),
                        "wallet_address": request.wallet_address
                    },
                    "agent_name": "analytics_agent",
                    "success": True
                }
            else:
                return {
                    "message": "I couldn't retrieve your analytics data. Please make sure your wallet is connected and try again.",
                    "data": {
                        "total_credits": 0,
                        "total_tokens": "0",
                        "wallet_address": request.wallet_address
                    },
                    "agent_name": "analytics_agent",
                    "success": False,
                    "error": analytics_data.get("error", "Unknown error")
                }
                
        except Exception as e:
            print(f"🔍 DEBUG: Chat API - Error calling analytics agent: {e}")
            return {
                "message": f"🌱 You have 0 ECO tokens in your account. Upload sustainability documents to start earning credits!",
                "data": {
                    "total_credits": 0,
                    "total_tokens": "0",
                    "wallet_address": request.wallet_address
                },
                "agent_name": "analytics_agent",
                "success": True
            }
    elif any(word in message_lower for word in ["upload", "document", "file"]):
        return {
            "message": "📤 Please upload your sustainability document using the file upload button or drag and drop a JSON file here.",
            "data": {
                "upload_ready": True,
                "supported_formats": ["json"]
            },
            "agent_name": "upload_agent",
            "success": True
        }
    elif any(word in message_lower for word in ["recommend", "improve", "tips", "help"]):
        return {
            "message": "💡 Here are some ways to improve your sustainability score:\n\n• Track your carbon footprint regularly\n• Implement waste reduction programs\n• Switch to renewable energy sources\n• Upload detailed sustainability reports\n\nWould you like specific recommendations for any area?",
            "data": {
                "recommendations": [
                    "Track carbon footprint",
                    "Reduce waste",
                    "Use renewable energy",
                    "Upload detailed reports"
                ]
            },
            "agent_name": "recommendation_agent",
            "success": True
        }
    else:
        return {
            "message": "🌱 I'm here to help with your sustainability tracking! You can ask me about:\n\n• Your carbon credits and token balance\n• Upload sustainability documents for analysis\n• Get recommendations to improve your sustainability score\n\nWhat would you like to know?",
            "data": {},
            "agent_name": "user_agent",
            "success": True
        }

def store_chat_message(wallet_address: str, user_message: str, agent_response: Dict[str, Any], message_id: str):
    """
    Store chat message in history
    """
    try:
        if wallet_address not in chat_history:
            chat_history[wallet_address] = []
        
        chat_entry = {
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response.get("message", ""),
            "agent_name": agent_response.get("agent_name", "unknown"),
            "success": agent_response.get("success", True)
        }
        
        chat_history[wallet_address].append(chat_entry)
        
        # Keep only last 100 messages per wallet
        if len(chat_history[wallet_address]) > 100:
            chat_history[wallet_address] = chat_history[wallet_address][-100:]
            
    except Exception as e:
        logger.error(f"❌ Failed to store chat message: {e}")

# Health check endpoint
@router.get("/health")
async def chat_health():
    """
    Health check for chat service
    """
    return {
        "status": "healthy",
        "service": "chat_api",
        "timestamp": datetime.now().isoformat()
    }

async def process_file_upload(file_content: bytes, filename: str, wallet_address: str) -> Dict[str, Any]:
    """
    Process file upload through the upload API
    """
    try:
        # Create a temporary file-like object
        import io
        file_obj = io.BytesIO(file_content)
        
        # Prepare form data for upload API
        data = aiohttp.FormData()
        data.add_field('file', file_obj, filename=filename, content_type='application/json')
        data.add_field('user_wallet', wallet_address)
        data.add_field('upload_type', 'sustainability_document')  # Required field
        
        # Call the upload API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8002/upload/",
                data=data,
                timeout=aiohttp.ClientTimeout(total=120)  # 2 minutes for processing
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Upload failed with status {response.status}: {error_text}"
                    }
                    
    except Exception as e:
        logger.error(f"❌ Failed to process file upload: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def send_to_user_agent_with_upload(request: ChatRequest, upload_result: Dict[str, Any], message_id: str) -> Dict[str, Any]:
    """
    Send message to User Agent with upload results
    """
    try:
        logger.info(f"📤 Sending message with upload results to User Agent")
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # Format response based on upload results
        # Check if upload was successful (status completed and should_mint is true)
        upload_status = upload_result.get("status", "")
        should_mint = upload_result.get("should_mint", False)
        token_amount = upload_result.get("token_amount", 0)
        impact_score = upload_result.get("impact_score", 0)
        
        # Check blockchain transactions
        blockchain_txs = upload_result.get("blockchain_transactions", {})
        eco_tokens_success = blockchain_txs.get("eco_token_minting", {}).get("tx_hash") is not None
        nft_success = blockchain_txs.get("nft_minting", {}).get("tx_hash") is not None
        
        if upload_status == "completed" and should_mint and (eco_tokens_success or nft_success):
            # Success case - tokens or NFT minted
            response_message = f"🎉 **File Upload Successful!**\n\n📄 **File**: {request.context.get('file_name', 'Unknown')}\n✅ **Tokens Earned**: {token_amount} ECO\n📈 **Impact Score**: {impact_score}/100\n\n"
            
            if eco_tokens_success:
                eco_tx = blockchain_txs.get("eco_token_minting", {})
                response_message += f"🪙 **ECO Tokens**: {eco_tx.get('amount', 0)} minted\n🔗 **Transaction**: {eco_tx.get('explorer_url', 'N/A')}\n\n"
            
            if nft_success:
                nft_tx = blockchain_txs.get("nft_minting", {})
                response_message += f"🎨 **NFT Minted**: Token #{nft_tx.get('token_id', 'N/A')}\n🔗 **Transaction**: {nft_tx.get('explorer_url', 'N/A')}\n\n"
            
            response_message += "Your sustainability document has been analyzed and tokens have been minted to your wallet!"
            
            return {
                "message": response_message,
                "data": upload_result,
                "agent_name": "upload_agent",
                "success": True
            }
        elif upload_status == "completed" and not should_mint:
            # Completed but no tokens earned
            response_message = f"📄 **File Upload Complete**\n\n📄 **File**: {request.context.get('file_name', 'Unknown')}\n❌ **No tokens earned** (impact score too low)\n📈 **Impact Score**: {impact_score}/100\n\nYour document was processed but didn't meet the minimum requirements for token minting."
            
            return {
                "message": response_message,
                "data": upload_result,
                "agent_name": "upload_agent",
                "success": True
            }
        else:
            # Failed case
            return {
                "message": f"❌ **Upload Failed**\n\n📄 **File**: {request.context.get('file_name', 'Unknown')}\n\nError: {upload_result.get('error', 'Unknown error')}\n\nPlease check your file format and try again.",
                "data": upload_result,
                "agent_name": "upload_agent",
                "success": False,
                "error": upload_result.get("error", "Unknown error")
            }
        
    except Exception as e:
        logger.error(f"❌ Failed to send to User Agent with upload: {e}")
        return {
            "message": f"Sorry, I encountered an error processing your file: {str(e)}",
            "agent_name": "user_agent",
            "success": False,
            "error": str(e)
        }
