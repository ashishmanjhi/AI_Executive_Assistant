"""
Email Analytics and Intelligence Module

This module provides advanced email analysis capabilities including:
- Sentiment analysis
- Priority scoring
- Relationship tracking
- Topic extraction
- Insights generation
"""

from .analytics_store import AnalyticsStore
from .email_analyzer import EmailAnalyzer
from .relationship_tracker import RelationshipTracker
from .insights_generator import InsightsGenerator

__all__ = [
    'AnalyticsStore',
    'EmailAnalyzer',
    'RelationshipTracker',
    'InsightsGenerator'
]

# Made with Bob
