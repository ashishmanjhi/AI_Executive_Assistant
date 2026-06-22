"""
Supervisor Agent

Coordinates multiple specialized agents and routes user queries
to the appropriate agent based on the task requirements.
"""

import logging
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
import os

logger = logging.getLogger(__name__)


SUPERVISOR_SYSTEM_PROMPT = """You are the Supervisor Agent, the coordinator of a multi-agent AI Executive Assistant system.

Your role is to analyze user queries and route them to the appropriate specialized agent.

## Available Agents:

### 1. Email Agent
**Handles:**
- Reading emails (fetch recent, search)
- Summarizing emails
- Generating daily digests
- Drafting emails
- Sending emails (with human approval)

**Route to Email Agent when user wants to:**
- "Show me my emails"
- "Search for emails about X"
- "Summarize my emails"
- "Generate daily digest"
- "Draft an email to X"
- "Send an email"

### 2. Knowledge Agent
**Handles:**
- Semantic search through email history
- Question answering using RAG
- Storing emails for search
- Extracting action items
- Finding emails by sender

**Route to Knowledge Agent when user wants to:**
- "What did X say about Y?"
- "Find information about Z in emails"
- "What are my action items?"
- "Search emails semantically"
- "Answer questions from email content"

### 3. Calendar Agent
**Handles:**
- Viewing calendar events
- Creating/scheduling meetings
- Checking availability
- Finding free time slots
- Managing calendars

**Route to Calendar Agent when user wants to:**
- "What's on my calendar?"
- "Schedule a meeting"
- "Create an event"
- "When am I free?"
- "Check my availability"
- "Find free time on Friday"
- "List my calendars"

## Routing Decision Process:

1. **Analyze the user's intent**
   - What is the primary goal?
   - What information or action is needed?

2. **Identify the appropriate agent**
   - Email operations → Email Agent
   - Knowledge/Q&A → Knowledge Agent
   - Scheduling → Calendar Agent

3. **Handle complex queries**
   - If query needs multiple agents, route to primary agent first
   - Primary agent can request help from others if needed

4. **Default routing**
   - If unclear, route to Email Agent (most general)
   - Email Agent can defer to Knowledge Agent if needed

## Routing Examples:

User: "Show me my recent emails"
Decision: Email Agent (reading emails)

User: "What did the client say about deployment?"
Decision: Knowledge Agent (question answering with RAG)

User: "Draft an email thanking John for the meeting"
Decision: Email Agent (email composition)

User: "Find all emails about the project and summarize them"
Decision: Email Agent first (can use Knowledge Agent for search)

User: "What are my pending tasks from emails?"
Decision: Knowledge Agent (action item extraction)

## Your Response Format:

When routing, respond with:
1. Which agent to use
2. Brief reason for the choice
3. Any context the agent needs

Example:
"Routing to Email Agent because you want to read recent emails."

Be decisive, clear, and efficient in your routing decisions.
"""


def create_supervisor_agent(model_name: str | None = None, temperature: float = 0.5):
    """
    Create the Supervisor Agent.
    
    This agent analyzes user queries and routes them to the appropriate
    specialized agent (Email Agent, Knowledge Agent, etc.).
    
    Args:
        model_name: Ollama model name (default: from .env or 'qwen3:4b')
        temperature: Model temperature (default: 0.5 for balanced routing)
    
    Returns:
        LangGraph agent executor for supervision and routing
    """
    # Get model configuration
    if model_name is None:
        model_name = os.getenv('OLLAMA_MODEL', 'qwen3:4b')
    
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # Initialize LLM
    llm = ChatOllama(
        model=model_name,
        base_url=base_url,
        temperature=temperature
    )
    
    logger.info("Supervisor Agent created successfully")
    return llm


def route_query(supervisor_llm, query: str) -> dict:
    """
    Route a user query to the appropriate agent.
    
    Args:
        supervisor_llm: Supervisor LLM instance
        query: User's query
    
    Returns:
        Dictionary with routing decision:
        {
            'agent': 'email' | 'knowledge' | 'calendar',
            'reason': 'Why this agent was chosen',
            'context': 'Additional context for the agent'
        }
    """
    try:
        # Create messages with system prompt and user query
        messages = [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=f"""Analyze this user query and decide which agent should handle it.

User Query: "{query}"

Respond in this exact format:
AGENT: [email|knowledge|calendar]
REASON: [Brief explanation]
CONTEXT: [Any relevant context for the agent]

Your decision:""")
        ]

        # Get routing decision
        response = supervisor_llm.invoke(messages)
        
        # Extract content
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        # Parse response
        lines = content.strip().split('\n')
        result = {
            'agent': 'email',  # default
            'reason': 'Default routing',
            'context': query
        }
        
        for line in lines:
            if line.startswith('AGENT:'):
                agent = line.split(':', 1)[1].strip().lower()
                if agent in ['email', 'knowledge', 'calendar']:
                    result['agent'] = agent
            elif line.startswith('REASON:'):
                result['reason'] = line.split(':', 1)[1].strip()
            elif line.startswith('CONTEXT:'):
                result['context'] = line.split(':', 1)[1].strip()
        
        logger.info(f"Routed query to {result['agent']} agent: {result['reason']}")
        return result
        
    except Exception as e:
        logger.error(f"Error routing query: {e}")
        # Default to email agent on error
        return {
            'agent': 'email',
            'reason': f'Error in routing: {str(e)}',
            'context': query
        }


def get_supervisor_info():
    """Get information about the Supervisor Agent."""
    return {
        "name": "Supervisor Agent",
        "role": "Multi-Agent Coordinator",
        "responsibilities": [
            "Analyze user queries",
            "Route to appropriate agent",
            "Coordinate multi-agent workflows",
            "Handle complex queries"
        ],
        "routing_logic": {
            "email_operations": "Email Agent",
            "knowledge_qa": "Knowledge Agent",
            "scheduling": "Calendar Agent (future)"
        },
        "agents_managed": [
            "Email Agent",
            "Knowledge Agent",
            "Calendar Agent (future)"
        ],
        "decision_factors": [
            "User intent",
            "Required capabilities",
            "Agent specialization",
            "Query complexity"
        ]
    }


# Made with Bob