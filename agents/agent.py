# agents/agent.py

from google.adk.agents import LlmAgent
from agents.greeting_agent import greeting_agent
from agents.booking_agent import booking_agent
from agents.itinerary_agent import itinerary_planning_agent
from agents.creative_agent import creative_and_search_agent

# --- Orchestrator with Corrected Routing Rules ---
root_agent = LlmAgent(
    name="TravelAssistOrchestrator",
    model="gemini-2.0-flash-live-001",
    # model="gemini-2.5-flash-preview-native-audio-dialog",
    description="A simple, stateless router that delegates tasks to specialist agents.",
    sub_agents=[
        greeting_agent,
        booking_agent,
        itinerary_planning_agent,
        creative_and_search_agent,
    ],
    # --- THIS INSTRUCTION IS CORRECTED WITH CONSISTENT NAMES ---
    instruction="""
    You are a silent, non-conversational routing system. Your ONLY function is to analyze the user's intent and immediately call `transfer_to_agent` with the correct `agent_name`. You MUST NOT generate any conversational text.

    **Routing Rules:**
    1.  **Greeting**: If this is the very first turn of the conversation, delegate to the `GreetingAgent`.
    2.  **Booking Intent**: If the user's request is about booking, reserving, or finding 'flights' or 'hotels', delegate to the `ConversationalBookingAgent`.
    3.  **Itinerary Intent**: If the user's request is about planning a trip, creating an 'itinerary', or asking 'what to do', delegate to the `ItineraryPlanningAgent`.
    4.  **Creative/Search Intent**: If the user's request is to 'generate an image', 'show a photo', or is a general knowledge question, delegate to the `CreativeAndSearchSpecialist`.

    Analyze the input and output your delegation call immediately.
    """
)
