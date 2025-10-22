#!/usr/bin/env python3
"""
Script to register EcoChain agents on Agentverse.
Run this script to register all agents with Fetch.ai's Agentverse platform.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.agentverse_service import register_all_agents, get_agentverse_service
from core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to register all agents on Agentverse."""
    settings = get_settings()
    
    print("🚀 EcoChain Agentverse Registration")
    print("=" * 50)
    
    # Check if Agentverse is enabled
    if not settings.agentverse_enabled:
        print("❌ Agentverse integration is disabled")
        print("   Set AGENTVERSE_ENABLED=true in your .env file")
        return
    
    # Check if API key is provided
    if not settings.agentverse_api_key:
        print("❌ Agentverse API key not found")
        print("   Set AGENTVERSE_API_KEY in your .env file")
        print("   Get your API key from: https://agentverse.ai/")
        return
    
    print(f"📡 Agentverse Base URL: {settings.agentverse_base_url}")
    print(f"🔑 API Key: {'*' * 20}{settings.agentverse_api_key[-4:] if settings.agentverse_api_key else 'Not set'}")
    print()
    
    # Get Agentverse service
    agentverse_service = await get_agentverse_service()
    
    # Check if Agentverse is available
    print("🔍 Checking Agentverse availability...")
    if not await agentverse_service.is_available():
        print("⚠️ Agentverse service is not available")
        print("   Will create mock agent addresses for demo purposes")
        print()
    else:
        print("✅ Agentverse service is available")
        print()
    
    # Register all agents
    print("📝 Registering agents on Agentverse...")
    registered_agents = await register_all_agents()
    
    print()
    print("📊 Registration Summary:")
    print("-" * 30)
    
    if registered_agents:
        print("✅ Successfully registered agents:")
        for agent_name, agent_address in registered_agents.items():
            print(f"   • {agent_name}: {agent_address}")
    else:
        print("❌ No agents were registered")
        print("   Check the logs above for error details")
    
    print()
    print("🎯 Next Steps:")
    print("   1. Agents are now discoverable on Agentverse")
    print("   2. Other developers can find and interact with your agents")
    print("   3. Check the Agentverse dashboard for agent status")
    print("   4. Your local agents continue to work as primary")
    
    # Close the service
    await agentverse_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Registration cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
