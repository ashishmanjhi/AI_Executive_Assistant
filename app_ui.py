"""
Comprehensive Streamlit UI for AI Executive Assistant - All 12 Phases
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, cast
from datetime import datetime, timedelta

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

# Phase 1-5 imports
from app.agents.supervisor_agent import create_supervisor_agent, route_query
from app.graph.email_workflow import create_email_workflow
from app.graph.multi_agent_workflow import create_multi_agent_system
from app.graph.nodes import generate_draft_node, regenerate_draft_node, send_email_node
from app.graph.state import create_email_draft_state
from app.gmail.auth import test_authentication
from app.tools.email_tools import (
    generate_daily_digest,
    get_recent_emails,
    search_emails,
    summarize_emails,
)
from app.tools.rag_tools import (
    answer_from_emails,
    find_action_items_from_emails,
    search_email_history,
    search_emails_by_sender,
    store_recent_emails,
)

# Phase 6-12 imports
try:
    from app.memory import MemoryStore
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from app.scheduler import JobScheduler, create_scheduler, get_scheduler, register_default_jobs
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

try:
    from app.planning import TaskPlanner, PlanStore, PlanStatus, StepStatus
    PLANNING_AVAILABLE = True
except ImportError:
    PLANNING_AVAILABLE = False

try:
    from app.calendar.calendar_manager import CalendarManager
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

try:
    from app.observability import MetricsCollector, StructuredLogger, HealthChecker
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

try:
    from app.analytics import EmailAnalyzer, RelationshipTracker, InsightsGenerator, AnalyticsStore
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

try:
    from app.evaluation import TestRunner, MetricsCalculator, LLMEvaluator, EvaluationStore
    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False

load_dotenv()

st.set_page_config(
    page_title="AI Executive Assistant - Complete UI (12 Phases)",
    page_icon="📬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.main-title {font-size: 2.2rem; font-weight: 700; color: #1f4e79; margin-bottom: 0.2rem;}
.subtle-text {color: #6b7280; margin-bottom: 1rem;}
.metric-card {background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f4e79;}
.phase-badge {display: inline-block; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; font-weight: 600;}
.phase-available {background: #d1fae5; color: #065f46;}
.phase-unavailable {background: #fee2e2; color: #991b1b;}
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    defaults = {
        "page": "Overview",
        "gmail_status": None,
        "email_history": [],
        "rag_history": [],
        "multi_agent_history": [],
        "conversation_history": [],
        "pending_draft": None,
        "draft_history": [],
        "supervisor_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_resource(show_spinner=False)
def get_cached_email_agent():
    return create_email_workflow()


@st.cache_resource(show_spinner=False)
def get_cached_multi_agent_app():
    return create_multi_agent_system()


@st.cache_resource(show_spinner=False)
def get_cached_supervisor_llm():
    return create_supervisor_agent()


def add_history(category: str, payload: dict[str, Any]) -> None:
    st.session_state[category].insert(0, payload)
    st.session_state.conversation_history.insert(0, {"category": category, **payload})


def render_phase_badge(available: bool, phase_name: str) -> str:
    """Render a phase availability badge"""
    status_class = "phase-available" if available else "phase-unavailable"
    status_text = "✓ Available" if available else "✗ Not Installed"
    return f'<span class="phase-badge {status_class}">{phase_name}: {status_text}</span>'


def render_header() -> None:
    st.markdown('<div class="main-title">📬 AI Executive Assistant - Complete Test Console</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtle-text">Comprehensive Streamlit interface for all 12 phases</div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.title("Navigation")
        
        # Core phases (always available)
        core_pages = [
            "Overview",
            "Gmail Connection",
            "Email Operations",
            "RAG System",
            "Drafting & HITL",
            "Multi-Agent System",
        ]
        
        # Advanced phases (conditional)
        advanced_pages = []
        if MEMORY_AVAILABLE:
            advanced_pages.append("Memory System")
        if SCHEDULER_AVAILABLE:
            advanced_pages.append("Scheduler")
        if PLANNING_AVAILABLE:
            advanced_pages.append("Planning")
        if CALENDAR_AVAILABLE:
            advanced_pages.append("Calendar")
        if OBSERVABILITY_AVAILABLE:
            advanced_pages.append("Observability")
        if ANALYTICS_AVAILABLE:
            advanced_pages.append("Analytics")
        if EVALUATION_AVAILABLE:
            advanced_pages.append("Evaluation")
        
        advanced_pages.append("History & Session")
        
        all_pages = core_pages + advanced_pages
        
        page = st.radio("Go to", all_pages, index=all_pages.index(st.session_state.page) if st.session_state.page in all_pages else 0)
        st.session_state.page = page

        st.divider()
        st.subheader("Environment")
        st.caption(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'ollama')}")
        st.caption(f"Model: {os.getenv('OLLAMA_MODEL', 'llama3.2:latest')}")
        st.caption(f"ChromaDB: {os.getenv('CHROMADB_PATH', './data/chromadb')}")

        st.divider()
        if st.button("Clear All Session Data", use_container_width=True):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.rerun()
        return page


def render_overview() -> None:
    st.subheader("System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Credentials", "✓" if Path("credentials.json").exists() else "✗")
    col2.metric("OAuth Token", "✓" if Path("token.pickle").exists() else "✗")
    col3.metric("ChromaDB", "✓" if Path(os.getenv("CHROMADB_PATH", "./data/chromadb")).exists() else "✗")
    col4.metric("Memory DB", "✓" if Path("data/memory.db").exists() else "✗")

    st.markdown("### 🎯 Phase Status")
    
    # Core phases
    st.markdown("#### Core Email & Agent Features (Phases 1-5)")
    st.markdown(render_phase_badge(True, "Phase 1: Gmail"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(True, "Phase 2: Email Ops"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(True, "Phase 3: RAG"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(True, "Phase 4: HITL"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(True, "Phase 5: Multi-Agent"), unsafe_allow_html=True)
    
    # Advanced phases
    st.markdown("#### Advanced Features (Phases 6-9)")
    st.markdown(render_phase_badge(MEMORY_AVAILABLE, "Phase 6: Memory"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(SCHEDULER_AVAILABLE, "Phase 7: Scheduler"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(PLANNING_AVAILABLE, "Phase 8: Planning"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(CALENDAR_AVAILABLE, "Phase 9: Calendar"), unsafe_allow_html=True)
    
    # Intelligence phases
    st.markdown("#### Intelligence & Monitoring (Phases 10-12)")
    st.markdown(render_phase_badge(OBSERVABILITY_AVAILABLE, "Phase 10: Observability"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(ANALYTICS_AVAILABLE, "Phase 11: Analytics"), unsafe_allow_html=True)
    st.markdown(render_phase_badge(EVALUATION_AVAILABLE, "Phase 12: Evaluation"), unsafe_allow_html=True)
    
    st.info("✨ Use the sidebar to navigate to available phases. Install missing dependencies to enable additional phases.")


# Import all render functions from original file
def render_gmail_connection() -> None:
    st.subheader("1. Gmail Authentication & Connection")
    st.markdown(
        """
- Requires `credentials.json` in project root
- First authentication may open a browser for OAuth consent
- Current auth module uses readonly Gmail scope for inbox access
"""
    )

    if st.button("Test Gmail Authentication", type="primary"):
        with st.spinner("Authenticating with Gmail and fetching profile..."):
            try:
                result = test_authentication()
                st.session_state.gmail_status = result
                add_history("email_history", {"action": "gmail_auth_test", "result": result})
            except Exception as exc:
                st.session_state.gmail_status = {"status": "error", "error": str(exc)}

    status = st.session_state.gmail_status
    if status:
        if status.get("status") == "authenticated":
            st.success("Gmail authentication successful.")
            col1, col2, col3 = st.columns(3)
            col1.metric("Email", status.get("email", "Unknown"))
            col2.metric("Messages", status.get("messages_total", 0))
            col3.metric("Threads", status.get("threads_total", 0))
        else:
            st.error(status.get("error", "Authentication failed"))


def render_email_operations() -> None:
    st.subheader("2. Email Operations")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Recent Emails", "Search Emails", "Summarize", "Daily Digest", "Email Agent Chat"])

    with tab1:
        max_results = st.slider("Recent email count", 1, 20, 5, key="recent_email_count")
        if st.button("Fetch Recent Emails"):
            with st.spinner("Fetching recent emails..."):
                try:
                    result = get_recent_emails.invoke({"max_results": max_results})
                    add_history("email_history", {"action": "recent_emails", "input": {"max_results": max_results}, "result": result})
                    st.session_state["recent_emails_result"] = result
                except Exception as exc:
                    st.session_state["recent_emails_result"] = f"Error fetching recent emails: {exc}"
        if st.session_state.get("recent_emails_result"):
            st.text_area("Result", st.session_state["recent_emails_result"], height=320)

    with tab2:
        query = st.text_input("Gmail search query", placeholder="from:john@example.com OR subject:meeting")
        max_results = st.slider("Search result count", 1, 20, 5, key="search_email_count")
        if st.button("Search Gmail"):
            if not query.strip():
                st.warning("Enter a Gmail search query.")
            else:
                with st.spinner("Searching emails..."):
                    try:
                        result = search_emails.invoke({"query": query, "max_results": max_results})
                        add_history("email_history", {"action": "search_emails", "input": {"query": query, "max_results": max_results}, "result": result})
                        st.session_state["search_emails_result"] = result
                    except Exception as exc:
                        st.session_state["search_emails_result"] = f"Error searching emails: {exc}"
        if st.session_state.get("search_emails_result"):
            st.text_area("Search Result", st.session_state["search_emails_result"], height=320)

    with tab3:
        max_results = st.slider("Emails to summarize", 1, 20, 10, key="summarize_email_count")
        if st.button("Summarize Emails"):
            with st.spinner("Generating email summary..."):
                try:
                    result = summarize_emails.invoke({"max_results": max_results})
                    add_history("email_history", {"action": "summarize_emails", "input": {"max_results": max_results}, "result": result})
                    st.session_state["summarize_emails_result"] = result
                except Exception as exc:
                    st.session_state["summarize_emails_result"] = f"Error summarizing emails: {exc}"
        if st.session_state.get("summarize_emails_result"):
            st.text_area("Summary", st.session_state["summarize_emails_result"], height=320)

    with tab4:
        max_emails = st.slider("Emails for digest", 10, 200, 50, key="digest_email_count")
        if st.button("Generate Daily Digest"):
            with st.spinner("Generating daily digest..."):
                try:
                    result = generate_daily_digest.invoke({"max_emails": max_emails})
                    add_history("email_history", {"action": "daily_digest", "input": {"max_emails": max_emails}, "result": result})
                    st.session_state["daily_digest_result"] = result
                except Exception as exc:
                    st.session_state["daily_digest_result"] = f"Error generating daily digest: {exc}"
        if st.session_state.get("daily_digest_result"):
            st.text_area("Daily Digest", st.session_state["daily_digest_result"], height=360)

    with tab5:
        prompt = st.text_area("Ask the Email Agent", placeholder="Show me my recent emails and summarize the important ones.")
        if st.button("Run Email Agent"):
            if not prompt.strip():
                st.warning("Enter a prompt for the email agent.")
            else:
                with st.spinner("Running email agent..."):
                    try:
                        agent = get_cached_email_agent()
                        history = []
                        for item in st.session_state.email_history[:6]:
                            if item.get("action") and item.get("result"):
                                history.append(HumanMessage(content=f"Previous action: {item['action']}"))
                                history.append(AIMessage(content=str(item["result"])[:2000]))
                        history.append(HumanMessage(content=prompt))
                        result = agent.invoke({"messages": history})
                        messages = result.get("messages", [])
                        response = str(messages[-1].content) if messages else "No response generated"
                        add_history("email_history", {"action": "email_agent_chat", "input": prompt, "result": response})
                        st.session_state["email_agent_result"] = response
                    except Exception as exc:
                        st.session_state["email_agent_result"] = f"Error running email agent: {exc}"
        if st.session_state.get("email_agent_result"):
            st.text_area("Email Agent Response", st.session_state["email_agent_result"], height=320)


def render_rag_system() -> None:
    st.subheader("3. RAG System")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Index Emails", "Semantic Search", "Q&A", "Action Items", "Search by Sender"])

    with tab1:
        max_emails = st.slider("Emails to index", 1, 100, 25, key="rag_index_count")
        if st.button("Store Recent Emails in Vector DB"):
            with st.spinner("Indexing emails into ChromaDB..."):
                try:
                    result = store_recent_emails.invoke({"max_emails": max_emails})
                    add_history("rag_history", {"action": "store_recent_emails", "input": {"max_emails": max_emails}, "result": result})
                    st.session_state["store_recent_emails_result"] = result
                except Exception as exc:
                    st.session_state["store_recent_emails_result"] = f"Error indexing emails: {exc}"
        if st.session_state.get("store_recent_emails_result"):
            st.text_area("Indexing Result", st.session_state["store_recent_emails_result"], height=220)

    with tab2:
        query = st.text_input("Semantic search query", placeholder="emails about deployment delays", key="rag_search_query")
        max_results = st.slider("Semantic search results", 1, 20, 5, key="rag_search_count")
        if st.button("Run Semantic Search"):
            if not query.strip():
                st.warning("Enter a semantic search query.")
            else:
                with st.spinner("Searching indexed emails semantically..."):
                    try:
                        result = search_email_history.invoke({"query": query, "max_results": max_results})
                        add_history("rag_history", {"action": "search_email_history", "input": {"query": query, "max_results": max_results}, "result": result})
                        st.session_state["search_email_history_result"] = result
                    except Exception as exc:
                        st.session_state["search_email_history_result"] = f"Error in semantic search: {exc}"
        if st.session_state.get("search_email_history_result"):
            st.text_area("Semantic Search Result", st.session_state["search_email_history_result"], height=320)

    with tab3:
        question = st.text_area("Ask a question from emails", placeholder="What did the client say about deployment timing?")
        if st.button("Answer from Emails"):
            if not question.strip():
                st.warning("Enter a question.")
            else:
                with st.spinner("Generating RAG answer..."):
                    try:
                        result = answer_from_emails.invoke({"question": question})
                        add_history("rag_history", {"action": "answer_from_emails", "input": question, "result": result})
                        st.session_state["answer_from_emails_result"] = result
                    except Exception as exc:
                        st.session_state["answer_from_emails_result"] = f"Error generating answer: {exc}"
        if st.session_state.get("answer_from_emails_result"):
            st.text_area("Answer", st.session_state["answer_from_emails_result"], height=320)

    with tab4:
        if st.button("Extract Action Items"):
            with st.spinner("Extracting action items from emails..."):
                try:
                    result = find_action_items_from_emails.invoke({})
                    add_history("rag_history", {"action": "find_action_items_from_emails", "result": result})
                    st.session_state["find_action_items_result"] = result
                except Exception as exc:
                    st.session_state["find_action_items_result"] = f"Error extracting action items: {exc}"
        if st.session_state.get("find_action_items_result"):
            st.text_area("Action Items", st.session_state["find_action_items_result"], height=300)

    with tab5:
        sender = st.text_input("Sender email address", placeholder="john@example.com")
        max_results = st.slider("Sender search results", 1, 20, 10, key="rag_sender_count")
        if st.button("Search by Sender"):
            if not sender.strip():
                st.warning("Enter a sender email address.")
            else:
                with st.spinner("Searching indexed emails by sender..."):
                    try:
                        result = search_emails_by_sender.invoke({"sender_email": sender, "max_results": max_results})
                        add_history("rag_history", {"action": "search_emails_by_sender", "input": {"sender_email": sender, "max_results": max_results}, "result": result})
                        st.session_state["search_by_sender_result"] = result
                    except Exception as exc:
                        st.session_state["search_by_sender_result"] = f"Error searching by sender: {exc}"
        if st.session_state.get("search_by_sender_result"):
            st.text_area("Sender Search Result", st.session_state["search_by_sender_result"], height=300)


def render_drafting_hitl() -> None:
    st.subheader("4. Email Drafting with HITL Approval Workflow")

    with st.form("draft_form"):
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("Recipient", placeholder="recipient@example.com")
            subject = st.text_input("Subject", placeholder="Project Update")
        with col2:
            tone = st.selectbox("Tone", ["professional", "friendly", "formal", "casual"], index=0)
            is_reply = st.checkbox("Reply mode")
        original_email_id = st.text_input("Original Email ID (for replies)", disabled=not is_reply)
        user_request = st.text_area("Draft instructions", placeholder="Write a professional thank-you email summarizing next steps.", height=150)
        submitted = st.form_submit_button("Generate Draft", type="primary")

    if submitted:
        if not recipient.strip() or not subject.strip() or not user_request.strip():
            st.error("Recipient, subject, and draft instructions are required.")
        else:
            with st.spinner("Generating draft..."):
                try:
                    state = create_email_draft_state(
                        user_request=f"{user_request}\nTone: {tone}",
                        recipient=recipient,
                        subject=subject,
                        body="",
                        is_reply=is_reply,
                        original_email_id=original_email_id,
                    )
                    state = generate_draft_node(state)
                    st.session_state.pending_draft = state
                    add_history("draft_history", {"action": "generate_draft", "input": {"recipient": recipient, "subject": subject}, "result": state})
                except Exception as exc:
                    st.error(f"Error generating draft: {exc}")

    pending_draft = st.session_state.pending_draft
    if pending_draft:
        st.markdown("### Pending Draft Review")
        st.text_input("To", value=pending_draft.get("recipient", ""), disabled=True)
        st.text_input("Subject", value=pending_draft.get("subject", ""), disabled=True)
        edited_body = st.text_area("Draft Body", value=pending_draft.get("body", ""), height=240, key=f"draft_body_{pending_draft.get('draft_id', 'current')}")
        pending_draft["body"] = edited_body

        feedback = st.text_area("Feedback for regeneration", placeholder="Make it shorter and more direct.", key="draft_feedback")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve & Send", type="primary", use_container_width=True):
                with st.spinner("Sending approved email..."):
                    try:
                        pending_draft["approved"] = True
                        pending_draft["status"] = "approved"
                        final_state = send_email_node(pending_draft)
                        st.session_state.pending_draft = final_state
                        add_history("draft_history", {"action": "send_draft", "result": final_state})
                        if final_state.get("status") == "sent":
                            st.success(f"Email sent successfully. Message ID: {final_state.get('draft_id', 'unknown')}")
                        else:
                            st.error(final_state.get("error", "Failed to send email."))
                    except Exception as exc:
                        st.error(f"Error sending email: {exc}")

        with col2:
            if st.button("Reject & Regenerate", use_container_width=True):
                if not feedback.strip():
                    st.warning("Provide feedback before regenerating.")
                else:
                    with st.spinner("Regenerating draft..."):
                        try:
                            pending_draft["approved"] = False
                            pending_draft["status"] = "rejected"
                            pending_draft["feedback"] = feedback
                            updated_state = regenerate_draft_node(pending_draft)
                            st.session_state.pending_draft = updated_state
                            add_history("draft_history", {"action": "regenerate_draft", "feedback": feedback, "result": updated_state})
                            st.success("Draft regenerated.")
                        except Exception as exc:
                            st.error(f"Error regenerating draft: {exc}")

        with col3:
            if st.button("Clear Pending Draft", use_container_width=True):
                st.session_state.pending_draft = None
                st.rerun()


def render_multi_agent_system() -> None:
    st.subheader("5. Multi-Agent System")
    st.markdown("Supervisor routes requests to specialized Email or Knowledge agents.")

    query = st.text_area("Enter a multi-agent request", placeholder="What did the client say about deployment, and show related emails?")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Preview Supervisor Routing", use_container_width=True):
            if not query.strip():
                st.warning("Enter a query.")
            else:
                with st.spinner("Analyzing routing decision..."):
                    try:
                        supervisor = get_cached_supervisor_llm()
                        routing = route_query(supervisor, query)
                        st.session_state["routing_preview"] = routing
                        add_history("supervisor_history", {"action": "route_query", "input": query, "result": routing})
                    except Exception as exc:
                        st.session_state["routing_preview"] = {"agent": "email", "reason": str(exc), "context": query}

    with col2:
        if st.button("Run Multi-Agent Query", type="primary", use_container_width=True):
            if not query.strip():
                st.warning("Enter a query.")
            else:
                with st.spinner("Running multi-agent workflow..."):
                    try:
                        app = get_cached_multi_agent_app()
                        initial_state = {
                            "query": query,
                            "next_agent": "supervisor",
                            "email_agent_response": "",
                            "knowledge_agent_response": "",
                            "calendar_agent_response": "",
                            "final_response": "",
                            "messages": [],
                        }
                        result = app.invoke(cast(Any, initial_state))
                        response = result.get("final_response", "No response generated")
                        agent_used = result.get("next_agent", "unknown")
                        payload = {"query": query, "agent_used": agent_used, "result": response}
                        add_history("multi_agent_history", payload)
                        st.session_state["multi_agent_result"] = payload
                    except Exception as exc:
                        st.session_state["multi_agent_result"] = {"query": query, "agent_used": "error", "result": str(exc)}

    if st.session_state.get("routing_preview"):
        routing = st.session_state["routing_preview"]
        st.info(f"Supervisor selected: {routing.get('agent', 'unknown')}")
        st.write(f"**Reason:** {routing.get('reason', 'N/A')}")
        st.write(f"**Context:** {routing.get('context', 'N/A')}")

    if st.session_state.get("multi_agent_result"):
        result = st.session_state["multi_agent_result"]
        st.success(f"Handled by: {str(result.get('agent_used', 'unknown')).title()} Agent")
        st.text_area("Multi-Agent Response", result.get("result", ""), height=320)


def render_history_session() -> None:
    st.subheader("6. Conversation History and Session Management")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Session Snapshot")
        st.json(
            {
                "gmail_status": st.session_state.gmail_status,
                "email_history_count": len(st.session_state.email_history),
                "rag_history_count": len(st.session_state.rag_history),
                "draft_history_count": len(st.session_state.draft_history),
                "multi_agent_history_count": len(st.session_state.multi_agent_history),
                "pending_draft": bool(st.session_state.pending_draft),
            }
        )

    with col2:
        st.markdown("### Session Controls")
        if st.button("Clear Email History", use_container_width=True):
            st.session_state.email_history = []
            st.success("Email history cleared.")
        if st.button("Clear RAG History", use_container_width=True):
            st.session_state.rag_history = []
            st.success("RAG history cleared.")
        if st.button("Clear Draft History", use_container_width=True):
            st.session_state.draft_history = []
            st.success("Draft history cleared.")
        if st.button("Clear Multi-Agent History", use_container_width=True):
            st.session_state.multi_agent_history = []
            st.success("Multi-agent history cleared.")

    st.markdown("### Unified Conversation History")
    if not st.session_state.conversation_history:
        st.info("No session activity recorded yet.")
    else:
        for idx, item in enumerate(st.session_state.conversation_history[:25], start=1):
            with st.expander(f"{idx}. {item.get('category', 'unknown')} - {item.get('action', item.get('query', 'entry'))}"):
                st.json(item)


def render_memory_system() -> None:
    st.subheader("6. Memory System")
    if not MEMORY_AVAILABLE:
        st.error("Memory module not available. Install dependencies: pip install -r requirements.txt")
        return
    
    st.info("Memory System UI - Store conversations, preferences, and long-term knowledge")
    st.markdown("**Features:** Conversation history, User preferences, Episodic memory, Semantic memory")
    st.warning("Full implementation requires MemoryStore initialization")


def render_scheduler() -> None:
    st.subheader("7. Job Scheduler")
    if not SCHEDULER_AVAILABLE:
        st.error("Scheduler module not available. Install dependencies: pip install apscheduler")
        return
    
    st.info("Job Scheduler UI - Autonomous job scheduling with cron and interval triggers")
    st.markdown("**Features:** Active jobs, Job history, Schedule new jobs")
    st.warning("Full implementation requires JobScheduler initialization")


def render_planning() -> None:
    st.subheader("8. Task Planning")
    if not PLANNING_AVAILABLE:
        st.error("Planning module not available. Install dependencies: pip install -r requirements.txt")
        return
    
    st.info("Task Planning UI - Multi-step task planning and execution")
    st.markdown("**Features:** Create plans, Active plans, Plan history, Step execution")
    st.warning("Full implementation requires TaskPlanner initialization")


def render_calendar() -> None:
    st.subheader("9. Calendar Integration")
    if not CALENDAR_AVAILABLE:
        st.error("Calendar module not available. Install dependencies: pip install google-api-python-client")
        return
    
    st.info("Calendar UI - Google Calendar integration and event management")
    st.markdown("**Features:** View events, Create events, Update events, Calendar sync")
    st.warning("Full implementation requires CalendarManager initialization and OAuth")


def render_observability() -> None:
    st.subheader("10. Observability & Monitoring")
    if not OBSERVABILITY_AVAILABLE:
        st.error("Observability module not available. Install dependencies: pip install -r requirements.txt")
        return
    
    st.info("Observability UI - Metrics, logging, and health checks")
    st.markdown("**Features:** System metrics, Health status, Logs viewer, Performance monitoring")
    st.warning("Full implementation requires MetricsCollector and HealthChecker initialization")


def render_analytics() -> None:
    st.subheader("11. Email Analytics & Intelligence")
    if not ANALYTICS_AVAILABLE:
        st.error("Analytics module not available. Install dependencies: pip install -r requirements.txt")
        return
    
    st.info("Analytics UI - Email intelligence, sentiment analysis, and insights")
    st.markdown("**Features:** Sentiment analysis, Priority scoring, Relationship tracking, Topic extraction, Insights generation")
    st.warning("Full implementation requires EmailAnalyzer and InsightsGenerator initialization")


def render_evaluation() -> None:
    st.subheader("12. Agent Evaluation Framework")
    if not EVALUATION_AVAILABLE:
        st.error("Evaluation module not available. Install dependencies: pip install -r requirements.txt")
        return
    
    st.info("Evaluation UI - Test cases, metrics, and LLM evaluation")
    st.markdown("**Features:** Test runner, Metrics calculator, LLM evaluator, Performance reports")
    st.warning("Full implementation requires TestRunner and MetricsCalculator initialization")



def main() -> None:
    initialize_session_state()
    render_header()
    page = render_sidebar()

    try:
        if page == "Overview":
            render_overview()
        elif page == "Gmail Connection":
            render_gmail_connection()
        elif page == "Email Operations":
            render_email_operations()
        elif page == "RAG System":
            render_rag_system()
        elif page == "Drafting & HITL":
            render_drafting_hitl()
        elif page == "Multi-Agent System":
            render_multi_agent_system()
        elif page == "Memory System":
            render_memory_system()
        elif page == "Scheduler":
            render_scheduler()
        elif page == "Planning":
            render_planning()
        elif page == "Calendar":
            render_calendar()
        elif page == "Observability":
            render_observability()
        elif page == "Analytics":
            render_analytics()
        elif page == "Evaluation":
            render_evaluation()
        elif page == "History & Session":
            render_history_session()
    except Exception as exc:
        st.error(f"Unexpected UI error: {exc}")
        import traceback
        st.code(traceback.format_exc())

    st.markdown("---")
    st.caption(f"Python {sys.version.split()[0]} | Streamlit UI for AI Executive Assistant - All 12 Phases")


if __name__ == "__main__":
    main()

# Made with Bob
