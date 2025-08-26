# agents/booking_agent.py

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from tools.planning_tools import (
    flight_search_tool,
    hotel_search_tool,
    mock_book_flight,
    mock_book_hotel
)

# --- Tool Definitions ---
flight_search_tool = FunctionTool(func=flight_search_tool)
book_flight_tool = FunctionTool(func=mock_book_flight)
hotel_search_tool = FunctionTool(func=hotel_search_tool)
book_hotel_tool = FunctionTool(func=mock_book_hotel)

# --- Simplified Agent Definition ---
booking_agent = LlmAgent(
    name="ConversationalBookingAgent",
    model="gemini-2.0-flash-live-001",
    tools=[flight_search_tool, hotel_search_tool, book_flight_tool, mock_book_hotel],
    instruction="""
    You are a friendly and hyper-efficient Travel Booking Assistant.

    **Your Single Task:** Help the user book a flight or a hotel.

    **Your Process:**
    1.  **Gather ALL Details:** Start by asking the user for ALL the information you need for the task.
        - For flights, ask for origin, destination, travel dates, and number of passengers in a single question.
        - For hotels, ask for location, check-in/out dates, number of guests, and budget in a single question.
    2.  **Execute Tool:** Once you have the details, call the correct tool (`flight_search_tool` or `hotel_search_tool`).
    3.  **Present Results:** Present the results returned by the tool using the structured Markdown templates for flights and hotels. Do not summarize or omit details.
    4.  **Confirm and Book:** Await the user's choice, confirm their selection by name, and then call the final booking tool (`mock_book_flight` or `mock_book_hotel`).
    5.  **Finish:** Present the final confirmation and end your task.
    """,
    description="A self-contained agent for handling flight and hotel bookings."
)
