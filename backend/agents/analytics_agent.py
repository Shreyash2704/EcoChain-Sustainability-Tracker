"""
Analytics Agent - Handles user credit and analytics queries
Wraps the analytics API to provide formatted credit information
"""

from uagents import Agent, Context, Model
from typing import Dict, Any, Optional
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsRequest(Model):
    """Request model for analytics queries"""
    wallet_address: str
    message: str
    context: Dict[str, Any] = {}
    message_id: Optional[str] = None

class AnalyticsResponse(Model):
    """Response model for analytics queries"""
    message: str
    data: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None

# Create Analytics Agent
analytics_agent = Agent(
    name="analytics_agent",
    port=8006,
    seed="analytics_agent_seed_phrase_for_ecochain_sustainability_tracker",
    mailbox=True,
    publish_agent_details=True,
    readme_path="AGENT_README.md"
)

# Agentverse metadata for agent discovery
analytics_agent.agentverse_metadata = {
    "name": "EcoChain Analytics Agent",
    "description": "Provides user analytics, leaderboards, and system statistics for sustainability tracking",
    "capabilities": [
        "user_analytics",
        "leaderboard_generation",
        "statistics",
        "credit_tracking",
        "nft_analytics",
        "system_overview"
    ],
    "protocols": ["uAgents", "HTTP"],
    "version": "1.0.0",
    "endpoints": {
        "analytics": "/agents/analytics/query",
        "health": "/agents/analytics/health"
    },
    "tags": ["analytics", "statistics", "leaderboard", "credits", "sustainability"]
}

@analytics_agent.on_message(model=AnalyticsRequest)
async def handle_analytics_request(ctx: Context, sender: str, msg: AnalyticsRequest):
    """
    Handle analytics requests and return formatted credit information
    """
    try:
        logger.info(f"📊 Analytics Agent received request for wallet: {msg.wallet_address}")
        print(f"🔍 DEBUG: Analytics Agent - Wallet address: {msg.wallet_address}")
        
        # Get user analytics data
        analytics_data = await get_user_analytics(msg.wallet_address)
        print(f"🔍 DEBUG: Analytics Agent - Analytics data result: {analytics_data}")
        
        if analytics_data.get("success", False):
            # Format response message
            response_message = format_analytics_response(analytics_data["data"])
            print(f"🔍 DEBUG: Analytics Agent - Formatted response: {response_message}")
            
            response = AnalyticsResponse(
                message=response_message,
                data=analytics_data["data"],
                success=True
            )
        else:
            print(f"🔍 DEBUG: Analytics Agent - Analytics data failed: {analytics_data.get('error', 'Unknown error')}")
            response = AnalyticsResponse(
                message="I couldn't retrieve your analytics data. Please make sure your wallet is connected and try again.",
                success=False,
                error=analytics_data.get("error", "Unknown error")
            )
        
        # Send response back to sender (User Agent)
        await ctx.send(sender, response)
        
    except Exception as e:
        logger.error(f"❌ Error in Analytics Agent: {e}")
        error_response = AnalyticsResponse(
            message=f"Sorry, I encountered an error retrieving your analytics: {str(e)}",
            success=False,
            error=str(e)
        )
        await ctx.send(sender, error_response)

async def get_user_analytics(wallet_address: str) -> Dict[str, Any]:
    """
    Get user analytics data from the analytics API
    """a
    try:
        import aiohttp
        
        print(f"🔍 DEBUG: get_user_analytics - Calling API for wallet: {wallet_address}")
        
        # Call the analytics API
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8002/analytics/user/{wallet_address}",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"🔍 DEBUG: get_user_analytics - API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"🔍 DEBUG: get_user_analytics - API data received: {data}")
                    return {
                        "success": True,
                        "data": data
                    }
                else:
                    error_text = await response.text()
                    print(f"🔍 DEBUG: get_user_analytics - API error: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"API error {response.status}: {error_text}"
                    }
                    
    except Exception as e:
        print(f"🔍 DEBUG: get_user_analytics - Exception: {e}")
        logger.error(f"❌ Failed to get analytics data: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def format_analytics_response(data: Dict[str, Any]) -> str:
    """
    Format analytics data into a user-friendly message
    """
    try:
        summary = data.get("summary", {})
        
        # Extract key metrics
        total_credits = summary.get("total_credits_earned", 0)
        total_documents = summary.get("total_documents_uploaded", 0)
        success_rate = summary.get("success_rate", 0)
        total_eco_tokens = summary.get("total_eco_tokens", "N/A")
        total_nfts = summary.get("total_nfts_owned", "N/A")
        
        # Format response
        response_parts = [
            f"🌱 **Your EcoChain Summary**",
            f"",
            f"💰 **Credits Earned**: {total_credits}",
            f"📄 **Documents Uploaded**: {total_documents}",
            f"✅ **Success Rate**: {success_rate:.1f}%",
        ]
        
        # Add blockchain data if available
        if total_eco_tokens != "N/A":
            response_parts.append(f"🪙 **ECO Tokens**: {total_eco_tokens}")
        
        if total_nfts != "N/A":
            response_parts.append(f"🎨 **NFTs Owned**: {total_nfts}")
        
        # Add recent activity
        upload_history = data.get("upload_history", [])
        if upload_history:
            recent_uploads = len([u for u in upload_history if u.get("status") == "completed"])
            response_parts.append(f"")
            response_parts.append(f"📈 **Recent Activity**: {recent_uploads} successful uploads")
        
        # Add encouragement
        if total_credits > 0:
            response_parts.append(f"")
            response_parts.append(f"🎉 Great job on your sustainability efforts! Keep it up!")
        else:
            response_parts.append(f"")
            response_parts.append(f"🚀 Ready to start your sustainability journey? Upload your first document!")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"❌ Error formatting analytics response: {e}")
        return f"Here's your analytics summary: {total_credits} credits earned from {total_documents} documents."

if __name__ == "__main__":
    analytics_agent.run()
