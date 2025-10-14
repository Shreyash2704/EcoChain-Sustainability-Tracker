"""
Lighthouse Service - IPFS file upload and management
Handles file uploads to IPFS via Lighthouse and returns Content IDs (CIDs)
"""

import requests
import json
from typing import Dict, Any, Optional, Union
from fastapi import UploadFile, HTTPException
import os
from datetime import datetime

class LighthouseService:
    def __init__(self, api_key: str, gateway_url: str = "https://gateway.lighthouse.storage"):
        self.api_key = api_key
        self.gateway_url = gateway_url
        self.upload_url = "https://api.lighthouse.storage/api/v0/add"
        self.pin_url = "https://api.lighthouse.storage/api/v0/pin/add"
    
    async def upload_file(self, file: UploadFile, pin: bool = True) -> Dict[str, Any]:
        """
        Upload a file to IPFS via Lighthouse
        
        Args:
            file: FastAPI UploadFile object
            pin: Whether to pin the file to ensure persistence
            
        Returns:
            Dict containing CID and metadata
        """
        try:
            # Read file content
            file_content = await file.read()
            
            # Prepare multipart form data
            files = {
                'file': (file.filename, file_content, file.content_type)
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Upload to IPFS
            response = requests.post(
                self.upload_url,
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Lighthouse upload failed: {response.text}"
                )
            
            result = response.json()
            cid = result.get('Hash')
            
            if not cid:
                raise HTTPException(
                    status_code=500,
                    detail="No CID returned from Lighthouse"
                )
            
            # Pin the file if requested
            if pin:
                await self.pin_file(cid)
            
            return {
                "cid": cid,
                "filename": file.filename,
                "size": len(file_content),
                "content_type": file.content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "gateway_url": f"{self.gateway_url}/ipfs/{cid}",
                "pinned": pin
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network error during upload: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {str(e)}"
            )
    
    async def upload_json(self, data: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """
        Upload JSON data to IPFS
        
        Args:
            data: Dictionary to upload as JSON
            filename: Optional filename for the JSON file
            
        Returns:
            Dict containing CID and metadata
        """
        try:
            if not filename:
                filename = f"data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert to JSON string
            json_content = json.dumps(data, indent=2).encode('utf-8')
            
            # Prepare multipart form data
            files = {
                'file': (filename, json_content, 'application/json')
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Upload to IPFS
            response = requests.post(
                self.upload_url,
                files=files,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Lighthouse JSON upload failed: {response.text}"
                )
            
            result = response.json()
            cid = result.get('Hash')
            
            if not cid:
                raise HTTPException(
                    status_code=500,
                    detail="No CID returned from Lighthouse"
                )
            
            # Pin the file
            await self.pin_file(cid)
            
            return {
                "cid": cid,
                "filename": filename,
                "size": len(json_content),
                "content_type": "application/json",
                "uploaded_at": datetime.utcnow().isoformat(),
                "gateway_url": f"{self.gateway_url}/ipfs/{cid}",
                "pinned": True,
                "data_keys": list(data.keys()) if isinstance(data, dict) else []
            }
            
        except json.JSONEncodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON data: {str(e)}"
            )
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network error during JSON upload: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"JSON upload failed: {str(e)}"
            )
    
    async def pin_file(self, cid: str) -> Dict[str, Any]:
        """
        Pin a file to ensure persistence
        
        Args:
            cid: Content ID to pin
            
        Returns:
            Dict with pin status
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            params = {
                'arg': cid
            }
            
            response = requests.post(
                self.pin_url,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Pin failed: {response.text}"
                )
            
            result = response.json()
            
            return {
                "cid": cid,
                "pinned": True,
                "pinned_at": datetime.utcnow().isoformat(),
                "pins": result.get('Pins', [])
            }
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Network error during pin: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Pin failed: {str(e)}"
            )
    
    async def get_file_info(self, cid: str) -> Dict[str, Any]:
        """
        Get information about a file from IPFS
        
        Args:
            cid: Content ID
            
        Returns:
            Dict with file information
        """
        try:
            # Try to fetch file metadata from gateway
            response = requests.head(f"{self.gateway_url}/ipfs/{cid}", timeout=10)
            
            if response.status_code == 200:
                return {
                    "cid": cid,
                    "exists": True,
                    "content_type": response.headers.get('content-type'),
                    "content_length": response.headers.get('content-length'),
                    "last_modified": response.headers.get('last-modified'),
                    "gateway_url": f"{self.gateway_url}/ipfs/{cid}"
                }
            else:
                return {
                    "cid": cid,
                    "exists": False,
                    "error": f"File not found or inaccessible (status: {response.status_code})"
                }
                
        except requests.RequestException as e:
            return {
                "cid": cid,
                "exists": False,
                "error": f"Network error: {str(e)}"
            }
    
    async def download_file(self, cid: str) -> bytes:
        """
        Download file content from IPFS
        
        Args:
            cid: Content ID
            
        Returns:
            File content as bytes
        """
        try:
            response = requests.get(f"{self.gateway_url}/ipfs/{cid}", timeout=30)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {cid}"
                )
            
            return response.content
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Download failed: {str(e)}"
            )

# Global instance (to be initialized with API key)
lighthouse_service: Optional[LighthouseService] = None

def initialize_lighthouse_service(api_key: str, gateway_url: str = None):
    """Initialize the global Lighthouse service instance"""
    global lighthouse_service
    lighthouse_service = LighthouseService(api_key, gateway_url)

def get_lighthouse_service() -> LighthouseService:
    """Get the global Lighthouse service instance"""
    if lighthouse_service is None:
        raise HTTPException(
            status_code=500,
            detail="Lighthouse service not initialized"
        )
    return lighthouse_service
