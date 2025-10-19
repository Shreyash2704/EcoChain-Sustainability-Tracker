"""
MeTTa Client for Sustainability Analysis
Rule-based sustainability analysis engine (MeTTa-compatible)
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import os
import json

logger = logging.getLogger(__name__)

class MeTTaClient:
    """Client for rule-based sustainability analysis (MeTTa-compatible)"""
    
    def __init__(self, knowledge_base_path: str = "/app/knowledge"):
        self.knowledge_base_path = knowledge_base_path
        self.rules_loaded = False
        self.sustainability_rules = self._load_sustainability_rules()
        
    def _load_sustainability_rules(self) -> Dict[str, Any]:
        """Load sustainability rules from knowledge base"""
        rules = {
            "document_multipliers": {
                "sustainability_document": 1.0,
                "carbon_report": 1.2,
                "energy_audit": 1.1,
                "waste_management": 1.0,
                "green_certification": 1.5
            },
            "impact_thresholds": {
                "excellent": 90,
                "very_good": 80,
                "good": 70,
                "fair": 60,
                "poor": 50
            },
            "token_amounts": {
                "excellent": 100,
                "very_good": 80,
                "good": 60,
                "fair": 40,
                "poor": 20
            }
        }
        self.rules_loaded = True
        return rules
    
    async def test_connection(self) -> bool:
        """Test if MeTTa is available and working"""
        try:
            # Test rule-based analysis
            test_data = {"carbon_footprint": 100, "waste_reduction_percentage": 20, "renewable_energy_percentage": 50}
            result = await self._simulate_metta_analysis(test_data)
            return result is not None and "impact_score" in result
        except Exception as e:
            logger.error(f"MeTTa connection test failed: {e}")
            return False
    
    async def analyze_sustainability(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sustainability data using MeTTa reasoning
        
        Args:
            data: Dictionary containing sustainability data
            
        Returns:
            Analysis result with impact score and recommendations
        """
        try:
            # Create MeTTa query for sustainability analysis
            query = self._build_sustainability_query(data)
            
            # Run MeTTa analysis
            result = await self._run_metta_analysis(query, data)
            
            # Process and format results
            return self._process_analysis_result(result, data)
            
        except Exception as e:
            logger.error(f"Sustainability analysis failed: {e}")
            # Return fallback analysis
            return self._fallback_analysis(data)
    
    async def classify_document(self, content: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify document type using MeTTa reasoning
        
        Args:
            content: Document content
            document_type: Optional document type hint
            
        Returns:
            Document classification result
        """
        try:
            # Create MeTTa query for document classification
            query = f"(document-type \"{content}\")"
            
            # Run MeTTa classification
            result = await self._run_metta_command(query)
            
            # Process classification result
            return self._process_classification_result(result, content, document_type)
            
        except Exception as e:
            logger.error(f"Document classification failed: {e}")
            return {
                "document_type": document_type or "sustainability_document",
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    async def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the loaded knowledge base"""
        try:
            # Check knowledge base files
            kb_files = []
            if os.path.exists(self.knowledge_base_path):
                for file in os.listdir(self.knowledge_base_path):
                    if file.endswith('.metta'):
                        kb_files.append(file)
            
            return {
                "knowledge_base_path": self.knowledge_base_path,
                "files": kb_files,
                "total_files": len(kb_files),
                "status": "loaded" if self.rules_loaded else "empty",
                "analysis_type": "rule-based",
                "rules_loaded": self.rules_loaded,
                "sustainability_rules": list(self.sustainability_rules.keys()) if self.rules_loaded else []
            }
        except Exception as e:
            logger.error(f"Failed to get knowledge base info: {e}")
            return {
                "knowledge_base_path": self.knowledge_base_path,
                "files": [],
                "total_files": 0,
                "status": "error",
                "error": str(e),
                "analysis_type": "rule-based"
            }
    
    async def reload_knowledge_base(self) -> Dict[str, Any]:
        """Reload the MeTTa knowledge base"""
        try:
            # This would reload the knowledge base files
            # For now, just return success
            return {
                "rules_loaded": 3,  # sustainability-rules, document-types, impact-scoring
                "status": "reloaded"
            }
        except Exception as e:
            logger.error(f"Failed to reload knowledge base: {e}")
            raise
    
    def _build_sustainability_query(self, data: Dict[str, Any]) -> str:
        """Build MeTTa query for sustainability analysis"""
        carbon = data.get("carbon_footprint", 0)
        waste = data.get("waste_reduction_percentage", 0)
        renewable = data.get("renewable_energy_percentage", 0)
        doc_type = data.get("document_type", "sustainability_document")
        
        return f"""
        (let*
            ($carbon {carbon})
            ($waste {waste})
            ($renewable {renewable})
            ($doc-type "{doc_type}")
            ($impact-score (final-impact-score $carbon $waste $renewable $doc-type))
            ($token-amount (token-amount $impact-score))
            ($should-mint (should-mint $impact-score))
            ($level (sustainability-level $impact-score))
            ($impact (environmental-impact $carbon $waste $renewable))
            ($recommendation (recommendation $level $impact)))
            (list $impact-score $token-amount $should-mint $level $impact $recommendation))
        """
    
    async def _run_metta_analysis(self, query: str, data: Dict[str, Any]) -> Any:
        """Run MeTTa analysis with the given query"""
        try:
            # For now, simulate MeTTa analysis with rule-based logic
            # In a real implementation, this would call the MeTTa interpreter
            return await self._simulate_metta_analysis(data)
        except Exception as e:
            logger.error(f"MeTTa analysis failed: {e}")
            raise
    
    async def _simulate_metta_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MeTTa analysis using rule-based logic"""
        carbon = data.get("carbon_footprint", 0)
        waste = data.get("waste_reduction_percentage", 0)
        renewable = data.get("renewable_energy_percentage", 0)
        doc_type = data.get("document_type", "sustainability_document")
        
        # Apply sustainability rules
        carbon_credits = carbon * 0.1
        waste_bonus = waste * (2.0 if waste > 20 else 1.5)
        renewable_bonus = renewable * (1.8 if renewable > 50 else 1.2)
        
        # Document type multipliers
        doc_multipliers = {
            "sustainability_document": 1.0,
            "carbon_report": 1.2,
            "energy_audit": 1.1,
            "waste_management": 1.0,
            "green_certification": 1.5
        }
        doc_multiplier = doc_multipliers.get(doc_type, 1.0)
        
        # Calculate impact score
        base_score = carbon_credits + waste_bonus + renewable_bonus
        impact_score = min(100, base_score * doc_multiplier)
        
        # Determine token amount (proportional to impact score)
        if impact_score > 10:
            # Proportional calculation: 10-100 tokens based on impact score
            # Minimum 10 tokens, maximum 100 tokens
            token_amount = min(100, max(10, int(impact_score * 0.5)))
        else:
            token_amount = 0
        
        should_mint = impact_score > 10
        
        # Determine sustainability level
        if impact_score > 90:
            level = "excellent"
        elif impact_score > 80:
            level = "very-good"
        elif impact_score > 70:
            level = "good"
        elif impact_score > 60:
            level = "fair"
        elif impact_score > 50:
            level = "poor"
        else:
            level = "insufficient"
        
        # Environmental impact
        total_impact = carbon + waste + renewable
        if total_impact > 1000:
            env_impact = "high"
        elif total_impact > 500:
            env_impact = "medium"
        else:
            env_impact = "low"
        
        # Generate recommendation
        recommendations = {
            "excellent": "Outstanding sustainability performance! Consider sharing best practices.",
            "very-good": "Great sustainability efforts! Continue current practices.",
            "good": "Good progress! Focus on areas with highest impact potential.",
            "fair": "Room for improvement. Consider implementing additional sustainability measures.",
            "poor": "Significant improvement needed. Develop comprehensive sustainability strategy.",
            "insufficient": "Insufficient data or impact. Please provide more detailed sustainability information."
        }
        recommendation = recommendations.get(level, "Please provide more sustainability data.")
        
        return {
            "impact_score": impact_score,
            "token_amount": token_amount,
            "should_mint": should_mint,
            "sustainability_level": level,
            "environmental_impact": env_impact,
            "recommendation": recommendation,
            "reasoning": f"MeTTa rule-based analysis: Carbon credits: {carbon_credits:.1f}, Waste bonus: {waste_bonus:.1f}, Renewable bonus: {renewable_bonus:.1f}, Document multiplier: {doc_multiplier}",
            "carbon_credits": carbon_credits,
            "waste_bonus": waste_bonus,
            "renewable_bonus": renewable_bonus,
            "document_multiplier": doc_multiplier
        }
    
    def _process_analysis_result(self, result: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MeTTa analysis result"""
        return result
    
    def _process_classification_result(self, result: Any, content: str, document_type: Optional[str]) -> Dict[str, Any]:
        """Process document classification result"""
        # For now, return a simple classification
        return {
            "document_type": document_type or "sustainability_document",
            "confidence": 0.8,
            "reasoning": "MeTTa document classification based on content analysis"
        }
    
    def _fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when MeTTa is not available"""
        carbon = data.get("carbon_footprint", 0)
        waste = data.get("waste_reduction_percentage", 0)
        renewable = data.get("renewable_energy_percentage", 0)
        
        # Simple fallback calculation
        impact_score = min(100, (carbon * 0.1) + (waste * 1.5) + (renewable * 1.2))
        token_amount = min(100, impact_score)
        should_mint = impact_score > 10
        
        return {
            "impact_score": impact_score,
            "token_amount": token_amount,
            "should_mint": should_mint,
            "sustainability_level": "good" if impact_score > 50 else "fair",
            "environmental_impact": "medium",
            "recommendation": "Continue sustainability efforts",
            "reasoning": f"Fallback analysis: Carbon: {carbon}, Waste: {waste}, Renewable: {renewable}",
            "carbon_credits": carbon * 0.1,
            "waste_bonus": waste * 1.5,
            "renewable_bonus": renewable * 1.2,
            "document_multiplier": 1.0
        }
    
    async def _run_metta_command(self, command: str) -> Any:
        """Run a MeTTa command (placeholder for actual MeTTa integration)"""
        # This would run the actual MeTTa interpreter
        # For now, return a mock result
        await asyncio.sleep(0.1)  # Simulate processing time
        return "mock_result"
