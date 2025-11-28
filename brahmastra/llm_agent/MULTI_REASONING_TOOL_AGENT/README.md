# Multi Tool Agent

AI agent that executes multiple tools simultaneously for maximum efficiency.
This agent can run multiple independent tools at the same time or execute the same tool with different parameters.

## Features

- **Parallel Tool Execution**: Run multiple independent tools at the same time
- **Batch Parameter Execution**: Execute the same tool with multiple parameter sets
- **Sequential Execution**: Handle dependent tasks when needed
- **Configurable Workers**: Control the number of parallel executions
- **Error Handling**: Per-tool error handling without stopping the entire execution
- **Verbose Mode**: Detailed logging of all operations

## Installation

```bash
pip install Brahmastra
```

## Import

```python
from brahmastra.llm_agent import Create_MultiToolAgent
from brahmastra.llm_provider import OpenAI_llm
from brahmastra.core import tool
```

## Use Cases

### 1. Parallel Independent Calls

Execute multiple different tools simultaneously when they don't depend on each other:

```python
@tool
def google_search(query: str) -> str:
    """Search Google for information"""
    return f"Google results for {query}"

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for information"""
    return f"Wikipedia results for {query}"

@tool
def news_search(query: str) -> str:
    """Search news articles"""
    return f"News results for {query}"

llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_MultiToolAgent(llm=llm, max_workers=5, verbose=True)
agent.add_tools(google_search, wikipedia_search, news_search)

# Agent will execute all three search tools in parallel
result = agent.invoke("Search for information about Python in Google, Wikipedia, and News")
```

### 2. Batch Parameter Calls

Execute the same tool with multiple different parameters:

```python
@tool
def analyze_website(url: str) -> str:
    """Analyze a website for SEO"""
    return f"Analysis of {url}"

llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_MultiToolAgent(llm=llm, max_workers=10, verbose=True)
agent.add_tools(analyze_website)

# Agent will execute analyze_website multiple times in parallel with different URLs
result = agent.invoke(
    "Analyze these websites: google.com, github.com, stackoverflow.com, python.org, and openai.com"
)
```

### 3. Mixed Execution

Combine both parallel and batch execution:

```python
@tool
def fetch_stock_price(symbol: str) -> str:
    """Get current stock price"""
    return f"Stock price for {symbol}: $100"

@tool
def fetch_company_info(symbol: str) -> str:
    """Get company information"""
    return f"Company info for {symbol}"

@tool
def fetch_news(symbol: str) -> str:
    """Get latest news about a company"""
    return f"News for {symbol}"

llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_MultiToolAgent(llm=llm, max_workers=10, verbose=True)
agent.add_tools(fetch_stock_price, fetch_company_info, fetch_news)

# Agent will execute multiple tools for multiple stocks in parallel
result = agent.invoke(
    "Get stock prices, company info, and latest news for AAPL, GOOGL, and MSFT"
)
```

## Configuration

### Parameters

- **llm**: Language model instance (required)
- **tools**: List of tools to add (optional)
- **max_workers**: Maximum number of parallel executions (default: 5)
- **max_iterations**: Maximum thinking iterations (default: 10)
- **verbose**: Enable detailed logging (default: False)
- **agent_introduction**: Custom introduction prompt (default: "")

### Example

```python
agent = Create_MultiReasoningToolAgent(
    llm=llm,
    max_workers=10,           # Run up to 10 tools in parallel
    max_iterations=15,        # Allow up to 15 thinking rounds
    verbose=True,             # Show detailed logs including reasoning
    agent_introduction="You are a research assistant specialized in data gathering."
)
```

## How It Works

1. **Agent reasons about the request** and determines which tools to use
2. **Strategic execution planning**:
   - Analyzes tool dependencies
   - Decides on execution mode: `parallel`, `batch`, or `sequential`
   - Optimizes for efficiency
3. **Parallel execution** using ThreadPoolExecutor
4. **Result aggregation** and presentation to the user

## Response Format

The agent returns:

```python
{
    "final_answer": "The comprehensive answer combining all tool results",
    "history": [
        {
            "thought": "Agent's reasoning about tool selection and execution strategy",
            "execution_mode": "parallel",
            "actions": [...],
            "results": [...]
        }
    ],
    "iterations": 3
}
```

## Best Practices

1. **Set appropriate max_workers**: More workers = faster execution, but more resource usage
2. **Use verbose mode during development**: Helps understand agent behavior and reasoning
3. **Design independent tools**: Tools that don't need sequential execution benefit most
4. **Handle errors gracefully**: Each tool execution is isolated - one failure won't stop others
5. **Provide clear tool descriptions**: Helps the agent make better strategic decisions

## Comparison with Other Agents

| Feature | Multi Reasoning Tool | ReAct | Tool Calling | Reasoning |
|---------|---------------------|-------|--------------|-----------|
| Strategic Reasoning | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| Tool Execution | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| Parallel Execution | ✅ Yes | ❌ No | ❌ No | ❌ N/A |
| Batch Parameters | ✅ Yes | ❌ No | ❌ No | ❌ N/A |
| Sequential Execution | ✅ Yes | ✅ Yes | ✅ Yes | ❌ N/A |
| Speed (independent tasks) | ⚡ Very Fast | 🐢 Slow | 🐢 Slow | ⚡ Fast |
| Resource Usage | 📊 Higher | 📊 Lower | 📊 Lower | 📊 Lower |

## When to Use

**Use Multi Reasoning Tool Agent when:**

- You need strategic reasoning about tool selection and execution strategy
- You need to gather information from multiple sources simultaneously
- You're processing multiple similar items (batch processing)
- Speed is critical and tasks are independent
- You have sufficient system resources for parallel execution
- You want to see the agent's thought process

**Use other agents when:**

- Tasks must be strictly sequential (use ReAct)
- You're on resource-constrained systems
- You only need to call one tool at a time (use Tool Calling)
- You need pure reasoning without tools (use Reasoning)

## Key Differentiator

The **Multi Reasoning Tool Agent** uniquely combines:

1. **Strategic thinking** about tool selection
2. **Execution optimization** (parallel/batch/sequential)
3. **Multi-tool coordination** for complex tasks

This makes it ideal for complex tasks requiring both intelligent decision-making and efficient execution.
