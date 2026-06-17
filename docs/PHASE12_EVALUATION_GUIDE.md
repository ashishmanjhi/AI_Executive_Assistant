# Phase 12: Agent Evaluation Framework - Complete Guide

## Overview

Phase 12 implements a comprehensive evaluation and testing framework for the AI Executive Assistant. This system provides tools to measure system performance, accuracy, and user satisfaction across all features through automated testing, metrics collection, and LLM-based evaluation.

## Architecture

```
app/evaluation/
├── __init__.py                # Package initialization
├── evaluation_store.py        # Database operations (710 lines)
├── test_runner.py             # Test execution engine (318 lines)
├── metrics_calculator.py      # Metrics computation (268 lines)
└── llm_evaluator.py          # LLM-as-judge evaluation (330 lines)

tests/
└── test_evaluation.py         # Comprehensive test suite (330 lines)
```

## Components

### 1. Evaluation Store (`evaluation_store.py`)

The Evaluation Store manages all database operations for the evaluation framework.

#### Database Schema

**Test Cases Table**

```sql
CREATE TABLE test_cases (
    id TEXT PRIMARY KEY,
    test_name TEXT NOT NULL,
    test_type TEXT NOT NULL,
    description TEXT,
    input_data TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    tags TEXT,
    is_active INTEGER DEFAULT 1
)
```

**Test Runs Table**

```sql
CREATE TABLE test_runs (
    id TEXT PRIMARY KEY,
    run_name TEXT NOT NULL,
    test_suite TEXT,
    started_at REAL NOT NULL,
    completed_at REAL,
    status TEXT NOT NULL,
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    skipped_tests INTEGER DEFAULT 0
)
```

**Test Results Table**

```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    test_case_id TEXT NOT NULL,
    status TEXT NOT NULL,
    actual_output TEXT,
    error_message TEXT,
    execution_time_ms INTEGER,
    metrics TEXT
)
```

**Evaluation Metrics Table**

```sql
CREATE TABLE evaluation_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_category TEXT NOT NULL,
    value REAL NOT NULL,
    target_value REAL,
    unit TEXT,
    test_run_id TEXT
)
```

**User Feedback Table**

```sql
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    feature TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    context TEXT
)
```

#### Key Methods

```python
from app.evaluation import EvaluationStore

store = EvaluationStore("data/evaluation.db")

# Create test case
test_id = store.create_test_case(
    test_name="Test Sentiment Analysis",
    test_type="accuracy",
    description="Test sentiment analysis accuracy",
    input_data={"text": "This is great!"},
    expected_output={"sentiment": "positive"},
    tags=["sentiment", "nlp"]
)

# Create test run
run_id = store.create_test_run(
    run_name="Sentiment Test Run",
    test_suite="sentiment_tests"
)

# Store test result
result_id = store.store_test_result(
    run_id=run_id,
    test_case_id=test_id,
    status="passed",
    actual_output={"sentiment": "positive"},
    execution_time_ms=150
)

# Store metric
metric_id = store.store_metric(
    metric_name="accuracy",
    metric_category="performance",
    value=95.5,
    target_value=90.0,
    unit="percent"
)

# Store user feedback
feedback_id = store.store_user_feedback(
    user_id="user1",
    feature="email_analysis",
    rating=5,
    feedback_text="Excellent feature!"
)
```

### 2. Test Runner (`test_runner.py`)

The Test Runner executes evaluation tests and collects results.

#### Features

**Register Test Functions**

```python
from app.evaluation import TestRunner, EvaluationStore

store = EvaluationStore()
runner = TestRunner(store)

# Register a test function
def test_sentiment_analysis(input_data):
    """Test function for sentiment analysis."""
    from app.analytics import EmailAnalyzer

    analyzer = EmailAnalyzer()
    result = analyzer.analyze_sentiment(input_data['text'])

    return {
        'sentiment': result['label'],
        'score': result['score']
    }

runner.register_test_function('sentiment', test_sentiment_analysis)
```

**Run Test Suite**

```python
# Run all tests of a specific type
result = runner.run_test_suite(
    suite_name="sentiment_suite",
    test_type="sentiment"
)

print(f"Total tests: {result['total_tests']}")
print(f"Passed: {result['passed_tests']}")
print(f"Failed: {result['failed_tests']}")
print(f"Pass rate: {result['passed_tests']/result['total_tests']*100:.1f}%")
```

**Run Single Test**

```python
# Run a specific test by ID
result = runner.run_single_test_by_id(test_case_id)

print(f"Status: {result['status']}")
print(f"Execution time: {result['execution_time_ms']}ms")
```

**Get Test Summary**

```python
# Get detailed summary of a test run
summary = runner.get_test_run_summary(run_id)

print(f"Pass rate: {summary['pass_rate']:.1f}%")
print(f"Average execution time: {summary['avg_execution_time_ms']:.1f}ms")
```

### 3. Metrics Calculator (`metrics_calculator.py`)

The Metrics Calculator computes various evaluation metrics.

#### Features

**Accuracy Metrics**

```python
from app.evaluation import MetricsCalculator, EvaluationStore

store = EvaluationStore()
calculator = MetricsCalculator(store)

# Calculate accuracy
accuracy = calculator.calculate_accuracy(correct=85, total=100)
print(f"Accuracy: {accuracy}%")

# Calculate precision, recall, F1
metrics = calculator.calculate_precision_recall_f1(
    true_positives=80,
    false_positives=10,
    false_negatives=20
)
print(f"Precision: {metrics['precision']:.2f}")
print(f"Recall: {metrics['recall']:.2f}")
print(f"F1 Score: {metrics['f1_score']:.2f}")
```

**Performance Metrics**

```python
# Calculate performance metrics from execution times
execution_times = [100, 150, 200, 120, 180, 160, 140, 190, 110, 170]

perf_metrics = calculator.calculate_performance_metrics(execution_times)

print(f"Min: {perf_metrics['min']}ms")
print(f"Max: {perf_metrics['max']}ms")
print(f"Mean: {perf_metrics['mean']:.1f}ms")
print(f"Median: {perf_metrics['median']}ms")
print(f"P95: {perf_metrics['p95']}ms")
print(f"P99: {perf_metrics['p99']}ms")
```

**Test Run Metrics**

```python
# Calculate comprehensive metrics for a test run
metrics = calculator.calculate_test_run_metrics(run_id)

print(f"Accuracy: {metrics['accuracy']:.1f}%")
print(f"Pass rate: {metrics['pass_rate']:.1f}%")
print(f"Avg execution time: {metrics['performance']['mean']:.1f}ms")
```

**Feature Metrics**

```python
# Calculate metrics for a feature based on user feedback
feature_metrics = calculator.calculate_feature_metrics("email_analysis")

print(f"Total feedback: {feature_metrics['total_feedback']}")
print(f"Average rating: {feature_metrics['average_rating']:.2f}/5")
print(f"Satisfaction rate: {feature_metrics['satisfaction_rate']:.1f}%")
```

**Trend Analysis**

```python
# Analyze metric trends over time
trend = calculator.calculate_trend_metrics(
    metric_name="accuracy",
    metric_category="performance",
    limit=10
)

print(f"Current value: {trend['current_value']}")
print(f"Trend: {trend['trend']}")  # improving/declining/stable
print(f"Average: {trend['avg_value']:.2f}")
```

### 4. LLM Evaluator (`llm_evaluator.py`)

The LLM Evaluator uses LLM-as-judge approach for qualitative evaluation.

#### Features

**Response Quality Evaluation**

```python
from app.evaluation import LLMEvaluator, EvaluationStore

store = EvaluationStore()
evaluator = LLMEvaluator(store)

# Evaluate response quality
evaluation = evaluator.evaluate_response_quality(
    prompt="Summarize this email",
    response="The email discusses project deadlines and budget approval.",
    criteria={
        'relevance': 'How relevant is the response?',
        'accuracy': 'How accurate is the information?',
        'completeness': 'How complete is the response?',
        'clarity': 'How clear is the response?'
    }
)

print(f"Overall score: {evaluation['overall_score']}/5")
print(f"Relevance: {evaluation['scores']['relevance']}/5")
print(f"Summary: {evaluation['summary']}")
```

**Sentiment Analysis Evaluation**

```python
# Evaluate sentiment analysis accuracy
evaluation = evaluator.evaluate_sentiment_accuracy(
    text="This is absolutely terrible!",
    predicted_sentiment="negative",
    predicted_score=-0.8
)

print(f"Actual sentiment: {evaluation['actual_sentiment']}")
print(f"Prediction correct: {evaluation['prediction_correct']}")
print(f"Confidence: {evaluation['confidence']}")
print(f"Explanation: {evaluation['explanation']}")
```

**Classification Evaluation**

```python
# Evaluate classification accuracy
evaluation = evaluator.evaluate_classification_accuracy(
    text="Let's schedule a meeting tomorrow at 3pm",
    predicted_category="meeting",
    possible_categories=["meeting", "task", "question", "notification"]
)

print(f"Correct category: {evaluation['correct_category']}")
print(f"Prediction correct: {evaluation['prediction_correct']}")
```

**Summary Quality Evaluation**

```python
# Evaluate summary quality
evaluation = evaluator.evaluate_summary_quality(
    original_text="Long email text here...",
    summary="Brief summary here..."
)

print(f"Overall score: {evaluation['overall_score']}/5")
print(f"Accuracy: {evaluation['scores']['accuracy']}/5")
print(f"Completeness: {evaluation['scores']['completeness']}/5")
print(f"Feedback: {evaluation['feedback']}")
```

**Batch Evaluation**

```python
# Perform batch evaluation
evaluations = [
    {
        'text': "This is great!",
        'predicted_sentiment': "positive",
        'predicted_score': 0.9
    },
    {
        'text': "This is terrible!",
        'predicted_sentiment': "negative",
        'predicted_score': -0.8
    }
]

results = evaluator.batch_evaluate(
    evaluations=evaluations,
    evaluation_type='sentiment'
)

print(f"Accuracy: {results['accuracy']:.1f}%")
print(f"Correct predictions: {results['correct_predictions']}/{results['total_evaluations']}")
```

## Integration Examples

### 1. Complete Evaluation Pipeline

```python
from app.evaluation import (
    EvaluationStore,
    TestRunner,
    MetricsCalculator,
    LLMEvaluator
)

# Initialize components
store = EvaluationStore()
runner = TestRunner(store)
calculator = MetricsCalculator(store)
evaluator = LLMEvaluator(store)

# Register test function
def test_email_analysis(input_data):
    from app.analytics import EmailAnalyzer

    analyzer = EmailAnalyzer()
    return analyzer.analyze_email(
        email_id=input_data['email_id'],
        user_id=input_data['user_id'],
        sender=input_data['sender'],
        subject=input_data['subject'],
        body=input_data['body']
    )

runner.register_test_function('email_analysis', test_email_analysis)

# Create test cases
test_id = store.create_test_case(
    test_name="Test Email Analysis",
    test_type="email_analysis",
    description="Test complete email analysis",
    input_data={
        'email_id': 'test123',
        'user_id': 'user1',
        'sender': 'sender@example.com',
        'subject': 'Project Update',
        'body': 'Here is the latest update...'
    },
    expected_output={
        'sentiment': {'label': 'positive'},
        'category': 'general'
    }
)

# Run tests
result = runner.run_test_suite("email_analysis_suite", test_type="email_analysis")

# Calculate metrics
metrics = calculator.calculate_test_run_metrics(result['run_id'])

# Print results
print(f"Tests run: {metrics['total_tests']}")
print(f"Accuracy: {metrics['accuracy']:.1f}%")
print(f"Avg execution time: {metrics['performance']['mean']:.1f}ms")
```

### 2. Automated Evaluation Job

```python
from app.scheduler import JobScheduler
from app.evaluation import TestRunner, EvaluationStore

store = EvaluationStore()
runner = TestRunner(store)
scheduler = JobScheduler()

def daily_evaluation_job():
    """Run daily evaluation tests."""

    # Run test suite
    result = runner.run_test_suite("daily_suite")

    # Calculate metrics
    calculator = MetricsCalculator(store)
    metrics = calculator.calculate_test_run_metrics(result['run_id'])

    # Alert if accuracy drops below threshold
    if metrics['accuracy'] < 85.0:
        print(f"ALERT: Accuracy dropped to {metrics['accuracy']:.1f}%")

    return metrics

# Schedule daily evaluation
scheduler.create_job(
    user_id='system',
    job_type='evaluation',
    job_name='Daily Evaluation',
    schedule_type='cron',
    schedule_value='0 2 * * *',  # 2 AM daily
    job_config={}
)
```

### 3. User Feedback Collection

```python
from app.evaluation import EvaluationStore, MetricsCalculator

store = EvaluationStore()
calculator = MetricsCalculator(store)

def collect_user_feedback(user_id, feature, rating, feedback_text):
    """Collect and analyze user feedback."""

    # Store feedback
    feedback_id = store.store_user_feedback(
        user_id=user_id,
        feature=feature,
        rating=rating,
        feedback_text=feedback_text
    )

    # Calculate feature metrics
    metrics = calculator.calculate_feature_metrics(feature)

    # Alert if rating drops
    if metrics['average_rating'] < 3.5:
        print(f"ALERT: {feature} rating dropped to {metrics['average_rating']:.2f}")

    return metrics

# Collect feedback
metrics = collect_user_feedback(
    user_id="user1",
    feature="email_analysis",
    rating=5,
    feedback_text="Very helpful!"
)

print(f"Average rating: {metrics['average_rating']:.2f}/5")
```

## Best Practices

### 1. Test Case Design

- **Clear naming**: Use descriptive test names
- **Comprehensive coverage**: Test edge cases and normal cases
- **Isolated tests**: Each test should be independent
- **Realistic data**: Use real-world examples

### 2. Metrics Selection

- **Relevant metrics**: Choose metrics that matter for your use case
- **Baseline targets**: Set realistic target values
- **Trend monitoring**: Track metrics over time
- **Actionable insights**: Focus on metrics you can improve

### 3. LLM Evaluation

- **Consistent criteria**: Use the same evaluation criteria
- **Low temperature**: Use low temperature for consistent evaluation
- **Multiple evaluations**: Run multiple evaluations for reliability
- **Human validation**: Validate LLM evaluations with human review

### 4. Continuous Evaluation

- **Automated testing**: Run tests automatically on schedule
- **Regression testing**: Test after each change
- **Performance monitoring**: Track execution times
- **User feedback**: Continuously collect and analyze feedback

## Testing

Run the comprehensive test suite:

```bash
python tests/test_evaluation.py
```

Test coverage:

- ✅ Evaluation Store: 5 tests
- ✅ Test Runner: 3 tests
- ✅ Metrics Calculator: 4 tests
- **Total: 12 tests, all passing**

## Performance Considerations

### Database Optimization

- Indexes on frequently queried columns
- Batch inserts for multiple test results
- Periodic cleanup of old test data

### Test Execution

- Parallel test execution for large suites
- Timeout protection for long-running tests
- Resource cleanup after each test

### Metrics Calculation

- Cache frequently accessed metrics
- Pre-compute aggregations
- Efficient SQL queries

## Troubleshooting

### Issue: Tests taking too long

**Solution**: Implement parallel execution or optimize test functions.

```python
# Use timeout for long-running tests
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Test execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout
```

### Issue: LLM evaluation inconsistent

**Solution**: Use lower temperature and multiple evaluations.

```python
# Run multiple evaluations and average
results = []
for _ in range(3):
    result = evaluator.evaluate_response_quality(...)
    results.append(result['overall_score'])

avg_score = sum(results) / len(results)
```

### Issue: Database growing too large

**Solution**: Implement data retention policy.

```python
# Clean up old test runs (older than 30 days)
import time
from datetime import timedelta

cutoff = time.time() - timedelta(days=30).total_seconds()

# Delete old test runs and results
# (Implement in evaluation_store.py)
```

## Future Enhancements

1. **A/B Testing**: Compare different model versions
2. **Regression Detection**: Automatically detect performance regressions
3. **Visual Dashboards**: Web-based evaluation dashboards
4. **Custom Metrics**: User-defined evaluation metrics
5. **Integration Testing**: End-to-end workflow testing
6. **Load Testing**: Performance under high load
7. **Adversarial Testing**: Test with challenging inputs

## Summary

Phase 12 provides a production-ready evaluation framework with:

✅ **Test Management**: Create, store, and manage test cases
✅ **Test Execution**: Automated test running with detailed results
✅ **Metrics Calculation**: Comprehensive performance and accuracy metrics
✅ **LLM Evaluation**: LLM-as-judge for qualitative assessment
✅ **User Feedback**: Collect and analyze user satisfaction
✅ **SQLite Persistence**: All evaluation data stored in database
✅ **Comprehensive Tests**: 12 tests covering all components
✅ **Easy Integration**: Simple APIs for common use cases

The evaluation framework enables continuous quality monitoring, performance tracking, and data-driven improvements to the AI Executive Assistant.
