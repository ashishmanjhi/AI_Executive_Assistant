# Phase 10: Observability & Monitoring - Complete Guide

## Overview

Phase 10 implements a comprehensive observability and monitoring system for the AI Executive Assistant. This system provides real-time insights into system health, performance metrics, and operational behavior through three core components:

1. **Metrics Collector**: Track and analyze system metrics (counters, gauges, histograms)
2. **Structured Logger**: Enhanced logging with context and persistence
3. **Health Checker**: Automated system health monitoring

## Architecture

```
app/observability/
├── __init__.py           # Package initialization
├── metrics_collector.py  # Metrics collection and storage
├── logger.py            # Structured logging system
└── health_checker.py    # Health monitoring system

tests/
└── test_observability.py # Comprehensive test suite
```

## Components

### 1. Metrics Collector (`metrics_collector.py`)

The Metrics Collector tracks three types of metrics:

#### Metric Types

**Counters**: Monotonically increasing values (e.g., request counts, error counts)

```python
from app.observability import MetricsCollector

collector = MetricsCollector()

# Increment counter
collector.increment_counter("api_requests", value=1.0, labels={"endpoint": "/chat"})
collector.increment_counter("errors", labels={"type": "validation"})
```

**Gauges**: Point-in-time values that can go up or down (e.g., memory usage, queue size)

```python
# Set gauge value
collector.set_gauge("memory_usage_mb", value=512.5, labels={"process": "main"})
collector.set_gauge("active_connections", value=42)
```

**Histograms**: Distribution of values (e.g., response times, request sizes)

```python
# Record histogram observation
collector.observe_histogram("response_time_ms", value=125.3, labels={"endpoint": "/search"})
collector.observe_histogram("request_size_bytes", value=2048)
```

#### Querying Metrics

```python
# Query specific metrics
metrics = collector.query_metrics(
    metric_name="api_requests",
    metric_type="counter",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
    limit=100
)

# Get metric summary (count, sum, avg, min, max)
summary = collector.get_metric_summary(
    metric_name="response_time_ms",
    start_time=datetime.now() - timedelta(days=1),
    end_time=datetime.now()
)
print(f"Average response time: {summary['avg']:.2f}ms")
```

#### Features

- **Thread-safe**: Uses threading locks for concurrent access
- **SQLite persistence**: All metrics stored in database
- **Label support**: Add dimensions to metrics for filtering
- **Aggregation**: Built-in summary statistics
- **Time-based queries**: Filter metrics by time range

### 2. Structured Logger (`logger.py`)

Enhanced logging system with context, persistence, and structured data.

#### Basic Usage

```python
from app.observability import StructuredLogger

logger = StructuredLogger()

# Different log levels
logger.debug("Debug message", user_id="user123", action="search")
logger.info("User logged in", user_id="user456", ip="192.168.1.1")
logger.warning("Rate limit approaching", user_id="user789", requests=95)
logger.error("Database connection failed", db="primary", retry_count=3)
logger.critical("System overload", cpu_percent=98, memory_percent=95)
```

#### Exception Logging

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error(
        "Operation failed",
        exception=e,
        user_id="user123",
        operation="data_processing"
    )
```

#### Querying Logs

```python
# Query logs by level and time
logs = logger.query_logs(
    level="ERROR",
    start_time=datetime.now() - timedelta(hours=24),
    end_time=datetime.now(),
    limit=50
)

# Query logs by user
user_logs = logger.query_logs(
    user_id="user123",
    start_time=datetime.now() - timedelta(days=7),
    limit=100
)
```

#### Features

- **Structured context**: Add arbitrary key-value pairs to logs
- **Exception tracking**: Automatic exception type, message, and traceback capture
- **Database persistence**: All logs stored in SQLite
- **Request tracking**: Built-in request_id for tracing
- **Error counting**: Track error counts per user
- **Flexible queries**: Filter by level, time, user, or any context field

### 3. Health Checker (`health_checker.py`)

Automated system health monitoring with default and custom checks.

#### Default Health Checks

The system includes three default checks:

**Disk Space Check**

```python
from app.observability import HealthChecker

checker = HealthChecker()

# Run disk space check
result = checker.run_check("disk_space")
print(f"Status: {result['status']}")  # healthy/degraded/unhealthy
print(f"Free space: {result['details']['free_gb']:.2f} GB")
```

**Memory Check**

```python
# Run memory check
result = checker.run_check("memory")
print(f"Memory usage: {result['details']['percent']:.1f}%")
```

**Database Check**

```python
# Run database check
result = checker.run_check("database")
print(f"Database: {result['status']}")
```

#### Custom Health Checks

Register custom health checks for your specific needs:

```python
def check_api_health():
    """Custom check for external API availability"""
    try:
        response = requests.get("https://api.example.com/health", timeout=5)
        if response.status_code == 200:
            return {
                "status": "healthy",
                "details": {"response_time_ms": response.elapsed.total_seconds() * 1000}
            }
        else:
            return {
                "status": "degraded",
                "details": {"status_code": response.status_code}
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "details": {"error": str(e)}
        }

# Register custom check
checker.register_check("external_api", check_api_health)

# Run custom check
result = checker.run_check("external_api")
```

#### Running All Checks

```python
# Run all registered checks
results = checker.run_all_checks()

for check_name, result in results.items():
    print(f"{check_name}: {result['status']}")
    if result['status'] != 'healthy':
        print(f"  Details: {result['details']}")
```

#### Health History

```python
# Get health check history
history = checker.get_health_history("disk_space", limit=10)

for record in history:
    print(f"{record['timestamp']}: {record['status']}")
    print(f"  Free space: {record['details']['free_gb']:.2f} GB")
```

#### Features

- **Default checks**: Disk, memory, and database monitoring out-of-the-box
- **Custom checks**: Register domain-specific health checks
- **Status levels**: healthy, degraded, unhealthy
- **History tracking**: All check results stored in database
- **Batch execution**: Run all checks at once
- **Detailed results**: Rich details for each check

## Integration Examples

### 1. API Endpoint Monitoring

```python
from app.observability import MetricsCollector, StructuredLogger
import time

collector = MetricsCollector()
logger = StructuredLogger()

def api_endpoint(request):
    start_time = time.time()

    try:
        # Increment request counter
        collector.increment_counter(
            "api_requests",
            labels={"endpoint": request.path, "method": request.method}
        )

        # Process request
        result = process_request(request)

        # Record response time
        response_time = (time.time() - start_time) * 1000
        collector.observe_histogram(
            "response_time_ms",
            value=response_time,
            labels={"endpoint": request.path}
        )

        # Log success
        logger.info(
            "Request processed",
            endpoint=request.path,
            response_time_ms=response_time,
            user_id=request.user_id
        )

        return result

    except Exception as e:
        # Increment error counter
        collector.increment_counter(
            "api_errors",
            labels={"endpoint": request.path, "error_type": type(e).__name__}
        )

        # Log error
        logger.error(
            "Request failed",
            exception=e,
            endpoint=request.path,
            user_id=request.user_id
        )

        raise
```

### 2. Background Job Monitoring

```python
from app.observability import MetricsCollector, StructuredLogger, HealthChecker

collector = MetricsCollector()
logger = StructuredLogger()
checker = HealthChecker()

def scheduled_job():
    """Example scheduled job with monitoring"""

    # Check system health before running
    health = checker.run_all_checks()
    if any(r['status'] == 'unhealthy' for r in health.values()):
        logger.warning("System unhealthy, skipping job", health=health)
        return

    logger.info("Starting scheduled job", job="email_digest")

    try:
        # Track job execution
        collector.increment_counter("jobs_started", labels={"job": "email_digest"})

        # Execute job
        result = generate_email_digest()

        # Track success
        collector.increment_counter("jobs_completed", labels={"job": "email_digest"})
        collector.set_gauge("last_job_success", value=time.time())

        logger.info("Job completed", job="email_digest", emails_processed=result['count'])

    except Exception as e:
        collector.increment_counter("jobs_failed", labels={"job": "email_digest"})
        logger.error("Job failed", exception=e, job="email_digest")
```

### 3. System Resource Monitoring

```python
from app.observability import MetricsCollector, HealthChecker
import psutil
import time

collector = MetricsCollector()
checker = HealthChecker()

def monitor_system_resources():
    """Periodic system resource monitoring"""

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    collector.set_gauge("cpu_usage_percent", value=cpu_percent)

    # Memory usage
    memory = psutil.virtual_memory()
    collector.set_gauge("memory_usage_percent", value=memory.percent)
    collector.set_gauge("memory_available_mb", value=memory.available / (1024 * 1024))

    # Disk usage
    disk = psutil.disk_usage('/')
    collector.set_gauge("disk_usage_percent", value=disk.percent)
    collector.set_gauge("disk_free_gb", value=disk.free / (1024 ** 3))

    # Run health checks
    health = checker.run_all_checks()

    # Track overall health status
    unhealthy_count = sum(1 for r in health.values() if r['status'] == 'unhealthy')
    collector.set_gauge("unhealthy_checks", value=unhealthy_count)

# Run every 60 seconds
while True:
    monitor_system_resources()
    time.sleep(60)
```

## Database Schema

### Metrics Table

```sql
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    metric_name TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    labels TEXT
)
```

### Logs Table

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    request_id TEXT,
    user_id TEXT
)
```

### Health Checks Table

```sql
CREATE TABLE health_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    check_name TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    duration_ms REAL
)
```

## Best Practices

### 1. Metric Naming

Use clear, hierarchical names:

```python
# Good
collector.increment_counter("api.requests.total")
collector.increment_counter("api.errors.validation")
collector.observe_histogram("api.response_time.ms")

# Avoid
collector.increment_counter("requests")
collector.increment_counter("errors")
```

### 2. Label Usage

Use labels for dimensions, not for high-cardinality data:

```python
# Good - finite set of values
collector.increment_counter("requests", labels={"endpoint": "/chat", "method": "POST"})

# Avoid - unbounded values
collector.increment_counter("requests", labels={"user_id": "user123456"})
```

### 3. Log Levels

Use appropriate log levels:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical messages for severe failures

### 4. Health Check Frequency

Balance monitoring frequency with system load:

```python
# Critical checks: every 30 seconds
# Standard checks: every 60 seconds
# Expensive checks: every 5 minutes
```

### 5. Context Enrichment

Add relevant context to logs:

```python
logger.info(
    "User action",
    user_id=user_id,
    action="search",
    query=query,
    results_count=len(results),
    response_time_ms=response_time
)
```

## Testing

Run the comprehensive test suite:

```bash
python tests/test_observability.py
```

Test coverage:

- ✅ Metrics Collector: 7 tests
- ✅ Structured Logger: 5 tests
- ✅ Health Checker: 5 tests
- **Total: 16 tests, all passing**

## Performance Considerations

### Metrics Collection

- Thread-safe operations with minimal locking
- Batch inserts for high-throughput scenarios
- Indexed queries for fast retrieval

### Logging

- Asynchronous logging for high-volume scenarios
- Configurable log retention policies
- Efficient JSON serialization

### Health Checks

- Timeout protection for external checks
- Cached results for expensive checks
- Parallel execution of independent checks

## Troubleshooting

### High Database Size

If the observability database grows too large:

```python
# Clean old metrics (older than 30 days)
collector.cleanup_old_metrics(days=30)

# Clean old logs (older than 7 days)
logger.cleanup_old_logs(days=7)

# Clean old health checks (older than 14 days)
checker.cleanup_old_checks(days=14)
```

### Performance Impact

If observability impacts performance:

1. Reduce metric collection frequency
2. Use sampling for high-volume metrics
3. Implement async logging
4. Batch metric writes

### Missing psutil

If you get `ModuleNotFoundError: No module named 'psutil'`:

```bash
pip install psutil
```

## Future Enhancements

Potential improvements for future phases:

1. **Alerting System**: Trigger alerts based on metrics/health
2. **Dashboard**: Web-based visualization of metrics
3. **Distributed Tracing**: Track requests across services
4. **Metric Aggregation**: Pre-compute aggregations for performance
5. **Export Formats**: Prometheus, OpenTelemetry, etc.
6. **Anomaly Detection**: ML-based anomaly detection on metrics

## Summary

Phase 10 provides a production-ready observability system with:

✅ **Metrics Collection**: Track counters, gauges, and histograms
✅ **Structured Logging**: Enhanced logging with context and persistence
✅ **Health Monitoring**: Automated system health checks
✅ **SQLite Persistence**: All data stored in database
✅ **Thread Safety**: Safe for concurrent access
✅ **Comprehensive Tests**: 16 tests, all passing
✅ **Easy Integration**: Simple APIs for common use cases

The system is ready for production use and provides the foundation for monitoring the AI Executive Assistant's health, performance, and behavior.
