# 🤖 Brahmastra LLM Agents

This module provides various AI agent implementations, each designed to solve specific problems that other agents couldn't handle effectively.

## 🔄 Evolution of Agents: Problems & Solutions

Understanding why each agent exists helps you choose the right one for your task.

---

### 1️⃣ Tool-Calling Agent (The Foundation)

**The Starting Point**
The simplest agent that can call tools based on user requests.

```python
from brahmastra.llm_agent import Create_ToolCalling_Agent

agent = Create_ToolCalling_Agent(llm=llm, verbose=True)
agent.add_tools(calculator, search_tool)
result = agent.invoke("Calculate 25 * 4")
```

**✅ What it does well:**

- Simple, direct tool invocation
- Fast execution for single tasks
- Easy to understand and debug

**❌ Problems it has:**

- **No reasoning** - Just calls tools without thinking
- **Single tool per turn** - Can't handle complex queries needing multiple tools
- **Weak learning from results** - Doesn't adapt based on tool outputs (LLM -> Reasoning)

---

### 2️⃣ ReAct Agent (Adding Reasoning)

**Solution:** Adds explicit reasoning before each action

The ReAct Agent was created to solve the "no reasoning" problem. It follows a **Thought → Action → Observation** loop.

```python
from brahmastra.llm_agent import Create_ReAct_Agent

agent = Create_ReAct_Agent(llm=llm, verbose=True, max_iterations=15)
agent.add_tools(wikipedia, calculator)
result = agent.invoke("What is the population of France and what's 10% of it?")
```

**How it solves Tool-Calling Agent's problems:**

| Problem | Solution |
|---------|----------|
| No reasoning | Explicit "Thought" step before each action |
| No learning | "Observation" step analyzes results before next action |
| Blind execution | Decides next step based on previous results |

**✅ What it does well:**

- Step-by-step reasoning
- Learns from tool outputs
- Handles multi-step problems
- Self-corrects when tools return unexpected results

**❌ Problems it still has:**

- **Sequential execution only** - One tool at a time, slow for independent tasks
- **Inefficient for parallel tasks** - If you need Wikipedia AND YouTube, it does them one by one
- **Overhead for simple tasks** - Too much thinking for straightforward queries

---

### 3️⃣ Multi-Tool Agent (Adding Parallelism)

**Solution:** Execute multiple tools simultaneously

The Multi-Tool Agent was created to solve the "sequential bottleneck" problem. When tasks are independent, why wait?

```python
from brahmastra.llm_agent import Create_MultiToolAgent

agent = Create_MultiToolAgent(llm=llm, verbose=True, max_workers=5)
agent.add_tools(wikipedia, youtube, calculator)
result = agent.invoke("Find info about AI on Wikipedia and YouTube, also calculate 100*50")
```

**How it solves ReAct Agent's problems:**

| Problem | Solution |
|---------|----------|
| Sequential execution | Parallel execution with thread pool |
| One tool at a time | Batch multiple tools simultaneously |
| Slow for independent tasks | Identifies independent tasks and runs them together |

**Execution Modes:**

- **Parallel**: Multiple different tools at once
- **Batch**: Same tool with different parameters
- **Sequential**: When results depend on each other

**✅ What it does well:**

- ⚡ 3-5x faster for multi-tool queries
- Smart dependency detection
- Automatic result aggregation
- Still maintains reasoning capabilities

**❌ Problems it still has:**

- **Needs tools** - Can't handle pure reasoning tasks
- **Overkill for thinking tasks** - Not optimized for deep analysis without tools

---

### 4️⃣ Reasoning Agent (Pure Thinking)

**Solution:** Deep reasoning without tool overhead

The Reasoning Agent was created for tasks that don't need tools at all - just deep thinking.

```python
from brahmastra.llm_agent import Create_Reasoning_Agent

agent = Create_Reasoning_Agent(llm=llm, verbose=True)
result = agent.invoke("Explain the implications of quantum computing on cryptography")
```

**How it solves the "everything needs tools" problem:**

| Problem | Solution |
|---------|----------|
| Tool overhead for thinking tasks | No tools, pure reasoning |
| Wasted cycles on tool detection | Direct to reasoning |
| Complex setup for simple analysis | Minimal configuration |

**✅ What it does well:**

- Deep, focused reasoning
- Optimized for thinking-heavy LLMs (o1, DeepSeek-R1)
- Structured step-by-step output
- No tool complexity

**❌ Limitations:**

- Cannot access external information
- Not suitable for tasks requiring real-time data

---

## 📊 Agent Comparison Matrix

| Feature | Tool-Calling | ReAct | Multi-Tool | Reasoning |
|---------|--------------|-------|------------|-----------|
| **Reasoning** | ❌ None | ✅ Explicit | ✅ Strategic | ✅ Deep |
| **Tool Execution** | ✅ Single | ✅ Sequential | ✅ Parallel | ❌ None |
| **Speed** | ⚡ Fast | 🐢 Slow | ⚡⚡ Fastest | ⚡ Fast |
| **Complexity** | Low | Medium | High | Low |
| **Best For** | Simple tasks | Multi-step | Complex queries | Analysis |

---

## 🎯 Which Agent Should You Use?

```flow
START
  │
  ▼
Does your task need external data/tools?
  │
  ├─ NO → Use Reasoning Agent
  │
  └─ YES
      │
      ▼
    Is it a simple, single-tool task?
      │
      ├─ YES → Use Tool-Calling Agent
      │
      └─ NO
          │
          ▼
        Are the sub-tasks independent?
          │
          ├─ YES → Use Multi-Tool Agent (parallel)
          │
          └─ NO → Use ReAct Agent (sequential reasoning)
```

---

## 🔧 Quick Decision Guide

| Your Task | Recommended Agent | Why |
|-----------|-------------------|-----|
| "Calculate 25 * 4" | Tool-Calling | Simple, single tool |
| "What's the capital of France?" | Tool-Calling | Single lookup |
| "Find France's capital and its population" | ReAct | Sequential dependency |
| "Search Wikipedia AND YouTube for AI" | Multi-Tool | Independent parallel tasks |
| "Compare AI tutorials from YouTube and Wikipedia" | Multi-Tool | Parallel fetch, then analyze |
| "Explain quantum computing" | Reasoning | Pure thinking, no tools needed |
| "Analyze the pros and cons of renewable energy" | Reasoning | Deep analysis |

---

## 📦 Available Agents Summary

| Agent | Import | Best For |
|-------|--------|----------|
| Tool-Calling | `Create_ToolCalling_Agent` | Simple, single tool tasks |
| ReAct | `Create_ReAct_Agent` | Sequential multi-step reasoning |
| Multi-Tool | `Create_MultiToolAgent` | Parallel tool execution |
| Reasoning | `Create_Reasoning_Agent` | Pure reasoning without tools |

---

## 🚀 Code Examples

### Tool-Calling Agent

```python
from brahmastra.llm_agent import Create_ToolCalling_Agent
from brahmastra.llm_provider import GoogleLLM

llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ToolCalling_Agent(llm=llm, verbose=True)
agent.add_tools(calculator)
result = agent.invoke("What is 125 * 8?")
```

### ReAct Agent

```python
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm, verbose=True, max_iterations=15)
agent.add_tools(wikipedia, calculator)
result = agent.invoke("What is the population of Tokyo and what's 15% of it?")
```

### Multi-Tool Agent

```python
from brahmastra.llm_agent import Create_MultiToolAgent
from brahmastra.llm_provider import GoogleLLM

llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_MultiToolAgent(llm=llm, verbose=True, max_workers=5)
agent.add_tools(wikipedia, youtube, calculator)
result = agent.invoke("Find AI info on Wikipedia and YouTube, calculate 50*100")
```

### Reasoning Agent

```python
from brahmastra.llm_agent import Create_Reasoning_Agent
from brahmastra.llm_provider import GoogleLLM

llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_Reasoning_Agent(llm=llm, verbose=True)
result = agent.invoke("What are the ethical implications of AI in healthcare?")
```

---

## ⚙️ Common Parameters

All agents share these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | LLM | Required | Language model instance |
| `tools` | List | `[]` | Initial tools list |
| `verbose` | bool | `False` | Show execution details |
| `max_iterations` | int | `10` | Maximum reasoning loops |

---

## 📁 Directory Structure

```structure
llm_agent/
├── __init__.py
├── README.md
├── TOOL_CALLING_AGENT/
│   ├── base.py
│   ├── prompt.py
│   └── README.md
├── REACT_AGENT/
│   ├── base.py
│   ├── prompt.py
│   └── README.md
├── MULTI_REASONING_TOOL_AGENT/
│   ├── base.py
│   ├── prompt.py
│   └── README.md
└── REASONING_AGENT/
    ├── base.py
    ├── prompt.py
    └── README.md
```

---

**Author:** devxJitin  
**Version:** 1.0.0  
**Part of the Brahmastra Framework**
