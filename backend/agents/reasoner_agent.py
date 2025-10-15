from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from typing import Dict, Any, Optional
import json
import base64
from datetime import datetime

# Create the reasoner agent
reasoner_agent = Agent(
    name="EcoChain ReasonerAgent",
    seed="eco_reasoner_agent_seed",
    port=8003
)

# Handle reasoning requests from verifier agent
@reasoner_agent.on_message(model=ChatMessage)
async def handle_verifier_data(ctx: Context, sender: str, msg: ChatMessage):
    """Handle document analysis requests from verifier agent"""
    try:
        # Parse incoming data from verifier agent
        reasoning_data = json.loads(msg.content[0].text)
        
        # Extract data
        upload_id = reasoning_data.get("upload_id")
        cid = reasoning_data.get("cid")
        gateway_url = reasoning_data.get("gateway_url")
        document_content = reasoning_data.get("document_content")
        user_wallet = reasoning_data.get("user_wallet")
        document_type = reasoning_data.get("document_type")
        filename = reasoning_data.get("filename")
        content_type = reasoning_data.get("content_type")
        metadata = reasoning_data.get("metadata")
        timestamp = reasoning_data.get("timestamp")
        
        print(f"\n🧠 REASONING ANALYSIS STARTED")
        print(f"=" * 50)
        print(f"📋 Upload ID: {upload_id}")
        print(f"🔗 CID: {cid}")
        print(f"👤 User Wallet: {user_wallet}")
        print(f"📄 Document: {filename} ({content_type})")
        print(f"📊 Type: {document_type}")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"=" * 50)
        
        # Decode document content if it's base64 encoded
        if document_content:
            try:
                decoded_content = base64.b64decode(document_content).decode('utf-8')
                print(f"📝 Document Content Preview: {decoded_content[:200]}...")
            except:
                print(f"📝 Document Content: {document_content[:200]}...")
        
        # Parse metadata if available
        if metadata:
            try:
                metadata_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
                print(f"🏷️ Metadata: {metadata_dict}")
            except:
                print(f"🏷️ Metadata: {metadata}")
        
        # Phase 2: Implement MeTTa integration and carbon credit calculation
        analysis_result = await analyze_document_and_calculate_credits(
            document_content=document_content,
            document_type=document_type,
            metadata=metadata,
            user_wallet=user_wallet
        )
        
        # Display results
        print(f"\n🎯 CARBON CREDIT ANALYSIS")
        print(f"=" * 50)
        print(f"✅ Should Mint Tokens: {analysis_result['should_mint']}")
        print(f"🪙 Token Amount: {analysis_result['token_amount']}")
        print(f"📊 Carbon Footprint: {analysis_result['carbon_footprint']} kg CO2")
        print(f"💡 Reasoning: {analysis_result['reasoning']}")
        print(f"📈 Impact Score: {analysis_result['impact_score']}/100")
        print(f"=" * 50)
        
        # Send response back to verifier agent
        response_data = {
            "upload_id": upload_id,
            "analysis_completed": True,
            "should_mint": analysis_result['should_mint'],
            "token_amount": analysis_result['token_amount'],
            "reasoning": analysis_result['reasoning'],
            "carbon_footprint": analysis_result['carbon_footprint'],
            "impact_score": analysis_result['impact_score'],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = ChatMessage(
            content=[TextContent(
                text=json.dumps(response_data)
            )]
        )
        await ctx.send(sender, response)
        
        print(f"📤 Analysis results sent back to verifier agent")
        print(f"🏁 REASONING ANALYSIS COMPLETED\n")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing reasoning data: {e}")
    except Exception as e:
        print(f"❌ Error in reasoning analysis: {e}")


async def analyze_document_and_calculate_credits(
    document_content: str,
    document_type: str,
    metadata: Optional[str],
    user_wallet: str
) -> Dict[str, Any]:
    """
    Analyze document using MeTTa service and calculate carbon credits
    """
    try:
        # Import MeTTa service
        from services.metta_service import MeTTaService
        
        # Initialize MeTTa service
        metta_service = MeTTaService()
        
        # Decode document content if base64 encoded
        try:
            decoded_content = base64.b64decode(document_content).decode('utf-8')
        except:
            decoded_content = document_content
        
        print(f"🔍 Starting MeTTa analysis...")
        
        # Parse document content to extract sustainability data
        try:
            document_data = json.loads(decoded_content)
        except:
            # If not JSON, create a mock structure
            document_data = {
                "sustainability_metrics": {
                    "carbon_footprint": 150.5,
                    "energy_consumption": 2500,
                    "waste_reduction": 15.2,
                    "renewable_energy_percentage": 85.0
                }
            }
        
        # Use MeTTa service to analyze the sustainability data
        metta_result = await metta_service.analyze_sustainability_data(
            data=document_data,
            analysis_type=document_type
        )
        
        print(f"✅ MeTTa analysis completed")
        
        # Extract sustainability metrics from MeTTa result
        sustainability_metrics = metta_result.get('sustainability_metrics', {})
        carbon_footprint = sustainability_metrics.get('carbon_footprint', 0)
        energy_consumption = sustainability_metrics.get('energy_consumption', 0)
        waste_reduction = sustainability_metrics.get('waste_reduction', 0)
        renewable_energy_percentage = sustainability_metrics.get('renewable_energy_percentage', 0)
        
        # Calculate carbon credits based on sustainability metrics
        credit_calculation = calculate_carbon_credits(
            carbon_footprint=carbon_footprint,
            energy_consumption=energy_consumption,
            waste_reduction=waste_reduction,
            renewable_energy_percentage=renewable_energy_percentage,
            document_type=document_type
        )
        
        return {
            "should_mint": credit_calculation['should_mint'],
            "token_amount": credit_calculation['token_amount'],
            "carbon_footprint": carbon_footprint,
            "reasoning": credit_calculation['reasoning'],
            "impact_score": credit_calculation['impact_score'],
            "metta_analysis": metta_result
        }
        
    except ImportError:
        print(f"⚠️ MeTTa service not available, using mock analysis")
        return await mock_carbon_credit_analysis(document_content, document_type, metadata)
    except Exception as e:
        print(f"❌ Error in MeTTa analysis: {e}")
        return await mock_carbon_credit_analysis(document_content, document_type, metadata)


def calculate_carbon_credits(
    carbon_footprint: float,
    energy_consumption: float,
    waste_reduction: float,
    renewable_energy_percentage: float,
    document_type: str
) -> Dict[str, Any]:
    """
    Calculate carbon credits based on sustainability metrics
    """
    # Base credit calculation rules
    base_credits = 0
    reasoning_parts = []
    
    # Carbon footprint reduction (1 credit per kg CO2 saved)
    if carbon_footprint > 0:
        carbon_credits = min(carbon_footprint * 0.1, 100)  # Max 100 credits from carbon
        base_credits += carbon_credits
        reasoning_parts.append(f"Carbon footprint reduction: {carbon_credits:.1f} credits")
    
    # Energy efficiency bonus
    if renewable_energy_percentage >= 50:
        energy_bonus = min(energy_consumption * 0.01, 50)  # Max 50 credits from energy
        base_credits += energy_bonus
        reasoning_parts.append(f"Renewable energy adoption ({renewable_energy_percentage}%): {energy_bonus:.1f} credits")
    
    # Waste reduction bonus
    if waste_reduction > 0:
        waste_bonus = min(waste_reduction * 2, 30)  # Max 30 credits from waste
        base_credits += waste_bonus
        reasoning_parts.append(f"Waste reduction ({waste_reduction}%): {waste_bonus:.1f} credits")
    
    # Document type multiplier
    type_multipliers = {
        "sustainability_document": 1.0,
        "carbon_footprint": 1.2,
        "certification": 1.5,
        "proof_of_impact": 2.0
    }
    
    multiplier = type_multipliers.get(document_type, 1.0)
    final_credits = base_credits * multiplier
    
    # Calculate impact score (0-100)
    impact_score = min((final_credits / 2) * 10, 100)  # Scale to 0-100
    
    # Decision logic
    should_mint = final_credits >= 10  # Minimum threshold for minting
    
    if not should_mint:
        reasoning_parts.append("Below minimum threshold (10 credits) for token minting")
    
    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No significant sustainability impact detected"
    
    return {
        "should_mint": should_mint,
        "token_amount": round(final_credits, 2),
        "reasoning": reasoning,
        "impact_score": round(impact_score, 1)
    }


async def mock_carbon_credit_analysis(
    document_content: str,
    document_type: str,
    metadata: Optional[str]
) -> Dict[str, Any]:
    """
    Mock carbon credit analysis when MeTTa service is not available
    """
    print(f"🎭 Using mock analysis for demonstration")
    
    # Mock sustainability metrics based on document type
    mock_metrics = {
        "sustainability_document": {
            "carbon_footprint": 150.5,
            "energy_consumption": 2500,
            "waste_reduction": 15.2,
            "renewable_energy_percentage": 85.0
        },
        "carbon_footprint": {
            "carbon_footprint": 200.0,
            "energy_consumption": 3000,
            "waste_reduction": 20.0,
            "renewable_energy_percentage": 90.0
        },
        "certification": {
            "carbon_footprint": 300.0,
            "energy_consumption": 4000,
            "waste_reduction": 25.0,
            "renewable_energy_percentage": 95.0
        },
        "proof_of_impact": {
            "carbon_footprint": 500.0,
            "energy_consumption": 5000,
            "waste_reduction": 30.0,
            "renewable_energy_percentage": 100.0
        }
    }
    
    metrics = mock_metrics.get(document_type, mock_metrics["sustainability_document"])
    
    # Calculate credits using mock data
    credit_calculation = calculate_carbon_credits(
        carbon_footprint=metrics["carbon_footprint"],
        energy_consumption=metrics["energy_consumption"],
        waste_reduction=metrics["waste_reduction"],
        renewable_energy_percentage=metrics["renewable_energy_percentage"],
        document_type=document_type
    )
    
    return {
        "should_mint": credit_calculation['should_mint'],
        "token_amount": credit_calculation['token_amount'],
        "carbon_footprint": metrics["carbon_footprint"],
        "reasoning": f"Mock analysis: {credit_calculation['reasoning']}",
        "impact_score": credit_calculation['impact_score']
    }


# Run the agent
if __name__ == "__main__":
    reasoner_agent.run()
