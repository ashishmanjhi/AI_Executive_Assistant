# Phase 6: Persistent Memory System - Complete Guide

## Overview

Phase 6 implements a comprehensive persistent memory system that enables the AI Executive Assistant to remember conversations, learn user preferences, and maintain context across sessions. The system uses SQLite for storage and LangGraph checkpointing for conversation state management.

## Architecture

### Components

1. **Memory Store** (`app/memory/memory_store.py`)
   - SQLite-based persistent storage
   - Five types of memory: Conversation, Preferences, Episodic, Semantic, Procedural

2. **Checkpointer** (`app/memory/checkpointer.py`)
   - LangGraph checkpoint integration
   - Enables conversation state persistence across sessions

3. **Memory-Enhanced Agent** (`app/agents/memory_agent.py`)
   - Agent with memory capabilities
   - Context-aware responses using historical data

## Memory Types

### 1. Conversation History

Stores all user-assistant interactions with metadata.

**Features:**

- Session-based organization
- Timestamp tracking
- Metadata support
- Retrievable by session or limit

**Usage:**

```python
from app.memory.memory_store import MemoryStore

memory = MemoryStore()

# Add message
memory.add_conversation_message(
    session_id="session_123",
    role="user",
    content="What emails do I have?",
    metadata={"source": "web_ui"}
)

# Get history
history = memory.get_conversation_history("session_123", limit=10)
```

### 2. User Preferences

Key-value storage for user settings and preferences.

**Features:**

- Persistent across sessions
- JSON value support
- Update tracking

**Usage:**

```python
# Set preference
memory.set_preference("email_summary_style", "concise")
memory.set_preference("work_hours", {"start": "09:00", "end": "17:00"})

# Get preference
style = memory.get_preference("email_summary_style")
all_prefs = memory.get_all_preferences()
```

### 3. Episodic Memory

Records specific events and interactions with importance ratings.

**Features:**

- Event type categorization
- Importance scoring (1-10)
- Context storage
- Timestamp tracking

**Usage:**

```python
# Record event
memory.add_episodic_memory(
    event_type="meeting",
    description="Had important meeting with CEO about Q4 strategy",
    context={"attendees": ["CEO", "CFO", "User"], "duration": "2 hours"},
    importance=9
)

# Retrieve important events
events = memory.get_episodic_memories(min_importance=7, limit=10)
```

### 4. Semantic Memory

Stores facts and knowledge about the user and context.

**Features:**

- Category-based organization
- Confidence scoring
- Source tracking
- Unique key constraints

**Usage:**

```python
# Store fact
memory.add_semantic_memory(
    category="user_info",
    key="name",
    value="Ashish Manjhi",
    confidence=1.0,
    source="user_profile"
)

# Retrieve facts
user_info = memory.get_semantic_memory("user_info")
name = memory.get_semantic_memory("user_info", "name")
```

### 5. Procedural Memory

Stores learned patterns and workflows with usage statistics.

**Features:**

- Pattern storage
- Usage tracking
- Success rate calculation
- Last used timestamp

**Usage:**

```python
# Store pattern
memory.add_procedural_memory(
    pattern_name="email_response_template",
    pattern_data={
        "greeting": "Hello {name},",
        "body_structure": ["acknowledge", "respond", "action_items"],
        "closing": "Best regards"
    }
)

# Update usage
memory.update_procedural_usage("email_response_template", success=True)

# Retrieve pattern
pattern = memory.get_procedural_memory("email_response_template")
```

## Memory-Enhanced Agent

### Basic Usage

```python
from app.agents.memory_agent import create_memory_agent

# Create agent
agent = create_memory_agent(session_id="user_session_001")

# Process message with memory context
response = agent.process_message("What's my timezone?")
print(response)

# Learn preferences
agent.learn_preference("notification_time", "09:00 AM")

# Remember facts
agent.remember_fact(
    category="work_context",
    key="current_project",
    value="AI Executive Assistant"
)

# Record events
agent.record_event(
    event_type="milestone",
    description="Completed Phase 6 implementation",
    importance=8
)
```

### Advanced Features

#### Context Building

The agent automatically builds context from:

- User preferences
- Recent important events (episodic memory)
- Known facts (semantic memory)

```python
# Context is automatically included in responses
response = agent.process_message("What should I focus on today?")
# Agent uses preferences, recent events, and facts to provide personalized response
```

#### Session Management

```python
# Get session summary
summary = agent.get_session_summary()
print(f"Session: {summary['session_id']}")
print(f"Messages: {summary['message_count']}")

# Start new session
new_session_id = agent.new_session()

# Clear current session
agent.clear_session()
```

#### Memory Statistics

```python
# Get overall statistics
stats = agent.get_memory_stats()
print(f"Total messages: {stats['total_messages']}")
print(f"Total preferences: {stats['total_preferences']}")
```

## LangGraph Checkpointing

### Purpose

Enables conversation state persistence across sessions, allowing the agent to resume conversations exactly where they left off.

### Usage

```python
from app.memory.checkpointer import get_checkpointer
from app.agents.memory_agent import MemoryWorkflow, create_memory_agent

# Create workflow with checkpointing
agent = create_memory_agent()
workflow = MemoryWorkflow(memory_agent=agent)

# Invoke with thread_id for persistence
result = workflow.invoke(
    user_message="Hello!",
    thread_id="conversation_thread_001"
)

# Later, resume the same conversation
result = workflow.invoke(
    user_message="Continue from where we left off",
    thread_id="conversation_thread_001"  # Same thread_id
)
```

### Checkpoint Management

```python
from app.memory.checkpointer import PersistentCheckpointer

checkpointer = PersistentCheckpointer()

# Clear specific thread
checkpointer.clear_checkpoints(thread_id="conversation_thread_001")

# Clear all checkpoints
checkpointer.clear_checkpoints()
```

## Database Schema

### Tables

1. **conversations**
   - id, session_id, timestamp, role, content, metadata
   - Indexes: session_id, timestamp

2. **user_preferences**
   - key (PRIMARY KEY), value, updated_at

3. **episodic_memory**
   - id, timestamp, event_type, description, context, importance
   - Indexes: event_type, timestamp, importance

4. **semantic_memory**
   - id, category, key, value, confidence, source, created_at, updated_at
   - Unique: (category, key)
   - Index: category

5. **procedural_memory**
   - id, pattern_name (UNIQUE), pattern_data, usage_count, success_rate, last_used, created_at

### Database Locations

- **Memory Store**: `data/memory.db`
- **Checkpoints**: `data/checkpoints.db`

## Testing

### Run Complete Test Suite

```bash
python test_memory_system.py
```

### Test Coverage

The test suite validates:

1. ✅ Memory Store initialization
2. ✅ User Preferences (set/get)
3. ✅ Episodic Memory (add/retrieve)
4. ✅ Semantic Memory (store/query)
5. ✅ Procedural Memory (patterns/usage)
6. ✅ Conversation History
7. ✅ Memory-Enhanced Agent
8. ✅ Cross-Session Persistence
9. ✅ Memory Statistics

### Expected Output

```
============================================================
  TEST SUMMARY
============================================================

[SUCCESS] All tests completed successfully!

Memory System Features Tested:
  [OK] Memory Store (SQLite-based)
  [OK] User Preferences
  [OK] Episodic Memory (Events)
  [OK] Semantic Memory (Facts)
  [OK] Procedural Memory (Patterns)
  [OK] Conversation History
  [OK] Memory-Enhanced Agent
  [OK] Cross-Session Persistence
  [OK] Memory Statistics
```

## Integration Examples

### Example 1: Email Assistant with Memory

```python
from app.agents.memory_agent import create_memory_agent

agent = create_memory_agent(session_id="email_assistant")

# First interaction
agent.learn_preference("email_style", "professional")
agent.remember_fact("user_info", "role", "Software Engineer")

response = agent.process_message("Draft an email to my team about the project update")
# Agent uses learned preferences and facts

# Later interaction (same or different session)
response = agent.process_message("Send a similar email to the client")
# Agent remembers previous context and preferences
```

### Example 2: Learning from Interactions

```python
agent = create_memory_agent()

# User provides feedback
agent.process_message("I prefer shorter summaries")
agent.learn_preference("summary_length", "short")

# Record successful interaction
agent.record_event(
    event_type="successful_task",
    description="User satisfied with email draft",
    importance=6
)

# Future interactions use this learning
response = agent.process_message("Summarize my emails")
# Agent provides shorter summary based on learned preference
```

### Example 3: Multi-Session Continuity

```python
# Session 1
agent1 = create_memory_agent(session_id="morning_session")
agent1.process_message("I need to prepare for the 2 PM meeting")
agent1.remember_fact("schedule", "next_meeting", "2 PM with CEO")

# Session 2 (later, different agent instance)
agent2 = create_memory_agent(session_id="afternoon_session")
response = agent2.process_message("What's my next meeting?")
# Agent retrieves fact from memory: "2 PM with CEO"
```

## Best Practices

### 1. Session Management

- Use meaningful session IDs (e.g., "user_123_2024_06_17")
- Create new sessions for distinct conversations
- Clear sessions when appropriate

### 2. Memory Organization

- Use consistent category names for semantic memory
- Set appropriate importance levels for episodic memory
- Update procedural memory usage statistics

### 3. Performance

- Limit conversation history retrieval (use `limit` parameter)
- Filter episodic memories by importance
- Index frequently queried fields

### 4. Data Privacy

- Store sensitive data encrypted if needed
- Implement data retention policies
- Provide user data export/deletion capabilities

## Troubleshooting

### Issue: Database locked

**Solution**: Ensure only one connection writes at a time, or use WAL mode:

```python
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA journal_mode=WAL")
```

### Issue: Memory growing too large

**Solution**: Implement cleanup routines:

```python
# Delete old conversations
cursor.execute("""
    DELETE FROM conversations
    WHERE timestamp < datetime('now', '-30 days')
""")

# Archive low-importance episodic memories
cursor.execute("""
    DELETE FROM episodic_memory
    WHERE importance < 5 AND timestamp < datetime('now', '-7 days')
""")
```

### Issue: Slow queries

**Solution**: Ensure indexes are created and analyze query plans:

```python
cursor.execute("ANALYZE")
cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE session_id = ?")
```

## Future Enhancements

Potential improvements for Phase 6:

1. **Vector-based Memory Search**
   - Semantic search across all memory types
   - Similar conversation retrieval

2. **Memory Consolidation**
   - Automatic summarization of old conversations
   - Pattern extraction from episodic memories

3. **Multi-User Support**
   - User-specific memory isolation
   - Shared organizational memory

4. **Memory Analytics**
   - Usage patterns visualization
   - Memory effectiveness metrics

5. **Advanced Checkpointing**
   - Branching conversations
   - Time-travel debugging

## Dependencies

```
langgraph>=1.2.5
langgraph-checkpoint-sqlite>=3.1.0
aiosqlite>=0.22.1
langchain-core>=1.4.7
```

## Files Created

- `app/memory/memory_store.py` - Core memory storage system
- `app/memory/checkpointer.py` - LangGraph checkpoint integration
- `app/memory/__init__.py` - Memory module exports
- `app/agents/memory_agent.py` - Memory-enhanced agent
- `test_memory_system.py` - Comprehensive test suite
- `PHASE6_MEMORY_GUIDE.md` - This guide

## Conclusion

Phase 6 provides a robust foundation for persistent memory in the AI Executive Assistant. The system enables:

- ✅ Long-term conversation continuity
- ✅ User preference learning
- ✅ Event and fact tracking
- ✅ Pattern recognition and reuse
- ✅ Cross-session context preservation

The memory system integrates seamlessly with existing agents and workflows, enhancing the assistant's ability to provide personalized, context-aware assistance.

---

**Next Phase**: Phase 7 - Scheduled Autonomous Jobs (See FUTURE_PHASES_ROADMAP.md)
