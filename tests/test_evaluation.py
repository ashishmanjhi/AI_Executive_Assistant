"""
Test suite for Evaluation Framework
"""

import unittest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.evaluation.evaluation_store import EvaluationStore
from app.evaluation.test_runner import TestRunner
from app.evaluation.metrics_calculator import MetricsCalculator
from app.evaluation.llm_evaluator import LLMEvaluator


class TestEvaluationStore(unittest.TestCase):
    """Test EvaluationStore functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = EvaluationStore(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_test_case(self):
        """Test creating a test case."""
        test_id = self.store.create_test_case(
            test_name="Test Sentiment Analysis",
            test_type="accuracy",
            description="Test sentiment analysis accuracy",
            input_data={"text": "This is great!"},
            expected_output={"sentiment": "positive"},
            tags=["sentiment", "nlp"]
        )
        
        self.assertIsNotNone(test_id)
        self.assertIsInstance(test_id, str)
        
        # Retrieve and verify
        test_cases = self.store.get_test_cases()
        self.assertEqual(len(test_cases), 1)
        self.assertEqual(test_cases[0]['test_name'], "Test Sentiment Analysis")
    
    def test_create_and_update_test_run(self):
        """Test creating and updating a test run."""
        run_id = self.store.create_test_run(
            run_name="Test Run 1",
            test_suite="sentiment_tests"
        )
        
        self.assertIsNotNone(run_id)
        
        # Update run
        success = self.store.update_test_run(
            run_id=run_id,
            status="completed",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            skipped_tests=0
        )
        
        self.assertTrue(success)
    
    def test_store_test_result(self):
        """Test storing a test result."""
        # Create test case and run
        test_id = self.store.create_test_case(
            test_name="Test 1",
            test_type="unit",
            description="Unit test",
            input_data={"x": 1},
            expected_output={"y": 2}
        )
        
        run_id = self.store.create_test_run(
            run_name="Run 1",
            test_suite="unit_tests"
        )
        
        # Store result
        result_id = self.store.store_test_result(
            run_id=run_id,
            test_case_id=test_id,
            status="passed",
            actual_output={"y": 2},
            execution_time_ms=150
        )
        
        self.assertIsInstance(result_id, int)
        self.assertGreater(result_id, 0)
        
        # Retrieve results
        results = self.store.get_test_results(run_id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'passed')
    
    def test_store_and_get_metrics(self):
        """Test storing and retrieving metrics."""
        metric_id = self.store.store_metric(
            metric_name="accuracy",
            metric_category="performance",
            value=95.5,
            target_value=90.0,
            unit="percent"
        )
        
        self.assertIsInstance(metric_id, int)
        
        # Retrieve metrics
        metrics = self.store.get_metrics(metric_name="accuracy")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]['value'], 95.5)
    
    def test_user_feedback(self):
        """Test user feedback storage and retrieval."""
        feedback_id = self.store.store_user_feedback(
            user_id="user1",
            feature="email_analysis",
            rating=5,
            feedback_text="Excellent feature!",
            context={"version": "1.0"}
        )
        
        self.assertIsInstance(feedback_id, int)
        
        # Retrieve feedback
        feedback = self.store.get_user_feedback(feature="email_analysis")
        self.assertEqual(len(feedback), 1)
        self.assertEqual(feedback[0]['rating'], 5)
        
        # Get average rating
        avg_rating = self.store.get_average_rating("email_analysis")
        self.assertEqual(avg_rating, 5.0)


class TestTestRunner(unittest.TestCase):
    """Test TestRunner functionality."""
    
    def setUp(self):
        """Set up test runner."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = EvaluationStore(self.temp_db.name)
        self.runner = TestRunner(self.store)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_register_test_function(self):
        """Test registering a test function."""
        def dummy_test(input_data):
            return {"result": "success"}
        
        self.runner.register_test_function("dummy", dummy_test)
        self.assertIn("dummy", self.runner.test_functions)
    
    def test_run_test_suite_empty(self):
        """Test running an empty test suite."""
        result = self.runner.run_test_suite("empty_suite")
        
        self.assertEqual(result['total_tests'], 0)
        self.assertEqual(result['status'], 'completed')
    
    def test_run_test_suite_with_tests(self):
        """Test running a test suite with tests."""
        # Register test function
        def simple_test(input_data):
            return {"output": input_data.get("input", 0) * 2}
        
        self.runner.register_test_function("simple", simple_test)
        
        # Create test cases
        self.store.create_test_case(
            test_name="Test 1",
            test_type="simple",
            description="Simple test",
            input_data={"input": 5},
            expected_output={"output": 10}
        )
        
        self.store.create_test_case(
            test_name="Test 2",
            test_type="simple",
            description="Simple test 2",
            input_data={"input": 3},
            expected_output={"output": 6}
        )
        
        # Run suite
        result = self.runner.run_test_suite("simple_suite", test_type="simple")
        
        self.assertEqual(result['total_tests'], 2)
        self.assertEqual(result['passed_tests'], 2)
        self.assertEqual(result['failed_tests'], 0)


class TestMetricsCalculator(unittest.TestCase):
    """Test MetricsCalculator functionality."""
    
    def setUp(self):
        """Set up metrics calculator."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = EvaluationStore(self.temp_db.name)
        self.calculator = MetricsCalculator(self.store)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_calculate_accuracy(self):
        """Test accuracy calculation."""
        accuracy = self.calculator.calculate_accuracy(correct=85, total=100)
        self.assertEqual(accuracy, 85.0)
        
        # Test edge case
        accuracy_zero = self.calculator.calculate_accuracy(correct=0, total=0)
        self.assertEqual(accuracy_zero, 0.0)
    
    def test_calculate_precision_recall_f1(self):
        """Test precision, recall, and F1 calculation."""
        metrics = self.calculator.calculate_precision_recall_f1(
            true_positives=80,
            false_positives=10,
            false_negatives=20
        )
        
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        
        # Verify calculations
        self.assertAlmostEqual(metrics['precision'], 80/90, places=2)
        self.assertAlmostEqual(metrics['recall'], 80/100, places=2)
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation."""
        execution_times = [100.0, 150.0, 200.0, 120.0, 180.0, 160.0, 140.0, 190.0, 110.0, 170.0]
        
        metrics = self.calculator.calculate_performance_metrics(execution_times)
        
        self.assertIn('min', metrics)
        self.assertIn('max', metrics)
        self.assertIn('mean', metrics)
        self.assertIn('median', metrics)
        self.assertIn('p95', metrics)
        
        self.assertEqual(metrics['min'], 100)
        self.assertEqual(metrics['max'], 200)
    
    def test_calculate_feature_metrics(self):
        """Test feature metrics calculation."""
        # Add some feedback
        self.store.store_user_feedback("user1", "feature1", 5, "Great!")
        self.store.store_user_feedback("user2", "feature1", 4, "Good")
        self.store.store_user_feedback("user3", "feature1", 5, "Excellent")
        
        metrics = self.calculator.calculate_feature_metrics("feature1")
        
        self.assertEqual(metrics['total_feedback'], 3)
        self.assertAlmostEqual(metrics['average_rating'], 4.67, places=1)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluationStore))
    suite.addTests(loader.loadTestsFromTestCase(TestTestRunner))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCalculator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

# Made with Bob
