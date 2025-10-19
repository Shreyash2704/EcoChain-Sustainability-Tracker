"""
OpenAI Service for natural language processing
Handles intent classification and data extraction for chat interface
"""

import openai
from typing import Dict, Any, Optional
import json
import re
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        
        if not self.api_key:
            logger.warning("⚠️ OpenAI API key not configured")
            self.client = None
        else:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def classify_intent(self, message: str) -> str:
        """
        Classify user intent using OpenAI GPT-4o-mini
        """
        if not self.client:
            logger.warning("OpenAI client not available, using fallback")
            return await self._fallback_intent_classification(message)
        
        try:
            system_prompt = """You are an intent classifier for a sustainability tracking system called EcoChain.

Classify user messages into one of these intents:
- get_credits: User asking about their carbon credits, token balance, or account summary
- upload_document: User wants to upload or analyze a sustainability document/report
- calculate_metrics: User asking what metrics they need for a target credit amount
- get_recommendations: User asking how to improve their sustainability score or get tips
- general_query: General sustainability questions or unclear requests

Examples:
- "How much credits do I have?" → get_credits
- "Upload this document" → upload_document
- "What do I need for 100 credits?" → calculate_metrics
- "How can I improve my score?" → get_recommendations
- "What is sustainability?" → general_query

Respond with ONLY the intent name, nothing else."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            intent = response.choices[0].message.content.strip().lower()
            logger.info(f"🎯 OpenAI classified intent: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"❌ OpenAI intent classification failed: {e}")
            return await self._fallback_intent_classification(message)
    
    async def extract_data(self, message: str, intent: str) -> Dict[str, Any]:
        """
        Extract relevant data from user message based on intent
        """
        if not self.client:
            return await self._fallback_data_extraction(message, intent)
        
        try:
            if intent == "calculate_metrics":
                return await self._extract_target_credits(message)
            elif intent == "get_credits":
                return await self._extract_wallet_info(message)
            elif intent == "upload_document":
                return await self._extract_upload_info(message)
            elif intent == "get_recommendations":
                return await self._extract_recommendation_context(message)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}")
            return {}
    
    async def _extract_target_credits(self, message: str) -> Dict[str, Any]:
        """Extract target credit amount from message"""
        if not self.client:
            # Fallback: simple regex
            numbers = re.findall(r'\d+', message)
            if numbers:
                return {"target_credits": int(numbers[0])}
            return {}
        
        try:
            system_prompt = """Extract the target credit amount from the user's message.
            Return a JSON object with the target_credits number.
            If no specific number is mentioned, return {"target_credits": 100}.
            
            Examples:
            "I want 50 credits" → {"target_credits": 50}
            "What do I need for 200 tokens?" → {"target_credits": 200}
            "How to get more credits?" → {"target_credits": 100}"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"❌ Target credits extraction failed: {e}")
            # Fallback
            numbers = re.findall(r'\d+', message)
            if numbers:
                return {"target_credits": int(numbers[0])}
            return {"target_credits": 100}
    
    async def _extract_wallet_info(self, message: str) -> Dict[str, Any]:
        """Extract wallet-related information"""
        return {}  # Wallet address comes from context, not message
    
    async def _extract_upload_info(self, message: str) -> Dict[str, Any]:
        """Extract upload-related information"""
        return {
            "has_file": "file" in message.lower() or "upload" in message.lower(),
            "document_type": "sustainability_document"  # Default
        }
    
    async def _extract_recommendation_context(self, message: str) -> Dict[str, Any]:
        """Extract context for recommendations"""
        return {
            "current_score": None,  # Would need to be fetched from analytics
            "focus_area": self._detect_focus_area(message)
        }
    
    def _detect_focus_area(self, message: str) -> str:
        """Detect what area user wants to focus on"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["carbon", "emission", "co2"]):
            return "carbon_footprint"
        elif any(word in message_lower for word in ["waste", "recycling"]):
            return "waste_reduction"
        elif any(word in message_lower for word in ["energy", "renewable", "solar"]):
            return "renewable_energy"
        else:
            return "general"
    
    async def generate_response(self, data: Dict[str, Any], intent: str) -> str:
        """
        Generate natural language response from data
        """
        if not self.client:
            return await self._fallback_response_generation(data, intent)
        
        try:
            system_prompt = f"""You are a helpful assistant for EcoChain, a sustainability tracking system.
            Generate a friendly, informative response based on the data and intent.
            
            Intent: {intent}
            Data: {json.dumps(data, indent=2)}
            
            Make the response:
            - Friendly and encouraging
            - Include specific numbers when available
            - Suggest next steps when appropriate
            - Keep it concise but informative"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate a response for the user."}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Response generation failed: {e}")
            return await self._fallback_response_generation(data, intent)
    
    async def _fallback_intent_classification(self, message: str) -> str:
        """Fallback intent classification using keyword matching"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["credit", "token", "balance", "how much"]):
            return "get_credits"
        elif any(word in message_lower for word in ["upload", "document", "file", "json"]):
            return "upload_document"
        elif any(word in message_lower for word in ["calculate", "need", "target", "score"]):
            return "calculate_metrics"
        elif any(word in message_lower for word in ["recommend", "improve", "increase", "tips"]):
            return "get_recommendations"
        else:
            return "general_query"
    
    async def _fallback_data_extraction(self, message: str, intent: str) -> Dict[str, Any]:
        """Fallback data extraction"""
        if intent == "calculate_metrics":
            numbers = re.findall(r'\d+', message)
            if numbers:
                return {"target_credits": int(numbers[0])}
            return {"target_credits": 100}
        return {}
    
    async def _fallback_response_generation(self, data: Dict[str, Any], intent: str) -> str:
        """Fallback response generation"""
        if intent == "get_credits":
            credits = data.get("total_credits", 0)
            return f"You have {credits} ECO tokens in your account!"
        elif intent == "upload_document":
            return "Please upload your sustainability document for analysis."
        elif intent == "calculate_metrics":
            target = data.get("target_credits", 100)
            return f"To earn {target} credits, you would need to improve your sustainability metrics."
        elif intent == "get_recommendations":
            return "Here are some ways to improve your sustainability score: focus on renewable energy, reduce waste, and track your carbon footprint."
        else:
            return "I'm here to help with your sustainability tracking. What would you like to know?"
