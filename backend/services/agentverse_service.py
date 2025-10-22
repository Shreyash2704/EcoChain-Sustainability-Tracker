"""
Agentverse integration service for EcoChain agents.
Handles agent registration, discovery, and communication via Fetch.ai's Agentverse platform.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentverseService:
    """Service for managing agent registration and communication via Agentverse."""
    
    def __init__(self):
        self.api_key = settings.agentverse_api_key
        self.base_url = settings.agentverse_base_url
        self.enabled = settings.agentverse_enabled
        self.agent_addresses: Dict[str, str] = {}
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
    
    async def is_available(self) -> bool:
        """Check if Agentverse service is available and configured."""
        if not self.enabled or not self.api_key:
            return False
        
        try:
            # Try to access the main Agentverse page to check connectivity
            response = await self.client.get("/")
            return response.status_code in [200, 302, 307]  # Accept redirects as available
        except Exception as e:
            logger.warning(f"Agentverse connectivity check failed: {e}")
            # For demo purposes, return True to allow mock agent creation
            return True
        
        # If we get here, Agentverse is not available but we'll create mock agents for demo
        logger.info("Agentverse not available, will create mock agent addresses for demo")
        return True
    
    async def register_agent(
        self, 
        agent_name: str, 
        agent_description: str, 
        capabilities: List[str],
        endpoint_url: str
    ) -> Optional[str]:
        """Register an agent on Agentverse and return its address."""
        if not await self.is_available():
            logger.warning("Agentverse not available, creating mock agent address for demo")
            # For demo purposes, generate a mock agent address
            import hashlib
            agent_hash = hashlib.md5(f"{agent_name}{endpoint_url}".encode()).hexdigest()[:16]
            agent_address = f"agent_{agent_hash}"
            self.agent_addresses[agent_name] = agent_address
            logger.info(f"Created mock agent address for {agent_name}: {agent_address}")
            return agent_address
        
        try:
            payload = {
                "name": agent_name,
                "description": agent_description,
                "capabilities": capabilities,
                "endpoint_url": endpoint_url,
                "protocol": "uAgents",
                "version": "1.0"
            }
            
            response = await self.client.post("/api/agents/register", json=payload)
            
            if response.status_code == 201:
                agent_data = response.json()
                agent_address = agent_data.get("address")
                self.agent_addresses[agent_name] = agent_address
                logger.info(f"Successfully registered {agent_name} on Agentverse: {agent_address}")
                return agent_address
            else:
                logger.error(f"Failed to register {agent_name}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error registering agent {agent_name}: {e}")
            return None
    
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get the status of a registered agent."""
        if agent_name not in self.agent_addresses:
            return {"status": "not_registered"}
        
        try:
            agent_address = self.agent_addresses[agent_name]
            response = await self.client.get(f"/api/agents/{agent_address}/status")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"Error getting status for {agent_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_message(
        self, 
        agent_name: str, 
        message: str, 
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """Send a message to an agent via Agentverse."""
        if agent_name not in self.agent_addresses:
            logger.error(f"Agent {agent_name} not registered on Agentverse")
            return None
        
        try:
            agent_address = self.agent_addresses[agent_name]
            payload = {
                "message": message,
                "type": message_type,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            response = await self.client.post(
                f"/api/agents/{agent_address}/message", 
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to send message to {agent_name}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error sending message to {agent_name}: {e}")
            return None
    
    async def discover_agents(self, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover agents on Agentverse, optionally filtered by capability."""
        if not await self.is_available():
            return []
        
        try:
            params = {"capability": capability} if capability else {}
            response = await self.client.get("/api/agents/discover", params=params)
            
            if response.status_code == 200:
                return response.json().get("agents", [])
            else:
                logger.error(f"Failed to discover agents: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error discovering agents: {e}")
            return []
    
    async def get_agent_metadata(self, agent_name: str) -> Dict[str, Any]:
        """Get metadata for a registered agent."""
        if agent_name not in self.agent_addresses:
            return {}
        
        try:
            agent_address = self.agent_addresses[agent_name]
            response = await self.client.get(f"/api/agents/{agent_address}/metadata")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting metadata for {agent_name}: {e}")
            return {}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global Agentverse service instance
agentverse_service = AgentverseService()


async def get_agentverse_service() -> AgentverseService:
    """Get the global Agentverse service instance."""
    return agentverse_service


async def register_all_agents() -> Dict[str, str]:
    """Register all EcoChain agents on Agentverse."""
    if not settings.agentverse_enabled:
        logger.info("Agentverse integration disabled")
        return {}
    
    agents_config = {
        "user_agent": {
            "description": "Orchestrates user interactions and routes requests to specialized agents",
            "capabilities": ["intent_classification", "user_routing", "chat_management"],
            "endpoint": f"http://{settings.host}:{settings.port}/agents/user"
        },
        "reasoner_agent": {
            "description": "Analyzes sustainability documents using MeTTa reasoning engine",
            "capabilities": ["sustainability_analysis", "carbon_footprint_calculation", "impact_assessment"],
            "endpoint": f"http://{settings.host}:{settings.port}/agents/reasoner"
        },
        "minting_agent": {
            "description": "Handles ECO token minting and NFT creation for sustainability proofs",
            "capabilities": ["token_minting", "nft_creation", "blockchain_transactions"],
            "endpoint": f"http://{settings.host}:{settings.port}/agents/minting"
        },
        "analytics_agent": {
            "description": "Provides user analytics, leaderboards, and system statistics",
            "capabilities": ["user_analytics", "leaderboard_generation", "statistics"],
            "endpoint": f"http://{settings.host}:{settings.port}/agents/analytics"
        }
    }
    
    registered_agents = {}
    
    for agent_name, config in agents_config.items():
        try:
            agent_address = await agentverse_service.register_agent(
                agent_name=agent_name,
                agent_description=config["description"],
                capabilities=config["capabilities"],
                endpoint_url=config["endpoint"]
            )
            
            if agent_address:
                registered_agents[agent_name] = agent_address
                logger.info(f"✅ Registered {agent_name} on Agentverse: {agent_address}")
            else:
                logger.warning(f"❌ Failed to register {agent_name} on Agentverse")
                
        except Exception as e:
            logger.error(f"Error registering {agent_name}: {e}")
    
    return registered_agents
