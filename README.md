# Odyssey-AI 🌍✈️

Odyssey-AI is an intelligent travel assistant application designed to streamline travel planning and enhance user experiences. It leverages advanced AI models, modular agents, and rich visual tools to provide personalized recommendations, itinerary planning, image generation, and creative solutions for travelers. With Odyssey-AI, users enjoy seamless, AI-powered travel planning via voice or text—complete with real-world photos and custom-generated visuals for each suggestion.

---

## Table of Contents
- [Key Technical Highlights](#key-technical-highlights)
- [Layman-Friendly Explanation](#layman-friendly-explanation)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Using Docker](#using-docker)
- [Endpoints](#endpoints)
- [User Journey](#user-journey)
- [Security & Privacy](#security--privacy)
- [Contributing](#contributing)
- [License](#license)

---

## Key Technical Highlights

- **Agent-Oriented Architecture:** Modular agents handle specific tasks such as greeting, booking, itinerary planning, and creative solutions.
- **Interactive Frontend:** A web-based interface allows users to interact seamlessly with the AI assistant.
- **Audio Processing:** Supports audio input and output using custom audio player and recorder tools.
- **Creative Tools:** Generates creative travel ideas and solutions using advanced AI models.
- **Google Cloud Integration:** Utilizes Google Cloud services for deployment and scalability.
- **Proactive Visuals:** The itinerary agent automatically sends authentic photos for every suggested place, restaurant, or activity using Google Maps and Google Place Photos API.
- **AI-Powered Image Generation:** The creative agent can generate custom images for travel ideas or user requests via Google Imagen.
- **Automated Visual Routing:** All image and photo requests are routed to specialist agents for fast, context-aware responses.
- **Structured, Visual-First Trip Planning:** The itinerary agent plans each day in a clear structure (Morning Activity, Lunch, Afternoon Activity, Dinner) and sends images for each, making the experience both informative and visually engaging.

---

## Layman-Friendly Explanation

Odyssey-AI is your smart travel buddy. It can chat with you through text or voice, help you book flights or hotels, and create personalized travel plans. What makes it unique is that it doesn’t just suggest places—it proactively sends real images of those places and can generate custom travel visuals on demand. Every itinerary is interactive and immersive, so you see exactly where you're going and what you'll experience before you even leave home.

---

## Project Structure

```text
Odyssey-AI/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── Dockerfile               # Containerization instructions
├── deploy.sh                # Deployment helper for Cloud Run
├── .env                     # Environment variables (not committed)
├── agents/                  # Core AI logic
│   ├── agent.py
│   ├── booking_agent.py
│   ├── creative_agent.py
│   ├── greeting_agent.py
│   └── itinerary_agent.py
├── frontend/
│   └── static/
│       ├── index.html
│       ├── js/
│       │   ├── app.js
│       │   ├── audio-player.js
│       │   ├── audio-recorder.js
│       │   ├── pcm-player-processor.js
│       │   └── pcm-recorder-processor.js
│       └── styles/
│           └── style.css
├── tools/                   # Utility tools for backend processing
│   ├── agent_wrappers.py
│   ├── creative_backend_tools.py
│   ├── place_photo_tools.py
│   └── planning_tools.py
├── README.md
└── LICENSE
```

---

## Tech Stack

**Backend**
- Python 3.8+
- FastAPI (for API handling)
- Google Cloud SDK (for deployment and scalability)

**Frontend**
- HTML5, CSS3, Vanilla JS (ES6+)
- Web Audio API + AudioWorklet
- Streams PCM as base64-encoded JSON over WebSocket

**DevOps**
- Docker & deploy.sh
- .env for secrets (not committed)
- Google Cloud Run for deployment

---

## Environment Variables

Create a `.env` file with the following keys:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY='your-api-key'
GOOGLE_PROJECT_ID='projectname'
LOCATION="us-central1"
STAGING_BUCKET='gs://bucketname'
GCP_BUCKET_NAME='bucketname'
REASONING_ENGINE_NAME='projects/project_id/locations/us-central1/reasoningEngines/engine_id'
```

> **Note:** Never commit .env or API keys to source control.

---

## Running Locally

**1. Create & activate virtual environment:**
```sh
python -m venv venv
venv\Scripts\activate  # On Windows
# Or on Unix/Mac: source venv/bin/activate
```

**2. Install dependencies:**
```sh
pip install -r requirements.txt
```

**3. Add your Google credentials to `.env`.**

**4. Start the server:**
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**5. Open the UI in your browser:**  
[http://localhost:8000/](http://localhost:8000/)

---

## Using Docker

**Build the image:**
```sh
docker build -t odyssey-ai .
```

**Run the container:**
```sh
docker run -p 8000:8000 --env-file .env odyssey-ai
```

---

## Endpoints

Odyssey-AI uses a single, unified **WebSocket endpoint** for all agent communication and audio interactions.

### Main Endpoints

- **`GET /`**  
  Serves the static UI (`frontend/static/index.html`).

- **`/static/*`**  
  Serves static files (HTML, JS, CSS, images) from the frontend.

### Core WebSocket Endpoint

- **`ws://<host>/ws/{session_id}?is_audio=true|false`**  
  - All agent communication (greeting, booking, itinerary, creative, images, audio) occurs over this single WebSocket endpoint.
  - `session_id` is a unique string per user session.
  - `is_audio=true` enables audio streaming and voice interaction; otherwise, interaction is text-based.
  - The backend routes each message to the correct agent (greeting, booking, itinerary, creative/image) and streams responses back, including text, images, and audio.

**No separate REST API endpoints** are exposed for agent actions; all agent and tool interactions—including text, audio, image responses, and proactive visuals—are handled via this websocket.

---

## User Journey

1. **User opens UI:** Sees a chat interface and mic button.
2. **User types or speaks:** Chat or voice input is captured.
3. **Browser captures audio:** AudioWorklet records raw PCM and streams it to the backend.
4. **Backend processes input:** Routes the input to the appropriate agent for processing (greeting, booking, itinerary, creative).
5. **Agent returns response:** Structured JSON and/or synthesized audio is sent back.
6. **Frontend displays results:** Shows text, plays audio, and handles tool results.
7. **Visual Features:** For every itinerary suggestion, the backend proactively sends real-world photos or AI-generated images, which are instantly displayed in the UI. Users can also request creative visuals or travel postcards and receive custom-generated images.

---

## Security & Privacy

- Never commit `.env` or keys.
- Treat user data as sensitive; use TLS in production.
- Minimize logging of PII.
- Add authentication and secure storage before production use.

---

## Contributing

1. Fork the repo, create a feature branch, and open a Pull Request.
2. Run linters and tests before submitting.
3. Keep changes modular:
   - Agent logic in `agents/`
   - Frontend logic in `frontend/static/js/`
4. Update README and `.env.example` for new keys.
5. Open issues for feature requests or improvements.

---

## License

MIT — see [LICENSE](LICENSE).
