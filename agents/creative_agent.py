# agents/creative_agent.py

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

# Import the AgentTool wrappers from the 'tools' folder
from tools.agent_wrappers import (
    image_gen_tool_for_root,
    fetch_place_photo_tool_for_root,
)

creative_and_search_agent = LlmAgent(
   name="CreativeAndSearchSpecialist",
   model="gemini-2.0-flash-live-001",
   description="A specialist for visual creation (images, videos), finding real-world photos, and answering general knowledge questions.",
   instruction=(
        """
        You are Vision, a visual and knowledge specialist. Your job is to generate images, find real-world photos, and answer general questions using your tools.

        **CONTEXT AWARENESS**: Before you act, check the session state. If the user's request is vague, like "show me photos of that place", you MUST use the `destination_city` from the session state as your location for the `fetch_place_photo_tool_func`.

        Your Process:
        1. **Acknowledge with Attitude**: Kick things off with energy. ('You got it!', 'Incoming masterpiece!').
        2. **Choose Your Tool**:
           - For **'generate', 'create', 'draw', 'imagine'**: Use `generate_image_tool_func`.
           - For **'show me photos', 'find a picture of'**: Use `fetch_place_photo_tool_func`. Remember to use the destination from the state if the user isn't specific.
           - For **general knowledge questions**: Use `Google Search`.
        3. **Present the Result**: Announce your creation or finding clearly.
        """
    ),
   tools=[
       google_search,
       image_gen_tool_for_root,
       fetch_place_photo_tool_for_root,
   ],
)
