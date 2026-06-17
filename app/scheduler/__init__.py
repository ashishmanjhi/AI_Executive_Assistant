"""
Scheduler Module
Autonomous job scheduling and execution
"""

from app.scheduler.job_scheduler import (
    JobScheduler,
    ScheduledJob,
    create_scheduler,
    get_scheduler
)
from app.scheduler.job_store import JobStore
from app.scheduler.predefined_jobs import (
    daily_email_digest_job,
    hourly_email_check_job,
    weekly_summary_job,
    register_default_jobs
)

__all__ = [
    "JobScheduler",
    "ScheduledJob",
    "JobStore",
    "create_scheduler",
    "get_scheduler",
    "daily_email_digest_job",
    "hourly_email_check_job",
    "weekly_summary_job",
    "register_default_jobs"
]

# Made with Bob
