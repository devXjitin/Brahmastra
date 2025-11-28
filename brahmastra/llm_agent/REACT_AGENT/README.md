# 🧠 ReAct Agent

An AI agent that implements the **Re**asoning + **Act**ing paradigm for step-by-step problem solving.

## Overview

The ReAct Agent follows a Thought → Action → Observation loop, where it:
1. **Thinks** about what to do next
2. **Acts** by calling a tool
3. **Observes** the result
4. Repeats until the task is complete

## Features

- 💭 Explicit reasoning steps
- 🔍 Observation-based learning
- 📝 Thought-Action-Observation loop
- 🎯 Goal-directed behavior
- 🔄 Iterative refinement

## Installation

```bash
pip install brahmastra
```

## Usage

```python
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM
from brahmastra.prebuild_tool import WikipediaSearchTool

# Create LLM
llm = GoogleLLM(model="gemini-2.0-flash")

# Create agent
agent = Create_ReAct_Agent(
    llm=llm,
    verbose=True,
    max_iterations=15
)

# Add tools
agent.add_tools(WikipediaSearchTool())

# Run query
result = agent.invoke("What is the capital of France and its population?")
print(result)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | LLM | Required | Language model instance |
| `tools` | List | `[]` | Initial tools list |
| `verbose` | bool | `False` | Show execution details |
| `max_iterations` | int | `10` | Maximum reasoning loops |
| `agent_introduction` | str | `""` | Custom system prompt |

## Execution Flow

```
[1] Iteration
  Thought: I need to find information about France's capital...
  Action: wikipedia_search(query="France capital")
  Observation: Paris is the capital of France...

[2] Iteration
  Thought: Now I need to find the population...
  Action: wikipedia_search(query="Paris population")
  Observation: Paris has a population of 2.1 million...

[3] Iteration
  Thought: I have all the information needed.
  Final Answer: The capital of France is Paris with a population of 2.1 million.
```

## Best For

- Multi-step research tasks
- Questions requiring multiple tool calls
- Tasks needing explicit reasoning
- Problems with sequential dependencies

---

**Author:** devxJitin  
**Version:** 1.0.0  
**Part of the Brahmastra Framework**
