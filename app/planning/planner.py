"""
Task Planner
LLM-powered multi-step task planning and decomposition
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from app.config.llm_config import create_llm
from app.planning.plan_store import PlanStore

logger = logging.getLogger(__name__)


class PlanStatus(str, Enum):
    """Plan execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Step execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """A single step in a plan"""
    step_number: int
    description: str
    action_type: str
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[int]] = None
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Plan:
    """A multi-step plan"""
    id: str
    goal: str
    description: Optional[str]
    steps: List[PlanStep]
    status: PlanStatus = PlanStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskPlanner:
    """
    LLM-powered task planner
    
    Decomposes complex tasks into executable steps using LLM reasoning.
    """
    
    def __init__(self, plan_store: Optional[PlanStore] = None):
        """Initialize task planner"""
        self.plan_store = plan_store or PlanStore()
        self.llm = create_llm(temperature=0.7)
        logger.info("Task planner initialized")
    
    def create_plan(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Plan:
        """
        Create a multi-step plan for achieving a goal
        
        Args:
            goal: The goal to achieve
            context: Additional context for planning
        
        Returns:
            Plan object with decomposed steps
        """
        logger.info(f"Creating plan for goal: {goal}")
        
        # Build planning prompt
        prompt = self._build_planning_prompt(goal, context)
        
        # Get plan from LLM
        response = self.llm.invoke(prompt)
        plan_text = str(response.content)
        
        # Parse plan into steps
        steps = self._parse_plan(plan_text)
        
        # Create plan object
        plan_id = str(uuid.uuid4())
        plan = Plan(
            id=plan_id,
            goal=goal,
            description=f"Plan to: {goal}",
            steps=steps,
            status=PlanStatus.PENDING,
            created_at=datetime.now(),
            metadata=context
        )
        
        # Store plan
        self._store_plan(plan)
        
        logger.info(f"Created plan {plan_id} with {len(steps)} steps")
        return plan
    
    def _build_planning_prompt(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for LLM to create a plan"""
        
        context_str = ""
        if context:
            context_str = "\n\nContext:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
        
        prompt = f"""You are an AI task planner. Break down the following goal into clear, actionable steps.

Goal: {goal}{context_str}

Create a detailed step-by-step plan. For each step, provide:
1. A clear description of what needs to be done
2. The type of action (e.g., "email", "search", "analyze", "draft", "schedule")
3. Any parameters needed for the action
4. Dependencies on previous steps (if any)

Format your response as a numbered list of steps. Each step should be on a new line starting with the step number.

Example format:
1. [ACTION_TYPE] Description of step 1 | Parameters: {{param1: value1}} | Dependencies: []
2. [ACTION_TYPE] Description of step 2 | Parameters: {{param2: value2}} | Dependencies: [1]

Now create the plan:"""
        
        return prompt
    
    def _parse_plan(self, plan_text: str) -> List[PlanStep]:
        """Parse LLM response into plan steps"""
        steps = []
        lines = plan_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            
            try:
                # Extract step number
                parts = line.split('.', 1)
                if len(parts) < 2:
                    continue
                
                step_number = int(parts[0].strip())
                rest = parts[1].strip()
                
                # Extract action type (if in brackets)
                action_type = "general"
                if rest.startswith('['):
                    end_bracket = rest.find(']')
                    if end_bracket > 0:
                        action_type = rest[1:end_bracket].lower()
                        rest = rest[end_bracket + 1:].strip()
                
                # Extract description (before |)
                description = rest
                parameters = None
                dependencies = None
                
                if '|' in rest:
                    parts = rest.split('|')
                    description = parts[0].strip()
                    
                    # Parse parameters and dependencies
                    for part in parts[1:]:
                        part = part.strip()
                        if part.lower().startswith('parameters:'):
                            # Simple parameter extraction
                            param_str = part.split(':', 1)[1].strip()
                            # For now, store as string; could parse JSON
                            parameters = {"raw": param_str}
                        elif part.lower().startswith('dependencies:'):
                            # Extract dependency numbers
                            dep_str = part.split(':', 1)[1].strip()
                            # Extract numbers from string like "[1, 2]" or "[]"
                            import re
                            deps = re.findall(r'\d+', dep_str)
                            dependencies = [int(d) for d in deps] if deps else None
                
                step = PlanStep(
                    step_number=step_number,
                    description=description,
                    action_type=action_type,
                    parameters=parameters,
                    dependencies=dependencies
                )
                
                steps.append(step)
                
            except Exception as e:
                logger.warning(f"Failed to parse step: {line}. Error: {e}")
                continue
        
        # If parsing failed, create a simple single-step plan
        if not steps:
            steps = [PlanStep(
                step_number=1,
                description=plan_text[:200],  # First 200 chars
                action_type="general"
            )]
        
        return steps
    
    def _store_plan(self, plan: Plan):
        """Store plan in database"""
        # Store plan
        self.plan_store.add_plan(
            plan_id=plan.id,
            goal=plan.goal,
            description=plan.description,
            status=plan.status.value,
            metadata=plan.metadata
        )
        
        # Store steps
        for step in plan.steps:
            self.plan_store.add_step(
                plan_id=plan.id,
                step_number=step.step_number,
                description=step.description,
                action_type=step.action_type,
                parameters=step.parameters,
                dependencies=step.dependencies,
                status=step.status.value
            )
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan by ID"""
        plan_data = self.plan_store.get_plan(plan_id)
        if not plan_data:
            return None
        
        steps_data = self.plan_store.get_plan_steps(plan_id)
        
        steps = [
            PlanStep(
                step_number=s["step_number"],
                description=s["description"],
                action_type=s["action_type"],
                parameters=s["parameters"],
                dependencies=s["dependencies"],
                status=StepStatus(s["status"]),
                result=s["result"],
                error=s["error"],
                started_at=datetime.fromisoformat(s["started_at"]) if s["started_at"] else None,
                completed_at=datetime.fromisoformat(s["completed_at"]) if s["completed_at"] else None
            )
            for s in steps_data
        ]
        
        return Plan(
            id=plan_data["id"],
            goal=plan_data["goal"],
            description=plan_data["description"],
            steps=steps,
            status=PlanStatus(plan_data["status"]),
            created_at=datetime.fromisoformat(plan_data["created_at"]) if plan_data["created_at"] else None,
            started_at=datetime.fromisoformat(plan_data["started_at"]) if plan_data["started_at"] else None,
            completed_at=datetime.fromisoformat(plan_data["completed_at"]) if plan_data["completed_at"] else None,
            metadata=plan_data["metadata"]
        )
    
    def get_all_plans(self, status: Optional[PlanStatus] = None) -> List[Plan]:
        """Get all plans, optionally filtered by status"""
        status_str = status.value if status else None
        plans_data = self.plan_store.get_all_plans(status=status_str)
        
        plans = []
        for plan_data in plans_data:
            plan = self.get_plan(plan_data["id"])
            if plan:
                plans.append(plan)
        
        return plans
    
    def update_plan_status(
        self,
        plan_id: str,
        status: PlanStatus,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update plan status"""
        self.plan_store.update_plan_status(
            plan_id=plan_id,
            status=status.value,
            started_at=started_at,
            completed_at=completed_at
        )
    
    def update_step_status(
        self,
        plan_id: str,
        step_number: int,
        status: StepStatus,
        result: Optional[str] = None,
        error: Optional[str] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        """Update step status"""
        self.plan_store.update_step_status(
            plan_id=plan_id,
            step_number=step_number,
            status=status.value,
            result=result,
            error=error,
            started_at=started_at,
            completed_at=completed_at
        )
    
    def get_next_steps(self, plan: Plan) -> List[PlanStep]:
        """Get next executable steps (dependencies satisfied)"""
        completed_steps = {
            step.step_number 
            for step in plan.steps 
            if step.status == StepStatus.COMPLETED
        }
        
        next_steps = []
        for step in plan.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            # Check if dependencies are satisfied
            if step.dependencies:
                if all(dep in completed_steps for dep in step.dependencies):
                    next_steps.append(step)
            else:
                next_steps.append(step)
        
        return next_steps
    
    def get_plan_progress(self, plan: Plan) -> Dict[str, Any]:
        """Get plan execution progress"""
        total_steps = len(plan.steps)
        completed_steps = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for s in plan.steps if s.status == StepStatus.FAILED)
        in_progress_steps = sum(1 for s in plan.steps if s.status == StepStatus.IN_PROGRESS)
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "in_progress_steps": in_progress_steps,
            "pending_steps": total_steps - completed_steps - failed_steps - in_progress_steps,
            "completion_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "status": plan.status.value
        }


# Global planner instance
_planner_instance: Optional[TaskPlanner] = None


def create_planner(plan_store: Optional[PlanStore] = None) -> TaskPlanner:
    """Create and return a planner instance"""
    global _planner_instance
    _planner_instance = TaskPlanner(plan_store=plan_store)
    return _planner_instance


def get_planner() -> Optional[TaskPlanner]:
    """Get the global planner instance"""
    return _planner_instance

# Made with Bob
