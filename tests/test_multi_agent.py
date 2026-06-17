"""
Test Multi-Agent System

Tests the multi-agent workflow with supervisor coordination.
"""

import os
from dotenv import load_dotenv
from app.graph.multi_agent_workflow import (
    create_multi_agent_system,
    run_multi_agent_query,
    run_multi_agent_conversation,
    get_multi_agent_info
)
from app.agents.supervisor_agent import route_query, create_supervisor_agent

# Load environment variables
load_dotenv()


def test_supervisor_routing():
    """Test supervisor routing logic"""
    print("\n" + "="*80)
    print("TEST 1: Supervisor Routing")
    print("="*80)
    
    supervisor_llm = create_supervisor_agent()
    
    test_queries = [
        "Show me my unread emails",
        "What did John say about the project deadline?",
        "Draft an email to Sarah about the meeting",
        "Search for emails about budget approval",
        "What are the action items from yesterday's emails?",
        "Send a reply to the latest email from Mike"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        routing = route_query(supervisor_llm, query)
        print(f"  -> Routed to: {routing['agent']}")
        print(f"  -> Reason: {routing['reason']}")
        print(f"  -> Context: {routing.get('context', 'N/A')}")


def test_email_agent_queries():
    """Test queries that should route to email agent"""
    print("\n" + "="*80)
    print("TEST 2: Email Agent Queries")
    print("="*80)
    
    workflow = create_multi_agent_system()
    
    email_queries = [
        "Show me my latest 3 emails",
        "Search for emails from john@example.com",
        "Summarize my unread emails"
    ]
    
    for query in email_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        try:
            response = run_multi_agent_query(query, workflow)
            print(f"\nResponse:\n{response}")
        except Exception as e:
            print(f"Error: {e}")


def test_knowledge_agent_queries():
    """Test queries that should route to knowledge agent"""
    print("\n" + "="*80)
    print("TEST 3: Knowledge Agent Queries")
    print("="*80)
    
    workflow = create_multi_agent_system()
    
    knowledge_queries = [
        "What did Sarah say about the budget?",
        "Find emails discussing project deadlines",
        "What are the action items from recent emails?"
    ]
    
    for query in knowledge_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        try:
            response = run_multi_agent_query(query, workflow)
            print(f"\nResponse:\n{response}")
        except Exception as e:
            print(f"Error: {e}")


def test_multi_turn_conversation():
    """Test multi-turn conversation with context"""
    print("\n" + "="*80)
    print("TEST 4: Multi-Turn Conversation")
    print("="*80)
    
    workflow = create_multi_agent_system()
    
    conversation = [
        "Show me emails from last week",
        "What did they say about the project?",
        "Draft a reply to the most recent one"
    ]
    
    print("\nStarting conversation...")
    for i, query in enumerate(conversation, 1):
        print(f"\n{'='*60}")
        print(f"Turn {i}: {query}")
        print('='*60)
        
        try:
            response = run_multi_agent_query(query, workflow)
            print(f"\nResponse:\n{response[:200]}...")
        except Exception as e:
            print(f"Error: {e}")


def test_system_info():
    """Test system information retrieval"""
    print("\n" + "="*80)
    print("TEST 5: System Information")
    print("="*80)
    
    info = get_multi_agent_info()
    print(f"\n{info}")


def test_interactive_mode():
    """Test interactive conversation mode"""
    print("\n" + "="*80)
    print("TEST 6: Interactive Mode (Demo)")
    print("="*80)
    
    print("\nInteractive mode allows continuous conversation.")
    print("Example usage:")
    print("  workflow = create_multi_agent_system()")
    print("  run_multi_agent_conversation(workflow)")
    print("\nThis would start an interactive session where you can:")
    print("  - Ask questions about emails")
    print("  - Search and retrieve information")
    print("  - Draft and send emails")
    print("  - Get summaries and action items")
    print("\nType 'quit' or 'exit' to end the session.")


def test_agent_specialization():
    """Test that agents handle their specialized domains correctly"""
    print("\n" + "="*80)
    print("TEST 7: Agent Specialization")
    print("="*80)
    
    workflow = create_multi_agent_system()
    supervisor_llm = create_supervisor_agent()
    
    test_cases = [
        {
            "query": "Read my latest email",
            "expected_agent": "email",
            "description": "Email operations should route to email agent"
        },
        {
            "query": "What did the CEO say about Q4 targets?",
            "expected_agent": "knowledge",
            "description": "Q&A should route to knowledge agent"
        },
        {
            "query": "Draft a meeting invite",
            "expected_agent": "email",
            "description": "Drafting should route to email agent"
        },
        {
            "query": "Extract action items from today's emails",
            "expected_agent": "knowledge",
            "description": "Action item extraction should route to knowledge agent"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test['description']}")
        print(f"Query: {test['query']}")
        print(f"Expected Agent: {test['expected_agent']}")
        print('='*60)
        
        try:
            # Get routing decision from supervisor
            routing = route_query(supervisor_llm, test['query'])
            actual_agent = routing['agent']
            
            if actual_agent == test['expected_agent']:
                print(f"✓ PASS: Correctly routed to {actual_agent} agent")
            else:
                print(f"✗ FAIL: Expected {test['expected_agent']}, got {actual_agent}")
            
            # Get actual response
            response = run_multi_agent_query(test['query'], workflow)
            print(f"\nResponse preview:\n{response[:150]}...")
        except Exception as e:
            print(f"✗ ERROR: {e}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("MULTI-AGENT SYSTEM TEST SUITE")
    print("="*80)
    
    tests = [
        ("Supervisor Routing", test_supervisor_routing),
        ("Email Agent Queries", test_email_agent_queries),
        ("Knowledge Agent Queries", test_knowledge_agent_queries),
        ("Multi-Turn Conversation", test_multi_turn_conversation),
        ("System Information", test_system_info),
        ("Interactive Mode Demo", test_interactive_mode),
        ("Agent Specialization", test_agent_specialization)
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        test_map = {
            "routing": test_supervisor_routing,
            "email": test_email_agent_queries,
            "knowledge": test_knowledge_agent_queries,
            "conversation": test_multi_turn_conversation,
            "info": test_system_info,
            "interactive": test_interactive_mode,
            "specialization": test_agent_specialization,
            "all": run_all_tests
        }
        
        if test_name in test_map:
            test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        # Run all tests by default
        run_all_tests()

# Made with Bob
