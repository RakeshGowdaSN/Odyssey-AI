# main.py

import os
import json
import asyncio
import base64
# No longer need functools or copy
# import functools
# import copy

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)
from google.genai import types as genai_types

from google.adk.tools import FunctionTool
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from agents.agent import root_agent
# --- NEW: Import the context variable we defined ---
# from tools.agent_wrappers import side_channel_context
from tools.agent_wrappers import side_channel_context, session_context

load_dotenv()

# --- Application Setup ---
APP_NAME = "ADK Streaming"
STATIC_DIR = Path("frontend/static")
session_service = InMemorySessionService()

# --- REVERTED: start_agent_session is simple again ---
async def start_agent_session(session_id: str, is_audio: bool = False):
    """Starts an agent session asynchronously."""
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
        # state={} # Newly added for banking

    )
    # We now use the global root_agent again, as it's never modified.
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    modality = "AUDIO"
    run_config = RunConfig(
        speech_config=genai_types.SpeechConfig(
            language_code="en-US",
            voice_config=genai_types.VoiceConfig(
                prebuilt_voice_config=genai_types.PrebuiltVoiceConfig(
                    voice_name="Leda"
                )
            ),
        ),
        response_modalities=[modality],
        # save_input_blobs_as_artifacts=True,
        support_cfc=False,
        streaming_mode=StreamingMode.BIDI,
        # max_llm_calls=1000,

        realtime_input_config = genai_types.RealtimeInputConfig(
        automatic_activity_detection=genai_types.AutomaticActivityDetection(
            disabled = False, # default
            start_of_speech_sensitivity= genai_types.StartSensitivity.START_SENSITIVITY_LOW,
            end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_LOW,
            prefix_padding_ms=10,
            silence_duration_ms= 3000,
        )
    ),

        # This tells the agent to transcribe its own generated audio.
        output_audio_transcription=genai_types.AudioTranscriptionConfig(),
        input_audio_transcription=genai_types.AudioTranscriptionConfig(),

    )

    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    # return live_events, live_request_queue
    return live_events, live_request_queue, session

async def agent_to_client_messaging(websocket: WebSocket, live_events):
    async for event in live_events:
        # The temporary debugging print() line can now be removed.

        # 1. Handle turn completion first
        if event.turn_complete or event.interrupted:
            await websocket.send_text(json.dumps({
                "turn_complete": event.turn_complete, 
                "interrupted": event.interrupted
            }))
            continue

        # 2. Process events that have content
        if event.content and event.content.parts:
            # Check the role to determine the author
            author = event.content.role

            for part in event.content.parts:
                # If there's text, send it with the correct type based on the author
                if part.text:
                    # If the author is the USER, it's an input transcription
                    if author == 'user':
                        await websocket.send_text(json.dumps({
                            "mime_type": "text/input_transcription",
                            "data": part.text
                        }))
                    # If the author is the MODEL, it's the agent's speech
                    elif author == 'model':
                        # Use the event.partial flag to distinguish live transcript from final text
                        if event.partial:
                            await websocket.send_text(json.dumps({
                                "mime_type": "text/transcription",
                                "data": part.text
                            }))
                        else:
                            await websocket.send_text(json.dumps({
                                "mime_type": "text/plain",
                                "data": part.text
                            }))

                # Handle audio data from the agent (this remains the same)
                elif part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                    await websocket.send_text(json.dumps({
                        "mime_type": "audio/pcm", 
                        "data": base64.b64encode(part.inline_data.data).decode("ascii")
                    }))


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    while True:
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        if message["mime_type"] == "text/plain":
            live_request_queue.send_content(content=Content(role="user", parts=[Part.from_text(text=message["data"])]))
        elif message["mime_type"] == "audio/pcm":
            live_request_queue.send_realtime(Blob(data=base64.b64decode(message["data"]), mime_type=message["mime_type"]))

async def handle_side_channel_messages(websocket: WebSocket, queue: asyncio.Queue):
    while True:
        data_from_queue = await queue.get()
        if isinstance(data_from_queue, list):
            message = {"mime_type": "image/url_list", "data": data_from_queue}
        elif isinstance(data_from_queue, str):
            message = {"mime_type": "image/url", "data": data_from_queue}
        else:
            queue.task_done()
            continue
        await websocket.send_text(json.dumps(message))
        queue.task_done()

# --- FastAPI App Setup (No Changes) ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root(): return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# --- FINAL REVISED: Websocket endpoint with contextvars ---
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, is_audio: bool = False):
    """Handles the WebSocket connection for a client session."""
    await websocket.accept()
    print(f"Client #{session_id} connected, audio mode: {is_audio}")

    side_channel_queue = asyncio.Queue()

    # Create a new async function to run our tasks. This makes it easy
    # to set the context for all of them.
    async def run_tasks_with_context():
        # Start the agent session (now uses the global agent)
        # live_events, live_request_queue = await start_agent_session(session_id, is_audio)
        
        # --- MODIFIED: Start the agent session and get the session object ---
        live_events, live_request_queue, session_object = await start_agent_session(session_id, is_audio)
        
        # --- THE BRIDGE (Part 2): Set the session object in the context variable ---
        session_context.set(session_object)
        
        # Create all concurrent tasks
        tasks = [
            agent_to_client_messaging(websocket, live_events),
            client_to_agent_messaging(websocket, live_request_queue),
            handle_side_channel_messages(websocket, side_channel_queue)
        ]
        done, pending = await asyncio.wait([asyncio.create_task(t) for t in tasks], return_when=asyncio.FIRST_COMPLETED)
        
        for task in pending:
            task.cancel()

    try:
        # --- THE FIX ---
        # Set the context variable to our session-specific queue
        side_channel_context.set(side_channel_queue)
        # Run all our tasks within this context. Any tool called by the agent
        # within this block can now access the queue.
        await run_tasks_with_context()

    except WebSocketDisconnect:
        print(f"Client #{session_id} disconnected cleanly.")
    except Exception as e:
        print(f"An error occurred in the websocket endpoint for client #{session_id}: {e}")
    finally:
        print(f"Connection for client #{session_id} closed.")
