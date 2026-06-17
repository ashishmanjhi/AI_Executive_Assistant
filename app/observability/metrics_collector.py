"""
Metrics Collector
Collects and stores application metrics
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and stores application metrics
    
    Tracks counters, gauges, and histograms for monitoring
    application performance and behavior.
    """
    
    def __init__(self, db_path: str = "data/metrics.db"):
        """Initialize metrics collector"""
        self.db_path = db_path
        self._lock = threading.Lock()
        
        # In-memory metrics for fast access
        self._counters = defaultdict(float)
        self._gauges = defaultdict(float)
        self._histograms = defaultdict(list)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        logger.info(f"Metrics collector initialized at {db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                labels TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metric_name 
            ON metrics(metric_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON metrics(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metric_type 
            ON metrics(metric_type)
        """)
        
        conn.commit()
        conn.close()
    
    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Increment a counter metric
        
        Args:
            name: Metric name
            value: Amount to increment (default: 1.0)
            labels: Optional labels for the metric
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            
            # Persist to database
            self._record_metric(name, "counter", self._counters[key], labels)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Set a gauge metric
        
        Args:
            name: Metric name
            value: Current value
            labels: Optional labels for the metric
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            
            # Persist to database
            self._record_metric(name, "gauge", value, labels)
    
    def observe_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Observe a value for histogram metric
        
        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels for the metric
        """
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
            
            # Keep only last 1000 values
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
            
            # Persist to database
            self._record_metric(name, "histogram", value, labels)
    
    def get_counter(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Get current counter value"""
        with self._lock:
            key = self._make_key(name, labels)
            return self._counters.get(key, 0.0)
    
    def get_gauge(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Get current gauge value"""
        with self._lock:
            key = self._make_key(name, labels)
            return self._gauges.get(key, 0.0)
    
    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """Get histogram statistics"""
        with self._lock:
            key = self._make_key(name, labels)
            values = self._histograms.get(key, [])
            
            if not values:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "avg": 0.0
                }
            
            return {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    k: self.get_histogram_stats(k.split(":")[0])
                    for k in self._histograms.keys()
                }
            }
    
    def query_metrics(
        self,
        metric_name: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query metrics from database
        
        Args:
            metric_name: Filter by metric name
            metric_type: Filter by metric type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of results
        
        Returns:
            List of metric records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT metric_name, metric_type, value, labels, timestamp FROM metrics WHERE 1=1"
        params = []
        
        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)
        
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        metrics = []
        for row in rows:
            metrics.append({
                "metric_name": row[0],
                "metric_type": row[1],
                "value": row[2],
                "labels": json.loads(row[3]) if row[3] else {},
                "timestamp": row[4]
            })
        
        return metrics
    
    def get_metric_summary(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a metric
        
        Args:
            metric_name: Metric name
            start_time: Start time filter
            end_time: End time filter
        
        Returns:
            Summary statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                COUNT(*) as count,
                AVG(value) as avg,
                MIN(value) as min,
                MAX(value) as max,
                SUM(value) as sum
            FROM metrics
            WHERE metric_name = ?
        """
        params = [metric_name]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        return {
            "metric_name": metric_name,
            "count": row[0] or 0,
            "avg": row[1] or 0.0,
            "min": row[2] or 0.0,
            "max": row[3] or 0.0,
            "sum": row[4] or 0.0
        }
    
    def clear_old_metrics(self, days: int = 30) -> int:
        """
        Clear metrics older than specified days
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of metrics deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = cutoff.replace(day=cutoff.day - days)
        
        cursor.execute(
            "DELETE FROM metrics WHERE timestamp < ?",
            (cutoff.isoformat(),)
        )
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleared {deleted} old metrics")
        return deleted
    
    def _record_metric(
        self,
        name: str,
        metric_type: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Record metric to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (metric_name, metric_type, value, labels)
                VALUES (?, ?, ?, ?)
            """, (
                name,
                metric_type,
                value,
                json.dumps(labels) if labels else None
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording metric: {e}")
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Make a unique key for a metric"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}"


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector

# Made with Bob
