"""
Test Calendar Authentication and Event Fetching
Quick script to verify Google Calendar integration
"""

import sys
from datetime import datetime, timedelta
from app.calendar.calendar_manager import CalendarManager

def test_calendar():
    """Test calendar authentication and basic operations"""
    
    print("=" * 60)
    print("Testing Google Calendar Integration")
    print("=" * 60)
    
    # Initialize manager
    print("\n1. Initializing CalendarManager...")
    manager = CalendarManager()
    print("   [OK] Manager initialized")
    
    # Authenticate
    print("\n2. Authenticating with Google Calendar...")
    try:
        success = manager.authenticate()
        if success:
            print("   [OK] Authentication successful")
        else:
            print("   [FAIL] Authentication failed")
            return
    except Exception as e:
        print(f"   [ERROR] Authentication error: {e}")
        return
    
    # List calendars
    print("\n3. Listing calendars...")
    try:
        calendars = manager.list_calendars()
        print(f"   [OK] Found {len(calendars)} calendar(s):")
        for cal in calendars:
            primary = " (PRIMARY)" if cal.get('primary') else ""
            print(f"      - {cal['summary']}{primary}")
            print(f"        ID: {cal['id']}")
    except Exception as e:
        print(f"   [ERROR] Error listing calendars: {e}")
        import traceback
        traceback.print_exc()
    
    # Get upcoming events
    print("\n4. Fetching upcoming events (next 30 days)...")
    try:
        time_min = datetime.now()
        time_max = time_min + timedelta(days=30)
        
        print(f"   Searching from: {time_min.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Searching to:   {time_max.strftime('%Y-%m-%d %H:%M')}")
        
        events = manager.get_events(
            time_min=time_min,
            time_max=time_max,
            max_results=50
        )
        
        if not events:
            print("   [WARN] No events found")
            print("   Note: Check your Google Calendar to verify you have events scheduled")
        else:
            print(f"   [OK] Found {len(events)} event(s):")
            for i, event in enumerate(events[:10], 1):  # Show first 10
                print(f"\n      {i}. {event['summary']}")
                print(f"         When: {event['start_time']}")
                if event.get('location'):
                    print(f"         Where: {event['location']}")
                if event.get('attendees'):
                    print(f"         Attendees: {len(event['attendees'])} person(s)")
            
            if len(events) > 10:
                print(f"\n      ... and {len(events) - 10} more events")
    
    except Exception as e:
        print(f"   [ERROR] Error fetching events: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_calendar()

# Made with Bob
