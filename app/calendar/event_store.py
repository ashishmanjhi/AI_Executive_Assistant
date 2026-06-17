"""
Event Store
SQLite-based storage for calendar events cache
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class EventStore:
    """
    SQLite-based storage for calendar events
    
    Caches Google Calendar events locally for faster access
    and offline capability.
    """
    
    def __init__(self, db_path: str = "data/calendar_events.db"):
        """Initialize event store"""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Event store initialized at {db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calendar events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
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
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_calendar_id 
            ON calendar_events(calendar_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_start_time 
            ON calendar_events(start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_end_time 
            ON calendar_events(end_time)
        """)
        
        conn.commit()
        conn.close()
    
    def add_event(
        self,
        event_id: str,
        calendar_id: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        status: str = "confirmed",
        is_all_day: bool = False,
        recurrence_rule: Optional[str] = None
    ) -> bool:
        """Add or update an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO calendar_events
                (id, calendar_id, summary, description, location, start_time, end_time,
                 attendees, status, is_all_day, recurrence_rule, updated_at, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                event_id,
                calendar_id,
                summary,
                description,
                location,
                start_time.isoformat(),
                end_time.isoformat(),
                json.dumps(attendees) if attendees else None,
                status,
                1 if is_all_day else 0,
                recurrence_rule
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding event: {e}")
            return False
        finally:
            conn.close()
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, calendar_id, summary, description, location, start_time, end_time,
                   attendees, status, is_all_day, recurrence_rule, created_at, updated_at
            FROM calendar_events
            WHERE id = ?
        """, (event_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "calendar_id": row[1],
            "summary": row[2],
            "description": row[3],
            "location": row[4],
            "start_time": row[5],
            "end_time": row[6],
            "attendees": json.loads(row[7]) if row[7] else [],
            "status": row[8],
            "is_all_day": bool(row[9]),
            "recurrence_rule": row[10],
            "created_at": row[11],
            "updated_at": row[12]
        }
    
    def get_events_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events within a time range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, calendar_id, summary, description, location, start_time, end_time,
                   attendees, status, is_all_day, recurrence_rule
            FROM calendar_events
            WHERE start_time >= ? AND end_time <= ?
        """
        params = [start_time.isoformat(), end_time.isoformat()]
        
        if calendar_id:
            query += " AND calendar_id = ?"
            params.append(calendar_id)
        
        query += " ORDER BY start_time"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                "id": row[0],
                "calendar_id": row[1],
                "summary": row[2],
                "description": row[3],
                "location": row[4],
                "start_time": row[5],
                "end_time": row[6],
                "attendees": json.loads(row[7]) if row[7] else [],
                "status": row[8],
                "is_all_day": bool(row[9]),
                "recurrence_rule": row[10]
            })
        
        return events
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Error deleting event: {e}")
            return False
        finally:
            conn.close()
    
    def clear_calendar(self, calendar_id: str) -> int:
        """Clear all events for a calendar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM calendar_events WHERE calendar_id = ?", (calendar_id,))
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Error clearing calendar: {e}")
            return 0
        finally:
            conn.close()
    
    def get_event_count(self, calendar_id: Optional[str] = None) -> int:
        """Get total number of cached events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if calendar_id:
            cursor.execute(
                "SELECT COUNT(*) FROM calendar_events WHERE calendar_id = ?",
                (calendar_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM calendar_events")
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_upcoming_events(
        self,
        limit: int = 10,
        calendar_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get upcoming events"""
        now = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, calendar_id, summary, description, location, start_time, end_time,
                   attendees, status, is_all_day, recurrence_rule
            FROM calendar_events
            WHERE start_time >= ?
        """
        params = [now.isoformat()]
        
        if calendar_id:
            query += " AND calendar_id = ?"
            params.append(calendar_id)
        
        query += " ORDER BY start_time LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                "id": row[0],
                "calendar_id": row[1],
                "summary": row[2],
                "description": row[3],
                "location": row[4],
                "start_time": row[5],
                "end_time": row[6],
                "attendees": json.loads(row[7]) if row[7] else [],
                "status": row[8],
                "is_all_day": bool(row[9]),
                "recurrence_rule": row[10]
            })
        
        return events

# Made with Bob
