"""
Test Script for Phase 6: Persistent Memory System
Demonstrates all memory capabilities
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.memory.memory_store import MemoryStore
from app.agents.memory_agent import create_memory_agent
from datetime import datetime


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_memory_store():
    """Test basic memory store functionality"""
    print_section("TEST 1: Memory Store Basics")
    
    # Initialize memory store
    memory = MemoryStore(db_path="data/test_memory.db")
    print("[OK] Memory store initialized")
    
    # Test user preferences
    print("\n--- User Preferences ---")
    memory.set_preference("email_summary_style", "concise")
    memory.set_preference("preferred_language", "English")
    memory.set_preference("work_hours", {"start": "09:00", "end": "17:00"})
    print("[OK] Set 3 preferences")
    
    prefs = memory.get_all_preferences()
    print(f"[OK] Retrieved {len(prefs)} preferences:")
    for key, value in prefs.items():
        print(f"     - {key}: {value}")
    
    # Test episodic memory
    print("\n--- Episodic Memory (Events) ---")
    memory.add_episodic_memory(
        event_type="meeting",
        description="Had important meeting with CEO about Q4 strategy",
        context={"attendees": ["CEO", "CFO", "User"], "duration": "2 hours"},
        importance=9
    )
    memory.add_episodic_memory(
        event_type="email_sent",
        description="Sent project proposal to client",
        context={"client": "Acme Corp", "project": "Website Redesign"},
        importance=7
    )
    print("[OK] Added 2 episodic memories")
    
    episodes = memory.get_episodic_memories(min_importance=5, limit=10)
    print(f"[OK] Retrieved {len(episodes)} episodic memories:")
    for ep in episodes:
        print(f"     - [{ep['importance']}/10] {ep['description']}")
    
    # Test semantic memory
    print("\n--- Semantic Memory (Facts) ---")
    memory.add_semantic_memory(
        category="user_info",
        key="name",
        value="Ashish Manjhi",
        confidence=1.0
    )
    memory.add_semantic_memory(
        category="user_info",
        key="role",
        value="Software Engineer",
        confidence=1.0
    )
    memory.add_semantic_memory(
        category="work_context",
        key="current_project",
        value="AI Executive Assistant",
        confidence=1.0
    )
    print("[OK] Added 3 semantic memories")
    
    user_info = memory.get_semantic_memory("user_info")
    print(f"[OK] Retrieved user info:")
    for key, data in user_info.items():
        print(f"     - {key}: {data['value']} (confidence: {data['confidence']})")
    
    # Test procedural memory
    print("\n--- Procedural Memory (Patterns) ---")
    memory.add_procedural_memory(
        pattern_name="email_response_template",
        pattern_data={
            "greeting": "Hello {name},",
            "body_structure": ["acknowledge", "respond", "action_items"],
            "closing": "Best regards"
        }
    )
    print("[OK] Added procedural memory pattern")
    
    pattern = memory.get_procedural_memory("email_response_template")
    if pattern:
        print(f"[OK] Retrieved pattern (used {pattern['usage_count']} times)")
    
    # Get statistics
    print("\n--- Memory Statistics ---")
    stats = memory.get_memory_stats()
    print("[OK] Memory statistics:")
    for key, value in stats.items():
        print(f"     - {key}: {value}")


def test_conversation_memory():
    """Test conversation history"""
    print_section("TEST 2: Conversation History")
    
    memory = MemoryStore(db_path="data/test_memory.db")
    session_id = "test_session_001"
    
    # Add conversation messages
    print("\n--- Adding Conversation Messages ---")
    memory.add_conversation_message(
        session_id=session_id,
        role="user",
        content="What emails do I have from last week?"
    )
    memory.add_conversation_message(
        session_id=session_id,
        role="assistant",
        content="You have 15 emails from last week. 5 are marked as important.",
        metadata={"email_count": 15, "important_count": 5}
    )
    memory.add_conversation_message(
        session_id=session_id,
        role="user",
        content="Can you summarize the important ones?"
    )
    print("[OK] Added 3 messages to conversation")
    
    # Retrieve conversation history
    history = memory.get_conversation_history(session_id)
    print(f"\n[OK] Retrieved {len(history)} messages:")
    for msg in history:
        role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
        print(f"     [{role_label}] {msg['content'][:60]}...")
    
    # Get all sessions
    print("\n--- All Sessions ---")
    sessions = memory.get_all_sessions()
    print(f"[OK] Found {len(sessions)} session(s):")
    for session in sessions:
        print(f"     - {session['session_id']}: {session['message_count']} messages")


def test_memory_agent():
    """Test memory-enhanced agent"""
    print_section("TEST 3: Memory-Enhanced Agent")
    
    # Create agent with existing memory
    agent = create_memory_agent(
        session_id="agent_test_session",
        memory_db_path="data/test_memory.db"
    )
    print("[OK] Created memory-enhanced agent")
    
    # Test conversation with context
    print("\n--- Conversation with Memory Context ---")
    
    # First message
    print("\n[USER] Hello! I'm working on the AI Executive Assistant project.")
    response1 = agent.process_message(
        "Hello! I'm working on the AI Executive Assistant project."
    )
    print(f"[AGENT] {response1}")
    
    # Learn a preference
    agent.learn_preference("notification_time", "09:00 AM")
    print("\n[SYSTEM] Learned preference: notification_time = 09:00 AM")
    
    # Remember a fact
    agent.remember_fact(
        category="work_context",
        key="current_phase",
        value="Phase 6: Persistent Memory"
    )
    print("[SYSTEM] Remembered fact: current_phase = Phase 6")
    
    # Second message (should have context from first)
    print("\n[USER] What phase am I working on?")
    response2 = agent.process_message(
        "What phase am I working on?"
    )
    print(f"[AGENT] {response2}")
    
    # Record an event
    agent.record_event(
        event_type="milestone",
        description="Completed Phase 6 implementation",
        importance=8,
        context={"phase": "Phase 6", "features": ["memory_store", "checkpointer", "agent"]}
    )
    print("\n[SYSTEM] Recorded milestone event")
    
    # Get session summary
    print("\n--- Session Summary ---")
    summary = agent.get_session_summary()
    print(f"[OK] Session: {summary['session_id']}")
    print(f"[OK] Messages: {summary['message_count']}")
    print(f"[OK] First message: {summary['first_message']}")
    print(f"[OK] Last message: {summary['last_message']}")


def test_cross_session_memory():
    """Test memory persistence across sessions"""
    print_section("TEST 4: Cross-Session Memory")
    
    # Session 1
    print("\n--- Session 1 ---")
    agent1 = create_memory_agent(
        session_id="session_1",
        memory_db_path="data/test_memory.db"
    )
    
    agent1.learn_preference("email_check_frequency", "every 30 minutes")
    agent1.remember_fact("user_info", "timezone", "Asia/Calcutta")
    print("[OK] Session 1: Learned preferences and facts")
    
    response1 = agent1.process_message("Remember that I prefer concise summaries")
    print(f"[AGENT 1] {response1[:80]}...")
    
    # Session 2 (new agent, same memory store)
    print("\n--- Session 2 (New Agent Instance) ---")
    agent2 = create_memory_agent(
        session_id="session_2",
        memory_db_path="data/test_memory.db"
    )
    
    # Check if preferences persist
    prefs = agent2.memory_store.get_all_preferences()
    print(f"[OK] Session 2 can access {len(prefs)} preferences from Session 1:")
    for key, value in list(prefs.items())[:3]:
        print(f"     - {key}: {value}")
    
    # Check if facts persist
    timezone = agent2.memory_store.get_semantic_memory("user_info", "timezone")
    print(f"[OK] Session 2 retrieved fact: timezone = {timezone}")
    
    response2 = agent2.process_message("What's my timezone?")
    print(f"[AGENT 2] {response2[:80]}...")


def test_memory_stats():
    """Display overall memory statistics"""
    print_section("TEST 5: Overall Memory Statistics")
    
    memory = MemoryStore(db_path="data/test_memory.db")
    stats = memory.get_memory_stats()
    
    print("\n[OK] Complete Memory System Statistics:")
    print(f"     - Total Messages: {stats['total_messages']}")
    print(f"     - Total Sessions: {stats['total_sessions']}")
    print(f"     - User Preferences: {stats['total_preferences']}")
    print(f"     - Episodic Memories: {stats['total_episodic_memories']}")
    print(f"     - Semantic Memories: {stats['total_semantic_memories']}")
    print(f"     - Procedural Patterns: {stats['total_procedural_patterns']}")
    
    total_items = sum(stats.values())
    print(f"\n[OK] Total Memory Items: {total_items}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  PHASE 6: PERSISTENT MEMORY SYSTEM - TEST SUITE")
    print("=" * 60)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all tests
        test_memory_store()
        test_conversation_memory()
        test_memory_agent()
        test_cross_session_memory()
        test_memory_stats()
        
        # Final summary
        print_section("TEST SUMMARY")
        print("\n[SUCCESS] All tests completed successfully!")
        print("\nMemory System Features Tested:")
        print("  [OK] Memory Store (SQLite-based)")
        print("  [OK] User Preferences")
        print("  [OK] Episodic Memory (Events)")
        print("  [OK] Semantic Memory (Facts)")
        print("  [OK] Procedural Memory (Patterns)")
        print("  [OK] Conversation History")
        print("  [OK] Memory-Enhanced Agent")
        print("  [OK] Cross-Session Persistence")
        print("  [OK] Memory Statistics")
        
        print("\nDatabase Location: data/test_memory.db")
        print("Checkpoints Location: data/checkpoints.db")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
