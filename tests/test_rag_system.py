"""
Test script for RAG system
"""

import os
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['OLLAMA_MODEL'] = 'qwen3:4b'

print("=" * 60)
print("RAG System Test")
print("=" * 60)

# Test 1: Import modules
print("\n1. Testing module imports...")
try:
    from app.rag import EmailStore, VectorSearch, EmailRetriever
    from app.tools.rag_tools import RAG_TOOLS
    print("   [OK] All modules imported successfully")
    print(f"   [OK] {len(RAG_TOOLS)} RAG tools loaded")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    exit(1)

# Test 2: Initialize components
print("\n2. Testing component initialization...")
try:
    email_store = EmailStore(
        persist_directory="./test_chromadb",
        collection_name="test_emails"
    )
    print("   [OK] EmailStore initialized")
    
    vector_search = VectorSearch(email_store)
    print("   [OK] VectorSearch initialized")
    
    retriever = EmailRetriever(vector_search)
    print("   [OK] EmailRetriever initialized")
except Exception as e:
    print(f"   [FAIL] Initialization failed: {e}")
    exit(1)

# Test 3: Store test email
print("\n3. Testing email storage...")
try:
    test_email = {
        'id': 'test_001',
        'subject': 'Project Deployment Schedule',
        'from': 'client@example.com',
        'to': 'me@example.com',
        'date': '2024-06-15T10:00:00Z',
        'body': 'We need to deploy the project by Friday, June 21st. Please ensure all testing is completed by Wednesday.',
        'thread_id': 'thread_001'
    }
    
    success = email_store.store_email(test_email)
    if success:
        print("   [OK] Test email stored successfully")
        print(f"   [OK] Total emails in store: {email_store.count_emails()}")
    else:
        print("   [FAIL] Failed to store email")
except Exception as e:
    print(f"   [FAIL] Storage failed: {e}")

# Test 4: Search functionality
print("\n4. Testing semantic search...")
try:
    results = vector_search.search("deployment deadline", n_results=1)
    if results:
        print(f"   [OK] Found {len(results)} result(s)")
        print(f"   [OK] Similarity score: {results[0].get('similarity', 0):.2%}")
    else:
        print("   [FAIL] No results found")
except Exception as e:
    print(f"   [FAIL] Search failed: {e}")

# Test 5: RAG question answering
print("\n5. Testing RAG question answering...")
try:
    answer = retriever.answer_question("When is the deployment deadline?")
    print("   [OK] Answer generated:")
    print(f"   {answer[:200]}..." if len(answer) > 200 else f"   {answer}")
except Exception as e:
    print(f"   [FAIL] RAG failed: {e}")

# Test 6: Tool integration
print("\n6. Testing tool integration...")
try:
    from app.agents.email_agent import ALL_TOOLS
    print(f"   [OK] Total tools available: {len(ALL_TOOLS)}")
    
    rag_tool_names = [
        'search_email_history',
        'answer_from_emails',
        'store_recent_emails',
        'find_action_items_from_emails',
        'search_emails_by_sender'
    ]
    
    loaded_tools = [tool.name for tool in ALL_TOOLS]
    for tool_name in rag_tool_names:
        if tool_name in loaded_tools:
            print(f"   [OK] {tool_name} loaded")
        else:
            print(f"   [FAIL] {tool_name} missing")
            
except Exception as e:
    print(f"   [FAIL] Tool integration failed: {e}")

# Cleanup
print("\n7. Cleaning up test data...")
try:
    import shutil
    if os.path.exists("./test_chromadb"):
        shutil.rmtree("./test_chromadb")
        print("   [OK] Test database cleaned up")
except Exception as e:
    print(f"   [FAIL] Cleanup failed: {e}")

print("\n" + "=" * 60)
print("RAG System Test Complete!")
print("=" * 60)

# Made with Bob
