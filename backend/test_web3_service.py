"""
Test script for Web3Service integration
Tests contract connections and basic functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from services.web3_service import Web3Service, initialize_web3_service, get_web3_service
from core.config import settings

# Load environment variables
load_dotenv()

async def test_web3_connection():
    print("🔍 Testing Web3Service Connection...")
    
    # Check if we have the required config
    print(f"RPC URL: {settings.sepolia_rpc_url}")
    print(f"Private Key: {'Set' if settings.private_key else 'Not Set'}")
    print(f"EcoCredit Address: {settings.eco_credit_token_address}")
    
    if not settings.sepolia_rpc_url or not settings.private_key:
        print("❌ Missing required configuration")
        return
    
    try:
        # Initialize Web3Service
        web3_service = Web3Service(settings.sepolia_rpc_url, settings.private_key)
        
        # Test connection
        is_connected = web3_service.w3.is_connected()
        print(f"✅ Web3 Connected: {is_connected}")
        
        if is_connected:
            # Get latest block
            latest_block = web3_service.w3.eth.block_number
            print(f"📦 Latest Block: {latest_block}")
            
            # Test contract connection
            contract = web3_service.get_contract('eco_credit_token')
            print(f"📄 Contract Connected: {contract.address}")
            
            # Test a simple read operation
            total_supply = contract.functions.totalSupply().call()
            print(f"🪙 Total Supply: {total_supply}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_web3_connection())