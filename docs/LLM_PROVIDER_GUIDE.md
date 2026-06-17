# LLM Provider Configuration Guide

## Overview

The AI Executive Assistant supports multiple LLM providers with easy switching via environment variables. This guide covers setup, configuration, and cost tracking for all supported providers.

## Supported Providers

| Provider             | Type  | Cost      | Speed     | Quality   | Best For                     |
| -------------------- | ----- | --------- | --------- | --------- | ---------------------------- |
| **Ollama**           | Local | Free      | Fast      | Good      | Development, Privacy         |
| **OpenAI**           | API   | Paid      | Very Fast | Excellent | Production, Reliability      |
| **Anthropic Claude** | API   | Paid      | Fast      | Excellent | Production, Complex Tasks    |
| **Hugging Face**     | API   | Free/Paid | Varies    | Varies    | Open Source, Experimentation |

## Quick Start

### 1. Choose Your Provider

**For Development** (Recommended):

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:latest
```

**For Production**:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 2. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install provider-specific packages
# For OpenAI:
pip install langchain-openai tiktoken

# For Claude:
pip install langchain-anthropic

# For Hugging Face:
pip install langchain-huggingface huggingface-hub

# For all providers:
pip install -r requirements_llm_providers.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Provider-Specific Setup

### Ollama (Local - Free)

**Advantages**:

- ✅ Free to use
- ✅ Fast inference
- ✅ Privacy (runs locally)
- ✅ No API limits
- ✅ Works offline

**Setup**:

1. **Install Ollama**:

   ```bash
   # Download from https://ollama.ai
   # Or use package manager
   ```

2. **Pull a Model**:

   ```bash
   ollama pull llama3.2:latest
   # Or other models:
   ollama pull mistral:latest
   ollama pull qwen3:4b
   ollama pull codellama:latest
   ```

3. **Start Ollama Server**:

   ```bash
   ollama serve
   ```

4. **Configure .env**:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2:latest
   ```

**Available Models**:

- `llama3.2:latest` - Meta's Llama 3.2 (Recommended)
- `mistral:latest` - Mistral 7B
- `qwen3:4b` - Qwen 3 4B (Fast, smaller)
- `codellama:latest` - Code-focused
- `phi3:latest` - Microsoft Phi-3

**Cost**: $0.00 (Free)

---

### OpenAI (API - Paid)

**Advantages**:

- ✅ Excellent quality
- ✅ Very fast
- ✅ Reliable
- ✅ Large context windows
- ✅ Function calling support

**Setup**:

1. **Get API Key**:
   - Go to https://platform.openai.com/api-keys
   - Create new API key
   - Copy the key (starts with `sk-`)

2. **Install Package**:

   ```bash
   pip install langchain-openai tiktoken
   ```

3. **Configure .env**:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

**Available Models**:

| Model           | Input Cost | Output Cost | Context | Best For                    |
| --------------- | ---------- | ----------- | ------- | --------------------------- |
| `gpt-3.5-turbo` | $0.50/1M   | $1.50/1M    | 16K     | Budget, Simple tasks        |
| `gpt-4o-mini`   | $0.15/1M   | $0.60/1M    | 128K    | **Recommended**, Best value |
| `gpt-4o`        | $5.00/1M   | $15.00/1M   | 128K    | High quality, Fast          |
| `gpt-4-turbo`   | $10.00/1M  | $30.00/1M   | 128K    | Complex tasks               |
| `gpt-4`         | $30.00/1M  | $60.00/1M   | 8K      | Legacy, Expensive           |

**Recommendation**: Use `gpt-4o-mini` for best cost/performance ratio.

**Cost Tracking**: Automatic (built-in)

---

### Anthropic Claude (API - Paid)

**Advantages**:

- ✅ Excellent quality
- ✅ Large context (200K tokens)
- ✅ Strong reasoning
- ✅ Good at following instructions
- ✅ Ethical AI focus

**Setup**:

1. **Get API Key**:
   - Go to https://console.anthropic.com/
   - Create account and get API key
   - Copy the key (starts with `sk-ant-`)

2. **Install Package**:

   ```bash
   pip install langchain-anthropic
   ```

3. **Configure .env**:
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```

**Available Models**:

| Model                        | Input Cost | Output Cost | Context | Best For                |
| ---------------------------- | ---------- | ----------- | ------- | ----------------------- |
| `claude-3-haiku-20240307`    | $0.25/1M   | $1.25/1M    | 200K    | Fast, Budget            |
| `claude-3-sonnet-20240229`   | $3.00/1M   | $15.00/1M   | 200K    | Balanced                |
| `claude-3-5-sonnet-20241022` | $3.00/1M   | $15.00/1M   | 200K    | **Recommended**, Latest |
| `claude-3-opus-20240229`     | $15.00/1M  | $75.00/1M   | 200K    | Highest quality         |

**Recommendation**: Use `claude-3-5-sonnet-20241022` for best balance.

**Cost Tracking**: Automatic (built-in)

---

### Hugging Face (API - Free/Paid)

**Advantages**:

- ✅ Open source models
- ✅ Free tier available
- ✅ Many model options
- ✅ Community support
- ✅ Customizable

**Setup**:

1. **Get API Key**:
   - Go to https://huggingface.co/settings/tokens
   - Create new token
   - Copy the token (starts with `hf_`)

2. **Install Package**:

   ```bash
   pip install langchain-huggingface huggingface-hub
   ```

3. **Configure .env**:
   ```env
   LLM_PROVIDER=huggingface
   HUGGINGFACE_API_KEY=hf_your-key-here
   HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
   ```

**Available Models**:

| Model                                | Size | Cost | Best For              |
| ------------------------------------ | ---- | ---- | --------------------- |
| `mistralai/Mistral-7B-Instruct-v0.2` | 7B   | Free | General purpose       |
| `meta-llama/Llama-2-7b-chat-hf`      | 7B   | Free | Chat, Conversation    |
| `google/flan-t5-xxl`                 | 11B  | Free | Instruction following |
| `tiiuae/falcon-7b-instruct`          | 7B   | Free | General purpose       |

**Note**: Some models require:

- Model approval/access request
- Paid inference endpoints for faster response
- Specific licenses

**Cost**: Free tier available, paid for faster inference

---

## Configuration Examples

### Example 1: Development Setup (Free)

```env
# .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

**Use Case**: Local development, testing, privacy-sensitive work

---

### Example 2: Production with OpenAI (Cost-Effective)

```env
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
ENABLE_COST_TRACKING=true
```

**Use Case**: Production deployment, best cost/performance

**Estimated Cost**: ~$0.10-0.50 per 1000 requests (depending on usage)

---

### Example 3: Production with Claude (High Quality)

```env
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
ENABLE_COST_TRACKING=true
```

**Use Case**: Production, complex reasoning, large context needs

**Estimated Cost**: ~$0.30-1.50 per 1000 requests

---

### Example 4: Hybrid Setup (Fallback)

```env
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Fallback to Ollama if OpenAI fails
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

**Use Case**: Production with local fallback for reliability

---

## Using the LLM Config in Code

### Basic Usage

```python
from app.config.llm_config import create_llm, track_usage

# Create LLM instance (uses .env configuration)
llm = create_llm()

# Use the LLM
response = llm.invoke("What is the capital of France?")

# Track usage and cost
cost = track_usage(response)
print(f"Cost: ${cost:.6f}")
```

### Custom Configuration

```python
from app.config.llm_config import create_llm

# Override temperature and max tokens
llm = create_llm(temperature=0.3, max_tokens=1000)

# Enable streaming
llm = create_llm(streaming=True)
```

### Get Usage Statistics

```python
from app.config.llm_config import get_usage_stats, reset_usage_stats

# Get current usage
stats = get_usage_stats()
print(f"Total cost: ${stats['total_cost_usd']}")
print(f"Total tokens: {stats['total_tokens']}")

# Reset statistics
reset_usage_stats()
```

### Get LLM Information

```python
from app.config.llm_config import get_llm_info

info = get_llm_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"Temperature: {info['temperature']}")
```

---

## Cost Tracking

### Automatic Tracking

Cost tracking is automatic for paid providers:

```python
from app.config.llm_config import create_llm, track_usage, get_usage_stats

llm = create_llm()

# Make requests
for query in queries:
    response = llm.invoke(query)
    track_usage(response)  # Automatically tracks cost

# View total cost
stats = get_usage_stats()
print(f"Total cost: ${stats['total_cost_usd']:.4f}")
```

### Cost Estimation

**Example Calculation**:

```
Query: "Summarize these 10 emails"
Input tokens: ~2,000 (emails content)
Output tokens: ~500 (summary)

OpenAI (gpt-4o-mini):
- Input: 2,000 / 1,000,000 * $0.15 = $0.0003
- Output: 500 / 1,000,000 * $0.60 = $0.0003
- Total: $0.0006 per request

1,000 requests = $0.60
10,000 requests = $6.00
```

### Cost Optimization Tips

1. **Use Smaller Models**: `gpt-4o-mini` instead of `gpt-4`
2. **Reduce Max Tokens**: Set appropriate limits
3. **Cache Results**: Don't re-process same queries
4. **Batch Processing**: Process multiple items together
5. **Use Ollama for Dev**: Free local testing

---

## Switching Providers

### Method 1: Environment Variable

Simply change `LLM_PROVIDER` in `.env`:

```env
# Switch from Ollama to OpenAI
LLM_PROVIDER=openai  # was: ollama
```

Restart the application.

### Method 2: Multiple Environments

Create different `.env` files:

```bash
.env.development  # Ollama
.env.production   # OpenAI
.env.staging      # Claude
```

Load appropriate file:

```bash
# Development
cp .env.development .env

# Production
cp .env.production .env
```

### Method 3: Runtime Switching

```python
import os
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['OPENAI_MODEL'] = 'gpt-4o-mini'

# Reload config
from app.config.llm_config import get_llm_config
config = get_llm_config()
llm = config.create_llm()
```

---

## Troubleshooting

### Issue: "Import langchain_openai could not be resolved"

**Solution**:

```bash
pip install langchain-openai tiktoken
```

### Issue: "OPENAI_API_KEY not found"

**Solution**:

1. Check `.env` file exists
2. Verify `OPENAI_API_KEY=sk-...` is set
3. Restart application

### Issue: "Ollama connection refused"

**Solution**:

```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: High costs with OpenAI

**Solutions**:

1. Switch to `gpt-4o-mini` (cheaper)
2. Reduce `LLM_MAX_TOKENS`
3. Implement caching
4. Use Ollama for development

### Issue: Slow responses with Hugging Face

**Solutions**:

1. Use paid inference endpoints
2. Switch to smaller model
3. Use Ollama or OpenAI instead

---

## Best Practices

### 1. Development vs Production

**Development**:

- Use Ollama (free, fast, local)
- Test with smaller models
- No cost concerns

**Production**:

- Use OpenAI or Claude (reliable, fast)
- Monitor costs
- Implement caching
- Set up alerts

### 2. Security

```env
# ❌ DON'T commit .env to git
# ✅ DO use .env.example as template
# ✅ DO use environment variables in production
# ✅ DO rotate API keys regularly
```

### 3. Cost Management

- Set up billing alerts in provider dashboard
- Monitor usage with `get_usage_stats()`
- Implement rate limiting
- Cache frequent queries
- Use appropriate model for task

### 4. Model Selection

| Task              | Recommended Model   | Reason         |
| ----------------- | ------------------- | -------------- |
| Simple queries    | gpt-4o-mini, Ollama | Cost-effective |
| Complex reasoning | claude-3-5-sonnet   | Best quality   |
| Code generation   | gpt-4o, codellama   | Specialized    |
| Large context     | claude-3-5-sonnet   | 200K context   |
| Budget-conscious  | gpt-4o-mini, Ollama | Lowest cost    |

---

## Migration Guide

### From Ollama to OpenAI

1. **Get OpenAI API Key**
2. **Install Package**:
   ```bash
   pip install langchain-openai tiktoken
   ```
3. **Update .env**:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```
4. **Restart Application**

No code changes needed!

### From OpenAI to Claude

1. **Get Anthropic API Key**
2. **Install Package**:
   ```bash
   pip install langchain-anthropic
   ```
3. **Update .env**:
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```
4. **Restart Application**

---

## FAQ

**Q: Which provider should I use?**

A:

- **Development**: Ollama (free, local)
- **Production (budget)**: OpenAI gpt-4o-mini
- **Production (quality)**: Claude 3.5 Sonnet
- **Open Source**: Hugging Face

**Q: How much will it cost?**

A: Depends on usage. Example:

- 1,000 requests/day with gpt-4o-mini: ~$0.60/day = $18/month
- 1,000 requests/day with claude-3-5-sonnet: ~$3/day = $90/month

**Q: Can I use multiple providers?**

A: Yes! The system supports automatic fallback. Set primary provider in `.env`, and it will fallback to Ollama if unavailable.

**Q: Is my data sent to external servers?**

A:

- **Ollama**: No, runs locally
- **OpenAI/Claude/HF**: Yes, sent to their servers
- For privacy: Use Ollama

**Q: How do I reduce costs?**

A:

1. Use gpt-4o-mini instead of gpt-4
2. Implement caching
3. Reduce max_tokens
4. Use Ollama for development
5. Batch process when possible

---

## Support

For issues:

1. Check this guide
2. Review `.env.example`
3. Check provider documentation:
   - OpenAI: https://platform.openai.com/docs
   - Anthropic: https://docs.anthropic.com
   - Hugging Face: https://huggingface.co/docs

---

**Made with Bob** 🤖

**Version**: 1.0  
**Last Updated**: 2026-06-17
