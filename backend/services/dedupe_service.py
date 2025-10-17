"""
Dedupe Service - Duplicate detection and prevention
Handles detection and prevention of duplicate sustainability proofs and data
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Set, Tuple
from fastapi import HTTPException
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class DedupeResult:
    is_duplicate: bool
    confidence: float
    similar_items: List[Dict[str, Any]]
    hash_value: str
    similarity_score: float

class DedupeService:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.proof_hashes: Dict[str, Dict[str, Any]] = {}
        self.user_activity: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.temporal_window = timedelta(hours=24)  # 24-hour window for temporal deduplication
    
    async def check_proof_duplicate(
        self, 
        proof_data: Dict[str, Any], 
        user_wallet: str
    ) -> DedupeResult:
        """
        Check if a sustainability proof is a duplicate
        
        Args:
            proof_data: Proof data to check
            user_wallet: User's wallet address
            
        Returns:
            DedupeResult with duplicate information
        """
        try:
            # Generate content hash
            content_hash = self._generate_content_hash(proof_data)
            
            # Check exact duplicate
            if content_hash in self.proof_hashes:
                existing_proof = self.proof_hashes[content_hash]
                return DedupeResult(
                    is_duplicate=True,
                    confidence=1.0,
                    similar_items=[existing_proof],
                    hash_value=content_hash,
                    similarity_score=1.0
                )
            
            # Check for similar proofs
            similar_proofs = await self._find_similar_proofs(proof_data, user_wallet)
            
            if similar_proofs:
                max_similarity = max(item['similarity'] for item in similar_proofs)
                
                if max_similarity >= self.similarity_threshold:
                    return DedupeResult(
                        is_duplicate=True,
                        confidence=max_similarity,
                        similar_items=similar_proofs,
                        hash_value=content_hash,
                        similarity_score=max_similarity
                    )
            
            # Check temporal duplicates
            temporal_duplicate = await self._check_temporal_duplicate(
                proof_data, user_wallet
            )
            
            if temporal_duplicate:
                return DedupeResult(
                    is_duplicate=True,
                    confidence=0.9,
                    similar_items=[temporal_duplicate],
                    hash_value=content_hash,
                    similarity_score=0.9
                )
            
            # Not a duplicate
            return DedupeResult(
                is_duplicate=False,
                confidence=0.0,
                similar_items=[],
                hash_value=content_hash,
                similarity_score=0.0
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Duplicate check failed: {str(e)}"
            )
    
    def _generate_content_hash(self, proof_data: Dict[str, Any]) -> str:
        """
        Generate a hash for proof content
        """
        # Normalize data for hashing
        normalized_data = self._normalize_proof_data(proof_data)
        
        # Create hash
        content_str = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def _normalize_proof_data(self, proof_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize proof data for consistent hashing
        """
        normalized = {}
        
        # Extract key fields
        key_fields = [
            'proof_type', 'carbon_impact', 'location', 'date', 
            'activity_type', 'energy_consumption', 'waste_amount'
        ]
        
        for field in key_fields:
            if field in proof_data:
                value = proof_data[field]
                
                # Normalize values
                if isinstance(value, str):
                    normalized[field] = value.lower().strip()
                elif isinstance(value, (int, float)):
                    # Round to 2 decimal places for consistency
                    normalized[field] = round(float(value), 2)
                else:
                    normalized[field] = value
        
        return normalized
    
    async def _find_similar_proofs(
        self, 
        proof_data: Dict[str, Any], 
        user_wallet: str
    ) -> List[Dict[str, Any]]:
        """
        Find similar proofs using fuzzy matching
        """
        similar_proofs = []
        
        for hash_value, existing_proof in self.proof_hashes.items():
            # Skip proofs from different users for now
            if existing_proof.get('user_wallet') != user_wallet:
                continue
            
            similarity = self._calculate_similarity(proof_data, existing_proof['data'])
            
            if similarity >= self.similarity_threshold:
                similar_proofs.append({
                    'hash': hash_value,
                    'similarity': similarity,
                    'proof_id': existing_proof.get('proof_id'),
                    'created_at': existing_proof.get('created_at'),
                    'data': existing_proof['data']
                })
        
        return similar_proofs
    
    def _calculate_similarity(
        self, 
        data1: Dict[str, Any], 
        data2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two proof datasets
        """
        # Normalize both datasets
        norm1 = self._normalize_proof_data(data1)
        norm2 = self._normalize_proof_data(data2)
        
        # Get common keys
        keys1 = set(norm1.keys())
        keys2 = set(norm2.keys())
        common_keys = keys1.intersection(keys2)
        
        if not common_keys:
            return 0.0
        
        # Calculate weighted similarity
        total_weight = 0
        weighted_similarity = 0
        
        # Define field weights
        field_weights = {
            'proof_type': 0.3,
            'carbon_impact': 0.25,
            'location': 0.2,
            'activity_type': 0.15,
            'date': 0.1
        }
        
        for key in common_keys:
            weight = field_weights.get(key, 0.05)
            similarity = self._field_similarity(norm1[key], norm2[key])
            
            weighted_similarity += similarity * weight
            total_weight += weight
        
        return weighted_similarity / total_weight if total_weight > 0 else 0.0
    
    def _field_similarity(self, value1: Any, value2: Any) -> float:
        """
        Calculate similarity between two field values
        """
        if value1 == value2:
            return 1.0
        
        if isinstance(value1, str) and isinstance(value2, str):
            # String similarity using simple character overlap
            set1 = set(value1.lower())
            set2 = set(value2.lower())
            
            if not set1 and not set2:
                return 1.0
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            return intersection / union if union > 0 else 0.0
        
        elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            # Numeric similarity
            if value1 == 0 and value2 == 0:
                return 1.0
            
            max_val = max(abs(value1), abs(value2))
            if max_val == 0:
                return 1.0
            
            diff = abs(value1 - value2)
            return max(0, 1 - (diff / max_val))
        
        return 0.0
    
    async def _check_temporal_duplicate(
        self, 
        proof_data: Dict[str, Any], 
        user_wallet: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check for temporal duplicates (same user, similar data, recent time)
        """
        current_time = datetime.utcnow()
        window_start = current_time - self.temporal_window
        
        # Get recent proofs from user
        recent_proofs = [
            proof for proof in self.user_activity[user_wallet]
            if datetime.fromisoformat(proof['created_at']) >= window_start
        ]
        
        for recent_proof in recent_proofs:
            similarity = self._calculate_similarity(proof_data, recent_proof['data'])
            
            if similarity >= 0.9:  # High similarity threshold for temporal
                return recent_proof
        
        return None
    
    async def register_proof(
        self, 
        proof_id: str, 
        proof_data: Dict[str, Any], 
        user_wallet: str
    ) -> None:
        """
        Register a new proof in the deduplication system
        
        Args:
            proof_id: Unique proof identifier
            proof_data: Proof data
            user_wallet: User's wallet address
        """
        try:
            content_hash = self._generate_content_hash(proof_data)
            
            # Store in hash registry
            self.proof_hashes[content_hash] = {
                'proof_id': proof_id,
                'user_wallet': user_wallet,
                'data': proof_data,
                'created_at': datetime.utcnow().isoformat(),
                'hash': content_hash
            }
            
            # Store in user activity
            self.user_activity[user_wallet].append({
                'proof_id': proof_id,
                'data': proof_data,
                'created_at': datetime.utcnow().isoformat()
            })
            
            # Clean up old activity (keep last 100 entries per user)
            if len(self.user_activity[user_wallet]) > 100:
                self.user_activity[user_wallet] = self.user_activity[user_wallet][-100:]
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Proof registration failed: {str(e)}"
            )
    
    async def get_duplicate_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about duplicate detection
        """
        try:
            total_proofs = len(self.proof_hashes)
            unique_users = len(self.user_activity)
            
            # Calculate average proofs per user
            avg_proofs_per_user = (
                sum(len(proofs) for proofs in self.user_activity.values()) / unique_users
                if unique_users > 0 else 0
            )
            
            return {
                "total_proofs": total_proofs,
                "unique_users": unique_users,
                "average_proofs_per_user": round(avg_proofs_per_user, 2),
                "similarity_threshold": self.similarity_threshold,
                "temporal_window_hours": self.temporal_window.total_seconds() / 3600,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get statistics: {str(e)}"
            )
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Clean up old data to prevent memory bloat
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Dict with cleanup statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            initial_count = len(self.proof_hashes)
            
            # Clean up proof hashes
            hashes_to_remove = []
            for hash_value, proof_info in self.proof_hashes.items():
                created_at = datetime.fromisoformat(proof_info['created_at'])
                if created_at < cutoff_date:
                    hashes_to_remove.append(hash_value)
            
            for hash_value in hashes_to_remove:
                del self.proof_hashes[hash_value]
            
            # Clean up user activity
            for user_wallet in self.user_activity:
                self.user_activity[user_wallet] = [
                    proof for proof in self.user_activity[user_wallet]
                    if datetime.fromisoformat(proof['created_at']) >= cutoff_date
                ]
            
            final_count = len(self.proof_hashes)
            cleaned_count = initial_count - final_count
            
            return {
                "initial_count": initial_count,
                "final_count": final_count,
                "cleaned_count": cleaned_count,
                "cutoff_date": cutoff_date.isoformat(),
                "cleanup_completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Cleanup failed: {str(e)}"
            )

# Global instance
dedupe_service: Optional[DedupeService] = None

def initialize_dedupe_service(similarity_threshold: float = 0.8):
    """Initialize the global dedupe service instance"""
    global dedupe_service
    dedupe_service = DedupeService(similarity_threshold)

def get_dedupe_service() -> DedupeService:
    """Get the global dedupe service instance"""
    if dedupe_service is None:
        raise HTTPException(
            status_code=500,
            detail="Dedupe service not initialized"
        )
    return dedupe_service
