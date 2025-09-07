# Odyssey-AI

Odyssey-AI is an intelligent travel assistant application designed to streamline travel planning and enhance user experiences. It leverages advanced AI models and modular agents to provide personalized recommendations, itinerary planning, and creative solutions for travelers.

---

## Features

- **Agent-Oriented Architecture**: Modular agents for greeting, booking, itinerary planning, and creative tasks.
- **Interactive Frontend**: A web-based interface for seamless interaction with the AI assistant.
- **Audio Processing**: Support for audio input and output using custom audio player and recorder tools.
- **Creative Tools**: Generate creative travel ideas and solutions using advanced AI models.
- **Google Cloud Integration**: Utilizes Google Cloud services for deployment and scalability.

---

## Code Repository Structure

The repository is organized as follows:

```text
Odyssey-AI/ 
├── agents/ # Specialized agents for handling specific tasks 
│ ├── agent.py # Root agent orchestrating sub-agents 
│ ├── booking_agent.py # Handles booking-related tasks 
│ ├── creative_agent.py # Provides creative travel solutions 
│ ├── greeting_agent.py # Manages user greetings and onboarding 
│ ├── itinerary_agent.py # Plans travel itineraries 
├── frontend/ # Web-based user interface 
│ ├── static/ # Static assets for the frontend 
│ │ ├── index.html # Main HTML file 
│ │ └── js/ # JavaScript files for frontend functionality 
│ │ ├── app.js # Main frontend logic 
│ │ ├── audio-player.js # Audio playback functionality 
│ │ ├── audio-recorder.js # Audio recording functionality 
│ │ ├── pcm-player-processor.js # PCM audio player processor 
│ │ └── pcm-recorder-processor.js # PCM audio recorder processor 
├── tools/ # Utility tools for backend processing 
│ ├── agent_wrappers.py # Wrappers for agent interactions 
│ ├── creative_backend_tools.py # Tools for creative content generation 
│ ├── place_photo_tools.py # Tools for handling place photos 
│ └── planning_tools.py # Tools for travel planning 
├── .env # Environment variables (not included in the repo) 
├── .gcloudignore # Files to ignore during Google Cloud deployment 
├── .gitignore # Files to ignore in Git 
├── deploy.sh # Deployment script 
├── Dockerfile # Docker configuration for containerization 
├── LICENSE # License file (MIT License) 
├── main.py # Main application entry point 
├── README.md # Project documentation 
├── requirements.txt # Python dependencies
```text

---

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud SDK installed
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/Odyssey-AI.git
    cd Odyssey-AI
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory and add the following variables:

    ```plaintext
    GOOGLE_PROJECT_ID=your-google-project-id
    GOOGLE_API_KEY=your-google-api-key
    ```

---

## Usage

### Running the Application Locally

1. Start the backend server:

    ```bash
    python main.py
    ```

2. Open the `index.html` file in the `frontend/static/` directory to access the web interface.

---

## Deployment

### Deploying to Google Cloud Run

1. Build and push the Docker image:

    ```bash
    gcloud builds submit --tag gcr.io/your-google-project-id/odyssey-ai
    ```

2. Deploy the application:

    ```bash
    gcloud run deploy odyssey-ai \
      --image gcr.io/your-google-project-id/odyssey-ai \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated
    ```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
