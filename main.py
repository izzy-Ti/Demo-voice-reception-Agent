"""
FastAPI application for the Hotel Voice Receptionist Agent.
Provides REST API endpoints and serves the voice-enabled frontend interface.
"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from hotel_data import db
from agent import receptionist_agent

app = FastAPI(
    title="Grand Azure Voice Receptionist Agent",
    description="Lightweight Hotel Voice Receptionist Agent powered by Gemini & Dummy Hotel System",
    version="1.0.0",
)

# Enable CORS for cross-origin or local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's voice-transcribed or typed message")
    session_id: Optional[str] = Field("default", description="Conversation session identifier")


class ChatResponse(BaseModel):
    reply: str
    actions: list
    engine: str
    session_id: str


@app.get("/")
def read_root():
    """Serves the main Voice Receptionist HTML interface."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        content={
            "status": "online",
            "message": "Grand Azure Hotel Voice Receptionist API is running. UI file missing.",
        }
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Processes a guest voice/text message through the Receptionist Agent (Gemini / Dummy fallback).
    """
    try:
        session_id = req.session_id or "default"
        res = receptionist_agent.respond(message=req.message, session_id=session_id)
        return ChatResponse(
            reply=res["reply"],
            actions=res.get("actions", []),
            engine=res.get("engine", "dummy"),
            session_id=session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hotel/status")
def hotel_status():
    """Returns real-time hotel dummy state: available rooms, bookings, and active requests."""
    return {
        "hotel": db.hotel_info,
        "rooms": db.room_types,
        "reservations": list(db.reservations.values()),
        "service_requests": db.service_requests,
        "active_gemini": receptionist_agent.client is not None,
        "model": receptionist_agent.model,
    }


@app.post("/api/hotel/reset")
def reset_database():
    """Resets the dummy hotel database to initial values."""
    db.reset_data()
    return {"status": "success", "message": "Dummy database reset to default state."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Grand Azure Voice Receptionist Agent on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
