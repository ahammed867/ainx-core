from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ainx.router import AINXRouterAgent
from ainx.protocol import AINXMessage

# Create FastAPI app
app = FastAPI()

# ✅ Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input model
class MessageInput(BaseModel):
    raw: str

# Initialize router agent
router = AINXRouterAgent(name="router")

# Define POST endpoint for message handling
@app.post("/message")
async def handle_message(message_input: MessageInput):
    ainx_msg = AINXMessage(message_input.raw)
    response = router.receive(ainx_msg)
    return {"response": response.raw}
