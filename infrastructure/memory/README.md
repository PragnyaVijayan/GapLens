# GapLens Memory System

This directory contains the persistent memory storage for the GapLens AI system.

## Directory Structure

```
infrastructure/memory/
├── sessions/          # Session-specific memory files
├── long_term/         # Long-term persistent memory
├── logs/             # Memory operation logs
└── README.md         # This file
```

## Memory Types

### 1. Session Memory (`sessions/`)
- **Purpose**: Stores temporary memory for active user sessions
- **Format**: JSON files named `session_YYYYMMDD_HHMMSS.json`
- **Content**: 
  - User questions and intents
  - Agent reasoning steps
  - Research findings
  - Analysis results
  - Final decisions
- **Lifetime**: Persists across system restarts but may be cleaned up

### 2. Long-term Memory (`long_term/`)
- **Purpose**: Stores persistent knowledge and patterns
- **Format**: JSON files organized by category
- **Content**:
  - Frequently used skill mappings
  - Common project patterns
  - Team composition templates
  - Learning from past analyses
- **Lifetime**: Permanent storage, manually managed

### 3. Memory Logs (`logs/`)
- **Purpose**: Tracks all memory operations for debugging
- **Format**: Daily log files (`memory_YYYYMMDD.log`)
- **Content**:
  - Memory read/write operations
  - Agent reasoning patterns used
  - Error logs
  - Performance metrics

## Memory Entry Structure

Each memory entry contains:

```json
{
  "id": "agent_timestamp",
  "timestamp": "ISO timestamp",
  "agent": "agent_name",
  "content": "actual_data",
  "reasoning_pattern": "COT|REWOO|REACT|TOT|AGENT",
  "reasoning_steps": ["step1", "step2", ...],
  "confidence": 0.8,
  "metadata": {
    "question": "original_question",
    "method": "analysis_method"
  }
}
```

## Reasoning Patterns

The system supports multiple reasoning patterns:

- **COT (Chain of Thought)**: Step-by-step logical reasoning
- **REWOO**: Reason, Evaluate, Work, Observe, Optimize
- **REACT**: Reason, Evaluate, Act, Check, Think
- **TOT (Tree of Thoughts)**: Multiple approach exploration
- **AGENT**: Multi-agent collaborative reasoning

## Usage

### In Code
```python
from core.memory_system import get_memory_system

# Get memory instances
long_term_memory, memory_logger = get_memory_system()

# Save session
session_file = long_term_memory.save_session(session_memory)

# Save to long-term memory
long_term_memory.save_to_long_term("skill_mapping", data, "skills")

# Retrieve data
data = long_term_memory.get_long_term_data("skill_mapping", "skills")
```

### File Management
- **Sessions**: Automatically cleaned up after 30 days
- **Long-term**: Manually managed, backup recommended
- **Logs**: Rotated monthly, keep last 12 months

## Performance Considerations

- Memory files are JSON for human readability
- Large datasets should be chunked
- Consider compression for long-term storage
- Regular cleanup of old session files
- Monitor log file sizes

## Security Notes

- Memory files may contain sensitive information
- Ensure proper file permissions
- Consider encryption for production use
- Regular security audits recommended
