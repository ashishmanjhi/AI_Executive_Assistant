# Phase 8: Multi-Step Planning - Implementation Guide

## Overview

Phase 8 implements a sophisticated multi-step planning system that can decompose complex goals into actionable steps, manage dependencies, and execute plans autonomously.

## Architecture

### Components

1. **Plan Store** (`app/planning/plan_store.py`)
   - SQLite-based persistence for plans and steps
   - CRUD operations for plan management
   - Status tracking and statistics

2. **Task Planner** (`app/planning/planner.py`)
   - LLM-powered task decomposition
   - Dependency management
   - Progress tracking
   - Next step determination

3. **Plan Executor** (`app/planning/plan_executor.py`)
   - Step-by-step execution engine
   - Action handler registry
   - Error handling and recovery

## Key Features

### 1. Intelligent Task Decomposition

The system uses an LLM to break down complex goals into actionable steps:

```python
from app.planning import TaskPlanner

planner = TaskPlanner()

# Create a plan from a natural language goal
plan = planner.create_plan(
    goal="Prepare a weekly summary report and email it to my team",
    context={"user": "john@example.com"}
)

print(f"Created plan with {len(plan.steps)} steps")
for step in plan.steps:
    print(f"{step.step_number}. {step.description}")
```

### 2. Dependency Management

Steps can depend on the completion of other steps:

```python
# Example plan structure
Plan:
  Step 1: Fetch recent emails (no dependencies)
  Step 2: Analyze email content (depends on Step 1)
  Step 3: Generate summary (depends on Step 2)
  Step 4: Draft email (depends on Step 3)
  Step 5: Send email (depends on Step 4)
```

The executor automatically determines which steps can run based on completed dependencies.

### 3. Action Types

The system supports multiple action types:

- **email**: Email-related operations (search, fetch, summarize)
- **search**: Semantic search using RAG
- **analyze**: Analysis and Q&A using RAG
- **draft**: Content generation using memory agent
- **general**: General-purpose actions

### 4. Custom Action Handlers

You can register custom action handlers:

```python
from app.planning import PlanExecutor, PlanStep

executor = PlanExecutor(planner)

def custom_handler(step: PlanStep):
    # Your custom logic here
    return {"result": "success"}

executor.register_action_handler("custom_action", custom_handler)
```

## Data Models

### Plan

```python
@dataclass
class Plan:
    id: str
    goal: str
    description: str
    steps: List[PlanStep]
    status: PlanStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
```

### PlanStep

```python
@dataclass
class PlanStep:
    step_number: int
    description: str
    action_type: str
    parameters: Optional[Dict[str, Any]]
    dependencies: Optional[List[int]]
    status: StepStatus
    result: Optional[str]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
```

### Status Enums

```python
class PlanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

## Usage Examples

### Example 1: Simple Plan Execution

```python
from app.planning import TaskPlanner, PlanExecutor

# Initialize
planner = TaskPlanner()
executor = PlanExecutor(planner)

# Create plan
plan = planner.create_plan(
    goal="Find and summarize emails about project updates",
    context={}
)

# Execute plan
success = executor.execute_plan(plan)

if success:
    print("Plan completed successfully!")

    # Get results
    plan = planner.get_plan(plan.id)
    for step in plan.steps:
        print(f"Step {step.step_number}: {step.status}")
        if step.result:
            print(f"  Result: {step.result}")
```

### Example 2: Monitoring Progress

```python
# Get plan progress
progress = planner.get_plan_progress(plan)

print(f"Progress: {progress['progress_percentage']}%")
print(f"Completed: {progress['completed_steps']}/{progress['total_steps']}")
print(f"Status: {progress['status']}")

# Get next executable steps
next_steps = planner.get_next_steps(plan)
print(f"Next steps: {[s.step_number for s in next_steps]}")
```

### Example 3: Manual Step Execution

```python
# Execute individual steps
for step in plan.steps:
    if step.status == StepStatus.PENDING:
        success = executor.execute_step(plan.id, step)
        if success:
            print(f"Step {step.step_number} completed")
        else:
            print(f"Step {step.step_number} failed")
            break
```

### Example 4: Plan Management

```python
# List all plans
plans = planner.store.list_plans()
for plan in plans:
    print(f"{plan.id}: {plan.goal} ({plan.status})")

# Get specific plan
plan = planner.get_plan("plan_123")

# Update plan status
planner.update_plan_status(
    plan_id="plan_123",
    status=PlanStatus.CANCELLED
)

# Delete plan
planner.store.delete_plan("plan_123")
```

## Database Schema

### Plans Table

```sql
CREATE TABLE plans (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    metadata TEXT
)
```

### Plan Steps Table

```sql
CREATE TABLE plan_steps (
    plan_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    action_type TEXT NOT NULL,
    parameters TEXT,
    dependencies TEXT,
    status TEXT NOT NULL,
    result TEXT,
    error TEXT,
    started_at TEXT,
    completed_at TEXT,
    PRIMARY KEY (plan_id, step_number),
    FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
)
```

## Integration with Other Phases

### Phase 5: Multi-Agent System

Plans can leverage the multi-agent system for complex tasks:

```python
# The executor can route actions to appropriate agents
# Email actions -> Email Agent
# Knowledge actions -> Knowledge Agent
```

### Phase 6: Persistent Memory

Plans can use memory for context-aware execution:

```python
# Steps can access user preferences and conversation history
# Memory is automatically used in general actions
```

### Phase 7: Scheduled Jobs

Plans can be scheduled for autonomous execution:

```python
from app.scheduler import JobScheduler

scheduler = JobScheduler()

def execute_daily_plan():
    plan = planner.create_plan(
        goal="Generate daily summary report",
        context={}
    )
    executor.execute_plan(plan)

scheduler.add_job(
    job_id="daily_plan",
    func=execute_daily_plan,
    trigger="cron",
    hour=9,
    minute=0
)
```

## Error Handling

The system includes comprehensive error handling:

1. **Step Failures**: Failed steps are marked with error messages
2. **Plan Failures**: Plans fail if critical steps fail
3. **Dependency Failures**: Steps with failed dependencies are skipped
4. **Recovery**: Plans can be resumed after fixing issues

```python
# Check for failures
plan = planner.get_plan(plan_id)
failed_steps = [s for s in plan.steps if s.status == StepStatus.FAILED]

for step in failed_steps:
    print(f"Step {step.step_number} failed: {step.error}")

    # Retry failed step
    executor.execute_step(plan.id, step)
```

## Testing

Run the test suite:

```bash
python tests/test_planning.py
```

Tests cover:

- Plan creation and storage
- Step management
- Dependency resolution
- Plan execution
- Progress tracking
- Custom action handlers

## Performance Considerations

1. **LLM Calls**: Plan creation requires LLM calls (can be slow)
2. **Database**: SQLite is suitable for single-user scenarios
3. **Concurrency**: Current implementation is single-threaded
4. **Memory**: Plans are loaded entirely into memory

## Future Enhancements

1. **Parallel Execution**: Execute independent steps in parallel
2. **Conditional Steps**: Steps that execute based on conditions
3. **Sub-plans**: Nested plans for complex workflows
4. **Plan Templates**: Reusable plan templates
5. **Human-in-the-Loop**: Approval gates for critical steps
6. **Plan Visualization**: Visual representation of plan execution
7. **Rollback**: Undo completed steps if plan fails

## Troubleshooting

### Issue: Plans not executing

**Solution**: Check that:

- LLM is properly configured
- Database is accessible
- Action handlers are registered

### Issue: Steps stuck in pending

**Solution**: Check dependencies:

```python
plan = planner.get_plan(plan_id)
for step in plan.steps:
    if step.status == StepStatus.PENDING and step.dependencies:
        deps_completed = all(
            plan.steps[d-1].status == StepStatus.COMPLETED
            for d in step.dependencies
        )
        if not deps_completed:
            print(f"Step {step.step_number} waiting on dependencies")
```

### Issue: Action handler not found

**Solution**: Register the handler:

```python
executor.register_action_handler("my_action", my_handler)
```

## Best Practices

1. **Clear Goals**: Provide specific, actionable goals
2. **Context**: Include relevant context for better planning
3. **Error Handling**: Always check execution results
4. **Monitoring**: Track plan progress regularly
5. **Cleanup**: Delete completed plans periodically
6. **Testing**: Test custom action handlers thoroughly

## API Reference

### TaskPlanner

```python
class TaskPlanner:
    def __init__(self, db_path: str = "data/plans.db")
    def create_plan(self, goal: str, context: Dict) -> Plan
    def get_plan(self, plan_id: str) -> Optional[Plan]
    def update_plan_status(self, plan_id: str, status: PlanStatus, ...)
    def update_step_status(self, plan_id: str, step_number: int, ...)
    def get_next_steps(self, plan: Plan) -> List[PlanStep]
    def get_plan_progress(self, plan: Plan) -> Dict[str, Any]
```

### PlanExecutor

```python
class PlanExecutor:
    def __init__(self, planner: TaskPlanner)
    def register_action_handler(self, action_type: str, handler: Callable)
    def execute_plan(self, plan: Plan) -> bool
    def execute_step(self, plan_id: str, step: PlanStep) -> bool
```

### PlanStore

```python
class PlanStore:
    def __init__(self, db_path: str = "data/plans.db")
    def add_plan(self, plan_id: str, goal: str, ...)
    def add_step(self, plan_id: str, step_number: int, ...)
    def get_plan(self, plan_id: str) -> Optional[Plan]
    def update_plan_status(self, plan_id: str, status: str, ...)
    def update_step_status(self, plan_id: str, step_number: int, ...)
    def delete_plan(self, plan_id: str)
    def get_plan_statistics(self) -> Dict[str, Any]
```

## Conclusion

Phase 8 provides a powerful multi-step planning system that enables the AI Executive Assistant to handle complex, multi-step tasks autonomously. The system is extensible, persistent, and integrates seamlessly with other phases.

For questions or issues, refer to the test suite or create an issue in the project repository.
