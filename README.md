# 🛎️ Grand Azure Hotel — AI Voice Receptionist Agent

A lightweight virtual hotel voice receptionist agent powered by **Google Gemini API** (`gemini-2.5-flash`) and **FastAPI**, with browser-native Web Speech recognition and voice synthesis.

---

## ✨ Features

- **🧠 Real AI via Gemini API**:
  - Sends user voice and text queries directly to Google Gemini (`gemini-2.5-flash`).
  - System prompt equips Gemini with full dummy hotel knowledge: room inventory, pricing, existing bookings, amenities, policies, and reception procedures.
  - Multi-turn conversational memory per session.
- **🎙️ Real-time Voice Interaction**:
  - Speech-to-Text using browser Web Speech Recognition (`webkitSpeechRecognition`).
  - Text-to-Speech audio response using browser Speech Synthesis.
  - Animated soundwave visualizers and status indicators.
  - Mute/unmute voice toggle and text input fallback.
- **🏨 Realistic Hotel Front-Desk Duties**:
  - **Room Availability & Rates**: Standard King ($140/nt), Deluxe Queen ($190/nt), Ocean View Suite ($290/nt), Presidential Penthouse ($590/nt).
  - **Booking**: Reserves rooms and generates confirmation codes (`HTL-XXXX`).
  - **Reservation Lookup**: Looks up bookings (e.g., John Doe `HTL-1024`, Sarah Connor `HTL-2048`, Michael Scott `HTL-3072`).
  - **Hotel Amenities & Policies**: Answers Wi-Fi credentials (`GrandAzure_Guest` / `AzureStay2026`), complimentary breakfast hours (6:30 AM – 10:30 AM), 4th-floor infinity pool, 24/7 fitness center, valet parking, and check-in (3 PM) / check-out (11 AM) times.
  - **Guest Services & Housekeeping**: Logs requests for extra towels, pillows, room cleaning, wake-up calls, or room service with reference IDs (`REQ-XXX`).
- **⚡ Super Lightweight Framework**:
  - Single FastAPI service with zero heavy binary dependencies.

---

## 🏗️ Project Structure

```
Demo-voice-reception-Agent/
├── main.py               # Lightweight FastAPI app & chat endpoints
├── agent.py              # Gemini Agent with hotel system prompt
├── static/
│   ├── index.html        # Voice receptionist web interface
│   ├── style.css         # Luxury hotel UI styling & audio visualizer
│   └── app.js            # Speech recognition & text-to-speech engine
├── tests/
│   └── test_agent.py     # Automated test suite
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── pytest.ini            # Pytest configuration
```

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your Gemini API Key
Create a `.env` file by copying the template:
```bash
cp .env.example .env
```
Open `.env` and add your Google Gemini API key:
```ini
GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
```
*(Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

### 3. Run the application
```bash
python main.py
```
Or with Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🗣️ Voice Prompts to Try

| Topic | Example Question |
| :--- | :--- |
| **Room Rates** | *"Do you have any rooms available tonight? What are the prices?"* |
| **Wi-Fi Details** | *"What is the Wi-Fi network and password?"* |
| **Breakfast** | *"What time is breakfast served and where is it located?"* |
| **Lookup Booking** | *"Can you look up the reservation for John Doe?"* |
| **Guest Services** | *"Can you please send extra towels to room 402?"* |
| **Book a Room** | *"I'd like to book a Deluxe Queen Suite for 2 nights for Alex Smith"* |
| **Check-out Time** | *"What time is check-out tomorrow?"* |
| **Amenities** | *"Where is the pool and what time does it close?"* |

---

## 🧪 Running Tests

```bash
python -m pytest
```

---

## 📄 License
MIT License
