"""
Test Suite for Observability System
Tests metrics, logging, and health checks
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.observability import MetricsCollector, StructuredLogger, HealthChecker
from app.observability.health_checker import HealthStatus


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection functionality"""
    
    def setUp(self):
        """Set up test metrics collector"""
        self.db_path = "test_metrics.db"
        self.collector = MetricsCollector(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_increment_counter(self):
        """Test counter increment"""
        self.collector.increment_counter("test_counter", 1.0)
        self.collector.increment_counter("test_counter", 2.0)
        
        value = self.collector.get_counter("test_counter")
        self.assertEqual(value, 3.0)
    
    def test_set_gauge(self):
        """Test gauge setting"""
        self.collector.set_gauge("test_gauge", 42.0)
        
        value = self.collector.get_gauge("test_gauge")
        self.assertEqual(value, 42.0)
        
        # Update gauge
        self.collector.set_gauge("test_gauge", 100.0)
        value = self.collector.get_gauge("test_gauge")
        self.assertEqual(value, 100.0)
    
    def test_observe_histogram(self):
        """Test histogram observations"""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        for v in values:
            self.collector.observe_histogram("test_histogram", v)
        
        stats = self.collector.get_histogram_stats("test_histogram")
        
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 5.0)
        self.assertEqual(stats["avg"], 3.0)
        self.assertEqual(stats["sum"], 15.0)
    
    def test_metrics_with_labels(self):
        """Test metrics with labels"""
        self.collector.increment_counter(
            "requests",
            1.0,
            labels={"method": "GET", "status": "200"}
        )
        
        self.collector.increment_counter(
            "requests",
            1.0,
            labels={"method": "POST", "status": "201"}
        )
        
        # Different labels create different metrics
        get_count = self.collector.get_counter(
            "requests",
            labels={"method": "GET", "status": "200"}
        )
        post_count = self.collector.get_counter(
            "requests",
            labels={"method": "POST", "status": "201"}
        )
        
        self.assertEqual(get_count, 1.0)
        self.assertEqual(post_count, 1.0)
    
    def test_query_metrics(self):
        """Test querying metrics"""
        # Add some metrics
        for i in range(5):
            self.collector.increment_counter("test_query", 1.0)
            time.sleep(0.01)  # Small delay
        
        # Query metrics
        metrics = self.collector.query_metrics(
            metric_name="test_query",
            limit=10
        )
        
        self.assertGreater(len(metrics), 0)
        self.assertEqual(metrics[0]["metric_name"], "test_query")
    
    def test_metric_summary(self):
        """Test metric summary"""
        # Add multiple values
        for i in range(1, 6):
            self.collector.set_gauge("test_summary", float(i))
        
        summary = self.collector.get_metric_summary("test_summary")
        
        self.assertEqual(summary["metric_name"], "test_summary")
        self.assertGreater(summary["count"], 0)
        self.assertGreater(summary["avg"], 0)


class TestStructuredLogger(unittest.TestCase):
    """Test structured logging functionality"""
    
    def setUp(self):
        """Set up test logger"""
        self.db_path = "test_logs.db"
        self.logger = StructuredLogger("test_logger", self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_log_levels(self):
        """Test different log levels"""
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        # Query logs
        logs = self.logger.query_logs(limit=10)
        
        self.assertEqual(len(logs), 5)
        levels = {log["level"] for log in logs}
        self.assertIn("DEBUG", levels)
        self.assertIn("INFO", levels)
        self.assertIn("WARNING", levels)
        self.assertIn("ERROR", levels)
        self.assertIn("CRITICAL", levels)
    
    def test_log_with_context(self):
        """Test logging with context"""
        self.logger.set_context(user_id="user123", request_id="req456")
        self.logger.info("Test message with context")
        
        logs = self.logger.query_logs(limit=1)
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["user_id"], "user123")
        self.assertEqual(logs[0]["request_id"], "req456")
    
    def test_log_with_exception(self):
        """Test logging with exception"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.logger.error("Error occurred", exception=e)
        
        logs = self.logger.query_logs(level="ERROR", limit=1)
        
        self.assertEqual(len(logs), 1)
        self.assertIsNotNone(logs[0]["exception"])
        self.assertIn("ValueError", str(logs[0]["exception"]))
    
    def test_query_logs_by_user(self):
        """Test querying logs by user"""
        self.logger.info("User 1 action", user_id="user1")
        self.logger.info("User 2 action", user_id="user2")
        self.logger.info("User 1 another action", user_id="user1")
        
        user1_logs = self.logger.query_logs(user_id="user1", limit=10)
        
        self.assertEqual(len(user1_logs), 2)
        self.assertTrue(all(log["user_id"] == "user1" for log in user1_logs))
    
    def test_error_count(self):
        """Test error counting"""
        self.logger.info("Info message")
        self.logger.error("Error 1")
        self.logger.error("Error 2")
        self.logger.critical("Critical error")
        
        error_count = self.logger.get_error_count()
        
        self.assertEqual(error_count, 3)  # 2 errors + 1 critical


class TestHealthChecker(unittest.TestCase):
    """Test health checking functionality"""
    
    def setUp(self):
        """Set up test health checker"""
        self.db_path = "test_health.db"
        self.checker = HealthChecker(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_default_checks(self):
        """Test default health checks"""
        result = self.checker.run_all_checks()
        
        self.assertIn("overall_status", result)
        self.assertIn("checks", result)
        self.assertIn("disk_space", result["checks"])
        self.assertIn("memory", result["checks"])
        self.assertIn("database", result["checks"])
    
    def test_disk_space_check(self):
        """Test disk space check"""
        result = self.checker.run_check("disk_space")
        
        self.assertIn("status", result)
        self.assertIn("message", result)
        self.assertIn("details", result)
        self.assertIn("percent_used", result["details"])
    
    def test_memory_check(self):
        """Test memory check"""
        result = self.checker.run_check("memory")
        
        self.assertIn("status", result)
        self.assertIn("message", result)
        self.assertIn("details", result)
        self.assertIn("percent_used", result["details"])
    
    def test_custom_check(self):
        """Test custom health check"""
        def custom_check():
            return {
                "status": HealthStatus.HEALTHY,
                "message": "Custom check passed",
                "details": {"custom_value": 42}
            }
        
        self.checker.register_check("custom", custom_check)
        result = self.checker.run_check("custom")
        
        self.assertEqual(result["status"], HealthStatus.HEALTHY)
        self.assertEqual(result["message"], "Custom check passed")
        self.assertEqual(result["details"]["custom_value"], 42)
    
    def test_health_history(self):
        """Test health check history"""
        # Run checks multiple times
        for _ in range(3):
            self.checker.run_check("disk_space")
            time.sleep(0.01)
        
        history = self.checker.get_health_history(check_name="disk_space", limit=10)
        
        self.assertGreaterEqual(len(history), 3)
        self.assertTrue(all(h["check_name"] == "disk_space" for h in history))


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestStructuredLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthChecker))
    
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
