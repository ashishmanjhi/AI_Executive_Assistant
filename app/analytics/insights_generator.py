"""
Insights Generator - Generate actionable insights from email analytics
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

from .analytics_store import AnalyticsStore
from .relationship_tracker import RelationshipTracker


class InsightsGenerator:
    """Generates actionable insights from email analytics data."""
    
    def __init__(self, store: AnalyticsStore):
        """
        Initialize the insights generator.
        
        Args:
            store: AnalyticsStore instance
        """
        self.store = store
        self.tracker = RelationshipTracker(store)
    
    def generate_daily_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate daily insights for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # High priority emails
        high_priority = self.store.get_high_priority_emails(
            user_id, threshold=0.7, limit=5
        )
        
        if high_priority:
            insights.append({
                'type': 'high_priority',
                'title': f'{len(high_priority)} High Priority Emails',
                'description': f'You have {len(high_priority)} emails requiring immediate attention.',
                'data': {'emails': high_priority},
                'importance': 0.9
            })
        
        # Sentiment analysis
        sentiment_dist = self.store.get_sentiment_distribution(user_id, days=1)
        negative_count = sentiment_dist.get('negative', 0)
        
        if negative_count > 0:
            insights.append({
                'type': 'sentiment_alert',
                'title': f'{negative_count} Negative Sentiment Emails',
                'description': f'You received {negative_count} emails with negative sentiment today.',
                'data': {'distribution': sentiment_dist},
                'importance': 0.7
            })
        
        # Follow-up suggestions
        follow_ups = self.tracker.suggest_follow_ups(user_id, days_threshold=7)
        
        if follow_ups:
            insights.append({
                'type': 'follow_up',
                'title': f'{len(follow_ups)} Contacts Need Follow-up',
                'description': 'Important contacts you haven\'t communicated with recently.',
                'data': {'contacts': follow_ups[:5]},
                'importance': 0.6
            })
        
        return insights
    
    def generate_weekly_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate weekly insights for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Communication patterns
        patterns = self.tracker.get_communication_patterns(user_id)
        
        if patterns['total_interactions'] > 0:
            insights.append({
                'type': 'communication_summary',
                'title': 'Weekly Communication Summary',
                'description': f'You had {patterns["total_interactions"]} email interactions this week.',
                'data': patterns,
                'importance': 0.5
            })
        
        # Sentiment trends
        sentiment_dist = self.store.get_sentiment_distribution(user_id, days=7)
        total_emails = sum(sentiment_dist.values())
        
        if total_emails > 0:
            positive_pct = (sentiment_dist.get('positive', 0) / total_emails) * 100
            negative_pct = (sentiment_dist.get('negative', 0) / total_emails) * 100
            
            insights.append({
                'type': 'sentiment_trend',
                'title': 'Weekly Sentiment Analysis',
                'description': f'{positive_pct:.1f}% positive, {negative_pct:.1f}% negative emails.',
                'data': {
                    'distribution': sentiment_dist,
                    'total': total_emails,
                    'percentages': {
                        'positive': positive_pct,
                        'neutral': (sentiment_dist.get('neutral', 0) / total_emails) * 100,
                        'negative': negative_pct
                    }
                },
                'importance': 0.6
            })
        
        # Relationship insights
        relationship_insights = self.tracker.get_relationship_insights(user_id)
        
        if relationship_insights['total_contacts'] > 0:
            insights.append({
                'type': 'relationship_summary',
                'title': 'Relationship Network Summary',
                'description': f'You have {relationship_insights["total_contacts"]} active contacts.',
                'data': relationship_insights,
                'importance': 0.5
            })
        
        # Network health
        network_stats = self.tracker.get_network_statistics(user_id)
        
        if network_stats['network_health'] == 'needs_attention':
            insights.append({
                'type': 'network_health',
                'title': 'Network Health Needs Attention',
                'description': 'Your communication network could benefit from more engagement.',
                'data': network_stats,
                'importance': 0.7
            })
        
        return insights
    
    def generate_monthly_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate monthly insights for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Top contacts
        top_contacts = self.store.get_top_contacts(user_id, limit=10)
        
        if top_contacts:
            insights.append({
                'type': 'top_contacts',
                'title': 'Top 10 Contacts This Month',
                'description': 'Your most frequent communication partners.',
                'data': {'contacts': top_contacts},
                'importance': 0.6
            })
        
        # VIP contacts
        vips = self.tracker.identify_vip_contacts(user_id, threshold=0.7)
        
        if vips:
            insights.append({
                'type': 'vip_contacts',
                'title': f'{len(vips)} VIP Contacts',
                'description': 'Contacts with strong relationships requiring attention.',
                'data': {'vips': vips},
                'importance': 0.8
            })
        
        # Relationship changes
        changes = self.tracker.detect_relationship_changes(user_id, days=30)
        dormant = [c for c in changes if c['type'] == 'dormant']
        
        if dormant:
            insights.append({
                'type': 'dormant_relationships',
                'title': f'{len(dormant)} Dormant Relationships',
                'description': 'Important contacts you haven\'t communicated with recently.',
                'data': {'dormant': dormant[:10]},
                'importance': 0.7
            })
        
        # Overall sentiment
        sentiment_dist = self.store.get_sentiment_distribution(user_id, days=30)
        total_emails = sum(sentiment_dist.values())
        
        if total_emails > 0:
            positive_pct = (sentiment_dist.get('positive', 0) / total_emails) * 100
            
            if positive_pct >= 70:
                sentiment_message = 'Excellent! Most of your emails have positive sentiment.'
            elif positive_pct >= 50:
                sentiment_message = 'Good balance of positive communications.'
            else:
                sentiment_message = 'Consider focusing on more positive interactions.'
            
            insights.append({
                'type': 'monthly_sentiment',
                'title': 'Monthly Sentiment Overview',
                'description': sentiment_message,
                'data': {
                    'distribution': sentiment_dist,
                    'total': total_emails,
                    'positive_percentage': positive_pct
                },
                'importance': 0.5
            })
        
        return insights
    
    def detect_anomalies(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Detect anomalies in email patterns.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of anomaly insights
        """
        anomalies = []
        
        # Unusual sentiment spike
        sentiment_dist = self.store.get_sentiment_distribution(user_id, days=1)
        total_today = sum(sentiment_dist.values())
        
        if total_today > 0:
            negative_pct = (sentiment_dist.get('negative', 0) / total_today) * 100
            
            if negative_pct > 50:
                anomalies.append({
                    'type': 'sentiment_spike',
                    'title': 'Unusual Negative Sentiment',
                    'description': f'{negative_pct:.1f}% of today\'s emails have negative sentiment.',
                    'data': {'distribution': sentiment_dist},
                    'importance': 0.8
                })
        
        # Unusual priority spike
        high_priority = self.store.get_high_priority_emails(
            user_id, threshold=0.8, limit=100
        )
        
        if len(high_priority) > 10:
            anomalies.append({
                'type': 'priority_spike',
                'title': 'High Volume of Urgent Emails',
                'description': f'{len(high_priority)} urgent emails detected.',
                'data': {'count': len(high_priority)},
                'importance': 0.9
            })
        
        return anomalies
    
    def generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recommendation insights
        """
        recommendations = []
        
        # Response time recommendations
        patterns = self.tracker.get_communication_patterns(user_id)
        response_stats = patterns.get('response_time_stats', {})
        
        if response_stats and response_stats.get('avg', 0) > 24:
            recommendations.append({
                'type': 'response_time',
                'title': 'Improve Response Time',
                'description': f'Your average response time is {response_stats["avg"]:.1f} hours. Consider responding faster.',
                'data': response_stats,
                'importance': 0.6
            })
        
        # Network expansion
        network_stats = self.tracker.get_network_statistics(user_id)
        
        if network_stats['activity_rate'] < 0.3:
            recommendations.append({
                'type': 'network_engagement',
                'title': 'Increase Network Engagement',
                'description': 'Only 30% of your contacts are active. Consider reaching out more.',
                'data': network_stats,
                'importance': 0.5
            })
        
        # Follow-up reminders
        follow_ups = self.tracker.suggest_follow_ups(user_id, days_threshold=14)
        
        if follow_ups:
            recommendations.append({
                'type': 'follow_up_reminder',
                'title': 'Follow-up Recommendations',
                'description': f'{len(follow_ups)} important contacts need follow-up.',
                'data': {'contacts': follow_ups[:5]},
                'importance': 0.7
            })
        
        return recommendations
    
    def store_insights(
        self,
        user_id: str,
        insights: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Store insights in the database.
        
        Args:
            user_id: User identifier
            insights: List of insights to store
            
        Returns:
            List of insight IDs
        """
        insight_ids = []
        
        for insight in insights:
            insight_id = self.store.store_insight(
                user_id=user_id,
                insight_type=insight['type'],
                title=insight['title'],
                description=insight['description'],
                data=insight.get('data'),
                importance_score=insight.get('importance', 0.5)
            )
            insight_ids.append(insight_id)
        
        return insight_ids
    
    def generate_and_store_insights(
        self,
        user_id: str,
        period: str = 'daily'
    ) -> List[int]:
        """
        Generate and store insights for a user.
        
        Args:
            user_id: User identifier
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            List of stored insight IDs
        """
        if period == 'daily':
            insights = self.generate_daily_insights(user_id)
        elif period == 'weekly':
            insights = self.generate_weekly_insights(user_id)
        elif period == 'monthly':
            insights = self.generate_monthly_insights(user_id)
        else:
            insights = []
        
        # Add anomalies and recommendations
        insights.extend(self.detect_anomalies(user_id))
        insights.extend(self.generate_recommendations(user_id))
        
        return self.store_insights(user_id, insights)

# Made with Bob
