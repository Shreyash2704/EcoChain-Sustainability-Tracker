from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from uagents import Bureau
from agents.user_agent import user_agent
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_with_agent(message: dict = Body(...)):
    text = message.get("text", "")
    print(f"Received from frontend: {text}")
    # For Sprint 1, just echo a mock response
    return {"response": f"Agent received: {text}"}


async def start_bureau():
    bureau = Bureau(port=8001)  # run agent separately
    bureau.add(user_agent)
    await bureau.run_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bureau())  # start agent
    import uvicorn
    uvicorn.run(app, host="localhost", port=8002)
