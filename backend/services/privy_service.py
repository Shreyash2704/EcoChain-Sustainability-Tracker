"""
Privy Service - Token validation and metadata management
Handles authentication token validation and user metadata fetching
"""

import requests
import json
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError

class PrivyService:
    def __init__(self, app_id: str, app_secret: str, api_url: str = "https://auth.privy.io/api/v1"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.api_url = api_url
        self.jwks_url = f"{api_url}/.well-known/jwks.json"
        self._jwks_cache = None
        self._jwks_cache_expiry = None
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a Privy authentication token
        
        Args:
            token: JWT token from Privy
            
        Returns:
            Dict containing user information and validation status
        """
        try:
            # Get JWKS for token verification
            jwks = await self._get_jwks()
            
            # Decode and verify token
            decoded_token = jwt.decode(
                token,
                jwks,
                algorithms=['RS256'],
                audience=self.app_id,
                options={"verify_exp": True}
            )
            
            # Extract user information
            user_id = decoded_token.get('sub')
            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token: missing user ID"
                )
            
            # Get additional user metadata
            user_metadata = await self.get_user_metadata(user_id)
            
            return {
                "valid": True,
                "user_id": user_id,
                "token_expires_at": datetime.fromtimestamp(decoded_token.get('exp', 0)).isoformat(),
                "issued_at": datetime.fromtimestamp(decoded_token.get('iat', 0)).isoformat(),
                "metadata": user_metadata,
                "wallet_address": user_metadata.get('wallet_address'),
                "email": user_metadata.get('email'),
                "phone": user_metadata.get('phone')
            }
            
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Token validation failed: {str(e)}"
            )
    
    async def get_user_metadata(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch user metadata from Privy
        
        Args:
            user_id: Privy user ID
            
        Returns:
            Dict containing user metadata
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.app_secret}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/users/{user_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch user metadata: {response.text}"
                )
            
            user_data = response.json()
            
            # Extract relevant information
            metadata = {
                "user_id": user_id,
                "created_at": user_data.get('createdAt'),
                "updated_at": user_data.get('updatedAt'),
                "email": None,
                "phone": None,
                "wallet_address": None,
                "linked_accounts": []
            }
            
            # Extract linked accounts
            linked_accounts = user_data.get('linkedAccounts', [])
            for account in linked_accounts:
                account_type = account.get('type')
                account_address = account.get('address')
                
                if account_type == 'email':
                    metadata['email'] = account_address
                elif account_type == 'phone':
                    metadata['phone'] = account_address
                elif account_type in ['wallet', 'ethereum', 'polygon']:
                    metadata['wallet_address'] = account_address
                
                metadata['linked_accounts'].append({
                    "type": account_type,
                    "address": account_address,
                    "verified": account.get('verified', False)
                })
            
            return metadata
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network error fetching user metadata: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch user metadata: {str(e)}"
            )
    
    async def get_user_wallets(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all wallet addresses associated with a user
        
        Args:
            user_id: Privy user ID
            
        Returns:
            List of wallet information
        """
        try:
            metadata = await self.get_user_metadata(user_id)
            wallets = []
            
            for account in metadata.get('linked_accounts', []):
                if account['type'] in ['wallet', 'ethereum', 'polygon', 'bitcoin']:
                    wallets.append({
                        "address": account['address'],
                        "type": account['type'],
                        "verified": account['verified']
                    })
            
            return wallets
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch user wallets: {str(e)}"
            )
    
    async def verify_wallet_ownership(self, user_id: str, wallet_address: str) -> bool:
        """
        Verify that a wallet address belongs to a user
        
        Args:
            user_id: Privy user ID
            wallet_address: Wallet address to verify
            
        Returns:
            Boolean indicating ownership
        """
        try:
            wallets = await self.get_user_wallets(user_id)
            
            for wallet in wallets:
                if wallet['address'].lower() == wallet_address.lower():
                    return wallet['verified']
            
            return False
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to verify wallet ownership: {str(e)}"
            )
    
    async def _get_jwks(self) -> Dict[str, Any]:
        """
        Get JWKS (JSON Web Key Set) for token verification
        Implements caching to avoid repeated requests
        """
        try:
            # Check cache
            if (self._jwks_cache and 
                self._jwks_cache_expiry and 
                datetime.utcnow() < self._jwks_cache_expiry):
                return self._jwks_cache
            
            # Fetch fresh JWKS
            response = requests.get(self.jwks_url, timeout=10)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch JWKS: {response.text}"
                )
            
            jwks = response.json()
            
            # Cache for 1 hour
            self._jwks_cache = jwks
            self._jwks_cache_expiry = datetime.utcnow() + timedelta(hours=1)
            
            return jwks
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network error fetching JWKS: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get JWKS: {str(e)}"
            )
    
    async def create_user_session(self, user_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a user session with metadata
        
        Args:
            user_id: Privy user ID
            metadata: Additional session metadata
            
        Returns:
            Dict containing session information
        """
        try:
            session_data = {
                "user_id": user_id,
                "session_id": f"session_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
                "metadata": metadata
            }
            
            return session_data
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create user session: {str(e)}"
            )

# Global instance (to be initialized with credentials)
privy_service: Optional[PrivyService] = None

def initialize_privy_service(app_id: str, app_secret: str, api_url: str = None):
    """Initialize the global Privy service instance"""
    global privy_service
    privy_service = PrivyService(app_id, app_secret, api_url)

def get_privy_service() -> PrivyService:
    """Get the global Privy service instance"""
    if privy_service is None:
        raise HTTPException(
            status_code=500,
            detail="Privy service not initialized"
        )
    return privy_service
