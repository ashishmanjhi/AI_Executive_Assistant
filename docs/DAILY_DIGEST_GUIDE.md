# Daily Email Digest Feature Guide

## Overview

The Daily Email Digest feature uses a **Map-Reduce architecture** to efficiently process large volumes of emails (100+) and generate a comprehensive, categorized summary report.

## Architecture

### Map-Reduce Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    FETCH EMAILS (100+)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      MAP PHASE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Batch 1      │  │ Batch 2      │  │ Batch N      │      │
│  │ (15 emails)  │  │ (15 emails)  │  │ (15 emails)  │      │
│  │      ↓       │  │      ↓       │  │      ↓       │      │
│  │  Summary 1   │  │  Summary 2   │  │  Summary N   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    REDUCE PHASE                              │
│         Combine all batch summaries into                     │
│         comprehensive daily digest                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CATEGORIZED DAILY REPORT                        │
│  🚨 Urgent  📅 Meetings  💰 Finance  💼 Work                │
│  👤 Personal  📋 Other  ✅ Action Items                      │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Efficient Batch Processing

- **Batch Size**: 15 emails per batch
- **Optimized for**: LLM context window limitations
- **Scalability**: Handles 100+ emails without performance degradation

### 2. Smart Categorization

The system automatically categorizes emails into:

| Category     | Icon | Description                                   |
| ------------ | ---- | --------------------------------------------- |
| Urgent       | 🚨   | Time-sensitive, requires immediate action     |
| Meetings     | 📅   | Calendar invites, schedules, meeting requests |
| Finance      | 💰   | Invoices, payments, financial matters         |
| Work         | 💼   | Projects, tasks, professional communications  |
| Personal     | 👤   | Non-work related emails                       |
| Other        | 📋   | Newsletters, notifications, misc              |
| Action Items | ✅   | Tasks requiring follow-up                     |

### 3. AI-Powered Summarization

- **Model**: qwen3:4b (Ollama)
- **Temperature**: 0.3 (focused, consistent summaries)
- **Context-Aware**: Understands email relationships and priorities

## Usage

### Interactive Mode

Start the assistant in interactive mode:

```bash
python main.py
```

Then ask for a daily digest:

```
You: Generate my daily email digest
You: Give me a comprehensive summary of today's inbox
You: Show me today's email report
```

### Example Output

```
📧 Daily Email Digest - June 15, 2026
### Example Output

```

📧 Daily Email Digest - June 15, 2026

```

```
