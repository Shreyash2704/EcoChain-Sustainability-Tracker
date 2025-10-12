from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

# Create the reasoner agent
reasoner_agent = Agent(
    name="EcoChain ReasonerAgent",
    seed="eco_reasoner_agent_seed",
    port=8003
)

# Handle reasoning requests
@reasoner_agent.on_message(model=ChatMessage)
async def handle_reasoning_request(ctx: Context, sender: str, msg: ChatMessage):
    reasoning_data = msg.content.text
    print(f"Reasoning request from {sender}: {reasoning_data}")
    
    # TODO: Implement reasoning logic
    # This could include:
    # - Analyzing sustainability patterns
    # - Making recommendations based on data
    # - Calculating environmental impact scores
    # - Generating insights from user behavior
    
    response = ChatMessage(
        content=TextContent(
            text=f"Analysis completed for: {reasoning_data}. Recommendation: Implement green energy solutions 🌱"
        )
    )
    await ctx.send(sender, response)

# Run the agent
if __name__ == "__main__":
    reasoner_agent.run()
