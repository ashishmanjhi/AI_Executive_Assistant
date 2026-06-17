"""
Metrics Calculator - Calculate evaluation metrics
"""

from typing import Dict, Any, List, Optional
import statistics

from .evaluation_store import EvaluationStore


class MetricsCalculator:
    """Calculates various evaluation metrics."""
    
    def __init__(self, store: EvaluationStore):
        """
        Initialize the metrics calculator.
        
        Args:
            store: EvaluationStore instance
        """
        self.store = store
    
    def calculate_accuracy(
        self,
        correct: int,
        total: int
    ) -> float:
        """
        Calculate accuracy percentage.
        
        Args:
            correct: Number of correct predictions
            total: Total number of predictions
            
        Returns:
            Accuracy as percentage (0-100)
        """
        if total == 0:
            return 0.0
        return (correct / total) * 100
    
    def calculate_precision_recall_f1(
        self,
        true_positives: int,
        false_positives: int,
        false_negatives: int
    ) -> Dict[str, float]:
        """
        Calculate precision, recall, and F1 score.
        
        Args:
            true_positives: Number of true positives
            false_positives: Number of false positives
            false_negatives: Number of false negatives
            
        Returns:
            Dictionary with precision, recall, and F1 score
        """
        precision = 0.0
        if (true_positives + false_positives) > 0:
            precision = true_positives / (true_positives + false_positives)
        
        recall = 0.0
        if (true_positives + false_negatives) > 0:
            recall = true_positives / (true_positives + false_negatives)
        
        f1 = 0.0
        if (precision + recall) > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def calculate_performance_metrics(
        self,
        execution_times: List[float]
    ) -> Dict[str, float]:
        """
        Calculate performance metrics from execution times.
        
        Args:
            execution_times: List of execution times in milliseconds
            
        Returns:
            Dictionary with performance metrics
        """
        if not execution_times:
            return {
                'min': 0.0,
                'max': 0.0,
                'mean': 0.0,
                'median': 0.0,
                'std_dev': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        sorted_times = sorted(execution_times)
        n = len(sorted_times)
        
        return {
            'min': min(execution_times),
            'max': max(execution_times),
            'mean': statistics.mean(execution_times),
            'median': statistics.median(execution_times),
            'std_dev': statistics.stdev(execution_times) if n > 1 else 0.0,
            'p95': sorted_times[int(n * 0.95)] if n > 0 else 0.0,
            'p99': sorted_times[int(n * 0.99)] if n > 0 else 0.0
        }
    
    def calculate_test_run_metrics(
        self,
        run_id: str
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for a test run.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Dictionary with all calculated metrics
        """
        results = self.store.get_test_results(run_id)
        
        if not results:
            return {'error': 'No results found for test run'}
        
        # Basic counts
        total = len(results)
        passed = sum(1 for r in results if r['status'] == 'passed')
        failed = sum(1 for r in results if r['status'] == 'failed')
        skipped = sum(1 for r in results if r['status'] == 'skipped')
        errors = sum(1 for r in results if r['status'] == 'error')
        
        # Accuracy
        accuracy = self.calculate_accuracy(passed, total)
        
        # Performance metrics
        execution_times = [
            r['execution_time_ms'] 
            for r in results 
            if r['execution_time_ms'] is not None
        ]
        performance = self.calculate_performance_metrics(execution_times)
        
        # Store metrics
        self.store.store_metric(
            metric_name='test_accuracy',
            metric_category='accuracy',
            value=accuracy,
            target_value=90.0,
            unit='percent',
            test_run_id=run_id
        )
        
        self.store.store_metric(
            metric_name='avg_execution_time',
            metric_category='performance',
            value=performance['mean'],
            target_value=1000.0,
            unit='ms',
            test_run_id=run_id
        )
        
        return {
            'run_id': run_id,
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'accuracy': accuracy,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'performance': performance
        }
    
    def calculate_feature_metrics(
        self,
        feature: str
    ) -> Dict[str, Any]:
        """
        Calculate metrics for a specific feature based on user feedback.
        
        Args:
            feature: Feature name
            
        Returns:
            Dictionary with feature metrics
        """
        feedback = self.store.get_user_feedback(feature=feature)
        
        if not feedback:
            return {
                'feature': feature,
                'total_feedback': 0,
                'average_rating': 0.0,
                'rating_distribution': {}
            }
        
        ratings = [f['rating'] for f in feedback]
        
        # Rating distribution
        distribution = {i: ratings.count(i) for i in range(1, 6)}
        
        # Calculate average
        avg_rating = sum(ratings) / len(ratings)
        
        # Store metric
        self.store.store_metric(
            metric_name=f'{feature}_rating',
            metric_category='user_satisfaction',
            value=avg_rating,
            target_value=4.0,
            unit='stars'
        )
        
        return {
            'feature': feature,
            'total_feedback': len(feedback),
            'average_rating': avg_rating,
            'rating_distribution': distribution,
            'satisfaction_rate': (sum(1 for r in ratings if r >= 4) / len(ratings) * 100)
        }
    
    def calculate_trend_metrics(
        self,
        metric_name: str,
        metric_category: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate trend metrics over time.
        
        Args:
            metric_name: Name of the metric
            metric_category: Category of the metric
            limit: Number of recent data points
            
        Returns:
            Dictionary with trend analysis
        """
        metrics = self.store.get_metrics(
            metric_name=metric_name,
            metric_category=metric_category,
            limit=limit
        )
        
        if not metrics:
            return {
                'metric_name': metric_name,
                'data_points': 0,
                'trend': 'no_data'
            }
        
        values = [m['value'] for m in metrics]
        
        # Calculate trend (simple: compare first half to second half)
        if len(values) >= 4:
            mid = len(values) // 2
            first_half_avg = sum(values[:mid]) / mid
            second_half_avg = sum(values[mid:]) / (len(values) - mid)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = 'improving'
            elif second_half_avg < first_half_avg * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'metric_name': metric_name,
            'data_points': len(values),
            'current_value': values[0] if values else 0,
            'min_value': min(values) if values else 0,
            'max_value': max(values) if values else 0,
            'avg_value': sum(values) / len(values) if values else 0,
            'trend': trend
        }

# Made with Bob
