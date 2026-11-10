"""
Lightweight FastAPI application for the Hotel Voice Receptionist Agent.
Handles voice/text chat requests by forwarding them to Gemini API.
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import receptionist_agent

app = FastAPI(
    title="Hotel Voice Receptionist Agent",
    description="Lightweight Hotel Voice Receptionist powered directly by Gemini API",
    version="1.0.0",
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User voice transcript or typed text")
    session_id: Optional[str] = Field("default", description="Conversation session ID")


@app.get("/")
def read_root():
    """Serves the voice receptionist web UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(content={"status": "online", "message": "Voice Receptionist API is ready."})


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    """Sends guest message to the Gemini Receptionist Agent."""
    try:
        session_id = req.session_id or "default"
        res = receptionist_agent.respond(message=req.message, session_id=session_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
def status_endpoint():
    """Returns agent configuration status."""
    has_key = bool(os.getenv("GEMINI_API_KEY", "").strip() and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here")
    return {
        "status": "online",
        "has_api_key": has_key,
        "model": receptionist_agent.model,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Hotel Voice Receptionist on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
