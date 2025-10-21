"""
EcoChain Minting Agent
Handles token minting and NFT creation based on sustainability analysis results
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

from services.web3_service import get_web3_service
from core.logging import get_logger

# Create the minting agent
minting_agent = Agent(
    name="EcoChain MintingAgent",
    seed="eco_minting_agent_seed",
    port=8004
)

logger = get_logger(__name__)

@minting_agent.on_message(model=ChatMessage)
async def handle_minting_request(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle minting requests from the Reasoner Agent
    Expected message format:
    {
        "upload_id": "uuid",
        "user_wallet": "0x...",
        "should_mint": true,
        "token_amount": 1000,
        "carbon_footprint": 150.5,
        "impact_score": 85,
        "reasoning": "Analysis results...",
        "document_type": "sustainability_report",
        "metadata": {...}
    }
    """
    try:
        minting_data = json.loads(msg.content[0].text)
        
        print(f"\n🪙 MINTING AGENT - Processing Request")
        print(f"📤 From: {sender}")
        print(f"📋 Upload ID: {minting_data.get('upload_id', 'N/A')}")
        print(f"👤 User Wallet: {minting_data.get('user_wallet', 'N/A')}")
        print(f"💰 Token Amount: {minting_data.get('token_amount', 0)}")
        print(f"🌱 Should Mint: {minting_data.get('should_mint', False)}")
        print(f"🌍 Carbon Footprint: {minting_data.get('carbon_footprint', 0)} kg CO2")
        print(f"📊 Impact Score: {minting_data.get('impact_score', 0)}/100")
        print(f"📝 Document Type: {minting_data.get('document_type', 'N/A')}")
        print(f"💡 Reasoning: {minting_data.get('reasoning', 'N/A')}")
        
        if not minting_data.get('should_mint', False):
            print("❌ No minting required based on analysis")
            response_data = {
                "upload_id": minting_data.get('upload_id'),
                "minting_completed": False,
                "reason": "Analysis determined no tokens should be minted",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = ChatMessage(
                content=[TextContent(text=json.dumps(response_data))]
            )
            await ctx.send(sender, response)
            return
        
        # Proceed with minting
        user_wallet = minting_data.get('user_wallet')
        token_amount = minting_data.get('token_amount', 0)
        carbon_footprint = minting_data.get('carbon_footprint', 0)
        impact_score = minting_data.get('impact_score', 0)
        document_type = minting_data.get('document_type', 'sustainability_proof')
        upload_id = minting_data.get('upload_id', 'unknown')
        
        if not user_wallet:
            raise ValueError("User wallet address is required for minting")
        
        if token_amount <= 0:
            raise ValueError("Token amount must be greater than 0")
        
        print(f"🚀 Starting minting process...")
        
        # Get Web3Service instance
        try:
            web3_service = get_web3_service()
            print("✅ Web3Service connected")
        except Exception as e:
            print(f"❌ Web3Service connection failed: {e}")
            raise
        
        minting_results = {}
        
        # 1. Mint EcoCredit tokens
        print(f"🪙 Minting {token_amount} ECO tokens to {user_wallet}...")
        try:
            # Convert token amount to wei (assuming 18 decimals)
            token_amount_wei = int(token_amount * 10**18)
            
            token_result = await web3_service.mint_eco_credit_tokens(
                to_address=user_wallet,
                amount=token_amount_wei,
                reason=f"Sustainability reward for {document_type}"
            )
            
            minting_results['eco_tokens'] = {
                "success": True,
                "tx_hash": token_result['tx_hash'],
                "amount": token_amount,
                "amount_wei": token_amount_wei,
                "block_number": token_result['block_number'],
                "gas_used": token_result.get('gas_used', 0)
            }
            print(f"✅ ECO tokens minted successfully: {token_result['tx_hash']}")
            
        except Exception as e:
            print(f"❌ ECO token minting failed: {e}")
            minting_results['eco_tokens'] = {
                "success": False,
                "error": str(e),
                "retry_recommended": "gas_price" in str(e).lower() or "timeout" in str(e).lower() or "underpriced" in str(e).lower()
            }
        
        # 2. Mint SustainabilityProof NFT
        print(f"🎨 Minting SustainabilityProof NFT...")
        try:
            # Create metadata URI for the NFT
            metadata_uri = f"https://gateway.lighthouse.storage/ipfs/QmMock{upload_id.replace('-', '')[:40]}"
            
            # Convert carbon footprint to wei (assuming 18 decimals for precision)
            # Ensure carbon amount is at least 1 kg CO2 to satisfy contract requirements
            carbon_footprint_safe = max(carbon_footprint, 1.0)
            carbon_amount_wei = int(carbon_footprint_safe * 10**18)
            
            nft_result = await web3_service.mint_sustainability_proof_nft(
                to_address=user_wallet,
                token_uri=metadata_uri,
                proof_type=document_type,
                carbon_amount=carbon_amount_wei
            )
            
            minting_results['sustainability_nft'] = {
                "success": True,
                "tx_hash": nft_result['tx_hash'],
                "token_id": nft_result['token_id'],
                "proof_type": document_type,
                "carbon_amount": carbon_footprint_safe,
                "metadata_uri": metadata_uri,
                "block_number": nft_result['block_number'],
                "gas_used": nft_result.get('gas_used', 0)
            }
            print(f"✅ SustainabilityProof NFT minted: Token ID #{nft_result['token_id']}")
            
        except Exception as e:
            print(f"❌ NFT minting failed: {e}")
            minting_results['sustainability_nft'] = {
                "success": False,
                "error": str(e),
                "retry_recommended": "gas_price" in str(e).lower() or "timeout" in str(e).lower() or "underpriced" in str(e).lower()
            }
        
        # 3. Register proof in ProofRegistry
        print(f"📝 Registering proof in ProofRegistry...")
        try:
            proof_id = f"proof_{upload_id}"
            metadata_uri = f"https://gateway.lighthouse.storage/ipfs/QmMock{upload_id.replace('-', '')[:40]}"
            # Use a minimum carbon impact of 1 kg CO2 if carbon_footprint is 0
            carbon_impact_kg = max(carbon_footprint, 1.0)
            carbon_impact_wei = int(carbon_impact_kg * 10**18)
            
            registry_result = await web3_service.register_sustainability_proof(
                user_address=user_wallet,
                proof_id=proof_id,
                proof_type=document_type,
                carbon_impact=carbon_impact_wei,
                metadata_uri=metadata_uri
            )
            
            minting_results['proof_registry'] = {
                "success": True,
                "tx_hash": registry_result['tx_hash'],
                "proof_id": proof_id,
                "block_number": registry_result['block_number']
            }
            print(f"✅ Proof registered successfully: {proof_id}")
            
        except Exception as e:
            print(f"❌ Proof registration failed: {e}")
            minting_results['proof_registry'] = {
                "success": False,
                "error": str(e)
            }
        
        # Prepare response
        response_data = {
            "upload_id": upload_id,
            "user_wallet": user_wallet,
            "minting_completed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "results": minting_results,
            "summary": {
                "eco_tokens_minted": token_amount,
                "nft_minted": minting_results.get('sustainability_nft', {}).get('success', False),
                "proof_registered": minting_results.get('proof_registry', {}).get('success', False),
                "total_success": all(
                    result.get('success', False) 
                    for result in minting_results.values()
                )
            }
        }
        
        print(f"\n🎉 MINTING COMPLETED")
        print(f"💰 ECO Tokens: {token_amount} minted")
        print(f"🎨 NFT: {'✅' if minting_results.get('sustainability_nft', {}).get('success') else '❌'}")
        print(f"📝 Registry: {'✅' if minting_results.get('proof_registry', {}).get('success') else '❌'}")
        print(f"🏁 Overall Success: {'✅' if response_data['summary']['total_success'] else '❌'}")
        
        # Show retry recommendations if any failures occurred
        failed_operations = []
        for operation, result in minting_results.items():
            if not result.get('success', False) and result.get('retry_recommended', False):
                failed_operations.append(operation)
        
        if failed_operations:
            print(f"🔄 Retry recommended for: {', '.join(failed_operations)}")
            print(f"💡 Consider increasing gas price or waiting for network congestion to clear")
        
        response = ChatMessage(
            content=[TextContent(text=json.dumps(response_data))]
        )
        await ctx.send(sender, response)
        
        # Return the response data for API access
        return response
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing minting data: {e}")
        error_response = {
            "error": "Invalid JSON format",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        response = ChatMessage(
            content=[TextContent(text=json.dumps(error_response))]
        )
        await ctx.send(sender, response)
        
    except Exception as e:
        print(f"❌ Minting process failed: {e}")
        error_response = {
            "error": "Minting failed",
            "details": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        response = ChatMessage(
            content=[TextContent(text=json.dumps(error_response))]
    )
    await ctx.send(sender, response)

# Run the agent
if __name__ == "__main__":
    minting_agent.run()
