# 🛎️ Demo Hotel Voice Receptionist Agent

A simple demo test agent for a hotel voice receptionist powered by **Google Gemini** (`gemini-3.8-flash`) and **FastAPI**.

The agent acts as **Alex**, a virtual front desk receptionist for the fictional *Grand Azure Hotel & Suites*, answering inquiries about room availability, reservations, dummy bookings, amenities (Wi-Fi, breakfast, pool), and housekeeping requests.

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment (`.env`)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Add your Gemini API key inside `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
```

### 3. Start the server
```bash
python main.py
```
*(Server runs on `http://localhost:8000`)*

---

## 📡 How to Test the API

Send a `POST` request to `http://localhost:8000/chat`:

### Request JSON:
```json
{
  "message": "Do you have any rooms available tonight? What are the prices?",
  "session_id": "demo-1"
}
```

### Response JSON:
```json
{
  "reply": "Welcome to Grand Azure Hotel & Suites! Yes, we have Standard King Rooms for $140/night, Deluxe Queen Suites for $190/night, Ocean View Suites for $290/night, and our Presidential Penthouse for $590/night. How may I assist you with a reservation?",
  "session_id": "demo-1",
  "model": "gemini-3.8-flash",
  "status": "success"
}
```

### Quick cURL Test:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the Wi-Fi password?"}'
```

### Quick PowerShell Test:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body '{"message":"What time is breakfast served?"}'
```

---

## 🏨 Example Questions to Ask
- *"Do you have any rooms available tonight?"*
- *"What is the Wi-Fi network and password?"*
- *"Can you look up the reservation for John Doe?"*
- *"Can you please send extra towels to room 402?"*
- *"What time is check-in and check-out?"*
- *"Please book a Deluxe Queen Suite for 2 nights for Alex Smith"*

---

## 🧪 Tests
```bash
python -m pytest
```

---

## 📄 License
MIT
