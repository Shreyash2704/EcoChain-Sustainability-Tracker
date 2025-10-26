"""
Main FastAPI application entry point for EcoChain Sustainability Tracker.
"""

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from uagents import Bureau
from agents.user_agent import user_agent
from agents.verifier_agent import verifier_agent
from agents.reasoner_agent import reasoner_agent
from agents.minting_agent import minting_agent
from agents.analytics_agent import analytics_agent
from agents.upload_agent import upload_agent
from agents.recommendation_agent import recommendation_agent
import asyncio

# Import API routers
from api.uploads import router as uploads_router
from api.analytics import router as analytics_router
from api.chat import router as chat_router
from api.blockscout import router as blockscout_router

# Import core configuration and services
from core.config import settings, is_development
from core.logging import get_logger
from services.web3_service import initialize_web3_service
from services.agentverse_service import register_all_agents, get_agentverse_service

logger = get_logger(__name__)

app = FastAPI(
    title="EcoChain Sustainability Tracker",
    description="API for sustainability tracking and verification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routers with /api prefix
app.include_router(uploads_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(blockscout_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "EcoChain Sustainability Tracker API"}

@app.post("/chat")
async def chat_with_agent(message: str = Body(..., embed=True)):
    """Chat with the user agent"""
    try:
        # This would integrate with the user agent
        return {"response": f"EcoChain received: {message}"}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug
    }

def initialize_services():
    """Initialize Web3Service and configure agents"""
    try:
        # Initialize Web3Service if configuration is available
        if settings.sepolia_rpc_url and settings.private_key:
            logger.info("Initializing Web3Service with Sepolia configuration...")
            initialize_web3_service(settings.sepolia_rpc_url, settings.private_key)
            logger.info("✅ Web3Service initialized successfully")
        else:
            logger.warning("⚠️ Web3Service not initialized - missing RPC URL or private key")
        
        # Configure agent addresses for User Agent routing
        from agents.user_agent import set_agent_addresses
        set_agent_addresses(
            analytics_agent.address,
            upload_agent.address,
            reasoner_agent.address,
            recommendation_agent.address
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise

async def initialize_agentverse():
    """Initialize Agentverse integration and register agents"""
    try:
        if settings.agentverse_enabled:
            logger.info("🌐 Initializing Agentverse integration...")
            agentverse_service = await get_agentverse_service()
            
            if await agentverse_service.is_available():
                registered_agents = await register_all_agents()
                if registered_agents:
                    logger.info(f"✅ Registered {len(registered_agents)} agents on Agentverse")
                    for agent_name, agent_address in registered_agents.items():
                        logger.info(f"   • {agent_name}: {agent_address}")
                else:
                    logger.warning("⚠️ No agents registered on Agentverse")
            else:
                logger.warning("⚠️ Agentverse service not available")
        else:
            logger.info("ℹ️ Agentverse integration disabled")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize Agentverse: {e}")
        # Don't raise - Agentverse is optional

async def start_bureau():
    """Start the uAgents Bureau with all agents"""
    try:
        # Initialize Agentverse integration
        await initialize_agentverse()
        
        # Create and configure Bureau
        bureau = Bureau(port=settings.bureau_port)
        
        # Add agents to Bureau
        bureau.add(user_agent)
        bureau.add(verifier_agent)
        bureau.add(reasoner_agent)
        bureau.add(minting_agent)
        bureau.add(analytics_agent)
        bureau.add(upload_agent)
        bureau.add(recommendation_agent)
        
        logger.info(f"🚀 Starting Bureau on port {settings.bureau_port}")
        await bureau.run_async()
        
    except Exception as e:
        logger.error(f"❌ Failed to start Bureau: {e}")
        raise

if __name__ == "__main__":
    # Initialize services (synchronous)
    initialize_services()
    
    # Start Bureau in background
    loop = asyncio.get_event_loop()
    loop.create_task(start_bureau())
    
    # Start FastAPI server
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    )