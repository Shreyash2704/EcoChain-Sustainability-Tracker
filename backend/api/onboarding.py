from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="/onboard", tags=["onboarding"])

# Mock database for demonstration
onboarding_sessions = {}

@router.post("/")
async def start_onboarding(user_data: Dict[str, Any] = Body(...)):
    """
    Start onboarding process for a new user
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Extract user information
        wallet_address = user_data.get("wallet_address")
        email = user_data.get("email")
        name = user_data.get("name")
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="Wallet address is required")
        
        # Store onboarding session
        onboarding_sessions[session_id] = {
            "session_id": session_id,
            "wallet_address": wallet_address,
            "email": email,
            "name": name,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "steps_completed": []
        }
        
        return {
            "session_id": session_id,
            "status": "onboarding_started",
            "next_step": "kyc_verification",
            "message": "Onboarding process initiated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding failed: {str(e)}")

@router.get("/{session_id}/status")
async def get_onboarding_status(session_id: str):
    """
    Get the current status of an onboarding session
    """
    if session_id not in onboarding_sessions:
        raise HTTPException(status_code=404, detail="Onboarding session not found")
    
    session = onboarding_sessions[session_id]
    return {
        "session_id": session_id,
        "status": session["status"],
        "steps_completed": session["steps_completed"],
        "created_at": session["created_at"]
    }

@router.post("/{session_id}/complete-step")
async def complete_onboarding_step(
    session_id: str, 
    step_data: Dict[str, Any] = Body(...)
):
    """
    Complete a step in the onboarding process
    """
    if session_id not in onboarding_sessions:
        raise HTTPException(status_code=404, detail="Onboarding session not found")
    
    session = onboarding_sessions[session_id]
    step_name = step_data.get("step_name")
    step_data_content = step_data.get("data", {})
    
    if not step_name:
        raise HTTPException(status_code=400, detail="Step name is required")
    
    # Add step to completed steps
    session["steps_completed"].append({
        "step_name": step_name,
        "data": step_data_content,
        "completed_at": datetime.utcnow().isoformat()
    })
    
    # Update status based on completed steps
    completed_steps = [step["step_name"] for step in session["steps_completed"]]
    
    if "kyc_verification" in completed_steps and "sustainability_profile" in completed_steps:
        session["status"] = "completed"
        next_step = None
    elif "kyc_verification" in completed_steps:
        next_step = "sustainability_profile"
    else:
        next_step = "kyc_verification"
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "next_step": next_step,
        "steps_completed": session["steps_completed"]
    }
