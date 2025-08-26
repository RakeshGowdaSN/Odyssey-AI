# tools/agent_wrappers.py
import json
import asyncio
from google.adk.tools import FunctionTool, agent_tool

# --- NEW: Import contextvars and create the context variable ---
# This variable will hold the queue for the current session.
from contextvars import ContextVar
side_channel_context = ContextVar('side_channel_queue', default=None)
    
# --- ADD THIS NEW CONTEXT VARIABLE FOR SESSION STATE ---
session_context = ContextVar('session_object', default=None)


# --- Tool Imports ---
from tools.creative_backend_tools import call_generate_image_api
from tools.place_photo_tools import fetch_and_upload_place_photos


# =========================================================================
# === IMAGE GENERATION FUNCTION TOOL (REVISED FOR CONTEXTVARS) ===
# =========================================================================
async def generate_image_tool_func(prompt: str) -> str:
    """
    Generates an image, finds the side-channel queue via contextvar to send
    the URL, and returns a simple success message to the agent.
    """
    # The function signature is now simple, which the ADK can parse.
    print(f"DEBUG: generate_image_tool_func called with prompt: '{prompt}'")
    
    # --- Get the queue from the context instead of as a parameter ---
    side_channel_queue = side_channel_context.get()
    
    if not prompt:
        return "Error: I didn't receive a prompt."
    try:
        public_url = await call_generate_image_api(prompt)

        if side_channel_queue:
            print(f"DEBUG: Putting URL into side channel queue via contextvar: {public_url}")
            await side_channel_queue.put(public_url)
        else:
            print("WARNING: Could not find side channel queue in context.")

        # Using your creative return message!
        return "Fresh from the Dreamscape. Now on your screen"

    except Exception as e:
        error_msg = f"Sorry, I failed to generate the image. The error was: {str(e)}"
        print(f"ERROR: {error_msg}")
        return f"Error: {error_msg}"

image_gen_tool_for_root = FunctionTool(
    func=generate_image_tool_func
)

# =========================================================================
# === PLACE PHOTO FUNCTION TOOL (REVISED FOR CONTEXTVARS) ===
# =========================================================================
async def fetch_place_photo_tool_func(place_name: str) -> str:
    """
    Fetches photos, finds the side-channel queue via contextvar to send the
    URL list, and returns a success message to the agent.
    """
    # The function signature is now simple, which the ADK can parse.
    print(f"DEBUG: fetch_place_photo_tool_func called with place_name: '{place_name}'")

    # --- Get the queue from the context instead of as a parameter ---
    side_channel_queue = side_channel_context.get()

    if not place_name:
        return "Error: No place_name provided."
    try:
        public_urls, display_name = await fetch_and_upload_place_photos(place_name)

        if side_channel_queue and public_urls:
            print(f"DEBUG: Putting list of {len(public_urls)} URLs for '{display_name}' into side channel queue via contextvar.")
            await side_channel_queue.put(public_urls)
        else:
            print("WARNING: Could not find side channel queue in context or no URLs were fetched.")

        # Using your creative return message!
        return f"Teleporting you there visually. Here comes {display_name}."

    except Exception as e:
        error_msg = f"I'm sorry, I couldn't get photos for that. The error was: {str(e)}"
        print(f"ERROR: {error_msg}")
        return f"Error: {error_msg}"

fetch_place_photo_tool_for_root = FunctionTool(
    func=fetch_place_photo_tool_func
)
