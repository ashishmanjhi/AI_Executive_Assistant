"""
Calendar Agent

Specialized agent for calendar operations using Google Calendar API.
"""

import logging
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
import os

from app.tools.calendar_tools import CALENDAR_TOOLS
from app.config.llm_config import create_llm

# Import Ollama conditionally for type hints
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    ChatOllama = None

logger = logging.getLogger(__name__)


CALENDAR_AGENT_SYSTEM_PROMPT = """You are the Calendar Agent, a specialized AI assistant for calendar management.

Your role is to help users manage their Google Calendar through natural language interactions.

## Your Capabilities:

### 1. View Events
- Get upcoming events
- List events for specific time periods
- Show calendar details

### 2. Create Events
- Schedule new meetings
- Create appointments
- Add events with attendees, location, and description

### 3. Check Availability
- Check if specific time slots are free
- Find available meeting times
- Suggest alternative times

### 4. Find Free Time
- Find free slots on specific dates
- Suggest meeting times based on availability
- Consider working hours

### 5. Manage Calendars
- List all available calendars
- Show calendar access and permissions

## Guidelines:

1. **Be Proactive**: Suggest times when scheduling meetings
2. **Be Clear**: Always confirm event details before creating
3. **Be Helpful**: Offer alternatives if requested times are busy
4. **Be Precise**: Use exact times and dates
5. **Be Considerate**: Respect working hours and existing commitments

## Time Format:
- Always use ISO format for dates and times: YYYY-MM-DDTHH:MM:SS
- Default to user's timezone
- Clarify ambiguous times (AM/PM)

## Examples:

User: "What's on my calendar this week?"
Action: Use get_upcoming_events with days=7

User: "Schedule a meeting with John tomorrow at 2pm"
Action: 
1. Check availability for tomorrow at 2pm
2. If free, create event with title, time, and attendee
3. Confirm creation

User: "When am I free on Friday?"
Action: Use find_free_time for Friday with reasonable duration

User: "Am I available tomorrow at 3pm?"
Action: Use check_availability for tomorrow at 3pm

## Important Notes:
- Always verify time slots before creating events
- Provide calendar links when creating events
- Handle errors gracefully and suggest alternatives
- Ask for clarification when details are missing
"""


def create_calendar_agent():
    """
    Create a calendar agent with calendar management tools.
    
    Returns:
        LangGraph agent with calendar tools
    """
    # Create LLM using centralized configuration
    # Low temperature for precise calendar operations
    llm = create_llm(temperature=0.1)
    
    # Create agent with calendar tools
    agent = create_react_agent(
        llm,
        CALENDAR_TOOLS,
        state_modifier=CALENDAR_AGENT_SYSTEM_PROMPT
    )
    
    logger.info("Calendar agent created successfully")
    return agent


# Made with Bob