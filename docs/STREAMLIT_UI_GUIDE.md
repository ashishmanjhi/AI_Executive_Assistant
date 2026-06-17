# Streamlit Web Interface Guide

## Overview

The Streamlit web interface (`app_ui.py`) provides a comprehensive testing console for all Phase 1-5 features of the AI Executive Assistant. It offers an intuitive, interactive way to test Gmail integration, email operations, RAG system, HITL drafting, and the multi-agent system.

## Features

### 📋 Available Pages

1. **Overview** - System status and phase coverage
2. **Gmail Connection** - Test Gmail authentication
3. **Email Operations** - Read, search, summarize emails, daily digest, email agent chat
4. **RAG System** - Index emails, semantic search, Q&A, action items, sender search
5. **Drafting & HITL** - Email drafting with human-in-the-loop approval workflow
6. **Multi-Agent System** - Supervisor routing and specialized agent execution
7. **History & Session** - View conversation history and manage session data

## Prerequisites

### 1. Environment Setup

Ensure you have completed the basic setup:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Verify Streamlit is installed
pip list | grep streamlit
# Should show: streamlit==1.58.0
```

### 2. Required Files

- `credentials.json` - Google OAuth credentials (in project root)
- `token.pickle` - Gmail OAuth token (generated on first auth)
- `.env` - Environment configuration

### 3. Environment Variables

Ensure your `.env` file contains:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# Gmail API
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle

# ChromaDB
CHROMADB_PATH=./data/chromadb
```

### 4. Services Running

Before starting the UI, ensure these services are running:

```bash
# 1. Ollama (for LLM)
ollama serve

# 2. Verify Ollama model is available
ollama list
# Should show llama3.2:latest or your configured model
```

## Running the Streamlit UI

### Quick Start

```bash
# From project root directory
streamlit run app_ui.py
```

The UI will automatically open in your default browser at `http://localhost:8501`

### Custom Port

```bash
# Run on a different port
streamlit run app_ui.py --server.port 8502
```

### Network Access

```bash
# Allow access from other devices on your network
streamlit run app_ui.py --server.address 0.0.0.0
```

### Development Mode

```bash
# Enable auto-reload on file changes
streamlit run app_ui.py --server.runOnSave true
```

## Using the Interface

### 1. Overview Page

**Purpose**: Check system status and prerequisites

**Actions**:

- View credentials file status
- Check OAuth token availability
- Verify ChromaDB path
- Review phase coverage

**What to Check**:

- ✅ Credentials File: Available
- ✅ OAuth Token: Available (or Missing on first run)
- ✅ ChromaDB Path: Ready

### 2. Gmail Connection Page

**Purpose**: Test Gmail authentication and connection

**Steps**:

1. Click "Test Gmail Authentication"
2. If first time, browser will open for OAuth consent
3. Grant permissions to the app
4. View authentication status and account info

**Expected Output**:

```
✅ Gmail authentication successful
Email: your-email@gmail.com
Messages: 1234
Threads: 567
```

**Troubleshooting**:

- If authentication fails, check `credentials.json` exists
- Ensure Gmail API is enabled in Google Cloud Console
- Delete `token.pickle` and re-authenticate if needed

### 3. Email Operations Page

#### Tab 1: Recent Emails

**Purpose**: Fetch and display recent emails

**Steps**:

1. Adjust slider for email count (1-20)
2. Click "Fetch Recent Emails"
3. View results in text area

**Use Case**: Quick inbox check

#### Tab 2: Search Emails

**Purpose**: Search emails using Gmail query syntax

**Steps**:

1. Enter Gmail search query (e.g., `from:john@example.com`)
2. Adjust result count
3. Click "Search Gmail"

**Query Examples**:

- `from:john@example.com` - Emails from John
- `subject:meeting` - Emails with "meeting" in subject
- `is:unread` - Unread emails
- `after:2024/01/01` - Emails after date
- `has:attachment` - Emails with attachments

#### Tab 3: Summarize

**Purpose**: Generate AI summary of recent emails

**Steps**:

1. Select number of emails to summarize (1-20)
2. Click "Summarize Emails"
3. View AI-generated summary

**Use Case**: Quick overview of inbox activity

#### Tab 4: Daily Digest

**Purpose**: Generate comprehensive daily email digest

**Steps**:

1. Select email count for digest (10-200)
2. Click "Generate Daily Digest"
3. View categorized digest with:
   - High priority emails
   - Action items
   - FYI emails
   - Summary statistics

**Use Case**: Morning briefing or end-of-day review

#### Tab 5: Email Agent Chat

**Purpose**: Conversational interface with email agent

**Steps**:

1. Enter natural language prompt
2. Click "Run Email Agent"
3. Agent uses tools to fulfill request

**Example Prompts**:

- "Show me my recent emails and summarize the important ones"
- "Search for emails from Sarah about the project"
- "What are my unread emails about?"

### 4. RAG System Page

#### Tab 1: Index Emails

**Purpose**: Store emails in vector database for semantic search

**Steps**:

1. Select number of emails to index (1-100)
2. Click "Store Recent Emails in Vector DB"
3. Wait for indexing to complete

**Note**: This is required before using semantic search, Q&A, or action items

**Recommendation**: Index 25-50 emails initially, then more as needed

#### Tab 2: Semantic Search

**Purpose**: Search emails by meaning, not just keywords

**Steps**:

1. Enter semantic query (e.g., "emails about deployment delays")
2. Adjust result count
3. Click "Run Semantic Search"

**Difference from Gmail Search**:

- Gmail: Keyword matching
- Semantic: Meaning-based matching

**Example Queries**:

- "emails about budget concerns"
- "discussions about project timeline"
- "client feedback on the product"

#### Tab 3: Q&A

**Purpose**: Ask questions and get answers from email content

**Steps**:

1. Enter question in text area
2. Click "Answer from Emails"
3. View AI-generated answer with context

**Example Questions**:

- "What did the client say about deployment timing?"
- "When is the project deadline?"
- "Who approved the budget increase?"

**How It Works**: RAG retrieves relevant emails, then LLM generates answer

#### Tab 4: Action Items

**Purpose**: Extract actionable tasks from emails

**Steps**:

1. Click "Extract Action Items"
2. View list of extracted action items

**Use Case**: Task management, to-do list generation

#### Tab 5: Search by Sender

**Purpose**: Find all emails from specific sender

**Steps**:

1. Enter sender email address
2. Adjust result count
3. Click "Search by Sender"

**Use Case**: Review all communications with a person

### 5. Drafting & HITL Page

**Purpose**: Draft emails with human-in-the-loop approval workflow

#### Drafting Process

**Steps**:

1. Fill in draft form:
   - **Recipient**: Email address
   - **Subject**: Email subject line
   - **Tone**: professional/friendly/formal/casual
   - **Reply mode**: Check if replying to existing email
   - **Original Email ID**: (if reply mode)
   - **Draft instructions**: What you want to say

2. Click "Generate Draft"

3. Review generated draft:
   - Edit body text directly
   - Provide feedback for regeneration

4. Choose action:
   - **Approve & Send**: Send the email
   - **Reject & Regenerate**: Provide feedback and regenerate
   - **Clear Pending Draft**: Cancel and start over

#### Example Workflow

**Scenario**: Thank-you email after meeting

```
Recipient: john@example.com
Subject: Thank you for the meeting
Tone: professional
Draft instructions: Thank John for the productive meeting about the project timeline. Mention we'll send the updated schedule by Friday.
```

**Generated Draft** → **Review** → **Edit if needed** → **Approve & Send**

**Regeneration Example**:

- Feedback: "Make it shorter and more direct"
- Agent regenerates with feedback applied

### 6. Multi-Agent System Page

**Purpose**: Test supervisor routing and specialized agent execution

#### Features

1. **Preview Supervisor Routing**
   - See which agent the supervisor would choose
   - View routing reason and context
   - No actual execution

2. **Run Multi-Agent Query**
   - Execute full multi-agent workflow
   - Supervisor routes to appropriate agent
   - Agent executes and returns response

#### Example Queries

**Email Agent Queries**:

- "Show me my latest emails"
- "Search for emails from Sarah"
- "Summarize my unread messages"

**Knowledge Agent Queries**:

- "What did John say about the project deadline?"
- "Find emails discussing budget approval"
- "Extract action items from recent emails"

**Complex Queries**:

- "What did the client say about deployment, and show related emails?"
- "Find all emails about the project and summarize key points"

#### Workflow

1. Enter query in text area
2. **Option A**: Click "Preview Supervisor Routing"
   - See routing decision without execution
   - Useful for understanding supervisor logic

3. **Option B**: Click "Run Multi-Agent Query"
   - Full execution with routing
   - View which agent handled the query
   - See final response

### 7. History & Session Page

**Purpose**: View conversation history and manage session data

#### Features

1. **Session Snapshot**
   - Gmail authentication status
   - History counts for each category
   - Pending draft status

2. **Session Controls**
   - Clear Email History
   - Clear RAG History
   - Clear Draft History
   - Clear Multi-Agent History

3. **Unified Conversation History**
   - Shows last 25 interactions
   - Expandable entries with full details
   - Includes all actions across all pages

#### Use Cases

- **Debugging**: Review what actions were taken
- **Testing**: Verify tool calls and responses
- **Cleanup**: Clear history between test sessions

## Tips & Best Practices

### 1. First-Time Setup

```bash
# 1. Start Ollama
ollama serve

# 2. Pull model if not already available
ollama pull llama3.2:latest

# 3. Run Streamlit
streamlit run app_ui.py

# 4. Test Gmail authentication first
# Navigate to "Gmail Connection" page
```

### 2. Testing Workflow

**Recommended Order**:

1. ✅ Gmail Connection - Authenticate
2. ✅ Email Operations - Fetch some emails
3. ✅ RAG System - Index emails
4. ✅ RAG System - Test semantic search
5. ✅ Drafting & HITL - Create a draft
6. ✅ Multi-Agent System - Test routing

### 3. Performance Tips

- **Caching**: Agents are cached with `@st.cache_resource`
- **Session State**: History persists during session
- **Clear Data**: Use "Clear All Session Data" in sidebar to reset

### 4. Error Handling

The UI includes comprehensive error handling:

- Try-except blocks around all operations
- Error messages displayed in UI
- Errors logged to session history

**Common Errors**:

1. **"Ollama connection failed"**
   - Solution: Start Ollama with `ollama serve`

2. **"Gmail authentication failed"**
   - Solution: Check `credentials.json`, re-authenticate

3. **"ChromaDB not found"**
   - Solution: Index emails first in RAG System tab

4. **"Model not found"**
   - Solution: Pull model with `ollama pull llama3.2:latest`

### 5. Session Management

**Clear Session Data**:

- Sidebar → "Clear All Session Data" button
- Resets all history and cached data
- Useful between test sessions

**Selective Clearing**:

- History & Session page → Clear specific history types
- Preserves other session data

## Advanced Usage

### 1. Custom Configuration

Edit `.env` to customize:

```env
# Use different model
OLLAMA_MODEL=mistral:latest

# Use different Ollama instance
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Use different ChromaDB location
CHROMADB_PATH=./custom_chromadb
```

### 2. Multiple Sessions

Open multiple browser tabs to test concurrent sessions:

- Each tab has independent session state
- Useful for testing different scenarios

### 3. Network Access

Share UI with team members:

```bash
# Run with network access
streamlit run app_ui.py --server.address 0.0.0.0 --server.port 8501

# Access from other devices
http://YOUR_IP:8501
```

### 4. Development Mode

Enable auto-reload for development:

```bash
streamlit run app_ui.py --server.runOnSave true
```

## Troubleshooting

### Issue: UI Won't Start

**Symptoms**: `streamlit: command not found`

**Solution**:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Verify Streamlit installed
pip list | grep streamlit

# Reinstall if needed
pip install streamlit==1.58.0
```

### Issue: Gmail Authentication Fails

**Symptoms**: "Authentication failed" error

**Solutions**:

1. Check `credentials.json` exists in project root
2. Verify Gmail API is enabled in Google Cloud Console
3. Delete `token.pickle` and re-authenticate
4. Check OAuth consent screen is configured

### Issue: Ollama Connection Error

**Symptoms**: "Connection refused" or "Model not found"

**Solutions**:

```bash
# 1. Start Ollama
ollama serve

# 2. Verify model exists
ollama list

# 3. Pull model if missing
ollama pull llama3.2:latest

# 4. Test Ollama
curl http://localhost:11434/api/tags
```

### Issue: ChromaDB Errors

**Symptoms**: "Collection not found" or "No documents indexed"

**Solutions**:

1. Navigate to RAG System → Index Emails tab
2. Index at least 10-25 emails
3. Wait for indexing to complete
4. Try semantic search again

### Issue: Slow Performance

**Symptoms**: Long loading times, UI freezes

**Solutions**:

1. Reduce number of emails processed
2. Clear session data (sidebar button)
3. Restart Streamlit
4. Check Ollama is running locally (not remote)
5. Use smaller model (e.g., `qwen3:4b` instead of `llama3.2:latest`)

### Issue: Draft Not Sending

**Symptoms**: "Failed to send email" error

**Solutions**:

1. Check Gmail API has send permissions
2. Verify `email_sender.py` is configured correctly
3. Check OAuth token has write permissions
4. Review error message in UI for details

## Keyboard Shortcuts

Streamlit provides built-in shortcuts:

- `R` - Rerun the app
- `C` - Clear cache
- `Ctrl+K` or `Cmd+K` - Open command palette
- `Ctrl+Shift+R` - Hard refresh

## Monitoring & Debugging

### 1. Streamlit Logs

View Streamlit logs in terminal:

```bash
streamlit run app_ui.py --logger.level=debug
```

### 2. Session State

View current session state:

- Navigate to "History & Session" page
- Check "Session Snapshot" section

### 3. Conversation History

Review all interactions:

- "History & Session" page
- "Unified Conversation History" section
- Expand entries to see full details

## Production Deployment

### Local Network

```bash
# Run on local network
streamlit run app_ui.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless true
```

### Cloud Deployment

For cloud deployment (Streamlit Cloud, AWS, etc.):

1. Add `requirements.txt` to repository
2. Configure secrets in Streamlit Cloud
3. Set environment variables
4. Deploy from GitHub repository

**Note**: Gmail OAuth requires authorized redirect URIs in Google Cloud Console

## Security Considerations

### 1. Credentials

- Never commit `credentials.json` or `token.pickle` to git
- Add to `.gitignore`
- Use environment variables for sensitive data

### 2. Network Access

- Default: localhost only (127.0.0.1)
- Network access: Use with caution
- Production: Use authentication and HTTPS

### 3. Session Data

- Session data stored in memory
- Cleared on browser close
- Use "Clear All Session Data" between users

## Next Steps

After testing all features in the UI:

1. **Phase 6**: Implement Persistent Memory
2. **Phase 7**: Add Scheduled Autonomous Jobs
3. **Phase 8**: Build Multi-Step Planning Engine
4. **Phase 9**: Integrate Calendar
5. **Phase 10**: Add Observability

See `FUTURE_PHASES_ROADMAP.md` for detailed implementation plans.

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Review phase-specific guides:
   - `GMAIL_SETUP.md`
   - `PHASE3_RAG_GUIDE.md`
   - `PHASE4_HITL_GUIDE.md`
   - `PHASE5_MULTI_AGENT_GUIDE.md`
3. Check Streamlit documentation: https://docs.streamlit.io

---

**Made with Bob** 🤖

**Version**: 1.0  
**Last Updated**: 2026-06-17  
**Streamlit Version**: 1.58.0
