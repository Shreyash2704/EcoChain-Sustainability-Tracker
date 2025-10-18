#!/usr/bin/env python3
"""
Analytics API endpoints for user activity tracking and leaderboards
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from services.web3_service import get_web3_service
from api.uploads import upload_sessions

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/user/{user_wallet}")
async def get_user_analytics(user_wallet: str):
    """
    Get comprehensive analytics for a specific user
    
    Returns:
    - Upload history with documents, credits, and proofs
    - Blockchain data (token balance, NFTs) - if Web3Service available
    - Summary statistics
    """
    try:
        # Get Web3Service instance (optional)
        web3_service = get_web3_service()
        blockchain_data_available = web3_service is not None
        
        # Get blockchain data (if available)
        token_balance = None
        user_nfts = []
        
        if blockchain_data_available:
            try:
                token_balance = await web3_service.get_user_token_balance(user_wallet)
                user_nfts = await web3_service.get_user_nfts(user_wallet)
            except Exception as e:
                print(f"⚠️ Failed to get blockchain data: {e}")
                blockchain_data_available = False
        
        # Get backend upload data
        user_uploads = [
            upload for upload in upload_sessions.values() 
            if upload.get("user_wallet", "").lower() == user_wallet.lower()
        ]
        
        # Calculate detailed statistics
        total_uploads = len(user_uploads)
        total_credits_earned = sum(upload.get("token_amount", 0) for upload in user_uploads)
        total_nfts = len(user_nfts) if blockchain_data_available else 0
        
        # Process upload history with detailed information
        upload_history = []
        for upload in user_uploads:
            upload_info = {
                "upload_id": upload.get("upload_id"),
                "filename": upload.get("filename"),
                "upload_timestamp": upload.get("timestamp"),
                "content_type": upload.get("content_type"),
                "ipfs_cid": upload.get("cid"),
                "ipfs_url": upload.get("gateway_url"),
                "credits_earned": upload.get("token_amount", 0),
                "impact_score": upload.get("impact_score", 0),
                "should_mint": upload.get("should_mint", False),
                "status": upload.get("status"),
                "metadata": upload.get("metadata", {})
            }
            
            # Add blockchain transaction details if available
            if "transaction_details" in upload:
                tx_details = upload["transaction_details"]
                upload_info["blockchain_transactions"] = {
                    "eco_token_tx": tx_details.get("eco_token_tx"),
                    "nft_tx": tx_details.get("nft_tx"),
                    "nft_token_id": tx_details.get("nft_token_id"),
                    "eco_token_explorer": f"https://sepolia.etherscan.io/tx/{tx_details.get('eco_token_tx')}" if tx_details.get("eco_token_tx") else None,
                    "nft_explorer": f"https://sepolia.etherscan.io/tx/{tx_details.get('nft_tx')}" if tx_details.get("nft_tx") else None
                }
            
            # Add analysis results if available
            if "analysis_result" in upload:
                analysis = upload["analysis_result"]
                upload_info["analysis"] = {
                    "carbon_footprint": analysis.get("carbon_footprint", 0),
                    "reasoning": analysis.get("reasoning", ""),
                    "document_type": analysis.get("document_type", ""),
                    "sustainability_metrics": analysis.get("sustainability_metrics", {})
                }
            
            upload_history.append(upload_info)
        
        # Sort uploads by timestamp (newest first)
        upload_history.sort(key=lambda x: x.get("upload_timestamp", ""), reverse=True)
        
        # Calculate additional statistics
        successful_uploads = len([u for u in user_uploads if u.get("status") == "completed"])
        total_carbon_impact = sum(
            upload.get("analysis_result", {}).get("carbon_footprint", 0) 
            for upload in user_uploads 
            if "analysis_result" in upload
        )
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_uploads = [
            upload for upload in user_uploads 
            if upload.get("timestamp") and 
            datetime.fromisoformat(upload["timestamp"].replace('Z', '+00:00')) > thirty_days_ago
        ]
        
        # Prepare response
        response = {
            "user_wallet": user_wallet,
            "summary": {
                "total_documents_uploaded": total_uploads,
                "successful_uploads": successful_uploads,
                "total_credits_earned": total_credits_earned,
                "total_carbon_impact": total_carbon_impact,
                "recent_activity_30_days": len(recent_uploads),
                "success_rate": (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0
            },
            "upload_history": upload_history,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Add blockchain data if available
        if blockchain_data_available and token_balance:
            response["summary"]["total_eco_tokens"] = token_balance.get("balance_formatted", "0")
            response["summary"]["total_nfts_owned"] = total_nfts
            response["blockchain_data"] = {
                "eco_token_balance": token_balance,
                "nft_collection": {
                    "count": total_nfts,
                    "nfts": user_nfts
                }
            }
        else:
            response["summary"]["total_eco_tokens"] = "N/A (Web3Service not available)"
            response["summary"]["total_nfts_owned"] = "N/A (Web3Service not available)"
            response["blockchain_data"] = {
                "status": "unavailable",
                "message": "Web3Service not initialized or blockchain data unavailable"
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user analytics: {str(e)}")

@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100, description="Number of top users to return"),
    sort_by: str = Query("credits", description="Sort by: credits, uploads, nfts, carbon_impact")
):
    """
    Get leaderboard of top users
    
    Sort options:
    - credits: Total ECO tokens earned
    - uploads: Number of documents uploaded
    - nfts: Number of NFTs owned
    - carbon_impact: Total carbon impact
    """
    try:
        # Get Web3Service instance (optional)
        web3_service = get_web3_service()
        blockchain_data_available = web3_service is not None
        
        # Group uploads by user
        user_stats = {}
        
        for upload in upload_sessions.values():
            user_wallet = upload.get("user_wallet")
            if not user_wallet:
                continue
                
            if user_wallet not in user_stats:
                user_stats[user_wallet] = {
                    "user_wallet": user_wallet,
                    "total_uploads": 0,
                    "successful_uploads": 0,
                    "total_credits": 0,
                    "total_carbon_impact": 0,
                    "total_nfts": 0,
                    "first_upload": None,
                    "last_upload": None,
                    "uploads": []
                }
            
            user_stats[user_wallet]["total_uploads"] += 1
            user_stats[user_wallet]["total_credits"] += upload.get("token_amount", 0)
            user_stats[user_wallet]["successful_uploads"] += 1 if upload.get("status") == "completed" else 0
            
            # Add carbon impact
            if "analysis_result" in upload:
                carbon_impact = upload["analysis_result"].get("carbon_footprint", 0)
                user_stats[user_wallet]["total_carbon_impact"] += carbon_impact
            
            # Track upload timestamps
            upload_time = upload.get("timestamp")
            if upload_time:
                if not user_stats[user_wallet]["first_upload"] or upload_time < user_stats[user_wallet]["first_upload"]:
                    user_stats[user_wallet]["first_upload"] = upload_time
                if not user_stats[user_wallet]["last_upload"] or upload_time > user_stats[user_wallet]["last_upload"]:
                    user_stats[user_wallet]["last_upload"] = upload_time
            
            user_stats[user_wallet]["uploads"].append(upload)
        
        # Get NFT counts for each user (if Web3Service available)
        if blockchain_data_available:
            for user_wallet in user_stats.keys():
                try:
                    user_nfts = await web3_service.get_user_nfts(user_wallet)
                    user_stats[user_wallet]["total_nfts"] = len(user_nfts)
                except Exception as e:
                    print(f"⚠️ Failed to get NFTs for {user_wallet}: {e}")
                    user_stats[user_wallet]["total_nfts"] = 0
        else:
            # Set NFT count to 0 if Web3Service not available
            for user_wallet in user_stats.keys():
                user_stats[user_wallet]["total_nfts"] = 0
        
        # Sort by specified criteria
        sort_key_map = {
            "credits": "total_credits",
            "uploads": "total_uploads", 
            "nfts": "total_nfts",
            "carbon_impact": "total_carbon_impact"
        }
        
        sort_key = sort_key_map.get(sort_by, "total_credits")
        
        leaderboard = sorted(
            user_stats.values(), 
            key=lambda x: x[sort_key], 
            reverse=True
        )[:limit]
        
        # Add ranking
        for i, user in enumerate(leaderboard):
            user["rank"] = i + 1
            user["success_rate"] = (user["successful_uploads"] / user["total_uploads"] * 100) if user["total_uploads"] > 0 else 0
        
        return {
            "leaderboard": leaderboard,
            "total_users": len(user_stats),
            "total_uploads": len(upload_sessions),
            "sort_by": sort_by,
            "limit": limit,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")

@router.get("/stats/overview")
async def get_system_overview():
    """
    Get overall system statistics and overview
    """
    try:
        # Get Web3Service instance (optional)
        web3_service = get_web3_service()
        blockchain_data_available = web3_service is not None
        
        # Calculate system-wide statistics
        total_uploads = len(upload_sessions)
        successful_uploads = len([u for u in upload_sessions.values() if u.get("status") == "completed"])
        total_credits_distributed = sum(upload.get("token_amount", 0) for upload in upload_sessions.values())
        total_carbon_impact = sum(
            upload.get("analysis_result", {}).get("carbon_footprint", 0) 
            for upload in upload_sessions.values() 
            if "analysis_result" in upload
        )
        
        # Get unique users
        unique_users = set(upload.get("user_wallet") for upload in upload_sessions.values() if upload.get("user_wallet"))
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = [
            upload for upload in upload_sessions.values() 
            if upload.get("timestamp") and 
            datetime.fromisoformat(upload["timestamp"].replace('Z', '+00:00')) > seven_days_ago
        ]
        
        # Get contract statistics (if Web3Service available)
        total_eco_supply = 0
        total_nft_supply = 0
        
        if blockchain_data_available:
            try:
                eco_contract = web3_service.get_contract('eco_credit_token')
                nft_contract = web3_service.get_contract('sustainability_proof')
                
                total_eco_supply = eco_contract.functions.totalSupply().call()
                total_nft_supply = nft_contract.functions.totalSupply().call()
            except Exception as e:
                print(f"⚠️ Failed to get contract stats: {e}")
                total_eco_supply = 0
                total_nft_supply = 0
        
        return {
            "system_overview": {
                "total_users": len(unique_users),
                "total_uploads": total_uploads,
                "successful_uploads": successful_uploads,
                "success_rate": (successful_uploads / total_uploads * 100) if total_uploads > 0 else 0,
                "total_credits_distributed": total_credits_distributed,
                "total_carbon_impact": total_carbon_impact,
                "recent_activity_7_days": len(recent_uploads)
            },
            "blockchain_stats": {
                "total_eco_tokens_minted": total_eco_supply if blockchain_data_available else "N/A (Web3Service not available)",
                "total_nfts_minted": total_nft_supply if blockchain_data_available else "N/A (Web3Service not available)",
                "eco_contract": "0x17874E9d6e22bf8025Fe7473684e50f36472CCd2",
                "nft_contract": "0x17874E9d6e22bf8025Fe7473684e50f36472CCd2",
                "status": "available" if blockchain_data_available else "unavailable"
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system overview: {str(e)}")

@router.get("/user/{user_wallet}/recent")
async def get_user_recent_activity(
    user_wallet: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to look back")
):
    """
    Get recent activity for a specific user
    """
    try:
        # Get user uploads
        user_uploads = [
            upload for upload in upload_sessions.values() 
            if upload.get("user_wallet", "").lower() == user_wallet.lower()
        ]
        
        # Filter by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_uploads = [
            upload for upload in user_uploads 
            if upload.get("timestamp") and 
            datetime.fromisoformat(upload["timestamp"].replace('Z', '+00:00')) > cutoff_date
        ]
        
        # Sort by timestamp (newest first)
        recent_uploads.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Calculate recent statistics
        recent_credits = sum(upload.get("token_amount", 0) for upload in recent_uploads)
        recent_carbon_impact = sum(
            upload.get("analysis_result", {}).get("carbon_footprint", 0) 
            for upload in recent_uploads 
            if "analysis_result" in upload
        )
        
        return {
            "user_wallet": user_wallet,
            "period_days": days,
            "recent_uploads": len(recent_uploads),
            "recent_credits_earned": recent_credits,
            "recent_carbon_impact": recent_carbon_impact,
            "uploads": recent_uploads,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent activity: {str(e)}")
