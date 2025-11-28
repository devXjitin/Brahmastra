# 🛠️ Brahmastra Utilities

Internal utilities for the Brahmastra framework.

## 📦 Components

### AgentLogger

A clean, minimal logger for agent operations with LangChain-style verbose output.

```python
from brahmastra.utils.logger import AgentLogger

# Create logger
logger = AgentLogger(verbose=True, agent_name="My Agent")

# Log agent lifecycle
logger.agent_start("What is AI?")
logger.iteration(1)
logger.thought("I need to search for information...")
logger.action("wikipedia_search", {"query": "artificial intelligence"})
logger.observation("AI is a branch of computer science...")
logger.agent_finish("AI stands for Artificial Intelligence...")
```

#### Features

- 🎨 Color-coded output (auto-detects terminal support)
- 📊 Clean, minimal formatting
- 🔄 Iteration tracking
- ✅ Success/error indicators
- 🎯 LangChain-style verbose output

#### Output Example

```
> Entering My Agent
  Input: What is AI?

[1] Iteration
  Thought: I need to search for information...
  Action: wikipedia_search
    ✓ wikipedia_search: AI is a branch...

> Finished My Agent
  Output: AI stands for Artificial Intelligence...
```

---

### Tool Executor

Utility for executing tools with error handling.

```python
from brahmastra.utils.tool_executor import Tool_Executor

# Create executor
executor = Tool_Executor(tools=[tool1, tool2])

# Execute tool
result = executor.execute("tool_name", {"param": "value"})
```

---

## 📁 Directory Structure

```
utils/
├── logger.py          # AgentLogger class
└── tool_executor.py   # Tool_Executor class
```

---

**Author:** devxJitin  
**Version:** 1.0.0  
**Part of the Brahmastra Framework**
