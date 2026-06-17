"""
Verify all imports work correctly
"""

import sys

def verify_imports():
    """Test that all major modules can be imported"""
    errors = []
    
    # Test core imports
    try:
        from app.config import llm_config
        print("[OK] app.config.llm_config")
    except Exception as e:
        errors.append(f"[FAIL] app.config.llm_config: {e}")
    
    try:
        from app.memory import memory_store
        print("[OK] app.memory.memory_store")
    except Exception as e:
        errors.append(f"[FAIL] app.memory.memory_store: {e}")
    
    try:
        from app.scheduler import job_scheduler
        print("[OK] app.scheduler.job_scheduler")
    except Exception as e:
        errors.append(f"[FAIL] app.scheduler.job_scheduler: {e}")
    
    try:
        from app.planning import plan_store
        print("[OK] app.planning.plan_store")
    except Exception as e:
        errors.append(f"[FAIL] app.planning.plan_store: {e}")
    
    try:
        from app.calendar import calendar_manager
        print("[OK] app.calendar.calendar_manager")
    except Exception as e:
        errors.append(f"[FAIL] app.calendar.calendar_manager: {e}")
    
    try:
        from app.observability import metrics_collector
        print("[OK] app.observability.metrics_collector")
    except Exception as e:
        errors.append(f"[FAIL] app.observability.metrics_collector: {e}")
    
    try:
        from app.analytics import email_analyzer
        print("[OK] app.analytics.email_analyzer")
    except Exception as e:
        errors.append(f"[FAIL] app.analytics.email_analyzer: {e}")
    
    try:
        from app.evaluation import evaluation_store
        print("[OK] app.evaluation.evaluation_store")
    except Exception as e:
        errors.append(f"[FAIL] app.evaluation.evaluation_store: {e}")
    
    if errors:
        print("\n[ERROR] Import Errors Found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n[SUCCESS] All imports successful!")
        return True

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)

# Made with Bob
