# Phase 2: LangGraph Agent Integration - User Guide

## Overview

Phase 2 transforms the basic email reader into an intelligent AI agent that can understand natural language queries and decide when to fetch emails. The agent uses LangGraph for orchestration and Ollama for local LLM inference.

## Architecture

```
User Query → LangGraph Agent → Reasoning → Tool Selection → Gmail API → Response
```

## Components

### 1. Tools (`app/tools/email_tools.py`)

- **get_recent_emails(max_results=5)**: Fetch recent emails
- **search_emails(query, max_results=5)**: Search emails

### 2. Agent (`app/agents/email_agent.py`)

AI agent that understands queries and uses tools

### 3. Workflow (`app/graph/email_workflow.py`)

Manages conversation and tool execution

### 4. Prompts (`app/prompts/email_prompts.py`)

Guides agent behavior

## Usage

```bash
# Run interactive mode (default)
python main.py

# Run Phase 1 (basic reader)
python main.py phase1

# Get help
python main.py help
```

## Example Conversations

**Fetch recent emails:**

```
You: Show me my recent emails
Assistant: [Fetches and displays 5 recent emails]
```

**Search emails:**

```
You: Find emails from john@example.com
Assistant: [Searches and displays matching emails]
```

**Follow-up questions:**

```
You: What's the most important one?
Assistant: [Analyzes and responds based on previous results]
```

## Gmail Search Operators

- `from:sender@example.com` - From specific sender
- `subject:keyword` - Subject contains keyword
- `is:unread` - Unread emails
- `is:starred` - Starred emails
- `has:attachment` - Has attachments
- `after:2024/01/01` - After date
- `before:2024/12/31` - Before date

## Prerequisites

1. **Ollama running:**

   ```bash
   ollama serve
   ```

2. **Model pulled:**

   ```bash
   ollama pull llama3.2
   ```

3. **Gmail credentials:**
   - Follow `GMAIL_SETUP.md`
   - Place `credentials.json` in project root

## Troubleshooting

**Agent not responding:**

- Check Ollama is running: `ollama list`
- Verify model is available
- Check `.env` for correct OLLAMA_BASE_URL

**Gmail errors:**

- Ensure credentials.json exists
- Re-authenticate if token expired
- Check GMAIL_SETUP.md

**Exit conversation:**
Type `exit`, `quit`, or `q`

## Key Differences: Phase 1 vs Phase 2

| Feature      | Phase 1              | Phase 2                 |
| ------------ | -------------------- | ----------------------- |
| Interface    | Direct function call | Natural language chat   |
| Intelligence | None                 | AI agent with reasoning |
| Flexibility  | Fixed behavior       | Dynamic tool selection  |
| Conversation | Single action        | Multi-turn dialogue     |
| User Input   | None                 | Interactive queries     |

## Next Steps

After Phase 2, you can:

- Add more tools (calendar, tasks)
- Implement multi-agent workflows
- Add memory persistence
- Create specialized agents
