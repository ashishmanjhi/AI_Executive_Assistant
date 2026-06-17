"""
Plan Store for Persistent Task Plans
Stores plans and their execution state in SQLite
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class PlanStore:
    """SQLite-based storage for task plans"""
    
    def __init__(self, db_path: str = "data/plans.db"):
        """Initialize plan store with SQLite database"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                goal TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                completed_at DATETIME,
                metadata TEXT
            )
        """)
        
        # Plan steps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plan_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                description TEXT NOT NULL,
                action_type TEXT NOT NULL,
                parameters TEXT,
                dependencies TEXT,
                status TEXT NOT NULL,
                result TEXT,
                error TEXT,
                started_at DATETIME,
                completed_at DATETIME,
                FOREIGN KEY (plan_id) REFERENCES plans(id),
                UNIQUE(plan_id, step_number)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plan_steps_plan_id 
            ON plan_steps(plan_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_plans_status 
            ON plans(status)
        """)
        
        conn.commit()
        conn.close()
    
    def add_plan(
        self,
        plan_id: str,
        goal: str,
        description: Optional[str] = None,
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a new plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO plans (id, goal, description, status, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                plan_id,
                goal,
                description,
                status,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def add_step(
        self,
        plan_id: str,
        step_number: int,
        description: str,
        action_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[int]] = None,
        status: str = "pending"
    ) -> bool:
        """Add a step to a plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO plan_steps 
                (plan_id, step_number, description, action_type, parameters, dependencies, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                plan_id,
                step_number,
                description,
                action_type,
                json.dumps(parameters) if parameters else None,
                json.dumps(dependencies) if dependencies else None,
                status
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, goal, description, status, created_at, updated_at,
                   started_at, completed_at, metadata
            FROM plans
            WHERE id = ?
        """, (plan_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "goal": row[1],
            "description": row[2],
            "status": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "started_at": row[6],
            "completed_at": row[7],
            "metadata": json.loads(row[8]) if row[8] else None
        }
    
    def get_plan_steps(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get all steps for a plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, plan_id, step_number, description, action_type, parameters,
                   dependencies, status, result, error, started_at, completed_at
            FROM plan_steps
            WHERE plan_id = ?
            ORDER BY step_number
        """, (plan_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        steps = []
        for row in rows:
            steps.append({
                "id": row[0],
                "plan_id": row[1],
                "step_number": row[2],
                "description": row[3],
                "action_type": row[4],
                "parameters": json.loads(row[5]) if row[5] else None,
                "dependencies": json.loads(row[6]) if row[6] else None,
                "status": row[7],
                "result": row[8],
                "error": row[9],
                "started_at": row[10],
                "completed_at": row[11]
            })
        
        return steps
    
    def update_plan_status(
        self,
        plan_id: str,
        status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update plan status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        values = [status]
        
        if started_at:
            updates.append("started_at = ?")
            values.append(started_at.isoformat())
        
        if completed_at:
            updates.append("completed_at = ?")
            values.append(completed_at.isoformat())
        
        values.append(plan_id)
        
        query = f"UPDATE plans SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def update_step_status(
        self,
        plan_id: str,
        step_number: int,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update step status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = ["status = ?"]
        values: List[Any] = [status]
        
        if result is not None:
            updates.append("result = ?")
            values.append(result)
        
        if error is not None:
            updates.append("error = ?")
            values.append(error)
        
        if started_at:
            updates.append("started_at = ?")
            values.append(started_at.isoformat())
        
        if completed_at:
            updates.append("completed_at = ?")
            values.append(completed_at.isoformat())
        
        values.append(plan_id)
        values.append(step_number)
        
        query = f"UPDATE plan_steps SET {', '.join(updates)} WHERE plan_id = ? AND step_number = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def get_all_plans(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all plans, optionally filtered by status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, goal, description, status, created_at, updated_at,
                       started_at, completed_at, metadata
                FROM plans
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, goal, description, status, created_at, updated_at,
                       started_at, completed_at, metadata
                FROM plans
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in rows:
            plans.append({
                "id": row[0],
                "goal": row[1],
                "description": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5],
                "started_at": row[6],
                "completed_at": row[7],
                "metadata": json.loads(row[8]) if row[8] else None
            })
        
        return plans
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan and its steps"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete steps first
        cursor.execute("DELETE FROM plan_steps WHERE plan_id = ?", (plan_id,))
        
        # Delete plan
        cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_plan_statistics(self) -> Dict[str, Any]:
        """Get statistics about plans"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total plans by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM plans 
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Total steps
        cursor.execute("SELECT COUNT(*) FROM plan_steps")
        total_steps = cursor.fetchone()[0]
        
        # Completed steps
        cursor.execute("SELECT COUNT(*) FROM plan_steps WHERE status = 'completed'")
        completed_steps = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_plans": sum(status_counts.values()),
            "plans_by_status": status_counts,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "completion_rate": (completed_steps / total_steps * 100) if total_steps > 0 else 0.0
        }

# Made with Bob
