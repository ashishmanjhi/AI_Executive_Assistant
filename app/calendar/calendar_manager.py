"""
Calendar Manager
Google Calendar API integration
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

from app.calendar.event_store import EventStore

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarManager:
    """
    Google Calendar integration manager
    
    Handles authentication, event management, and synchronization
    with Google Calendar API.
    """
    
    def __init__(
        self,
        credentials_path: str = "credentials.json",
        token_path: str = "calendar_token.pickle",
        event_store: Optional[EventStore] = None
    ):
        """Initialize calendar manager"""
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.event_store = event_store or EventStore()
        self.service = None
        
        logger.info("Calendar manager initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API
        
        Returns:
            True if authentication successful
        """
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed calendar credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Obtained new calendar credentials")
                except Exception as e:
                    logger.error(f"Error getting credentials: {e}")
                    return False
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Calendar service built successfully")
            return True
        except Exception as e:
            logger.error(f"Error building calendar service: {e}")
            return False
    
    def get_service(self):
        """Get or create calendar service"""
        if not self.service:
            if not self.authenticate():
                raise RuntimeError("Failed to authenticate with Google Calendar")
        return self.service
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars
        
        Returns:
            List of calendar dictionaries
        """
        try:
            service = self.get_service()
            calendar_list = service.calendarList().list().execute()
            
            calendars = []
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar.get('summary', ''),
                    'description': calendar.get('description', ''),
                    'primary': calendar.get('primary', False),
                    'access_role': calendar.get('accessRole', '')
                })
            
            logger.info(f"Found {len(calendars)} calendars")
            return calendars
            
        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            return []
    
    def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
        sync_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get events from calendar
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time filter
            time_max: End time filter
            max_results: Maximum number of events
            sync_cache: Whether to sync with local cache
        
        Returns:
            List of event dictionaries
        """
        try:
            service = self.get_service()
            
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.now()
            if not time_max:
                time_max = time_min + timedelta(days=30)
            
            # Fetch events from Google Calendar
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                event_data = self._parse_event(event, calendar_id)
                events.append(event_data)
                
                # Sync to cache
                if sync_cache:
                    self._sync_event_to_cache(event_data)
            
            logger.info(f"Retrieved {len(events)} events from {calendar_id}")
            return events
            
        except HttpError as e:
            logger.error(f"Error getting events: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary'
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new calendar event
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            attendees: List of attendee emails
            calendar_id: Calendar ID
        
        Returns:
            Created event data or None if failed
        """
        try:
            service = self.get_service()
            
            event_body = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event_body['description'] = description
            
            if location:
                event_body['location'] = location
            
            if attendees:
                event_body['attendees'] = [{'email': email} for email in attendees]
            
            event = service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()
            
            event_data = self._parse_event(event, calendar_id)
            
            # Sync to cache
            self._sync_event_to_cache(event_data)
            
            logger.info(f"Created event: {summary}")
            return event_data
            
        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def update_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        **updates
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing event
        
        Args:
            event_id: Event ID
            calendar_id: Calendar ID
            **updates: Fields to update
        
        Returns:
            Updated event data or None if failed
        """
        try:
            service = self.get_service()
            
            # Get existing event
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Apply updates
            if 'summary' in updates:
                event['summary'] = updates['summary']
            if 'description' in updates:
                event['description'] = updates['description']
            if 'location' in updates:
                event['location'] = updates['location']
            if 'start_time' in updates:
                event['start'] = {
                    'dateTime': updates['start_time'].isoformat(),
                    'timeZone': 'UTC'
                }
            if 'end_time' in updates:
                event['end'] = {
                    'dateTime': updates['end_time'].isoformat(),
                    'timeZone': 'UTC'
                }
            
            # Update event
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            event_data = self._parse_event(updated_event, calendar_id)
            
            # Sync to cache
            self._sync_event_to_cache(event_data)
            
            logger.info(f"Updated event: {event_id}")
            return event_data
            
        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            return None
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Delete an event
        
        Args:
            event_id: Event ID
            calendar_id: Calendar ID
        
        Returns:
            True if deleted successfully
        """
        try:
            service = self.get_service()
            
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Remove from cache
            self.event_store.delete_event(event_id)
            
            logger.info(f"Deleted event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    def check_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = 'primary'
    ) -> bool:
        """
        Check if a time slot is available
        
        Args:
            start_time: Start of time slot
            end_time: End of time slot
            calendar_id: Calendar ID
        
        Returns:
            True if time slot is free
        """
        events = self.get_events(
            calendar_id=calendar_id,
            time_min=start_time,
            time_max=end_time,
            sync_cache=False
        )
        
        return len(events) == 0
    
    def find_free_slots(
        self,
        date: datetime,
        duration_minutes: int = 60,
        calendar_id: str = 'primary',
        working_hours: tuple = (9, 17)
    ) -> List[Dict[str, datetime]]:
        """
        Find free time slots on a given date
        
        Args:
            date: Date to check
            duration_minutes: Required duration in minutes
            calendar_id: Calendar ID
            working_hours: Tuple of (start_hour, end_hour)
        
        Returns:
            List of free slots with start and end times
        """
        start_hour, end_hour = working_hours
        
        # Get events for the day
        day_start = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        day_end = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
        events = self.get_events(
            calendar_id=calendar_id,
            time_min=day_start,
            time_max=day_end,
            max_results=100,
            sync_cache=False
        )
        
        # Sort events by start time
        events.sort(key=lambda e: e['start_time'])
        
        # Find gaps
        free_slots = []
        current_time = day_start
        
        for event in events:
            event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))
            
            # Check if there's a gap before this event
            if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                free_slots.append({
                    'start': current_time,
                    'end': event_start
                })
            
            current_time = max(current_time, event_end)
        
        # Check if there's time after the last event
        if (day_end - current_time).total_seconds() >= duration_minutes * 60:
            free_slots.append({
                'start': current_time,
                'end': day_end
            })
        
        return free_slots
    
    def _parse_event(self, event: Dict, calendar_id: str) -> Dict[str, Any]:
        """Parse Google Calendar event to standard format"""
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        return {
            'id': event['id'],
            'calendar_id': calendar_id,
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'start_time': start,
            'end_time': end,
            'attendees': [a.get('email') for a in event.get('attendees', [])],
            'status': event.get('status', 'confirmed'),
            'is_all_day': 'date' in event['start'],
            'html_link': event.get('htmlLink', '')
        }
    
    def _sync_event_to_cache(self, event_data: Dict[str, Any]):
        """Sync event to local cache"""
        try:
            start_time = datetime.fromisoformat(
                event_data['start_time'].replace('Z', '+00:00')
            )
            end_time = datetime.fromisoformat(
                event_data['end_time'].replace('Z', '+00:00')
            )
            
            self.event_store.add_event(
                event_id=event_data['id'],
                calendar_id=event_data['calendar_id'],
                summary=event_data['summary'],
                start_time=start_time,
                end_time=end_time,
                description=event_data.get('description'),
                location=event_data.get('location'),
                attendees=event_data.get('attendees'),
                status=event_data.get('status', 'confirmed'),
                is_all_day=event_data.get('is_all_day', False)
            )
        except Exception as e:
            logger.error(f"Error syncing event to cache: {e}")

# Made with Bob
