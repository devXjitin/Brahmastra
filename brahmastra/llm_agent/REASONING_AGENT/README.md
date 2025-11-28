# 🎓 Reasoning Agent

A pure reasoning agent for complex logical tasks that don't require external tools.

## Overview

The Reasoning Agent is optimized for tasks that require deep thinking and step-by-step analysis without needing to call external tools. It's particularly effective with reasoning-focused models like OpenAI o1, o3, or DeepSeek-R1.

## Features

- 🧠 Deep reasoning capabilities
- 📊 Step-by-step analysis
- 🎯 Optimized for reasoning models
- 📝 Structured output format
- 💭 Explicit reasoning steps

## Installation

```bash
pip install brahmastra
```

## Usage

```python
from brahmastra.llm_agent import Create_Reasoning_Agent
from brahmastra.llm_provider import GoogleLLM

# Create LLM (works best with reasoning-capable models)
llm = GoogleLLM(model="gemini-2.0-flash")

# Create agent
agent = Create_Reasoning_Agent(
    llm=llm,
    verbose=True
)

# Run query (no tools needed)
result = agent.invoke(
    "Explain the implications of quantum computing on modern cryptography"
)
print(result)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | LLM | Required | Language model instance |
| `verbose` | bool | `False` | Show reasoning steps |
| `agent_introduction` | str | `""` | Custom system prompt |

## Output Format

The agent returns structured reasoning:

```json
{
    "Reasoning Steps": [
        "Step 1: Quantum computing uses qubits...",
        "Step 2: Current cryptography relies on...",
        "Step 3: Shor's algorithm can break...",
        "Step 4: Therefore, the implications are..."
    ],
    "Final Response": "Quantum computing poses significant challenges..."
}
```

## Best For

- Complex logical reasoning
- Mathematical problems
- Analysis and synthesis tasks
- Questions not requiring external data
- Deep explanations

## Recommended Models

For best results, use with reasoning-focused models:

- OpenAI o1, o3
- DeepSeek-R1
- Google Gemini (with thinking)
- Claude 3 Opus

---

**Author:** devxJitin  
**Version:** 1.0.0  
**Part of the Brahmastra Framework**
