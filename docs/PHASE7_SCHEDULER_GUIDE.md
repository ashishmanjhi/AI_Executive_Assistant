# Phase 7: Scheduled Autonomous Jobs - Complete Guide

## Overview

Phase 7 implements a robust job scheduling system that enables the AI Executive Assistant to run tasks automatically on a schedule. The system uses APScheduler for job execution and SQLite for persistent storage.

## Architecture

### Components

1. **Job Store** (`app/scheduler/job_store.py`)
   - SQLite-based persistent storage for job configurations
   - Execution history tracking
   - Job statistics and analytics

2. **Job Scheduler** (`app/scheduler/job_scheduler.py`)
   - APScheduler backend for job execution
   - Support for cron, interval, and one-time scheduling
   - Job lifecycle management (add, remove, pause, resume)

3. **Predefined Jobs** (`app/scheduler/predefined_jobs.py`)
   - Common scheduled tasks (daily digest, hourly checks, etc.)
   - Easy registration and configuration

## Features

### Schedule Types

1. **Cron-based Scheduling**
   - Traditional cron expressions
   - Precise time-based execution
   - Example: Daily at 9:00 AM, Weekly on Sundays

2. **Interval-based Scheduling**
   - Recurring execution at fixed intervals
   - Example: Every hour, Every 30 minutes

3. **One-time Scheduling**
   - Execute once at a specific date/time
   - Useful for reminders and one-off tasks

### Job Management

- **Add Jobs**: Register new scheduled tasks
- **Remove Jobs**: Delete scheduled tasks
- **Pause Jobs**: Temporarily disable execution
- **Resume Jobs**: Re-enable paused jobs
- **Update Jobs**: Modify job configuration

### Persistence

- Job configurations stored in SQLite
- Execution history tracked
- Jobs automatically restored on restart
- Statistics and success rates calculated

## Usage

### Basic Example

```python
from app.scheduler.job_scheduler import (
    JobScheduler,
    ScheduledJob,
    ScheduleType,
    create_scheduler
)

# Create scheduler
scheduler = create_scheduler()

# Define job function
def my_task(**kwargs):
    print(f"Task executed with params: {kwargs}")
    return {"status": "success"}

# Register job function
scheduler.register_job_function("my_task_type", my_task)

# Create scheduled job
job = ScheduledJob(
    id="my_daily_task",
    name="My Daily Task",
    description="Runs every day at 9 AM",
    job_type="my_task_type",
    schedule_type=ScheduleType.CRON,
    schedule_config={"hour": 9, "minute": 0},
    job_function=my_task,
    job_config={"param1": "value1"},
    enabled=True
)

# Add and start
scheduler.add_job(job)
scheduler.start()
```

### Interval Scheduling

```python
# Run every hour
job = ScheduledJob(
    id="hourly_check",
    name="Hourly Check",
    job_type="check",
    schedule_type=ScheduleType.INTERVAL,
    schedule_config={"hours": 1},
    job_function=check_function,
    enabled=True
)

# Run every 30 minutes
job = ScheduledJob(
    id="frequent_check",
    name="Frequent Check",
    job_type="check",
    schedule_type=ScheduleType.INTERVAL,
    schedule_config={"minutes": 30},
    job_function=check_function,
    enabled=True
)
```

### Cron Scheduling

```python
# Daily at 9:00 AM
schedule_config = {"hour": 9, "minute": 0}

# Every Monday at 10:00 AM
schedule_config = {"day_of_week": "mon", "hour": 10, "minute": 0}

# Every Sunday at 6:00 PM
schedule_config = {"day_of_week": "sun", "hour": 18, "minute": 0}

# Every minute
schedule_config = {"minute": "*"}

# Every 15 minutes
schedule_config = {"minute": "*/15"}
```

### Job Management

```python
# Pause a job
scheduler.pause_job("my_daily_task")

# Resume a job
scheduler.resume_job("my_daily_task")

# Remove a job
scheduler.remove_job("my_daily_task")

# Get job information
job_info = scheduler.get_job_info("my_daily_task")
print(f"Next run: {job_info['next_run_time']}")
print(f"Success rate: {job_info['stats']['success_rate']}%")

# Get all jobs
all_jobs = scheduler.get_all_jobs()
for job in all_jobs:
    print(f"{job['name']}: {job['enabled']}")

# Get execution history
history = scheduler.get_job_history("my_daily_task", limit=10)
for execution in history:
    print(f"{execution['started_at']}: {execution['status']}")
```

## Predefined Jobs

### Available Jobs

1. **Daily Email Digest**
   - Generates daily email summary
   - Default: 9:00 AM
   - Configurable email count

2. **Hourly Email Check**
   - Checks for new important emails
   - Default: Every hour
   - Flags important messages

3. **Weekly Summary**
   - Generates weekly activity report
   - Default: Sunday 6:00 PM
   - Includes important events

4. **Morning Briefing**
   - Daily morning briefing
   - Default: 8:00 AM
   - Emails, calendar, tasks

### Using Predefined Jobs

```python
from app.scheduler.predefined_jobs import register_default_jobs

# Register all default jobs
register_default_jobs(scheduler)

# Enable specific job
scheduler.resume_job("daily_email_digest")

# Configure job parameters
scheduler.job_store.update_job(
    "daily_email_digest",
    job_config={"max_emails": 30}
)
```

### Creating Custom Jobs

```python
def custom_job_function(**kwargs):
    """Custom job implementation"""
    try:
        # Your job logic here
        result = perform_task()

        # Record in memory if needed
        from app.agents.memory_agent import create_memory_agent
        agent = create_memory_agent(session_id="scheduler_custom")
        agent.record_event(
            event_type="custom_task",
            description="Custom task completed",
            importance=7
        )

        return {"status": "success", "result": result}

    except Exception as e:
        return {"status": "error", "error": str(e)}

# Register and schedule
scheduler.register_job_function("custom", custom_job_function)

job = ScheduledJob(
    id="custom_task",
    name="Custom Task",
    job_type="custom",
    schedule_type=ScheduleType.CRON,
    schedule_config={"hour": 14, "minute": 30},
    job_function=custom_job_function,
    enabled=True
)

scheduler.add_job(job)
```

## Job Store API

### Adding Jobs

```python
from app.scheduler.job_store import JobStore

store = JobStore()

store.add_job(
    job_id="unique_id",
    name="Job Name",
    job_type="job_type",
    schedule_type="cron",
    schedule_config={"hour": 9, "minute": 0},
    description="Job description",
    job_config={"param": "value"},
    enabled=True
)
```

### Querying Jobs

```python
# Get specific job
job = store.get_job("unique_id")

# Get all jobs
all_jobs = store.get_all_jobs()

# Get enabled jobs only
enabled_jobs = store.get_all_jobs(enabled_only=True)
```

### Execution History

```python
# Record execution
store.add_execution(
    job_id="unique_id",
    started_at=datetime.now(),
    completed_at=datetime.now(),
    status="success",
    result="Task completed"
)

# Get execution history
history = store.get_job_executions("unique_id", limit=50)

# Get statistics
stats = store.get_execution_stats("unique_id")
print(f"Total runs: {stats['total_runs']}")
print(f"Success rate: {stats['success_rate']}%")
```

## Database Schema

### Tables

1. **jobs**
   - id (PRIMARY KEY)
   - name, description
   - job_type, schedule_type
   - schedule_config (JSON)
   - job_config (JSON)
   - enabled (BOOLEAN)
   - created_at, updated_at
   - last_run, next_run

2. **job_executions**
   - id (PRIMARY KEY)
   - job_id (FOREIGN KEY)
   - started_at, completed_at
   - status (success/failed)
   - result, error

### Database Location

- **Production**: `data/scheduler.db`
- **Test**: `data/test_scheduler.db`

## Testing

### Run Quick Test

```bash
python test_scheduler_quick.py
```

### Test Coverage

The test suite validates:

1. ✅ Job Store (SQLite persistence)
2. ✅ Job Scheduler (APScheduler backend)
3. ✅ Interval-based scheduling
4. ✅ Cron-based scheduling
5. ✅ Job execution and history
6. ✅ Job management (pause/resume/remove)
7. ✅ Predefined jobs
8. ✅ Execution statistics

### Expected Output

```
[SUCCESS] All tests completed successfully!

Scheduler Features Tested:
  [OK] Job Store (SQLite persistence)
  [OK] Job Scheduler (APScheduler backend)
  [OK] Interval-based scheduling
  [OK] Job execution and history
  [OK] Job management (pause/resume)
  [OK] Predefined jobs registration
  [OK] Execution statistics
```

## Integration Examples

### Example 1: Daily Email Digest

```python
from app.scheduler import create_scheduler, register_default_jobs

# Create and start scheduler
scheduler = create_scheduler()
register_default_jobs(scheduler)

# Enable daily digest
scheduler.resume_job("daily_email_digest")

# Start scheduler
scheduler.start()

# Scheduler runs in background
# Daily digest will be generated at 9:00 AM
```

### Example 2: Custom Monitoring Job

```python
def monitor_system(**kwargs):
    """Monitor system health"""
    from app.memory.memory_store import MemoryStore

    memory = MemoryStore()
    stats = memory.get_memory_stats()

    # Check if memory is growing too large
    if stats['total_messages'] > 10000:
        # Alert or cleanup
        print("Warning: High message count")

    return {"status": "success", "stats": stats}

# Schedule to run every 6 hours
scheduler.register_job_function("monitor", monitor_system)

job = ScheduledJob(
    id="system_monitor",
    name="System Monitor",
    job_type="monitor",
    schedule_type=ScheduleType.INTERVAL,
    schedule_config={"hours": 6},
    job_function=monitor_system,
    enabled=True
)

scheduler.add_job(job)
```

### Example 3: Scheduled Reminders

```python
from datetime import datetime, timedelta

def send_reminder(**kwargs):
    """Send a reminder"""
    message = kwargs.get("message", "Reminder!")
    print(f"REMINDER: {message}")
    return {"status": "success"}

# Schedule one-time reminder for tomorrow at 2 PM
tomorrow_2pm = datetime.now().replace(hour=14, minute=0) + timedelta(days=1)

scheduler.register_job_function("reminder", send_reminder)

job = ScheduledJob(
    id="meeting_reminder",
    name="Meeting Reminder",
    job_type="reminder",
    schedule_type=ScheduleType.DATE,
    schedule_config={"run_date": tomorrow_2pm},
    job_function=send_reminder,
    job_config={"message": "Team meeting in 1 hour"},
    enabled=True
)

scheduler.add_job(job)
```

## Best Practices

### 1. Job Function Design

```python
def good_job_function(**kwargs):
    """Well-designed job function"""
    try:
        # Get parameters
        param = kwargs.get("param", "default")

        # Perform task
        result = do_work(param)

        # Return structured result
        return {
            "status": "success",
            "result": result,
            "timestamp": str(datetime.now())
        }

    except Exception as e:
        # Handle errors gracefully
        logger.error(f"Job failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
```

### 2. Error Handling

- Always return a result dictionary
- Include status ("success" or "error")
- Log errors for debugging
- Don't let exceptions crash the scheduler

### 3. Resource Management

- Keep job functions lightweight
- Avoid long-running operations
- Use timeouts for external calls
- Clean up resources properly

### 4. Scheduling Strategy

- Use cron for time-specific tasks
- Use intervals for recurring checks
- Consider timezone implications
- Avoid overlapping executions

## Troubleshooting

### Issue: Job not executing

**Check:**

1. Is the scheduler started? `scheduler.start()`
2. Is the job enabled? `job_info['enabled']`
3. Is the job function registered?
4. Check logs for errors

### Issue: Jobs not persisting

**Solution:**

- Ensure database directory exists
- Check file permissions
- Verify database path is correct

### Issue: High CPU usage

**Solution:**

- Reduce job frequency
- Optimize job functions
- Use longer intervals
- Disable unnecessary jobs

## Future Enhancements

Potential improvements for Phase 7:

1. **Job Dependencies**
   - Chain jobs together
   - Conditional execution

2. **Job Priorities**
   - Priority queue for execution
   - Resource allocation

3. **Distributed Scheduling**
   - Multi-instance coordination
   - Load balancing

4. **Advanced Monitoring**
   - Real-time job status
   - Performance metrics
   - Alert system

5. **Job Templates**
   - Reusable job configurations
   - Parameter validation

## Dependencies

```
apscheduler>=3.11.2
tzlocal>=5.4.3
```

## Files Created

- `app/scheduler/job_store.py` - Job persistence
- `app/scheduler/job_scheduler.py` - Scheduler implementation
- `app/scheduler/predefined_jobs.py` - Default jobs
- `app/scheduler/__init__.py` - Module exports
- `test_scheduler_quick.py` - Quick test suite
- `PHASE7_SCHEDULER_GUIDE.md` - This guide

## Conclusion

Phase 7 provides a comprehensive scheduling system that enables autonomous task execution. The system is:

- ✅ Persistent (survives restarts)
- ✅ Flexible (multiple schedule types)
- ✅ Manageable (pause/resume/remove)
- ✅ Observable (execution history and stats)
- ✅ Extensible (easy to add new jobs)

The scheduler integrates seamlessly with the memory system (Phase 6) and provides a foundation for autonomous agent behavior.

---

**Next Phase**: Phase 8 - Multi-Step Planning (See FUTURE_PHASES_ROADMAP.md)
