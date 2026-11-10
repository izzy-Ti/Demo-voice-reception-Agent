# 🛎️ Grand Azure Hotel — AI Voice Receptionist API

A lightweight Hotel Voice Receptionist API powered directly by **Google Gemini 3.8 Flash** (`gemini-3.8-flash`) and **FastAPI**.

---

## ⚡ Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your Gemini API key and model are set inside `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=8000
```

### 3. Run the API Server
```bash
python main.py
```
*(Runs on **http://localhost:8000**)*

---

## 📡 API Testing & JSON Request

### Endpoint: `POST /chat` (or `POST /api/chat`)

#### Request Headers:
`Content-Type: application/json`

#### Request JSON Payload:
```json
{
  "message": "Do you have any rooms available tonight? What are the rates?",
  "session_id": "my-session-1"
}
```

#### Successful Response JSON:
```json
{
  "reply": "Welcome to Grand Azure Hotel & Suites! Yes, we have rooms available tonight. Our Standard King is $140 per night, the Deluxe Queen Suite is $190, our Ocean View Suite is $290, and the Presidential Penthouse is $590. Would you like me to book one for you?",
  "session_id": "my-session-1",
  "model": "gemini-3.8-flash",
  "status": "success"
}
```

---

## 💻 Sample Test Commands

### Using cURL:
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the Wi-Fi network and password?"}'
```

### Using PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -ContentType "application/json" -Body '{"message":"Can you look up the reservation for John Doe?"}'
```

### Checking API Status:
Open your browser or run:
```bash
curl http://localhost:8000/
```

---

## 🏨 Hotel Reception Capabilities & Prompts

| Topic | Sample Request JSON `message` |
| :--- | :--- |
| **Room Rates** | `"Do you have any rooms available tonight? What are the prices?"` |
| **Wi-Fi Details** | `"What is the Wi-Fi network and password?"` |
| **Breakfast Hours** | `"What time is breakfast served and where is it located?"` |
| **Reservation Lookup** | `"Can you look up the reservation for John Doe?"` |
| **Housekeeping** | `"Can you please send extra towels to room 402?"` |
| **Room Booking** | `"Please book a Deluxe Queen Suite for 2 nights for Alex Smith"` |
| **Check-out Time** | `"What time is check-out tomorrow?"` |
| **Amenities** | `"Where is the pool and gym located?"` |

---

## 🧪 Running Automated Tests

```bash
python -m pytest
```

---

## 📄 License
MIT License
