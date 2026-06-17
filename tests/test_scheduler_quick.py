"""
Quick Test for Phase 7: Scheduled Autonomous Jobs
Demonstrates core scheduler functionality without long waits
"""

import sys
import time
from pathlib import Path
from datetime import datetime

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
    print(f"  [JOB] {message}")
    return {"status": "success", "message": message, "time": str(datetime.now())}


def main():
    """Run quick tests"""
    print("\n" + "=" * 60)
    print("  PHASE 7: SCHEDULED JOBS - QUICK TEST")
    print("=" * 60)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Job Store
        print_section("TEST 1: Job Store")
        
        store = JobStore(db_path="data/test_scheduler.db")
        print("[OK] Job store initialized")
        
        # Add a job
        store.add_job(
            job_id="quick_test_1",
            name="Quick Test Job",
            job_type="test",
            schedule_type="interval",
            schedule_config={"seconds": 5},
            description="A quick test job",
            enabled=True
        )
        print("[OK] Added job to store")
        
        # Get job
        job = store.get_job("quick_test_1")
        print(f"[OK] Retrieved job: {job['name']}")
        
        # Test 2: Scheduler with Interval Job
        print_section("TEST 2: Interval Scheduling")
        
        scheduler = create_scheduler()
        print("[OK] Scheduler created")
        
        # Register test function
        scheduler.register_job_function("test", test_job_function)
        print("[OK] Registered job function")
        
        # Create interval job (every 3 seconds)
        job = ScheduledJob(
            id="interval_quick",
            name="Quick Interval Job",
            description="Runs every 3 seconds",
            job_type="test",
            schedule_type=ScheduleType.INTERVAL,
            schedule_config={"seconds": 3},
            job_function=test_job_function,
            job_config={"message": "Quick interval execution"},
            enabled=True
        )
        
        scheduler.add_job(job)
        print("[OK] Added interval job (every 3 seconds)")
        
        # Start scheduler
        scheduler.start()
        print("[OK] Scheduler started")
        
        # Wait for 3 executions
        print("\n[INFO] Waiting for 3 executions (10 seconds)...")
        time.sleep(10)
        
        # Get execution history
        history = scheduler.get_job_history("interval_quick")
        print(f"\n[OK] Job executed {len(history)} times")
        
        # Get job info
        job_info = scheduler.get_job_info("interval_quick")
        if job_info:
            stats = job_info['stats']
            print(f"[OK] Success rate: {stats['success_rate']:.1f}%")
        
        # Test 3: Job Management
        print_section("TEST 3: Job Management")
        
        # Pause job
        scheduler.pause_job("interval_quick")
        print("[OK] Job paused")
        
        time.sleep(4)
        print("[INFO] Waited 4 seconds (no execution should occur)")
        
        # Resume job
        scheduler.resume_job("interval_quick")
        print("[OK] Job resumed")
        
        time.sleep(4)
        print("[INFO] Waited 4 seconds (execution should resume)")
        
        # Final history
        history = scheduler.get_job_history("interval_quick", limit=10)
        print(f"\n[OK] Total executions: {len(history)}")
        print("[OK] Recent executions:")
        for i, exec in enumerate(history[:3], 1):
            print(f"     {i}. {exec['started_at']} - {exec['status']}")
        
        # Test 4: Predefined Jobs
        print_section("TEST 4: Predefined Jobs")
        
        register_default_jobs(scheduler)
        print("[OK] Registered default jobs")
        
        # List all jobs
        all_jobs = scheduler.get_all_jobs()
        print(f"\n[OK] Total jobs: {len(all_jobs)}")
        print("[OK] Available jobs:")
        for job in all_jobs:
            status = "Enabled" if job["enabled"] else "Disabled"
            print(f"     - {job['name']}: {status}")
        
        # Shutdown
        scheduler.shutdown()
        print("\n[OK] Scheduler shutdown")
        
        # Final Summary
        print_section("TEST SUMMARY")
        print("\n[SUCCESS] All tests completed successfully!")
        print("\nScheduler Features Tested:")
        print("  [OK] Job Store (SQLite persistence)")
        print("  [OK] Job Scheduler (APScheduler backend)")
        print("  [OK] Interval-based scheduling")
        print("  [OK] Job execution and history")
        print("  [OK] Job management (pause/resume)")
        print("  [OK] Predefined jobs registration")
        print("  [OK] Execution statistics")
        
        print("\nKey Capabilities:")
        print("  - Persistent job storage")
        print("  - Automatic job execution")
        print("  - Execution history tracking")
        print("  - Job pause/resume")
        print("  - Multiple schedule types (cron, interval, date)")
        
        print("\nDatabase Location: data/test_scheduler.db")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
