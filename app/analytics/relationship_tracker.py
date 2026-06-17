"""
Relationship Tracker - Track and analyze communication relationships
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from .analytics_store import AnalyticsStore


class RelationshipTracker:
    """Tracks and analyzes communication relationships."""
    
    def __init__(self, store: AnalyticsStore):
        """
        Initialize the relationship tracker.
        
        Args:
            store: AnalyticsStore instance
        """
        self.store = store
    
    def track_email(
        self,
        user_id: str,
        sender: str,
        recipient: str,
        is_sent: bool,
        timestamp: Optional[datetime] = None
    ):
        """
        Track an email for relationship analysis.
        
        Args:
            user_id: User identifier
            sender: Email sender
            recipient: Email recipient
            is_sent: True if user sent the email
            timestamp: Email timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Determine the contact (the other party)
        contact = recipient if is_sent else sender
        
        # Update relationship
        self.store.update_relationship(
            user_id=user_id,
            contact_email=contact,
            emails_sent=1 if is_sent else 0,
            emails_received=0 if is_sent else 1
        )
    
    def track_response(
        self,
        user_id: str,
        contact: str,
        response_time_hours: float
    ):
        """
        Track email response time.
        
        Args:
            user_id: User identifier
            contact: Contact email
            response_time_hours: Response time in hours
        """
        self.store.update_relationship(
            user_id=user_id,
            contact_email=contact,
            response_time_hours=response_time_hours
        )
    
    def get_relationship_insights(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get relationship insights for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with relationship insights
        """
        top_contacts = self.store.get_top_contacts(user_id, limit=20)
        
        if not top_contacts:
            return {
                'top_contacts': [],
                'total_contacts': 0,
                'avg_response_time': None,
                'most_frequent': None,
                'strongest_relationship': None
            }
        
        # Calculate statistics
        total_contacts = len(top_contacts)
        
        # Average response time (excluding None values)
        response_times = [
            c['avg_response_time_hours'] 
            for c in top_contacts 
            if c['avg_response_time_hours'] is not None
        ]
        avg_response_time = (
            sum(response_times) / len(response_times) 
            if response_times else None
        )
        
        # Most frequent contact
        most_frequent = max(
            top_contacts,
            key=lambda c: c['total_emails_sent'] + c['total_emails_received']
        )
        
        # Strongest relationship
        strongest = max(
            top_contacts,
            key=lambda c: c['relationship_strength']
        )
        
        return {
            'top_contacts': top_contacts[:10],
            'total_contacts': total_contacts,
            'avg_response_time': avg_response_time,
            'most_frequent': {
                'email': most_frequent['contact_email'],
                'total_emails': (
                    most_frequent['total_emails_sent'] + 
                    most_frequent['total_emails_received']
                )
            },
            'strongest_relationship': {
                'email': strongest['contact_email'],
                'strength': strongest['relationship_strength']
            }
        }
    
    def identify_vip_contacts(
        self,
        user_id: str,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Identify VIP contacts based on relationship strength.
        
        Args:
            user_id: User identifier
            threshold: Minimum relationship strength
            
        Returns:
            List of VIP contacts
        """
        all_contacts = self.store.get_top_contacts(user_id, limit=100)
        
        vips = [
            c for c in all_contacts 
            if c['relationship_strength'] >= threshold
        ]
        
        return vips
    
    def get_communication_patterns(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Analyze communication patterns.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with communication patterns
        """
        contacts = self.store.get_top_contacts(user_id, limit=100)
        
        if not contacts:
            return {
                'frequency_distribution': {},
                'response_time_stats': {},
                'total_interactions': 0
            }
        
        # Frequency distribution
        frequency_dist = defaultdict(int)
        for contact in contacts:
            freq = contact['communication_frequency']
            frequency_dist[freq] += 1
        
        # Response time statistics
        response_times = [
            c['avg_response_time_hours'] 
            for c in contacts 
            if c['avg_response_time_hours'] is not None
        ]
        
        if response_times:
            response_stats = {
                'min': min(response_times),
                'max': max(response_times),
                'avg': sum(response_times) / len(response_times),
                'median': sorted(response_times)[len(response_times) // 2]
            }
        else:
            response_stats = {}
        
        # Total interactions
        total_interactions = sum(
            c['total_emails_sent'] + c['total_emails_received']
            for c in contacts
        )
        
        return {
            'frequency_distribution': dict(frequency_dist),
            'response_time_stats': response_stats,
            'total_interactions': total_interactions,
            'active_contacts': len(contacts)
        }
    
    def detect_relationship_changes(
        self,
        user_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect significant changes in relationships.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            List of relationship changes
        """
        contacts = self.store.get_top_contacts(user_id, limit=50)
        changes = []
        
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_timestamp = cutoff.timestamp()
        
        for contact in contacts:
            last_interaction = contact['last_interaction']
            
            # Check for dormant relationships
            if last_interaction and last_interaction < cutoff_timestamp:
                days_since = (datetime.now().timestamp() - last_interaction) / 86400
                changes.append({
                    'type': 'dormant',
                    'contact': contact['contact_email'],
                    'days_since_last_contact': int(days_since),
                    'previous_strength': contact['relationship_strength']
                })
        
        return changes
    
    def suggest_follow_ups(
        self,
        user_id: str,
        days_threshold: int = 14
    ) -> List[Dict[str, Any]]:
        """
        Suggest contacts to follow up with.
        
        Args:
            user_id: User identifier
            days_threshold: Days since last contact to trigger suggestion
            
        Returns:
            List of follow-up suggestions
        """
        vips = self.identify_vip_contacts(user_id, threshold=0.6)
        suggestions = []
        
        cutoff = datetime.now() - timedelta(days=days_threshold)
        cutoff_timestamp = cutoff.timestamp()
        
        for contact in vips:
            last_interaction = contact['last_interaction']
            
            if last_interaction and last_interaction < cutoff_timestamp:
                days_since = (datetime.now().timestamp() - last_interaction) / 86400
                
                suggestions.append({
                    'contact': contact['contact_email'],
                    'days_since_last_contact': int(days_since),
                    'relationship_strength': contact['relationship_strength'],
                    'total_interactions': (
                        contact['total_emails_sent'] + 
                        contact['total_emails_received']
                    ),
                    'reason': f"No contact in {int(days_since)} days with important contact"
                })
        
        # Sort by relationship strength
        suggestions.sort(key=lambda x: x['relationship_strength'], reverse=True)
        
        return suggestions[:10]
    
    def get_network_statistics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get overall network statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with network statistics
        """
        contacts = self.store.get_top_contacts(user_id, limit=1000)
        
        if not contacts:
            return {
                'total_contacts': 0,
                'active_contacts': 0,
                'vip_contacts': 0,
                'avg_relationship_strength': 0.0,
                'network_health': 'unknown'
            }
        
        # Count active contacts (contacted in last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        cutoff_timestamp = cutoff.timestamp()
        
        active_contacts = sum(
            1 for c in contacts 
            if c['last_interaction'] and c['last_interaction'] >= cutoff_timestamp
        )
        
        # Count VIP contacts
        vip_contacts = sum(
            1 for c in contacts 
            if c['relationship_strength'] >= 0.7
        )
        
        # Average relationship strength
        avg_strength = sum(
            c['relationship_strength'] for c in contacts
        ) / len(contacts)
        
        # Network health assessment
        if avg_strength >= 0.6 and active_contacts >= len(contacts) * 0.3:
            health = 'excellent'
        elif avg_strength >= 0.4 and active_contacts >= len(contacts) * 0.2:
            health = 'good'
        elif avg_strength >= 0.3:
            health = 'fair'
        else:
            health = 'needs_attention'
        
        return {
            'total_contacts': len(contacts),
            'active_contacts': active_contacts,
            'vip_contacts': vip_contacts,
            'avg_relationship_strength': round(avg_strength, 3),
            'network_health': health,
            'activity_rate': round(active_contacts / len(contacts), 3) if contacts else 0.0
        }

# Made with Bob
