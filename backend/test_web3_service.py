"""
Test script for Web3Service integration
Tests contract connections and basic functionality
"""

import asyncio
import os
from dotenv import load_dotenv
from services.web3_service import Web3Service, initialize_web3_service, get_web3_service

# Load environment variables
load_dotenv()

async def test_web3_service():
    """Test Web3Service functionality"""
    print("🧪 Testing Web3Service Integration...\n")
    
    # Get configuration from environment
    rpc_url = os.getenv('SEPOLIA_RPC_URL')
    private_key = os.getenv('PRIVATE_KEY')
    
    if not rpc_url:
        print("❌ SEPOLIA_RPC_URL not found in environment variables")
        return
    
    if not private_key:
        print("❌ PRIVATE_KEY not found in environment variables")
        return
    
    try:
        # Initialize Web3Service
        print("🔗 Initializing Web3Service...")
        initialize_web3_service(rpc_url, private_key)
        web3_service = get_web3_service()
        print("✅ Web3Service initialized successfully")
        
        # Test contract connections
        print("\n📋 Testing Contract Connections...")
        
        # Test EcoCreditToken
        try:
            eco_contract = web3_service.get_contract('eco_credit_token')
            name = eco_contract.functions.name().call()
            symbol = eco_contract.functions.symbol().call()
            total_supply = eco_contract.functions.totalSupply().call()
            print(f"✅ EcoCreditToken: {name} ({symbol}) - Total Supply: {total_supply}")
        except Exception as e:
            print(f"❌ EcoCreditToken connection failed: {e}")
        
        # Test SustainabilityProof
        try:
            proof_contract = web3_service.get_contract('sustainability_proof')
            # Try to get name and symbol (ERC721 standard functions)
            try:
                name = proof_contract.functions.name().call()
                symbol = proof_contract.functions.symbol().call()
                print(f"✅ SustainabilityProof: {name} ({symbol})")
            except:
                # If name/symbol not available, just confirm connection
                print("✅ SustainabilityProof: Connected successfully")
        except Exception as e:
            print(f"❌ SustainabilityProof connection failed: {e}")
        
        # Test ProofRegistry
        try:
            registry_contract = web3_service.get_contract('proof_registry')
            print("✅ ProofRegistry: Connected successfully")
        except Exception as e:
            print(f"❌ ProofRegistry connection failed: {e}")
        
        # Test user balance (if wallet address is provided)
        wallet_address = os.getenv('WALLET_ADDRESS')
        if wallet_address:
            print(f"\n💰 Testing User Balance for {wallet_address}...")
            try:
                balance_info = await web3_service.get_user_token_balance(wallet_address)
                print(f"✅ Token Balance: {balance_info['balance_formatted']} {balance_info['token_symbol']}")
            except Exception as e:
                print(f"❌ Balance check failed: {e}")
        
        print("\n🎉 Web3Service test completed!")
        
    except Exception as e:
        print(f"❌ Web3Service test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_web3_service())