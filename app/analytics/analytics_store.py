"""
Analytics Store - Database operations for email analytics
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import threading


class AnalyticsStore:
    """Manages storage and retrieval of email analytics data."""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        """
        Initialize the analytics store.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Email analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_analytics (
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
                    analyzed_at REAL NOT NULL,
                    created_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_email_analytics_user 
                ON email_analytics(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_email_analytics_sender 
                ON email_analytics(sender_email)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_email_analytics_priority 
                ON email_analytics(priority_score)
            """)
            
            # Communication relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS communication_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    contact_email TEXT NOT NULL,
                    total_emails_sent INTEGER DEFAULT 0,
                    total_emails_received INTEGER DEFAULT 0,
                    avg_response_time_hours REAL,
                    last_interaction REAL,
                    relationship_strength REAL,
                    communication_frequency TEXT,
                    created_at REAL DEFAULT (julianday('now')),
                    updated_at REAL DEFAULT (julianday('now')),
                    UNIQUE(user_id, contact_email)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_user 
                ON communication_relationships(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_strength 
                ON communication_relationships(relationship_strength)
            """)
            
            # Email topics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_name TEXT NOT NULL UNIQUE,
                    keywords TEXT NOT NULL,
                    email_count INTEGER DEFAULT 0,
                    created_at REAL DEFAULT (julianday('now')),
                    updated_at REAL DEFAULT (julianday('now'))
                )
            """)
            
            # Email topic mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_topic_mapping (
                    email_id TEXT NOT NULL,
                    topic_id INTEGER NOT NULL,
                    relevance_score REAL NOT NULL,
                    PRIMARY KEY (email_id, topic_id),
                    FOREIGN KEY (topic_id) REFERENCES email_topics(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic_mapping_email 
                ON email_topic_mapping(email_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic_mapping_topic 
                ON email_topic_mapping(topic_id)
            """)
            
            # Analytics insights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_insights (
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
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_insights_user 
                ON analytics_insights(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_insights_type 
                ON analytics_insights(insight_type)
            """)
            
            # Email statistics table (aggregated daily)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    emails_received INTEGER DEFAULT 0,
                    emails_sent INTEGER DEFAULT 0,
                    avg_response_time_hours REAL,
                    top_senders TEXT,
                    top_topics TEXT,
                    sentiment_distribution TEXT,
                    created_at REAL DEFAULT (julianday('now')),
                    UNIQUE(user_id, date)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_statistics_user 
                ON email_statistics(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_statistics_date 
                ON email_statistics(date)
            """)
            
            conn.commit()
            conn.close()
    
    def store_email_analysis(
        self,
        email_id: str,
        user_id: str,
        sender_email: str,
        sentiment: Dict[str, Any],
        priority: Dict[str, float],
        category: str,
        topics: List[str],
        entities: Dict[str, List[str]]
    ) -> bool:
        """
        Store email analysis results.
        
        Args:
            email_id: Unique email identifier
            user_id: User identifier
            sender_email: Email sender address
            sentiment: Sentiment analysis results
            priority: Priority scores
            category: Email category
            topics: List of extracted topics
            entities: Extracted entities
            
        Returns:
            True if stored successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO email_analytics
                    (email_id, user_id, sender_email, sentiment_score, sentiment_label,
                     priority_score, urgency_score, importance_score, category,
                     topics, entities, analyzed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email_id,
                    user_id,
                    sender_email,
                    sentiment.get('score'),
                    sentiment.get('label'),
                    priority.get('priority_score'),
                    priority.get('urgency_score'),
                    priority.get('importance_score'),
                    category,
                    json.dumps(topics),
                    json.dumps(entities),
                    datetime.now().timestamp()
                ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                print(f"Error storing email analysis: {e}")
                return False
    
    def get_email_analysis(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis for a specific email.
        
        Args:
            email_id: Email identifier
            
        Returns:
            Analysis data or None if not found
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM email_analytics WHERE email_id = ?
            """, (email_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'email_id': row['email_id'],
                    'user_id': row['user_id'],
                    'sender_email': row['sender_email'],
                    'sentiment': {
                        'score': row['sentiment_score'],
                        'label': row['sentiment_label']
                    },
                    'priority': {
                        'priority_score': row['priority_score'],
                        'urgency_score': row['urgency_score'],
                        'importance_score': row['importance_score']
                    },
                    'category': row['category'],
                    'topics': json.loads(row['topics']) if row['topics'] else [],
                    'entities': json.loads(row['entities']) if row['entities'] else {},
                    'analyzed_at': row['analyzed_at']
                }
            return None
    
    def get_high_priority_emails(
        self,
        user_id: str,
        threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get high priority emails for a user.
        
        Args:
            user_id: User identifier
            threshold: Minimum priority score
            limit: Maximum number of results
            
        Returns:
            List of high priority email analyses
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM email_analytics
                WHERE user_id = ? AND priority_score >= ?
                ORDER BY priority_score DESC, analyzed_at DESC
                LIMIT ?
            """, (user_id, threshold, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'email_id': row['email_id'],
                    'sender_email': row['sender_email'],
                    'priority_score': row['priority_score'],
                    'urgency_score': row['urgency_score'],
                    'importance_score': row['importance_score'],
                    'category': row['category'],
                    'sentiment_label': row['sentiment_label'],
                    'analyzed_at': row['analyzed_at']
                })
            
            return results
    
    def update_relationship(
        self,
        user_id: str,
        contact_email: str,
        emails_sent: int = 0,
        emails_received: int = 0,
        response_time_hours: Optional[float] = None
    ) -> bool:
        """
        Update communication relationship data.
        
        Args:
            user_id: User identifier
            contact_email: Contact email address
            emails_sent: Number of emails sent
            emails_received: Number of emails received
            response_time_hours: Average response time in hours
            
        Returns:
            True if updated successfully
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get existing relationship
                cursor.execute("""
                    SELECT * FROM communication_relationships
                    WHERE user_id = ? AND contact_email = ?
                """, (user_id, contact_email))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    new_sent = existing[3] + emails_sent
                    new_received = existing[4] + emails_received
                    
                    # Calculate new average response time
                    if response_time_hours is not None and existing[5] is not None:
                        total_emails = new_sent + new_received
                        old_total = existing[3] + existing[4]
                        new_avg = (
                            (existing[5] * old_total + response_time_hours) / 
                            (total_emails if total_emails > 0 else 1)
                        )
                    elif response_time_hours is not None:
                        new_avg = response_time_hours
                    else:
                        new_avg = existing[5]
                    
                    # Calculate relationship strength (0-1)
                    total_interactions = new_sent + new_received
                    recency_factor = 1.0  # Could be based on last_interaction
                    strength = min(1.0, (total_interactions / 100) * recency_factor)
                    
                    # Determine frequency
                    frequency = self._calculate_frequency(total_interactions)
                    
                    cursor.execute("""
                        UPDATE communication_relationships
                        SET total_emails_sent = ?,
                            total_emails_received = ?,
                            avg_response_time_hours = ?,
                            last_interaction = ?,
                            relationship_strength = ?,
                            communication_frequency = ?,
                            updated_at = julianday('now')
                        WHERE user_id = ? AND contact_email = ?
                    """, (
                        new_sent, new_received, new_avg,
                        datetime.now().timestamp(), strength, frequency,
                        user_id, contact_email
                    ))
                else:
                    # Insert new
                    strength = min(1.0, (emails_sent + emails_received) / 100)
                    frequency = self._calculate_frequency(emails_sent + emails_received)
                    
                    cursor.execute("""
                        INSERT INTO communication_relationships
                        (user_id, contact_email, total_emails_sent, total_emails_received,
                         avg_response_time_hours, last_interaction, relationship_strength,
                         communication_frequency)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id, contact_email, emails_sent, emails_received,
                        response_time_hours, datetime.now().timestamp(),
                        strength, frequency
                    ))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                print(f"Error updating relationship: {e}")
                return False
    
    def _calculate_frequency(self, total_emails: int) -> str:
        """Calculate communication frequency category."""
        if total_emails >= 50:
            return "very_high"
        elif total_emails >= 20:
            return "high"
        elif total_emails >= 10:
            return "medium"
        elif total_emails >= 5:
            return "low"
        else:
            return "very_low"
    
    def get_top_contacts(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top contacts by relationship strength.
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
            
        Returns:
            List of top contacts
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM communication_relationships
                WHERE user_id = ?
                ORDER BY relationship_strength DESC, last_interaction DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'contact_email': row['contact_email'],
                    'total_emails_sent': row['total_emails_sent'],
                    'total_emails_received': row['total_emails_received'],
                    'avg_response_time_hours': row['avg_response_time_hours'],
                    'last_interaction': row['last_interaction'],
                    'relationship_strength': row['relationship_strength'],
                    'communication_frequency': row['communication_frequency']
                })
            
            return results
    
    def store_insight(
        self,
        user_id: str,
        insight_type: str,
        title: str,
        description: str,
        data: Optional[Dict[str, Any]] = None,
        importance_score: float = 0.5
    ) -> int:
        """
        Store an analytics insight.
        
        Args:
            user_id: User identifier
            insight_type: Type of insight
            title: Insight title
            description: Insight description
            data: Additional data
            importance_score: Importance score (0-1)
            
        Returns:
            Insight ID
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analytics_insights
                (user_id, insight_type, title, description, data, importance_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id, insight_type, title, description,
                json.dumps(data) if data else None, importance_score
            ))
            
            insight_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # lastrowid should always be an int after INSERT, but type checker needs assurance
            if insight_id is None:
                raise RuntimeError("Failed to get insight ID after insert")
            
            return insight_id
    
    def get_insights(
        self,
        user_id: str,
        insight_type: Optional[str] = None,
        unread_only: bool = False,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get insights for a user.
        
        Args:
            user_id: User identifier
            insight_type: Filter by insight type
            unread_only: Only return unread insights
            limit: Maximum number of results
            
        Returns:
            List of insights
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM analytics_insights WHERE user_id = ?"
            params: List[Any] = [user_id]
            
            if insight_type:
                query += " AND insight_type = ?"
                params.append(insight_type)
            
            if unread_only:
                query += " AND is_read = 0"
            
            query += " ORDER BY importance_score DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'insight_type': row['insight_type'],
                    'title': row['title'],
                    'description': row['description'],
                    'data': json.loads(row['data']) if row['data'] else None,
                    'importance_score': row['importance_score'],
                    'is_read': bool(row['is_read']),
                    'created_at': row['created_at']
                })
            
            return results
    
    def mark_insight_read(self, insight_id: int) -> bool:
        """Mark an insight as read."""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE analytics_insights SET is_read = 1 WHERE id = ?
                """, (insight_id,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                print(f"Error marking insight as read: {e}")
                return False
    
    def get_sentiment_distribution(
        self,
        user_id: str,
        days: int = 7
    ) -> Dict[str, int]:
        """
        Get sentiment distribution for recent emails.
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with sentiment counts
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = (datetime.now() - timedelta(days=days)).timestamp()
            
            cursor.execute("""
                SELECT sentiment_label, COUNT(*) as count
                FROM email_analytics
                WHERE user_id = ? AND analyzed_at >= ?
                GROUP BY sentiment_label
            """, (user_id, cutoff))
            
            rows = cursor.fetchall()
            conn.close()
            
            distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
            for row in rows:
                if row[0]:
                    distribution[row[0]] = row[1]
            
            return distribution

# Made with Bob
