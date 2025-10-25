"""
Upload Agent - Handles document upload and processing requests
Wraps the upload API to handle document processing
"""

from uagents import Agent, Context, Model
from typing import Dict, Any, Optional
import logging
import asyncio
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UploadRequest(Model):
    """Request model for upload operations"""
    wallet_address: str
    message: str
    context: Dict[str, Any] = {}
    file_data: Optional[str] = None  # Base64 encoded file data
    filename: Optional[str] = None
    message_id: Optional[str] = None

class UploadResponse(Model):
    """Response model for upload operations"""
    message: str
    data: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None

# Create Upload Agent
upload_agent = Agent(
    name="upload_agent",
    port=8007,
    seed="upload_agent_seed_phrase_for_ecochain_sustainability_tracker"
)

@upload_agent.on_message(model=UploadRequest)
async def handle_upload_request(ctx: Context, sender: str, msg: UploadRequest):
    """
    Handle upload requests and process documents
    """
    try:
        logger.info(f"📤 Upload Agent received request from wallet: {msg.wallet_address}")
        
        # Check if file data is provided
        if not msg.file_data:
            response = UploadResponse(
                message="Please provide a file to upload. You can drag and drop a JSON file or use the upload button.",
                success=False,
                error="No file data provided"
            )
            await ctx.send(sender, response)
            return
        
        # Process the upload
        upload_result = await process_document_upload(
            msg.wallet_address,
            msg.file_data,
            msg.filename or "sustainability_document.json"
        )
        
        if upload_result.get("success", False):
            # Format response message
            response_message = format_upload_response(upload_result["data"])
            
            response = UploadResponse(
                message=response_message,
                data=upload_result["data"],
                success=True
            )
        else:
            response = UploadResponse(
                message=f"I couldn't process your document: {upload_result.get('error', 'Unknown error')}",
                success=False,
                error=upload_result.get("error", "Unknown error")
            )
        
        # Send response back to sender (User Agent)
        await ctx.send(sender, response)
        
    except Exception as e:
        logger.error(f"❌ Error in Upload Agent: {e}")
        error_response = UploadResponse(
            message=f"Sorry, I encountered an error processing your upload: {str(e)}",
            success=False,
            error=str(e)
        )
        await ctx.send(sender, error_response)

async def process_document_upload(wallet_address: str, file_data: str, filename: str) -> Dict[str, Any]:
    """
    Process document upload via the upload API
    """
    try:
        import aiohttp
        
        # Decode base64 file data
        try:
            file_bytes = base64.b64decode(file_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid file data: {str(e)}"
            }
        
        # Prepare multipart form data
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename=filename, content_type='application/json')
        data.add_field('user_wallet', wallet_address)
        
        # Call the upload API
        from core.config import get_settings
        settings = get_settings()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.upload_url}/upload/",
                data=data,
                timeout=aiohttp.ClientTimeout(total=120)  # 2 minutes for processing
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "data": result
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"Upload failed with status {response.status}: {error_text}"
                    }
                    
    except Exception as e:
        logger.error(f"❌ Failed to process upload: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def format_upload_response(data: Dict[str, Any]) -> str:
    """
    Format upload results into a user-friendly message
    """
    try:
        # Extract key information
        upload_id = data.get("upload_id", "Unknown")
        status = data.get("status", "Unknown")
        cid = data.get("cid", "N/A")
        
        # Analysis results
        analysis = data.get("analysis", {})
        should_mint = analysis.get("should_mint", False)
        token_amount = analysis.get("token_amount", 0)
        impact_score = analysis.get("impact_score", 0)
        reasoning = analysis.get("reasoning", "No analysis available")
        
        # Blockchain transactions
        blockchain = data.get("blockchain_transactions", {})
        eco_tokens = blockchain.get("eco_tokens", {})
        sustainability_nft = blockchain.get("sustainability_nft", {})
        
        # Format response
        response_parts = [
            f"📄 **Document Upload Complete!**",
            f"",
            f"🆔 **Upload ID**: {upload_id}",
            f"📊 **Status**: {status}",
            f"🔗 **IPFS CID**: {cid}",
            f"",
        ]
        
        # Add analysis results
        if should_mint:
            response_parts.extend([
                f"🎉 **Analysis Results**",
                f"✅ **Tokens Earned**: {token_amount} ECO",
                f"📈 **Impact Score**: {impact_score}/100",
                f"💡 **Reasoning**: {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}",
                f"",
            ])
        else:
            response_parts.extend([
                f"📊 **Analysis Results**",
                f"❌ **No tokens earned** (impact score too low)",
                f"📈 **Impact Score**: {impact_score}/100",
                f"💡 **Reasoning**: {reasoning[:100]}{'...' if len(reasoning) > 100 else ''}",
                f"",
            ])
        
        # Add blockchain transaction info
        if eco_tokens.get("success", False):
            tx_hash = eco_tokens.get("tx_hash", "N/A")
            response_parts.append(f"🪙 **ECO Tokens Minted**: {tx_hash}")
        
        if sustainability_nft.get("success", False):
            nft_tx_hash = sustainability_nft.get("tx_hash", "N/A")
            token_id = sustainability_nft.get("token_id", "N/A")
            response_parts.append(f"🎨 **NFT Minted**: Token #{token_id} - {nft_tx_hash}")
        
        # Add explorer links
        if eco_tokens.get("explorer_url"):
            response_parts.append(f"🔍 **View on Explorer**: {eco_tokens['explorer_url']}")
        
        # Add encouragement
        if should_mint:
            response_parts.append(f"")
            response_parts.append(f"🌟 Congratulations! Your sustainability efforts have been rewarded!")
        else:
            response_parts.append(f"")
            response_parts.append(f"💪 Keep working on your sustainability metrics to earn tokens!")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"❌ Error formatting upload response: {e}")
        return f"Document uploaded successfully! Upload ID: {upload_id}"

if __name__ == "__main__":
    upload_agent.run()
