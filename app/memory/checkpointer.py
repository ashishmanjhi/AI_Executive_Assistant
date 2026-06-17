"""
LangGraph Checkpointer Integration
Enables persistent conversation state across sessions
"""

from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # type: ignore
from pathlib import Path
from typing import Optional
import sqlite3
import aiosqlite  # type: ignore


class PersistentCheckpointer:
    """Manages LangGraph checkpoints for conversation continuity"""
    
    def __init__(self, db_path: str = "data/checkpoints.db"):
        """Initialize checkpointer with SQLite database"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize checkpointer and connection
        self.checkpointer = None
        self._conn = None
    
    def get_checkpointer(self) -> SqliteSaver:
        """Get or create the checkpointer instance"""
        if self.checkpointer is None:
            # Create connection and enter the context manager
            self._conn = sqlite3.connect(self.db_path)
            self.checkpointer = SqliteSaver(self._conn)
        return self.checkpointer
    
    def close(self):
        """Close the database connection"""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            self.checkpointer = None
    
    async def get_async_checkpointer(self) -> AsyncSqliteSaver:
        """Get async checkpointer for async workflows"""
        conn = await aiosqlite.connect(self.db_path)
        return AsyncSqliteSaver(conn)
    
    def clear_checkpoints(self, thread_id: Optional[str] = None):
        """Clear checkpoints for a specific thread or all threads"""
        # Note: SqliteSaver doesn't have a built-in clear method
        # We'll need to manually delete from the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if thread_id:
            cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        else:
            cursor.execute("DELETE FROM checkpoints")
        
        conn.commit()
        conn.close()


# Global checkpointer instance
_checkpointer_instance: Optional[PersistentCheckpointer] = None


def get_checkpointer(db_path: str = "data/checkpoints.db") -> SqliteSaver:
    """Get global checkpointer instance"""
    global _checkpointer_instance
    
    if _checkpointer_instance is None:
        _checkpointer_instance = PersistentCheckpointer(db_path)
    
    return _checkpointer_instance.get_checkpointer()

# Made with Bob
