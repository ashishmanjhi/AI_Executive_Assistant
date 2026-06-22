"""
Multi-Agent Workflow

Coordinates multiple specialized agents using a supervisor pattern.
"""

import logging
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.graph.state import MultiAgentState
from app.agents.supervisor_agent import create_supervisor_agent, route_query
from app.agents.email_agent_specialized import create_email_agent
from app.agents.knowledge_agent import create_knowledge_agent

# Try to import calendar agent
try:
    from app.agents.calendar_agent import create_calendar_agent
    CALENDAR_AGENT_AVAILABLE = True
except ImportError:
    CALENDAR_AGENT_AVAILABLE = False

logger = logging.getLogger(__name__)


def create_multi_agent_system():
    """
    Create a multi-agent system with supervisor coordination.
    
    Architecture:
    User Query → Supervisor → Route to Agent → Execute → Response
    
    Agents:
    - Supervisor: Routes queries to appropriate agent
    - Email Agent: Handles email operations
    - Knowledge Agent: Handles Q&A and semantic search
    - Calendar Agent: Handles calendar operations (if available)
    
    Returns:
        Compiled LangGraph multi-agent workflow
    """
    # Initialize agents
    supervisor_llm = create_supervisor_agent()
    email_agent = create_email_agent()
    knowledge_agent = create_knowledge_agent()
    
    # Initialize calendar agent if available
    calendar_agent = None
    if CALENDAR_AGENT_AVAILABLE:
        try:
            calendar_agent = create_calendar_agent()
            logger.info("Calendar agent initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize calendar agent: {e}")
            calendar_agent = None
    
    # Create state graph
    workflow = StateGraph(MultiAgentState)
    
    # Define supervisor node
    def supervisor_node(state: MultiAgentState) -> MultiAgentState:
        """Route query to appropriate agent."""
        try:
            query = state.get("query", "")
            
            # Get routing decision
            routing = route_query(supervisor_llm, query)
            
            # Update state
            state["next_agent"] = routing["agent"]
            
            logger.info(f"Supervisor routed to {routing['agent']}: {routing['reason']}")
            return state
            
        except Exception as e:
            logger.error(f"Error in supervisor node: {e}")
            state["next_agent"] = "email"  # Default
            return state
    
    # Define email agent node
    def email_agent_node(state: MultiAgentState) -> MultiAgentState:
        """Execute email agent."""
        try:
            query = state.get("query", "")
            messages = state.get("messages", [])
            
            # Add user message if not already in messages
            if not messages or not isinstance(messages[-1], HumanMessage):
                messages.append(HumanMessage(content=query))
            
            # Invoke email agent
            result = email_agent.invoke({"messages": messages})
            
            # Extract response
            response_messages = result.get("messages", [])
            if response_messages:
                last_message = response_messages[-1]
                if isinstance(last_message, AIMessage):
                    # Explicitly cast to str to handle complex content types
                    response = str(last_message.content)
                else:
                    response = str(last_message)
            else:
                response = "No response from Email Agent"
            
            # Update state
            state["email_agent_response"] = response
            state["final_response"] = response
            state["messages"] = response_messages
            
            logger.info("Email Agent completed task")
            return state
            
        except Exception as e:
            logger.error(f"Error in email agent node: {e}")
            state["email_agent_response"] = f"Error: {str(e)}"
            state["final_response"] = f"Error: {str(e)}"
            return state
    
    # Define knowledge agent node
    def knowledge_agent_node(state: MultiAgentState) -> MultiAgentState:
        """Execute knowledge agent."""
        try:
            query = state.get("query", "")
            messages = state.get("messages", [])
            
            # Add user message if not already in messages
            if not messages or not isinstance(messages[-1], HumanMessage):
                messages.append(HumanMessage(content=query))
            
            # Invoke knowledge agent
            result = knowledge_agent.invoke({"messages": messages})
            
            # Extract response
            response_messages = result.get("messages", [])
            if response_messages:
                last_message = response_messages[-1]
                if isinstance(last_message, AIMessage):
                    # Explicitly cast to str to handle complex content types
                    response = str(last_message.content)
                else:
                    response = str(last_message)
            else:
                response = "No response from Knowledge Agent"
            
            # Update state
            state["knowledge_agent_response"] = response
            state["final_response"] = response
            state["messages"] = response_messages
            
            logger.info("Knowledge Agent completed task")
            return state
            
        except Exception as e:
            logger.error(f"Error in knowledge agent node: {e}")
            state["knowledge_agent_response"] = f"Error: {str(e)}"
            state["final_response"] = f"Error: {str(e)}"
            return state
    
    # Define calendar agent node (if available)
    def calendar_agent_node(state: MultiAgentState) -> MultiAgentState:
        """Execute calendar agent."""
        if not calendar_agent:
            state["calendar_agent_response"] = "Calendar agent not available"
            state["final_response"] = "Calendar agent not available. Please ensure calendar dependencies are installed."
            return state
        
        try:
            query = state.get("query", "")
            messages = state.get("messages", [])
            
            # Add user message if not already in messages
            if not messages or not isinstance(messages[-1], HumanMessage):
                messages.append(HumanMessage(content=query))
            
            # Invoke calendar agent
            result = calendar_agent.invoke({"messages": messages})
            
            # Extract response
            response_messages = result.get("messages", [])
            if response_messages:
                last_message = response_messages[-1]
                if isinstance(last_message, AIMessage):
                    response = str(last_message.content)
                else:
                    response = str(last_message)
            else:
                response = "No response from Calendar Agent"
            
            # Update state
            state["calendar_agent_response"] = response
            state["final_response"] = response
            state["messages"] = response_messages
            
            logger.info("Calendar Agent completed task")
            return state
            
        except Exception as e:
            logger.error(f"Error in calendar agent node: {e}")
            state["calendar_agent_response"] = f"Error: {str(e)}"
            state["final_response"] = f"Error: {str(e)}"
            return state
    
    # Add nodes to workflow
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("email_agent", email_agent_node)
    workflow.add_node("knowledge_agent", knowledge_agent_node)
    
    # Add calendar agent node if available
    if calendar_agent:
        workflow.add_node("calendar_agent", calendar_agent_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Define routing function
    def route_to_agent(state: MultiAgentState) -> Literal["email_agent", "knowledge_agent", "calendar_agent", "end"]:
        """Route to the appropriate agent based on supervisor decision."""
        next_agent = state.get("next_agent", "email")
        
        if next_agent == "email":
            return "email_agent"
        elif next_agent == "knowledge":
            return "knowledge_agent"
        elif next_agent == "calendar":
            # Only route to calendar if calendar_agent is available
            if calendar_agent:
                return "calendar_agent"
            else:
                logger.warning("Calendar agent requested but not available, ending workflow")
                return "end"
        else:
            return "end"
    
    # Add conditional edges from supervisor
    if calendar_agent:
        workflow.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "email_agent": "email_agent",
                "knowledge_agent": "knowledge_agent",
                "calendar_agent": "calendar_agent",
                "end": END
            }
        )
    else:
        workflow.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "email_agent": "email_agent",
                "knowledge_agent": "knowledge_agent",
                "end": END
            }
        )
    
    # Add edges from agents to end
    workflow.add_edge("email_agent", END)
    workflow.add_edge("knowledge_agent", END)
    if calendar_agent:
        workflow.add_edge("calendar_agent", END)
    
    # Compile workflow
    app = workflow.compile()
    
    logger.info("Multi-agent system created successfully")
    return app


def run_multi_agent_query(query: str, app=None) -> str:
    """
    Run a query through the multi-agent system.
    
    Args:
        query: User's query
        app: Optional pre-created multi-agent app
    
    Returns:
        Final response from the appropriate agent
    
    Example:
        >>> response = run_multi_agent_query("Show me my recent emails")
        >>> print(response)
    """
    if app is None:
        app = create_multi_agent_system()
    
    # Create initial state
    initial_state = MultiAgentState(
        query=query,
        next_agent="supervisor",
        email_agent_response="",
        knowledge_agent_response="",
        calendar_agent_response="",
        final_response="",
        messages=[]
    )
    
    # Run workflow
    result = app.invoke(initial_state)
    
    # Extract final response
    final_response = result.get("final_response", "No response generated")
    
    return final_response


def run_multi_agent_conversation(app=None):
    """
    Run an interactive conversation with the multi-agent system.
    
    Args:
        app: Optional pre-created multi-agent app
    
    This provides a REPL-style interface where the supervisor
    automatically routes queries to the appropriate agent.
    """
    if app is None:
        app = create_multi_agent_system()
    
    print("\n" + "="*60)
    print("Multi-Agent AI Executive Assistant")
    print("="*60)
    print("\nAvailable Agents:")
    print("  • Email Agent: Email operations (read, search, draft, send)")
    print("  • Knowledge Agent: Q&A and semantic search (RAG)")
    print("\nThe Supervisor will automatically route your queries.")
    print("\nType 'exit', 'quit', or 'q' to end the conversation.")
    print("="*60 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye! Have a great day!")
                break
            
            if not user_input:
                continue
            
            # Create state
            state = MultiAgentState(
                query=user_input,
                next_agent="supervisor",
                email_agent_response="",
                knowledge_agent_response="",
                calendar_agent_response="",
                final_response="",
                messages=[]
            )
            
            # Run workflow
            print("\nAssistant: ", end="", flush=True)
            result = app.invoke(state)
            
            # Display response
            response = result.get("final_response", "No response generated")
            agent_used = result.get("next_agent", "unknown")
            
            print(response)
            print(f"\n[Handled by: {agent_used.title()} Agent]")
            print()
            
        except KeyboardInterrupt:
            print("\n\nConversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again or type 'exit' to quit.\n")


# Workflow information
MULTI_AGENT_INFO = {
    "name": "Multi-Agent System",
    "pattern": "Supervisor + Specialized Agents",
    "agents": {
        "supervisor": "Routes queries to appropriate agent",
        "email_agent": "Handles email operations",
        "knowledge_agent": "Handles Q&A and semantic search"
    },
    "workflow": "Query -> Supervisor -> Route -> Agent -> Response",
    "benefits": [
        "Separation of concerns",
        "Specialized expertise",
        "Scalable architecture",
        "Easy to add new agents"
    ]
}


def get_multi_agent_info():
    """Get information about the multi-agent system."""
    return MULTI_AGENT_INFO


# Made with Bob