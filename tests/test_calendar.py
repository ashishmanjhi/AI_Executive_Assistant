"""
Test Suite for Calendar Integration
Tests calendar manager, event store, and tools
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.calendar import CalendarManager, EventStore


class TestEventStore(unittest.TestCase):
    """Test event storage functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.db_path = "test_events.db"
        self.store = EventStore(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_add_event(self):
        """Test adding an event"""
        event_id = "test_event_1"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        success = self.store.add_event(
            event_id=event_id,
            calendar_id="primary",
            summary="Test Meeting",
            start_time=start_time,
            end_time=end_time,
            description="Test description",
            location="Test location"
        )
        
        self.assertTrue(success)
        
        # Verify event was added
        event = self.store.get_event(event_id)
        self.assertIsNotNone(event)
        assert event is not None  # Type narrowing for type checker
        self.assertEqual(event['summary'], "Test Meeting")
        self.assertEqual(event['location'], "Test location")
    
    def test_get_events_in_range(self):
        """Test getting events in a time range"""
        now = datetime.now()
        
        # Add multiple events
        for i in range(3):
            start_time = now + timedelta(hours=i)
            end_time = start_time + timedelta(hours=1)
            
            self.store.add_event(
                event_id=f"event_{i}",
                calendar_id="primary",
                summary=f"Meeting {i}",
                start_time=start_time,
                end_time=end_time
            )
        
        # Get events in range
        events = self.store.get_events_in_range(
            start_time=now,
            end_time=now + timedelta(hours=4)
        )
        
        self.assertEqual(len(events), 3)
    
    def test_delete_event(self):
        """Test deleting an event"""
        event_id = "test_delete"
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=1)
        
        self.store.add_event(
            event_id=event_id,
            calendar_id="primary",
            summary="To Delete",
            start_time=start_time,
            end_time=end_time
        )
        
        # Delete event
        success = self.store.delete_event(event_id)
        self.assertTrue(success)
        
        # Verify deletion
        event = self.store.get_event(event_id)
        self.assertIsNone(event)
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events"""
        now = datetime.now()
        
        # Add past event
        past_start = now - timedelta(hours=2)
        past_end = past_start + timedelta(hours=1)
        self.store.add_event(
            event_id="past_event",
            calendar_id="primary",
            summary="Past Meeting",
            start_time=past_start,
            end_time=past_end
        )
        
        # Add future events
        for i in range(2):
            start_time = now + timedelta(hours=i+1)
            end_time = start_time + timedelta(hours=1)
            
            self.store.add_event(
                event_id=f"future_{i}",
                calendar_id="primary",
                summary=f"Future Meeting {i}",
                start_time=start_time,
                end_time=end_time
            )
        
        # Get upcoming events
        upcoming = self.store.get_upcoming_events(limit=10)
        
        # Should only get future events
        self.assertEqual(len(upcoming), 2)
        self.assertTrue(all('Future' in e['summary'] for e in upcoming))
    
    def test_event_count(self):
        """Test counting events"""
        # Initially empty
        count = self.store.get_event_count()
        self.assertEqual(count, 0)
        
        # Add events
        now = datetime.now()
        for i in range(5):
            start_time = now + timedelta(hours=i)
            end_time = start_time + timedelta(hours=1)
            
            self.store.add_event(
                event_id=f"count_{i}",
                calendar_id="primary",
                summary=f"Event {i}",
                start_time=start_time,
                end_time=end_time
            )
        
        # Check count
        count = self.store.get_event_count()
        self.assertEqual(count, 5)


class TestCalendarManager(unittest.TestCase):
    """Test calendar manager functionality"""
    
    def setUp(self):
        """Set up test manager"""
        self.db_path = "test_calendar.db"
        self.store = EventStore(self.db_path)
        self.manager = CalendarManager(event_store=self.store)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_manager_initialization(self):
        """Test manager initializes correctly"""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.event_store)
    
    def test_parse_event(self):
        """Test event parsing"""
        google_event = {
            'id': 'test123',
            'summary': 'Test Meeting',
            'description': 'Test description',
            'location': 'Test location',
            'start': {'dateTime': '2024-01-01T10:00:00Z'},
            'end': {'dateTime': '2024-01-01T11:00:00Z'},
            'status': 'confirmed',
            'attendees': [
                {'email': 'user1@example.com'},
                {'email': 'user2@example.com'}
            ],
            'htmlLink': 'https://calendar.google.com/event?eid=test123'
        }
        
        parsed = self.manager._parse_event(google_event, 'primary')
        
        self.assertEqual(parsed['id'], 'test123')
        self.assertEqual(parsed['summary'], 'Test Meeting')
        self.assertEqual(parsed['calendar_id'], 'primary')
        self.assertEqual(len(parsed['attendees']), 2)
        self.assertFalse(parsed['is_all_day'])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEventStore))
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

# Made with Bob
