# Odyssey-AI 🌍✈️

Odyssey-AI is an intelligent travel assistant application designed to streamline travel planning and enhance user experiences. It leverages advanced AI models and modular agents to provide personalized recommendations, itinerary planning, and creative solutions for travelers. With Odyssey-AI, users can enjoy seamless, AI-powered travel planning via voice or text.

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

---

## Layman-Friendly Explanation

Odyssey-AI is an intelligent travel assistant application designed to streamline travel planning and enhance user experiences. It leverages advanced AI models and modular agents to provide personalized recommendations, itinerary planning, and creative solutions for travelers. With Odyssey-AI, users can enjoy seamless, AI-powered travel planning via voice or text.

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

---

## Endpoints

**1. `GET /`**  
Serves the static UI (`frontend/static/index.html`)

**2. Static files**  
Mounted at `/static` → `frontend/static/*`

**3. API Endpoints**  
Endpoints for interacting with agents (e.g., booking, itinerary planning) are defined in `main.py`.

---

## User Journey

1. **User opens UI:** Sees a chat interface and mic button.
2. **User types or speaks:** Chat or voice input is captured.
3. **Browser captures audio:** AudioWorklet records raw PCM and streams it to the backend.
4. **Backend processes input:** Routes the input to the appropriate agent for processing.
5. **Agent returns response:** Structured JSON and/or synthesized audio is sent back.
6. **Frontend displays results:** Shows text, plays audio, and handles tool results.

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

