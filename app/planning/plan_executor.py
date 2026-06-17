"""
Plan Executor
Executes multi-step plans with action handlers
"""

import logging
from datetime import datetime
from typing import Dict, Callable, Optional, Any

from app.planning.planner import Plan, PlanStep, PlanStatus, StepStatus, TaskPlanner
from app.tools.email_tools import get_recent_emails, search_emails, summarize_emails
from app.tools.rag_tools import search_email_history, answer_from_emails
from app.agents.memory_agent import create_memory_agent

logger = logging.getLogger(__name__)


class PlanExecutor:
    """
    Executes multi-step plans
    
    Manages step execution with action handlers and dependency resolution.
    """
    
    def __init__(self, planner: TaskPlanner):
        """Initialize plan executor"""
        self.planner = planner
        self.action_handlers: Dict[str, Callable] = {}
        
        # Register default action handlers
        self._register_default_handlers()
        
        logger.info("Plan executor initialized")
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self.register_action_handler("email", self._handle_email_action)
        self.register_action_handler("search", self._handle_search_action)
        self.register_action_handler("analyze", self._handle_analyze_action)
        self.register_action_handler("draft", self._handle_draft_action)
        self.register_action_handler("general", self._handle_general_action)
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a custom action handler"""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered action handler: {action_type}")
    
    def execute_plan(self, plan: Plan) -> bool:
        """
        Execute a complete plan
        
        Args:
            plan: The plan to execute
        
        Returns:
            True if plan completed successfully
        """
        logger.info(f"Starting execution of plan: {plan.id}")
        
        # Update plan status
        self.planner.update_plan_status(
            plan_id=plan.id,
            status=PlanStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            # Execute steps in order, respecting dependencies
            while True:
                # Get next executable steps
                next_steps = self.planner.get_next_steps(plan)
                
                if not next_steps:
                    # Check if all steps are completed
                    all_completed = all(
                        step.status == StepStatus.COMPLETED 
                        for step in plan.steps
                    )
                    
                    if all_completed:
                        # Plan completed successfully
                        self.planner.update_plan_status(
                            plan_id=plan.id,
                            status=PlanStatus.COMPLETED,
                            completed_at=datetime.now()
                        )
                        logger.info(f"Plan {plan.id} completed successfully")
                        return True
                    else:
                        # No more executable steps but not all completed
                        # Some steps may have failed or have unsatisfied dependencies
                        self.planner.update_plan_status(
                            plan_id=plan.id,
                            status=PlanStatus.FAILED,
                            completed_at=datetime.now()
                        )
                        logger.error(f"Plan {plan.id} failed: no more executable steps")
                        return False
                
                # Execute next steps
                for step in next_steps:
                    success = self.execute_step(plan.id, step)
                    if not success:
                        logger.warning(f"Step {step.step_number} failed")
                
                # Reload plan to get updated step statuses
                plan = self.planner.get_plan(plan.id)
                if not plan:
                    logger.error(f"Failed to reload plan {plan.id}")
                    return False
        
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            self.planner.update_plan_status(
                plan_id=plan.id,
                status=PlanStatus.FAILED,
                completed_at=datetime.now()
            )
            return False
    
    def execute_step(self, plan_id: str, step: PlanStep) -> bool:
        """
        Execute a single step
        
        Args:
            plan_id: ID of the plan
            step: The step to execute
        
        Returns:
            True if step completed successfully
        """
        logger.info(f"Executing step {step.step_number}: {step.description}")
        
        # Update step status to in_progress
        self.planner.update_step_status(
            plan_id=plan_id,
            step_number=step.step_number,
            status=StepStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            # Get action handler
            handler = self.action_handlers.get(
                step.action_type,
                self.action_handlers.get("general")
            )
            
            if not handler:
                raise ValueError(f"No handler for action type: {step.action_type}")
            
            # Execute action
            result = handler(step)
            
            # Update step status to completed
            self.planner.update_step_status(
                plan_id=plan_id,
                step_number=step.step_number,
                status=StepStatus.COMPLETED,
                result=str(result),
                completed_at=datetime.now()
            )
            
            logger.info(f"Step {step.step_number} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Step {step.step_number} failed: {e}")
            
            # Update step status to failed
            self.planner.update_step_status(
                plan_id=plan_id,
                step_number=step.step_number,
                status=StepStatus.FAILED,
                error=str(e),
                completed_at=datetime.now()
            )
            
            return False
    
    # Default action handlers
    
    def _handle_email_action(self, step: PlanStep) -> Dict[str, Any]:
        """Handle email-related actions"""
        description_lower = step.description.lower()
        
        if "search" in description_lower or "find" in description_lower:
            # Search emails
            query = step.parameters.get("query", "") if step.parameters else ""
            if not query:
                # Extract query from description
                query = step.description
            
            result = search_emails.invoke({"query": query, "max_results": 10})
            return {
                "action": "email_search",
                "query": query,
                "result": result
            }
        
        elif "recent" in description_lower or "latest" in description_lower:
            # Get recent emails
            result = get_recent_emails.invoke({"max_results": 10})
            return {
                "action": "recent_emails",
                "result": result
            }
        
        elif "summarize" in description_lower:
            # Summarize emails
            result = get_recent_emails.invoke({"max_results": 5})
            return {
                "action": "email_summary",
                "result": result
            }
        
        else:
            return {
                "action": "email_general",
                "message": f"Processed email action: {step.description}"
            }
    
    def _handle_search_action(self, step: PlanStep) -> Dict[str, Any]:
        """Handle search actions"""
        query = step.parameters.get("query", "") if step.parameters else step.description
        
        # Use RAG semantic search
        result = search_email_history.invoke({"query": query, "max_results": 5})
        
        return {
            "action": "search",
            "query": query,
            "result": result
        }
    
    def _handle_analyze_action(self, step: PlanStep) -> Dict[str, Any]:
        """Handle analysis actions"""
        question = step.parameters.get("question", "") if step.parameters else step.description
        
        # Use RAG Q&A
        answer = answer_from_emails.invoke({"question": question})
        
        return {
            "action": "analyze",
            "question": question,
            "answer": answer
        }
    
    def _handle_draft_action(self, step: PlanStep) -> Dict[str, Any]:
        """Handle drafting actions"""
        # Use memory agent to draft
        agent = create_memory_agent(session_id="plan_executor")
        
        prompt = f"Draft the following: {step.description}"
        if step.parameters:
            prompt += f"\n\nParameters: {step.parameters}"
        
        response = agent.process_message(prompt)
        
        return {
            "action": "draft",
            "description": step.description,
            "draft": response
        }
    
    def _handle_general_action(self, step: PlanStep) -> Dict[str, Any]:
        """Handle general actions"""
        # Use memory agent for general tasks
        agent = create_memory_agent(session_id="plan_executor")
        
        response = agent.process_message(step.description)
        
        return {
            "action": "general",
            "description": step.description,
            "result": response
        }

# Made with Bob
