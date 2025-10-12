from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/user", tags=["users"])

# Mock database for demonstration
users_database = {}

@router.get("/{wallet_address}")
async def get_user_profile(wallet_address: str):
    """
    Get user profile by wallet address
    """
    if wallet_address not in users_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_database[wallet_address]
    
    # Calculate additional metrics
    total_carbon_saved = sum(
        proof.get("carbon_impact", 0) 
        for proof in user.get("proofs", [])
        if proof.get("status") == "verified"
    )
    
    total_tokens = len([
        proof for proof in user.get("proofs", [])
        if proof.get("blockchain_tx_hash")
    ])
    
    return {
        **user,
        "metrics": {
            "total_carbon_saved": total_carbon_saved,
            "total_tokens_minted": total_tokens,
            "verification_rate": len([
                p for p in user.get("proofs", []) 
                if p.get("status") == "verified"
            ]) / max(len(user.get("proofs", [])), 1)
        }
    }

@router.post("/{wallet_address}")
async def create_or_update_user(
    wallet_address: str, 
    user_data: Dict[str, Any] = Body(...)
):
    """
    Create or update user profile
    """
    try:
        # Extract user data
        name = user_data.get("name")
        email = user_data.get("email")
        bio = user_data.get("bio", "")
        sustainability_goals = user_data.get("sustainability_goals", [])
        preferences = user_data.get("preferences", {})
        
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Create or update user
        if wallet_address in users_database:
            # Update existing user
            user = users_database[wallet_address]
            user.update({
                "name": name,
                "email": email,
                "bio": bio,
                "sustainability_goals": sustainability_goals,
                "preferences": preferences,
                "updated_at": datetime.utcnow().isoformat()
            })
        else:
            # Create new user
            user = {
                "wallet_address": wallet_address,
                "name": name,
                "email": email,
                "bio": bio,
                "sustainability_goals": sustainability_goals,
                "preferences": preferences,
                "proofs": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_verified": False,
                "kyc_status": "pending"
            }
            users_database[wallet_address] = user
        
        return {
            "wallet_address": wallet_address,
            "status": "created" if wallet_address not in users_database else "updated",
            "message": "User profile saved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User operation failed: {str(e)}")

@router.get("/{wallet_address}/proofs")
async def get_user_proofs(
    wallet_address: str,
    status: Optional[str] = None,
    proof_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get all proofs for a specific user
    """
    if wallet_address not in users_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_database[wallet_address]
    proofs = user.get("proofs", [])
    
    # Apply filters
    if status:
        proofs = [p for p in proofs if p.get("status") == status]
    
    if proof_type:
        proofs = [p for p in proofs if p.get("proof_type") == proof_type]
    
    # Apply pagination
    total_count = len(proofs)
    proofs = proofs[offset:offset + limit]
    
    return {
        "wallet_address": wallet_address,
        "proofs": proofs,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/{wallet_address}/achievements")
async def get_user_achievements(wallet_address: str):
    """
    Get user achievements and milestones
    """
    if wallet_address not in users_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_database[wallet_address]
    proofs = user.get("proofs", [])
    
    # Calculate achievements
    verified_proofs = [p for p in proofs if p.get("status") == "verified"]
    total_carbon_saved = sum(p.get("carbon_impact", 0) for p in verified_proofs)
    
    achievements = []
    
    # Define achievement thresholds
    if total_carbon_saved >= 1000:
        achievements.append({
            "name": "Carbon Hero",
            "description": "Saved over 1000kg of CO2",
            "unlocked_at": datetime.utcnow().isoformat(),
            "badge": "carbon_hero"
        })
    
    if len(verified_proofs) >= 10:
        achievements.append({
            "name": "Proof Master",
            "description": "Verified 10+ sustainability proofs",
            "unlocked_at": datetime.utcnow().isoformat(),
            "badge": "proof_master"
        })
    
    if len([p for p in verified_proofs if p.get("proof_type") == "renewable_energy"]) >= 5:
        achievements.append({
            "name": "Green Energy Champion",
            "description": "5+ renewable energy proofs",
            "unlocked_at": datetime.utcnow().isoformat(),
            "badge": "green_energy_champion"
        })
    
    return {
        "wallet_address": wallet_address,
        "achievements": achievements,
        "total_achievements": len(achievements),
        "stats": {
            "total_carbon_saved": total_carbon_saved,
            "verified_proofs": len(verified_proofs),
            "total_proofs": len(proofs)
        }
    }

@router.post("/{wallet_address}/verify")
async def verify_user_kyc(
    wallet_address: str, 
    kyc_data: Dict[str, Any] = Body(...)
):
    """
    Verify user KYC status
    """
    if wallet_address not in users_database:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_database[wallet_address]
    
    # Mock KYC verification
    is_verified = kyc_data.get("is_verified", False)
    verification_notes = kyc_data.get("verification_notes", "")
    
    user["kyc_status"] = "verified" if is_verified else "rejected"
    user["kyc_verified_at"] = datetime.utcnow().isoformat()
    user["kyc_notes"] = verification_notes
    
    if is_verified:
        user["is_verified"] = True
    
    return {
        "wallet_address": wallet_address,
        "kyc_status": user["kyc_status"],
        "is_verified": user["is_verified"],
        "message": f"KYC verification {'completed' if is_verified else 'rejected'}"
    }
