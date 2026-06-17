"""
Test Runner - Execute evaluation tests and collect results
"""

import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from .evaluation_store import EvaluationStore


class TestRunner:
    """Runs evaluation tests and collects metrics."""
    
    def __init__(self, store: EvaluationStore):
        """
        Initialize the test runner.
        
        Args:
            store: EvaluationStore instance
        """
        self.store = store
        self.test_functions: Dict[str, Callable] = {}
    
    def register_test_function(self, test_type: str, func: Callable):
        """
        Register a test function for a specific test type.
        
        Args:
            test_type: Type of test
            func: Function to execute the test
        """
        self.test_functions[test_type] = func
    
    def run_test_suite(
        self,
        suite_name: str,
        test_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a suite of tests.
        
        Args:
            suite_name: Name of the test suite
            test_type: Optional filter by test type
            
        Returns:
            Dictionary with test run results
        """
        # Create test run
        run_name = f"{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_id = self.store.create_test_run(
            run_name=run_name,
            test_suite=suite_name
        )
        
        # Get test cases
        test_cases = self.store.get_test_cases(test_type=test_type, active_only=True)
        
        if not test_cases:
            self.store.update_test_run(
                run_id=run_id,
                status='completed',
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0
            )
            return {
                'run_id': run_id,
                'status': 'completed',
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'results': []
            }
        
        # Run tests
        results = []
        for test_case in test_cases:
            result = self._run_single_test(run_id, test_case)
            results.append(result)
        
        # Calculate summary
        passed = sum(1 for r in results if r['status'] == 'passed')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        
        # Update test run
        self.store.update_test_run(
            run_id=run_id,
            status='completed',
            total_tests=len(results),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped
        )
        
        return {
            'run_id': run_id,
            'status': 'completed',
            'total_tests': len(results),
            'passed_tests': passed,
            'failed_tests': failed,
            'skipped_tests': skipped,
            'results': results
        }
    
    def _run_single_test(
        self,
        run_id: str,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            run_id: Test run ID
            test_case: Test case data
            
        Returns:
            Test result dictionary
        """
        test_id = test_case['id']
        test_type = test_case['test_type']
        
        # Check if test function is registered
        if test_type not in self.test_functions:
            self.store.store_test_result(
                run_id=run_id,
                test_case_id=test_id,
                status='skipped',
                error_message=f"No test function registered for type: {test_type}"
            )
            return {
                'test_case_id': test_id,
                'test_name': test_case['test_name'],
                'status': 'skipped',
                'error_message': f"No test function registered for type: {test_type}"
            }
        
        # Execute test
        start_time = time.time()
        
        try:
            test_func = self.test_functions[test_type]
            actual_output = test_func(test_case['input_data'])
            
            # Compare with expected output
            expected = test_case['expected_output']
            passed = self._compare_outputs(actual_output, expected)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            status = 'passed' if passed else 'failed'
            error_message = None if passed else "Output does not match expected"
            
            # Store result
            self.store.store_test_result(
                run_id=run_id,
                test_case_id=test_id,
                status=status,
                actual_output=actual_output,
                error_message=error_message,
                execution_time_ms=execution_time
            )
            
            return {
                'test_case_id': test_id,
                'test_name': test_case['test_name'],
                'status': status,
                'execution_time_ms': execution_time,
                'actual_output': actual_output,
                'expected_output': expected,
                'error_message': error_message
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            self.store.store_test_result(
                run_id=run_id,
                test_case_id=test_id,
                status='error',
                error_message=str(e),
                execution_time_ms=execution_time
            )
            
            return {
                'test_case_id': test_id,
                'test_name': test_case['test_name'],
                'status': 'error',
                'execution_time_ms': execution_time,
                'error_message': str(e)
            }
    
    def _compare_outputs(
        self,
        actual: Any,
        expected: Any
    ) -> bool:
        """
        Compare actual and expected outputs.
        
        Args:
            actual: Actual output
            expected: Expected output
            
        Returns:
            True if outputs match
        """
        # Simple comparison - can be enhanced for complex types
        if isinstance(expected, dict) and isinstance(actual, dict):
            # Check if all expected keys are present with correct values
            for key, value in expected.items():
                if key not in actual:
                    return False
                if not self._compare_outputs(actual[key], value):
                    return False
            return True
        elif isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            for exp_item, act_item in zip(expected, actual):
                if not self._compare_outputs(act_item, exp_item):
                    return False
            return True
        else:
            return actual == expected
    
    def run_single_test_by_id(self, test_case_id: str) -> Dict[str, Any]:
        """
        Run a single test case by ID.
        
        Args:
            test_case_id: Test case ID
            
        Returns:
            Test result
        """
        # Get test case
        test_cases = self.store.get_test_cases()
        test_case = next((tc for tc in test_cases if tc['id'] == test_case_id), None)
        
        if not test_case:
            return {
                'error': 'Test case not found',
                'test_case_id': test_case_id
            }
        
        # Create temporary run
        run_id = self.store.create_test_run(
            run_name=f"single_test_{test_case_id}",
            test_suite="single"
        )
        
        # Run test
        result = self._run_single_test(run_id, test_case)
        
        # Update run
        status = 'passed' if result['status'] == 'passed' else 'failed'
        self.store.update_test_run(
            run_id=run_id,
            status=status,
            total_tests=1,
            passed_tests=1 if status == 'passed' else 0,
            failed_tests=0 if status == 'passed' else 1,
            skipped_tests=0
        )
        
        return result
    
    def get_test_run_summary(self, run_id: str) -> Dict[str, Any]:
        """
        Get summary of a test run.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Test run summary
        """
        results = self.store.get_test_results(run_id)
        
        if not results:
            return {'error': 'Test run not found'}
        
        # Calculate statistics
        total = len(results)
        passed = sum(1 for r in results if r['status'] == 'passed')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        errors = sum(1 for r in results if r['status'] == 'error')
        
        execution_times = [r['execution_time_ms'] for r in results if r['execution_time_ms']]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'run_id': run_id,
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'avg_execution_time_ms': avg_time,
            'results': results
        }

# Made with Bob
