# Demo Hotel Voice Receptionist Agent

A simple demo test agent for a hotel voice receptionist powered by Gemini and FastAPI.

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

> **Note**: Add your `GEMINI_API_KEY` to `.env` (see `.env.example`).

## How to Test

Send a `POST` request to `http://localhost:8000/chat`:

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Do you have any rooms available tonight?"}'
```
