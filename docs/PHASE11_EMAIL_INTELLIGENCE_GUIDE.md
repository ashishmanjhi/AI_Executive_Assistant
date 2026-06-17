# Phase 11: Email Intelligence & Analytics - Complete Guide

## Overview

Phase 11 implements a comprehensive email intelligence and analytics system for the AI Executive Assistant. This system provides deep insights into email communications through sentiment analysis, priority scoring, relationship tracking, and actionable insights generation.

## Architecture

```
app/analytics/
├── __init__.py                # Package initialization
├── analytics_store.py         # Database operations (698 lines)
├── email_analyzer.py          # Email analysis with LLM (418 lines)
├── relationship_tracker.py    # Communication relationship tracking (330 lines)
└── insights_generator.py      # Actionable insights generation (357 lines)

tests/
└── test_analytics.py          # Comprehensive test suite (527 lines)
```

## Components

### 1. Analytics Store (`analytics_store.py`)

The Analytics Store manages all database operations for email analytics data.

#### Database Schema

**Email Analytics Table**

```sql
CREATE TABLE email_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    sentiment_score REAL,
    sentiment_label TEXT,
    priority_score REAL,
    urgency_score REAL,
    importance_score REAL,
    category TEXT,
    topics TEXT,
    entities TEXT,
    analyzed_at REAL NOT NULL
)
```

**Communication Relationships Table**

```sql
CREATE TABLE communication_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    total_emails_sent INTEGER DEFAULT 0,
    total_emails_received INTEGER DEFAULT 0,
    avg_response_time_hours REAL,
    last_interaction REAL,
    relationship_strength REAL,
    communication_frequency TEXT,
    UNIQUE(user_id, contact_email)
)
```

**Analytics Insights Table**

```sql
CREATE TABLE analytics_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    data TEXT,
    importance_score REAL DEFAULT 0.5,
    is_read INTEGER DEFAULT 0,
    created_at REAL DEFAULT (julianday('now'))
)
```

#### Key Methods

```python
from app.analytics import AnalyticsStore

store = AnalyticsStore("data/analytics.db")

# Store email analysis
store.store_email_analysis(
    email_id="email123",
    user_id="user1",
    sender_email="sender@example.com",
    sentiment={'score': 0.8, 'label': 'positive'},
    priority={'priority_score': 0.7, 'urgency_score': 0.6, 'importance_score': 0.8},
    category='meeting',
    topics=['project', 'deadline'],
    entities={'people': ['John'], 'dates': ['2024-01-01']}
)

# Get high priority emails
high_priority = store.get_high_priority_emails(
    user_id="user1",
    threshold=0.7,
    limit=10
)

# Update relationship
store.update_relationship(
    user_id="user1",
    contact_email="contact@example.com",
    emails_sent=5,
    emails_received=3,
    response_time_hours=2.5
)

# Get top contacts
top_contacts = store.get_top_contacts("user1", limit=10)

# Store insight
insight_id = store.store_insight(
    user_id="user1",
    insight_type="high_priority",
    title="5 High Priority Emails",
    description="You have 5 emails requiring immediate attention.",
    data={'count': 5},
    importance_score=0.9
)

# Get insights
insights = store.get_insights("user1", unread_only=True)
```

### 2. Email Analyzer (`email_analyzer.py`)

The Email Analyzer performs comprehensive email analysis using LLM.

#### Features

**Sentiment Analysis**

```python
from app.analytics import EmailAnalyzer

analyzer = EmailAnalyzer()

# Analyze sentiment
sentiment = analyzer.analyze_sentiment(
    "This is great! I'm very happy with the results."
)
# Returns: {'score': 0.8, 'label': 'positive', 'confidence': 0.9}
```

**Priority Scoring**

```python
# Calculate priority
priority = analyzer.calculate_priority(
    subject="URGENT: Critical issue",
    body="This requires immediate attention.",
    sender="ceo@company.com"
)
# Returns: {
#     'priority_score': 0.85,
#     'urgency_score': 0.9,
#     'importance_score': 0.8
# }
```

**Category Classification**

```python
# Classify email
category = analyzer.classify_category(
    subject="Meeting tomorrow at 3pm",
    body="Let's schedule a meeting to discuss the project."
)
# Returns: 'meeting'
```

**Topic Extraction**

```python
# Extract topics
topics = analyzer.extract_topics(
    subject="Project Update",
    body="Here's an update on the project deadline and budget approval."
)
# Returns: ['project deadline', 'budget approval']
```

**Entity Extraction**

```python
# Extract entities
entities = analyzer.extract_entities(
    "Meeting on January 15, 2024 with budget of $50,000"
)
# Returns: {
#     'people': [],
#     'organizations': [],
#     'dates': ['January 15, 2024'],
#     'amounts': ['$50,000']
# }
```

**Complete Analysis**

```python
# Analyze entire email
result = analyzer.analyze_email(
    email_id="email123",
    user_id="user1",
    sender="sender@example.com",
    subject="Project Update",
    body="Here's the latest update on our project..."
)
# Returns complete analysis with sentiment, priority, category, topics, entities
```

### 3. Relationship Tracker (`relationship_tracker.py`)

The Relationship Tracker analyzes communication patterns and relationships.

#### Features

**Track Emails**

```python
from app.analytics import RelationshipTracker, AnalyticsStore

store = AnalyticsStore()
tracker = RelationshipTracker(store)

# Track sent email
tracker.track_email(
    user_id="user1",
    sender="user1@example.com",
    recipient="contact@example.com",
    is_sent=True
)

# Track received email
tracker.track_email(
    user_id="user1",
    sender="contact@example.com",
    recipient="user1@example.com",
    is_sent=False
)
```

**Relationship Insights**

```python
# Get relationship insights
insights = tracker.get_relationship_insights("user1")
# Returns: {
#     'top_contacts': [...],
#     'total_contacts': 50,
#     'avg_response_time': 3.5,
#     'most_frequent': {'email': 'contact@example.com', 'total_emails': 100},
#     'strongest_relationship': {'email': 'vip@example.com', 'strength': 0.95}
# }
```

**VIP Contacts**

```python
# Identify VIP contacts
vips = tracker.identify_vip_contacts(
    user_id="user1",
    threshold=0.7
)
# Returns list of contacts with relationship strength >= 0.7
```

**Communication Patterns**

```python
# Analyze communication patterns
patterns = tracker.get_communication_patterns("user1")
# Returns: {
#     'frequency_distribution': {'high': 10, 'medium': 20, 'low': 15},
#     'response_time_stats': {'min': 0.5, 'max': 48, 'avg': 5.2},
#     'total_interactions': 500
# }
```

**Follow-up Suggestions**

```python
# Get follow-up suggestions
suggestions = tracker.suggest_follow_ups(
    user_id="user1",
    days_threshold=14
)
# Returns list of contacts needing follow-up
```

**Network Statistics**

```python
# Get network statistics
stats = tracker.get_network_statistics("user1")
# Returns: {
#     'total_contacts': 100,
#     'active_contacts': 45,
#     'vip_contacts': 12,
#     'avg_relationship_strength': 0.65,
#     'network_health': 'good'
# }
```

### 4. Insights Generator (`insights_generator.py`)

The Insights Generator creates actionable insights from analytics data.

#### Features

**Daily Insights**

```python
from app.analytics import InsightsGenerator, AnalyticsStore

store = AnalyticsStore()
generator = InsightsGenerator(store)

# Generate daily insights
insights = generator.generate_daily_insights("user1")
# Returns list of insights:
# - High priority emails
# - Sentiment alerts
# - Follow-up suggestions
```

**Weekly Insights**

```python
# Generate weekly insights
insights = generator.generate_weekly_insights("user1")
# Returns:
# - Communication summary
# - Sentiment trends
# - Relationship summary
# - Network health
```

**Monthly Insights**

```python
# Generate monthly insights
insights = generator.generate_monthly_insights("user1")
# Returns:
# - Top contacts
# - VIP contacts
# - Dormant relationships
# - Overall sentiment
```

**Anomaly Detection**

```python
# Detect anomalies
anomalies = generator.detect_anomalies("user1")
# Returns:
# - Sentiment spikes
# - Priority spikes
# - Unusual patterns
```

**Recommendations**

```python
# Generate recommendations
recommendations = generator.generate_recommendations("user1")
# Returns:
# - Response time improvements
# - Network engagement suggestions
# - Follow-up reminders
```

**Store Insights**

```python
# Generate and store insights
insight_ids = generator.generate_and_store_insights(
    user_id="user1",
    period="daily"  # or 'weekly', 'monthly'
)
# Generates insights and stores them in database
```

## Integration Examples

### 1. Complete Email Analysis Pipeline

```python
from app.analytics import AnalyticsStore, EmailAnalyzer

store = AnalyticsStore()
analyzer = EmailAnalyzer()

def process_email(email):
    """Process and analyze an email."""

    # Analyze email
    analysis = analyzer.analyze_email(
        email_id=email['id'],
        user_id=email['user_id'],
        sender=email['from'],
        subject=email['subject'],
        body=email['body']
    )

    # Store analysis
    store.store_email_analysis(
        email_id=analysis['email_id'],
        user_id=analysis['user_id'],
        sender_email=analysis['sender'],
        sentiment=analysis['sentiment'],
        priority=analysis['priority'],
        category=analysis['category'],
        topics=analysis['topics'],
        entities=analysis['entities']
    )

    return analysis

# Process email
email = {
    'id': 'email123',
    'user_id': 'user1',
    'from': 'sender@example.com',
    'subject': 'Project Update',
    'body': 'Here is the latest update...'
}

analysis = process_email(email)
print(f"Priority: {analysis['priority']['priority_score']}")
print(f"Sentiment: {analysis['sentiment']['label']}")
print(f"Category: {analysis['category']}")
```

### 2. Relationship Tracking System

```python
from app.analytics import AnalyticsStore, RelationshipTracker

store = AnalyticsStore()
tracker = RelationshipTracker(store)

def track_email_interaction(email, is_sent):
    """Track email for relationship analysis."""

    tracker.track_email(
        user_id=email['user_id'],
        sender=email['from'],
        recipient=email['to'],
        is_sent=is_sent,
        timestamp=email['timestamp']
    )

    # Get updated insights
    insights = tracker.get_relationship_insights(email['user_id'])

    # Check for VIPs
    if insights['strongest_relationship']['strength'] > 0.8:
        print(f"VIP contact: {insights['strongest_relationship']['email']}")

    return insights

# Track sent email
email = {
    'user_id': 'user1',
    'from': 'user1@example.com',
    'to': 'contact@example.com',
    'timestamp': datetime.now()
}

insights = track_email_interaction(email, is_sent=True)
```

### 3. Daily Insights Dashboard

```python
from app.analytics import AnalyticsStore, InsightsGenerator

store = AnalyticsStore()
generator = InsightsGenerator(store)

def generate_daily_dashboard(user_id):
    """Generate daily insights dashboard."""

    # Generate insights
    insights = generator.generate_daily_insights(user_id)

    # Store insights
    insight_ids = generator.store_insights(user_id, insights)

    # Display insights
    print("=== Daily Insights Dashboard ===\n")

    for insight in insights:
        print(f"[{insight['type'].upper()}]")
        print(f"Title: {insight['title']}")
        print(f"Description: {insight['description']}")
        print(f"Importance: {insight['importance']:.1f}")
        print()

    return insights

# Generate dashboard
insights = generate_daily_dashboard("user1")
```

### 4. Automated Insights Job

```python
from app.analytics import AnalyticsStore, InsightsGenerator
from app.scheduler import JobScheduler

store = AnalyticsStore()
generator = InsightsGenerator(store)
scheduler = JobScheduler()

def daily_insights_job(user_id):
    """Daily insights generation job."""

    # Generate and store insights
    insight_ids = generator.generate_and_store_insights(
        user_id=user_id,
        period='daily'
    )

    print(f"Generated {len(insight_ids)} insights for {user_id}")

    return {'insight_count': len(insight_ids)}

# Schedule daily insights
scheduler.create_job(
    user_id='user1',
    job_type='daily_insights',
    job_name='Daily Email Insights',
    schedule_type='cron',
    schedule_value='0 8 * * *',  # 8 AM daily
    job_config={'user_id': 'user1'}
)
```

## Best Practices

### 1. Sentiment Analysis

- Use for understanding email tone
- Track sentiment trends over time
- Alert on negative sentiment spikes
- Consider context (formal vs informal)

### 2. Priority Scoring

- Combine urgency and importance
- Use sender reputation
- Check for time-sensitive keywords
- Adjust thresholds per user

### 3. Relationship Tracking

- Track all email interactions
- Update relationship strength regularly
- Monitor response times
- Identify dormant relationships

### 4. Insights Generation

- Generate insights at appropriate intervals
- Prioritize actionable insights
- Avoid insight fatigue
- Provide context and recommendations

## Performance Considerations

### Database Optimization

```python
# Use indexes for common queries
# Already created in analytics_store.py:
# - idx_email_analytics_user
# - idx_email_analytics_sender
# - idx_email_analytics_priority
# - idx_relationships_user
# - idx_relationships_strength
```

### Batch Processing

```python
# Analyze multiple emails in batch
emails = [...]  # List of emails
results = analyzer.batch_analyze(emails)

# Store in batch
for result in results:
    store.store_email_analysis(...)
```

### Caching

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_insights(user_id, period):
    return generator.generate_daily_insights(user_id)
```

## Testing

Run the comprehensive test suite:

```bash
python tests/test_analytics.py
```

Test coverage:

- ✅ Analytics Store: 7 tests
- ✅ Email Analyzer: 5 tests
- ✅ Relationship Tracker: 6 tests
- ✅ Insights Generator: 5 tests
- **Total: 23 tests**

## Troubleshooting

### Issue: Sentiment analysis returns neutral for all emails

**Solution**: Check LLM configuration and ensure model is responding correctly.

```python
# Test LLM directly
from app.config.llm_config import create_llm

llm = create_llm()
response = llm.invoke("Test message")
print(response.content)
```

### Issue: Relationship strength not updating

**Solution**: Ensure emails are being tracked properly.

```python
# Verify tracking
tracker.track_email(...)
contacts = store.get_top_contacts(user_id)
print(contacts)
```

### Issue: No insights generated

**Solution**: Check if there's enough data.

```python
# Check data availability
high_priority = store.get_high_priority_emails(user_id)
sentiment_dist = store.get_sentiment_distribution(user_id)
print(f"High priority: {len(high_priority)}")
print(f"Sentiment distribution: {sentiment_dist}")
```

## Future Enhancements

Potential improvements for future versions:

1. **Advanced ML Models**: Use specialized models for sentiment and classification
2. **Real-time Analysis**: Stream processing for immediate insights
3. **Predictive Analytics**: Predict email importance before reading
4. **Network Visualization**: Graph-based relationship visualization
5. **Custom Categories**: User-defined email categories
6. **Multi-language Support**: Analyze emails in multiple languages
7. **Integration with Calendar**: Correlate emails with meetings
8. **Email Clustering**: Group similar emails automatically

## Summary

Phase 11 provides a production-ready email intelligence system with:

✅ **Email Analysis**: Sentiment, priority, category, topics, entities
✅ **Relationship Tracking**: Communication patterns and network analysis
✅ **Insights Generation**: Daily, weekly, monthly insights
✅ **Anomaly Detection**: Identify unusual patterns
✅ **Recommendations**: Actionable suggestions
✅ **SQLite Persistence**: All data stored in database
✅ **LLM Integration**: Advanced analysis using language models
✅ **Comprehensive Tests**: 23 tests covering all components

The system is ready for production use and provides deep insights into email communications, helping users manage their inbox more effectively and maintain strong professional relationships.
