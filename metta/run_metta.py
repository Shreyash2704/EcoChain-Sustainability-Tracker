#!/usr/bin/env python3
"""
MeTTa Service Runner for EcoChain Sustainability Analysis
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api.server import app
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for MeTTa service"""
    logger.info("🚀 Starting MeTTa Sustainability Analysis Service")
    
    # Get configuration from environment
    host = os.getenv("METTA_HOST", "0.0.0.0")
    port = int(os.getenv("METTA_PORT", "8080"))
    
    logger.info(f"📡 Starting server on {host}:{port}")
    logger.info("🧠 MeTTa Sustainability Analysis API ready")
    
    # Start the FastAPI server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
