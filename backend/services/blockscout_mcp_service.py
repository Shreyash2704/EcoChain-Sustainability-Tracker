"""
Blockscout MCP (Model Context Protocol) Service
Provides AI agents with blockchain data querying capabilities
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BlockscoutMCPService:
    """Service for AI agents to query blockchain data via Blockscout API"""
    
    def __init__(self):
        self.base_url = "https://sepolia.blockscout.com"  # Default Sepolia explorer
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def query_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Query transaction details for AI consumption"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v2/transactions/{tx_hash}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "transaction": {
                        "hash": data.get("hash"),
                        "from": data.get("from", {}).get("hash"),
                        "to": data.get("to", {}).get("hash"),
                        "value": data.get("value"),
                        "gas_used": data.get("gas_used"),
                        "gas_price": data.get("gas_price"),
                        "block_number": data.get("block_number"),
                        "timestamp": data.get("timestamp"),
                        "status": data.get("status"),
                        "confirmations": data.get("confirmations", 0)
                    },
                    "explorer_url": f"{self.base_url}/tx/{tx_hash}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Transaction not found: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying transaction {tx_hash}: {e}")
            return {
                "status": "error",
                "message": f"Failed to query transaction: {str(e)}"
            }
    
    async def query_token_balance(self, address: str, token_address: str) -> Dict[str, Any]:
        """Query token balance for AI consumption"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v2/tokens/{token_address}/holders",
                params={"holder_address_hash": address}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    holder_data = data["items"][0]
                    return {
                        "status": "success",
                        "balance": {
                            "address": address,
                            "token_address": token_address,
                            "symbol": holder_data.get("token", {}).get("symbol"),
                            "name": holder_data.get("token", {}).get("name"),
                            "decimals": holder_data.get("token", {}).get("decimals"),
                            "balance": holder_data.get("value"),
                            "balance_formatted": self._format_token_amount(
                                holder_data.get("value", "0"),
                                holder_data.get("token", {}).get("decimals", 18)
                            )
                        },
                        "explorer_url": f"{self.base_url}/token/{token_address}"
                    }
                else:
                    return {
                        "status": "success",
                        "balance": {
                            "address": address,
                            "token_address": token_address,
                            "balance": "0",
                            "balance_formatted": "0.000000"
                        }
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Token balance not found: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying token balance: {e}")
            return {
                "status": "error",
                "message": f"Failed to query token balance: {str(e)}"
            }
    
    async def query_nft_collection(self, address: str, contract_address: str) -> Dict[str, Any]:
        """Query NFT collection for AI consumption"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v2/tokens/{contract_address}/instances",
                params={"holder_address_hash": address}
            )
            
            if response.status_code == 200:
                data = response.json()
                nfts = []
                
                for item in data.get("items", []):
                    nft = {
                        "token_id": item.get("token_id"),
                        "name": item.get("token", {}).get("name", f"NFT #{item.get('token_id')}"),
                        "description": item.get("token", {}).get("description", ""),
                        "image": item.get("token", {}).get("image_url", ""),
                        "attributes": item.get("token", {}).get("attributes", []),
                        "transaction_hash": item.get("transaction_hash"),
                        "block_number": item.get("block_number")
                    }
                    nfts.append(nft)
                
                return {
                    "status": "success",
                    "collection": {
                        "owner": address,
                        "contract_address": contract_address,
                        "total_nfts": len(nfts),
                        "nfts": nfts
                    },
                    "explorer_url": f"{self.base_url}/token/{contract_address}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"NFT collection not found: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying NFT collection: {e}")
            return {
                "status": "error",
                "message": f"Failed to query NFT collection: {str(e)}"
            }
    
    async def query_recent_transactions(self, address: str, limit: int = 10) -> Dict[str, Any]:
        """Query recent transactions for AI consumption"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v2/addresses/{address}/transactions",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                data = response.json()
                transactions = []
                
                for tx in data.get("items", []):
                    transaction = {
                        "hash": tx.get("hash"),
                        "from": tx.get("from", {}).get("hash"),
                        "to": tx.get("to", {}).get("hash"),
                        "value": tx.get("value"),
                        "gas_used": tx.get("gas_used"),
                        "block_number": tx.get("block_number"),
                        "timestamp": tx.get("timestamp"),
                        "status": tx.get("status")
                    }
                    transactions.append(transaction)
                
                return {
                    "status": "success",
                    "transactions": {
                        "address": address,
                        "total": len(transactions),
                        "recent": transactions
                    },
                    "explorer_url": f"{self.base_url}/address/{address}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Recent transactions not found: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying recent transactions: {e}")
            return {
                "status": "error",
                "message": f"Failed to query recent transactions: {str(e)}"
            }
    
    async def query_contract_info(self, contract_address: str) -> Dict[str, Any]:
        """Query contract information for AI consumption"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v2/tokens/{contract_address}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "contract": {
                        "address": contract_address,
                        "name": data.get("name"),
                        "symbol": data.get("symbol"),
                        "decimals": data.get("decimals"),
                        "total_supply": data.get("total_supply"),
                        "type": data.get("type"),
                        "verified": data.get("verified", False)
                    },
                    "explorer_url": f"{self.base_url}/token/{contract_address}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Contract not found: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error querying contract info: {e}")
            return {
                "status": "error",
                "message": f"Failed to query contract info: {str(e)}"
            }
    
    def _format_token_amount(self, amount: str, decimals: int) -> str:
        """Format token amount for display"""
        try:
            value = float(amount) / (10 ** decimals)
            return f"{value:.6f}"
        except:
            return "0.000000"
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global MCP service instance
mcp_service = BlockscoutMCPService()


async def get_mcp_service() -> BlockscoutMCPService:
    """Get the global MCP service instance"""
    return mcp_service


async def query_blockchain_data(query_type: str, **kwargs) -> Dict[str, Any]:
    """Main function for AI agents to query blockchain data"""
    service = await get_mcp_service()
    
    try:
        if query_type == "transaction":
            return await service.query_transaction(kwargs.get("tx_hash", ""))
        elif query_type == "token_balance":
            return await service.query_token_balance(
                kwargs.get("address", ""),
                kwargs.get("token_address", "")
            )
        elif query_type == "nft_collection":
            return await service.query_nft_collection(
                kwargs.get("address", ""),
                kwargs.get("contract_address", "")
            )
        elif query_type == "recent_transactions":
            return await service.query_recent_transactions(
                kwargs.get("address", ""),
                kwargs.get("limit", 10)
            )
        elif query_type == "contract_info":
            return await service.query_contract_info(kwargs.get("contract_address", ""))
        else:
            return {
                "status": "error",
                "message": f"Unknown query type: {query_type}"
            }
    except Exception as e:
        logger.error(f"Error in blockchain data query: {e}")
        return {
            "status": "error",
            "message": f"Query failed: {str(e)}"
        }
