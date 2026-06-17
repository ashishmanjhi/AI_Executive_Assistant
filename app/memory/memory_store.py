"""
Persistent Memory Store for AI Executive Assistant
Manages conversation history, user preferences, and long-term memory
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class MemoryStore:
    """SQLite-based persistent memory storage"""
    
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize memory store with SQLite database"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON conversations(timestamp)
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Episodic memory (specific events/interactions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                context TEXT,
                importance INTEGER DEFAULT 5
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON episodic_memory(event_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance ON episodic_memory(importance)
        """)
        
        # Semantic memory (facts, knowledge)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON semantic_memory(category)
        """)
        
        # Procedural memory (learned patterns, workflows)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS procedural_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT UNIQUE NOT NULL,
                pattern_data TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_used DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==================== Conversation History ====================
    
    def add_conversation_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add a message to conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO conversations (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, content, metadata_json))
        
        message_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, role, content, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                "id": row[0],
                "timestamp": row[1],
                "role": row[2],
                "content": row[3],
                "metadata": json.loads(row[4]) if row[4] else None
            })
        
        return list(reversed(messages))  # Return in chronological order
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all conversation sessions with summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                session_id,
                MIN(timestamp) as first_message,
                MAX(timestamp) as last_message,
                COUNT(*) as message_count
            FROM conversations
            GROUP BY session_id
            ORDER BY last_message DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                "session_id": row[0],
                "first_message": row[1],
                "last_message": row[2],
                "message_count": row[3]
            })
        
        return sessions
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
    
    # ==================== User Preferences ====================
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        value_json = json.dumps(value)
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value_json))
        
        conn.commit()
        conn.close()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return default
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key, value FROM user_preferences")
        rows = cursor.fetchall()
        conn.close()
        
        preferences = {}
        for row in rows:
            preferences[row[0]] = json.loads(row[1])
        
        return preferences
    
    # ==================== Episodic Memory ====================
    
    def add_episodic_memory(
        self,
        event_type: str,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        importance: int = 5
    ) -> int:
        """Add an episodic memory (specific event)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context_json = json.dumps(context) if context else None
        
        cursor.execute("""
            INSERT INTO episodic_memory (event_type, description, context, importance)
            VALUES (?, ?, ?, ?)
        """, (event_type, description, context_json, importance))
        
        memory_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        
        return memory_id
    
    def get_episodic_memories(
        self,
        event_type: Optional[str] = None,
        min_importance: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve episodic memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, event_type, description, context, importance
            FROM episodic_memory
            WHERE importance >= ?
        """
        params: List[Any] = [min_importance]
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memories.append({
                "id": row[0],
                "timestamp": row[1],
                "event_type": row[2],
                "description": row[3],
                "context": json.loads(row[4]) if row[4] else None,
                "importance": row[5]
            })
        
        return memories
    
    # ==================== Semantic Memory ====================
    
    def add_semantic_memory(
        self,
        category: str,
        key: str,
        value: Any,
        confidence: float = 1.0,
        source: Optional[str] = None
    ):
        """Add or update semantic memory (facts, knowledge)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        value_json = json.dumps(value)
        
        cursor.execute("""
            INSERT OR REPLACE INTO semantic_memory 
            (category, key, value, confidence, source, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (category, key, value_json, confidence, source))
        
        conn.commit()
        conn.close()
    
    def get_semantic_memory(
        self,
        category: str,
        key: Optional[str] = None
    ) -> Optional[Any]:
        """Retrieve semantic memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if key:
            cursor.execute("""
                SELECT value FROM semantic_memory
                WHERE category = ? AND key = ?
            """, (category, key))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return json.loads(row[0])
            return None
        else:
            cursor.execute("""
                SELECT key, value, confidence, source
                FROM semantic_memory
                WHERE category = ?
            """, (category,))
            rows = cursor.fetchall()
            conn.close()
            
            memories = {}
            for row in rows:
                memories[row[0]] = {
                    "value": json.loads(row[1]),
                    "confidence": row[2],
                    "source": row[3]
                }
            return memories
    
    # ==================== Procedural Memory ====================
    
    def add_procedural_memory(
        self,
        pattern_name: str,
        pattern_data: Dict[str, Any]
    ):
        """Add or update procedural memory (learned patterns)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pattern_json = json.dumps(pattern_data)
        
        cursor.execute("""
            INSERT OR REPLACE INTO procedural_memory (pattern_name, pattern_data)
            VALUES (?, ?)
        """, (pattern_name, pattern_json))
        
        conn.commit()
        conn.close()
    
    def get_procedural_memory(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve procedural memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_data, usage_count, success_rate, last_used
            FROM procedural_memory
            WHERE pattern_name = ?
        """, (pattern_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "pattern_data": json.loads(row[0]),
                "usage_count": row[1],
                "success_rate": row[2],
                "last_used": row[3]
            }
        return None
    
    def update_procedural_usage(
        self,
        pattern_name: str,
        success: bool
    ):
        """Update usage statistics for a procedural memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current stats
        cursor.execute("""
            SELECT usage_count, success_rate
            FROM procedural_memory
            WHERE pattern_name = ?
        """, (pattern_name,))
        
        row = cursor.fetchone()
        if row:
            usage_count = row[0] + 1
            old_success_rate = row[1]
            
            # Calculate new success rate
            new_success_rate = (old_success_rate * row[0] + (1 if success else 0)) / usage_count
            
            cursor.execute("""
                UPDATE procedural_memory
                SET usage_count = ?,
                    success_rate = ?,
                    last_used = CURRENT_TIMESTAMP
                WHERE pattern_name = ?
            """, (usage_count, new_success_rate, pattern_name))
            
            conn.commit()
        
        conn.close()
    
    # ==================== Utility Methods ====================
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Conversation stats
        cursor.execute("SELECT COUNT(*) FROM conversations")
        stats["total_messages"] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
        stats["total_sessions"] = cursor.fetchone()[0]
        
        # Preference stats
        cursor.execute("SELECT COUNT(*) FROM user_preferences")
        stats["total_preferences"] = cursor.fetchone()[0]
        
        # Episodic memory stats
        cursor.execute("SELECT COUNT(*) FROM episodic_memory")
        stats["total_episodic_memories"] = cursor.fetchone()[0]
        
        # Semantic memory stats
        cursor.execute("SELECT COUNT(*) FROM semantic_memory")
        stats["total_semantic_memories"] = cursor.fetchone()[0]
        
        # Procedural memory stats
        cursor.execute("SELECT COUNT(*) FROM procedural_memory")
        stats["total_procedural_patterns"] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def clear_all_memory(self):
        """Clear all memory (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations")
        cursor.execute("DELETE FROM user_preferences")
        cursor.execute("DELETE FROM episodic_memory")
        cursor.execute("DELETE FROM semantic_memory")
        cursor.execute("DELETE FROM procedural_memory")
        
        conn.commit()
        conn.close()

# Made with Bob
