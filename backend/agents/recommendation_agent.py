"""
Recommendation Agent - Provides sustainability recommendations and tips
Queries MeTTa knowledge base for personalized advice
"""

from uagents import Agent, Context, Model
from typing import Dict, Any, Optional
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationRequest(Model):
    """Request model for recommendation queries"""
    wallet_address: str
    message: str
    context: Dict[str, Any] = {}
    focus_area: Optional[str] = None
    current_score: Optional[int] = None
    message_id: Optional[str] = None

class RecommendationResponse(Model):
    """Response model for recommendation queries"""
    message: str
    data: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None

# Create Recommendation Agent
recommendation_agent = Agent(
    name="recommendation_agent",
    port=8008,
    seed="recommendation_agent_seed_phrase_for_ecochain_sustainability_tracker"
)

@recommendation_agent.on_message(model=RecommendationRequest)
async def handle_recommendation_request(ctx: Context, sender: str, msg: RecommendationRequest):
    """
    Handle recommendation requests and provide sustainability advice
    """
    try:
        logger.info(f"💡 Recommendation Agent received request from wallet: {msg.wallet_address}")
        
        # Get user's current analytics for context
        user_analytics = await get_user_analytics(msg.wallet_address)
        
        # Generate recommendations
        recommendations = await generate_recommendations(
            msg.message,
            msg.focus_area,
            user_analytics
        )
        
        if recommendations.get("success", False):
            # Format response message
            response_message = format_recommendation_response(recommendations["data"])
            
            response = RecommendationResponse(
                message=response_message,
                data=recommendations["data"],
                success=True
            )
        else:
            response = RecommendationResponse(
                message="I couldn't generate recommendations at the moment. Please try again later.",
                success=False,
                error=recommendations.get("error", "Unknown error")
            )
        
        # Send response back to sender (User Agent)
        await ctx.send(sender, response)
        
    except Exception as e:
        logger.error(f"❌ Error in Recommendation Agent: {e}")
        error_response = RecommendationResponse(
            message=f"Sorry, I encountered an error generating recommendations: {str(e)}",
            success=False,
            error=str(e)
        )
        await ctx.send(sender, error_response)

async def get_user_analytics(wallet_address: str) -> Optional[Dict[str, Any]]:
    """
    Get user analytics for personalized recommendations
    """
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8002/analytics/user/{wallet_address}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Could not fetch analytics for recommendations: {response.status}")
                    return None
                    
    except Exception as e:
        logger.warning(f"Failed to get user analytics for recommendations: {e}")
        return None

async def generate_recommendations(
    message: str, 
    focus_area: Optional[str], 
    user_analytics: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate personalized sustainability recommendations
    """
    try:
        # Get recommendations from MeTTa knowledge base
        metta_recommendations = await get_metta_recommendations(message, focus_area)
        
        # Combine with user-specific recommendations
        personalized_recommendations = generate_personalized_tips(user_analytics, focus_area)
        
        # Merge recommendations
        all_recommendations = {
            "general_tips": metta_recommendations.get("tips", []),
            "personalized_tips": personalized_recommendations,
            "focus_area": focus_area or "general",
            "priority_actions": get_priority_actions(user_analytics, focus_area)
        }
        
        return {
            "success": True,
            "data": all_recommendations
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to generate recommendations: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def get_metta_recommendations(message: str, focus_area: Optional[str]) -> Dict[str, Any]:
    """
    Get recommendations from MeTTa knowledge base
    """
    try:
        import aiohttp
        
        # Prepare query for MeTTa
        query_data = {
            "query": message,
            "focus_area": focus_area or "general",
            "type": "recommendations"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8003/api/query",
                json=query_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"MeTTa recommendations failed: {response.status}")
                    return {"tips": get_fallback_recommendations(focus_area)}
                    
    except Exception as e:
        logger.warning(f"MeTTa recommendations unavailable: {e}")
        return {"tips": get_fallback_recommendations(focus_area)}

def get_fallback_recommendations(focus_area: Optional[str]) -> list:
    """
    Fallback recommendations when MeTTa is unavailable
    """
    general_tips = [
        "🌱 Track your carbon footprint regularly using sustainability tools",
        "♻️ Implement a comprehensive recycling program at home and work",
        "⚡ Switch to renewable energy sources like solar or wind power",
        "🚗 Reduce transportation emissions by using public transport or carpooling",
        "💧 Conserve water by fixing leaks and using water-efficient appliances",
        "🌿 Plant trees and maintain green spaces to offset carbon emissions"
    ]
    
    if focus_area == "carbon_footprint":
        return [
            "📊 Use carbon tracking apps to monitor daily emissions",
            "🚗 Switch to electric or hybrid vehicles",
            "✈️ Reduce air travel and choose direct flights when possible",
            "🏠 Improve home insulation and energy efficiency",
            "🌱 Support carbon offset programs and reforestation projects"
        ]
    elif focus_area == "waste_reduction":
        return [
            "♻️ Implement a zero-waste lifestyle with reusable containers",
            "📦 Choose products with minimal packaging",
            "🍽️ Compost organic waste to reduce landfill contributions",
            "🛒 Buy in bulk to reduce packaging waste",
            "♻️ Repair and repurpose items instead of throwing them away"
        ]
    elif focus_area == "renewable_energy":
        return [
            "☀️ Install solar panels on your home or business",
            "💡 Switch to LED lighting and energy-efficient appliances",
            "🌬️ Consider wind energy options for your property",
            "🔋 Use smart energy management systems",
            "⚡ Participate in community renewable energy programs"
        ]
    else:
        return general_tips

def generate_personalized_tips(user_analytics: Optional[Dict[str, Any]], focus_area: Optional[str]) -> list:
    """
    Generate personalized tips based on user's current performance
    """
    if not user_analytics:
        return []
    
    tips = []
    summary = user_analytics.get("summary", {})
    
    # Analyze user's current performance
    total_credits = summary.get("total_credits_earned", 0)
    total_documents = summary.get("total_documents_uploaded", 0)
    success_rate = summary.get("success_rate", 0)
    
    # Generate personalized recommendations
    if total_documents == 0:
        tips.append("🚀 Start by uploading your first sustainability document to begin earning credits!")
    elif total_credits < 50:
        tips.append("📈 Focus on improving your sustainability metrics to earn more credits")
    elif success_rate < 80:
        tips.append("✅ Work on document quality to improve your success rate")
    else:
        tips.append("🌟 Great job! Consider sharing your sustainability practices with others")
    
    # Focus area specific tips
    if focus_area == "carbon_footprint" and total_credits < 100:
        tips.append("🌱 Your carbon footprint reduction efforts are paying off! Keep tracking and improving.")
    
    return tips

def get_priority_actions(user_analytics: Optional[Dict[str, Any]], focus_area: Optional[str]) -> list:
    """
    Get priority actions based on user's current state
    """
    actions = []
    
    if not user_analytics:
        actions = [
            "📄 Upload your first sustainability document",
            "🌱 Set up carbon footprint tracking",
            "♻️ Start a waste reduction program"
        ]
    else:
        summary = user_analytics.get("summary", {})
        total_documents = summary.get("total_documents_uploaded", 0)
        
        if total_documents < 3:
            actions.append("📊 Upload more documents to build a comprehensive sustainability profile")
        
        if focus_area:
            actions.append(f"🎯 Focus on improving your {focus_area.replace('_', ' ')} metrics")
        
        actions.append("📈 Set a target for your next credit milestone")
    
    return actions

def format_recommendation_response(data: Dict[str, Any]) -> str:
    """
    Format recommendations into a user-friendly message
    """
    try:
        general_tips = data.get("general_tips", [])
        personalized_tips = data.get("personalized_tips", [])
        priority_actions = data.get("priority_actions", [])
        focus_area = data.get("focus_area", "general")
        
        response_parts = [
            f"💡 **Sustainability Recommendations**",
            f"",
        ]
        
        # Add personalized tips first
        if personalized_tips:
            response_parts.append("🎯 **Personalized for You:**")
            for tip in personalized_tips:
                response_parts.append(f"• {tip}")
            response_parts.append("")
        
        # Add general tips
        if general_tips:
            response_parts.append(f"🌱 **{focus_area.replace('_', ' ').title()} Tips:**")
            for tip in general_tips[:5]:  # Limit to top 5
                response_parts.append(f"• {tip}")
            response_parts.append("")
        
        # Add priority actions
        if priority_actions:
            response_parts.append("🚀 **Priority Actions:**")
            for action in priority_actions:
                response_parts.append(f"• {action}")
            response_parts.append("")
        
        # Add encouragement
        response_parts.append("💪 Every small step towards sustainability makes a difference!")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"❌ Error formatting recommendation response: {e}")
        return "Here are some sustainability recommendations to help you improve your impact!"

if __name__ == "__main__":
    recommendation_agent.run()
