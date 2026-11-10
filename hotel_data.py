"""
Dummy Hotel Database and Management Operations for Grand Azure Hotel & Suites.
Provides in-memory state and helper functions for front desk operations.
"""

from datetime import datetime, date, timedelta
import random
from typing import Dict, List, Optional, Any


class HotelDatabase:
    """In-memory database storing hotel rooms, bookings, amenities, and service requests."""

    def __init__(self):
        self.reset_data()

    def reset_data(self):
        """Initializes or resets dummy data to default state."""
        self.hotel_info = {
            "name": "Grand Azure Hotel & Suites",
            "rating": "5-Star Luxury Resort",
            "phone": "+1 (800) 555-AZURE",
            "address": "777 Coastal Promenade, Palm Bay, CA 90210",
            "check_in_time": "3:00 PM",
            "check_out_time": "11:00 AM",
        }

        self.room_types = {
            "standard king": {
                "name": "Standard King Room",
                "price_per_night": 140,
                "capacity": 2,
                "description": "Comfortable king bed, city skyline view, work desk, 55-inch smart TV, marble shower.",
                "total_inventory": 20,
                "available": 6,
            },
            "deluxe queen": {
                "name": "Deluxe Queen Suite",
                "price_per_night": 190,
                "capacity": 4,
                "description": "Two plush queen beds, private balcony, seating area, complimentary mini-bar, soaking tub.",
                "total_inventory": 15,
                "available": 4,
            },
            "ocean view suite": {
                "name": "Ocean View Executive Suite",
                "price_per_night": 290,
                "capacity": 3,
                "description": "Panoramic ocean view, king bed, separate living salon, Jacuzzi bath, Nespresso machine.",
                "total_inventory": 10,
                "available": 2,
            },
            "presidential suite": {
                "name": "Presidential Penthouse Suite",
                "price_per_night": 590,
                "capacity": 4,
                "description": "Top floor, wrap-around terrace, private elevator access, butler service, grand piano, dining for 6.",
                "total_inventory": 2,
                "available": 1,
            },
        }

        today_str = date.today().isoformat()
        tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
        in_three_days = (date.today() + timedelta(days=3)).isoformat()

        self.reservations: Dict[str, Dict[str, Any]] = {
            "HTL-1024": {
                "confirmation_code": "HTL-1024",
                "guest_name": "John Doe",
                "room_type": "Deluxe Queen Suite",
                "room_number": "402",
                "check_in": today_str,
                "check_out": in_three_days,
                "status": "Checked-In",
                "guests": 2,
                "special_requests": "Extra feather pillows, quiet floor",
            },
            "HTL-2048": {
                "confirmation_code": "HTL-2048",
                "guest_name": "Sarah Connor",
                "room_type": "Ocean View Executive Suite",
                "room_number": "710",
                "check_in": tomorrow_str,
                "check_out": (date.today() + timedelta(days=4)).isoformat(),
                "status": "Confirmed",
                "guests": 1,
                "special_requests": "Late arrival (around 8:00 PM)",
            },
            "HTL-3072": {
                "confirmation_code": "HTL-3072",
                "guest_name": "Michael Scott",
                "room_type": "Standard King Room",
                "room_number": "305",
                "check_in": (date.today() - timedelta(days=2)).isoformat(),
                "check_out": today_str,
                "status": "Checked-In",
                "guests": 1,
                "special_requests": "Late check-out requested (1:00 PM)",
            },
        }

        self.amenities = {
            "wifi": {
                "name": "High-Speed Wi-Fi",
                "details": "Complimentary ultra-fast Wi-Fi throughout the hotel. Network: 'GrandAzure_Guest', Password: 'AzureStay2026'. Premium streaming speeds included.",
            },
            "breakfast": {
                "name": "Breakfast Buffet",
                "details": "Served daily from 6:30 AM to 10:30 AM at the Garden Terrace on Level 1. Features fresh pastries, artisanal omelet station, tropical fruits, and specialty coffees. Complimentary for all registered guests.",
            },
            "pool": {
                "name": "Heated Infinity Pool & Sun Deck",
                "details": "Located on the 4th floor terrace. Open daily from 7:00 AM to 10:00 PM. Cabanas and towel service are complimentary. Poolside refreshments available from 11:00 AM.",
            },
            "gym": {
                "name": "24/7 Wellness & Fitness Center",
                "details": "Located on the 3rd floor. Equipped with Peloton bikes, Technogym equipment, free weights, and yoga mats. Accessible 24/7 with your room keycard.",
            },
            "spa": {
                "name": "The Azure Serenity Spa",
                "details": "Full-service luxury spa on the 4th floor. Open from 9:00 AM to 8:00 PM. Offering hot stone massages, facial rejuvenation, and hydrotherapy. Bookings recommended 24 hours in advance.",
            },
            "dining": {
                "name": "Restaurants & Bars",
                "details": "1) 'Azure Bistro' (Mediterranean & fresh seafood, open 12:00 PM – 11:00 PM). 2) 'Skyline Rooftop Bar & Lounge' (Signature craft cocktails & small plates, open 5:00 PM – 1:00 AM). 3) 24-hour in-room dining.",
            },
            "parking": {
                "name": "Parking & Valet",
                "details": "Complimentary secure underground self-parking for all guests. Valet service is available 24/7 at the front entrance for $25/day (gratis for Penthouse guests). EV charging stations are available on level P2.",
            },
            "checkout_policy": {
                "name": "Check-in & Check-out Times",
                "details": "Standard check-in is 3:00 PM. Standard check-out is 11:00 AM. Complimentary luggage storage is available at the bell desk. Late checkout up to 2:00 PM can be requested subject to availability.",
            },
            "shuttle": {
                "name": "Airport & Local Shuttle",
                "details": "Complimentary Mercedes shuttle runs between the hotel and the International Airport every hour on the hour between 6:00 AM and 11:00 PM. Contact the bell desk to reserve a seat.",
            },
        }

        self.service_requests: List[Dict[str, Any]] = [
            {
                "id": "REQ-101",
                "room_number": "402",
                "guest_name": "John Doe",
                "service_type": "Housekeeping",
                "details": "Extra bath towels and bathrobes",
                "status": "In Progress",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        ]

    def get_room_types(self) -> Dict[str, Any]:
        """Returns all room types and pricing."""
        return self.room_types

    def check_availability(self, room_type_query: Optional[str] = None, nights: int = 1) -> Dict[str, Any]:
        """Check room availability for a given room category or all categories."""
        if room_type_query:
            query_lower = room_type_query.strip().lower()
            matching_key = None
            for key in self.room_types:
                if key in query_lower or query_lower in key:
                    matching_key = key
                    break

            if matching_key:
                room = self.room_types[matching_key]
                return {
                    "matched": True,
                    "room_key": matching_key,
                    "name": room["name"],
                    "available_rooms": room["available"],
                    "price_per_night": room["price_per_night"],
                    "total_estimate": room["price_per_night"] * max(1, nights),
                    "capacity": room["capacity"],
                    "description": room["description"],
                    "status": "Available" if room["available"] > 0 else "Sold Out",
                }

        # Otherwise return summary of all rooms
        summary = []
        for key, r in self.room_types.items():
            summary.append({
                "type": r["name"],
                "available": r["available"],
                "price_per_night": r["price_per_night"],
                "capacity": r["capacity"],
                "description": r["description"],
            })
        return {
            "matched": False,
            "rooms": summary,
            "total_available": sum(r["available"] for r in self.room_types.values()),
        }

    def book_room(
        self,
        guest_name: str,
        room_type: str,
        check_in_date: Optional[str] = None,
        nights: int = 1,
        guests: int = 1,
        special_requests: str = "",
    ) -> Dict[str, Any]:
        """Books a room with dummy data confirmation code."""
        if not guest_name or not guest_name.strip():
            return {"success": False, "error": "Guest name is required for booking."}

        # Resolve room type
        query_lower = (room_type or "").lower().strip()
        matched_key = None
        for key in self.room_types:
            if key in query_lower or query_lower in key or any(w in query_lower for w in key.split()):
                matched_key = key
                break
        
        if not matched_key:
            # Default to standard king if ambiguous
            matched_key = "standard king"

        room = self.room_types[matched_key]
        if room["available"] <= 0:
            return {
                "success": False,
                "error": f"Sorry, {room['name']} is completely booked for the requested dates.",
            }

        # Decrement availability
        room["available"] -= 1

        confirmation_code = f"HTL-{random.randint(4000, 9999)}"
        assigned_room = f"{random.randint(2, 8)}0{random.randint(1, 9)}"

        if not check_in_date:
            check_in_date = date.today().isoformat()
        
        try:
            ci_date = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            co_date = (ci_date + timedelta(days=max(1, int(nights)))).isoformat()
        except Exception:
            co_date = (date.today() + timedelta(days=max(1, int(nights)))).isoformat()

        total_price = room["price_per_night"] * max(1, int(nights))

        reservation = {
            "confirmation_code": confirmation_code,
            "guest_name": guest_name.strip(),
            "room_type": room["name"],
            "room_number": assigned_room,
            "check_in": check_in_date,
            "check_out": co_date,
            "nights": max(1, int(nights)),
            "guests": max(1, int(guests)),
            "total_price": total_price,
            "status": "Confirmed",
            "special_requests": special_requests or "None",
        }

        self.reservations[confirmation_code] = reservation
        return {
            "success": True,
            "booking": reservation,
            "message": f"Reservation successfully confirmed for {guest_name}. Confirmation code: {confirmation_code}. Room: {room['name']} (assigned room #{assigned_room}). Total: ${total_price}.",
        }

    def lookup_reservation(self, query: str) -> Dict[str, Any]:
        """Looks up a reservation by confirmation code or guest name."""
        if not query:
            return {"found": False, "message": "Please provide a guest name or reservation code."}

        clean_query = query.strip().upper()
        # Direct code match
        if clean_query in self.reservations:
            return {"found": True, "reservation": self.reservations[clean_query]}

        # Name match
        query_lower = query.strip().lower()
        for res in self.reservations.values():
            if query_lower in res["guest_name"].lower():
                return {"found": True, "reservation": res}

        return {
            "found": False,
            "message": f"No reservation found matching '{query}'. Please verify the name or confirmation code.",
        }

    def request_service(
        self,
        room_number: str,
        service_type: str,
        details: str,
        guest_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Logs a room service, housekeeping, or front desk request."""
        req_id = f"REQ-{random.randint(200, 999)}"
        new_request = {
            "id": req_id,
            "room_number": room_number.strip() if room_number else "Front Desk",
            "guest_name": guest_name or "Hotel Guest",
            "service_type": service_type.strip() if service_type else "General Guest Request",
            "details": details.strip() if details else "Assistance requested",
            "status": "Received & Dispatched",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.service_requests.append(new_request)
        return {
            "success": True,
            "request_id": req_id,
            "message": f"Your request for {new_request['service_type']} (Room {new_request['room_number']}) has been dispatched to our staff. Reference #{req_id}.",
            "request": new_request,
        }

    def get_amenity_info(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Provides information on hotel amenities, policies, and hours."""
        if not topic:
            return {
                "hotel": self.hotel_info["name"],
                "amenities": [v["name"] for v in self.amenities.values()],
            }

        topic_clean = topic.strip().lower()
        for key, val in self.amenities.items():
            if key in topic_clean or topic_clean in key or any(w in topic_clean for w in val["name"].lower().split()):
                return {"found": True, "name": val["name"], "details": val["details"]}

        # General summary if not a specific keyword
        return {
            "found": False,
            "message": "We offer complimentary high-speed Wi-Fi, daily breakfast buffet, 24/7 fitness center, heated 4th-floor infinity pool, full-service spa, valet parking, and 24/7 dining.",
            "available_topics": list(self.amenities.keys()),
        }


# Global database instance
db = HotelDatabase()
