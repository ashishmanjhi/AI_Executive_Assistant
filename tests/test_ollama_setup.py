"""
Test Ollama Setup with qwen3:4b

Quick test to verify your Ollama configuration is working correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_ollama_connection():
    """Test 1: Verify Ollama is running"""
    print("\n" + "="*60)
    print("TEST 1: Ollama Connection")
    print("="*60)
    
    try:
        import requests
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{base_url}/api/tags")
        
        if response.status_code == 200:
            print(f"[OK] Ollama is running at {base_url}")
            models = response.json().get("models", [])
            print(f"[OK] Found {len(models)} models:")
            for model in models:
                print(f"   - {model['name']} ({model['size'] // (1024*1024)} MB)")
            return True
        else:
            print(f"[FAIL] Ollama returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to Ollama: {e}")
        print("\nTo fix:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Verify it's running: curl http://localhost:11434/api/tags")
        return False


def test_llm_config():
    """Test 2: Verify LLM configuration"""
    print("\n" + "="*60)
    print("TEST 2: LLM Configuration")
    print("="*60)
    
    try:
        from app.config.llm_config import get_llm_info
        
        info = get_llm_info()
        print(f"[OK] Provider: {info['provider']}")
        print(f"[OK] Model: {info['model']}")
        print(f"[OK] Temperature: {info['temperature']}")
        print(f"[OK] Max Tokens: {info['max_tokens']}")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        return False


def test_basic_query():
    """Test 3: Run a basic query"""
    print("\n" + "="*60)
    print("TEST 3: Basic Query")
    print("="*60)
    
    try:
        from app.config.llm_config import create_llm
        
        print("Creating LLM instance...")
        llm = create_llm()
        
        print("Sending test query...")
        query = "What is 2+2? Answer in one word."
        response = llm.invoke(query)
        
        print(f"[OK] Query: {query}")
        print(f"[OK] Response: {response.content}")
        return True
    except Exception as e:
        print(f"[FAIL] Query failed: {e}")
        return False


def test_email_summary():
    """Test 4: Test email summarization"""
    print("\n" + "="*60)
    print("TEST 4: Email Summarization")
    print("="*60)
    
    try:
        from app.config.llm_config import create_llm
        
        llm = create_llm()
        
        email_text = """
        From: john@example.com
        Subject: Project Update
        
        Hi team,
        
        The project is progressing well. We've completed the first phase
        and are moving into testing. The deadline is next Friday.
        Please review the attached documents and provide feedback by Wednesday.
        
        Thanks,
        John
        """
        
        query = f"Summarize this email in one sentence:\n\n{email_text}"
        print("Summarizing test email...")
        response = llm.invoke(query)
        
        print(f"[OK] Summary: {response.content}")
        return True
    except Exception as e:
        print(f"[FAIL] Summarization failed: {e}")
        return False


def test_cost_tracking():
    """Test 5: Verify cost tracking (should be $0 for Ollama)"""
    print("\n" + "="*60)
    print("TEST 5: Cost Tracking")
    print("="*60)
    
    try:
        from app.config.llm_config import create_llm, track_usage, get_usage_stats, reset_usage_stats
        
        reset_usage_stats()
        llm = create_llm()
        
        # Make a few requests
        queries = [
            "What is AI?",
            "What is machine learning?",
            "What is deep learning?"
        ]
        
        print(f"Making {len(queries)} test queries...")
        for query in queries:
            response = llm.invoke(query)
            cost = track_usage(response)
            print(f"  - Query cost: ${cost:.6f}")
        
        stats = get_usage_stats()
        print(f"\n[OK] Total cost: ${stats['total_cost_usd']:.4f} (Should be $0.00 for Ollama)")
        print(f"[OK] Total tokens: {stats['total_tokens']:,}")
        return True
    except Exception as e:
        print(f"[FAIL] Cost tracking failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("OLLAMA SETUP TEST - qwen3:4b")
    print("="*80)
    
    print("\nTesting your Ollama configuration with qwen3:4b model...")
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("LLM Configuration", test_llm_config),
        ("Basic Query", test_basic_query),
        ("Email Summarization", test_email_summary),
        ("Cost Tracking", test_cost_tracking)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Your Ollama setup is working perfectly!")
        print("\nYou can now:")
        print("  1. Run the Streamlit UI: streamlit run app_ui.py")
        print("  2. Test the system: python example_llm_usage.py")
        print("  3. Start building with Phase 6: Persistent Memory")
    else:
        print("\n[WARNING] Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Verify model: ollama list")
        print("  3. Check .env file has: OLLAMA_MODEL=qwen3:4b")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

# Made with Bob
