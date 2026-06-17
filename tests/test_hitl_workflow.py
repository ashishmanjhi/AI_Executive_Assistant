"""
Test script for Human-in-the-Loop (HITL) workflow
"""

import os
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['OLLAMA_MODEL'] = 'qwen3:4b'

print("=" * 60)
print("HITL Workflow Test")
print("=" * 60)

# Test 1: Import modules
print("\n1. Testing module imports...")
try:
    from app.graph import (
        create_hitl_workflow,
        run_hitl_workflow_interactive,
        EmailDraftState,
        create_email_draft_state
    )
    print("   [OK] All HITL modules imported successfully")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    exit(1)

# Test 2: Create workflow
print("\n2. Testing workflow creation...")
try:
    workflow = create_hitl_workflow()
    print("   [OK] HITL workflow created successfully")
except Exception as e:
    print(f"   [FAIL] Workflow creation failed: {e}")
    exit(1)

# Test 3: Create initial state
print("\n3. Testing state creation...")
try:
    state = create_email_draft_state(
        user_request="Send a thank you email to John for the meeting",
        recipient="john@example.com",
        subject="Thank You",
        body=""
    )
    print("   [OK] Email draft state created")
    print(f"   [OK] Draft ID: {state['draft_id']}")
    print(f"   [OK] Status: {state['status']}")
except Exception as e:
    print(f"   [FAIL] State creation failed: {e}")
    exit(1)

# Test 4: Test draft generation node
print("\n4. Testing draft generation...")
try:
    from app.graph.nodes import generate_draft_node
    
    test_state = create_email_draft_state(
        user_request="Write a professional email thanking the client for their business",
        recipient="client@example.com",
        subject="Thank You for Your Business",
        body=""
    )
    
    result_state = generate_draft_node(test_state)
    
    if result_state['body'] and len(result_state['body']) > 0:
        print("   [OK] Draft generated successfully")
        print(f"   [OK] Draft length: {len(result_state['body'])} characters")
        print(f"   [OK] Status: {result_state['status']}")
    else:
        print("   [FAIL] Draft body is empty")
        
except Exception as e:
    print(f"   [FAIL] Draft generation failed: {e}")

# Test 5: Test email sender module
print("\n5. Testing email sender module...")
try:
    from app.gmail.email_sender import (
        create_message,
        format_email_preview,
        validate_email_address
    )
    
    # Test email validation
    assert validate_email_address("test@example.com") == True
    assert validate_email_address("invalid-email") == False
    print("   [OK] Email validation working")
    
    # Test message creation
    message = create_message(
        to="test@example.com",
        subject="Test",
        body="This is a test email"
    )
    assert 'raw' in message
    print("   [OK] Message creation working")
    
    # Test preview formatting
    preview = format_email_preview(
        to="test@example.com",
        subject="Test",
        body="This is a test email"
    )
    assert "To: test@example.com" in preview
    print("   [OK] Preview formatting working")
    
except Exception as e:
    print(f"   [FAIL] Email sender test failed: {e}")

# Test 6: Test draft tools
print("\n6. Testing draft tools...")
try:
    from app.tools.draft_tools import DRAFT_TOOLS
    
    print(f"   [OK] {len(DRAFT_TOOLS)} draft tools loaded")
    for tool in DRAFT_TOOLS:
        print(f"   [OK] - {tool.name}")
        
except Exception as e:
    print(f"   [FAIL] Draft tools test failed: {e}")

# Test 7: Integration test
print("\n7. Testing workflow integration...")
try:
    from app.tools import DRAFT_TOOLS
    from app.agents.email_agent import ALL_TOOLS
    
    # Check if draft tools are available
    draft_tool_names = [tool.name for tool in DRAFT_TOOLS]
    all_tool_names = [tool.name for tool in ALL_TOOLS]
    
    print(f"   [OK] Total tools available: {len(ALL_TOOLS)}")
    print(f"   [OK] Draft tools: {len(DRAFT_TOOLS)}")
    
    # Note: Draft tools are separate from agent tools for now
    # They will be integrated in the HITL workflow
    
except Exception as e:
    print(f"   [FAIL] Integration test failed: {e}")

print("\n" + "=" * 60)
print("HITL Workflow Test Complete!")
print("=" * 60)

print("\n" + "=" * 60)
print("INTERACTIVE TEST")
print("=" * 60)
print("\nTo test the interactive HITL workflow, run:")
print("\n  python -c \"from app.graph import run_hitl_workflow_interactive; \\")
print("             run_hitl_workflow_interactive(")
print("                 user_request='Thank the client for the meeting',")
print("                 recipient='client@example.com',")
print("                 subject='Thank You'")
print("             )\"")
print("\nThis will:")
print("  1. Generate an email draft")
print("  2. Show it to you for approval")
print("  3. Wait for your decision (approve/reject/cancel)")
print("  4. Send the email if approved")
print("=" * 60)

# Made with Bob
