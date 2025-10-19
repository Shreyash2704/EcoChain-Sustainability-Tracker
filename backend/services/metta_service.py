"""
MeTTa Service - Local MeTTa reasoner integration
Handles calls to local MeTTa reasoner or wrapper for sustainability analysis
"""

import subprocess
import json
import tempfile
import os
from typing import Dict, Any, Optional, List, Union
from fastapi import HTTPException
from datetime import datetime
import asyncio
import aiofiles

class MeTTaService:
    def __init__(self, metta_path: str = None, wrapper_url: str = None):
        self.metta_path = metta_path or os.getenv('METTA_PATH', 'metta')
        # Try to get wrapper URL from settings first, then environment
        if wrapper_url:
            self.wrapper_url = wrapper_url
        else:
            try:
                from core.config import settings
                self.wrapper_url = settings.metta_wrapper_url
            except:
                self.wrapper_url = os.getenv('METTA_WRAPPER_URL')
        self.timeout = 30  # seconds
    
    async def analyze_sustainability_data(
        self, 
        data: Dict[str, Any], 
        analysis_type: str = "carbon_footprint"
    ) -> Dict[str, Any]:
        """
        Analyze sustainability data using MeTTa reasoner
        
        Args:
            data: Sustainability data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dict containing analysis results
        """
        try:
            if self.wrapper_url:
                return await self._call_wrapper_api(data, analysis_type)
            else:
                # Check if MeTTa is available before trying to call it
                if await self._is_metta_available():
                    return await self._call_local_metta(data, analysis_type)
                else:
                    # MeTTa not available, return mock analysis
                    return await self._generate_mock_analysis(data, analysis_type)
                
        except Exception as e:
            # If MeTTa fails, return mock analysis instead of raising error
            print(f"⚠️ MeTTa analysis failed: {str(e)}, using mock analysis")
            return await self._generate_mock_analysis(data, analysis_type)
    
    async def _is_metta_available(self) -> bool:
        """Check if MeTTa is available on the system"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.metta_path, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=5
            )
            return process.returncode == 0
        except (FileNotFoundError, asyncio.TimeoutError, OSError):
            return False
    
    async def _generate_mock_analysis(
        self, 
        data: Dict[str, Any], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """Generate mock analysis when MeTTa is not available"""
        # Extract sustainability metrics from data
        sustainability_metrics = data.get('sustainability_metrics', {})
        
        # Generate mock analysis based on document type
        mock_metrics = {
            "sustainability_document": {
                "carbon_footprint": sustainability_metrics.get('carbon_footprint', 150.5),
                "energy_consumption": sustainability_metrics.get('energy_consumption', 2500),
                "waste_reduction": sustainability_metrics.get('waste_reduction', 15.2),
                "renewable_energy_percentage": sustainability_metrics.get('renewable_energy_percentage', 85.0)
            },
            "carbon_footprint": {
                "carbon_footprint": sustainability_metrics.get('carbon_footprint', 200.0),
                "energy_consumption": sustainability_metrics.get('energy_consumption', 3000),
                "waste_reduction": sustainability_metrics.get('waste_reduction', 20.0),
                "renewable_energy_percentage": sustainability_metrics.get('renewable_energy_percentage', 90.0)
            },
            "certification": {
                "carbon_footprint": sustainability_metrics.get('carbon_footprint', 300.0),
                "energy_consumption": sustainability_metrics.get('energy_consumption', 4000),
                "waste_reduction": sustainability_metrics.get('waste_reduction', 25.0),
                "renewable_energy_percentage": sustainability_metrics.get('renewable_energy_percentage', 95.0)
            },
            "proof_of_impact": {
                "carbon_footprint": sustainability_metrics.get('carbon_footprint', 500.0),
                "energy_consumption": sustainability_metrics.get('energy_consumption', 5000),
                "waste_reduction": sustainability_metrics.get('waste_reduction', 30.0),
                "renewable_energy_percentage": sustainability_metrics.get('renewable_energy_percentage', 100.0)
            }
        }
        
        metrics = mock_metrics.get(analysis_type, mock_metrics["sustainability_document"])
        
        return {
            "analysis_type": analysis_type,
            "sustainability_metrics": metrics,
            "method": "mock_analysis",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "MeTTa not available, using mock analysis"
        }
    
    async def _call_wrapper_api(
        self, 
        data: Dict[str, Any], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Call MeTTa Docker API
        """
        import aiohttp
        
        # Prepare data for MeTTa API
        # Extract data from nested sustainability_metrics if present
        sustainability_metrics = data.get("sustainability_metrics", {})
        
        metta_data = {
            "carbon_footprint": sustainability_metrics.get("carbon_footprint", data.get("carbon_footprint", 0)),
            "waste_reduction_percentage": sustainability_metrics.get("waste_reduction_percentage", sustainability_metrics.get("waste_reduction", data.get("waste_reduction_percentage", 0))),
            "renewable_energy_percentage": sustainability_metrics.get("renewable_energy_percentage", data.get("renewable_energy_percentage", 0)),
            "document_type": data.get("document_type", "sustainability_document"),
            "content": data.get("content", ""),
            "metadata": data.get("metadata", {})
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.wrapper_url}/analyze",
                json=metta_data,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=500,
                        detail=f"MeTTa Docker API error: {error_text}"
                    )
                
                result = await response.json()
                # Convert MeTTa API response to expected format
                return {
                    "impact_score": result.get("impact_score", 0),
                    "token_amount": result.get("token_amount", 0),
                    "should_mint": result.get("should_mint", False),
                    "sustainability_level": result.get("sustainability_level", "fair"),
                    "environmental_impact": result.get("environmental_impact", "medium"),
                    "recommendation": result.get("recommendation", "Continue sustainability efforts"),
                    "reasoning": result.get("reasoning", "MeTTa analysis completed"),
                    "carbon_credits": result.get("carbon_credits", 0),
                    "waste_bonus": result.get("waste_bonus", 0),
                    "renewable_bonus": result.get("renewable_bonus", 0),
                    "document_multiplier": result.get("document_multiplier", 1.0),
                    "method": "metta_docker",
                    "timestamp": datetime.utcnow().isoformat()
                }
    
    async def _call_local_metta(
        self, 
        data: Dict[str, Any], 
        analysis_type: str
    ) -> Dict[str, Any]:
        """
        Call local MeTTa reasoner
        """
        # Create temporary MeTTa script
        metta_script = self._generate_metta_script(data, analysis_type)
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.metta', delete=False) as f:
            f.write(metta_script)
            script_path = f.name
        
        try:
            # Execute MeTTa script
            process = await asyncio.create_subprocess_exec(
                self.metta_path,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            if process.returncode != 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"MeTTa execution failed: {stderr.decode()}"
                )
            
            # Parse MeTTa output
            result = self._parse_metta_output(stdout.decode())
            
            return {
                "analysis_type": analysis_type,
                "result": result,
                "execution_time": self.timeout,
                "timestamp": datetime.utcnow().isoformat(),
                "method": "local_metta"
            }
            
        finally:
            # Clean up temporary file
            os.unlink(script_path)
    
    def _generate_metta_script(self, data: Dict[str, Any], analysis_type: str) -> str:
        """
        Generate MeTTa script for analysis
        """
        script = f"""
; MeTTa script for {analysis_type} analysis
; Generated at {datetime.utcnow().isoformat()}

; Define data facts
"""
        
        # Add data as MeTTa facts
        for key, value in data.items():
            if isinstance(value, (str, int, float)):
                script += f'& {key} {value}\n'
            elif isinstance(value, dict):
                script += f'& {key} {self._dict_to_metta(value)}\n'
            elif isinstance(value, list):
                script += f'& {key} {self._list_to_metta(value)}\n'
        
        # Add analysis rules based on type
        if analysis_type == "carbon_footprint":
            script += self._get_carbon_footprint_rules()
        elif analysis_type == "sustainability_score":
            script += self._get_sustainability_score_rules()
        elif analysis_type == "impact_assessment":
            script += self._get_impact_assessment_rules()
        else:
            script += self._get_generic_analysis_rules()
        
        # Add query
        script += f"""
; Query for results
! {analysis_type}_result
"""
        
        return script
    
    def _dict_to_metta(self, d: Dict[str, Any]) -> str:
        """Convert dictionary to MeTTa format"""
        items = []
        for k, v in d.items():
            if isinstance(v, (str, int, float)):
                items.append(f'({k} {v})')
            else:
                items.append(f'({k} {v})')
        return f'({" ".join(items)})'
    
    def _list_to_metta(self, l: List[Any]) -> str:
        """Convert list to MeTTa format"""
        items = [str(item) for item in l]
        return f'({" ".join(items)})'
    
    def _get_carbon_footprint_rules(self) -> str:
        """Get carbon footprint analysis rules"""
        return """
; Carbon footprint analysis rules
& carbon_footprint_analysis
    (if (and (energy_consumption ?energy) (energy_type ?type))
        (then (carbon_emission ?energy ?type ?emission)))
    
& carbon_footprint_result
    (if (carbon_emission ?energy ?type ?emission)
        (then (total_carbon ?emission)))
"""
    
    def _get_sustainability_score_rules(self) -> str:
        """Get sustainability score analysis rules"""
        return """
; Sustainability score analysis rules
& sustainability_score_analysis
    (if (and (renewable_energy ?percentage) (waste_reduction ?reduction))
        (then (sustainability_score ?percentage ?reduction ?score)))
    
& sustainability_score_result
    (if (sustainability_score ?percentage ?reduction ?score)
        (then (final_score ?score)))
"""
    
    def _get_impact_assessment_rules(self) -> str:
        """Get impact assessment rules"""
        return """
; Impact assessment rules
& impact_assessment_analysis
    (if (and (activity ?activity) (impact_type ?type) (magnitude ?mag))
        (then (environmental_impact ?activity ?type ?mag)))
    
& impact_assessment_result
    (if (environmental_impact ?activity ?type ?mag)
        (then (total_impact ?mag)))
"""
    
    def _get_generic_analysis_rules(self) -> str:
        """Get generic analysis rules"""
        return """
; Generic analysis rules
& generic_analysis
    (if (data ?key ?value)
        (then (analysis_result ?key ?value)))
    
& generic_analysis_result
    (if (analysis_result ?key ?value)
        (then (result ?key ?value)))
"""
    
    def _parse_metta_output(self, output: str) -> Dict[str, Any]:
        """
        Parse MeTTa output into structured data
        """
        result = {}
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('(') and line.endswith(')'):
                # Parse MeTTa expression
                content = line[1:-1]  # Remove parentheses
                parts = content.split()
                
                if len(parts) >= 2:
                    key = parts[0]
                    value = ' '.join(parts[1:])
                    
                    # Try to convert to appropriate type
                    if value.isdigit():
                        result[key] = int(value)
                    elif value.replace('.', '').isdigit():
                        result[key] = float(value)
                    else:
                        result[key] = value
        
        return result
    
    async def get_recommendations(
        self, 
        analysis_result: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get sustainability recommendations based on analysis
        
        Args:
            analysis_result: Results from sustainability analysis
            user_profile: User profile information
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = []
            
            # Carbon footprint recommendations
            if 'total_carbon' in analysis_result:
                carbon_amount = analysis_result['total_carbon']
                
                if carbon_amount > 1000:  # High carbon footprint
                    recommendations.append({
                        "type": "carbon_reduction",
                        "priority": "high",
                        "title": "Reduce Carbon Footprint",
                        "description": "Your carbon footprint is above average. Consider switching to renewable energy sources.",
                        "actions": [
                            "Install solar panels",
                            "Use public transportation",
                            "Reduce energy consumption"
                        ],
                        "potential_savings": f"{carbon_amount * 0.3:.0f} kg CO2/year"
                    })
            
            # Sustainability score recommendations
            if 'final_score' in analysis_result:
                score = analysis_result['final_score']
                
                if score < 70:  # Low sustainability score
                    recommendations.append({
                        "type": "sustainability_improvement",
                        "priority": "medium",
                        "title": "Improve Sustainability Score",
                        "description": "Your sustainability score can be improved with targeted actions.",
                        "actions": [
                            "Increase renewable energy usage",
                            "Implement waste reduction strategies",
                            "Adopt sustainable practices"
                        ],
                        "potential_improvement": f"{100 - score:.0f} points"
                    })
            
            # Generic recommendations based on user profile
            if user_profile.get('sustainability_goals'):
                for goal in user_profile['sustainability_goals']:
                    recommendations.append({
                        "type": "goal_alignment",
                        "priority": "low",
                        "title": f"Work towards: {goal}",
                        "description": f"Align your actions with your goal: {goal}",
                        "actions": [
                            "Set specific milestones",
                            "Track progress regularly",
                            "Celebrate achievements"
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate recommendations: {str(e)}"
            )
    
    async def validate_sustainability_claim(
        self, 
        claim: Dict[str, Any], 
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a sustainability claim against evidence
        
        Args:
            claim: The sustainability claim to validate
            evidence: Supporting evidence data
            
        Returns:
            Dict containing validation results
        """
        try:
            # Combine claim and evidence for analysis
            analysis_data = {
                "claim": claim,
                "evidence": evidence,
                "validation_type": "claim_verification"
            }
            
            # Run analysis
            result = await self.analyze_sustainability_data(
                analysis_data, 
                "claim_validation"
            )
            
            # Determine validation status
            confidence_score = result.get('confidence_score', 0)
            is_valid = confidence_score > 0.7
            
            return {
                "claim": claim,
                "is_valid": is_valid,
                "confidence_score": confidence_score,
                "validation_details": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Claim validation failed: {str(e)}"
            )

# Global instance (to be initialized with MeTTa path or wrapper URL)
metta_service: Optional[MeTTaService] = None

def initialize_metta_service(metta_path: str = None, wrapper_url: str = None):
    """Initialize the global MeTTa service instance"""
    global metta_service
    metta_service = MeTTaService(metta_path, wrapper_url)

def get_metta_service() -> MeTTaService:
    """Get the global MeTTa service instance"""
    if metta_service is None:
        raise HTTPException(
            status_code=500,
            detail="MeTTa service not initialized"
        )
    return metta_service
