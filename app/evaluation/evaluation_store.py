"""
Evaluation Store - Database operations for evaluation framework
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
import uuid


class EvaluationStore:
    """Manages storage and retrieval of evaluation data."""
    
    def __init__(self, db_path: str = "data/evaluation.db"):
        """
        Initialize the evaluation store.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id TEXT PRIMARY KEY,
                    test_name TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    description TEXT,
                    input_data TEXT NOT NULL,
                    expected_output TEXT NOT NULL,
                    tags TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at REAL DEFAULT (julianday('now')),
                    updated_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_cases_type 
                ON test_cases(test_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_cases_active 
                ON test_cases(is_active)
            """)
            
            # Test runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id TEXT PRIMARY KEY,
                    run_name TEXT NOT NULL,
                    test_suite TEXT,
                    started_at REAL NOT NULL,
                    completed_at REAL,
                    status TEXT NOT NULL,
                    total_tests INTEGER DEFAULT 0,
                    passed_tests INTEGER DEFAULT 0,
                    failed_tests INTEGER DEFAULT 0,
                    skipped_tests INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_runs_started 
                ON test_runs(started_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_runs_status 
                ON test_runs(status)
            """)
            
            # Test results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    test_case_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    actual_output TEXT,
                    error_message TEXT,
                    execution_time_ms INTEGER,
                    metrics TEXT,
                    executed_at REAL DEFAULT (julianday('now')),
                    FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_results_run 
                ON test_results(run_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_results_case 
                ON test_results(test_case_id)
            """)
            
            # Evaluation metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_category TEXT NOT NULL,
                    value REAL NOT NULL,
                    target_value REAL,
                    unit TEXT,
                    test_run_id TEXT,
                    recorded_at REAL DEFAULT (julianday('now')),
                    metadata TEXT,
                    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE SET NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name 
                ON evaluation_metrics(metric_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_category 
                ON evaluation_metrics(metric_category)
            """)
            
            # User feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    feature TEXT NOT NULL,
                    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                    feedback_text TEXT,
                    context TEXT,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_user 
                ON user_feedback(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_feature 
                ON user_feedback(feature)
            """)
            
            conn.commit()
            conn.close()
    
    def create_test_case(
        self,
        test_name: str,
        test_type: str,
        description: str,
        input_data: Dict[str, Any],
        expected_output: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new test case.
        
        Args:
            test_name: Name of the test
            test_type: Type of test (unit, integration, performance, accuracy)
            description: Test description
            input_data: Input data for the test
            expected_output: Expected output
            tags: Optional tags for categorization
            
        Returns:
            Test case ID
        """
        with self.lock:
            test_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_cases
                (id, test_name, test_type, description, input_data, expected_output, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                test_id,
                test_name,
                test_type,
                description,
                json.dumps(input_data),
                json.dumps(expected_output),
                json.dumps(tags or [])
            ))
            
            conn.commit()
            conn.close()
            
            return test_id
    
    def get_test_cases(
        self,
        test_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get test cases.
        
        Args:
            test_type: Filter by test type
            active_only: Only return active test cases
            
        Returns:
            List of test cases
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM test_cases WHERE 1=1"
            params = []
            
            if test_type:
                query += " AND test_type = ?"
                params.append(test_type)
            
            if active_only:
                query += " AND is_active = 1"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'test_name': row['test_name'],
                    'test_type': row['test_type'],
                    'description': row['description'],
                    'input_data': json.loads(row['input_data']),
                    'expected_output': json.loads(row['expected_output']),
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'is_active': bool(row['is_active']),
                    'created_at': row['created_at']
                })
            
            return results
    
    def create_test_run(
        self,
        run_name: str,
        test_suite: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new test run.
        
        Args:
            run_name: Name of the test run
            test_suite: Test suite name
            metadata: Additional metadata
            
        Returns:
            Test run ID
        """
        with self.lock:
            run_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_runs
                (id, run_name, test_suite, started_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                run_name,
                test_suite,
                datetime.now().timestamp(),
                'running',
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            return run_id
    
    def update_test_run(
        self,
        run_id: str,
        status: str,
        total_tests: int,
        passed_tests: int,
        failed_tests: int,
        skipped_tests: int
    ) -> bool:
        """
        Update test run results.
        
        Args:
            run_id: Test run ID
            status: Final status
            total_tests: Total number of tests
            passed_tests: Number of passed tests
            failed_tests: Number of failed tests
            skipped_tests: Number of skipped tests
            
        Returns:
            True if updated successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE test_runs
                    SET completed_at = ?,
                        status = ?,
                        total_tests = ?,
                        passed_tests = ?,
                        failed_tests = ?,
                        skipped_tests = ?
                    WHERE id = ?
                """, (
                    datetime.now().timestamp(),
                    status,
                    total_tests,
                    passed_tests,
                    failed_tests,
                    skipped_tests,
                    run_id
                ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                print(f"Error updating test run: {e}")
                return False
    
    def store_test_result(
        self,
        run_id: str,
        test_case_id: str,
        status: str,
        actual_output: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store a test result.
        
        Args:
            run_id: Test run ID
            test_case_id: Test case ID
            status: Test status (passed, failed, skipped, error)
            actual_output: Actual output from test
            error_message: Error message if failed
            execution_time_ms: Execution time in milliseconds
            metrics: Additional metrics
            
        Returns:
            Result ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO test_results
                (run_id, test_case_id, status, actual_output, error_message,
                 execution_time_ms, metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                test_case_id,
                status,
                json.dumps(actual_output) if actual_output else None,
                error_message,
                execution_time_ms,
                json.dumps(metrics) if metrics else None
            ))
            
            result_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # lastrowid should always be set after INSERT, but handle None case for type safety
            if result_id is None:
                raise RuntimeError("Failed to get result ID after inserting test result")
            
            return result_id
    
    def get_test_results(
        self,
        run_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get test results for a run.
        
        Args:
            run_id: Test run ID
            
        Returns:
            List of test results
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM test_results WHERE run_id = ?
                ORDER BY executed_at
            """, (run_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'test_case_id': row['test_case_id'],
                    'status': row['status'],
                    'actual_output': json.loads(row['actual_output']) if row['actual_output'] else None,
                    'error_message': row['error_message'],
                    'execution_time_ms': row['execution_time_ms'],
                    'metrics': json.loads(row['metrics']) if row['metrics'] else None,
                    'executed_at': row['executed_at']
                })
            
            return results
    
    def store_metric(
        self,
        metric_name: str,
        metric_category: str,
        value: float,
        target_value: Optional[float] = None,
        unit: Optional[str] = None,
        test_run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store an evaluation metric.
        
        Args:
            metric_name: Name of the metric
            metric_category: Category (performance, accuracy, quality)
            value: Metric value
            target_value: Target value for comparison
            unit: Unit of measurement
            test_run_id: Associated test run ID
            metadata: Additional metadata
            
        Returns:
            Metric ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO evaluation_metrics
                (metric_name, metric_category, value, target_value, unit,
                 test_run_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metric_name,
                metric_category,
                value,
                target_value,
                unit,
                test_run_id,
                json.dumps(metadata) if metadata else None
            ))
            
            metric_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # lastrowid should always be set after INSERT, but handle None case for type safety
            if metric_id is None:
                raise RuntimeError("Failed to get metric ID after inserting evaluation metric")
            
            return metric_id
    
    def get_metrics(
        self,
        metric_name: Optional[str] = None,
        metric_category: Optional[str] = None,
        test_run_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get evaluation metrics.
        
        Args:
            metric_name: Filter by metric name
            metric_category: Filter by category
            test_run_id: Filter by test run
            limit: Maximum number of results
            
        Returns:
            List of metrics
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM evaluation_metrics WHERE 1=1"
            params = []
            
            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)
            
            if metric_category:
                query += " AND metric_category = ?"
                params.append(metric_category)
            
            if test_run_id:
                query += " AND test_run_id = ?"
                params.append(test_run_id)
            
            query += " ORDER BY recorded_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'metric_name': row['metric_name'],
                    'metric_category': row['metric_category'],
                    'value': row['value'],
                    'target_value': row['target_value'],
                    'unit': row['unit'],
                    'test_run_id': row['test_run_id'],
                    'recorded_at': row['recorded_at'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                })
            
            return results
    
    def store_user_feedback(
        self,
        user_id: str,
        feature: str,
        rating: int,
        feedback_text: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store user feedback.
        
        Args:
            user_id: User identifier
            feature: Feature being rated
            rating: Rating (1-5)
            feedback_text: Optional feedback text
            context: Additional context
            
        Returns:
            Feedback ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_feedback
                (user_id, feature, rating, feedback_text, context)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                feature,
                rating,
                feedback_text,
                json.dumps(context) if context else None
            ))
            
            feedback_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # lastrowid should always be set after INSERT, but handle None case for type safety
            if feedback_id is None:
                raise RuntimeError("Failed to get feedback ID after inserting user feedback")
            
            return feedback_id
    
    def get_user_feedback(
        self,
        feature: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get user feedback.
        
        Args:
            feature: Filter by feature
            user_id: Filter by user
            limit: Maximum number of results
            
        Returns:
            List of feedback entries
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM user_feedback WHERE 1=1"
            params = []
            
            if feature:
                query += " AND feature = ?"
                params.append(feature)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'feature': row['feature'],
                    'rating': row['rating'],
                    'feedback_text': row['feedback_text'],
                    'context': json.loads(row['context']) if row['context'] else None,
                    'created_at': row['created_at']
                })
            
            return results
    
    def get_average_rating(self, feature: str) -> Optional[float]:
        """Get average rating for a feature."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(rating) as avg_rating
                FROM user_feedback
                WHERE feature = ?
            """, (feature,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result and result[0] else None

# Made with Bob
