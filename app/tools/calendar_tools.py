"""
Calendar Tools for LangGraph
LangChain tool wrappers for calendar operations
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from langchain_core.tools import tool

from app.calendar.calendar_manager import CalendarManager

logger = logging.getLogger(__name__)

# Initialize calendar manager (lazy loading)
_calendar_manager = None


def get_calendar_manager() -> CalendarManager:
    """Get or initialize calendar manager"""
    global _calendar_manager
    
    if _calendar_manager is None:
        _calendar_manager = CalendarManager()
        _calendar_manager.authenticate()
    
    return _calendar_manager


@tool
def list_calendars() -> str:
    """
    List all available calendars.
    
    Use this tool to see what calendars the user has access to.
    
    Returns:
        Formatted list of calendars
    
    Examples:
        - "Show me my calendars"
        - "What calendars do I have?"
    """
    try:
        manager = get_calendar_manager()
        calendars = manager.list_calendars()
        
        if not calendars:
            return "No calendars found."
        
        output = [f"Found {len(calendars)} calendar(s):\n"]
        
        for i, cal in enumerate(calendars, 1):
            primary = " (Primary)" if cal.get('primary') else ""
            output.append(f"{i}. {cal['summary']}{primary}")
            output.append(f"   ID: {cal['id']}")
            output.append(f"   Access: {cal.get('access_role', 'N/A')}\n")
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Error listing calendars: {e}")
        return f"Error listing calendars: {str(e)}"


@tool
def get_upcoming_events(days: int = 7, max_results: int = 10) -> str:
    """
    Get upcoming calendar events.
    
    Use this tool to see what events are scheduled in the near future.
    
    Args:
        days: Number of days to look ahead (default: 7)
        max_results: Maximum number of events to return (default: 10)
    
    Returns:
        Formatted list of upcoming events
    
    Examples:
        - "What's on my calendar this week?"
        - "Show me my upcoming meetings"
        - "What do I have scheduled?"
    """
    try:
        manager = get_calendar_manager()
        
        time_min = datetime.now()
        time_max = time_min + timedelta(days=days)
        
        events = manager.get_events(
            time_min=time_min,
            time_max=time_max,
            max_results=max_results
        )
        
        if not events:
            return f"No events scheduled in the next {days} days."
        
        output = [f"Found {len(events)} upcoming event(s):\n"]
        
        for i, event in enumerate(events, 1):
            start = event['start_time']
            output.append(f"{i}. {event['summary']}")
            output.append(f"   When: {start}")
            
            if event.get('location'):
                output.append(f"   Where: {event['location']}")
            
            if event.get('attendees'):
                attendees = ', '.join(event['attendees'][:3])
                if len(event['attendees']) > 3:
                    attendees += f" and {len(event['attendees']) - 3} more"
                output.append(f"   Attendees: {attendees}")
            
            output.append("")
        
        return "\n".join(output)
        
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        return f"Error getting events: {str(e)}"


@tool
def create_calendar_event(
    summary: str,
    start_time: str,
    duration_minutes: int = 60,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """
    Create a new calendar event.
    
    Use this tool to schedule meetings or events.
    
    Args:
        summary: Event title/summary
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        duration_minutes: Event duration in minutes (default: 60)
        description: Event description (optional)
        location: Event location (optional)
    
    Returns:
        Confirmation message with event details
    
    Examples:
        - "Schedule a meeting with John tomorrow at 2pm"
        - "Create an event called 'Team Standup' for Monday at 9am"
        - "Add a 30-minute call with client at 3pm today"
    """
    try:
        manager = get_calendar_manager()
        
        # Parse start time
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Create event
        event = manager.create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            location=location
        )
        
        if not event:
            return "Failed to create event."
        
        output = [f"✅ Event created successfully!\n"]
        output.append(f"Title: {event['summary']}")
        output.append(f"When: {event['start_time']}")
        output.append(f"Duration: {duration_minutes} minutes")
        
        if location:
            output.append(f"Where: {location}")
        
        if event.get('html_link'):
            output.append(f"\nView in Calendar: {event['html_link']}")
        
        return "\n".join(output)
        
    except ValueError as e:
        return f"Invalid time format. Please use ISO format (YYYY-MM-DDTHH:MM:SS): {str(e)}"
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return f"Error creating event: {str(e)}"


@tool
def check_availability(start_time: str, end_time: str) -> str:
    """
    Check if a time slot is available.
    
    Use this tool to see if the user is free during a specific time.
    
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
    
    Returns:
        Availability status
    
    Examples:
        - "Am I free tomorrow at 2pm?"
        - "Check if I'm available Monday morning"
        - "Do I have anything scheduled at 3pm today?"
    """
    try:
        manager = get_calendar_manager()
        
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        is_free = manager.check_availability(start_dt, end_dt)
        
        if is_free:
            return f"✅ You are free from {start_time} to {end_time}"
        else:
            return f"❌ You have events scheduled during {start_time} to {end_time}"
        
    except ValueError as e:
        return f"Invalid time format: {str(e)}"
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return f"Error checking availability: {str(e)}"


@tool
def find_free_time(date: str, duration_minutes: int = 60) -> str:
    """
    Find free time slots on a specific date.
    
    Use this tool to find when the user is available for meetings.
    
    Args:
        date: Date in ISO format (YYYY-MM-DD)
        duration_minutes: Required duration in minutes (default: 60)
    
    Returns:
        List of available time slots
    
    Examples:
        - "When am I free tomorrow?"
        - "Find a 30-minute slot on Friday"
        - "What times are available next Monday?"
    """
    try:
        manager = get_calendar_manager()
        
        date_dt = datetime.fromisoformat(date)
        
        free_slots = manager.find_free_slots(
            date=date_dt,
            duration_minutes=duration_minutes
        )
        
        if not free_slots:
            return f"No free slots of {duration_minutes} minutes found on {date}"
        
        output = [f"Found {len(free_slots)} free slot(s) on {date}:\n"]
        
        for i, slot in enumerate(free_slots, 1):
            start = slot['start'].strftime('%H:%M')
            end = slot['end'].strftime('%H:%M')
            duration = (slot['end'] - slot['start']).total_seconds() / 60
            output.append(f"{i}. {start} - {end} ({int(duration)} minutes)")
        
        return "\n".join(output)
        
    except ValueError as e:
        return f"Invalid date format. Please use YYYY-MM-DD: {str(e)}"
    except Exception as e:
        logger.error(f"Error finding free time: {e}")
        return f"Error finding free time: {str(e)}"


@tool
def delete_calendar_event(event_id: str) -> str:
    """
    Delete a calendar event.
    
    Use this tool to cancel or remove events.
    
    Args:
        event_id: ID of the event to delete
    
    Returns:
        Confirmation message
    
    Examples:
        - "Cancel my 2pm meeting"
        - "Delete the team standup event"
        - "Remove the event with ID xyz123"
    """
    try:
        manager = get_calendar_manager()
        
        success = manager.delete_event(event_id)
        
        if success:
            return f"✅ Event deleted successfully"
        else:
            return f"❌ Failed to delete event"
        
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return f"Error deleting event: {str(e)}"


# Export all calendar tools
CALENDAR_TOOLS = [
    list_calendars,
    get_upcoming_events,
    create_calendar_event,
    check_availability,
    find_free_time,
    delete_calendar_event
]

# Tool descriptions for agent
CALENDAR_TOOLS_DESCRIPTION = """
## Calendar Tools

1. **list_calendars**: List all available calendars
   - Use when: User wants to see their calendars
   - Example: "Show me my calendars"

2. **get_upcoming_events**: Get upcoming calendar events
   - Use when: User wants to see scheduled events
   - Example: "What's on my calendar this week?"

3. **create_calendar_event**: Create a new event
   - Use when: User wants to schedule something
   - Example: "Schedule a meeting tomorrow at 2pm"

4. **check_availability**: Check if a time slot is free
   - Use when: User asks about availability
   - Example: "Am I free tomorrow at 3pm?"

5. **find_free_time**: Find available time slots
   - Use when: User needs to find meeting times
   - Example: "When am I free on Friday?"

6. **delete_calendar_event**: Delete an event
   - Use when: User wants to cancel an event
   - Example: "Cancel my 2pm meeting"
"""

# Made with Bob
