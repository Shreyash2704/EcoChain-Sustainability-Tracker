from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
# Create the agent
user_agent = Agent(
    name="EcoChain UserAgent",
    seed="eco_user_agent_seed",
    port=8001
)

# Handle chat messages
@user_agent.on_message(model=ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    user_text = msg.content.text
    print(f"Message from {sender}: {user_text}")
    response = ChatMessage(content=TextContent(text=f"Hello 👋, you said: {user_text}"))
    await ctx.send(sender, response)

# Run the agent
if __name__ == "__main__":
    user_agent.run()
