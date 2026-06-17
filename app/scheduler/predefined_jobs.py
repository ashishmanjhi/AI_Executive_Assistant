"""
Predefined Jobs
Common scheduled tasks for the AI Executive Assistant
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.tools.email_tools import generate_daily_digest
from app.gmail import fetch_recent_emails
from app.agents.memory_agent import create_memory_agent
from app.scheduler.job_scheduler import ScheduledJob, ScheduleType, JobScheduler

logger = logging.getLogger(__name__)


def daily_email_digest_job(**kwargs) -> Dict[str, Any]:
    """
    Generate and send daily email digest
    
    Runs daily at configured time (default: 9:00 AM)
    """
    try:
        logger.info("Starting daily email digest job")
        
        # Get configuration
        max_emails = kwargs.get("max_emails", 20)
        
        # Generate digest
        # Note: generate_daily_digest is a LangChain tool, so we need to invoke it
        digest_result = generate_daily_digest.invoke({"max_emails": max_emails})
        
        # Parse the result (it returns a string, not a dict)
        digest = {
            "summary": digest_result,
            "emails": []  # Tool returns formatted string, not structured data
        }
        
        # Store in memory for user to review
        agent = create_memory_agent(session_id="scheduler_daily_digest")
        agent.record_event(
            event_type="daily_digest",
            description=f"Generated daily email digest with {len(digest.get('emails', []))} emails",
            importance=7,
            context={"digest_summary": digest.get("summary", "")}
        )
        
        logger.info(f"Daily digest generated: {len(digest.get('emails', []))} emails")
        
        return {
            "status": "success",
            "emails_count": len(digest.get("emails", [])),
            "summary": digest.get("summary", "")
        }
        
    except Exception as e:
        logger.error(f"Daily digest job failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def hourly_email_check_job(**kwargs) -> Dict[str, Any]:
    """
    Check for new emails and flag important ones
    
    Runs every hour
    """
    try:
        logger.info("Starting hourly email check job")
        
        # Get configuration
        max_results = kwargs.get("max_results", 10)
        
        # Fetch recent emails
        emails = fetch_recent_emails(max_results=max_results)
        
        # Count important emails (those with IMPORTANT label or from VIPs)
        important_count = sum(
            1 for email in emails 
            if "IMPORTANT" in email.get("labels", [])
        )
        
        # Record in memory if there are important emails
        if important_count > 0:
            agent = create_memory_agent(session_id="scheduler_email_check")
            agent.record_event(
                event_type="important_emails",
                description=f"Found {important_count} important emails",
                importance=8,
                context={"total_emails": len(emails), "important_count": important_count}
            )
        
        logger.info(f"Email check completed: {len(emails)} emails, {important_count} important")
        
        return {
            "status": "success",
            "total_emails": len(emails),
            "important_emails": important_count
        }
        
    except Exception as e:
        logger.error(f"Hourly email check job failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def weekly_summary_job(**kwargs) -> Dict[str, Any]:
    """
    Generate weekly activity summary
    
    Runs weekly on configured day (default: Sunday at 6:00 PM)
    """
    try:
        logger.info("Starting weekly summary job")
        
        # Get memory agent
        agent = create_memory_agent(session_id="scheduler_weekly_summary")
        
        # Get memory statistics
        stats = agent.get_memory_stats()
        
        # Get recent important events
        from app.memory.memory_store import MemoryStore
        memory = MemoryStore()
        events = memory.get_episodic_memories(min_importance=7, limit=20)
        
        # Create summary
        summary = {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "total_conversations": stats.get("total_messages", 0),
            "important_events": len(events),
            "events": [
                {
                    "type": event["event_type"],
                    "description": event["description"],
                    "importance": event["importance"]
                }
                for event in events[:10]  # Top 10 events
            ]
        }
        
        # Record summary
        agent.record_event(
            event_type="weekly_summary",
            description=f"Generated weekly summary: {len(events)} important events",
            importance=8,
            context=summary
        )
        
        logger.info(f"Weekly summary generated: {len(events)} important events")
        
        return {
            "status": "success",
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Weekly summary job failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def morning_briefing_job(**kwargs) -> Dict[str, Any]:
    """
    Generate morning briefing with emails, calendar, and tasks
    
    Runs daily at configured time (default: 8:00 AM)
    """
    try:
        logger.info("Starting morning briefing job")
        
        # Get recent emails
        emails = fetch_recent_emails(max_results=10)
        important_emails = [e for e in emails if "IMPORTANT" in e.get("labels", [])]
        
        # Get memory agent
        agent = create_memory_agent(session_id="scheduler_morning_briefing")
        
        # Get today's important events from memory
        from app.memory.memory_store import MemoryStore
        memory = MemoryStore()
        
        # Get user preferences
        prefs = memory.get_all_preferences()
        
        # Create briefing
        briefing = {
            "date": datetime.now().strftime("%Y-%m-%d %A"),
            "emails": {
                "total": len(emails),
                "important": len(important_emails)
            },
            "preferences": prefs,
            "greeting": f"Good morning! Here's your briefing for {datetime.now().strftime('%A, %B %d')}"
        }
        
        # Record briefing
        agent.record_event(
            event_type="morning_briefing",
            description=f"Generated morning briefing: {len(important_emails)} important emails",
            importance=7,
            context=briefing
        )
        
        logger.info("Morning briefing generated")
        
        return {
            "status": "success",
            "briefing": briefing
        }
        
    except Exception as e:
        logger.error(f"Morning briefing job failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def register_default_jobs(scheduler: JobScheduler):
    """
    Register default scheduled jobs
    
    Args:
        scheduler: JobScheduler instance
    """
    
    # Register job functions
    scheduler.register_job_function("daily_digest", daily_email_digest_job)
    scheduler.register_job_function("hourly_check", hourly_email_check_job)
    scheduler.register_job_function("weekly_summary", weekly_summary_job)
    scheduler.register_job_function("morning_briefing", morning_briefing_job)
    
    # Define default jobs
    default_jobs = [
        ScheduledJob(
            id="daily_email_digest",
            name="Daily Email Digest",
            description="Generate daily email digest at 9:00 AM",
            job_type="daily_digest",
            schedule_type=ScheduleType.CRON,
            schedule_config={
                "hour": 9,
                "minute": 0
            },
            job_function=daily_email_digest_job,
            job_config={"max_emails": 20},
            enabled=False  # Disabled by default, user can enable
        ),
        ScheduledJob(
            id="hourly_email_check",
            name="Hourly Email Check",
            description="Check for new important emails every hour",
            job_type="hourly_check",
            schedule_type=ScheduleType.INTERVAL,
            schedule_config={
                "hours": 1
            },
            job_function=hourly_email_check_job,
            job_config={"max_results": 10},
            enabled=False  # Disabled by default
        ),
        ScheduledJob(
            id="weekly_summary",
            name="Weekly Summary",
            description="Generate weekly activity summary on Sunday at 6:00 PM",
            job_type="weekly_summary",
            schedule_type=ScheduleType.CRON,
            schedule_config={
                "day_of_week": "sun",
                "hour": 18,
                "minute": 0
            },
            job_function=weekly_summary_job,
            enabled=False  # Disabled by default
        ),
        ScheduledJob(
            id="morning_briefing",
            name="Morning Briefing",
            description="Generate morning briefing at 8:00 AM",
            job_type="morning_briefing",
            schedule_type=ScheduleType.CRON,
            schedule_config={
                "hour": 8,
                "minute": 0
            },
            job_function=morning_briefing_job,
            enabled=False  # Disabled by default
        )
    ]
    
    # Add jobs to scheduler
    for job in default_jobs:
        scheduler.add_job(job, replace_existing=True)
    
    logger.info(f"Registered {len(default_jobs)} default jobs")

# Made with Bob
