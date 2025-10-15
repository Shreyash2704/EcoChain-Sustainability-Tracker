#!/usr/bin/env python3
"""
Direct test of reasoner agent functionality
"""

import asyncio
import json
import base64

async def test_reasoner_direct():
    """Test reasoner agent functions directly"""
    print("🧪 Testing Reasoner Agent Directly")
    print("=" * 50)
    
    try:
        # Import reasoner functions
        from agents.reasoner_agent import analyze_document_and_calculate_credits, calculate_carbon_credits
        
        # Test document content
        test_document = {
            "sustainability_metrics": {
                "carbon_footprint": 200.0,
                "energy_consumption": 3000,
                "waste_reduction": 20.0,
                "renewable_energy_percentage": 90.0
            },
            "company_info": {
                "name": "GreenTech Solutions",
                "industry": "Technology"
            }
        }
        
        # Convert to JSON string
        document_content = json.dumps(test_document, indent=2)
        
        print(f"📄 Test Document:")
        print(f"{document_content}")
        print(f"=" * 50)
        
        # Test carbon credit calculation directly
        print(f"🧮 Testing Carbon Credit Calculation...")
        credit_result = calculate_carbon_credits(
            carbon_footprint=200.0,
            energy_consumption=3000,
            waste_reduction=20.0,
            renewable_energy_percentage=90.0,
            document_type="sustainability_document"
        )
        
        print(f"✅ Credit Calculation Result:")
        print(f"   Should Mint: {credit_result['should_mint']}")
        print(f"   Token Amount: {credit_result['token_amount']}")
        print(f"   Reasoning: {credit_result['reasoning']}")
        print(f"   Impact Score: {credit_result['impact_score']}")
        print(f"=" * 50)
        
        # Test full analysis
        print(f"🔍 Testing Full Analysis...")
        analysis_result = await analyze_document_and_calculate_credits(
            document_content=document_content,
            document_type="sustainability_document",
            metadata='{"description": "Direct test"}',
            user_wallet="0x1234567890abcdef1234567890abcdef12345678"
        )
        
        print(f"✅ Full Analysis Result:")
        print(f"   Should Mint: {analysis_result['should_mint']}")
        print(f"   Token Amount: {analysis_result['token_amount']}")
        print(f"   Carbon Footprint: {analysis_result['carbon_footprint']} kg CO2")
        print(f"   Reasoning: {analysis_result['reasoning']}")
        print(f"   Impact Score: {analysis_result['impact_score']}")
        print(f"=" * 50)
        
        print(f"🎉 Reasoner Agent Test Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Direct Reasoner Agent Test")
    print("=" * 60)
    asyncio.run(test_reasoner_direct())
    print("=" * 60)
    print("🏁 Test completed!")
