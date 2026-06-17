# AI Executive Assistant

An intelligent AI-powered executive assistant built with LangGraph, LangChain, and multiple LLM providers. This production-ready system features multi-agent orchestration, RAG-powered knowledge retrieval, human-in-the-loop workflows, comprehensive email management, calendar integration, observability, email intelligence, and agent evaluation capabilities.

## 🌟 Key Features

### Core Capabilities

- 🤖 **Multi-Agent System**: Supervisor-coordinated specialized agents (Email, Knowledge, Calendar)
- 📧 **Gmail Integration**: Full email operations (read, search, draft, send, reply)
- 🧠 **RAG Memory System**: Semantic search and Q&A using ChromaDB vector store
- 👤 **Human-in-the-Loop**: Safe email sending with draft approval workflow
- 💬 **Interactive Interface**: Streamlit web UI and CLI modes
- 🔄 **Persistent Memory**: 5 types of memory (conversation, preferences, episodic, semantic, procedural)
- ⏰ **Scheduled Jobs**: Autonomous background tasks with cron scheduling
- 🎯 **Multi-Step Planning**: LLM-powered task decomposition and execution
- 📅 **Calendar Integration**: Google Calendar sync, event management, and scheduling
- 📊 **Email Intelligence**: Analytics, relationship tracking, and insights generation
- 🔍 **Observability**: Comprehensive metrics, logging, and health monitoring
- 🧪 **Agent Evaluation**: Testing framework with LLM-as-judge evaluation

### Advanced Features

- 🔌 **Multiple LLM Providers**: Ollama (local), OpenAI, Anthropic Claude, Hugging Face
- 💰 **Cost Tracking**: Automatic usage and cost monitoring for paid providers
- 🔍 **Semantic Search**: Vector-based email search with ChromaDB
- 📝 **Smart Drafting**: AI-powered email composition with tone control
- 🔐 **OAuth2 Authentication**: Secure Gmail and Calendar API integration
- 📅 **Job Scheduling**: APScheduler-based autonomous task execution
- 🎯 **Task Planning**: Intelligent multi-step workflow decomposition
- 📈 **Email Analytics**: Sender patterns, response times, sentiment analysis
- 🤝 **Relationship Tracking**: Communication frequency and interaction patterns
- 📊 **Metrics & Monitoring**: Real-time performance and health tracking
- 🧪 **Comprehensive Testing**: Full test suite with evaluation framework

## Architecture

```
AI_Executive_Assistant/
├── app/
│   ├── graph/          # LangGraph workflow definitions
│   ├── agents/         # Agent implementations
│   ├── tools/          # Tool functions for agents
│   ├── gmail/          # Gmail API integration
│   ├── rag/            # RAG system components
│   ├── memory/         # Persistent memory system
│   ├── scheduler/      # Job scheduling system
│   ├── planning/       # Multi-step task planning
│   ├── calendar/       # Google Calendar integration
│   ├── observability/  # Metrics, logging, health checks
│   ├── analytics/      # Email intelligence & analytics
│   ├── evaluation/     # Agent evaluation framework
│   ├── prompts/        # System and agent prompts
│   └── config/         # Configuration files
├── docs/               # All documentation (20+ guides)
├── ui/                 # Streamlit UI components
├── tests/              # Unit and integration tests
├── main.py             # Backend initialization
├── app.py              # Streamlit web interface
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## 📋 Prerequisites

- **Python 3.11.9** or higher
- **LLM Provider** (choose one):
  - Ollama (recommended for development - free, local)
  - OpenAI API key (recommended for production)
  - Anthropic Claude API key
  - Hugging Face API token
- **Google API credentials** for Gmail integration
- **Git** (for cloning repository)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd AI_Executive_Assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For specific LLM providers, install additional packages:
pip install -r requirements_llm_providers.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
# Required: LLM_PROVIDER, Gmail credentials
# Optional: API keys for paid providers
```

### 3. Setup LLM Provider

**Option A: Ollama (Free, Local - Recommended for Development)**

```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2:latest

# Start Ollama server
ollama serve

# Configure in .env:
# LLM_PROVIDER=ollama
# OLLAMA_MODEL=llama3.2:latest
```

**Option B: OpenAI (Paid - Recommended for Production)**

```bash
# Get API key from https://platform.openai.com/api-keys
# Configure in .env:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o-mini
```

See [LLM_PROVIDER_GUIDE.md](docs/LLM_PROVIDER_GUIDE.md) for detailed provider setup.

### 4. Setup Gmail API

Follow the detailed guide: [GMAIL_SETUP.md](docs/GMAIL_SETUP.md)

1. Create Google Cloud project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to project root
5. Run authentication flow (first time only)

## 💻 Usage

### Interactive CLI Mode (Recommended)

```bash
python main.py
```

**Example Interactions:**

```
You: Show me my latest emails
Assistant: [Fetches and displays recent emails]

You: What did John say about the project deadline?
Assistant: [Uses RAG to search and answer from email history]

You: Draft a reply thanking him
Assistant: [Creates draft and shows for approval]

You: Send it
Assistant: [Sends after your approval]
```

### Streamlit Web UI

```bash
streamlit run app.py
```

Access at `http://localhost:8501`

Features:

- Chat interface with conversation history
- Email management dashboard
- RAG-powered search
- Draft approval workflow
- Cost tracking (for paid providers)

### Test Specific Features

```bash
# Test memory system
python test_memory_system.py

# Test RAG system
python test_rag_system.py

# Test HITL workflow
python test_hitl_workflow.py

# Test multi-agent system
python test_multi_agent.py

# Test Ollama setup
python test_ollama_setup.py
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# LLM Provider Configuration
LLM_PROVIDER=ollama  # ollama, openai, anthropic, huggingface
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Ollama (Local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest

# OpenAI (Paid)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic Claude (Paid)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Hugging Face (Free/Paid)
HUGGINGFACE_API_KEY=hf_your-key-here
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Gmail API
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# ChromaDB (RAG)
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=email_store

# Cost Tracking
ENABLE_COST_TRACKING=true

# Application
LOG_LEVEL=INFO
DEBUG_MODE=false
```

See [LLM_PROVIDER_GUIDE.md](docs/LLM_PROVIDER_GUIDE.md) for detailed configuration options.

## 📁 Project Structure

```
AI_Executive_Assistant/
├── app/
│   ├── agents/                    # Specialized agents
│   │   ├── supervisor_agent.py    # Routes queries to specialized agents
│   │   ├── email_agent_specialized.py  # Email operations
│   │   ├── knowledge_agent.py     # RAG-powered Q&A
│   │   └── memory_agent.py        # Memory management
│   ├── graph/                     # LangGraph workflows
│   │   ├── multi_agent_workflow.py  # Multi-agent orchestration
│   │   ├── hitl_workflow.py       # Human-in-the-loop for emails
│   │   ├── email_workflow.py      # Email processing workflow
│   │   ├── nodes.py               # Workflow nodes
│   │   └── state.py               # State definitions
│   ├── tools/                     # Agent tools
│   │   ├── email_tools.py         # Gmail operations
│   │   ├── draft_tools.py         # Email drafting & sending
│   │   ├── rag_tools.py           # RAG search & Q&A
│   │   └── calendar_tools.py      # Calendar operations
│   ├── rag/                       # RAG system
│   │   ├── email_store.py         # Vector storage
│   │   ├── vector_search.py       # Semantic search
│   │   └── retriever.py           # Q&A with context
│   ├── gmail/                     # Gmail integration
│   │   ├── auth.py                # OAuth2 authentication
│   │   ├── email_reader.py        # Read & search emails
│   │   └── email_sender.py        # Send emails
│   ├── calendar/                  # Calendar integration
│   │   ├── event_store.py         # Event caching
│   │   └── calendar_manager.py    # Google Calendar API
│   ├── memory/                    # Persistent memory system
│   │   ├── memory_store.py        # 5 types of memory storage
│   │   └── checkpointer.py        # State persistence
│   ├── scheduler/                 # Job scheduling
│   │   ├── job_scheduler.py       # APScheduler integration
│   │   ├── job_store.py           # Job persistence
│   │   └── predefined_jobs.py     # Default scheduled tasks
│   ├── planning/                  # Multi-step planning
│   │   ├── plan_store.py          # Plan persistence
│   │   ├── planner.py             # LLM-powered task decomposition
│   │   └── plan_executor.py       # Step execution engine
│   ├── observability/             # Monitoring & observability
│   │   ├── metrics_collector.py   # Performance metrics
│   │   ├── logger.py              # Structured logging
│   │   └── health_checker.py      # System health checks
│   ├── analytics/                 # Email intelligence
│   │   ├── analytics_store.py     # Analytics data storage
│   │   ├── email_analyzer.py      # Email analysis
│   │   ├── relationship_tracker.py # Communication patterns
│   │   └── insights_generator.py  # Actionable insights
│   ├── evaluation/                # Agent evaluation
│   │   ├── evaluation_store.py    # Test cases & results
│   │   ├── test_runner.py         # Test execution
│   │   ├── metrics_calculator.py  # Performance metrics
│   │   └── llm_evaluator.py       # LLM-as-judge evaluation
│   ├── prompts/                   # System prompts
│   │   └── email_prompts.py       # Agent prompts
│   └── config/                    # Configuration
│       └── llm_config.py          # LLM provider setup
├── tests/                         # Test scripts
├── ui/                            # Streamlit UI components
├── main.py                        # CLI entry point
├── app.py                         # Streamlit web app
├── requirements.txt               # Core dependencies
├── requirements_llm_providers.txt # LLM provider packages
└── *.md                           # Documentation guides
```

## 🛠️ Technology Stack

### Core Framework

- **LangGraph** - Multi-agent orchestration and workflow management
- **LangChain** - LLM framework and tool abstractions
- **Python 3.11.9** - Core programming language

### LLM Providers

- **Ollama** - Local LLM inference (free, private)
- **OpenAI** - GPT-4o, GPT-4o-mini (paid, production)
- **Anthropic** - Claude 3.5 Sonnet (paid, high quality)
- **Hugging Face** - Open source models (free/paid)

### Data & Storage

- **ChromaDB** - Vector database for RAG
- **SentenceTransformers** - Text embeddings (all-MiniLM-L6-v2)
- **SQLite** - Persistent storage (memory, jobs, plans)
- **APScheduler** - Background job scheduling

### APIs & Integration

- **Gmail API** - Email operations with OAuth2
- **Google Cloud** - Authentication and credentials

### UI & Interface

- **Streamlit** - Web UI framework
- **Rich** - CLI formatting and display

## 📚 Documentation

All documentation is located in the **[docs/](docs/)** folder. See **[docs/README.md](docs/README.md)** for complete documentation index.

### Phase Guides

- **[PHASE2_GUIDE.md](docs/PHASE2_GUIDE.md)** - LangGraph agent integration
- **[PHASE3_RAG_GUIDE.md](docs/PHASE3_RAG_GUIDE.md)** - RAG memory system with ChromaDB
- **[PHASE4_HITL_GUIDE.md](docs/PHASE4_HITL_GUIDE.md)** - Human-in-the-loop workflows
- **[PHASE5_MULTI_AGENT_GUIDE.md](docs/PHASE5_MULTI_AGENT_GUIDE.md)** - Multi-agent system
- **[PHASE6_MEMORY_GUIDE.md](docs/PHASE6_MEMORY_GUIDE.md)** - Persistent memory system
- **[PHASE7_SCHEDULER_GUIDE.md](PHASE7_SCHEDULER_GUIDE.md)** - Job scheduling system
- **[PHASE8_PLANNING_GUIDE.md](PHASE8_PLANNING_GUIDE.md)** - Multi-step planning
- **[PHASE9_CALENDAR_GUIDE.md](PHASE9_CALENDAR_GUIDE.md)** - Calendar integration
- **[PHASE10_OBSERVABILITY_GUIDE.md](PHASE10_OBSERVABILITY_GUIDE.md)** - Monitoring & observability
- **[PHASE11_EMAIL_INTELLIGENCE_GUIDE.md](PHASE11_EMAIL_INTELLIGENCE_GUIDE.md)** - Email analytics & intelligence
- **[PHASE12_EVALUATION_GUIDE.md](PHASE12_EVALUATION_GUIDE.md)** - Agent evaluation framework

### Setup & Configuration

- **[LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md)** - LLM provider configuration
- **[GMAIL_SETUP.md](GMAIL_SETUP.md)** - Gmail API setup
- **[OLLAMA_MODEL_GUIDE.md](OLLAMA_MODEL_GUIDE.md)** - Ollama model selection
- **[STREAMLIT_UI_GUIDE.md](STREAMLIT_UI_GUIDE.md)** - Web UI usage
- **[DAILY_DIGEST_GUIDE.md](DAILY_DIGEST_GUIDE.md)** - Daily email digest

### Educational Resources

- **[PROJECT_LEARNING_GUIDE.md](PROJECT_LEARNING_GUIDE.md)** - Complete learning guide for all phases
- **[FUTURE_PHASES_ROADMAP.md](FUTURE_PHASES_ROADMAP.md)** - Future enhancements

## 🎯 Use Cases

### Email Management

- Read and search emails with natural language
- Semantic search across email history
- Generate daily email digests
- Extract action items and deadlines

### AI-Powered Drafting

- Draft professional emails with context
- Generate replies to existing emails
- Multiple tone options (professional, friendly, formal)
- Human approval before sending (HITL)

### Knowledge Retrieval

- Ask questions about email content
- Find information across conversations
- Summarize email threads
- Track project discussions

### Task Management

- Extract action items from emails
- Identify deadlines and commitments
- Track pending tasks
- Generate task summaries

## 🚦 Development Phases

### ✅ Phase 1: Gmail Integration

- OAuth2 authentication
- Email reading and searching
- Basic Gmail API operations

### ✅ Phase 2: LangGraph Agent

- ReAct agent with tool calling
- Natural language email queries
- Interactive conversation mode

### ✅ Phase 3: RAG Memory System

- Vector storage with ChromaDB
- Semantic email search
- RAG-powered question answering
- Action item extraction

### ✅ Phase 4: Human-in-the-Loop

- Email draft generation
- Human approval workflow
- Feedback-based regeneration
- Safe email sending

### ✅ Phase 5: Multi-Agent System

- Supervisor agent for routing
- Specialized email agent
- Knowledge agent for RAG
- Multi-turn conversations

### ✅ Phase 6: Persistent Memory

- 5 types of memory storage
- Conversation history tracking
- User preferences management
- Episodic and semantic memory
- LangGraph checkpointer integration

### ✅ Phase 7: Scheduled Autonomous Jobs

- APScheduler-based job system
- Cron and interval scheduling
- Job persistence in SQLite
- Predefined jobs (daily digest, email checks)
- Job management (add, remove, pause, resume)

### ✅ Phase 8: Multi-Step Planning

- LLM-powered task decomposition
- Dependency management between steps
- Action handler system (email, search, analyze, draft)
- Plan execution engine
- Progress tracking and error recovery

### ✅ Phase 9: Calendar Integration

- Google Calendar API integration
- Event store with SQLite caching
- 6 calendar tools (list, create, update, delete, search, find slots)
- Conflict detection and scheduling
- Recurring event support

### ✅ Phase 10: Observability & Monitoring

- Metrics collector (performance, usage, errors)
- Structured logging with context
- Health checker (system, dependencies, resources)
- Real-time monitoring and alerting
- Performance tracking and optimization

### ✅ Phase 11: Email Intelligence & Analytics

- Analytics store (sender patterns, response times)
- Email analyzer (sentiment, urgency, categories)
- Relationship tracker (communication frequency)
- Insights generator (actionable recommendations)
- Long-term trend analysis

### ✅ Phase 12: Agent Evaluation Framework

- Evaluation store (test cases, runs, results)
- Test runner (automated test execution)
- Metrics calculator (accuracy, performance, trends)
- LLM evaluator (LLM-as-judge evaluation)
- User feedback collection and analysis

### 🔮 Future Phases

- Phase 13: Voice interface
- Phase 14: Document analysis
- Phase 15: Mobile app
- Phase 16: Advanced analytics dashboard

See [FUTURE_PHASES_ROADMAP.md](docs/FUTURE_PHASES_ROADMAP.md) for details.

## 🧪 Testing

All test files are located in the `tests/` folder.

### Run All Tests

```bash
# Test memory system
python tests/test_memory_system.py

# Test RAG system
python tests/test_rag_system.py

# Test HITL workflow
python tests/test_hitl_workflow.py

# Test multi-agent system
python tests/test_multi_agent.py

# Test scheduler
python tests/test_scheduler.py

# Test planning
python tests/test_planning.py

# Test calendar
python tests/test_calendar.py

# Test observability
python tests/test_observability.py

# Test analytics
python tests/test_analytics.py

# Test evaluation
python tests/test_evaluation.py

# Test Ollama setup
python tests/test_ollama_setup.py
```

### Test Coverage

- ✅ Gmail authentication and operations
- ✅ LangGraph workflow execution
- ✅ RAG vector search and Q&A
- ✅ HITL draft approval flow
- ✅ Multi-agent routing and coordination
- ✅ Memory persistence
- ✅ Cost tracking

## 💰 Cost Considerations

### Free Options

- **Ollama**: Completely free, runs locally
- **Hugging Face**: Free tier available

### Paid Options (Estimated Monthly Costs)

**Light Usage** (1,000 requests/day):

- OpenAI (gpt-4o-mini): ~$18/month
- Claude (3.5 Sonnet): ~$90/month

**Medium Usage** (5,000 requests/day):

- OpenAI (gpt-4o-mini): ~$90/month
- Claude (3.5 Sonnet): ~$450/month

**Cost Optimization Tips**:

1. Use Ollama for development (free)
2. Choose gpt-4o-mini for production (best value)
3. Implement caching for repeated queries
4. Set appropriate max_tokens limits
5. Monitor usage with built-in cost tracking

See [LLM_PROVIDER_GUIDE.md](LLM_PROVIDER_GUIDE.md) for detailed cost analysis.

## 🤝 Contributing

Contributions are welcome! Areas for contribution:

- New specialized agents (Calendar, Tasks, Documents)
- Additional LLM provider integrations
- UI/UX improvements
- Performance optimizations
- Documentation enhancements
- Test coverage expansion

**Process**:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

**"Ollama connection refused"**

```bash
# Start Ollama server
ollama serve
```

**"Gmail authentication failed"**

- Delete `token.json` and re-authenticate
- Check `credentials.json` is in project root
- Verify Gmail API is enabled in Google Cloud Console

**"ChromaDB collection not found"**

```bash
# Index emails first
python -c "from app.tools.rag_tools import store_recent_emails; store_recent_emails(50)"
```

**"High OpenAI costs"**

- Switch to `gpt-4o-mini` model
- Reduce `LLM_MAX_TOKENS` in .env
- Use Ollama for development

### Getting Help

1. Check the relevant guide in documentation
2. Review `.env.example` for configuration
3. Run test scripts to verify setup
4. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, LLM provider)

## 🙏 Acknowledgments

- **LangChain** team for the excellent LLM framework
- **LangGraph** for powerful agent orchestration
- **Ollama** for making local LLMs accessible
- **Streamlit** for the intuitive UI framework
- **ChromaDB** for efficient vector storage
- **OpenAI**, **Anthropic**, **Hugging Face** for LLM APIs

## 📊 Project Stats

- **Total Lines of Code**: ~15,000+
- **Agents**: 4 (Supervisor, Email, Knowledge, Memory)
- **Tools**: 25+ specialized tools
- **Workflows**: 3 (Multi-agent, HITL, Email)
- **Test Scripts**: 12 comprehensive test suites
- **Documentation**: 20+ detailed guides
- **Phases Completed**: 12 major phases
- **Database Tables**: 15+ (Memory, Jobs, Plans, Calendar, Analytics, Evaluation)

---

**Built with ❤️ using LangGraph, LangChain, and modern AI technologies**

**Version**: 2.0.0
**Last Updated**: 2026-06-17
**Status**: Production Ready ✅
