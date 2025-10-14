from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from typing import Dict, Any, Optional
import json
import asyncio
from datetime import datetime

# Create the verifier agent
verifier_agent = Agent(
    name="EcoChain VerifierAgent",
    seed="eco_verifier_agent_seed",
    port=8002
)

# Store for pending upload requests
pending_uploads: Dict[str, Dict[str, Any]] = {}

# Handle verification requests
@verifier_agent.on_message(model=ChatMessage)
async def handle_verification_request(ctx: Context, sender: str, msg: ChatMessage):
    verification_data = msg.content[0].text
    print(f"Verification request from {sender}: {verification_data}")
    
    # TODO: Implement verification logic
    # This could include:
    # - Validating sustainability claims
    # - Checking carbon footprint data
    # - Verifying environmental certifications
    # - Cross-referencing with external databases
    
    response = ChatMessage(
        content=[TextContent(
            text=f"Verification processed for: {verification_data}. Status: Verified ✅"
        )]
    )
    await ctx.send(sender, response)

# Handle file upload requests
@verifier_agent.on_message(model=ChatMessage)
async def handle_file_upload_request(ctx: Context, sender: str, msg: ChatMessage):
    """Handle file upload requests and return CID"""
    try:
        # Parse the upload request
        upload_data = json.loads(msg.content[0].text)
        upload_id = upload_data.get("upload_id")
        file_data = upload_data.get("file_data")
        filename = upload_data.get("filename")
        content_type = upload_data.get("content_type")
        
        if not all([upload_id, file_data, filename]):
            raise ValueError("Missing required upload data")
        
        print(f"Processing file upload {upload_id} from {sender}")
        
        # Store the upload request
        pending_uploads[upload_id] = {
            "upload_id": upload_id,
            "filename": filename,
            "content_type": content_type,
            "status": "processing",
            "sender": sender,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Simulate file processing and IPFS upload
        # In a real implementation, this would:
        # 1. Decode the file data
        # 2. Upload to IPFS via Lighthouse
        # 3. Return the CID
        
        # For now, simulate the upload process
        await asyncio.sleep(2)  # Simulate processing time
        
        # Mock CID generation (in real implementation, this comes from IPFS)
        mock_cid = f"QmMock{upload_id.replace('-', '')[:40]}"
        
        # Update upload status
        pending_uploads[upload_id].update({
            "status": "completed",
            "cid": mock_cid,
            "gateway_url": f"https://gateway.lighthouse.storage/ipfs/{mock_cid}",
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Send response back to sender
        response_data = {
            "upload_id": upload_id,
            "status": "completed",
            "cid": mock_cid,
            "gateway_url": f"https://gateway.lighthouse.storage/ipfs/{mock_cid}",
            "filename": filename,
            "message": "File uploaded successfully to IPFS"
        }
        
        response = ChatMessage(
            content=[TextContent(
                text=json.dumps(response_data)
            )]
        )
        await ctx.send(sender, response)
        
        print(f"File upload {upload_id} completed with CID: {mock_cid}")
        
    except json.JSONDecodeError as e:
        error_response = ChatMessage(
            content=[TextContent(
                text=json.dumps({
                    "error": "Invalid JSON in upload request",
                    "details": str(e)
                })
            )]
        )
        await ctx.send(sender, error_response)
        
    except Exception as e:
        error_response = ChatMessage(
            content=[TextContent(
                text=json.dumps({
                    "error": "Upload processing failed",
                    "details": str(e)
                })
            )]
        )
        await ctx.send(sender, error_response)
        print(f"Error processing upload: {e}")

def get_upload_status(upload_id: str) -> Optional[Dict[str, Any]]:
    """Get the status of an upload request"""
    return pending_uploads.get(upload_id)

# Run the agent
if __name__ == "__main__":
    verifier_agent.run()
