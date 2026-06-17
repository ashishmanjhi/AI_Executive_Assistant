"""
Email Analyzer - Advanced email analysis using LLM
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from app.config.llm_config import create_llm


class EmailAnalyzer:
    """Performs comprehensive email analysis using LLM."""
    
    def __init__(self):
        """Initialize the email analyzer."""
        self.llm = create_llm()
    
    def analyze_email(
        self,
        email_id: str,
        user_id: str,
        sender: str,
        subject: str,
        body: str,
        received_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive email analysis.
        
        Args:
            email_id: Unique email identifier
            user_id: User identifier
            sender: Email sender address
            subject: Email subject
            body: Email body text
            received_at: When email was received
            
        Returns:
            Dictionary containing all analysis results
        """
        # Sentiment analysis
        sentiment = self.analyze_sentiment(body)
        
        # Priority scoring
        priority = self.calculate_priority(subject, body, sender)
        
        # Category classification
        category = self.classify_category(subject, body)
        
        # Topic extraction
        topics = self.extract_topics(subject, body)
        
        # Entity extraction
        entities = self.extract_entities(body)
        
        return {
            'email_id': email_id,
            'user_id': user_id,
            'sender': sender,
            'sentiment': sentiment,
            'priority': priority,
            'category': category,
            'topics': topics,
            'entities': entities,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of email text.
        
        Args:
            text: Email text to analyze
            
        Returns:
            Dictionary with sentiment score, label, and confidence
        """
        if not text or len(text.strip()) < 10:
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.5
            }
        
        prompt = f"""Analyze the sentiment of this email text and return ONLY a JSON object with no additional text:

Email text:
{text[:1000]}

Return JSON with:
- score: float from -1.0 (very negative) to 1.0 (very positive)
- label: one of 'positive', 'neutral', or 'negative'
- confidence: float from 0.0 to 1.0

Example response:
{{"score": 0.7, "label": "positive", "confidence": 0.85}}"""
        
        try:
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response - ensure it's always a string
            if hasattr(response, 'content'):
                # Handle case where content might be a list or other type
                content = response.content
                if isinstance(content, list):
                    # If it's a list, join the elements or take the first string element
                    content = ' '.join(str(item) for item in content)
                else:
                    content = str(content)
            else:
                content = str(response)
            
            # Try to find JSON in the response
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate and normalize
                score = float(result.get('score', 0.0))
                score = max(-1.0, min(1.0, score))
                
                label = result.get('label', 'neutral')
                if label not in ['positive', 'neutral', 'negative']:
                    label = 'neutral'
                
                confidence = float(result.get('confidence', 0.5))
                confidence = max(0.0, min(1.0, confidence))
                
                return {
                    'score': score,
                    'label': label,
                    'confidence': confidence
                }
            else:
                # Fallback if no JSON found
                return {
                    'score': 0.0,
                    'label': 'neutral',
                    'confidence': 0.5
                }
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return {
                'score': 0.0,
                'label': 'neutral',
                'confidence': 0.5
            }
    
    def calculate_priority(
        self,
        subject: str,
        body: str,
        sender: str
    ) -> Dict[str, float]:
        """
        Calculate email priority scores.
        
        Args:
            subject: Email subject
            body: Email body
            sender: Sender email address
            
        Returns:
            Dictionary with priority, urgency, and importance scores
        """
        urgency_score = self._calculate_urgency(subject, body)
        importance_score = self._calculate_importance(sender, subject, body)
        
        # Overall priority is weighted combination
        priority_score = (urgency_score * 0.6) + (importance_score * 0.4)
        
        return {
            'priority_score': round(priority_score, 3),
            'urgency_score': round(urgency_score, 3),
            'importance_score': round(importance_score, 3)
        }
    
    def _calculate_urgency(self, subject: str, body: str) -> float:
        """Calculate urgency score based on keywords and patterns."""
        urgency = 0.3  # Base urgency
        
        text = (subject + " " + body).lower()
        
        # Urgent keywords
        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency',
            'important', 'deadline', 'today', 'now', 'quick', 'fast'
        ]
        
        for keyword in urgent_keywords:
            if keyword in text:
                urgency += 0.15
        
        # Time-sensitive patterns
        time_patterns = [
            r'by \d+:\d+',  # by 3:00
            r'by (today|tomorrow|tonight)',
            r'within \d+ (hour|minute)',
            r'due (today|tomorrow)',
            r'expires? (today|tomorrow|soon)'
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text):
                urgency += 0.2
                break
        
        # Exclamation marks (but cap the bonus)
        exclamation_count = text.count('!')
        urgency += min(0.1, exclamation_count * 0.03)
        
        # ALL CAPS in subject (indicates urgency)
        if subject and subject.isupper() and len(subject) > 5:
            urgency += 0.15
        
        return min(1.0, urgency)
    
    def _calculate_importance(
        self,
        sender: str,
        subject: str,
        body: str
    ) -> float:
        """Calculate importance score."""
        importance = 0.5  # Base importance
        
        # Check if sender is from important domain
        important_domains = ['ceo', 'president', 'director', 'manager', 'vp']
        sender_lower = sender.lower()
        
        for domain in important_domains:
            if domain in sender_lower:
                importance += 0.2
                break
        
        # Check for important keywords
        text = (subject + " " + body).lower()
        important_keywords = [
            'contract', 'agreement', 'legal', 'compliance',
            'board', 'executive', 'strategic', 'confidential',
            'meeting', 'decision', 'approval', 'budget'
        ]
        
        for keyword in important_keywords:
            if keyword in text:
                importance += 0.1
        
        return min(1.0, importance)
    
    def classify_category(self, subject: str, body: str) -> str:
        """
        Classify email into a category.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Category name
        """
        text = (subject + " " + body).lower()
        
        # Simple keyword-based classification
        categories = {
            'meeting': ['meeting', 'schedule', 'calendar', 'appointment', 'call'],
            'task': ['task', 'todo', 'action item', 'follow up', 'reminder'],
            'question': ['question', 'help', 'how to', 'can you', 'could you', '?'],
            'notification': ['notification', 'alert', 'update', 'fyi', 'heads up'],
            'invoice': ['invoice', 'payment', 'bill', 'receipt', 'purchase'],
            'newsletter': ['newsletter', 'digest', 'weekly', 'monthly', 'unsubscribe'],
            'social': ['linkedin', 'facebook', 'twitter', 'social', 'network'],
            'personal': ['personal', 'private', 'confidential']
        }
        
        # Count matches for each category
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        # Return category with highest score
        if scores:
            return max(scores, key=lambda k: scores[k])
        
        return 'general'
    
    def extract_topics(self, subject: str, body: str) -> List[str]:
        """
        Extract main topics from email.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            List of topic strings
        """
        if not body or len(body.strip()) < 20:
            return []
        
        prompt = f"""Extract the main topics from this email. Return ONLY a JSON array of topic strings with no additional text.

Subject: {subject}
Body: {body[:800]}

Return a JSON array of 2-5 main topics. Example:
["project deadline", "budget approval", "team meeting"]"""
        
        try:
            response = self.llm.invoke(prompt)
            
            # Extract content and ensure it's always a string
            if hasattr(response, 'content'):
                content = response.content
                if isinstance(content, list):
                    content = ' '.join(str(item) for item in content)
                else:
                    content = str(content)
            else:
                content = str(response)
            
            # Try to find JSON array in response
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                topics = json.loads(json_match.group())
                if isinstance(topics, list):
                    # Filter and clean topics
                    return [str(t).strip() for t in topics if t][:5]
            
            return []
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return []
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from email text.
        
        Args:
            text: Email text
            
        Returns:
            Dictionary with entity types and lists of entities
        """
        entities = {
            'people': [],
            'organizations': [],
            'dates': [],
            'amounts': []
        }
        
        if not text or len(text.strip()) < 20:
            return entities
        
        # Simple pattern-based extraction
        
        # Dates (simple patterns)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        # Amounts (currency)
        amount_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        entities['amounts'] = re.findall(amount_pattern, text)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]  # Limit to 10 per type
        
        return entities
    
    def batch_analyze(
        self,
        emails: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple emails in batch.
        
        Args:
            emails: List of email dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        
        for email in emails:
            try:
                result = self.analyze_email(
                    email_id=email.get('id', ''),
                    user_id=email.get('user_id', ''),
                    sender=email.get('from', ''),
                    subject=email.get('subject', ''),
                    body=email.get('body', ''),
                    received_at=email.get('received_at')
                )
                results.append(result)
            except Exception as e:
                print(f"Error analyzing email {email.get('id')}: {e}")
                continue
        
        return results

# Made with Bob
