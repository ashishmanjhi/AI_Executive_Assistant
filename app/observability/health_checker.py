"""
Health Checker
System health monitoring and checks
"""

import sqlite3
import logging
import psutil
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """
    System health checker
    
    Monitors system health including database connections,
    disk space, memory usage, and custom health checks.
    """
    
    def __init__(self, db_path: str = "data/health_checks.db"):
        """Initialize health checker"""
        self.db_path = db_path
        self._checks = {}
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Register default checks
        self._register_default_checks()
        
        logger.info(f"Health checker initialized at {db_path}")
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Health checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_name TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT,
                checked_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_check_name 
            ON health_checks(check_name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON health_checks(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_checked_at 
            ON health_checks(checked_at)
        """)
        
        conn.commit()
        conn.close()
    
    def register_check(self, name: str, check_func: Callable[[], Dict[str, Any]]):
        """
        Register a custom health check
        
        Args:
            name: Check name
            check_func: Function that returns health check result
                       Should return dict with 'status', 'message', 'details'
        """
        self._checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    def _register_default_checks(self):
        """Register default health checks"""
        self.register_check("disk_space", self._check_disk_space)
        self.register_check("memory", self._check_memory)
        self.register_check("database", self._check_database)
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """
        Run a specific health check
        
        Args:
            name: Check name
        
        Returns:
            Health check result
        """
        if name not in self._checks:
            return {
                "check_name": name,
                "status": HealthStatus.UNHEALTHY,
                "message": f"Unknown health check: {name}",
                "details": {}
            }
        
        try:
            result = self._checks[name]()
            result["check_name"] = name
            result["checked_at"] = datetime.now().isoformat()
            
            # Store result
            self._store_check(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error running health check {name}: {e}")
            result = {
                "check_name": name,
                "status": HealthStatus.UNHEALTHY,
                "message": f"Check failed: {str(e)}",
                "details": {},
                "checked_at": datetime.now().isoformat()
            }
            self._store_check(result)
            return result
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all registered health checks
        
        Returns:
            Overall health status and individual check results
        """
        results = {}
        overall_status = HealthStatus.HEALTHY
        
        for name in self._checks.keys():
            result = self.run_check(name)
            results[name] = result
            
            # Determine overall status
            if result["status"] == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result["status"] == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_health_history(
        self,
        check_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get health check history
        
        Args:
            check_name: Filter by check name
            limit: Maximum number of results
        
        Returns:
            List of health check records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT check_name, status, message, details, checked_at
            FROM health_checks
            WHERE 1=1
        """
        params = []
        
        if check_name:
            query += " AND check_name = ?"
            params.append(check_name)
        
        query += " ORDER BY checked_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "check_name": row[0],
                "status": row[1],
                "message": row[2],
                "details": row[3],
                "checked_at": row[4]
            })
        
        return history
    
    def _store_check(self, result: Dict[str, Any]):
        """Store health check result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO health_checks (check_name, status, message, details)
                VALUES (?, ?, ?, ?)
            """, (
                result["check_name"],
                result["status"],
                result.get("message", ""),
                str(result.get("details", {}))
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing health check: {e}")
    
    # Default health checks
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            percent_used = disk.percent
            
            if percent_used > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Disk space critical: {percent_used}% used"
            elif percent_used > 80:
                status = HealthStatus.DEGRADED
                message = f"Disk space warning: {percent_used}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {percent_used}% used"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "percent_used": percent_used
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Failed to check disk space: {str(e)}",
                "details": {}
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            
            if percent_used > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Memory critical: {percent_used}% used"
            elif percent_used > 80:
                status = HealthStatus.DEGRADED
                message = f"Memory warning: {percent_used}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory OK: {percent_used}% used"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "percent_used": percent_used
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Failed to check memory: {str(e)}",
                "details": {}
            }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Try to connect to main databases
            databases = [
                "data/memory.db",
                "data/jobs.db",
                "data/plans.db",
                "data/calendar_events.db"
            ]
            
            accessible = 0
            total = len(databases)
            
            for db_path in databases:
                if os.path.exists(db_path):
                    try:
                        conn = sqlite3.connect(db_path)
                        conn.execute("SELECT 1")
                        conn.close()
                        accessible += 1
                    except:
                        pass
            
            if accessible == total:
                status = HealthStatus.HEALTHY
                message = f"All {total} databases accessible"
            elif accessible > 0:
                status = HealthStatus.DEGRADED
                message = f"{accessible}/{total} databases accessible"
            else:
                status = HealthStatus.UNHEALTHY
                message = "No databases accessible"
            
            return {
                "status": status,
                "message": message,
                "details": {
                    "total_databases": total,
                    "accessible_databases": accessible
                }
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"Failed to check databases: {str(e)}",
                "details": {}
            }


# Global health checker instance
_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get or create global health checker"""
    global _health_checker
    
    if _health_checker is None:
        _health_checker = HealthChecker()
    
    return _health_checker

# Made with Bob
