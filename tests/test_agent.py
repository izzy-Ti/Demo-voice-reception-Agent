"""
Unit and integration tests for the Grand Azure Hotel Voice Receptionist Agent.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from hotel_data import HotelDatabase, db
from agent import HotelReceptionistAgent, receptionist_agent
from main import app

client = TestClient(app)


class TestHotelDatabase:
    """Tests for dummy hotel database operations."""

    def setup_method(self):
        db.reset_data()

    def test_initial_rooms_available(self):
        summary = db.check_availability()
        assert summary["total_available"] > 0
        assert len(summary["rooms"]) == 4

    def test_check_specific_room_availability(self):
        result = db.check_availability(room_type_query="deluxe queen")
        assert result["matched"] is True
        assert result["name"] == "Deluxe Queen Suite"
        assert result["price_per_night"] == 190
        assert result["available_rooms"] > 0

    def test_book_room_success(self):
        initial_avail = db.room_types["deluxe queen"]["available"]
        res = db.book_room(
            guest_name="Alice Walker",
            room_type="deluxe queen",
            nights=3,
            guests=2,
        )
        assert res["success"] is True
        assert "booking" in res
        code = res["booking"]["confirmation_code"]
        assert code.startswith("HTL-")
        assert res["booking"]["nights"] == 3
        assert res["booking"]["total_price"] == 190 * 3
        # Ensure inventory decremented
        assert db.room_types["deluxe queen"]["available"] == initial_avail - 1

    def test_book_room_missing_name(self):
        res = db.book_room(guest_name="", room_type="standard king")
        assert res["success"] is False
        assert "Guest name is required" in res["error"]

    def test_lookup_reservation_by_code(self):
        res = db.lookup_reservation("HTL-1024")
        assert res["found"] is True
        assert res["reservation"]["guest_name"] == "John Doe"
        assert res["reservation"]["room_number"] == "402"

    def test_lookup_reservation_by_name(self):
        res = db.lookup_reservation("John Doe")
        assert res["found"] is True
        assert res["reservation"]["confirmation_code"] == "HTL-1024"

    def test_lookup_reservation_not_found(self):
        res = db.lookup_reservation("Unknown Guest 999")
        assert res["found"] is False

    def test_request_service(self):
        req = db.request_service(
            room_number="402",
            service_type="Housekeeping",
            details="Extra shampoo and slippers",
            guest_name="John Doe",
        )
        assert req["success"] is True
        assert req["request_id"].startswith("REQ-")
        assert req["request"]["room_number"] == "402"
        assert req["request"]["service_type"] == "Housekeeping"
        assert len(db.service_requests) >= 2

    def test_amenities_lookup(self):
        wifi = db.get_amenity_info("wifi")
        assert wifi["found"] is True
        assert "GrandAzure_Guest" in wifi["details"]
        assert "AzureStay2026" in wifi["details"]

        bf = db.get_amenity_info("breakfast")
        assert bf["found"] is True
        assert "Garden Terrace" in bf["details"]


class TestReceptionistAgent:
    """Tests for conversational agent responses and tool triggers."""

    def setup_method(self):
        db.reset_data()
        self.agent = HotelReceptionistAgent(api_key=None)

    def test_greeting(self):
        res = self.agent.respond("Hello there!")
        assert "Alex" in res["reply"]
        assert "Grand Azure" in res["reply"]

    def test_wifi_inquiry(self):
        res = self.agent.respond("What is the wifi password?")
        assert "GrandAzure_Guest" in res["reply"]
        assert "AzureStay2026" in res["reply"]
        assert any(a["tool"] == "get_hotel_amenity_info" for a in res["actions"])

    def test_breakfast_inquiry(self):
        res = self.agent.respond("What time is breakfast served?")
        assert "6:30 AM" in res["reply"] or "Garden Terrace" in res["reply"]

    def test_service_request_extra_towels(self):
        res = self.agent.respond("Can you please send extra towels to room 502?")
        assert "Room 502" in res["reply"]
        assert any(a["tool"] == "request_hotel_service" for a in res["actions"])

    def test_lookup_booking_conversation(self):
        res = self.agent.respond("Can you look up the reservation for John Doe?")
        assert "HTL-1024" in res["reply"] or "John Doe" in res["reply"]
        assert any(a["tool"] == "lookup_reservation" for a in res["actions"])

    def test_book_room_conversation(self):
        res = self.agent.respond("Please book a Deluxe Queen room for 2 nights for Alex Smith")
        assert "HTL-" in res["reply"]
        assert "Deluxe Queen" in res["reply"]
        assert any(a["tool"] == "book_room" for a in res["actions"])


class TestFastAPIRoutes:
    """Tests for HTTP endpoints."""

    def setup_method(self):
        db.reset_data()

    def test_get_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_api_chat_endpoint(self):
        payload = {"message": "What is the check out time?", "session_id": "test-session-1"}
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "actions" in data
        assert data["session_id"] == "test-session-1"

    def test_hotel_status_endpoint(self):
        response = client.get("/api/hotel/status")
        assert response.status_code == 200
        data = response.json()
        assert "rooms" in data
        assert "reservations" in data
        assert "service_requests" in data
        assert len(data["reservations"]) >= 3

    def test_hotel_reset_endpoint(self):
        # Book a room
        client.post("/api/chat", json={"message": "Book a room for Test Guest"})
        # Reset
        response = client.post("/api/hotel/reset")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
