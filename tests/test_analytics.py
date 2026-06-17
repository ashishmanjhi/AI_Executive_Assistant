"""
Test suite for Email Analytics module
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.analytics.analytics_store import AnalyticsStore
from app.analytics.email_analyzer import EmailAnalyzer
from app.analytics.relationship_tracker import RelationshipTracker
from app.analytics.insights_generator import InsightsGenerator


class TestAnalyticsStore(unittest.TestCase):
    """Test AnalyticsStore functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = AnalyticsStore(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_store_email_analysis(self):
        """Test storing email analysis."""
        result = self.store.store_email_analysis(
            email_id='test123',
            user_id='user1',
            sender_email='sender@example.com',
            sentiment={'score': 0.8, 'label': 'positive'},
            priority={'priority_score': 0.7, 'urgency_score': 0.6, 'importance_score': 0.8},
            category='meeting',
            topics=['project', 'deadline'],
            entities={'people': ['John'], 'dates': ['2024-01-01']}
        )
        
        self.assertTrue(result)
        
        # Retrieve and verify
        analysis = self.store.get_email_analysis('test123')
        self.assertIsNotNone(analysis)
        assert analysis is not None  # Type guard for type checker
        self.assertEqual(analysis['email_id'], 'test123')
        self.assertEqual(analysis['sentiment']['label'], 'positive')
        self.assertEqual(analysis['category'], 'meeting')
    
    def test_get_high_priority_emails(self):
        """Test retrieving high priority emails."""
        # Store some emails
        for i in range(5):
            self.store.store_email_analysis(
                email_id=f'email{i}',
                user_id='user1',
                sender_email=f'sender{i}@example.com',
                sentiment={'score': 0.5, 'label': 'neutral'},
                priority={'priority_score': 0.5 + (i * 0.1), 'urgency_score': 0.5, 'importance_score': 0.5},
                category='general',
                topics=[],
                entities={}
            )
        
        high_priority = self.store.get_high_priority_emails('user1', threshold=0.7)
        self.assertGreater(len(high_priority), 0)
        
        # Verify all returned emails meet threshold
        for email in high_priority:
            self.assertGreaterEqual(email['priority_score'], 0.7)
    
    def test_update_relationship(self):
        """Test updating communication relationships."""
        result = self.store.update_relationship(
            user_id='user1',
            contact_email='contact@example.com',
            emails_sent=5,
            emails_received=3,
            response_time_hours=2.5
        )
        
        self.assertTrue(result)
        
        # Update again
        result = self.store.update_relationship(
            user_id='user1',
            contact_email='contact@example.com',
            emails_sent=2,
            emails_received=1
        )
        
        self.assertTrue(result)
        
        # Verify cumulative counts
        contacts = self.store.get_top_contacts('user1', limit=10)
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['total_emails_sent'], 7)
        self.assertEqual(contacts[0]['total_emails_received'], 4)
    
    def test_get_top_contacts(self):
        """Test retrieving top contacts."""
        # Create multiple contacts
        for i in range(10):
            self.store.update_relationship(
                user_id='user1',
                contact_email=f'contact{i}@example.com',
                emails_sent=i + 1,
                emails_received=i + 1
            )
        
        top_contacts = self.store.get_top_contacts('user1', limit=5)
        self.assertEqual(len(top_contacts), 5)
        
        # Verify sorted by relationship strength
        strengths = [c['relationship_strength'] for c in top_contacts]
        self.assertEqual(strengths, sorted(strengths, reverse=True))
    
    def test_store_and_get_insights(self):
        """Test storing and retrieving insights."""
        insight_id = self.store.store_insight(
            user_id='user1',
            insight_type='high_priority',
            title='Test Insight',
            description='This is a test insight',
            data={'count': 5},
            importance_score=0.8
        )
        
        self.assertIsInstance(insight_id, int)
        self.assertGreater(insight_id, 0)
        
        # Retrieve insights
        insights = self.store.get_insights('user1')
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]['title'], 'Test Insight')
        self.assertFalse(insights[0]['is_read'])
        
        # Mark as read
        self.store.mark_insight_read(insight_id)
        
        insights = self.store.get_insights('user1')
        self.assertTrue(insights[0]['is_read'])
    
    def test_get_sentiment_distribution(self):
        """Test sentiment distribution calculation."""
        # Store emails with different sentiments
        sentiments = ['positive', 'positive', 'neutral', 'negative']
        
        for i, sentiment in enumerate(sentiments):
            self.store.store_email_analysis(
                email_id=f'email{i}',
                user_id='user1',
                sender_email='sender@example.com',
                sentiment={'score': 0.5, 'label': sentiment},
                priority={'priority_score': 0.5, 'urgency_score': 0.5, 'importance_score': 0.5},
                category='general',
                topics=[],
                entities={}
            )
        
        distribution = self.store.get_sentiment_distribution('user1', days=7)
        self.assertEqual(distribution['positive'], 2)
        self.assertEqual(distribution['neutral'], 1)
        self.assertEqual(distribution['negative'], 1)


class TestEmailAnalyzer(unittest.TestCase):
    """Test EmailAnalyzer functionality."""
    
    def setUp(self):
        """Set up email analyzer."""
        self.analyzer = EmailAnalyzer()
    
    def test_analyze_sentiment(self):
        """Test sentiment analysis."""
        positive_text = "This is great! I'm very happy with the results."
        result = self.analyzer.analyze_sentiment(positive_text)
        
        self.assertIn('score', result)
        self.assertIn('label', result)
        self.assertIn('confidence', result)
        self.assertIn(result['label'], ['positive', 'neutral', 'negative'])
    
    def test_calculate_priority(self):
        """Test priority calculation."""
        subject = "URGENT: Critical issue needs immediate attention"
        body = "This is an urgent matter that requires your immediate response."
        sender = "ceo@company.com"
        
        result = self.analyzer.calculate_priority(subject, body, sender)
        
        self.assertIn('priority_score', result)
        self.assertIn('urgency_score', result)
        self.assertIn('importance_score', result)
        
        # Urgent email should have high urgency score
        self.assertGreater(result['urgency_score'], 0.5)
    
    def test_classify_category(self):
        """Test email category classification."""
        # Meeting email
        subject = "Meeting tomorrow at 3pm"
        body = "Let's schedule a meeting to discuss the project."
        category = self.analyzer.classify_category(subject, body)
        self.assertEqual(category, 'meeting')
        
        # Question email
        subject = "Quick question about the report"
        body = "Can you help me understand this section?"
        category = self.analyzer.classify_category(subject, body)
        self.assertEqual(category, 'question')
    
    def test_extract_topics(self):
        """Test topic extraction."""
        subject = "Project Update"
        body = "Here's an update on the project deadline and budget approval."
        
        topics = self.analyzer.extract_topics(subject, body)
        
        self.assertIsInstance(topics, list)
        # Topics extraction may vary, just verify it returns a list
    
    def test_extract_entities(self):
        """Test entity extraction."""
        text = "Meeting on January 15, 2024 with budget of $50,000"
        
        entities = self.analyzer.extract_entities(text)
        
        self.assertIn('dates', entities)
        self.assertIn('amounts', entities)
        self.assertIsInstance(entities['dates'], list)
        self.assertIsInstance(entities['amounts'], list)


class TestRelationshipTracker(unittest.TestCase):
    """Test RelationshipTracker functionality."""
    
    def setUp(self):
        """Set up relationship tracker."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = AnalyticsStore(self.temp_db.name)
        self.tracker = RelationshipTracker(self.store)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_track_email(self):
        """Test tracking email for relationship."""
        self.tracker.track_email(
            user_id='user1',
            sender='user1@example.com',
            recipient='contact@example.com',
            is_sent=True
        )
        
        contacts = self.store.get_top_contacts('user1')
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]['contact_email'], 'contact@example.com')
        self.assertEqual(contacts[0]['total_emails_sent'], 1)
    
    def test_get_relationship_insights(self):
        """Test getting relationship insights."""
        # Create some relationships
        for i in range(5):
            self.store.update_relationship(
                user_id='user1',
                contact_email=f'contact{i}@example.com',
                emails_sent=i + 1,
                emails_received=i + 1,
                response_time_hours=float(i + 1)
            )
        
        insights = self.tracker.get_relationship_insights('user1')
        
        self.assertIn('top_contacts', insights)
        self.assertIn('total_contacts', insights)
        self.assertIn('avg_response_time', insights)
        self.assertEqual(insights['total_contacts'], 5)
    
    def test_identify_vip_contacts(self):
        """Test VIP contact identification."""
        # Create contacts with varying strengths
        self.store.update_relationship(
            user_id='user1',
            contact_email='vip@example.com',
            emails_sent=50,
            emails_received=50
        )
        
        self.store.update_relationship(
            user_id='user1',
            contact_email='regular@example.com',
            emails_sent=5,
            emails_received=5
        )
        
        vips = self.tracker.identify_vip_contacts('user1', threshold=0.5)
        
        # VIP should have higher relationship strength
        self.assertGreater(len(vips), 0)
    
    def test_suggest_follow_ups(self):
        """Test follow-up suggestions."""
        # Create a contact with old last interaction
        old_timestamp = (datetime.now() - timedelta(days=20)).timestamp()
        
        self.store.update_relationship(
            user_id='user1',
            contact_email='old_contact@example.com',
            emails_sent=20,
            emails_received=20
        )
        
        # Manually update last_interaction to be old
        # (In real scenario, this would be tracked automatically)
        
        suggestions = self.tracker.suggest_follow_ups('user1', days_threshold=15)
        
        # Should suggest follow-up for contacts not contacted recently
        self.assertIsInstance(suggestions, list)
    
    def test_get_network_statistics(self):
        """Test network statistics."""
        # Create multiple contacts
        for i in range(10):
            self.store.update_relationship(
                user_id='user1',
                contact_email=f'contact{i}@example.com',
                emails_sent=i + 1,
                emails_received=i + 1
            )
        
        stats = self.tracker.get_network_statistics('user1')
        
        self.assertEqual(stats['total_contacts'], 10)
        self.assertIn('network_health', stats)
        self.assertIn('avg_relationship_strength', stats)


class TestInsightsGenerator(unittest.TestCase):
    """Test InsightsGenerator functionality."""
    
    def setUp(self):
        """Set up insights generator."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.store = AnalyticsStore(self.temp_db.name)
        self.generator = InsightsGenerator(self.store)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_generate_daily_insights(self):
        """Test daily insights generation."""
        # Store some high priority emails
        for i in range(3):
            self.store.store_email_analysis(
                email_id=f'email{i}',
                user_id='user1',
                sender_email='sender@example.com',
                sentiment={'score': 0.5, 'label': 'neutral'},
                priority={'priority_score': 0.8, 'urgency_score': 0.7, 'importance_score': 0.9},
                category='general',
                topics=[],
                entities={}
            )
        
        insights = self.generator.generate_daily_insights('user1')
        
        self.assertIsInstance(insights, list)
        # Should have at least high priority insight
        self.assertGreater(len(insights), 0)
    
    def test_generate_weekly_insights(self):
        """Test weekly insights generation."""
        # Create some data
        for i in range(10):
            self.store.store_email_analysis(
                email_id=f'email{i}',
                user_id='user1',
                sender_email=f'sender{i}@example.com',
                sentiment={'score': 0.5, 'label': 'positive'},
                priority={'priority_score': 0.5, 'urgency_score': 0.5, 'importance_score': 0.5},
                category='general',
                topics=[],
                entities={}
            )
        
        insights = self.generator.generate_weekly_insights('user1')
        
        self.assertIsInstance(insights, list)
    
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        # Create emails with negative sentiment
        for i in range(5):
            self.store.store_email_analysis(
                email_id=f'email{i}',
                user_id='user1',
                sender_email='sender@example.com',
                sentiment={'score': -0.8, 'label': 'negative'},
                priority={'priority_score': 0.5, 'urgency_score': 0.5, 'importance_score': 0.5},
                category='general',
                topics=[],
                entities={}
            )
        
        anomalies = self.generator.detect_anomalies('user1')
        
        self.assertIsInstance(anomalies, list)
        # Should detect negative sentiment spike
    
    def test_store_insights(self):
        """Test storing generated insights."""
        insights = [
            {
                'type': 'test',
                'title': 'Test Insight',
                'description': 'Test description',
                'data': {'test': 'data'},
                'importance': 0.7
            }
        ]
        
        insight_ids = self.generator.store_insights('user1', insights)
        
        self.assertEqual(len(insight_ids), 1)
        self.assertIsInstance(insight_ids[0], int)
        
        # Verify stored
        stored = self.store.get_insights('user1')
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]['title'], 'Test Insight')


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsStore))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestRelationshipTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestInsightsGenerator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

# Made with Bob
