"""
Test Suite for Multi-Step Planning System
Tests plan creation, execution, and management
"""

import os
import sys
import unittest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.planning import (
    PlanStore,
    TaskPlanner,
    PlanExecutor,
    Plan,
    PlanStep,
    PlanStatus,
    StepStatus
)


class TestPlanStore(unittest.TestCase):
    """Test plan storage functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.db_path = "test_plans.db"
        self.store = PlanStore(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_add_plan(self):
        """Test adding a plan"""
        plan_id = "test_plan_1"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Test goal",
            description="Test description",
            status=PlanStatus.PENDING,
            metadata={"test": "data"}
        )
        
        plan_data = self.store.get_plan(plan_id)
        self.assertIsNotNone(plan_data)
        self.assertEqual(plan_data['id'], plan_id)
        self.assertEqual(plan_data['goal'], "Test goal")
        self.assertEqual(plan_data['status'], PlanStatus.PENDING.value)
    
    def test_add_steps(self):
        """Test adding steps to a plan"""
        plan_id = "test_plan_2"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Multi-step goal",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        # Add steps
        self.store.add_step(
            plan_id=plan_id,
            step_number=1,
            description="Step 1",
            action_type="email",
            parameters={"query": "test"},
            dependencies=None,
            status=StepStatus.PENDING
        )
        
        self.store.add_step(
            plan_id=plan_id,
            step_number=2,
            description="Step 2",
            action_type="analyze",
            parameters={},
            dependencies=[1],
            status=StepStatus.PENDING
        )
        
        steps = self.store.get_plan_steps(plan_id)
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0]['step_number'], 1)
        self.assertEqual(steps[1]['dependencies'], [1])
    
    def test_update_plan_status(self):
        """Test updating plan status"""
        plan_id = "test_plan_3"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Status test",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        # Update to in progress
        now = datetime.now()
        self.store.update_plan_status(
            plan_id=plan_id,
            status=PlanStatus.IN_PROGRESS,
            started_at=now
        )
        
        plan_data = self.store.get_plan(plan_id)
        self.assertEqual(plan_data['status'], PlanStatus.IN_PROGRESS.value)
        self.assertIsNotNone(plan_data['started_at'])
    
    def test_update_step_status(self):
        """Test updating step status"""
        plan_id = "test_plan_4"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Step status test",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        self.store.add_step(
            plan_id=plan_id,
            step_number=1,
            description="Test step",
            action_type="general",
            parameters={},
            dependencies=None,
            status=StepStatus.PENDING
        )
        
        # Update step status
        self.store.update_step_status(
            plan_id=plan_id,
            step_number=1,
            status=StepStatus.COMPLETED,
            result="Success",
            completed_at=datetime.now()
        )
        
        steps = self.store.get_plan_steps(plan_id)
        self.assertEqual(steps[0]['status'], StepStatus.COMPLETED.value)
        self.assertEqual(steps[0]['result'], "Success")
    
    def test_list_plans(self):
        """Test listing all plans"""
        # Add multiple plans
        for i in range(3):
            self.store.add_plan(
                plan_id=f"plan_{i}",
                goal=f"Goal {i}",
                description="Test",
                status=PlanStatus.PENDING,
                metadata={}
            )
        
        # Get all plans by querying individually
        plan_count = 0
        for i in range(3):
            plan = self.store.get_plan(f"plan_{i}")
            if plan:
                plan_count += 1
        self.assertEqual(plan_count, 3)
    
    def test_delete_plan(self):
        """Test deleting a plan"""
        plan_id = "test_plan_delete"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Delete test",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        self.store.delete_plan(plan_id)
        plan = self.store.get_plan(plan_id)
        self.assertIsNone(plan)


class TestTaskPlanner(unittest.TestCase):
    """Test task planning functionality"""
    
    def setUp(self):
        """Set up test planner"""
        self.db_path = "test_planner.db"
        self.store = PlanStore(self.db_path)
        self.planner = TaskPlanner(plan_store=self.store)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_create_simple_plan(self):
        """Test creating a simple plan"""
        goal = "Send a summary of recent emails to my manager"
        context = {"user": "test_user"}
        
        plan = self.planner.create_plan(goal, context)
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan.goal, goal)
        self.assertEqual(plan.status, PlanStatus.PENDING)
        self.assertGreater(len(plan.steps), 0)
        
        print(f"\nCreated plan with {len(plan.steps)} steps:")
        for step in plan.steps:
            print(f"  {step.step_number}. {step.description} ({step.action_type})")
    
    def test_get_next_steps(self):
        """Test getting next executable steps"""
        # Create a plan with dependencies
        plan_id = "test_next_steps"
        self.planner.store.add_plan(
            plan_id=plan_id,
            goal="Test dependencies",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        # Add steps with dependencies
        self.store.add_step(
            plan_id=plan_id,
            step_number=1,
            description="Step 1",
            action_type="general",
            parameters={},
            dependencies=None,
            status=StepStatus.PENDING
        )
        
        self.store.add_step(
            plan_id=plan_id,
            step_number=2,
            description="Step 2",
            action_type="general",
            parameters={},
            dependencies=[1],
            status=StepStatus.PENDING
        )
        
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        
        # Initially, only step 1 should be executable
        assert plan is not None
        next_steps = self.planner.get_next_steps(plan)
        self.assertEqual(len(next_steps), 1)
        self.assertEqual(next_steps[0].step_number, 1)
        
        # Complete step 1
        self.planner.update_step_status(
            plan_id=plan_id,
            step_number=1,
            status=StepStatus.COMPLETED,
            completed_at=datetime.now()
        )
        
        # Now step 2 should be executable
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        next_steps = self.planner.get_next_steps(plan)
        self.assertEqual(len(next_steps), 1)
        self.assertEqual(next_steps[0].step_number, 2)
    
    def test_get_plan_progress(self):
        """Test calculating plan progress"""
        plan_id = "test_progress"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Progress test",
            description="Test",
            status=PlanStatus.IN_PROGRESS,
            metadata={}
        )
        
        # Add 4 steps
        for i in range(1, 5):
            self.store.add_step(
                plan_id=plan_id,
                step_number=i,
                description=f"Step {i}",
                action_type="general",
                parameters={},
                dependencies=None,
                status=StepStatus.PENDING
            )
        
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        
        # Initially 0% complete
        progress = self.planner.get_plan_progress(plan)
        self.assertEqual(progress["completed_steps"], 0)
        self.assertEqual(progress["total_steps"], 4)
        self.assertEqual(progress["progress_percentage"], 0.0)
        
        # Complete 2 steps
        for i in [1, 2]:
            self.planner.update_step_status(
                plan_id=plan_id,
                step_number=i,
                status=StepStatus.COMPLETED,
                completed_at=datetime.now()
            )
        
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        progress = self.planner.get_plan_progress(plan)
        self.assertEqual(progress["completed_steps"], 2)
        self.assertEqual(progress["progress_percentage"], 50.0)


class TestPlanExecutor(unittest.TestCase):
    """Test plan execution functionality"""
    
    def setUp(self):
        """Set up test executor"""
        self.db_path = "test_executor.db"
        self.store = PlanStore(self.db_path)
        self.planner = TaskPlanner(plan_store=self.store)
        self.executor = PlanExecutor(self.planner)
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
    
    def test_execute_simple_plan(self):
        """Test executing a simple plan"""
        # Create a simple plan manually
        plan_id = "test_execute_simple"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Execute simple test",
            description="Test execution",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        # Add a simple general action step
        self.store.add_step(
            plan_id=plan_id,
            step_number=1,
            description="Say hello",
            action_type="general",
            parameters={},
            dependencies=None,
            status=StepStatus.PENDING
        )
        
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        
        # Execute the plan
        success = self.executor.execute_plan(plan)
        
        # Check results
        self.assertTrue(success)
        
        # Reload plan to check status
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        self.assertEqual(plan.status, PlanStatus.COMPLETED)
        self.assertEqual(plan.steps[0].status, StepStatus.COMPLETED)
        
        print(f"\nPlan executed successfully")
        print(f"Step result: {plan.steps[0].result}")
    
    def test_custom_action_handler(self):
        """Test registering and using custom action handler"""
        # Register custom handler
        def custom_handler(step: PlanStep):
            return {"custom": "result", "step": step.description}
        
        self.executor.register_action_handler("custom", custom_handler)
        
        # Create plan with custom action
        plan_id = "test_custom_handler"
        self.store.add_plan(
            plan_id=plan_id,
            goal="Test custom handler",
            description="Test",
            status=PlanStatus.PENDING,
            metadata={}
        )
        
        self.store.add_step(
            plan_id=plan_id,
            step_number=1,
            description="Custom action",
            action_type="custom",
            parameters={},
            dependencies=None,
            status=StepStatus.PENDING
        )
        
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        success = self.executor.execute_plan(plan)
        
        self.assertTrue(success)
        
        # Check custom result
        plan = self.planner.get_plan(plan_id)
        assert plan is not None
        result = plan.steps[0].result or ''
        self.assertIn("custom", result)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPlanStore))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskPlanner))
    suite.addTests(loader.loadTestsFromTestCase(TestPlanExecutor))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

# Made with Bob
