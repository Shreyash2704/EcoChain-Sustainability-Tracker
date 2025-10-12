from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/proofs", tags=["proofs"])

# Mock database for demonstration
proofs_database = {}

@router.post("/")
async def create_proof(proof_data: Dict[str, Any] = Body(...)):
    """
    Create a new sustainability proof
    """
    try:
        proof_id = str(uuid.uuid4())
        
        # Extract required fields
        user_wallet = proof_data.get("user_wallet")
        proof_type = proof_data.get("proof_type")
        evidence_data = proof_data.get("evidence_data", {})
        carbon_impact = proof_data.get("carbon_impact", 0)
        
        if not user_wallet or not proof_type:
            raise HTTPException(
                status_code=400, 
                detail="user_wallet and proof_type are required"
            )
        
        # Validate proof type
        allowed_proof_types = [
            "carbon_offset", "renewable_energy", "waste_reduction", 
            "sustainable_transport", "green_building", "tree_planting"
        ]
        if proof_type not in allowed_proof_types:
            raise HTTPException(
                status_code=400,
                detail=f"Proof type {proof_type} not supported"
            )
        
        # Create proof record
        proof = {
            "proof_id": proof_id,
            "user_wallet": user_wallet,
            "proof_type": proof_type,
            "evidence_data": evidence_data,
            "carbon_impact": carbon_impact,
            "status": "pending_verification",
            "created_at": datetime.utcnow().isoformat(),
            "verified_at": None,
            "verification_score": None,
            "blockchain_tx_hash": None
        }
        
        proofs_database[proof_id] = proof
        
        return {
            "proof_id": proof_id,
            "status": "created",
            "message": "Proof created successfully and queued for verification"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof creation failed: {str(e)}")

@router.get("/{proof_id}")
async def get_proof(proof_id: str):
    """
    Get details of a specific proof
    """
    if proof_id not in proofs_database:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    return proofs_database[proof_id]

@router.get("/")
async def list_proofs(
    user_wallet: Optional[str] = None,
    proof_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List proofs with optional filtering
    """
    proofs = list(proofs_database.values())
    
    # Apply filters
    if user_wallet:
        proofs = [p for p in proofs if p["user_wallet"] == user_wallet]
    
    if proof_type:
        proofs = [p for p in proofs if p["proof_type"] == proof_type]
    
    if status:
        proofs = [p for p in proofs if p["status"] == status]
    
    # Apply pagination
    total_count = len(proofs)
    proofs = proofs[offset:offset + limit]
    
    return {
        "proofs": proofs,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

@router.post("/{proof_id}/verify")
async def verify_proof(proof_id: str, verification_data: Dict[str, Any] = Body(...)):
    """
    Verify a proof (typically called by verifier agent)
    """
    if proof_id not in proofs_database:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    proof = proofs_database[proof_id]
    
    if proof["status"] != "pending_verification":
        raise HTTPException(
            status_code=400, 
            detail=f"Proof is not in pending_verification status. Current status: {proof['status']}"
        )
    
    # Extract verification data
    verification_score = verification_data.get("verification_score", 0)
    verification_notes = verification_data.get("verification_notes", "")
    is_verified = verification_data.get("is_verified", False)
    
    # Update proof status
    proof["status"] = "verified" if is_verified else "rejected"
    proof["verified_at"] = datetime.utcnow().isoformat()
    proof["verification_score"] = verification_score
    proof["verification_notes"] = verification_notes
    
    return {
        "proof_id": proof_id,
        "status": proof["status"],
        "verification_score": verification_score,
        "message": f"Proof {proof['status']} successfully"
    }

@router.post("/{proof_id}/mint")
async def mint_proof_token(proof_id: str, minting_data: Dict[str, Any] = Body(...)):
    """
    Mint a token for a verified proof
    """
    if proof_id not in proofs_database:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    proof = proofs_database[proof_id]
    
    if proof["status"] != "verified":
        raise HTTPException(
            status_code=400,
            detail="Only verified proofs can be minted"
        )
    
    if proof["blockchain_tx_hash"]:
        raise HTTPException(
            status_code=400,
            detail="Proof has already been minted"
        )
    
    # Mock blockchain transaction
    tx_hash = f"0x{''.join([str(uuid.uuid4()).replace('-', '')[:8] for _ in range(8)])}"
    
    proof["blockchain_tx_hash"] = tx_hash
    proof["minted_at"] = datetime.utcnow().isoformat()
    proof["token_metadata"] = minting_data.get("token_metadata", {})
    
    return {
        "proof_id": proof_id,
        "tx_hash": tx_hash,
        "status": "minted",
        "message": "Proof token minted successfully"
    }
