from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent

# Create the notification agent
notification_agent = Agent(
    name="EcoChain NotificationAgent",
    seed="eco_notification_agent_seed",
    port=8005
)

# Handle notification requests
@notification_agent.on_message(model=ChatMessage)
async def handle_notification_request(ctx: Context, sender: str, msg: ChatMessage):
    notification_data = msg.content.text
    print(f"Notification request from {sender}: {notification_data}")
    
    # TODO: Implement notification logic
    # This could include:
    # - Sending sustainability milestone alerts
    # - Notifying about carbon credit opportunities
    # - Alerting about environmental impact thresholds
    # - Sending achievement notifications

    
    
    
    response = ChatMessage(
        content=TextContent(
            text=f"Notification sent for: {notification_data}. Status: Delivered 📧"
        )
    )
    await ctx.send(sender, response)

# Run the agent
if __name__ == "__main__":
    notification_agent.run()
