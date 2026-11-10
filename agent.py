"""
Hotel Voice Receptionist Agent powered by Gemini with a smart fallback engine.
Handles conversational hotel inquiries, bookings, reservation lookups,
amenities information, and guest service requests.
"""

import os
import re
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from hotel_data import db

load_dotenv()

SYSTEM_INSTRUCTION = """
You are Alex, a warm, polished, and attentive virtual voice receptionist at the 5-star Grand Azure Hotel & Suites.
Your voice is calm, welcoming, and helpful.

Key Guidelines:
1. Speak concisely and conversationally. Your words will be spoken out loud via text-to-speech to the hotel guest. Avoid markdown tables, bullet lists with asterisks, or unpronounceable formatting.
2. Use tools whenever the guest wants to check room availability, book a room, look up a booking, ask about amenities (Wi-Fi, breakfast, pool, gym, etc.), or request guest services (towels, room cleaning, wake-up calls).
3. If booking information is incomplete (e.g. missing guest name or room type), kindly ask the guest for the missing detail.
4. Always maintain a gracious 5-star hospitality tone: greet warmly, confirm details clearly, and thank the guest.
5. Hotel basics: Check-in is 3:00 PM, Check-out is 11:00 AM. Wi-Fi network is 'GrandAzure_Guest', password 'AzureStay2026'. Breakfast is complimentary 6:30 AM to 10:30 AM on Level 1.
"""


# Function definitions for Gemini Tool Calling
def check_room_availability(room_type: str = "", nights: int = 1) -> Dict[str, Any]:
    """Check room availability and pricing at Grand Azure Hotel & Suites."""
    return db.check_availability(room_type_query=room_type, nights=nights)


def book_room(
    guest_name: str,
    room_type: str = "Standard King Room",
    check_in_date: str = "",
    nights: int = 1,
    guests: int = 1,
    special_requests: str = "",
) -> Dict[str, Any]:
    """Book a hotel room for a guest and generate a reservation confirmation code."""
    return db.book_room(
        guest_name=guest_name,
        room_type=room_type,
        check_in_date=check_in_date,
        nights=nights,
        guests=guests,
        special_requests=special_requests,
    )


def lookup_reservation(query: str) -> Dict[str, Any]:
    """Look up an existing hotel reservation by guest name or reservation confirmation code."""
    return db.lookup_reservation(query)


def request_hotel_service(
    room_number: str,
    service_type: str,
    details: str,
    guest_name: str = "Guest",
) -> Dict[str, Any]:
    """Submit a room service, housekeeping, maintenance, or front-desk request for a room."""
    return db.request_service(
        room_number=room_number,
        service_type=service_type,
        details=details,
        guest_name=guest_name,
    )


def get_hotel_amenity_info(topic: str = "") -> Dict[str, Any]:
    """Get information regarding hotel amenities, breakfast, wifi, pool, spa, gym, parking, or check-out times."""
    return db.get_amenity_info(topic)


HOTEL_TOOLS = [
    check_room_availability,
    book_room,
    lookup_reservation,
    request_hotel_service,
    get_hotel_amenity_info,
]


class HotelReceptionistAgent:
    """Manages conversations between hotel guests and the virtual voice receptionist."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = None
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._init_gemini_client()

    def _init_gemini_client(self):
        """Initializes Google GenAI client if API key is provided."""
        if self.api_key and self.api_key.strip():
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key.strip())
            except Exception as e:
                print(f"[Warning] Failed to initialize Gemini Client: {e}. Falling back to rule-based engine.")
                self.client = None
        else:
            self.client = None

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves or creates conversation history for a session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        """Clears conversation history for a session."""
        if session_id in self.sessions:
            self.sessions[session_id] = []

    def respond(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Main entry point to respond to a user message via Gemini or fallback engine."""
        history = self.get_session_history(session_id)
        message_clean = (message or "").strip()

        if not message_clean:
            return {
                "reply": "Good day! Welcome to Grand Azure Hotel & Suites. My name is Alex. How may I assist you today?",
                "actions": [],
                "engine": "dummy",
            }

        # Try Gemini first if client is available
        if self.client:
            try:
                return self._respond_with_gemini(message_clean, history)
            except Exception as err:
                print(f"[Gemini API Notice] Exception occurred: {err}. Using local dummy engine fallback.")

        # Fallback to smart rule-based receptionist dummy agent
        return self._respond_fallback(message_clean, history)

    def _respond_with_gemini(self, message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processes message using Gemini with function calling."""
        from google.genai import types

        actions_taken = []
        
        # Build contents from history
        contents = []
        for turn in history[-6:]:  # Keep recent context
            contents.append(types.Content(
                role=turn["role"],
                parts=[types.Part.from_text(text=turn["content"])]
            ))
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        ))

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=HOTEL_TOOLS,
            temperature=0.7,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        # Check for function/tool calls
        if response.function_calls:
            for call in response.function_calls:
                fn_name = call.name
                fn_args = call.args or {}
                actions_taken.append({"tool": fn_name, "args": fn_args})

                # Execute tool
                result = None
                if fn_name == "check_room_availability":
                    result = check_room_availability(**fn_args)
                elif fn_name == "book_room":
                    result = book_room(**fn_args)
                elif fn_name == "lookup_reservation":
                    result = lookup_reservation(**fn_args)
                elif fn_name == "request_hotel_service":
                    result = request_hotel_service(**fn_args)
                elif fn_name == "get_hotel_amenity_info":
                    result = get_hotel_amenity_info(**fn_args)
                else:
                    result = {"status": "unknown function"}

                # Add function response back to contents and generate final spoken response
                contents.append(response.candidates[0].content)
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(
                        name=fn_name,
                        response={"result": result}
                    )]
                ))

            followup = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            final_reply = followup.text
        else:
            final_reply = response.text

        # Record in history
        history.append({"role": "user", "content": message})
        history.append({"role": "model", "content": final_reply})

        return {
            "reply": final_reply.strip(),
            "actions": actions_taken,
            "engine": "gemini",
        }

    def _respond_fallback(self, message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligent dummy receptionist engine that parses guest requests and executes
        hotel operations without needing an external API key.
        """
        msg_lower = message.lower().strip()
        actions = []
        reply = ""

        # 1. Greeting
        if any(w in msg_lower for w in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]) and len(msg_lower.split()) <= 4:
            reply = "Hello and welcome to Grand Azure Hotel & Suites! My name is Alex, your front desk receptionist. How may I be of service to you today?"

        # 2. Amenities: Wi-Fi
        elif any(w in msg_lower for w in ["wifi", "wi-fi", "internet", "network", "password"]):
            info = get_hotel_amenity_info("wifi")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "wifi"}, "result": info})
            reply = "Our Wi-Fi is complimentary for all guests. Connect to 'GrandAzure_Guest' with password 'AzureStay2026'."

        # 3. Amenities: Breakfast
        elif any(w in msg_lower for w in ["breakfast", "dining", "food", "eat", "buffet", "morning meal"]):
            info = get_hotel_amenity_info("breakfast")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "breakfast"}, "result": info})
            reply = "Complimentary breakfast is served daily from 6:30 AM to 10:30 AM at the Garden Terrace on Level 1. We have a fresh pastry bar, artisan omelet station, and specialty coffees."

        # 4. Amenities: Pool / Gym / Spa / Parking / Checkout Times
        elif any(w in msg_lower for w in ["pool", "swim", "swimming"]):
            info = get_hotel_amenity_info("pool")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "pool"}, "result": info})
            reply = "Our heated infinity pool and sun deck are located on the 4th floor, open daily from 7:00 AM to 10:00 PM with complimentary cabanas and towel service."

        elif any(w in msg_lower for w in ["gym", "fitness", "workout", "exercise"]):
            info = get_hotel_amenity_info("gym")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "gym"}, "result": info})
            reply = "Our wellness and fitness center is on the 3rd floor, fully equipped with Peloton bikes and weights, and open 24 hours a day with your room key."

        elif any(w in msg_lower for w in ["spa", "massage"]):
            info = get_hotel_amenity_info("spa")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "spa"}, "result": info})
            reply = "The Azure Serenity Spa is on the 4th floor, open from 9:00 AM to 8:00 PM offering massages and hydrotherapy."

        elif any(w in msg_lower for w in ["check out time", "checkout time", "check-out time", "check in time", "check-in time", "what time is check out", "what time is checkout"]):
            reply = "Standard check-in begins at 3:00 PM, and check-out is by 11:00 AM. If you require late check-out or luggage storage, I would be delighted to arrange that for you."

        elif any(w in msg_lower for w in ["parking", "valet", "car"]):
            info = get_hotel_amenity_info("parking")
            actions.append({"tool": "get_hotel_amenity_info", "args": {"topic": "parking"}, "result": info})
            reply = "We offer complimentary secure underground self-parking for all guests, as well as 24-hour valet service at the front entrance for $25 per day."

        # 5. Room Service / Housekeeping / Amenities Request
        elif any(w in msg_lower for w in ["towel", "pillows", "blanket", "housekeeping", "clean my room", "wake-up", "wake up", "room service", "luggage", "iron", "water"]):
            # Extract room number if mentioned
            room_match = re.search(r'room\s*(?:number\s*)?#?(\d+)', msg_lower)
            room_num = room_match.group(1) if room_match else "402"
            
            svc_type = "Housekeeping"
            if "wake" in msg_lower:
                svc_type = "Wake-up Call"
            elif "service" in msg_lower or "food" in msg_lower:
                svc_type = "Room Service"
            elif "luggage" in msg_lower:
                svc_type = "Bell Desk / Luggage"

            res = request_hotel_service(room_number=room_num, service_type=svc_type, details=message)
            actions.append({"tool": "request_hotel_service", "args": {"room_number": room_num, "service_type": svc_type, "details": message}, "result": res})
            reply = f"Certainly! I have logged your request for {svc_type} for Room {room_num}. Reference number is {res['request_id']}. Our team is attending to it immediately."

        # 6. Reservation Lookup (John Doe, Michael Scott, Sarah Connor, or HTL-xxxx)
        elif any(w in msg_lower for w in ["lookup", "look up", "reservation", "booking for", "find my booking", "check my reservation", "htl-"]):
            # Extract potential code or name
            code_match = re.search(r'htl-\d+', msg_lower)
            query = code_match.group(0).upper() if code_match else ""
            if not query:
                for name in ["john doe", "sarah connor", "michael scott", "john", "sarah", "michael"]:
                    if name in msg_lower:
                        query = name.title()
                        break
            if not query:
                # Look for name after "for"
                for_match = re.search(r'(?:reservation|booking)\s+(?:for|under)\s+([a-zA-Z\s]+)', msg_lower)
                if for_match:
                    query = for_match.group(1).strip().title()

            if query:
                res = lookup_reservation(query)
                actions.append({"tool": "lookup_reservation", "args": {"query": query}, "result": res})
                if res["found"]:
                    b = res["reservation"]
                    reply = f"I found your reservation, {b['guest_name']}! Confirmation code {b['confirmation_code']} for the {b['room_type']}, room {b['room_number']}. Status is {b['status']} with check-out on {b['check_out']}."
                else:
                    reply = f"I checked our records, but couldn't find an active reservation for '{query}'. Could you please double check the spelling or provide your confirmation code?"
            else:
                reply = "I would be happy to look up your reservation. Could you please provide your confirmation code or the name under which it was booked?"

        # 7. Room Booking
        elif any(w in msg_lower for w in ["book", "reserve", "reservation for a room", "i want a room", "need a room"]):
            # Extract guest name if present
            name_match = re.search(r'(?:name is|for|under)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)', msg_lower)
            guest_name = name_match.group(1).title() if name_match else "Valued Guest"
            
            # Determine room type
            room_type = "standard king"
            if "deluxe" in msg_lower or "queen" in msg_lower:
                room_type = "deluxe queen"
            elif "ocean" in msg_lower or "sea" in msg_lower:
                room_type = "ocean view suite"
            elif "presidential" in msg_lower or "penthouse" in msg_lower:
                room_type = "presidential suite"

            # Determine nights
            night_match = re.search(r'(\d+)\s*(?:night|day)', msg_lower)
            nights = int(night_match.group(1)) if night_match else 2

            res = book_room(guest_name=guest_name, room_type=room_type, nights=nights)
            actions.append({"tool": "book_room", "args": {"guest_name": guest_name, "room_type": room_type, "nights": nights}, "result": res})
            
            if res.get("success"):
                b = res["booking"]
                reply = f"Wonderful news, {guest_name}! I have booked the {b['room_type']} for you for {b['nights']} night(s). Your confirmation code is {b['confirmation_code']} and room #{b['room_number']} is assigned. Total comes to ${b['total_price']}. We look forward to hosting you!"
            else:
                reply = f"I apologize, but we could not complete the reservation: {res.get('error', 'Room unavailable')}. May I suggest an alternative room type?"

        # 8. Room Availability / Pricing Inquiry
        elif any(w in msg_lower for w in ["available", "availability", "rooms", "rates", "how much", "price", "pricing"]):
            avail = check_room_availability()
            actions.append({"tool": "check_room_availability", "args": {}, "result": avail})
            reply = "We currently have rooms available! Our Standard King starts at $140 per night, Deluxe Queen Suite at $190, Ocean View Suite at $290, and our Presidential Suite at $590. Would you like me to book one for you?"

        # 9. Generic / Assistance
        else:
            reply = "Thank you for contacting the Grand Azure front desk. As your virtual receptionist, I can check room availability, book a stay, look up your reservation, arrange extra towels or room service, or provide hotel information such as Wi-Fi and breakfast hours. How may I assist you?"

        # Save to history
        history.append({"role": "user", "content": message})
        history.append({"role": "model", "content": reply})

        return {
            "reply": reply,
            "actions": actions,
            "engine": "dummy_receptionist",
        }


# Global agent instance
receptionist_agent = HotelReceptionistAgent()
