"""
Job Scheduler
APScheduler-based job scheduling system with persistence
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from app.scheduler.job_store import JobStore

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Supported schedule types"""
    CRON = "cron"
    INTERVAL = "interval"
    DATE = "date"  # One-time execution


class JobStatus(str, Enum):
    """Job execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


@dataclass
class ScheduledJob:
    """Scheduled job configuration"""
    id: str
    name: str
    job_type: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    job_function: Callable
    description: Optional[str] = None
    job_config: Optional[Dict[str, Any]] = None
    enabled: bool = True


class JobScheduler:
    """
    Job Scheduler with APScheduler backend
    
    Features:
    - Cron-based scheduling
    - Interval-based scheduling
    - One-time scheduled execution
    - Job persistence
    - Execution history
    - Error handling and retry
    """
    
    def __init__(self, job_store: Optional[JobStore] = None):
        """Initialize job scheduler"""
        self.job_store = job_store or JobStore()
        self.scheduler = BackgroundScheduler()
        self.job_functions: Dict[str, Callable] = {}
        
        # Add event listeners
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
        
        logger.info("Job scheduler initialized")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Job scheduler started")
            
            # Load and schedule persisted jobs
            self._load_persisted_jobs()
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Job scheduler shutdown")
    
    def register_job_function(self, job_type: str, function: Callable):
        """Register a job function for a job type"""
        self.job_functions[job_type] = function
        logger.info(f"Registered job function for type: {job_type}")
    
    def add_job(
        self,
        job: ScheduledJob,
        replace_existing: bool = False
    ) -> bool:
        """
        Add a new scheduled job
        
        Args:
            job: ScheduledJob configuration
            replace_existing: Replace if job with same ID exists
        
        Returns:
            True if job was added successfully
        """
        try:
            # Store job configuration
            success = self.job_store.add_job(
                job_id=job.id,
                name=job.name,
                job_type=job.job_type,
                schedule_type=job.schedule_type.value,
                schedule_config=job.schedule_config,
                description=job.description,
                job_config=job.job_config,
                enabled=job.enabled
            )
            
            if not success and not replace_existing:
                logger.warning(f"Job {job.id} already exists")
                return False
            
            if not success and replace_existing:
                self.job_store.update_job(
                    job_id=job.id,
                    name=job.name,
                    job_type=job.job_type,
                    schedule_type=job.schedule_type.value,
                    schedule_config=job.schedule_config,
                    description=job.description,
                    job_config=job.job_config,
                    enabled=job.enabled
                )
            
            # Store job function reference by job_id
            self.job_functions[job.id] = job.job_function
            
            # Also store by job_type for loading persisted jobs
            if job.job_type not in self.job_functions:
                self.job_functions[job.job_type] = job.job_function
            
            # Schedule job if enabled
            if job.enabled:
                self._schedule_job(job)
            
            logger.info(f"Added job: {job.id} ({job.name})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding job {job.id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            # Remove from scheduler
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Remove from store
            success = self.job_store.delete_job(job_id)
            
            # Remove function reference
            if job_id in self.job_functions:
                del self.job_functions[job_id]
            
            logger.info(f"Removed job: {job_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a job"""
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.pause_job(job_id)
            
            self.job_store.update_job(job_id, enabled=False)
            logger.info(f"Paused job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.resume_job(job_id)
            else:
                # Job not in scheduler, reload it
                job_config = self.job_store.get_job(job_id)
                if job_config:
                    self._schedule_job_from_config(job_config)
            
            self.job_store.update_job(job_id, enabled=True)
            logger.info(f"Resumed job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming job {job_id}: {e}")
            return False
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        job_config = self.job_store.get_job(job_id)
        if not job_config:
            return None
        
        # Get scheduler info
        scheduler_job = self.scheduler.get_job(job_id)
        if scheduler_job:
            job_config["next_run_time"] = scheduler_job.next_run_time
        
        # Get execution stats
        stats = self.job_store.get_execution_stats(job_id)
        job_config["stats"] = stats
        
        return job_config
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs with their information"""
        jobs = self.job_store.get_all_jobs()
        
        for job in jobs:
            # Add scheduler info
            scheduler_job = self.scheduler.get_job(job["id"])
            if scheduler_job:
                # APScheduler Job object has next_run_time as a property
                try:
                    job["next_run_time"] = str(scheduler_job.next_run_time) if hasattr(scheduler_job, 'next_run_time') else None
                except:
                    job["next_run_time"] = None
            
            # Add execution stats
            stats = self.job_store.get_execution_stats(job["id"])
            job["stats"] = stats
        
        return jobs
    
    def get_job_history(self, job_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history for a job"""
        return self.job_store.get_job_executions(job_id, limit)
    
    def _schedule_job(self, job: ScheduledJob):
        """Schedule a job with APScheduler"""
        trigger = self._create_trigger(job.schedule_type, job.schedule_config)
        
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            id=job.id,
            name=job.name,
            args=[job.id],
            replace_existing=True
        )
        
        logger.info(f"Scheduled job: {job.id}")
    
    def _schedule_job_from_config(self, job_config: Dict[str, Any]):
        """Schedule a job from stored configuration"""
        job_type = job_config["job_type"]
        
        # Get job function
        if job_type in self.job_functions:
            job_function = self.job_functions[job_type]
        else:
            logger.warning(f"No function registered for job type: {job_type}")
            return
        
        # Create ScheduledJob
        job = ScheduledJob(
            id=job_config["id"],
            name=job_config["name"],
            job_type=job_type,
            schedule_type=ScheduleType(job_config["schedule_type"]),
            schedule_config=job_config["schedule_config"],
            job_function=job_function,
            description=job_config.get("description"),
            job_config=job_config.get("job_config"),
            enabled=job_config["enabled"]
        )
        
        if job.enabled:
            self._schedule_job(job)
    
    def _create_trigger(self, schedule_type: ScheduleType, config: Dict[str, Any]):
        """Create APScheduler trigger from configuration"""
        if schedule_type == ScheduleType.CRON:
            return CronTrigger(**config)
        elif schedule_type == ScheduleType.INTERVAL:
            return IntervalTrigger(**config)
        elif schedule_type == ScheduleType.DATE:
            return DateTrigger(**config)
        else:
            raise ValueError(f"Unsupported schedule type: {schedule_type}")
    
    def _execute_job(self, job_id: str):
        """Execute a job"""
        started_at = datetime.now()
        
        logger.info(f"Executing job: {job_id}")
        
        try:
            # Get job function
            if job_id not in self.job_functions:
                raise ValueError(f"No function registered for job: {job_id}")
            
            job_function = self.job_functions[job_id]
            
            # Get job config
            job_config = self.job_store.get_job(job_id)
            job_params = job_config.get("job_config") if job_config else None
            
            # Execute job with params if available
            if job_params:
                result = job_function(**job_params)
            else:
                result = job_function()
            
            # Record successful execution
            completed_at = datetime.now()
            self.job_store.add_execution(
                job_id=job_id,
                started_at=started_at,
                completed_at=completed_at,
                status=JobStatus.SUCCESS.value,
                result=str(result) if result else None
            )
            
            # Update last run time
            self.job_store.update_job_schedule(job_id, last_run=completed_at)
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            # Record failed execution
            completed_at = datetime.now()
            self.job_store.add_execution(
                job_id=job_id,
                started_at=started_at,
                completed_at=completed_at,
                status=JobStatus.FAILED.value,
                error=str(e)
            )
            
            logger.error(f"Job {job_id} failed: {e}")
            raise
    
    def _job_executed_listener(self, event):
        """Listen to job execution events"""
        job_id = event.job_id
        
        if event.exception:
            logger.error(f"Job {job_id} raised exception: {event.exception}")
        else:
            logger.debug(f"Job {job_id} executed successfully")
    
    def _load_persisted_jobs(self):
        """Load and schedule persisted jobs"""
        jobs = self.job_store.get_all_jobs(enabled_only=True)
        
        for job_config in jobs:
            try:
                self._schedule_job_from_config(job_config)
            except Exception as e:
                logger.error(f"Error loading job {job_config['id']}: {e}")
        
        logger.info(f"Loaded {len(jobs)} persisted jobs")


# Global scheduler instance
_scheduler_instance: Optional[JobScheduler] = None


def create_scheduler(job_store: Optional[JobStore] = None) -> JobScheduler:
    """Create and return a new scheduler instance"""
    global _scheduler_instance
    _scheduler_instance = JobScheduler(job_store=job_store)
    return _scheduler_instance


def get_scheduler() -> Optional[JobScheduler]:
    """Get the global scheduler instance"""
    return _scheduler_instance

# Made with Bob
