"""
LLM Evaluator - Evaluate LLM outputs using LLM-as-judge
"""

import json
import re
from typing import Dict, Any, Optional

from app.config.llm_config import create_llm
from .evaluation_store import EvaluationStore


class LLMEvaluator:
    """Evaluates LLM outputs using LLM-as-judge approach."""
    
    def __init__(self, store: EvaluationStore):
        """
        Initialize the LLM evaluator.
        
        Args:
            store: EvaluationStore instance
        """
        self.store = store
        self.llm = create_llm(temperature=0.1)  # Low temperature for consistent evaluation
    
    def evaluate_response_quality(
        self,
        prompt: str,
        response: str,
        criteria: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of an LLM response.
        
        Args:
            prompt: Original prompt
            response: LLM response to evaluate
            criteria: Evaluation criteria (relevance, accuracy, completeness, clarity)
            
        Returns:
            Dictionary with evaluation scores and feedback
        """
        if criteria is None:
            criteria = {
                'relevance': 'How relevant is the response to the prompt?',
                'accuracy': 'How accurate is the information provided?',
                'completeness': 'How complete is the response?',
                'clarity': 'How clear and well-structured is the response?'
            }
        
        eval_prompt = f"""Evaluate the following LLM response based on these criteria:

Prompt: {prompt}

Response: {response}

Criteria:
{json.dumps(criteria, indent=2)}

For each criterion, provide a score from 1-5 and a brief explanation.
Return ONLY a JSON object with this structure:
{{
    "scores": {{
        "relevance": <score 1-5>,
        "accuracy": <score 1-5>,
        "completeness": <score 1-5>,
        "clarity": <score 1-5>
    }},
    "feedback": {{
        "relevance": "<explanation>",
        "accuracy": "<explanation>",
        "completeness": "<explanation>",
        "clarity": "<explanation>"
    }},
    "overall_score": <average score>,
    "summary": "<brief overall assessment>"
}}"""
        
        try:
            result = self.llm.invoke(eval_prompt)
            # Ensure content is always a string for regex matching
            if hasattr(result, 'content'):
                content = result.content
                # Handle case where content might be a list
                if isinstance(content, list):
                    content = str(content)
                elif not isinstance(content, str):
                    content = str(content)
            else:
                content = str(result)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                return evaluation
            else:
                return {
                    'error': 'Failed to parse evaluation',
                    'raw_response': content
                }
                
        except Exception as e:
            return {
                'error': f'Evaluation failed: {str(e)}'
            }
    
    def evaluate_sentiment_accuracy(
        self,
        text: str,
        predicted_sentiment: str,
        predicted_score: float
    ) -> Dict[str, Any]:
        """
        Evaluate sentiment analysis accuracy.
        
        Args:
            text: Original text
            predicted_sentiment: Predicted sentiment label
            predicted_score: Predicted sentiment score
            
        Returns:
            Dictionary with evaluation results
        """
        eval_prompt = f"""Evaluate this sentiment analysis:

Text: {text}

Predicted Sentiment: {predicted_sentiment}
Predicted Score: {predicted_score}

Is the sentiment analysis correct? Provide:
1. Your assessment of the actual sentiment (positive/neutral/negative)
2. Whether the prediction is correct (yes/no)
3. A confidence score (0-1)
4. Brief explanation

Return ONLY a JSON object:
{{
    "actual_sentiment": "<positive/neutral/negative>",
    "prediction_correct": <true/false>,
    "confidence": <0-1>,
    "explanation": "<brief explanation>"
}}"""
        
        try:
            result = self.llm.invoke(eval_prompt)
            # Ensure content is always a string for regex matching
            if hasattr(result, 'content'):
                content = result.content
                # Handle case where content might be a list
                if isinstance(content, list):
                    content = str(content)
                elif not isinstance(content, str):
                    content = str(content)
            else:
                content = str(result)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                
                # Store metric
                if evaluation.get('prediction_correct'):
                    self.store.store_metric(
                        metric_name='sentiment_accuracy',
                        metric_category='accuracy',
                        value=1.0,
                        target_value=0.85,
                        unit='binary'
                    )
                
                return evaluation
            else:
                return {'error': 'Failed to parse evaluation'}
                
        except Exception as e:
            return {'error': f'Evaluation failed: {str(e)}'}
    
    def evaluate_classification_accuracy(
        self,
        text: str,
        predicted_category: str,
        possible_categories: list
    ) -> Dict[str, Any]:
        """
        Evaluate classification accuracy.
        
        Args:
            text: Original text
            predicted_category: Predicted category
            possible_categories: List of possible categories
            
        Returns:
            Dictionary with evaluation results
        """
        eval_prompt = f"""Evaluate this classification:

Text: {text}

Predicted Category: {predicted_category}
Possible Categories: {', '.join(possible_categories)}

Is the classification correct? Provide:
1. The most appropriate category
2. Whether the prediction is correct
3. Confidence score (0-1)
4. Brief explanation

Return ONLY a JSON object:
{{
    "correct_category": "<category>",
    "prediction_correct": <true/false>,
    "confidence": <0-1>,
    "explanation": "<brief explanation>"
}}"""
        
        try:
            result = self.llm.invoke(eval_prompt)
            # Ensure content is always a string for regex matching
            if hasattr(result, 'content'):
                content = result.content
                # Handle case where content might be a list
                if isinstance(content, list):
                    content = str(content)
                elif not isinstance(content, str):
                    content = str(content)
            else:
                content = str(result)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                
                # Store metric
                if evaluation.get('prediction_correct'):
                    self.store.store_metric(
                        metric_name='classification_accuracy',
                        metric_category='accuracy',
                        value=1.0,
                        target_value=0.90,
                        unit='binary'
                    )
                
                return evaluation
            else:
                return {'error': 'Failed to parse evaluation'}
                
        except Exception as e:
            return {'error': f'Evaluation failed: {str(e)}'}
    
    def evaluate_summary_quality(
        self,
        original_text: str,
        summary: str
    ) -> Dict[str, Any]:
        """
        Evaluate summary quality.
        
        Args:
            original_text: Original text
            summary: Generated summary
            
        Returns:
            Dictionary with evaluation results
        """
        eval_prompt = f"""Evaluate this summary:

Original Text: {original_text[:1000]}...

Summary: {summary}

Evaluate on these criteria:
1. Accuracy: Does it accurately represent the original?
2. Completeness: Does it cover key points?
3. Conciseness: Is it appropriately concise?
4. Coherence: Is it well-structured and clear?

Return ONLY a JSON object:
{{
    "scores": {{
        "accuracy": <1-5>,
        "completeness": <1-5>,
        "conciseness": <1-5>,
        "coherence": <1-5>
    }},
    "overall_score": <average>,
    "feedback": "<brief assessment>"
}}"""
        
        try:
            result = self.llm.invoke(eval_prompt)
            # Ensure content is always a string for regex matching
            if hasattr(result, 'content'):
                content = result.content
                # Handle case where content might be a list
                if isinstance(content, list):
                    content = str(content)
                elif not isinstance(content, str):
                    content = str(content)
            else:
                content = str(result)
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                
                # Store metric
                if 'overall_score' in evaluation:
                    self.store.store_metric(
                        metric_name='summary_quality',
                        metric_category='quality',
                        value=evaluation['overall_score'],
                        target_value=4.0,
                        unit='score'
                    )
                
                return evaluation
            else:
                return {'error': 'Failed to parse evaluation'}
                
        except Exception as e:
            return {'error': f'Evaluation failed: {str(e)}'}
    
    def batch_evaluate(
        self,
        evaluations: list,
        evaluation_type: str
    ) -> Dict[str, Any]:
        """
        Perform batch evaluation.
        
        Args:
            evaluations: List of evaluation tasks
            evaluation_type: Type of evaluation
            
        Returns:
            Dictionary with batch results
        """
        results = []
        
        for eval_task in evaluations:
            if evaluation_type == 'sentiment':
                result = self.evaluate_sentiment_accuracy(
                    text=eval_task['text'],
                    predicted_sentiment=eval_task['predicted_sentiment'],
                    predicted_score=eval_task['predicted_score']
                )
            elif evaluation_type == 'classification':
                result = self.evaluate_classification_accuracy(
                    text=eval_task['text'],
                    predicted_category=eval_task['predicted_category'],
                    possible_categories=eval_task['possible_categories']
                )
            elif evaluation_type == 'summary':
                result = self.evaluate_summary_quality(
                    original_text=eval_task['original_text'],
                    summary=eval_task['summary']
                )
            else:
                result = {'error': f'Unknown evaluation type: {evaluation_type}'}
            
            results.append(result)
        
        # Calculate aggregate metrics
        correct_count = sum(1 for r in results if r.get('prediction_correct', False))
        total_count = len(results)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'evaluation_type': evaluation_type,
            'total_evaluations': total_count,
            'correct_predictions': correct_count,
            'accuracy': accuracy,
            'results': results
        }

# Made with Bob
