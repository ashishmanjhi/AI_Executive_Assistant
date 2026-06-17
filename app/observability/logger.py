"""
Structured Logger
Enhanced logging with context and structured data
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
import traceback
import uuid

# Log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class StructuredLogger:
    """
    Structured logger with context and database storage
    
    Provides enhanced logging with structured data, context tracking,
    and persistent storage for analysis.
    """
    
    def __init__(
        self,
        name: str,
        db_path: str = "data/logs.db",
        level: int = INFO
    ):
        """Initialize structured logger"""
        self.name = name
        self.db_path = db_path
        self.level = level
        
        # Create standard logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Context storage
        self._context = {}
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Application logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS application_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                message TEXT NOT NULL,
                context TEXT,
                user_id TEXT,
                request_id TEXT,
                trace_id TEXT,
                exception TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_level 
            ON application_logs(level)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON application_logs(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_logger_name 
            ON application_logs(logger_name)
        """)
        
        conn.commit()
        conn.close()
    
    def set_context(self, **kwargs):
        """Set context for subsequent log messages"""
        self._context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self._context = {}
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(WARNING, message, **kwargs)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message"""
        if exception:
            kwargs['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        self._log(ERROR, message, **kwargs)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log critical message"""
        if exception:
            kwargs['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        self._log(CRITICAL, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method"""
        # Merge context with kwargs
        log_data = {**self._context, **kwargs}
        
        # Log to standard logger
        level_name = logging.getLevelName(level)
        self.logger.log(level, f"{message} | {json.dumps(log_data)}")
        
        # Store in database
        self._store_log(level_name, message, log_data)
    
    def _store_log(self, level: str, message: str, context: Dict[str, Any]):
        """Store log in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract special fields
            user_id = context.pop('user_id', None)
            request_id = context.pop('request_id', None)
            trace_id = context.pop('trace_id', None)
            exception = context.pop('exception', None)
            
            cursor.execute("""
                INSERT INTO application_logs
                (level, logger_name, message, context, user_id, request_id, trace_id, exception)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                level,
                self.name,
                message,
                json.dumps(context) if context else None,
                user_id,
                request_id,
                trace_id,
                json.dumps(exception) if exception else None
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error storing log: {e}")
    
    def query_logs(
        self,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        Query logs from database
        
        Args:
            level: Filter by log level
            start_time: Filter by start time
            end_time: Filter by end time
            user_id: Filter by user ID
            limit: Maximum number of results
        
        Returns:
            List of log records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT level, logger_name, message, context, user_id, 
                   request_id, trace_id, exception, timestamp
            FROM application_logs
            WHERE 1=1
        """
        params = []
        
        if level:
            query += " AND level = ?"
            params.append(level)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                "level": row[0],
                "logger_name": row[1],
                "message": row[2],
                "context": json.loads(row[3]) if row[3] else {},
                "user_id": row[4],
                "request_id": row[5],
                "trace_id": row[6],
                "exception": json.loads(row[7]) if row[7] else None,
                "timestamp": row[8]
            })
        
        return logs
    
    def get_error_count(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """Get count of error and critical logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) FROM application_logs
            WHERE level IN ('ERROR', 'CRITICAL')
        """
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def clear_old_logs(self, days: int = 30) -> int:
        """
        Clear logs older than specified days
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of logs deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = cutoff.replace(day=cutoff.day - days)
        
        cursor.execute(
            "DELETE FROM application_logs WHERE timestamp < ?",
            (cutoff.isoformat(),)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted


def get_logger(name: str, level: int = INFO) -> StructuredLogger:
    """Get or create a structured logger"""
    return StructuredLogger(name, level=level)


# Request ID context manager
class RequestContext:
    """Context manager for request tracking"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.request_id = str(uuid.uuid4())
    
    def __enter__(self):
        self.logger.set_context(request_id=self.request_id)
        return self.request_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.clear_context()

# Made with Bob
