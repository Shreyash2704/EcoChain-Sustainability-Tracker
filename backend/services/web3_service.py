"""
Web3 Service - Blockchain contract interactions
Handles smart contract ABIs, read/write operations, and blockchain interactions
"""

from web3 import Web3
from typing import Dict, Any, Optional, List, Union
from fastapi import HTTPException
import json
import os
from datetime import datetime
from eth_account import Account
from eth_typing import Address

class Web3Service:
    def __init__(self, rpc_url: str, private_key: str = None):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        self.account = None
        
        if private_key:
            self.account = Account.from_key(private_key)
        
        # Contract ABIs and addresses
        self.contracts = {}
        self._load_contract_abis()
    
    def _load_contract_abis(self):
        """Load contract ABIs from files or environment"""
        # Carbon Credit NFT Contract ABI
        self.contracts['carbon_credit_nft'] = {
            'abi': [
                {
                    "inputs": [
                        {"internalType": "address", "name": "to", "type": "address"},
                        {"internalType": "string", "name": "tokenURI", "type": "string"},
                        {"internalType": "uint256", "name": "carbonAmount", "type": "uint256"},
                        {"internalType": "string", "name": "proofType", "type": "string"}
                    ],
                    "name": "mintCarbonCredit",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                    "name": "tokenURI",
                    "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                    "name": "getCarbonAmount",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                    "name": "getProofType",
                    "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"},
                        {"internalType": "uint256", "name": "index", "type": "uint256"}
                    ],
                    "name": "tokenOfOwnerByIndex",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ],
            'address': os.getenv('CARBON_CREDIT_NFT_ADDRESS', '0x0000000000000000000000000000000000000000')
        }
        
        # Sustainability Proof Registry ABI
        self.contracts['proof_registry'] = {
            'abi': [
                {
                    "inputs": [
                        {"internalType": "address", "name": "user", "type": "address"},
                        {"internalType": "string", "name": "proofId", "type": "string"},
                        {"internalType": "string", "name": "proofType", "type": "string"},
                        {"internalType": "uint256", "name": "carbonImpact", "type": "uint256"},
                        {"internalType": "string", "name": "metadataURI", "type": "string"}
                    ],
                    "name": "registerProof",
                    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "string", "name": "proofId", "type": "string"}],
                    "name": "getProof",
                    "outputs": [
                        {"internalType": "address", "name": "user", "type": "address"},
                        {"internalType": "string", "name": "proofType", "type": "string"},
                        {"internalType": "uint256", "name": "carbonImpact", "type": "uint256"},
                        {"internalType": "string", "name": "metadataURI", "type": "string"},
                        {"internalType": "bool", "name": "verified", "type": "bool"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "string", "name": "proofId", "type": "string"},
                        {"internalType": "bool", "name": "verified", "type": "bool"}
                    ],
                    "name": "verifyProof",
                    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ],
            'address': os.getenv('PROOF_REGISTRY_ADDRESS', '0x0000000000000000000000000000000000000000')
        }
    
    def get_contract(self, contract_name: str):
        """Get a contract instance"""
        if contract_name not in self.contracts:
            raise HTTPException(
                status_code=400,
                detail=f"Contract {contract_name} not found"
            )
        
        contract_info = self.contracts[contract_name]
        return self.w3.eth.contract(
            address=contract_info['address'],
            abi=contract_info['abi']
        )
    
    async def mint_carbon_credit_nft(
        self, 
        to_address: str, 
        token_uri: str, 
        carbon_amount: int, 
        proof_type: str
    ) -> Dict[str, Any]:
        """
        Mint a carbon credit NFT
        
        Args:
            to_address: Recipient address
            token_uri: IPFS URI for token metadata
            carbon_amount: Amount of carbon credits (in wei)
            proof_type: Type of sustainability proof
            
        Returns:
            Dict containing transaction details
        """
        try:
            if not self.account:
                raise HTTPException(
                    status_code=500,
                    detail="No account configured for minting"
                )
            
            contract = self.get_contract('carbon_credit_nft')
            
            # Build transaction
            transaction = contract.functions.mintCarbonCredit(
                to_address,
                token_uri,
                carbon_amount,
                proof_type
            ).build_transaction({
                'from': self.account.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Get token ID from event logs
            token_id = None
            for log in receipt.logs:
                try:
                    decoded = contract.events.Transfer().process_log(log)
                    if decoded['args']['to'].lower() == to_address.lower():
                        token_id = decoded['args']['tokenId']
                        break
                except:
                    continue
            
            return {
                "tx_hash": tx_hash.hex(),
                "token_id": token_id,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "success" if receipt.status == 1 else "failed",
                "to_address": to_address,
                "carbon_amount": carbon_amount,
                "proof_type": proof_type
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Minting failed: {str(e)}"
            )
    
    async def register_sustainability_proof(
        self,
        user_address: str,
        proof_id: str,
        proof_type: str,
        carbon_impact: int,
        metadata_uri: str
    ) -> Dict[str, Any]:
        """
        Register a sustainability proof on-chain
        
        Args:
            user_address: User's wallet address
            proof_id: Unique proof identifier
            proof_type: Type of sustainability proof
            carbon_impact: Carbon impact amount
            metadata_uri: IPFS URI for proof metadata
            
        Returns:
            Dict containing transaction details
        """
        try:
            if not self.account:
                raise HTTPException(
                    status_code=500,
                    detail="No account configured for registration"
                )
            
            contract = self.get_contract('proof_registry')
            
            # Build transaction
            transaction = contract.functions.registerProof(
                user_address,
                proof_id,
                proof_type,
                carbon_impact,
                metadata_uri
            ).build_transaction({
                'from': self.account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "success" if receipt.status == 1 else "failed",
                "proof_id": proof_id,
                "user_address": user_address
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Proof registration failed: {str(e)}"
            )
    
    async def verify_proof(self, proof_id: str, verified: bool) -> Dict[str, Any]:
        """
        Verify a sustainability proof on-chain
        
        Args:
            proof_id: Proof identifier
            verified: Verification status
            
        Returns:
            Dict containing transaction details
        """
        try:
            if not self.account:
                raise HTTPException(
                    status_code=500,
                    detail="No account configured for verification"
                )
            
            contract = self.get_contract('proof_registry')
            
            # Build transaction
            transaction = contract.functions.verifyProof(
                proof_id,
                verified
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "success" if receipt.status == 1 else "failed",
                "proof_id": proof_id,
                "verified": verified
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Proof verification failed: {str(e)}"
            )
    
    async def get_user_nfts(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Get all carbon credit NFTs owned by a user
        
        Args:
            user_address: User's wallet address
            
        Returns:
            List of NFT information
        """
        try:
            contract = self.get_contract('carbon_credit_nft')
            
            # Get balance
            balance = contract.functions.balanceOf(user_address).call()
            
            nfts = []
            for i in range(balance):
                token_id = contract.functions.tokenOfOwnerByIndex(user_address, i).call()
                token_uri = contract.functions.tokenURI(token_id).call()
                carbon_amount = contract.functions.getCarbonAmount(token_id).call()
                proof_type = contract.functions.getProofType(token_id).call()
                
                nfts.append({
                    "token_id": token_id,
                    "token_uri": token_uri,
                    "carbon_amount": carbon_amount,
                    "proof_type": proof_type,
                    "owner": user_address
                })
            
            return nfts
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get user NFTs: {str(e)}"
            )
    
    async def get_proof_details(self, proof_id: str) -> Dict[str, Any]:
        """
        Get details of a registered proof
        
        Args:
            proof_id: Proof identifier
            
        Returns:
            Dict containing proof details
        """
        try:
            contract = self.get_contract('proof_registry')
            
            proof_data = contract.functions.getProof(proof_id).call()
            
            return {
                "proof_id": proof_id,
                "user": proof_data[0],
                "proof_type": proof_data[1],
                "carbon_impact": proof_data[2],
                "metadata_uri": proof_data[3],
                "verified": proof_data[4]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get proof details: {str(e)}"
            )
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction status and details
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Dict containing transaction status
        """
        try:
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            
            return {
                "tx_hash": tx_hash,
                "status": "success" if receipt.status == 1 else "failed",
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "gas_price": tx.gasPrice,
                "from_address": tx['from'],
                "to_address": tx.to,
                "value": tx.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get transaction status: {str(e)}"
            )

# Global instance (to be initialized with RPC URL and private key)
web3_service: Optional[Web3Service] = None

def initialize_web3_service(rpc_url: str, private_key: str = None):
    """Initialize the global Web3 service instance"""
    global web3_service
    web3_service = Web3Service(rpc_url, private_key)

def get_web3_service() -> Web3Service:
    """Get the global Web3 service instance"""
    if web3_service is None:
        raise HTTPException(
            status_code=500,
            detail="Web3 service not initialized"
        )
    return web3_service
