"""
MeTTa HTTP Wrapper API for EcoChain Sustainability Analysis
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging
from .metta_client import MeTTaClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MeTTa Sustainability Analysis API",
    description="HTTP wrapper for MeTTa reasoner for sustainability analysis",
    version="1.0.0"
)

# Initialize MeTTa client
metta_client = MeTTaClient()

class SustainabilityData(BaseModel):
    """Input data for sustainability analysis"""
    carbon_footprint: float
    waste_reduction_percentage: float
    renewable_energy_percentage: float
    document_type: str
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    """Result of sustainability analysis"""
    impact_score: float
    token_amount: float
    should_mint: bool
    sustainability_level: str
    environmental_impact: str
    recommendation: str
    reasoning: str
    carbon_credits: float
    waste_bonus: float
    renewable_bonus: float
    document_multiplier: float

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MeTTa connection
        test_result = await metta_client.test_connection()
        return {
            "status": "healthy",
            "metta_available": test_result,
            "service": "MeTTa Sustainability Analysis API"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "metta_available": False,
            "error": str(e)
        }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_sustainability(data: SustainabilityData):
    """
    Analyze sustainability data using MeTTa reasoner
    
    Args:
        data: Sustainability data to analyze
        
    Returns:
        Analysis result with impact score and recommendations
    """
    try:
        logger.info(f"Analyzing sustainability data: {data.document_type}")
        
        # Convert input data to MeTTa format
        metta_data = {
            "carbon_footprint": data.carbon_footprint,
            "waste_reduction": data.waste_reduction_percentage,
            "renewable_energy": data.renewable_energy_percentage,
            "document_type": data.document_type,
            "content": data.content or "",
            "metadata": data.metadata or {}
        }
        
        # Run MeTTa analysis
        result = await metta_client.analyze_sustainability(metta_data)
        
        logger.info(f"Analysis complete: impact_score={result['impact_score']}, should_mint={result['should_mint']}")
        
        return AnalysisResult(**result)
        
    except Exception as e:
        logger.error(f"Sustainability analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sustainability analysis failed: {str(e)}"
        )

@app.post("/classify-document")
async def classify_document(content: str, document_type: Optional[str] = None):
    """
    Classify document type using MeTTa reasoning
    
    Args:
        content: Document content to classify
        document_type: Optional hint for document type
        
    Returns:
        Document classification result
    """
    try:
        logger.info(f"Classifying document with type hint: {document_type}")
        
        result = await metta_client.classify_document(content, document_type)
        
        return {
            "document_type": result["document_type"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"]
        }
        
    except Exception as e:
        logger.error(f"Document classification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Document classification failed: {str(e)}"
        )

@app.get("/knowledge-base")
async def get_knowledge_base():
    """
    Get information about the MeTTa knowledge base
    
    Returns:
        Knowledge base information
    """
    try:
        kb_info = await metta_client.get_knowledge_base_info()
        return kb_info
    except Exception as e:
        logger.error(f"Failed to get knowledge base info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get knowledge base info: {str(e)}"
        )

@app.post("/reload-knowledge")
async def reload_knowledge_base():
    """
    Reload the MeTTa knowledge base
    
    Returns:
        Reload status
    """
    try:
        result = await metta_client.reload_knowledge_base()
        return {
            "status": "success",
            "message": "Knowledge base reloaded successfully",
            "rules_loaded": result["rules_loaded"]
        }
    except Exception as e:
        logger.error(f"Failed to reload knowledge base: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload knowledge base: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
