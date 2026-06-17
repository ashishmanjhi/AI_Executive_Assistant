# AI Executive Assistant - Future Phases Roadmap

## Table of Contents

1. [Phase 6: Persistent Memory System](#phase-6-persistent-memory-system)
2. [Phase 7: Scheduled Jobs & Automation](#phase-7-scheduled-jobs--automation)
3. [Phase 8: Multi-Step Planning Engine](#phase-8-multi-step-planning-engine)
4. [Phase 9: Calendar Integration](#phase-9-calendar-integration)
5. [Phase 10: Observability & Monitoring](#phase-10-observability--monitoring)
6. [Phase 11: Email Intelligence & Analytics](#phase-11-email-intelligence--analytics)
7. [Phase 12: Evaluation Framework](#phase-12-evaluation-framework)
8. [Phase 13: Voice Interface](#phase-13-voice-interface)
9. [Production Features](#production-features)

---

## Phase 6: Persistent Memory System

### Overview

Implement a sophisticated memory system using MySQL to store conversation history, user preferences, learned patterns, and contextual information across sessions.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory System Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   LangGraph  │─────▶│    Memory    │─────▶│   MySQL   │ │
│  │   Workflow   │      │   Manager    │      │  Database │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │   Memory     │             │       │
│         └─────────────▶│   Retriever  │◀────────────┘       │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Embeddings  │                     │
│                        │   (OpenAI)   │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Memory Types:
┌────────────────┬──────────────────┬─────────────────────────┐
│ Short-term     │ Working Memory   │ Recent conversation     │
│ Long-term      │ Episodic Memory  │ Past interactions       │
│ Semantic       │ Knowledge Base   │ Facts & preferences     │
│ Procedural     │ Task Memory      │ How to do things        │
└────────────────┴──────────────────┴─────────────────────────┘
```

### Database Schema

```sql
-- Conversations table
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    summary TEXT,
    metadata JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Messages table
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding BLOB,
    metadata JSON,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User preferences table
CREATE TABLE user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT NOT NULL,
    category VARCHAR(100),
    confidence_score FLOAT DEFAULT 1.0,
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_pref (user_id, preference_key),
    INDEX idx_user_id (user_id),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Episodic memory table
CREATE TABLE episodic_memory (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    context JSON,
    importance_score FLOAT DEFAULT 0.5,
    occurred_at TIMESTAMP NOT NULL,
    embedding BLOB,
    INDEX idx_user_id (user_id),
    INDEX idx_event_type (event_type),
    INDEX idx_occurred_at (occurred_at),
    INDEX idx_importance (importance_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Semantic facts table
CREATE TABLE semantic_facts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    fact_type VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    predicate VARCHAR(255) NOT NULL,
    object TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_fact_type (fact_type),
    INDEX idx_subject (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Task memory table
CREATE TABLE task_memory (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    task_steps JSON NOT NULL,
    success_count INT DEFAULT 0,
    failure_count INT DEFAULT 0,
    avg_duration_seconds INT,
    last_executed TIMESTAMP NULL,
    metadata JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_task_name (task_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Database Setup**

- Create MySQL database and tables
- Set up connection pooling
- Configure indexes for performance

**Step 2: Memory Manager**

- Implement conversation tracking
- Add preference learning
- Build episodic memory storage
- Create semantic fact storage
- Implement task memory

**Step 3: LangGraph Integration**

- Add memory loading node
- Implement context enrichment
- Create memory saving node
- Add checkpointing with MySQL

**Step 4: Testing**

- Unit tests for each memory type
- Integration tests with workflows
- Performance benchmarks
- Load testing

### Success Criteria

- [ ] All memory types (short-term, long-term, semantic, procedural) implemented
- [ ] Conversation history persisted across sessions
- [ ] User preferences learned and applied automatically
- [ ] Episodic memory retrieval with >80% relevance
- [ ] Semantic facts stored and queried efficiently
- [ ] Task memory improves execution over time
- [ ] Memory retrieval latency <100ms for 95th percentile
- [ ] Database handles 1000+ concurrent users

---

## Phase 7: Scheduled Jobs & Automation

### Overview

Implement a robust job scheduling system for automated tasks like daily digests, follow-ups, reminders, and periodic maintenance.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Scheduler Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   APScheduler│─────▶│  Job Queue   │─────▶│  Workers  │ │
│  │   (Cron)     │      │   (MySQL)    │      │  (Celery) │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │  Job Store   │             │       │
│         └─────────────▶│   (MySQL)    │◀────────────┘       │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Execution   │                     │
│                        │    Logs      │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Job Types:
┌────────────────┬──────────────────┬─────────────────────────┐
│ Daily Digest   │ 8:00 AM Daily    │ Email summary           │
│ Follow-ups     │ Every 2 hours    │ Check pending items     │
│ Reminders      │ User-defined     │ Custom notifications    │
│ Maintenance    │ 2:00 AM Daily    │ Cleanup & optimization  │
│ Analytics      │ Weekly           │ Generate reports        │
└────────────────┴──────────────────┴─────────────────────────┘
```

### Database Schema

```sql
-- Scheduled jobs table
CREATE TABLE scheduled_jobs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    job_type VARCHAR(100) NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    schedule_type ENUM('cron', 'interval', 'date') NOT NULL,
    schedule_value VARCHAR(255) NOT NULL,
    job_config JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    next_run TIMESTAMP NULL,
    last_run TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_job_type (job_type),
    INDEX idx_next_run (next_run),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Job execution history
CREATE TABLE job_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NULL,
    status ENUM('running', 'success', 'failed', 'cancelled') NOT NULL,
    result TEXT,
    error_message TEXT,
    execution_time_ms INT,
    FOREIGN KEY (job_id) REFERENCES scheduled_jobs(id) ON DELETE CASCADE,
    INDEX idx_job_id (job_id),
    INDEX idx_started_at (started_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Job queue table (for distributed processing)
CREATE TABLE job_queue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(36) NOT NULL,
    priority INT DEFAULT 5,
    scheduled_for TIMESTAMP NOT NULL,
    claimed_by VARCHAR(255) NULL,
    claimed_at TIMESTAMP NULL,
    status ENUM('pending', 'claimed', 'processing', 'completed', 'failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES scheduled_jobs(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_scheduled_for (scheduled_for),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User reminders table
CREATE TABLE user_reminders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    remind_at TIMESTAMP NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(255),
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_remind_at (remind_at),
    INDEX idx_completed (is_completed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Scheduler Setup**

- Install APScheduler and Celery
- Configure MySQL job store
- Set up worker processes
- Implement job queue

**Step 2: Job Types**

- Daily digest generator
- Follow-up checker
- Reminder system
- Maintenance tasks
- Analytics reports

**Step 3: Job Management**

- Create/update/delete jobs
- Pause/resume functionality
- Retry logic
- Error handling

**Step 4: Monitoring**

- Execution logging
- Performance metrics
- Failure alerts
- Dashboard

### Code Example: Daily Digest Job

```python
# app/scheduler/jobs/daily_digest.py
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def generate_daily_digest(user_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and send daily email digest."""
    logger.info(f"Generating daily digest for user {user_id}")

    # Get emails from last 24 hours
    since_date = datetime.now() - timedelta(days=1)
    emails = fetch_recent_emails(user_id, since_date)

    # Categorize emails
    categories = categorize_emails(emails)

    # Generate HTML digest
    digest_html = create_digest_html(categories)

    # Send email
    send_digest_email(user_id, digest_html, config)

    return {
        'emails_processed': len(emails),
        'categories': {k: len(v) for k, v in categories.items()},
        'sent_at': datetime.now().isoformat()
    }

# Register job
scheduler.register_handler('daily_digest', generate_daily_digest)

# Create job for user
scheduler.create_job(
    user_id='user@example.com',
    job_type='daily_digest',
    job_name='Morning Email Digest',
    schedule_type='cron',
    schedule_value='0 8 * * *',  # 8 AM daily
    job_config={'recipient_email': 'user@example.com'}
)
```

### Success Criteria

- [ ] APScheduler integrated with MySQL job store
- [ ] Daily digest sent reliably at scheduled time
- [ ] Follow-up system identifies pending items
- [ ] Reminders trigger at correct times
- [ ] Maintenance jobs run without conflicts
- [ ] Job execution tracked with full history
- [ ] Failed jobs retry with exponential backoff
- [ ] System handles 10,000+ scheduled jobs

---

## Phase 8: Multi-Step Planning Engine

### Overview

Implement an advanced planning system that breaks down complex tasks into executable steps, manages dependencies, and adapts plans based on execution results.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Planning Engine Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  User Goal   │─────▶│   Planner    │─────▶│   Plan    │ │
│  │              │      │     LLM      │      │   Store   │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                                │                     │       │
│                                ▼                     │       │
│                        ┌──────────────┐             │       │
│                        │  Execution   │             │       │
│                        │   Engine     │◀────────────┘       │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Monitoring  │                     │
│                        │  & Adaption  │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Planning Flow:
User Goal → Decompose → Create Steps → Execute → Monitor → Adapt
```

### Database Schema

```sql
-- Plans table
CREATE TABLE plans (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    status ENUM('draft', 'active', 'paused', 'completed', 'failed') DEFAULT 'draft',
    priority INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    metadata JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Plan steps table
CREATE TABLE plan_steps (
    id VARCHAR(36) PRIMARY KEY,
    plan_id VARCHAR(36) NOT NULL,
    step_number INT NOT NULL,
    description TEXT NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    action_config JSON NOT NULL,
    dependencies JSON,
    status ENUM('pending', 'ready', 'running', 'completed', 'failed', 'skipped') DEFAULT 'pending',
    result TEXT,
    error_message TEXT,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
    INDEX idx_plan_id (plan_id),
    INDEX idx_status (status),
    UNIQUE KEY unique_plan_step (plan_id, step_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Plan execution log
CREATE TABLE plan_execution_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_id VARCHAR(36) NOT NULL,
    step_id VARCHAR(36),
    event_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE,
    FOREIGN KEY (step_id) REFERENCES plan_steps(id) ON DELETE SET NULL,
    INDEX idx_plan_id (plan_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Planner LLM**

- Design planning prompts
- Implement goal decomposition
- Create step generation
- Add dependency analysis

**Step 2: Execution Engine**

- Build step executor
- Implement dependency resolver
- Add parallel execution
- Create error handling

**Step 3: Monitoring & Adaptation**

- Track execution progress
- Detect failures
- Implement replanning
- Add learning from failures

**Step 4: Integration**

- Connect with existing tools
- Add to LangGraph workflow
- Implement checkpointing
- Create UI for plan visualization

### Code Example: Planning System

```python
# app/planning/planner.py
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import mysql.connector
from openai import OpenAI

class MultiStepPlanner:
    """Advanced planning system for complex tasks."""

    def __init__(self, db_config: Dict[str, Any], openai_api_key: str):
        self.db_config = db_config
        self.client = OpenAI(api_key=openai_api_key)

    def create_plan(self, user_id: str, goal: str, context: Optional[Dict] = None) -> str:
        """Create a multi-step plan for achieving a goal."""
        plan_id = str(uuid.uuid4())

        # Use LLM to decompose goal into steps
        steps = self._decompose_goal(goal, context)

        # Store plan
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            # Insert plan
            cursor.execute(
                """INSERT INTO plans (id, user_id, goal, status, metadata)
                   VALUES (%s, %s, %s, 'draft', %s)""",
                (plan_id, user_id, goal, json.dumps(context or {}))
            )

            # Insert steps
            for i, step in enumerate(steps, 1):
                step_id = str(uuid.uuid4())
                cursor.execute(
                    """INSERT INTO plan_steps
                       (id, plan_id, step_number, description, action_type,
                        action_config, dependencies)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (step_id, plan_id, i, step['description'],
                     step['action_type'], json.dumps(step['config']),
                     json.dumps(step.get('dependencies', [])))
                )

            conn.commit()
            return plan_id

        finally:
            cursor.close()
            conn.close()

    def _decompose_goal(self, goal: str, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """Use LLM to decompose goal into actionable steps."""
        prompt = f"""Break down this goal into specific, actionable steps:

Goal: {goal}

Context: {json.dumps(context, indent=2) if context else 'None'}

For each step, provide:
1. Description: What needs to be done
2. Action Type: The type of action (email, search, calendar, etc.)
3. Config: Configuration for the action
4. Dependencies: Which previous steps must complete first (by step number)

Return as JSON array of steps."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a planning expert. Break down goals into clear, executable steps."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get('steps', [])

    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute a plan step by step."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            # Update plan status
            cursor.execute(
                """UPDATE plans SET status = 'active', started_at = NOW()
                   WHERE id = %s""",
                (plan_id,)
            )
            conn.commit()

            # Get all steps
            cursor.execute(
                """SELECT * FROM plan_steps
                   WHERE plan_id = %s
                   ORDER BY step_number""",
                (plan_id,)
            )
            steps = cursor.fetchall()

            # Execute steps
            results = []
            for step in steps:
                if self._can_execute_step(step, results):
                    result = self._execute_step(step)
                    results.append(result)

                    # Check if plan should continue
                    if result['status'] == 'failed' and not result.get('can_continue'):
                        self._log_event(plan_id, step['id'], 'plan_failed',
                                      'Plan execution stopped due to critical failure')
                        break

            # Update plan status
            all_completed = all(r['status'] == 'completed' for r in results)
            final_status = 'completed' if all_completed else 'failed'

            cursor.execute(
                """UPDATE plans SET status = %s, completed_at = NOW()
                   WHERE id = %s""",
                (final_status, plan_id)
            )
            conn.commit()

            return {
                'plan_id': plan_id,
                'status': final_status,
                'steps_executed': len(results),
                'results': results
            }

        finally:
            cursor.close()
            conn.close()

    def _can_execute_step(self, step: Dict, completed_results: List[Dict]) -> bool:
        """Check if step dependencies are satisfied."""
        dependencies = json.loads(step.get('dependencies', '[]'))

        if not dependencies:
            return True

        completed_steps = {r['step_number'] for r in completed_results
                          if r['status'] == 'completed'}

        return all(dep in completed_steps for dep in dependencies)

    def _execute_step(self, step: Dict) -> Dict[str, Any]:
        """Execute a single step."""
        step_id = step['id']
        plan_id = step['plan_id']

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            # Update step status
            cursor.execute(
                """UPDATE plan_steps SET status = 'running', started_at = NOW()
                   WHERE id = %s""",
                (step_id,)
            )
            conn.commit()

            # Execute action based on type
            action_type = step['action_type']
            action_config = json.loads(step['action_config'])

            try:
                result = self._execute_action(action_type, action_config)
                status = 'completed'
                error = None
            except Exception as e:
                result = None
                status = 'failed'
                error = str(e)

            # Update step with result
            cursor.execute(
                """UPDATE plan_steps
                   SET status = %s, result = %s, error_message = %s,
                       completed_at = NOW()
                   WHERE id = %s""",
                (status, json.dumps(result) if result else None, error, step_id)
            )
            conn.commit()

            # Log execution
            self._log_event(plan_id, step_id, 'step_completed' if status == 'completed' else 'step_failed',
                          f"Step {step['step_number']}: {step['description']}")

            return {
                'step_number': step['step_number'],
                'status': status,
                'result': result,
                'error': error,
                'can_continue': status == 'completed' or not action_config.get('critical', True)
            }

        finally:
            cursor.close()
            conn.close()

    def _execute_action(self, action_type: str, config: Dict[str, Any]) -> Any:
        """Execute an action based on type."""
        # This would integrate with existing tools
        if action_type == 'email':
            return self._send_email(config)
        elif action_type == 'search':
            return self._search_emails(config)
        elif action_type == 'calendar':
            return self._calendar_action(config)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def _log_event(self, plan_id: str, step_id: Optional[str],
                   event_type: str, message: str, details: Optional[Dict] = None):
        """Log a plan execution event."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO plan_execution_log
                   (plan_id, step_id, event_type, message, details)
                   VALUES (%s, %s, %s, %s, %s)""",
                (plan_id, step_id, event_type, message,
                 json.dumps(details) if details else None)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
```

### Success Criteria

- [ ] LLM successfully decomposes complex goals into steps
- [ ] Dependency resolution works correctly
- [ ] Steps execute in correct order
- [ ] Failed steps trigger appropriate handling
- [ ] Plans can be paused and resumed
- [ ] Execution logs provide full audit trail
- [ ] System handles plans with 20+ steps
- [ ] Replanning works when steps fail

---

## Phase 9: Calendar Integration

### Overview

Integrate with Google Calendar to manage meetings, schedule events, check availability, and coordinate with email workflows.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                Calendar Integration Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   LangGraph  │─────▶│   Calendar   │─────▶│  Google   │ │
│  │   Workflow   │      │   Manager    │      │ Calendar  │ │
│  └──────────────┘      └──────────────┘      │    API    │ │
│         │                      │              └───────────┘ │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │   Event      │             │       │
│         └─────────────▶│   Cache      │◀────────────┘       │
│                        │   (MySQL)    │                     │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Conflict    │                     │
│                        │  Detection   │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Features:
┌────────────────┬──────────────────────────────────────────┐
│ Event Creation │ Create meetings from email requests      │
│ Availability   │ Check free/busy times                    │
│ Scheduling     │ Find optimal meeting times               │
│ Reminders      │ Send meeting reminders                   │
│ Conflicts      │ Detect and resolve scheduling conflicts  │
└────────────────┴──────────────────────────────────────────┘
```

### Database Schema

```sql
-- Calendar events cache
CREATE TABLE calendar_events (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    calendar_id VARCHAR(255) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    description TEXT,
    location VARCHAR(500),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    attendees JSON,
    status VARCHAR(50),
    is_all_day BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_start_time (start_time),
    INDEX idx_end_time (end_time),
    INDEX idx_calendar_id (calendar_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Meeting requests from emails
CREATE TABLE meeting_requests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    email_id VARCHAR(255) NOT NULL,
    requester_email VARCHAR(255) NOT NULL,
    proposed_times JSON NOT NULL,
    duration_minutes INT NOT NULL,
    subject VARCHAR(500),
    description TEXT,
    status ENUM('pending', 'scheduled', 'declined', 'expired') DEFAULT 'pending',
    scheduled_event_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_email_id (email_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Availability preferences
CREATE TABLE availability_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    day_of_week INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 5,
    UNIQUE KEY unique_user_day_time (user_id, day_of_week, start_time),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Google Calendar API Setup**

- Configure OAuth2 credentials
- Implement authentication flow
- Set up API client
- Handle token refresh

**Step 2: Calendar Manager**

- Event CRUD operations
- Availability checking
- Conflict detection
- Smart scheduling

**Step 3: Email Integration**

- Parse meeting requests from emails
- Extract date/time information
- Propose alternative times
- Send calendar invites

**Step 4: Tools & Workflows**

- Create calendar tools for LangGraph
- Add to agent workflows
- Implement HITL for confirmations
- Build scheduling assistant

### Code Example: Calendar Manager

```python
# app/calendar/calendar_manager.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import mysql.connector
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dateutil import parser
import pytz

class CalendarManager:
    """Manages Google Calendar integration."""

    def __init__(self, db_config: Dict[str, Any], credentials: Credentials):
        self.db_config = db_config
        self.service = build('calendar', 'v3', credentials=credentials)

    def create_event(
        self,
        user_id: str,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> str:
        """Create a calendar event."""
        event = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        # Create event in Google Calendar
        created_event = self.service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()

        # Cache in database
        self._cache_event(user_id, created_event)

        return created_event['id']

    def check_availability(
        self,
        user_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if user is available during time range."""
        # Query cached events
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """SELECT COUNT(*) FROM calendar_events
                   WHERE user_id = %s
                   AND status != 'cancelled'
                   AND (
                       (start_time <= %s AND end_time > %s) OR
                       (start_time < %s AND end_time >= %s) OR
                       (start_time >= %s AND end_time <= %s)
                   )""",
                (user_id, start_time, start_time, end_time, end_time,
                 start_time, end_time)
            )

            count = cursor.fetchone()[0]
            return count == 0

        finally:
            cursor.close()
            conn.close()

    def find_available_slots(
        self,
        user_id: str,
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime,
        num_slots: int = 3
    ) -> List[Dict[str, datetime]]:
        """Find available time slots."""
        slots = []
        current = start_date

        while current < end_date and len(slots) < num_slots:
            slot_end = current + timedelta(minutes=duration_minutes)

            # Check if within working hours
            if self._is_working_hours(user_id, current):
                # Check availability
                if self.check_availability(user_id, current, slot_end):
                    slots.append({
                        'start': current,
                        'end': slot_end
                    })

            # Move to next 30-minute slot
            current += timedelta(minutes=30)

        return slots

    def _is_working_hours(self, user_id: str, time: datetime) -> bool:
        """Check if time is within user's working hours."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            day_of_week = time.weekday()
            time_only = time.time()

            cursor.execute(
                """SELECT is_available FROM availability_preferences
                   WHERE user_id = %s
                   AND day_of_week = %s
                   AND start_time <= %s
                   AND end_time >= %s""",
                (user_id, day_of_week, time_only, time_only)
            )

            result = cursor.fetchone()
            return result[0] if result else True  # Default to available

        finally:
            cursor.close()
            conn.close()

    def sync_events(self, user_id: str, days_ahead: int = 30):
        """Sync events from Google Calendar to local cache."""
        now = datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        for event in events:
            self._cache_event(user_id, event)

    def _cache_event(self, user_id: str, event: Dict[str, Any]):
        """Cache event in database."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            start_time = parser.parse(start)
            end_time = parser.parse(end)

            attendees = [a['email'] for a in event.get('attendees', [])]

            cursor.execute(
                """INSERT INTO calendar_events
                   (id, user_id, calendar_id, summary, description, location,
                    start_time, end_time, attendees, status, synced_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                   ON DUPLICATE KEY UPDATE
                   summary = VALUES(summary),
                   description = VALUES(description),
                   location = VALUES(location),
                   start_time = VALUES(start_time),
                   end_time = VALUES(end_time),
                   attendees = VALUES(attendees),
                   status = VALUES(status),
                   synced_at = NOW()""",
                (event['id'], user_id, 'primary',
                 event.get('summary', ''),
                 event.get('description'),
                 event.get('location'),
                 start_time, end_time,
                 json.dumps(attendees),
                 event.get('status', 'confirmed'))
            )
            conn.commit()

        finally:
            cursor.close()
            conn.close()
```

### Success Criteria

- [ ] Google Calendar API integrated successfully
- [ ] Events created from email requests
- [ ] Availability checking works accurately
- [ ] Smart scheduling finds optimal times
- [ ] Conflict detection prevents double-booking
- [ ] Calendar syncs reliably every 15 minutes
- [ ] Meeting requests processed automatically
- [ ] HITL confirmation for important meetings

---

## Phase 10: Observability & Monitoring

### Overview

Implement comprehensive monitoring, logging, and observability infrastructure to track system health, performance, and user behavior.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Observability Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │ Application  │─────▶│   Metrics    │─────▶│Prometheus │ │
│  │   Metrics    │      │  Collector   │      │           │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                                │                     │       │
│  ┌──────────────┐              ▼                     │       │
│  │   Logs       │      ┌──────────────┐             │       │
│  │ (Structured) │─────▶│   MySQL      │             │       │
│  └──────────────┘      │   Storage    │             │       │
│                        └──────────────┘             │       │
│  ┌──────────────┐              │                     │       │
│  │   Traces     │              ▼                     ▼       │
│  │  (OpenTel)   │      ┌──────────────┐      ┌───────────┐ │
│  └──────────────┘─────▶│   Grafana    │◀─────│  Alerts   │ │
│                        │  Dashboard   │      │  Manager  │ │
│                        └──────────────┘      └───────────┘ │
└─────────────────────────────────────────────────────────────┘

Monitoring Layers:
┌────────────────┬──────────────────────────────────────────┐
│ Infrastructure │ CPU, Memory, Disk, Network               │
│ Application    │ Request rate, latency, errors            │
│ Business       │ Emails processed, tasks completed        │
│ User           │ Active users, feature usage              │
└────────────────┴──────────────────────────────────────────┘
```

### Database Schema

```sql
-- Application metrics
CREATE TABLE metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_type ENUM('counter', 'gauge', 'histogram') NOT NULL,
    value DOUBLE NOT NULL,
    labels JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Application logs
CREATE TABLE application_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL,
    logger_name VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    context JSON,
    user_id VARCHAR(255),
    request_id VARCHAR(36),
    trace_id VARCHAR(36),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_level (level),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id),
    INDEX idx_request_id (request_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance traces
CREATE TABLE traces (
    id VARCHAR(36) PRIMARY KEY,
    trace_name VARCHAR(255) NOT NULL,
    parent_id VARCHAR(36),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_ms INT NOT NULL,
    status VARCHAR(50),
    attributes JSON,
    INDEX idx_trace_name (trace_name),
    INDEX idx_start_time (start_time),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System health checks
CREATE TABLE health_checks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    check_name VARCHAR(255) NOT NULL,
    status ENUM('healthy', 'degraded', 'unhealthy') NOT NULL,
    message TEXT,
    details JSON,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_check_name (check_name),
    INDEX idx_status (status),
    INDEX idx_checked_at (checked_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alert rules
CREATE TABLE alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_name VARCHAR(255) NOT NULL UNIQUE,
    metric_name VARCHAR(255) NOT NULL,
    condition VARCHAR(50) NOT NULL,
    threshold DOUBLE NOT NULL,
    duration_seconds INT DEFAULT 60,
    severity ENUM('info', 'warning', 'critical') NOT NULL,
    notification_channels JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_name (metric_name),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alert history
CREATE TABLE alert_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rule_id INT NOT NULL,
    triggered_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP NULL,
    current_value DOUBLE NOT NULL,
    message TEXT NOT NULL,
    notified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id) ON DELETE CASCADE,
    INDEX idx_rule_id (rule_id),
    INDEX idx_triggered_at (triggered_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Metrics Collection**

- Implement Prometheus metrics
- Add custom business metrics
- Create metrics middleware
- Set up exporters

**Step 2: Structured Logging**

- Configure structured logging
- Add context to logs
- Implement log aggregation
- Create log queries

**Step 3: Distributed Tracing**

- Integrate OpenTelemetry
- Add trace instrumentation
- Track request flows
- Analyze bottlenecks

**Step 4: Dashboards & Alerts**

- Create Grafana dashboards
- Set up alert rules
- Configure notifications
- Build health checks

### Code Example: Observability System

```python
# app/observability/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Dict, Any
import mysql.connector
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores application metrics."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.registry = CollectorRegistry()

        # Define metrics
        self.email_processed = Counter(
            'emails_processed_total',
            'Total emails processed',
            ['status', 'type'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['endpoint', 'method'],
            registry=self.registry
        )

        self.active_users = Gauge(
            'active_users',
            'Number of active users',
            registry=self.registry
        )

        self.llm_tokens = Counter(
            'llm_tokens_total',
            'Total LLM tokens used',
            ['model', 'type'],
            registry=self.registry
        )

    def record_metric(
        self,
        metric_name: str,
        metric_type: str,
        value: float,
        labels: Dict[str, str] = None
    ):
        """Record a metric to database."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO metrics (metric_name, metric_type, value, labels)
                   VALUES (%s, %s, %s, %s)""",
                (metric_name, metric_type, value, json.dumps(labels or {}))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime
    ) -> list:
        """Retrieve metrics for analysis."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT * FROM metrics
                   WHERE metric_name = %s
                   AND timestamp BETWEEN %s AND %s
                   ORDER BY timestamp""",
                (metric_name, start_time, end_time)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


# app/observability/logger.py
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import mysql.connector

class StructuredLogger:
    """Structured logging with context."""

    def __init__(self, db_config: Dict[str, Any], name: str):
        self.db_config = db_config
        self.logger = logging.getLogger(name)
        self.context = {}

    def set_context(self, **kwargs):
        """Set logging context."""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logging context."""
        self.context = {}

    def _log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Internal logging method."""
        # Combine context with extra data
        log_data = {**self.context, **(extra or {})}

        # Log to standard logger
        getattr(self.logger, level.lower())(message, extra=log_data)

        # Store in database
        self._store_log(level, message, log_data)

    def _store_log(self, level: str, message: str, context: Dict[str, Any]):
        """Store log in database."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO application_logs
                   (level, logger_name, message, context, user_id, request_id, trace_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (level.upper(), self.logger.name, message,
                 json.dumps(context), context.get('user_id'),
                 context.get('request_id'), context.get('trace_id'))
            )
            conn.commit()
        except Exception as e:
            # Don't fail the application if logging fails
            print(f"Failed to store log: {e}")
        finally:
            cursor.close()
            conn.close()

    def debug(self, message: str, **kwargs):
        self._log('DEBUG', message, kwargs)

    def info(self, message: str, **kwargs):
        self._log('INFO', message, kwargs)

    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, kwargs)

    def error(self, message: str, **kwargs):
        self._log('ERROR', message, kwargs)

    def critical(self, message: str, **kwargs):
        self._log('CRITICAL', message, kwargs)


# app/observability/tracer.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from typing import Dict, Any
import mysql.connector
import json
from datetime import datetime
import uuid

class DistributedTracer:
    """Distributed tracing with OpenTelemetry."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

        # Set up tracer
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)

    def start_trace(self, name: str, parent_id: str = None) -> str:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())

        with self.tracer.start_as_current_span(name) as span:
            span.set_attribute("trace_id", trace_id)
            if parent_id:
                span.set_attribute("parent_id", parent_id)

        return trace_id

    def end_trace(
        self,
        trace_id: str,
        status: str = "success",
        attributes: Dict[str, Any] = None
    ):
        """End a trace and store it."""
        # This would be called when the traced operation completes
        pass

    def store_trace(
        self,
        trace_id: str,
        trace_name: str,
        parent_id: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        attributes: Dict[str, Any]
    ):
        """Store trace in database."""
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO traces
                   (id, trace_name, parent_id, start_time, end_time,
                    duration_ms, status, attributes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (trace_id, trace_name, parent_id, start_time, end_time,
                 duration_ms, status, json.dumps(attributes or {}))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()


# app/observability/health.py
from typing import Dict, Any, List
import mysql.connector
from datetime import datetime
import json

class HealthChecker:
    """System health monitoring."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.checks = {}

    def register_check(self, name: str, check_func):
        """Register a health check."""
        self.checks[name] = check_func

    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = 'healthy'

        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = result

                # Store in database
                self._store_check(name, result)

                # Update overall status
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result['status'] == 'degraded' and overall_status == 'healthy':
                    overall_status = 'degraded'

            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'message': f"Check failed: {str(e)}"
                }
                overall_status = 'unhealthy'

        return {
            'status': overall_status,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }

    def _store_check(self, check_name: str, result: Dict[str, Any]):
        """Store health check result."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO health_checks
                   (check_name, status, message, details)
                   VALUES (%s, %s, %s, %s)""",
                (check_name, result['status'], result.get('message'),
                 json.dumps(result.get('details', {})))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

# Example health checks
def database_check():
    """Check database connectivity."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {'status': 'healthy', 'message': 'Database connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}

def api_check():
    """Check external API connectivity."""
    # Check OpenAI, Gmail API, etc.
    return {'status': 'healthy', 'message': 'APIs accessible'}
```

### Success Criteria

- [ ] Prometheus metrics exported and scraped
- [ ] Structured logs stored and queryable
- [ ] Distributed tracing tracks request flows
- [ ] Grafana dashboards show key metrics
- [ ] Alert rules trigger on anomalies
- [ ] Health checks run every minute
- [ ] 99.9% of logs captured
- [ ] Trace overhead <5% of request time

---

## Phase 11: Email Intelligence & Analytics

### Overview

Build advanced email analytics and intelligence features including sentiment analysis, priority scoring, relationship tracking, and insights generation.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│            Email Intelligence Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Emails     │─────▶│  Analysis    │─────▶│  Insights │ │
│  │   Stream     │      │   Pipeline   │      │  Storage  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │  ML Models   │             │       │
│         └─────────────▶│  - Sentiment │◀────────────┘       │
│                        │  - Priority  │                     │
│                        │  - Category  │                     │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Dashboard   │                     │
│                        │  & Reports   │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Analytics Features:
┌────────────────┬──────────────────────────────────────────┐
│ Sentiment      │ Positive, neutral, negative detection    │
│ Priority       │ Urgency and importance scoring           │
│ Relationships  │ Communication patterns and networks      │
│ Topics         │ Automatic topic extraction               │
│ Trends         │ Volume, response time, patterns          │
└────────────────┴──────────────────────────────────────────┘
```

### Database Schema

```sql
-- Email analytics
CREATE TABLE email_analytics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(50),
    priority_score FLOAT,
    urgency_score FLOAT,
    importance_score FLOAT,
    category VARCHAR(100),
    topics JSON,
    entities JSON,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_sender (sender_email),
    INDEX idx_priority (priority_score),
    INDEX idx_sentiment (sentiment_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Communication relationships
CREATE TABLE communication_relationships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    total_emails_sent INT DEFAULT 0,
    total_emails_received INT DEFAULT 0,
    avg_response_time_hours FLOAT,
    last_interaction TIMESTAMP,
    relationship_strength FLOAT,
    communication_frequency VARCHAR(50),
    UNIQUE KEY unique_user_contact (user_id, contact_email),
    INDEX idx_user_id (user_id),
    INDEX idx_strength (relationship_strength)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Email topics
CREATE TABLE email_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic_name VARCHAR(255) NOT NULL,
    keywords JSON NOT NULL,
    email_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_topic (topic_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Email topic mapping
CREATE TABLE email_topic_mapping (
    email_id VARCHAR(255) NOT NULL,
    topic_id INT NOT NULL,
    relevance_score FLOAT NOT NULL,
    PRIMARY KEY (email_id, topic_id),
    FOREIGN KEY (topic_id) REFERENCES email_topics(id) ON DELETE CASCADE,
    INDEX idx_email_id (email_id),
    INDEX idx_topic_id (topic_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analytics insights
CREATE TABLE analytics_insights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    insight_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    data JSON,
    importance_score FLOAT DEFAULT 0.5,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_type (insight_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Email statistics (aggregated)
CREATE TABLE email_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    emails_received INT DEFAULT 0,
    emails_sent INT DEFAULT 0,
    avg_response_time_hours FLOAT,
    top_senders JSON,
    top_topics JSON,
    sentiment_distribution JSON,
    UNIQUE KEY unique_user_date (user_id, date),
    INDEX idx_user_id (user_id),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Analysis Pipeline**

- Implement sentiment analysis
- Build priority scoring
- Add category classification
- Extract entities and topics

**Step 2: Relationship Tracking**

- Track communication patterns
- Calculate relationship strength
- Analyze response times
- Identify key contacts

**Step 3: Insights Generation**

- Detect trends and patterns
- Generate actionable insights
- Create recommendations
- Build notification system

**Step 4: Visualization**

- Create analytics dashboard
- Build reports
- Add charts and graphs
- Implement export features

### Code Example: Email Intelligence

```python
# app/analytics/email_analyzer.py
from typing import Dict, Any, List
import mysql.connector
from openai import OpenAI
import json
from datetime import datetime, timedelta

class EmailAnalyzer:
    """Advanced email analysis and intelligence."""

    def __init__(self, db_config: Dict[str, Any], openai_api_key: str):
        self.db_config = db_config
        self.client = OpenAI(api_key=openai_api_key)

    def analyze_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive email analysis."""
        # Sentiment analysis
        sentiment = self._analyze_sentiment(email['body'])

        # Priority scoring
        priority = self._calculate_priority(email)

        # Category classification
        category = self._classify_category(email)

        # Topic extraction
        topics = self._extract_topics(email['body'])

        # Entity extraction
        entities = self._extract_entities(email['body'])

        # Store analysis
        self._store_analysis(
            email['id'],
            email['user_id'],
            email['from'],
            sentiment,
            priority,
            category,
            topics,
            entities
        )

        return {
            'sentiment': sentiment,
            'priority': priority,
            'category': category,
            'topics': topics,
            'entities': entities
        }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using LLM."""
        prompt = f"""Analyze the sentiment of this email:

{text}

Return JSON with:
- score: float from -1 (very negative) to 1 (very positive)
- label: 'positive', 'neutral', or 'negative'
- confidence: float from 0 to 1"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sentiment analysis expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _calculate_priority(self, email: Dict[str, Any]) -> Dict[str, float]:
        """Calculate email priority scores."""
        urgency = 0.5
        importance = 0.5

        # Check for urgency indicators
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency']
        subject_lower = email.get('subject', '').lower()
        body_lower = email.get('body', '').lower()

        for keyword in urgent_keywords:
            if keyword in subject_lower or keyword in body_lower:
                urgency += 0.2

        # Check sender importance (from relationship data)
        sender_importance = self._get_sender_importance(
            email['user_id'],
            email['from']
        )
        importance = sender_importance

        # Overall priority
        priority = (urgency * 0.6 + importance * 0.4)

        return {
            'priority_score': min(priority, 1.0),
            'urgency_score': min(urgency, 1.0),
            'importance_score': importance
        }

    def _classify_category(self, email: Dict[str, Any]) -> str:
        """Classify email into category."""
        prompt = f"""Classify this email into one category:

Subject: {email.get('subject', '')}
Body: {email.get('body', '')[:500]}

Categories: work, personal, finance, travel, shopping, social, newsletter, spam

Return only the category name."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an email classification expert."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip().lower()

    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from email."""
        prompt = f"""Extract the main topics from this email:

{text[:1000]}

Return a JSON array of 3-5 topic keywords."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a topic extraction expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get('topics', [])

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from email."""
        # This would use NER model or LLM
        return {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': []
        }

    def _store_analysis(
        self,
        email_id: str,
        user_id: str,
        sender: str,
        sentiment: Dict,
        priority: Dict,
        category: str,
        topics: List[str],
        entities: Dict
    ):
        """Store analysis results."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO email_analytics
                   (email_id, user_id, sender_email, sentiment_score, sentiment_label,
                    priority_score, urgency_score, importance_score, category, topics, entities)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                   sentiment_score = VALUES(sentiment_score),
                   sentiment_label = VALUES(sentiment_label),
                   priority_score = VALUES(priority_score),
                   urgency_score = VALUES(urgency_score),
                   importance_score = VALUES(importance_score),
                   category = VALUES(category),
                   topics = VALUES(topics),
                   entities = VALUES(entities),
                   analyzed_at = CURRENT_TIMESTAMP""",
                (email_id, user_id, sender,
                 sentiment['score'], sentiment['label'],
                 priority['priority_score'], priority['urgency_score'],
                 priority['importance_score'], category,
                 json.dumps(topics), json.dumps(entities))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_relationships(self, user_id: str, email: Dict[str, Any]):
        """Update communication relationship data."""
        sender = email['from']
        is_sent = email.get('is_sent', False)

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            if is_sent:
                cursor.execute(
                    """INSERT INTO communication_relationships
                       (user_id, contact_email, total_emails_sent, last_interaction)
                       VALUES (%s, %s, 1, NOW())
                       ON DUPLICATE KEY UPDATE
                       total_emails_sent = total_emails_sent + 1,
                       last_interaction = NOW()""",
                    (user_id, sender)
                )
            else:
                cursor.execute(
                    """INSERT INTO communication_relationships
                       (user_id, contact_email, total_emails_received, last_interaction)
                       VALUES (%s, %s, 1, NOW())
                       ON DUPLICATE KEY UPDATE
                       total_emails_received = total_emails_received + 1,
                       last_interaction = NOW()""",
                    (user_id, sender)
                )

            conn.commit()

            # Recalculate relationship strength
            self._calculate_relationship_strength(user_id, sender)

        finally:
            cursor.close()
            conn.close()

    def generate_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate actionable insights from email data."""
        insights = []

        # Insight 1: Unresponsive contacts
        insights.extend(self._find_unresponsive_contacts(user_id))

        # Insight 2: High priority emails
        insights.extend(self._find_high_priority_emails(user_id))

        # Insight 3: Communication trends
        insights.extend(self._analyze_communication_trends(user_id))

        # Store insights
        for insight in insights:
            self._store_insight(user_id, insight)

        return insights

    def _find_unresponsive_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """Find contacts that haven't been responded to."""
        # Query for contacts with pending responses
        return []

    def _find_high_priority_emails(self, user_id: str) -> List[Dict[str, Any]]:
        """Find high priority emails needing attention."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT email_id, sender_email, priority_score
                   FROM email_analytics
                   WHERE user_id = %s
                   AND priority_score > 0.7
                   AND analyzed_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                   ORDER BY priority_score DESC
                   LIMIT 5""",
                (user_id,)
            )

            high_priority = cursor.fetchall()

            if high_priority:
                return [{
                    'type': 'high_priority_emails',
                    'title': f'{len(high_priority)} high priority emails need attention',
                    'description': 'You have important emails that may require immediate action',
                    'data': high_priority,
                    'importance_score': 0.8
                }]

            return []

        finally:
            cursor.close()
            conn.close()
```

### Success Criteria

- [ ] Sentiment analysis accuracy >85%
- [ ] Priority scoring correlates with user actions
- [ ] Category classification accuracy >90%
- [ ] Topic extraction identifies key themes
- [ ] Relationship tracking updates in real-time
- [ ] Insights generated daily
- [ ] Dashboard loads in <2 seconds
- [ ] Analytics pipeline processes 1000 emails/minute

---

## Phase 12: Evaluation Framework

### Overview

Implement comprehensive evaluation and testing framework to measure system performance, accuracy, and user satisfaction across all features.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Evaluation Framework Architecture               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Test Cases  │─────▶│  Evaluation  │─────▶│  Results  │ │
│  │  & Datasets  │      │   Engine     │      │  Storage  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │   Metrics    │             │       │
│         └─────────────▶│  Calculator  │◀────────────┘       │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │  Reporting   │                     │
│                        │  Dashboard   │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘

Evaluation Types:
┌────────────────┬──────────────────────────────────────────┐
│ Unit Tests     │ Individual component testing             │
│ Integration    │ End-to-end workflow testing              │
│ Performance    │ Speed, latency, throughput               │
│ Accuracy       │ LLM output quality and correctness       │
│ User Feedback  │ Satisfaction and usability metrics       │
└────────────────┴──────────────────────────────────────────┘
```

### Database Schema

```sql
-- Test cases
CREATE TABLE test_cases (
    id VARCHAR(36) PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    description TEXT,
    input_data JSON NOT NULL,
    expected_output JSON NOT NULL,
    tags JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_test_type (test_type),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Test runs
CREATE TABLE test_runs (
    id VARCHAR(36) PRIMARY KEY,
    run_name VARCHAR(255) NOT NULL,
    test_suite VARCHAR(255),
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NULL,
    status ENUM('running', 'completed', 'failed', 'cancelled') NOT NULL,
    total_tests INT DEFAULT 0,
    passed_tests INT DEFAULT 0,
    failed_tests INT DEFAULT 0,
    skipped_tests INT DEFAULT 0,
    metadata JSON,
    INDEX idx_started_at (started_at),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Test results
CREATE TABLE test_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL,
    test_case_id VARCHAR(36) NOT NULL,
    status ENUM('passed', 'failed', 'skipped', 'error') NOT NULL,
    actual_output JSON,
    error_message TEXT,
    execution_time_ms INT,
    metrics JSON,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES test_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    INDEX idx_run_id (run_id),
    INDEX idx_test_case_id (test_case_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Evaluation metrics
CREATE TABLE evaluation_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_category VARCHAR(100) NOT NULL,
    value DOUBLE NOT NULL,
    target_value DOUBLE,
    unit VARCHAR(50),
    test_run_id VARCHAR(36),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (test_run_id) REFERENCES test_runs(id) ON DELETE SET NULL,
    INDEX idx_metric_name (metric_name),
    INDEX idx_category (metric_category),
    INDEX idx_recorded_at (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User feedback
CREATE TABLE user_feedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    feature VARCHAR(100) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_feature (feature),
    INDEX idx_rating (rating),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- A/B test experiments
CREATE TABLE ab_experiments (
    id VARCHAR(36) PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    variant_a JSON NOT NULL,
    variant_b JSON NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NULL,
    status ENUM('draft', 'running', 'completed', 'cancelled') DEFAULT 'draft',
    winner VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_start_date (start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- A/B test results
CREATE TABLE ab_test_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    experiment_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    variant VARCHAR(10) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DOUBLE NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES ab_experiments(id) ON DELETE CASCADE,
    INDEX idx_experiment_id (experiment_id),
    INDEX idx_variant (variant),
    INDEX idx_metric_name (metric_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Test Framework**

- Create test case management
- Build test runner
- Implement assertions
- Add test fixtures

**Step 2: Metrics Collection**

- Define evaluation metrics
- Implement metric calculators
- Add benchmarking
- Create baselines

**Step 3: LLM Evaluation**

- Implement LLM-as-judge
- Add human evaluation
- Create golden datasets
- Measure accuracy

**Step 4: Reporting**

- Build evaluation dashboard
- Generate reports
- Add visualizations
- Implement alerts

### Code Example: Evaluation Framework

```python
# app/evaluation/test_runner.py
from typing import Dict, Any, List, Optional
import mysql.connector
import json
import uuid
from datetime import datetime
import time

class TestRunner:
    """Runs evaluation tests and collects metrics."""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    def create_test_case(
        self,
        test_name: str,
        test_type: str,
        description: str,
        input_data: Dict[str, Any],
        expected_output: Dict[str, Any],
        tags: List[str] = None
    ) -> str:
        """Create a new test case."""
        test_id = str(uuid.uuid4())

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO test_cases
                   (id, test_name, test_type, description, input_data,
                    expected_output, tags)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (test_id, test_name, test_type, description,
                 json.dumps(input_data), json.dumps(expected_output),
                 json.dumps(tags or []))
            )
            conn.commit()
            return test_id
        finally:
            cursor.close()
            conn.close()

    def run_test_suite(
        self,
        suite_name: str,
        test_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a suite of tests."""
        run_id = str(uuid.uuid4())

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            # Create test run
            cursor.execute(
                """INSERT INTO test_runs (id, run_name, test_suite, started_at, status)
                   VALUES (%s, %s, %s, NOW(), 'running')""",
                (run_id, f"{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                 suite_name)
            )
            conn.commit()

            # Get test cases
            if test_type:
                cursor.execute(
                    """SELECT * FROM test_cases
                       WHERE test_type = %s AND is_active = TRUE""",
                    (test_type,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM test_cases WHERE is_active = TRUE"
                )

            test_cases = cursor.fetchall()

            # Run tests
            results = []
            for test_case in test_cases:
                result = self._run_single_test(run_id, test_case)
                results.append(result)

            # Update test run
            passed = sum(1 for r in results if r['status'] == 'passed')
            failed = sum(1 for r in results if r['status'] == 'failed')
            skipped = sum(1 for r in results if r['status'] == 'skipped')

            cursor.execute(
                """UPDATE test_runs
                   SET completed_at = NOW(), status = 'completed',
                       total_tests = %s, passed_tests = %s,
                       failed_tests = %s, skipped_tests = %s
                   WHERE id = %s""",
                (len(results), passed, failed, skipped, run_id)
            )
            conn.commit()

            return {
                'run_id': run_id,
                'total': len(results),
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'results': results
            }

        finally:
            cursor.close()
            conn.close()

    def _run_single_test(
        self,
        run_id: str,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single test case."""
        start_time = time.time()

        try:
            input_data = json.loads(test_case['input_data'])
            expected_output = json.loads(test_case['expected_output'])

            # Execute test based on type
            actual_output = self._execute_test(
                test_case['test_type'],
                input_data
            )

            # Compare results
            passed = self._compare_outputs(expected_output, actual_output)

            execution_time = int((time.time() - start_time) * 1000)

            # Calculate metrics
            metrics = self._calculate_metrics(
                expected_output,
                actual_output,
                test_case['test_type']
            )

            # Store result
            self._store_result(
                run_id,
                test_case['id'],
                'passed' if passed else 'failed',
                actual_output,
                None,
                execution_time,
                metrics
            )

            return {
                'test_id': test_case['id'],
                'test_name': test_case['test_name'],
                'status': 'passed' if passed else 'failed',
                'execution_time_ms': execution_time,
                'metrics': metrics
            }

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)

            self._store_result(
                run_id,
                test_case['id'],
                'error',
                None,
                str(e),
                execution_time,
                {}
            )

            return {
                'test_id': test_case['id'],
                'test_name': test_case['test_name'],
                'status': 'error',
                'error': str(e),
                'execution_time_ms': execution_time
            }

    def _execute_test(self, test_type: str, input_data: Dict[str, Any]) -> Any:
        """Execute test based on type."""
        if test_type == 'email_classification':
            return self._test_email_classification(input_data)
        elif test_type == 'sentiment_analysis':
            return self._test_sentiment_analysis(input_data)
        elif test_type == 'priority_scoring':
            return self._test_priority_scoring(input_data)
        elif test_type == 'response_generation':
            return self._test_response_generation(input_data)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    def _compare_outputs(self, expected: Any, actual: Any) -> bool:
        """Compare expected and actual outputs."""
        if isinstance(expected, dict) and isinstance(actual, dict):
            # For dict outputs, check key metrics
            for key in expected:
                if key not in actual:
                    return False
                if not self._values_match(expected[key], actual[key]):
                    return False
            return True
        else:
            return self._values_match(expected, actual)

    def _values_match(self, expected: Any, actual: Any, tolerance: float = 0.1) -> bool:
        """Check if values match within tolerance."""
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) <= tolerance
        else:
            return expected == actual

    def _calculate_metrics(
        self,
        expected: Any,
        actual: Any,
        test_type: str
    ) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        metrics = {}

        if test_type == 'sentiment_analysis':
            if isinstance(expected, dict) and isinstance(actual, dict):
                # Calculate accuracy
                metrics['score_diff'] = abs(
                    expected.get('score', 0) - actual.get('score', 0)
                )
                metrics['label_match'] = 1.0 if expected.get('label') == actual.get('label') else 0.0

        elif test_type == 'priority_scoring':
            if isinstance(expected, dict) and isinstance(actual, dict):
                metrics['priority_diff'] = abs(
                    expected.get('priority_score', 0) - actual.get('priority_score', 0)
                )

        return metrics

    def _store_result(
        self,
        run_id: str,
        test_case_id: str,
        status: str,
        actual_output: Any,
        error_message: Optional[str],
        execution_time_ms: int,
        metrics: Dict[str, float]
    ):
        """Store test result."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO test_results
                   (run_id, test_case_id, status, actual_output, error_message,
                    execution_time_ms, metrics)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (run_id, test_case_id, status,
                 json.dumps(actual_output) if actual_output else None,
                 error_message, execution_time_ms, json.dumps(metrics))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()


# app/evaluation/llm_evaluator.py
from openai import OpenAI
import json

class LLMEvaluator:
    """Use LLM as a judge for evaluation."""

    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)

    def evaluate_response_quality(
        self,
        prompt: str,
        response: str,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Evaluate response quality using LLM."""
        evaluation_prompt = f"""Evaluate this AI assistant response:

Prompt: {prompt}

Response: {response}

Criteria to evaluate:
{chr(10).join(f"- {c}" for c in criteria)}

For each criterion, provide:
1. Score (1-5)
2. Explanation

Return as JSON."""

        result = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert evaluator of AI responses."},
                {"role": "user", "content": evaluation_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(result.choices[0].message.content)

    def compare_responses(
        self,
        prompt: str,
        response_a: str,
        response_b: str
    ) -> Dict[str, Any]:
        """Compare two responses and determine which is better."""
        comparison_prompt = f"""Compare these two AI assistant responses:

Prompt: {prompt}

Response A: {response_a}

Response B: {response_b}

Which response is better and why? Consider:
- Accuracy
- Helpfulness
- Clarity
- Completeness

Return JSON with: winner (A or B), reasoning, scores for each criterion."""

        result = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at comparing AI responses."},
                {"role": "user", "content": comparison_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(result.choices[0].message.content)


# app/evaluation/metrics.py
class EvaluationMetrics:
    """Calculate various evaluation metrics."""

    @staticmethod
    def accuracy(predictions: List[Any], ground_truth: List[Any]) -> float:
        """Calculate accuracy."""
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")

        correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
        return correct / len(predictions)

    @staticmethod
    def precision_recall_f1(
        predictions: List[str],
        ground_truth: List[str],
        positive_label: str
    ) -> Dict[str, float]:
        """Calculate precision, recall, and F1 score."""
        tp = sum(1 for p, g in zip(predictions, ground_truth)
                if p == positive_label and g == positive_label)
        fp = sum(1 for p, g in zip(predictions, ground_truth)
                if p == positive_label and g != positive_label)
        fn = sum(1 for p, g in zip(predictions, ground_truth)
                if p != positive_label and g == positive_label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    @staticmethod
    def mean_absolute_error(predictions: List[float], ground_truth: List[float]) -> float:
        """Calculate MAE."""
        if len(predictions) != len(ground_truth):
            raise ValueError("Predictions and ground truth must have same length")

        return sum(abs(p - g) for p, g in zip(predictions, ground_truth)) / len(predictions)
```

### Success Criteria

- [ ] Test framework covers all major features
- [ ] Automated tests run on every deployment
- [ ] LLM evaluation accuracy >90%
- [ ] Performance benchmarks established
- [ ] User feedback collected systematically
- [ ] A/B testing framework operational
- [ ] Evaluation dashboard accessible
- [ ] Regression detection automated

---

## Phase 13: Voice Interface

### Overview

Add voice input and output capabilities, enabling hands-free interaction with the AI assistant through speech recognition and text-to-speech.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                Voice Interface Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Audio      │─────▶│   Speech     │─────▶│   Text    │ │
│  │   Input      │      │ Recognition  │      │  Process  │ │
│  └──────────────┘      │  (Whisper)   │      └───────────┘ │
│                        └──────────────┘             │       │
│                                                      ▼       │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Audio      │◀─────│     TTS      │◀─────│ LangGraph │ │
│  │   Output     │      │   (OpenAI)   │      │ Workflow  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Voice Command Processing                 │  │
│  │  - Wake word detection                                │  │
│  │  - Intent recognition                                 │  │
│  │  - Context management                                 │  │
│  │  - Multi-turn conversations                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Voice Features:
┌────────────────┬──────────────────────────────────────────┐
│ Speech-to-Text │ Convert voice to text (Whisper API)      │
│ Text-to-Speech │ Convert responses to voice (OpenAI TTS)  │
│ Wake Word      │ Activate with "Hey Assistant"            │
│ Commands       │ Quick actions via voice                  │
│ Conversations  │ Natural multi-turn dialogues             │
└────────────────┴──────────────────────────────────────────┘
```

### Database Schema

```sql
-- Voice interactions
CREATE TABLE voice_interactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    audio_input_path VARCHAR(500),
    transcribed_text TEXT NOT NULL,
    intent VARCHAR(100),
    response_text TEXT NOT NULL,
    audio_output_path VARCHAR(500),
    duration_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Voice sessions
CREATE TABLE voice_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP NULL,
    interaction_count INT DEFAULT 0,
    total_duration_seconds FLOAT DEFAULT 0,
    context JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Voice commands
CREATE TABLE voice_commands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    command_phrase VARCHAR(255) NOT NULL UNIQUE,
    intent VARCHAR(100) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    parameters JSON,
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,
    INDEX idx_intent (intent),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Voice preferences
CREATE TABLE voice_preferences (
    user_id VARCHAR(255) PRIMARY KEY,
    voice_model VARCHAR(50) DEFAULT 'alloy',
    speech_rate FLOAT DEFAULT 1.0,
    wake_word_enabled BOOLEAN DEFAULT TRUE,
    auto_play_responses BOOLEAN DEFAULT TRUE,
    language VARCHAR(10) DEFAULT 'en',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### Implementation Plan

**Step 1: Speech Recognition**

- Integrate Whisper API
- Implement audio recording
- Add real-time transcription
- Handle multiple languages

**Step 2: Text-to-Speech**

- Integrate OpenAI TTS
- Add voice selection
- Implement audio streaming
- Cache common responses

**Step 3: Voice Commands**

- Define command vocabulary
- Implement intent recognition
- Add quick actions
- Create command shortcuts

**Step 4: Conversation Management**

- Track voice sessions
- Maintain context
- Handle interruptions
- Add confirmation flows

### Code Example: Voice Interface

```python
# app/voice/voice_interface.py
from typing import Dict, Any, Optional
import mysql.connector
from openai import OpenAI
import uuid
from datetime import datetime
import os
import json

class VoiceInterface:
    """Voice input/output interface."""

    def __init__(self, db_config: Dict[str, Any], openai_api_key: str):
        self.db_config = db_config
        self.client = OpenAI(api_key=openai_api_key)
        self.audio_dir = "data/voice_audio"
        os.makedirs(self.audio_dir, exist_ok=True)

    def start_session(self, user_id: str) -> str:
        """Start a new voice session."""
        session_id = str(uuid.uuid4())

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO voice_sessions (id, user_id, started_at)
                   VALUES (%s, %s, NOW())""",
                (session_id, user_id)
            )
            conn.commit()
            return session_id
        finally:
            cursor.close()
            conn.close()

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio to text using Whisper."""
        with open(audio_file_path, 'rb') as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        return transcript

    def synthesize_speech(
        self,
        text: str,
        user_id: str,
        voice: str = "alloy"
    ) -> str:
        """Convert text to speech using OpenAI TTS."""
        # Get user preferences
        preferences = self._get_voice_preferences(user_id)
        voice = preferences.get('voice_model', voice)

        # Generate speech
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=preferences.get('speech_rate', 1.0)
        )

        # Save audio file
        audio_id = str(uuid.uuid4())
        audio_path = os.path.join(self.audio_dir, f"{audio_id}.mp3")
        response.stream_to_file(audio_path)

        return audio_path

    def process_voice_input(
        self,
        user_id: str,
        session_id: str,
        audio_file_path: str
    ) -> Dict[str, Any]:
        """Process voice input end-to-end."""
        start_time = datetime.now()

        # Transcribe audio
        transcribed_text = self.transcribe_audio(audio_file_path)

        # Recognize intent
        intent = self._recognize_intent(transcribed_text)

        # Process with LangGraph workflow
        response_text = self._process_with_workflow(
            user_id,
            transcribed_text,
            intent
        )

        # Synthesize response
        audio_output_path = self.synthesize_speech(response_text, user_id)

        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()

        # Store interaction
        interaction_id = self._store_interaction(
            user_id,
            session_id,
            audio_file_path,
            transcribed_text,
            intent,
            response_text,
            audio_output_path,
            duration
        )

        return {
            'interaction_id': interaction_id,
            'transcribed_text': transcribed_text,
            'intent': intent,
            'response_text': response_text,
            'audio_output_path': audio_output_path,
            'duration_seconds': duration
        }

    def _recognize_intent(self, text: str) -> str:
        """Recognize intent from transcribed text."""
        # Check for registered voice commands
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM voice_commands WHERE is_active = TRUE"
            )
            commands = cursor.fetchall()

            text_lower = text.lower()
            for command in commands:
                if command['command_phrase'].lower() in text_lower:
                    # Update usage count
                    cursor.execute(
                        """UPDATE voice_commands
                           SET usage_count = usage_count + 1
                           WHERE id = %s""",
                        (command['id'],)
                    )
                    conn.commit()
                    return command['intent']

            # Use LLM for intent recognition if no command matched
            return self._llm_intent_recognition(text)

        finally:
            cursor.close()
            conn.close()

    def _llm_intent_recognition(self, text: str) -> str:
        """Use LLM to recognize intent."""
        prompt = f"""Classify the intent of this voice command:

"{text}"

Possible intents:
- read_emails: User wants to hear their emails
- send_email: User wants to send an email
- schedule_meeting: User wants to schedule a meeting
- check_calendar: User wants to check their calendar
- search: User wants to search for something
- general_query: General question or conversation

Return only the intent name."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classification expert."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    def _process_with_workflow(
        self,
        user_id: str,
        text: str,
        intent: str
    ) -> str:
        """Process input with LangGraph workflow."""
        # This would integrate with existing workflows
        # For now, return a simple response
        return f"I understand you want to {intent.replace('_', ' ')}. Processing your request..."

    def _store_interaction(
        self,
        user_id: str,
        session_id: str,
        audio_input_path: str,
        transcribed_text: str,
        intent: str,
        response_text: str,
        audio_output_path: str,
        duration: float
    ) -> str:
        """Store voice interaction."""
        interaction_id = str(uuid.uuid4())

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO voice_interactions
                   (id, user_id, session_id, audio_input_path, transcribed_text,
                    intent, response_text, audio_output_path, duration_seconds)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (interaction_id, user_id, session_id, audio_input_path,
                 transcribed_text, intent, response_text, audio_output_path, duration)
            )

            # Update session
            cursor.execute(
                """UPDATE voice_sessions
                   SET interaction_count = interaction_count + 1,
                       total_duration_seconds = total_duration_seconds + %s
                   WHERE id = %s""",
                (duration, session_id)
            )

            conn.commit()
            return interaction_id

        finally:
            cursor.close()
            conn.close()

    def _get_voice_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user voice preferences."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM voice_preferences WHERE user_id = %s",
                (user_id,)
            )
            prefs = cursor.fetchone()

            if not prefs:
                # Create default preferences
                cursor.execute(
                    """INSERT INTO voice_preferences (user_id)
                       VALUES (%s)""",
                    (user_id,)
                )
                conn.commit()
                return {
                    'voice_model': 'alloy',
                    'speech_rate': 1.0,
                    'wake_word_enabled': True,
                    'auto_play_responses': True,
                    'language': 'en'
                }

            return prefs

        finally:
            cursor.close()
            conn.close()

    def register_command(
        self,
        command_phrase: str,
        intent: str,
        action_type: str,
        parameters: Dict[str, Any] = None
    ):
        """Register a new voice command."""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO voice_commands
                   (command_phrase, intent, action_type, parameters)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE
                   intent = VALUES(intent),
                   action_type = VALUES(action_type),
                   parameters = VALUES(parameters)""",
                (command_phrase, intent, action_type, json.dumps(parameters or {}))
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()


# Example usage
voice_interface = VoiceInterface(db_config, openai_api_key)

# Register common commands
voice_interface.register_command(
    "read my emails",
    "read_emails",
    "fetch_and_read",
    {"max_emails": 5}
)

voice_interface.register_command(
    "schedule a meeting",
    "schedule_meeting",
    "calendar_create",
    {}
)

# Start voice session
session_id = voice_interface.start_session("user@example.com")

# Process voice input
result = voice_interface.process_voice_input(
    "user@example.com",
    session_id,
    "path/to/audio.mp3"
)

print(f"Transcribed: {result['transcribed_text']}")
print(f"Intent: {result['intent']}")
print(f"Response: {result['response_text']}")
print(f"Audio saved to: {result['audio_output_path']}")
```

### Success Criteria

- [ ] Speech recognition accuracy >95%
- [ ] TTS sounds natural and clear
- [ ] Voice commands recognized reliably
- [ ] Multi-turn conversations work smoothly
- [ ] Latency <2 seconds for full cycle
- [ ] Wake word detection accuracy >90%
- [ ] Supports multiple languages
- [ ] Voice interface accessible via mobile app

---

## Production Features

### Overview

Essential production-ready features for reliability, performance, security, and scalability in a production environment.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Production Features Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Request    │─────▶│Rate Limiter  │─────▶│  Circuit  │ │
│  │   Gateway    │      │   (Redis)    │      │  Breaker  │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         │                      │                     │       │
│         │                      ▼                     │       │
│         │              ┌──────────────┐             │       │
│         │              │    Cache     │             │       │
│         └─────────────▶│   (Redis)    │◀────────────┘       │
│                        └──────────────┘                     │
│                                │                             │
│                                ▼                             │
│                        ┌──────────────┐                     │
│                        │   Security   │                     │
│                        │   & Auth     │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

### 1. Error Recovery & Resilience

#### Implementation

```python
# app/production/error_recovery.py
from typing import Callable, Any, Optional
import time
import logging
from functools import wraps
import mysql.connector

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """Handles error recovery and resilience patterns."""

    @staticmethod
    def retry_with_backoff(
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """Decorator for retry with exponential backoff."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                delay = base_delay
                last_exception = None

                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e

                        if attempt == max_retries:
                            logger.error(
                                f"Function {func.__name__} failed after {max_retries} retries: {e}"
                            )
                            raise

                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )

                        time.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)

                raise last_exception

            return wrapper
        return decorator

    @staticmethod
    def circuit_breaker(
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        """Circuit breaker pattern implementation."""
        class CircuitBreaker:
            def __init__(self):
                self.failure_count = 0
                self.last_failure_time = None
                self.state = 'closed'  # closed, open, half_open

            def call(self, func: Callable, *args, **kwargs) -> Any:
                if self.state == 'open':
                    if time.time() - self.last_failure_time >= timeout:
                        self.state = 'half_open'
                        logger.info(f"Circuit breaker for {func.__name__} entering half-open state")
                    else:
                        raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)

                    if self.state == 'half_open':
                        self.state = 'closed'
                        self.failure_count = 0
                        logger.info(f"Circuit breaker for {func.__name__} closed")

                    return result

                except expected_exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()

                    if self.failure_count >= failure_threshold:
                        self.state = 'open'
                        logger.error(
                            f"Circuit breaker OPENED for {func.__name__} "
                            f"after {failure_threshold} failures"
                        )

                    raise

        breaker = CircuitBreaker()

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                return breaker.call(func, *args, **kwargs)
            return wrapper

        return decorator

    @staticmethod
    def graceful_degradation(fallback_func: Callable):
        """Provide fallback functionality on failure."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"Function {func.__name__} failed: {e}. "
                        f"Using fallback function."
                    )
                    return fallback_func(*args, **kwargs)
            return wrapper
        return decorator


# Example usage
@ErrorRecovery.retry_with_backoff(max_retries=3)
@ErrorRecovery.circuit_breaker(failure_threshold=5)
def call_external_api(endpoint: str) -> dict:
    """Call external API with retry and circuit breaker."""
    # API call implementation
    pass
```

#### Database Schema

```sql
-- Error logs
CREATE TABLE error_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    error_type VARCHAR(255) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context JSON,
    user_id VARCHAR(255),
    request_id VARCHAR(36),
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_error_type (error_type),
    INDEX idx_severity (severity),
    INDEX idx_occurred_at (occurred_at),
    INDEX idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Circuit breaker state
CREATE TABLE circuit_breaker_state (
    service_name VARCHAR(255) PRIMARY KEY,
    state ENUM('closed', 'open', 'half_open') DEFAULT 'closed',
    failure_count INT DEFAULT 0,
    last_failure_time TIMESTAMP NULL,
    last_success_time TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2. Rate Limiting

#### Implementation

```python
# app/production/rate_limiter.py
from typing import Optional
import redis
import time
from datetime import datetime, timedelta

class RateLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        Returns (allowed, info_dict)
        """
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"

        # Get current count
        current_count = self.redis.get(window_key)
        current_count = int(current_count) if current_count else 0

        if current_count >= max_requests:
            # Rate limit exceeded
            ttl = self.redis.ttl(window_key)
            return False, {
                'allowed': False,
                'limit': max_requests,
                'remaining': 0,
                'reset_in': ttl if ttl > 0 else window_seconds
            }

        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window_seconds)
        pipe.execute()

        return True, {
            'allowed': True,
            'limit': max_requests,
            'remaining': max_requests - current_count - 1,
            'reset_in': window_seconds
        }

    def check_user_rate_limit(
        self,
        user_id: str,
        endpoint: str = 'global'
    ) -> tuple[bool, dict]:
        """Check rate limit for a specific user and endpoint."""
        # Different limits for different endpoints
        limits = {
            'global': (100, 60),  # 100 requests per minute
            'email_send': (10, 60),  # 10 emails per minute
            'llm_query': (50, 60),  # 50 LLM queries per minute
            'api_call': (1000, 3600)  # 1000 API calls per hour
        }

        max_requests, window = limits.get(endpoint, limits['global'])
        key = f"{user_id}:{endpoint}"

        return self.check_rate_limit(key, max_requests, window)


# Middleware for FastAPI/Flask
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, rate_limiter: RateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter

    async def dispatch(self, request: Request, call_next):
        # Extract user ID from request
        user_id = request.headers.get('X-User-ID', 'anonymous')
        endpoint = request.url.path

        # Check rate limit
        allowed, info = self.rate_limiter.check_user_rate_limit(user_id, endpoint)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {info['reset_in']} seconds.",
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': str(info['reset_in'])
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers['X-RateLimit-Limit'] = str(info['limit'])
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        response.headers['X-RateLimit-Reset'] = str(info['reset_in'])

        return response
```

#### Database Schema

```sql
-- Rate limit tracking
CREATE TABLE rate_limit_violations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    violation_count INT DEFAULT 1,
    first_violation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_violation TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_endpoint (endpoint)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 3. Caching Strategy

#### Implementation

```python
# app/production/cache.py
from typing import Any, Optional, Callable
import redis
import json
import hashlib
from functools import wraps
import pickle

class CacheManager:
    """Multi-level caching with Redis."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def cache_result(
        self,
        ttl: int = 3600,
        key_prefix: str = '',
        serialize: str = 'json'
    ):
        """Decorator to cache function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                cache_key = self._generate_key(key_prefix, func.__name__, args, kwargs)

                # Try to get from cache
                cached = self.get(cache_key, serialize)
                if cached is not None:
                    return cached

                # Execute function
                result = func(*args, **kwargs)

                # Store in cache
                self.set(cache_key, result, ttl, serialize)

                return result

            return wrapper
        return decorator

    def _generate_key(
        self,
        prefix: str,
        func_name: str,
        args: tuple,
        kwargs: dict
    ) -> str:
        """Generate cache key from function arguments."""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{func_name}:{key_hash}"

    def get(self, key: str, serialize: str = 'json') -> Optional[Any]:
        """Get value from cache."""
        value = self.redis.get(key)
        if value is None:
            return None

        if serialize == 'json':
            return json.loads(value)
        elif serialize == 'pickle':
            return pickle.loads(value)
        else:
            return value.decode('utf-8')

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        serialize: str = 'json'
    ):
        """Set value in cache."""
        if serialize == 'json':
            value = json.dumps(value)
        elif serialize == 'pickle':
            value = pickle.dumps(value)

        self.redis.setex(key, ttl, value)

    def delete(self, key: str):
        """Delete key from cache."""
        self.redis.delete(key)

    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)

    def get_or_set(
        self,
        key: str,
        func: Callable,
        ttl: int = 3600,
        serialize: str = 'json'
    ) -> Any:
        """Get from cache or execute function and cache result."""
        value = self.get(key, serialize)
        if value is not None:
            return value

        value = func()
        self.set(key, value, ttl, serialize)
        return value


# Example usage
cache = CacheManager(redis_client)

@cache.cache_result(ttl=300, key_prefix='email')
def get_user_emails(user_id: str, limit: int = 50):
    """Get user emails with caching."""
    # Fetch emails from database
    return emails

# Cache email analytics
@cache.cache_result(ttl=3600, key_prefix='analytics')
def get_email_analytics(user_id: str, date_range: str):
    """Get email analytics with caching."""
    # Calculate analytics
    return analytics
```

---

### 4. Batch Processing

#### Implementation

```python
# app/production/batch_processor.py
from typing import List, Callable, Any, Optional
import mysql.connector
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Efficient batch processing for large datasets."""

    def __init__(self, db_config: dict, max_workers: int = 10):
        self.db_config = db_config
        self.max_workers = max_workers

    def process_in_batches(
        self,
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100,
        parallel: bool = True
    ) -> List[Any]:
        """Process items in batches."""
        results = []
        total_batches = (len(items) + batch_size - 1) // batch_size

        logger.info(f"Processing {len(items)} items in {total_batches} batches")

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = i // batch_size + 1

            logger.info(f"Processing batch {batch_num}/{total_batches}")

            if parallel:
                batch_results = self._process_batch_parallel(batch, process_func)
            else:
                batch_results = self._process_batch_sequential(batch, process_func)

            results.extend(batch_results)

        return results

    def _process_batch_parallel(
        self,
        batch: List[Any],
        process_func: Callable
    ) -> List[Any]:
        """Process batch items in parallel."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(process_func, item): item
                for item in batch
            }

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing item {item}: {e}")
                    results.append({'error': str(e), 'item': item})

        return results

    def _process_batch_sequential(
        self,
        batch: List[Any],
        process_func: Callable
    ) -> List[Any]:
        """Process batch items sequentially."""
        results = []

        for item in batch:
            try:
                result = process_func(item)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing item {item}: {e}")
                results.append({'error': str(e), 'item': item})

        return results

    def bulk_insert(
        self,
        table: str,
        records: List[dict],
        batch_size: int = 1000
    ):
        """Bulk insert records into database."""
        if not records:
            return

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            # Get column names from first record
            columns = list(records[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)

            insert_query = f"""
                INSERT INTO {table} ({column_names})
                VALUES ({placeholders})
            """

            # Process in batches
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                values = [tuple(record[col] for col in columns) for record in batch]

                cursor.executemany(insert_query, values)
                conn.commit()

                logger.info(f"Inserted batch {i // batch_size + 1}, {len(batch)} records")

        finally:
            cursor.close()
            conn.close()

    def bulk_update(
        self,
        table: str,
        updates: List[dict],
        key_column: str,
        batch_size: int = 1000
    ):
        """Bulk update records in database."""
        if not updates:
            return

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            # Get update columns (excluding key)
            update_columns = [col for col in updates[0].keys() if col != key_column]
            set_clause = ', '.join([f"{col} = %s" for col in update_columns])

            update_query = f"""
                UPDATE {table}
                SET {set_clause}
                WHERE {key_column} = %s
            """

            # Process in batches
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                values = [
                    tuple([record[col] for col in update_columns] + [record[key_column]])
                    for record in batch
                ]

                cursor.executemany(update_query, values)
                conn.commit()

                logger.info(f"Updated batch {i // batch_size + 1}, {len(batch)} records")

        finally:
            cursor.close()
            conn.close()


# Example: Batch process emails
batch_processor = BatchProcessor(db_config, max_workers=10)

def analyze_email(email: dict) -> dict:
    """Analyze a single email."""
    # Perform analysis
    return {
        'email_id': email['id'],
        'sentiment': 0.8,
        'priority': 0.6
    }

# Process 10,000 emails in batches
emails = fetch_emails(limit=10000)
results = batch_processor.process_in_batches(
    emails,
    analyze_email,
    batch_size=100,
    parallel=True
)

# Bulk insert results
batch_processor.bulk_insert('email_analytics', results, batch_size=1000)
```

---

### 5. Security Features

#### Implementation

```python
# app/production/security.py
from typing import Optional
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets
import mysql.connector
from cryptography.fernet import Fernet
import bcrypt

class SecurityManager:
    """Handles authentication, authorization, and encryption."""

    def __init__(self, db_config: dict, secret_key: str, encryption_key: bytes):
        self.db_config = db_config
        self.secret_key = secret_key
        self.cipher = Fernet(encryption_key)

    # JWT Token Management
    def create_access_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(hours=1)

        expire = datetime.utcnow() + expires_delta

        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }

        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=30)

        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }

        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # Password Management
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    # Data Encryption
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        encrypted = self.cipher.encrypt(data.encode('utf-8'))
        return encrypted.decode('utf-8')

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        decrypted = self.cipher.decrypt(encrypted_data.encode('utf-8'))
        return decrypted.decode('utf-8')

    # API Key Management
    def generate_api_key(self, user_id: str, name: str) -> str:
        """Generate API key for user."""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO api_keys (user_id, key_name, key_hash, created_at)
                   VALUES (%s, %s, %s, NOW())""",
                (user_id, name, key_hash)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return api_key

    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return user_id."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT user_id, is_active FROM api_keys
                   WHERE key_hash = %s""",
                (key_hash,)
            )
            result = cursor.fetchone()

            if result and result['is_active']:
                # Update last used
                cursor.execute(
                    """UPDATE api_keys SET last_used = NOW()
                       WHERE key_hash = %s""",
                    (key_hash,)
                )
                conn.commit()
                return result['user_id']

            return None
        finally:
            cursor.close()
            conn.close()

    # Input Validation
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
```

#### Database Schema

```sql
-- API keys
CREATE TABLE api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    key_name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_key_hash (key_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Security audit log
CREATE TABLE security_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Implementation Roadmap Summary

### Phase Priority Matrix

| Phase                          | Priority | Complexity | Dependencies | Estimated Time |
| ------------------------------ | -------- | ---------- | ------------ | -------------- |
| Phase 6: Persistent Memory     | High     | Medium     | None         | 3-4 weeks      |
| Phase 7: Scheduled Jobs        | High     | Medium     | Phase 6      | 2-3 weeks      |
| Phase 8: Multi-Step Planning   | Medium   | High       | Phase 6      | 4-5 weeks      |
| Phase 9: Calendar Integration  | Medium   | Medium     | Phase 7      | 2-3 weeks      |
| Phase 10: Observability        | High     | Medium     | None         | 2-3 weeks      |
| Phase 11: Email Intelligence   | Medium   | High       | Phase 6, 10  | 3-4 weeks      |
| Phase 12: Evaluation Framework | High     | Medium     | Phase 10     | 2-3 weeks      |
| Phase 13: Voice Interface      | Low      | Medium     | Phase 6      | 3-4 weeks      |
| Production Features            | Critical | High       | All phases   | Ongoing        |

### Recommended Implementation Order

1. **Phase 10: Observability** (Week 1-3)
   - Essential for monitoring all other features
   - Implement first to track system health

2. **Phase 6: Persistent Memory** (Week 4-7)
   - Foundation for many other features
   - Critical for user experience

3. **Production Features** (Week 8-11)
   - Error recovery, rate limiting, caching
   - Essential for reliability

4. **Phase 7: Scheduled Jobs** (Week 12-14)
   - Builds on memory system
   - Enables automation

5. **Phase 12: Evaluation Framework** (Week 15-17)
   - Measure quality of all features
   - Guide improvements

6. **Phase 9: Calendar Integration** (Week 18-20)
   - High user value
   - Moderate complexity

7. **Phase 11: Email Intelligence** (Week 21-24)
   - Advanced analytics
   - Requires memory and observability

8. **Phase 8: Multi-Step Planning** (Week 25-29)
   - Complex feature
   - Builds on multiple systems

9. **Phase 13: Voice Interface** (Week 30-33)
   - Nice-to-have feature
   - Can be added last

### Success Metrics

- **System Reliability**: 99.9% uptime
- **Performance**: <200ms p95 latency
- **Scalability**: Support 10,000+ concurrent users
- **Security**: Zero critical vulnerabilities
- **User Satisfaction**: >4.5/5 rating
- **Feature Adoption**: >70% of users use advanced features
- **Cost Efficiency**: <$0.10 per user per day

---

## Conclusion

This roadmap provides a comprehensive plan for evolving the AI Executive Assistant into a production-ready, enterprise-grade system. Each phase builds upon previous work and adds significant value to users.

### Key Takeaways

1. **MySQL-First Approach**: All data persistence uses MySQL for reliability and scalability
2. **Production-Ready**: Emphasis on error handling, monitoring, and security
3. **Incremental Development**: Each phase can be developed and deployed independently
4. **User-Centric**: Features prioritized based on user value and impact
5. **Measurable**: Clear success criteria for each phase

### Next Steps

1. Review and prioritize phases based on business needs
2. Set up development environment for selected phase
3. Create detailed technical specifications
4. Begin implementation with Phase 10 (Observability)
5. Iterate based on user feedback and metrics

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-15  
**Maintained By**: Development Team
