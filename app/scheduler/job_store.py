"""
Job Store for Persistent Scheduled Jobs
Stores job configurations and execution history in SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class JobStore:
    """SQLite-based storage for scheduled jobs"""
    
    def __init__(self, db_path: str = "data/scheduler.db"):
        """Initialize job store with SQLite database"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                job_type TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_config TEXT NOT NULL,
                job_config TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_run DATETIME,
                next_run DATETIME
            )
        """)
        
        # Job execution history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                started_at DATETIME NOT NULL,
                completed_at DATETIME,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_executions_job_id 
            ON job_executions(job_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_job_executions_started_at 
            ON job_executions(started_at)
        """)
        
        conn.commit()
        conn.close()
    
    def add_job(
        self,
        job_id: str,
        name: str,
        job_type: str,
        schedule_type: str,
        schedule_config: Dict[str, Any],
        description: Optional[str] = None,
        job_config: Optional[Dict[str, Any]] = None,
        enabled: bool = True
    ) -> bool:
        """Add a new job to the store"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO jobs 
                (id, name, description, job_type, schedule_type, schedule_config, job_config, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                name,
                description,
                job_type,
                schedule_type,
                json.dumps(schedule_config),
                json.dumps(job_config) if job_config else None,
                enabled
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def update_job(
        self,
        job_id: str,
        **kwargs
    ) -> bool:
        """Update job configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['name', 'description', 'job_type', 'schedule_type', 'enabled']:
                update_fields.append(f"{key} = ?")
                values.append(value)
            elif key in ['schedule_config', 'job_config']:
                update_fields.append(f"{key} = ?")
                values.append(json.dumps(value) if value else None)
        
        if not update_fields:
            conn.close()
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(job_id)
        
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, job_type, schedule_type, schedule_config,
                   job_config, enabled, created_at, updated_at, last_run, next_run
            FROM jobs
            WHERE id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "job_type": row[3],
            "schedule_type": row[4],
            "schedule_config": json.loads(row[5]),
            "job_config": json.loads(row[6]) if row[6] else None,
            "enabled": bool(row[7]),
            "created_at": row[8],
            "updated_at": row[9],
            "last_run": row[10],
            "next_run": row[11]
        }
    
    def get_all_jobs(self, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, description, job_type, schedule_type, schedule_config,
                   job_config, enabled, created_at, updated_at, last_run, next_run
            FROM jobs
        """
        
        if enabled_only:
            query += " WHERE enabled = 1"
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "job_type": row[3],
                "schedule_type": row[4],
                "schedule_config": json.loads(row[5]),
                "job_config": json.loads(row[6]) if row[6] else None,
                "enabled": bool(row[7]),
                "created_at": row[8],
                "updated_at": row[9],
                "last_run": row[10],
                "next_run": row[11]
            })
        
        return jobs
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def update_job_schedule(
        self,
        job_id: str,
        last_run: Optional[datetime] = None,
        next_run: Optional[datetime] = None
    ):
        """Update job schedule information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if last_run:
            updates.append("last_run = ?")
            values.append(last_run.isoformat())
        
        if next_run:
            updates.append("next_run = ?")
            values.append(next_run.isoformat())
        
        if updates:
            values.append(job_id)
            query = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    def add_execution(
        self,
        job_id: str,
        started_at: datetime,
        status: str,
        completed_at: Optional[datetime] = None,
        result: Optional[str] = None,
        error: Optional[str] = None
    ) -> int:
        """Record job execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO job_executions 
            (job_id, started_at, completed_at, status, result, error)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            started_at.isoformat(),
            completed_at.isoformat() if completed_at else None,
            status,
            result,
            error
        ))
        
        execution_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        
        return execution_id
    
    def get_job_executions(
        self,
        job_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get execution history for a job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, job_id, started_at, completed_at, status, result, error
            FROM job_executions
            WHERE job_id = ?
            ORDER BY started_at DESC
            LIMIT ?
        """, (job_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        executions = []
        for row in rows:
            executions.append({
                "id": row[0],
                "job_id": row[1],
                "started_at": row[2],
                "completed_at": row[3],
                "status": row[4],
                "result": row[5],
                "error": row[6]
            })
        
        return executions
    
    def get_execution_stats(self, job_id: str) -> Dict[str, Any]:
        """Get execution statistics for a job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_runs,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                MAX(started_at) as last_execution
            FROM job_executions
            WHERE job_id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0.0,
                "last_execution": None
            }
        
        total = row[0] or 0
        successful = row[1] or 0
        
        return {
            "total_runs": total,
            "successful_runs": successful,
            "failed_runs": row[2] or 0,
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "last_execution": row[3]
        }

# Made with Bob
