"""
Unit and integration tests for the Gemini Hotel Voice Receptionist Agent.
"""

import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from agent import HotelReceptionistAgent, SYSTEM_PROMPT
from main import app

client = TestClient(app)


class TestSystemPrompt:
    """Verifies that the system prompt contains all necessary dummy hotel data."""

    def test_system_prompt_contains_rooms(self):
        assert "Standard King Room" in SYSTEM_PROMPT
        assert "$140" in SYSTEM_PROMPT
        assert "Deluxe Queen Suite" in SYSTEM_PROMPT
        assert "$190" in SYSTEM_PROMPT
        assert "Ocean View Executive Suite" in SYSTEM_PROMPT
        assert "Presidential Penthouse" in SYSTEM_PROMPT

    def test_system_prompt_contains_dummy_bookings(self):
        assert "John Doe" in SYSTEM_PROMPT
        assert "HTL-1024" in SYSTEM_PROMPT
        assert "Sarah Connor" in SYSTEM_PROMPT
        assert "HTL-2048" in SYSTEM_PROMPT
        assert "Michael Scott" in SYSTEM_PROMPT

    def test_system_prompt_contains_amenities_and_policies(self):
        assert "GrandAzure_Guest" in SYSTEM_PROMPT
        assert "AzureStay2026" in SYSTEM_PROMPT
        assert "Garden Terrace" in SYSTEM_PROMPT
        assert "6:30 AM" in SYSTEM_PROMPT
        assert "3:00 PM" in SYSTEM_PROMPT
        assert "11:00 AM" in SYSTEM_PROMPT


class TestAgentBehavior:
    """Verifies agent response logic and Gemini API integration."""

    def test_empty_message_returns_greeting(self):
        agent = HotelReceptionistAgent(api_key=None)
        res = agent.respond("")
        assert "Alex" in res["reply"]
        assert "Grand Azure" in res["reply"]

    def test_missing_api_key_returns_guidance(self):
        agent = HotelReceptionistAgent(api_key="")
        res = agent.respond("Hello, do you have rooms?")
        assert "GEMINI_API_KEY" in res["reply"]
        assert res.get("error") == "MISSING_API_KEY"

    def test_gemini_api_call(self):
        agent = HotelReceptionistAgent(api_key="dummy-test-key")
        # Mock the Gemini client models.generate_content
        mock_response = MagicMock()
        mock_response.text = "We have Standard King and Deluxe Queen rooms available tonight starting at $140."
        
        agent.client = MagicMock()
        agent.client.models.generate_content.return_value = mock_response

        res = agent.respond("Do you have rooms available tonight?", session_id="test-session")
        assert "Standard King" in res["reply"]
        assert res["session_id"] == "test-session"
        
        # Verify history is saved
        history = agent.get_session_history("test-session")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "model"


class TestFastAPIRoutes:
    """Verifies FastAPI HTTP endpoints."""

    def test_get_root_page(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_api_status_endpoint(self):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "has_api_key" in data
        assert "model" in data

    def test_api_chat_endpoint(self):
        response = client.post("/api/chat", json={"message": "", "session_id": "test-1"})
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "session_id" in data
