# Phase 5: Multi-Agent System - Complete Guide

## Overview

Phase 5 implements a sophisticated multi-agent system with supervisor coordination. The system uses specialized agents that handle specific domains (email operations, knowledge retrieval) coordinated by a supervisor agent that routes queries intelligently.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Query                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Supervisor Agent                           │
│  • Analyzes user intent                                      │
│  • Routes to appropriate specialized agent                   │
│  • Provides context and instructions                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Email Agent  │ │Knowledge Agt │ │Calendar Agent│
│              │ │              │ │  (Future)    │
│ • Read       │ │ • Semantic   │ │              │
│ • Search     │ │   Search     │ │              │
│ • Summarize  │ │ • Q&A        │ │              │
│ • Draft      │ │ • Action     │ │              │
│ • Send       │ │   Items      │ │              │
│ • HITL       │ │ • Indexing   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Final Response                            │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Supervisor Agent (`app/agents/supervisor_agent.py`)

**Purpose**: Central coordinator that analyzes queries and routes to specialized agents.

**Key Features**:

- Intent analysis using LLM
- Intelligent routing logic
- Context extraction for specialized agents
- Structured response parsing

**Routing Logic**:

```python
def route_query(supervisor_llm, query: str) -> dict:
    """
    Returns:
    {
        'agent': 'email' | 'knowledge' | 'calendar',
        'reason': 'Why this agent was chosen',
        'context': 'Additional context for the agent'
    }
    """
```

**Example Routing Decisions**:

- "Show me my emails" → Email Agent
- "What did John say about the project?" → Knowledge Agent
- "Draft a reply to Sarah" → Email Agent
- "Extract action items from today's emails" → Knowledge Agent

### 2. Email Agent (`app/agents/email_agent_specialized.py`)

**Purpose**: Handles all email-related operations.

**Tools** (8 total):

1. `read_emails` - Fetch emails from Gmail
2. `search_emails` - Search with Gmail query syntax
3. `summarize_emails` - Generate email summaries
4. `draft_email` - Create new email drafts
5. `draft_reply_email` - Create reply drafts
6. `send_email_draft` - Send drafts with HITL approval
7. `send_reply_draft` - Send reply drafts with HITL approval
8. `generate_daily_digest` - Create daily email digest

**Capabilities**:

- Reading and searching emails
- Email summarization
- Drafting new emails and replies
- Human-in-the-loop approval for sending
- Daily digest generation

**Configuration**:

- Temperature: 0.7 (balanced creativity)
- Model: llama3.2:latest (configurable)

### 3. Knowledge Agent (`app/agents/knowledge_agent.py`)

**Purpose**: Handles knowledge retrieval and question answering using RAG.

**Tools** (5 total):

1. `semantic_search_emails` - Vector-based email search
2. `answer_question_about_emails` - RAG-based Q&A
3. `index_emails_to_vector_store` - Add emails to vector DB
4. `extract_action_items` - Extract tasks from emails
5. `get_vector_store_stats` - Vector store statistics

**Capabilities**:

- Semantic search across email content
- Question answering with context
- Action item extraction
- Email indexing for RAG
- Vector store management

**Configuration**:

- Temperature: 0.3 (more factual responses)
- Model: llama3.2:latest (configurable)
- Embeddings: all-MiniLM-L6-v2

### 4. Multi-Agent Workflow (`app/graph/multi_agent_workflow.py`)

**Purpose**: LangGraph workflow that coordinates all agents.

**State Management**:

```python
class MultiAgentState(TypedDict):
    query: str                      # User's query
    next_agent: str                 # Which agent to route to
    email_agent_response: str       # Email agent's response
    knowledge_agent_response: str   # Knowledge agent's response
    final_response: str             # Final response to user
    messages: list[BaseMessage]     # Conversation history
```

**Workflow Nodes**:

1. **Supervisor Node**: Routes queries to specialized agents
2. **Email Agent Node**: Executes email operations
3. **Knowledge Agent Node**: Executes knowledge retrieval

**Conditional Routing**:

```python
def route_to_agent(state: MultiAgentState) -> str:
    """Routes based on supervisor's decision"""
    next_agent = state.get("next_agent", "supervisor")
    if next_agent == "email":
        return "email_agent"
    elif next_agent == "knowledge":
        return "knowledge_agent"
    else:
        return END
```

## Usage

### 1. Single Query Execution

```python
from app.graph.multi_agent_workflow import create_multi_agent_system, run_multi_agent_query

# Create the workflow
workflow = create_multi_agent_system()

# Run a single query
result = run_multi_agent_query(workflow, "Show me my latest emails")

print(f"Routed to: {result['next_agent']}")
print(f"Response: {result['final_response']}")
```

### 2. Interactive Conversation Mode

```python
from app.graph.multi_agent_workflow import create_multi_agent_system, run_multi_agent_conversation

# Create the workflow
workflow = create_multi_agent_system()

# Start interactive session
run_multi_agent_conversation(workflow)
```

**Interactive Session Example**:

```
Multi-Agent Assistant (type 'quit' to exit)

You: Show me emails from last week
Assistant: [Email agent fetches and displays emails]

You: What did they say about the project deadline?
Assistant: [Knowledge agent searches and answers]

You: Draft a reply to the most recent one
Assistant: [Email agent creates draft with HITL approval]
```

### 3. Programmatic Usage

```python
from app.agents import (
    create_supervisor_agent,
    create_specialized_email_agent,
    create_knowledge_agent,
    route_query
)

# Create agents individually
supervisor = create_supervisor_agent()
email_agent = create_specialized_email_agent()
knowledge_agent = create_knowledge_agent()

# Route a query
routing = route_query(supervisor, "What did John say about the budget?")
print(f"Route to: {routing['agent']}")  # 'knowledge'

# Use the appropriate agent
if routing['agent'] == 'knowledge':
    response = knowledge_agent.invoke({
        "messages": [("user", routing['context'])]
    })
```

## Query Routing Examples

### Email Agent Queries

These queries route to the Email Agent:

1. **Reading Emails**:
   - "Show me my latest emails"
   - "Read my unread messages"
   - "Get emails from today"

2. **Searching Emails**:
   - "Search for emails from john@example.com"
   - "Find emails about the project"
   - "Show me emails with attachments"

3. **Summarizing**:
   - "Summarize my unread emails"
   - "Give me a summary of today's emails"
   - "Create a daily digest"

4. **Drafting**:
   - "Draft an email to Sarah about the meeting"
   - "Create a reply to the latest email"
   - "Write an email to the team"

5. **Sending** (with HITL):
   - "Send a reply to Mike's email"
   - "Send the draft I just created"

### Knowledge Agent Queries

These queries route to the Knowledge Agent:

1. **Question Answering**:
   - "What did John say about the budget?"
   - "When is the project deadline?"
   - "Who approved the proposal?"

2. **Semantic Search**:
   - "Find emails discussing quarterly targets"
   - "Search for conversations about hiring"
   - "Show me emails related to the conference"

3. **Action Items**:
   - "What are my action items from today's emails?"
   - "Extract tasks from recent emails"
   - "List pending items from this week"

4. **Information Retrieval**:
   - "What was decided in the last meeting?"
   - "Find information about the new policy"
   - "What are the key points from the CEO's email?"

## Testing

### Run All Tests

```bash
python test_multi_agent.py
```

### Run Specific Tests

```bash
# Test supervisor routing
python test_multi_agent.py routing

# Test email agent
python test_multi_agent.py email

# Test knowledge agent
python test_multi_agent.py knowledge

# Test multi-turn conversation
python test_multi_agent.py conversation

# Test agent specialization
python test_multi_agent.py specialization
```

### Test Coverage

The test suite includes:

1. **Supervisor Routing Tests**: Verify correct routing decisions
2. **Email Agent Tests**: Test email operations
3. **Knowledge Agent Tests**: Test RAG and Q&A
4. **Multi-Turn Conversation**: Test context maintenance
5. **Agent Specialization**: Verify domain separation
6. **System Information**: Test metadata retrieval

## Configuration

### Environment Variables

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Gmail API (for email agent)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# ChromaDB (for knowledge agent)
CHROMA_PERSIST_DIR=./chroma_db
```

### Agent Configuration

```python
# Supervisor Agent
supervisor = create_supervisor_agent(
    model_name="llama3.2:latest",
    temperature=0.5  # Balanced for routing decisions
)

# Email Agent
email_agent = create_specialized_email_agent(
    model_name="llama3.2:latest",
    temperature=0.7  # Creative for drafting
)

# Knowledge Agent
knowledge_agent = create_knowledge_agent(
    model_name="llama3.2:latest",
    temperature=0.3  # Factual for Q&A
)
```

## Advanced Features

### 1. Context Preservation

The system maintains conversation context across multiple turns:

```python
# Turn 1
"Show me emails from last week"
# → Email agent fetches emails

# Turn 2 (uses context from Turn 1)
"What did they say about the project?"
# → Knowledge agent searches within those emails

# Turn 3 (uses context from Turn 1 & 2)
"Draft a reply to the most recent one"
# → Email agent creates reply with context
```

### 2. Agent Collaboration

Agents can defer to each other when needed:

```python
# Email agent recognizes it needs knowledge retrieval
"Show me emails and tell me what they're about"
# → Email agent fetches emails
# → Supervisor routes follow-up to knowledge agent
# → Knowledge agent analyzes content
```

### 3. Human-in-the-Loop Integration

Email sending requires human approval:

```python
# User: "Send a reply to John's email"
# 1. Email agent drafts reply
# 2. Shows draft to user
# 3. User approves/rejects/modifies
# 4. Email sent only after approval
```

### 4. Extensibility

Easy to add new specialized agents:

```python
# Add Calendar Agent
from app.agents.calendar_agent import create_calendar_agent

# Update supervisor routing
def route_query(supervisor_llm, query: str) -> dict:
    # Add calendar routing logic
    if "schedule" in query or "meeting" in query:
        return {"agent": "calendar", ...}
```

## Performance Considerations

### 1. Model Selection

- **Supervisor**: Needs good reasoning (llama3.2:latest)
- **Email Agent**: Needs creativity for drafting (temperature 0.7)
- **Knowledge Agent**: Needs accuracy for Q&A (temperature 0.3)

### 2. Vector Store

- **Embeddings**: all-MiniLM-L6-v2 (fast, good quality)
- **Persistence**: ChromaDB with disk persistence
- **Indexing**: Batch index emails for efficiency

### 3. Caching

- LangGraph automatically caches state
- Vector store persists across sessions
- Gmail API uses token caching

## Troubleshooting

### Issue: Incorrect Routing

**Problem**: Queries routed to wrong agent

**Solution**:

1. Check supervisor prompt in `supervisor_agent.py`
2. Add more routing examples
3. Adjust temperature (lower = more consistent)

### Issue: Agent Not Responding

**Problem**: Agent returns empty response

**Solution**:

1. Verify tools are properly loaded
2. Check Ollama is running
3. Review agent system prompt
4. Check tool execution logs

### Issue: Context Not Maintained

**Problem**: Multi-turn conversation loses context

**Solution**:

1. Verify `messages` field in state
2. Check state management in workflow
3. Ensure proper message formatting

## Future Enhancements

### Planned Features

1. **Calendar Agent**: Schedule management and meeting coordination
2. **Task Agent**: Task tracking and project management
3. **Document Agent**: Document search and analysis
4. **Analytics Agent**: Email analytics and insights

### Potential Improvements

1. **Parallel Execution**: Run multiple agents simultaneously
2. **Agent Memory**: Long-term memory across sessions
3. **Tool Sharing**: Shared tools between agents
4. **Dynamic Routing**: Learn routing patterns over time
5. **Agent Feedback**: Agents provide feedback to supervisor

## Integration with Previous Phases

### Phase 1-2: Gmail Integration

- Email agent uses Gmail tools
- OAuth2 authentication
- Email fetching and searching

### Phase 3: RAG Memory

- Knowledge agent uses vector store
- Semantic search capabilities
- Question answering with context

### Phase 4: Human-in-the-Loop

- Email agent integrates HITL workflow
- Draft approval process
- Send confirmation

### Phase 5: Multi-Agent System

- Supervisor coordinates all capabilities
- Specialized agents for domains
- Intelligent routing and collaboration

## Summary

Phase 5 implements a production-ready multi-agent system with:

✅ **Supervisor Agent**: Intelligent query routing
✅ **Email Agent**: Complete email operations with HITL
✅ **Knowledge Agent**: RAG-based Q&A and search
✅ **LangGraph Workflow**: Coordinated execution
✅ **Interactive Mode**: Conversational interface
✅ **Comprehensive Testing**: Full test suite
✅ **Extensible Architecture**: Easy to add new agents

The system provides a powerful, flexible foundation for an AI Executive Assistant that can handle complex, multi-step tasks across different domains.

---

**Made with Bob** 🤖
