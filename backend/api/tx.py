from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/tx", tags=["transactions"])

# Mock database for demonstration
transactions_database = {}

@router.get("/{tx_hash}")
async def get_transaction(tx_hash: str):
    """
    Get transaction details by hash
    """
    if tx_hash not in transactions_database:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx = transactions_database[tx_hash]
    
    return {
        "tx_hash": tx_hash,
        "status": tx["status"],
        "block_number": tx.get("block_number"),
        "gas_used": tx.get("gas_used"),
        "gas_price": tx.get("gas_price"),
        "from_address": tx["from_address"],
        "to_address": tx["to_address"],
        "value": tx.get("value", 0),
        "data": tx.get("data", ""),
        "timestamp": tx["timestamp"],
        "proof_id": tx.get("proof_id"),
        "token_id": tx.get("token_id"),
        "contract_address": tx.get("contract_address")
    }

@router.post("/")
async def create_transaction(tx_data: Dict[str, Any]):
    """
    Create a new transaction record (typically called after blockchain transaction)
    """
    try:
        tx_hash = tx_data.get("tx_hash")
        if not tx_hash:
            raise HTTPException(status_code=400, detail="Transaction hash is required")
        
        if tx_hash in transactions_database:
            raise HTTPException(status_code=400, detail="Transaction already exists")
        
        # Create transaction record
        transaction = {
            "tx_hash": tx_hash,
            "status": tx_data.get("status", "pending"),
            "block_number": tx_data.get("block_number"),
            "gas_used": tx_data.get("gas_used"),
            "gas_price": tx_data.get("gas_price"),
            "from_address": tx_data.get("from_address"),
            "to_address": tx_data.get("to_address"),
            "value": tx_data.get("value", 0),
            "data": tx_data.get("data", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "proof_id": tx_data.get("proof_id"),
            "token_id": tx_data.get("token_id"),
            "contract_address": tx_data.get("contract_address"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        transactions_database[tx_hash] = transaction
        
        return {
            "tx_hash": tx_hash,
            "status": "recorded",
            "message": "Transaction recorded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction creation failed: {str(e)}")

@router.put("/{tx_hash}/status")
async def update_transaction_status(
    tx_hash: str, 
    status_data: Dict[str, Any]
):
    """
    Update transaction status (e.g., when transaction is confirmed on blockchain)
    """
    if tx_hash not in transactions_database:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx = transactions_database[tx_hash]
    
    new_status = status_data.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    valid_statuses = ["pending", "confirmed", "failed", "reverted"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Valid statuses: {valid_statuses}"
        )
    
    # Update transaction
    tx["status"] = new_status
    tx["updated_at"] = datetime.utcnow().isoformat()
    
    # Add additional fields if provided
    if "block_number" in status_data:
        tx["block_number"] = status_data["block_number"]
    if "gas_used" in status_data:
        tx["gas_used"] = status_data["gas_used"]
    if "gas_price" in status_data:
        tx["gas_price"] = status_data["gas_price"]
    
    return {
        "tx_hash": tx_hash,
        "status": new_status,
        "message": f"Transaction status updated to {new_status}"
    }

@router.get("/")
async def list_transactions(
    user_address: Optional[str] = None,
    status: Optional[str] = None,
    proof_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List transactions with optional filtering
    """
    transactions = list(transactions_database.values())
    
    # Apply filters
    if user_address:
        transactions = [
            tx for tx in transactions 
            if tx.get("from_address") == user_address or tx.get("to_address") == user_address
        ]
    
    if status:
        transactions = [tx for tx in transactions if tx.get("status") == status]
    
    if proof_id:
        transactions = [tx for tx in transactions if tx.get("proof_id") == proof_id]
    
    # Sort by timestamp (newest first)
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Apply pagination
    total_count = len(transactions)
    transactions = transactions[offset:offset + limit]
    
    return {
        "transactions": transactions,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/{tx_hash}/receipt")
async def get_transaction_receipt(tx_hash: str):
    """
    Get detailed transaction receipt
    """
    if tx_hash not in transactions_database:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    tx = transactions_database[tx_hash]
    
    # Generate mock receipt
    receipt = {
        "transaction_hash": tx_hash,
        "block_hash": f"0x{''.join([str(uuid.uuid4()).replace('-', '')[:8] for _ in range(8)])}",
        "block_number": tx.get("block_number", 12345678),
        "transaction_index": 0,
        "from": tx["from_address"],
        "to": tx["to_address"],
        "gas_used": tx.get("gas_used", 21000),
        "cumulative_gas_used": tx.get("gas_used", 21000),
        "gas_price": tx.get("gas_price", "20000000000"),
        "effective_gas_price": tx.get("gas_price", "20000000000"),
        "status": 1 if tx["status"] == "confirmed" else 0,
        "logs": [],
        "logs_bloom": "0x" + "0" * 512,
        "contract_address": tx.get("contract_address"),
        "proof_id": tx.get("proof_id"),
        "token_id": tx.get("token_id")
    }
    
    return receipt
