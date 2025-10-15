from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from uagents import Bureau
from agents.user_agent import user_agent
from agents.verifier_agent import verifier_agent
from agents.reasoner_agent import reasoner_agent
import asyncio

# Import API routers
from api.uploads import router as uploads_router

app = FastAPI(
    title="EcoChain Sustainability Tracker",
    description="API for sustainability tracking and verification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(uploads_router)

@app.post("/chat")
async def chat_with_agent(message: dict = Body(...)):
    text = message.get("text", "")
    print(f"Received from frontend: {text}")
    # For Sprint 1, just echo a mock response
    return {"response": f"Agent received: {text}"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": "EcoChain Sustainability Tracker",
        "version": "1.0.0"
    }

async def start_bureau():
    bureau = Bureau(port=8001)  # run agent separately
    bureau.add(user_agent)
    bureau.add(verifier_agent)
    bureau.add(reasoner_agent)
    await bureau.run_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bureau())  # start agent
    import uvicorn
    uvicorn.run(app, host="localhost", port=8002)
