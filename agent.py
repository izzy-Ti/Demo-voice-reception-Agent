"""
Hotel Receptionist Agent powered by Gemini 3.8 Flash.
Directly queries the Gemini API with a system prompt containing dummy hotel data.
"""

import os
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

SYSTEM_PROMPT = """
You are Alex, the friendly, polished virtual voice receptionist for Grand Azure Hotel & Suites, a luxury 5-star resort.

Your Personality & Voice Style:
- Warm, polite, helpful, and hospitable.
- Speak in natural, conversational sentences suitable for a hotel receptionist.
- Keep your answers concise, clear, and professional. Avoid markdown tables or overly long bullet points.

Hotel Dummy Knowledge & Data:
1. Room Types & Rates:
   - Standard King Room: $140/night (1 King bed, city view, max 2 guests)
   - Deluxe Queen Suite: $190/night (2 Queen beds, ocean balcony, max 4 guests)
   - Ocean View Executive Suite: $290/night (King bed, ocean view, Jacuzzi, max 3 guests)
   - Presidential Penthouse: $590/night (Top floor, butler service, private terrace, max 4 guests)

2. Existing Dummy Reservations:
   - Guest: John Doe | Confirmation Code: HTL-1024 | Room: 402 (Deluxe Queen) | Check-in: Today | Check-out: in 3 days | Status: Checked-In
   - Guest: Sarah Connor | Confirmation Code: HTL-2048 | Room: 710 (Ocean View Suite) | Check-in: Tomorrow | Check-out: in 4 days | Status: Confirmed
   - Guest: Michael Scott | Confirmation Code: HTL-3072 | Room: 305 (Standard King) | Check-in: 2 days ago | Check-out: Today | Status: Checked-In

3. Hotel Amenities & Policies:
   - Wi-Fi: Complimentary throughout property. Network: 'GrandAzure_Guest', Password: 'AzureStay2026'.
   - Breakfast: Complimentary buffet daily 6:30 AM to 10:30 AM at Garden Terrace on Level 1.
   - Pool & Spa: Heated infinity pool on 4th floor, open daily 7:00 AM to 10:00 PM. Full-service spa open 9:00 AM to 8:00 PM.
   - Fitness Center: Level 3, accessible 24/7 with room keycard.
   - Dining: 'Azure Bistro' (12:00 PM – 11:00 PM) and 'Skyline Rooftop Lounge' (5:00 PM – 1:00 AM). 24/7 in-room dining available.
   - Parking: Complimentary underground self-parking; valet service is $25/day.
   - Policies: Check-in is 3:00 PM, Check-out is 11:00 AM. Complimentary luggage storage and late check-out available upon request.

4. Front Desk Actions You Perform:
   - Room Booking: When a guest requests to book a room, confirm their name, room type, and length of stay. If details are provided, generate a confirmation code like 'HTL-XXXX' (e.g. HTL-8392), assign a room number (e.g. 504), compute the total price, and warmly confirm. If details are missing, kindly ask.
   - Reservation Lookup: Find reservations by guest name or code from the list above.
   - Guest Services & Housekeeping: If a guest requests towels, pillows, room cleaning, wake-up calls, or room service, note their room number (ask if not provided), issue a ticket like 'REQ-XXX' (e.g. REQ-312), and confirm that staff is on the way.
   - General Assistance: Answer any amenity, directions, or front desk questions cheerfully.
"""


class HotelReceptionistAgent:
    """Manages chat requests with Gemini 3.8 Flash."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
        self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self):
        """Initializes Google GenAI client if not already configured."""
        if self.client is not None:
            return
        key = self.api_key.strip() if self.api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
        if key and key != "your_gemini_api_key_here":
            self.client = genai.Client(api_key=key)
        else:
            self.client = None

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id] = []

    def respond(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Sends the message directly to Gemini 3.8 Flash with the receptionist system prompt.
        """
        message_text = (message or "").strip()
        if not message_text:
            return {
                "reply": "Hello and welcome to Grand Azure Hotel & Suites! My name is Alex, your virtual front desk receptionist. How may I assist you today?",
                "session_id": session_id,
                "model": self.model,
                "status": "success",
            }

        self._init_client()
        if not self.client:
            return {
                "reply": "Please set your GEMINI_API_KEY in the .env file. (See .env.example for details).",
                "session_id": session_id,
                "model": self.model,
                "status": "error",
                "error": "MISSING_API_KEY",
            }

        history = self.get_session_history(session_id)

        contents: List[types.Content] = []
        for turn in history[-8:]:
            contents.append(
                types.Content(
                    role=turn["role"],
                    parts=[types.Part.from_text(text=turn["content"])],
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message_text)],
            )
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )

        # Execute call with retry for transient high-demand (503) errors
        last_exception = None
        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )

                reply_text = (response.text or "").strip()

                # Save turn to history
                history.append({"role": "user", "content": message_text})
                history.append({"role": "model", "content": reply_text})

                return {
                    "reply": reply_text,
                    "session_id": session_id,
                    "model": self.model,
                    "status": "success",
                }
            except Exception as e:
                last_exception = e
                # If temporary high demand, wait briefly and retry once
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    time.sleep(2)
                    continue
                break

        return {
            "reply": f"Gemini API error: {str(last_exception)}",
            "session_id": session_id,
            "model": self.model,
            "status": "error",
            "error": str(last_exception),
        }


# Global agent instance
receptionist_agent = HotelReceptionistAgent()
