"""
User Agent - Main orchestrator for all user interactions
Uses OpenAI to classify user intents and routes to specialized agents
"""

from uagents import Agent, Context, Model
from typing import Dict, Any, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMessage(Model):
    """Message model for chat interactions"""
    wallet_address: str
    message: str
    context: Dict[str, Any] = {}
    message_id: Optional[str] = None

class ChatResponse(Model):
    """Response model for chat interactions"""
    message: str
    data: Optional[Dict[str, Any]] = None
    agent_name: str
    success: bool = True
    error: Optional[str] = None

class IntentClassification(Model):
    """Model for intent classification results"""
    intent: str
    confidence: float
    extracted_data: Dict[str, Any] = {}

# Create User Agent
user_agent = Agent(
    name="user_agent",
    port=8005,
    seed="user_agent_seed_phrase_for_ecochain_sustainability_tracker",
    mailbox=True,
    publish_agent_details=True,
    readme_path="AGENT_README.md"
)

# Agentverse metadata for agent discovery
user_agent.agentverse_metadata = {
    "name": "EcoChain User Agent",
    "description": "Orchestrates user interactions and routes requests to specialized agents for sustainability tracking",
    "capabilities": [
        "intent_classification",
        "user_routing", 
        "chat_management",
        "sustainability_guidance",
        "multi_agent_coordination"
    ],
    "protocols": ["uAgents", "HTTP"],
    "version": "1.0.0",
    "endpoints": {
        "chat": "/agents/user/chat",
        "health": "/agents/user/health"
    },
    "tags": ["sustainability", "orchestration", "ai", "chat"]
}

# Agent addresses (will be set when other agents are created)
analytics_agent_address = None
upload_agent_address = None
reasoner_agent_address = None
recommendation_agent_address = None

@user_agent.on_message(model=ChatMessage)
async def handle_user_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle incoming user messages, classify intent, and route to appropriate agents
    """
    try:
        logger.info(f"🧠 User Agent received message: {msg.message[:50]}...")
        
        # Classify user intent using OpenAI
        intent_result = await classify_user_intent(msg.message)
        intent = intent_result.get("intent", "general_query")
        confidence = intent_result.get("confidence", 0.0)
        extracted_data = intent_result.get("extracted_data", {})
        
        logger.info(f"🎯 Intent classified as: {intent} (confidence: {confidence:.2f})")
        
        # Route to appropriate agent based on intent
        if intent == "get_credits":
            response = await route_to_analytics_agent(ctx, msg, extracted_data)
        elif intent == "upload_document":
            response = await route_to_upload_agent(ctx, msg, extracted_data)
        elif intent == "calculate_metrics":
            response = await route_to_reasoner_agent(ctx, msg, extracted_data)
        elif intent == "get_recommendations":
            response = await route_to_recommendation_agent(ctx, msg, extracted_data)
        elif intent == "blockchain_query":
            response = await handle_blockchain_query(msg, extracted_data)
        else:
            response = await handle_general_query(msg, extracted_data)
        
        # Send response back to sender
        await ctx.send(sender, response)

    except Exception as e:
        logger.error(f"❌ Error in User Agent: {e}")
        error_response = ChatResponse(
            message=f"Sorry, I encountered an error: {str(e)}",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )
        await ctx.send(sender, error_response)

async def classify_user_intent(message: str) -> Dict[str, Any]:
    """
    Use OpenAI to classify user intent and extract relevant data
    """
    try:
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()
        
        # Classify intent
        intent = await openai_service.classify_intent(message)
        
        # Extract relevant data from message
        extracted_data = await openai_service.extract_data(message, intent)
        
        return {
            "intent": intent,
            "confidence": 0.9,  # TODO: Get actual confidence from OpenAI
            "extracted_data": extracted_data
        }
        
    except Exception as e:
        logger.error(f"❌ Intent classification failed: {e}")
        # Fallback to simple keyword matching
        return await fallback_intent_classification(message)

async def fallback_intent_classification(message: str) -> Dict[str, Any]:
    """
    Fallback intent classification using keyword matching
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["credit", "token", "balance", "how much"]):
        return {
            "intent": "get_credits",
            "confidence": 0.7,
            "extracted_data": {}
        }
    elif any(word in message_lower for word in ["upload", "document", "file", "json"]):
        return {
            "intent": "upload_document",
            "confidence": 0.7,
            "extracted_data": {}
        }
    elif any(word in message_lower for word in ["calculate", "need", "target", "score"]):
        return {
            "intent": "calculate_metrics",
            "confidence": 0.7,
            "extracted_data": {}
        }
    elif any(word in message_lower for word in ["recommend", "improve", "increase", "tips"]):
        return {
            "intent": "get_recommendations",
            "confidence": 0.7,
            "extracted_data": {}
        }
    elif any(word in message_lower for word in ["transaction", "tx", "hash", "block", "nft", "token", "balance", "explorer"]):
        return {
            "intent": "blockchain_query",
            "confidence": 0.8,
            "extracted_data": {}
        }
    else:
        return {
            "intent": "general_query",
            "confidence": 0.5,
            "extracted_data": {}
        }

async def route_to_analytics_agent(ctx: Context, msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Route request to Analytics Agent"""
    try:
        if not analytics_agent_address:
            return ChatResponse(
                message="Analytics Agent is not available. Please try again later.",
                agent_name="user_agent",
                success=False,
                error="Analytics agent not configured"
            )
        
        # Send message to Analytics Agent
        response = await ctx.send(analytics_agent_address, msg)
        
        return ChatResponse(
            message=response.message,
            data=response.data,
            agent_name="analytics_agent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error routing to Analytics Agent: {e}")
        return ChatResponse(
            message="I couldn't retrieve your credit information. Please try again.",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )

async def route_to_upload_agent(ctx: Context, msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Route request to Upload Agent"""
    try:
        if not upload_agent_address:
            return ChatResponse(
                message="Upload Agent is not available. Please try again later.",
                agent_name="user_agent",
                success=False,
                error="Upload agent not configured"
            )
        
        # Send message to Upload Agent
        response = await ctx.send(upload_agent_address, msg)
        
        return ChatResponse(
            message=response.message,
            data=response.data,
            agent_name="upload_agent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error routing to Upload Agent: {e}")
        return ChatResponse(
            message="I couldn't process your upload. Please try again.",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )

async def route_to_reasoner_agent(ctx: Context, msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Route request to Reasoner Agent"""
    try:
        if not reasoner_agent_address:
            return ChatResponse(
                message="Reasoner Agent is not available. Please try again later.",
                agent_name="user_agent",
                success=False,
                error="Reasoner agent not configured"
            )
        
        # Send message to Reasoner Agent
        response = await ctx.send(reasoner_agent_address, msg)
        
        return ChatResponse(
            message=response.message,
            data=response.data,
            agent_name="reasoner_agent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error routing to Reasoner Agent: {e}")
        return ChatResponse(
            message="I couldn't calculate the metrics. Please try again.",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )

async def route_to_recommendation_agent(ctx: Context, msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Route request to Recommendation Agent"""
    try:
        if not recommendation_agent_address:
            return ChatResponse(
                message="Recommendation Agent is not available. Please try again later.",
                agent_name="user_agent",
                success=False,
                error="Recommendation agent not configured"
            )
        
        # Send message to Recommendation Agent
        response = await ctx.send(recommendation_agent_address, msg)
        
        return ChatResponse(
            message=response.message,
            data=response.data,
            agent_name="recommendation_agent",
            success=True
        )
        
    except Exception as e:
        logger.error(f"❌ Error routing to Recommendation Agent: {e}")
        return ChatResponse(
            message="I couldn't get recommendations. Please try again.",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )

async def handle_blockchain_query(msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Handle blockchain-related queries using MCP service"""
    try:
        from services.blockscout_mcp_service import query_blockchain_data
        
        message_lower = msg.message.lower()
        wallet_address = msg.wallet_address
        
        # Determine query type based on message content
        if any(word in message_lower for word in ["transaction", "tx", "hash"]):
            # Extract transaction hash from message
            import re
            tx_hash_match = re.search(r'0x[a-fA-F0-9]{64}', msg.message)
            if tx_hash_match:
                tx_hash = tx_hash_match.group()
                result = await query_blockchain_data("transaction", tx_hash=tx_hash)
                
                if result["status"] == "success":
                    tx = result["transaction"]
                    response_message = f"🔍 **Transaction Details**\n\n"
                    response_message += f"**Hash:** `{tx['hash']}`\n"
                    response_message += f"**From:** `{tx['from']}`\n"
                    response_message += f"**To:** `{tx['to']}`\n"
                    response_message += f"**Value:** {int(tx['value']) / 1e18:.6f} ETH\n"
                    response_message += f"**Gas Used:** {int(tx['gas_used']):,}\n"
                    response_message += f"**Block:** #{tx['block_number']:,}\n"
                    response_message += f"**Status:** {tx['status']}\n"
                    response_message += f"**Confirmations:** {tx['confirmations']}\n\n"
                    response_message += f"🔗 [View on Explorer]({result['explorer_url']})"
                    
                    return ChatResponse(
                        message=response_message,
                        data=result,
                        agent_name="user_agent",
                        success=True
                    )
                else:
                    return ChatResponse(
                        message=f"❌ {result['message']}",
                        agent_name="user_agent",
                        success=False,
                        error=result['message']
                    )
            else:
                return ChatResponse(
                    message="Please provide a valid transaction hash (0x...) to look up transaction details.",
                    agent_name="user_agent",
                    success=False,
                    error="No transaction hash found in message"
                )
        
        elif any(word in message_lower for word in ["balance", "token"]):
            # Query token balance
            result = await query_blockchain_data("token_balance", 
                                               address=wallet_address,
                                               token_address="0x...")  # ECO token address
            
            if result["status"] == "success":
                balance = result["balance"]
                response_message = f"💰 **Token Balance**\n\n"
                response_message += f"**Address:** `{balance['address']}`\n"
                response_message += f"**Token:** {balance['name']} ({balance['symbol']})\n"
                response_message += f"**Balance:** {balance['balance_formatted']} {balance['symbol']}\n\n"
                response_message += f"🔗 [View on Explorer]({result['explorer_url']})"
                
                return ChatResponse(
                    message=response_message,
                    data=result,
                    agent_name="user_agent",
                    success=True
                )
            else:
                return ChatResponse(
                    message=f"❌ {result['message']}",
                    agent_name="user_agent",
                    success=False,
                    error=result['message']
                )
        
        elif any(word in message_lower for word in ["nft", "collection"]):
            # Query NFT collection
            result = await query_blockchain_data("nft_collection",
                                               address=wallet_address,
                                               contract_address="0x...")  # NFT contract address
            
            if result["status"] == "success":
                collection = result["collection"]
                response_message = f"🎨 **NFT Collection**\n\n"
                response_message += f"**Owner:** `{collection['owner']}`\n"
                response_message += f"**Total NFTs:** {collection['total_nfts']}\n\n"
                
                if collection['nfts']:
                    response_message += "**Recent NFTs:**\n"
                    for nft in collection['nfts'][:3]:  # Show first 3 NFTs
                        response_message += f"• {nft['name']} (ID: {nft['token_id']})\n"
                
                response_message += f"\n🔗 [View on Explorer]({result['explorer_url']})"
                
                return ChatResponse(
                    message=response_message,
                    data=result,
                    agent_name="user_agent",
                    success=True
                )
            else:
                return ChatResponse(
                    message=f"❌ {result['message']}",
                    agent_name="user_agent",
                    success=False,
                    error=result['message']
                )
        
        else:
            return ChatResponse(
                message="I can help you with blockchain queries! Try asking about:\n\n• Transaction details: 'Show me transaction 0x...'\n• Token balance: 'What's my token balance?'\n• NFT collection: 'Show my NFTs'\n• Recent transactions: 'Show my recent transactions'",
                agent_name="user_agent",
                success=True
            )
    
    except Exception as e:
        logger.error(f"❌ Error in blockchain query: {e}")
        return ChatResponse(
            message="Sorry, I couldn't process your blockchain query. Please try again.",
            agent_name="user_agent",
            success=False,
            error=str(e)
        )

async def handle_general_query(msg: ChatMessage, extracted_data: Dict[str, Any]) -> ChatResponse:
    """Handle general sustainability queries"""
    return ChatResponse(
        message="I'm here to help with your sustainability tracking! You can ask me about:\n\n• Your carbon credits and token balance\n• Upload sustainability documents for analysis\n• Calculate what metrics you need for target credits\n• Get recommendations to improve your sustainability score\n• Blockchain queries: transactions, NFTs, balances\n\nWhat would you like to know?",
        agent_name="user_agent",
        success=True
    )

def set_agent_addresses(analytics_addr, upload_addr, reasoner_addr, recommendation_addr):
    """Set addresses of other agents for routing"""
    global analytics_agent_address, upload_agent_address, reasoner_agent_address, recommendation_agent_address
    analytics_agent_address = analytics_addr
    upload_agent_address = upload_addr
    reasoner_agent_address = reasoner_addr
    recommendation_agent_address = recommendation_addr
    logger.info("✅ User Agent addresses configured")

if __name__ == "__main__":
    user_agent.run()
