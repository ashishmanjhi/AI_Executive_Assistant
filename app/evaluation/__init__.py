"""
Agent Evaluation Framework

This module provides comprehensive evaluation and testing capabilities for the AI Executive Assistant:
- Test case management
- Test execution and reporting
- Performance metrics
- LLM evaluation
- User feedback collection
"""

from .evaluation_store import EvaluationStore
from .test_runner import TestRunner
from .metrics_calculator import MetricsCalculator
from .llm_evaluator import LLMEvaluator

__all__ = [
    'EvaluationStore',
    'TestRunner',
    'MetricsCalculator',
    'LLMEvaluator'
]

# Made with Bob
