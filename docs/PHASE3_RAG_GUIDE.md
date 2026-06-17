# Phase 3: RAG Memory System - Complete Guide

## Overview

Phase 3 implements a **RAG (Retrieval-Augmented Generation)** memory system that enables semantic email search and intelligent question answering. The system stores emails as vector embeddings in ChromaDB, allowing the AI agent to search through email history and answer questions based on actual email content.

## Architecture

### Core Components

```
app/rag/
├── email_store.py      # ChromaDB vector store for email storage
├── vector_search.py    # Semantic search engine
├── retriever.py        # RAG-powered question answering
└── __init__.py         # Package initialization

app/tools/
└── rag_tools.py        # LangChain tool wrappers for agent integration
```

### Technology Stack

- **ChromaDB**: Vector database for storing email embeddings
- **SentenceTransformer**: Embedding model (all-MiniLM-L6-v2)
- **Ollama**: LLM for generating answers (qwen3:4b)
- **LangChain**: Tool integration framework

## Key Features

### 1. Email Storage with Embeddings

- Store emails as vector embeddings in ChromaDB
- Preserve metadata (subject, sender, date, thread_id)
- Batch processing support for efficient storage
- Automatic embedding generation using SentenceTransformer

### 2. Semantic Search

- Search emails by meaning, not just keywords
- Filter by sender, date range, or thread
- Similarity scoring for relevance ranking
- Find similar emails based on content

### 3. RAG Question Answering

- Answer questions using retrieved email context
- Cite specific emails in responses
- Handle complex queries across multiple emails
- Extract action items and deadlines

## Component Details

### EmailStore (`app/rag/email_store.py`)

**Purpose**: Manages email storage in ChromaDB with vector embeddings.

**Key Methods**:

```python
store_email(email: Dict[str, Any]) -> bool
    # Store a single email with embedding

store_emails_batch(emails: List[Dict[str, Any]]) -> Dict[str, int]
    # Store multiple emails efficiently

get_email(email_id: str) -> Optional[Dict[str, Any]]
    # Retrieve email by ID

delete_email(email_id: str) -> bool
    # Remove email from store

get_collection_stats() -> Dict[str, Any]
    # Get storage statistics
```

**Email Format**:

```python
{
    "id": "unique_email_id",
    "subject": "Email subject",
    "from": "sender@example.com",
    "to": "recipient@example.com",
    "date": "2024-06-15T10:30:00Z",
    "body": "Email content...",
    "thread_id": "thread_123",
    "labels": ["INBOX", "IMPORTANT"]
}
```

### VectorSearch (`app/rag/vector_search.py`)

**Purpose**: Provides semantic search capabilities over stored emails.

**Key Methods**:

```python
search(query: str, n_results: int = 5, **filters) -> List[Dict[str, Any]]
    # Semantic search with optional filters

search_by_sender(sender: str, n_results: int = 10) -> List[Dict[str, Any]]
    # Find all emails from specific sender

search_by_date_range(start_date: str, end_date: str, n_results: int = 20) -> List[Dict[str, Any]]
    # Search within date range

find_similar_emails(email_id: str, n_results: int = 5) -> List[Dict[str, Any]]
    # Find emails similar to a given email
```

**Search Result Format**:

```python
{
    "id": "email_id",
    "subject": "Email subject",
    "from": "sender@example.com",
    "date": "2024-06-15",
    "body": "Email content...",
    "similarity": 0.85,  # 0-1 score
    "metadata": {...}
}
```

### EmailRetriever (`app/rag/retriever.py`)

**Purpose**: RAG-powered question answering using retrieved email context.

**Key Methods**:

```python
answer_question(question: str, n_results: int = 3, **search_kwargs) -> str
    # Answer question using email context

retrieve_context(query: str, n_results: int = 3, **search_kwargs) -> List[Dict[str, Any]]
    # Get relevant emails for a query

summarize_emails(query: str, n_results: int = 5) -> str
    # Summarize emails matching query

find_action_items(query: str = "action items tasks deadlines", n_results: int = 10) -> str
    # Extract action items from emails
```

**RAG Prompt Template**:

```
You are an AI assistant analyzing email content.

Context from emails:
[Retrieved email content with metadata]

Question: {user_question}

Instructions:
- Answer based ONLY on the provided email context
- Cite specific emails (sender, date) when possible
- If information is not in the emails, say so
- Be concise and accurate

Answer:
```

## RAG Tools for Agent

### Available Tools

1. **search_email_history**

   ```python
   search_email_history(query: str) -> str
   ```

   - Semantic search through stored emails
   - Returns top 5 most relevant emails
   - Use for: "Find emails about X", "Search for Y"

2. **answer_from_emails**

   ```python
   answer_from_emails(question: str) -> str
   ```

   - RAG-powered question answering
   - Retrieves context and generates answer
   - Use for: "What did X say about Y?", "When is Z due?"

3. **store_recent_emails**

   ```python
   store_recent_emails(max_results: int = 50) -> str
   ```

   - Index recent emails for searching
   - Stores emails with embeddings in ChromaDB
   - Use for: "Store my recent emails", "Index my inbox"

4. **find_action_items_from_emails**

   ```python
   find_action_items_from_emails() -> str
   ```

   - Extract tasks and deadlines from emails
   - Searches for action-related content
   - Use for: "What are my pending tasks?", "Show action items"

5. **search_emails_by_sender**
   ```python
   search_emails_by_sender(sender: str) -> str
   ```

   - Find all emails from specific sender
   - Returns up to 10 most recent emails
   - Use for: "Show emails from X", "What did Y send?"

## Usage Examples

### Example 1: Store and Search Emails

```python
# Store recent emails
from app.tools.rag_tools import store_recent_emails

result = store_recent_emails(max_results=100)
print(result)
# Output: "Successfully stored 100 emails in the vector database."

# Search for specific content
from app.tools.rag_tools import search_email_history

results = search_email_history("deployment schedule")
print(results)
# Output: Top 5 emails about deployment with subjects, senders, dates
```

### Example 2: Answer Questions

```python
from app.tools.rag_tools import answer_from_emails

# Ask about specific information
answer = answer_from_emails("What did the client say about the deployment deadline?")
print(answer)
# Output: "Based on the email from client@example.com on June 2nd,
#          they requested deployment by Friday, June 7th."

# Ask about action items
answer = answer_from_emails("What tasks do I need to complete this week?")
print(answer)
# Output: Extracted tasks with deadlines from relevant emails
```

### Example 3: Find Emails by Sender

```python
from app.tools.rag_tools import search_emails_by_sender

emails = search_emails_by_sender("manager@company.com")
print(emails)
# Output: List of recent emails from the manager
```

### Example 4: Extract Action Items

```python
from app.tools.rag_tools import find_action_items_from_emails

action_items = find_action_items_from_emails()
print(action_items)
# Output: "Action Items from Emails:
#          1. Complete project report by Friday (from manager@company.com)
#          2. Review pull request #123 (from developer@company.com)
#          3. Schedule meeting with client (from client@example.com)"
```

## Agent Integration

### Tool Usage in Conversation

**User**: "Store my recent emails"
**Agent**: _Uses store_recent_emails tool_
**Output**: "I've stored 50 recent emails in the search database."

**User**: "What did the client say about deployment?"
**Agent**: _Uses answer_from_emails tool_
**Output**: "Based on the email from client@example.com on June 2nd, they requested deployment by Friday and mentioned testing should be completed by Wednesday."

**User**: "Find emails about the project"
**Agent**: _Uses search_email_history tool_
**Output**: "I found 5 emails about the project:

1. Project Update - from manager@company.com (June 10)
2. Project Requirements - from client@example.com (June 8)
   ..."

### Prompt Guidelines

The agent has been configured with these guidelines:

1. **Always store emails first** before searching or answering questions
2. **Use semantic search** for finding relevant emails
3. **Cite sources** when answering questions (sender, date)
4. **Be honest** if information is not in the emails
5. **Extract action items** when asked about tasks or deadlines

## Configuration

### Environment Variables

Add to `.env`:

```bash
# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=email_store

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Ollama Configuration (for RAG)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

### Customization

**Change Embedding Model**:

```python
# In app/rag/email_store.py
self.embedding_model = SentenceTransformer('your-model-name')
```

**Adjust Search Results**:

```python
# In app/rag/vector_search.py
def search(self, query: str, n_results: int = 10):  # Change default
    ...
```

**Modify RAG Prompt**:

```python
# In app/rag/retriever.py
def _create_rag_prompt(self, question: str, context: str) -> str:
    return f"""Your custom prompt template
    Context: {context}
    Question: {question}
    """
```

## Performance Considerations

### Embedding Generation

- **Model**: all-MiniLM-L6-v2 (fast, 384 dimensions)
- **Speed**: ~100 emails/second on CPU
- **Memory**: ~500MB for model + embeddings

### Vector Search

- **ChromaDB**: In-memory with disk persistence
- **Search Speed**: <100ms for 10,000 emails
- **Scalability**: Handles 100,000+ emails efficiently

### Batch Processing

```python
# Store emails in batches for better performance
emails = fetch_emails(max_results=1000)
result = store_emails_batch(emails)
# Much faster than storing one by one
```

## Troubleshooting

### Issue: "Collection not found"

**Solution**: Store emails first using `store_recent_emails()`

### Issue: "No results found"

**Solution**:

- Check if emails are stored: `get_collection_stats()`
- Try broader search query
- Verify email content is not empty

### Issue: "Embedding model download failed"

**Solution**:

- Check internet connection
- Model downloads automatically on first use
- Manually download: `SentenceTransformer('all-MiniLM-L6-v2')`

### Issue: "ChromaDB persistence error"

**Solution**:

- Check write permissions for `./chroma_db` directory
- Ensure sufficient disk space
- Delete and recreate: `rm -rf chroma_db`

## Testing

### Manual Testing

```python
# Test email storage
from app.rag.email_store import EmailStore

store = EmailStore()
test_email = {
    "id": "test_001",
    "subject": "Test Email",
    "from": "test@example.com",
    "to": "me@example.com",
    "date": "2024-06-15T10:00:00Z",
    "body": "This is a test email about deployment.",
    "thread_id": "thread_001"
}
store.store_email(test_email)

# Test search
from app.rag.vector_search import VectorSearch

search = VectorSearch(store)
results = search.search("deployment")
print(f"Found {len(results)} results")

# Test RAG
from app.rag.retriever import EmailRetriever

retriever = EmailRetriever(search)
answer = retriever.answer_question("What is the test email about?")
print(answer)
```

### Integration Testing

```bash
# Run the agent with RAG tools
python main.py

# Test commands:
# 1. "Store my recent emails"
# 2. "Search for emails about project"
# 3. "What did the client say about deployment?"
# 4. "Show me action items from emails"
```

## Best Practices

1. **Store emails regularly**: Run `store_recent_emails()` daily or weekly
2. **Use specific queries**: "deployment deadline" vs "emails"
3. **Combine tools**: Store → Search → Answer for best results
4. **Monitor storage**: Check `get_collection_stats()` periodically
5. **Clean old data**: Delete outdated emails to maintain performance

## Next Steps

### Phase 4 Ideas

- **Multi-modal RAG**: Support attachments (PDFs, images)
- **Advanced filtering**: By labels, importance, read/unread
- **Conversation memory**: Remember previous questions
- **Email threading**: Group related emails
- **Smart summaries**: Auto-generate email summaries
- **Scheduled indexing**: Automatic background email storage

## Summary

Phase 3 successfully implements a complete RAG memory system with:

- ✅ Vector storage with ChromaDB
- ✅ Semantic search capabilities
- ✅ RAG-powered question answering
- ✅ 5 integrated agent tools
- ✅ Batch processing support
- ✅ Metadata filtering
- ✅ Action item extraction

The system enables natural language queries over email history, making the AI Executive Assistant truly intelligent and context-aware.
