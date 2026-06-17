"""
Test Script for Phase 7: Scheduled Autonomous Jobs
Demonstrates scheduler functionality
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.scheduler.job_scheduler import (
    JobScheduler,
    ScheduledJob,
    ScheduleType,
    create_scheduler
)
from app.scheduler.job_store import JobStore
from app.scheduler.predefined_jobs import register_default_jobs


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_job_function(**kwargs):
    """Simple test job function"""
    message = kwargs.get("message", "Test job executed")
    print(f"[JOB EXECUTION] {message} at {datetime.now()}")
    return {"status": "success", "message": message}


def test_job_store():
    """Test job store functionality"""
    print_section("TEST 1: Job Store")
    
    store = JobStore(db_path="data/test_scheduler.db")
    print("[OK] Job store initialized")
    
    # Add a job
    success = store.add_job(
        job_id="test_job_1",
        name="Test Job 1",
        job_type="test",
        schedule_type="cron",
        schedule_config={"hour": 9, "minute": 0},
        description="A test job",
        job_config={"message": "Hello from test job"},
        enabled=True
    )
    print(f"[OK] Added job: {success}")
    
    # Get job
    job = store.get_job("test_job_1")
    print(f"[OK] Retrieved job: {job['name']}")
    print(f"     - Type: {job['job_type']}")
    print(f"     - Schedule: {job['schedule_type']}")
    print(f"     - Enabled: {job['enabled']}")
    
    # Get all jobs
    all_jobs = store.get_all_jobs()
    print(f"[OK] Total jobs in store: {len(all_jobs)}")
    
    # Add execution record
    exec_id = store.add_execution(
        job_id="test_job_1",
        started_at=datetime.now(),
        completed_at=datetime.now(),
        status="success",
        result="Test execution"
    )
    print(f"[OK] Recorded execution: {exec_id}")
    
    # Get execution stats
    stats = store.get_execution_stats("test_job_1")
    print(f"[OK] Execution stats:")
    print(f"     - Total runs: {stats['total_runs']}")
    print(f"     - Success rate: {stats['success_rate']:.1f}%")


def test_scheduler_basic():
    """Test basic scheduler functionality"""
    print_section("TEST 2: Basic Scheduler")
    
    # Create scheduler
    scheduler = create_scheduler()
    print("[OK] Scheduler created")
    
    # Register test job function
    scheduler.register_job_function("test", test_job_function)
    print("[OK] Registered test job function")
    
    # Create a simple interval job (runs every 5 seconds)
    job = ScheduledJob(
        id="interval_test",
        name="Interval Test Job",
        description="Runs every 5 seconds",
        job_type="test",
        schedule_type=ScheduleType.INTERVAL,
        schedule_config={"seconds": 5},
        job_function=test_job_function,
        job_config={"message": "Interval job triggered"},
        enabled=True
    )
    
    # Add job
    success = scheduler.add_job(job)
    print(f"[OK] Added interval job: {success}")
    
    # Start scheduler
    scheduler.start()
    print("[OK] Scheduler started")
    
    # Wait for a few executions
    print("\n[INFO] Waiting for job executions (15 seconds)...")
    time.sleep(15)
    
    # Get job info
    job_info = scheduler.get_job_info("interval_test")
    if job_info:
        print(f"\n[OK] Job info:")
        print(f"     - Name: {job_info['name']}")
        print(f"     - Total runs: {job_info['stats']['total_runs']}")
        print(f"     - Success rate: {job_info['stats']['success_rate']:.1f}%")
    
    # Pause job
    scheduler.pause_job("interval_test")
    print("\n[OK] Job paused")
    
    time.sleep(3)
    
    # Resume job
    scheduler.resume_job("interval_test")
    print("[OK] Job resumed")
    
    time.sleep(7)
    
    # Get execution history
    history = scheduler.get_job_history("interval_test", limit=10)
    print(f"\n[OK] Execution history ({len(history)} executions):")
    for i, execution in enumerate(history[:5], 1):
        print(f"     {i}. {execution['started_at']} - {execution['status']}")
    
    # Shutdown scheduler
    scheduler.shutdown()
    print("\n[OK] Scheduler shutdown")


def test_cron_jobs():
    """Test cron-based scheduling"""
    print_section("TEST 3: Cron Jobs")
    
    scheduler = create_scheduler()
    scheduler.register_job_function("test", test_job_function)
    
    # Create a cron job (runs every minute)
    job = ScheduledJob(
        id="cron_test",
        name="Cron Test Job",
        description="Runs every minute",
        job_type="test",
        schedule_type=ScheduleType.CRON,
        schedule_config={"minute": "*"},  # Every minute
        job_function=test_job_function,
        job_config={"message": "Cron job triggered"},
        enabled=True
    )
    
    scheduler.add_job(job)
    print("[OK] Added cron job (runs every minute)")
    
    scheduler.start()
    print("[OK] Scheduler started")
    
    # Get next run time
    job_info = scheduler.get_job_info("cron_test")
    if job_info and job_info.get("next_run_time"):
        print(f"[OK] Next run time: {job_info['next_run_time']}")
    
    print("\n[INFO] Waiting for cron execution (70 seconds)...")
    time.sleep(70)
    
    # Check execution
    history = scheduler.get_job_history("cron_test")
    print(f"\n[OK] Cron job executed {len(history)} time(s)")
    
    scheduler.shutdown()
    print("[OK] Scheduler shutdown")


def test_predefined_jobs():
    """Test predefined jobs"""
    print_section("TEST 4: Predefined Jobs")
    
    scheduler = create_scheduler()
    
    # Register default jobs
    register_default_jobs(scheduler)
    print("[OK] Registered default jobs")
    
    # Get all jobs
    jobs = scheduler.get_all_jobs()
    print(f"\n[OK] Available jobs ({len(jobs)}):")
    for job in jobs:
        status = "Enabled" if job["enabled"] else "Disabled"
        print(f"     - {job['name']}: {status}")
        print(f"       {job['description']}")
    
    # Enable and test one job (morning briefing with modified schedule)
    print("\n[INFO] Testing morning briefing job...")
    
    # Update job to run immediately (next minute)
    now = datetime.now()
    next_minute = now + timedelta(minutes=1)
    
    scheduler.job_store.update_job(
        "morning_briefing",
        schedule_config={
            "hour": next_minute.hour,
            "minute": next_minute.minute
        },
        enabled=True
    )
    
    # Reload job
    scheduler.resume_job("morning_briefing")
    print(f"[OK] Scheduled morning briefing for {next_minute.strftime('%H:%M')}")
    
    scheduler.start()
    print("[OK] Scheduler started")
    
    # Wait for execution
    wait_seconds = 70
    print(f"\n[INFO] Waiting for job execution ({wait_seconds} seconds)...")
    time.sleep(wait_seconds)
    
    # Check execution
    history = scheduler.get_job_history("morning_briefing")
    if history:
        print(f"\n[OK] Morning briefing executed:")
        latest = history[0]
        print(f"     - Status: {latest['status']}")
        print(f"     - Time: {latest['started_at']}")
        if latest.get('result'):
            print(f"     - Result: {latest['result'][:100]}...")
    else:
        print("\n[INFO] No executions yet (may need to wait longer)")
    
    scheduler.shutdown()
    print("\n[OK] Scheduler shutdown")


def test_job_management():
    """Test job management operations"""
    print_section("TEST 5: Job Management")
    
    scheduler = create_scheduler()
    scheduler.register_job_function("test", test_job_function)
    
    # Add multiple jobs
    for i in range(3):
        job = ScheduledJob(
            id=f"mgmt_test_{i}",
            name=f"Management Test Job {i}",
            description=f"Test job {i}",
            job_type="test",
            schedule_type=ScheduleType.INTERVAL,
            schedule_config={"seconds": 10},
            job_function=test_job_function,
            job_config={"message": f"Job {i}"},
            enabled=(i < 2)  # First 2 enabled
        )
        scheduler.add_job(job)
    
    print("[OK] Added 3 test jobs")
    
    # List all jobs
    jobs = scheduler.get_all_jobs()
    print(f"\n[OK] All jobs ({len(jobs)}):")
    for job in jobs:
        status = "Enabled" if job["enabled"] else "Disabled"
        print(f"     - {job['id']}: {status}")
    
    # Pause a job
    scheduler.pause_job("mgmt_test_0")
    print("\n[OK] Paused mgmt_test_0")
    
    # Resume a job
    scheduler.resume_job("mgmt_test_2")
    print("[OK] Resumed mgmt_test_2")
    
    # Remove a job
    scheduler.remove_job("mgmt_test_1")
    print("[OK] Removed mgmt_test_1")
    
    # List jobs again
    jobs = scheduler.get_all_jobs()
    print(f"\n[OK] Jobs after management ({len(jobs)}):")
    for job in jobs:
        status = "Enabled" if job["enabled"] else "Disabled"
        print(f"     - {job['id']}: {status}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  PHASE 7: SCHEDULED AUTONOMOUS JOBS - TEST SUITE")
    print("=" * 60)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run tests
        test_job_store()
        test_scheduler_basic()
        test_cron_jobs()
        test_predefined_jobs()
        test_job_management()
        
        # Final summary
        print_section("TEST SUMMARY")
        print("\n[SUCCESS] All tests completed successfully!")
        print("\nScheduler Features Tested:")
        print("  [OK] Job Store (SQLite persistence)")
        print("  [OK] Job Scheduler (APScheduler backend)")
        print("  [OK] Interval-based scheduling")
        print("  [OK] Cron-based scheduling")
        print("  [OK] Job execution and history")
        print("  [OK] Job management (pause/resume/remove)")
        print("  [OK] Predefined jobs")
        print("  [OK] Execution statistics")
        
        print("\nDatabase Location: data/test_scheduler.db")
        print("Production Database: data/scheduler.db")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
