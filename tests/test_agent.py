"""
Unit and integration tests for the Gemini 3.8 Flash Hotel Voice Receptionist API.
"""

import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from agent import HotelReceptionistAgent, SYSTEM_PROMPT
from main import app

client = TestClient(app)


class TestPromptAndModel:
    """Verifies system prompt content and model configuration."""

    def test_system_prompt_hotel_knowledge(self):
        assert "Grand Azure Hotel & Suites" in SYSTEM_PROMPT
        assert "Standard King Room" in SYSTEM_PROMPT
        assert "$140" in SYSTEM_PROMPT
        assert "Deluxe Queen Suite" in SYSTEM_PROMPT
        assert "$190" in SYSTEM_PROMPT
        assert "John Doe" in SYSTEM_PROMPT
        assert "HTL-1024" in SYSTEM_PROMPT
        assert "GrandAzure_Guest" in SYSTEM_PROMPT
        assert "AzureStay2026" in SYSTEM_PROMPT

    def test_default_model_is_gemini_3_8_flash(self):
        agent = HotelReceptionistAgent()
        assert agent.model == "gemini-3.8-flash"


class TestAgentResponseLogic:
    """Verifies agent chat behavior."""

    def test_empty_message_returns_greeting(self):
        agent = HotelReceptionistAgent(api_key=None)
        res = agent.respond("")
        assert res["status"] == "success"
        assert "Alex" in res["reply"]
        assert "Grand Azure" in res["reply"]

    def test_missing_api_key(self):
        agent = HotelReceptionistAgent(api_key="")
        agent.client = None
        res = agent.respond("Hello!")
        assert res["status"] == "error"
        assert res.get("error") == "MISSING_API_KEY"

    def test_successful_gemini_response(self):
        agent = HotelReceptionistAgent(api_key="test-key")
        mock_response = MagicMock()
        mock_response.text = "Hello! We have Deluxe Queen Suites available for $190 per night."
        
        agent.client = MagicMock()
        agent.client.models.generate_content.return_value = mock_response

        res = agent.respond("Do you have rooms?", session_id="test-sess")
        assert res["status"] == "success"
        assert "Deluxe Queen" in res["reply"]
        assert res["model"] == "gemini-3.8-flash"
        assert res["session_id"] == "test-sess"


class TestApiEndpoints:
    """Verifies FastAPI HTTP endpoints."""

    def test_root_endpoint_returns_json_info(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["model"] == "gemini-3.8-flash"
        assert data["endpoint"] == "POST /chat"
        assert "sample_request_json" in data
        assert "message" in data["sample_request_json"]

    def test_chat_endpoint_validates_request(self):
        response = client.post("/chat", json={"message": ""})
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "model" in data

    def test_api_chat_alias_endpoint(self):
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 200
        assert "reply" in response.json()

    def test_reset_session_endpoint(self):
        response = client.post("/reset", json={"session_id": "test-session-1"})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
