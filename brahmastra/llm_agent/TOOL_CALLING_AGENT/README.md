# Tool Calling Agent

AI agent that executes tools based on LLM decisions with structured JSON responses.

## Features

- **Structured Tool Execution**: Tools are called based on LLM reasoning
- **JSON Response Format**: Clean, parsable output format
- **Memory Support**: Maintains conversation history
- **Custom Prompts**: Configure agent personality
- **Verbose Logging**: Track agent decisions and actions
- **Flexible Tool Integration**: Add tools dynamically

## Installation

```bash
pip install Brahmastra
```

## Import

```python
from brahmastra.llm_agent import Create_ToolCalling_Agent
from brahmastra.llm_provider import OpenAI_llm
from brahmastra.core import tool
```

## Quick Start

```python
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression"""
    return str(eval(expression))

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city"""
    return f"Weather in {city}: Sunny, 75°F"

# Create agent
llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_ToolCalling_Agent(llm=llm, verbose=True)

# Add tools
agent.add_tools(calculator, get_weather)

# Use agent
result = agent.invoke("What's 25 * 4 and what's the weather in Paris?")
print(result)
```

## Usage

### Basic Tool Calling

```python
@tool
def search_database(query: str) -> str:
    """Search the knowledge database"""
    return f"Results for: {query}"

llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_ToolCalling_Agent(llm=llm)
agent.add_tools(search_database)

response = agent.invoke("Find information about Python programming")
```

### With Memory

```python
from brahmastra.memory import ConversationalWindowMemory

memory = ConversationalWindowMemory(window_size=10)
agent = Create_ToolCalling_Agent(llm=llm, memory=memory)
agent.add_tools(calculator)

# First conversation
agent.invoke("Calculate 100 + 50")

# Memory retained
agent.invoke("Multiply that by 2")  # Agent remembers previous result
```

### Custom Agent Personality

```python
custom_prompt = "You are a helpful financial advisor assistant."

agent = Create_ToolCalling_Agent(
    llm=llm, 
    prompt=custom_prompt,
    verbose=True
)
```

### Multiple Tools

```python
@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return a / b

agent = Create_ToolCalling_Agent(llm=llm)
agent.add_tools(add, multiply, divide)

result = agent.invoke("Calculate (10 + 5) * 3 / 2")
```

## API Reference

### Create_ToolCalling_Agent

```python
Create_ToolCalling_Agent(
    llm,                    # LLM instance with generate_response() method
    verbose: bool = False,  # Enable detailed logging
    prompt: str = None,     # Custom agent introduction
    memory = None           # Memory instance for conversation history
)
```

### Methods

#### add_tools(*tools)

Add one or more tools to the agent.

```python
agent.add_tools(tool1, tool2, tool3)
```

#### add_tool(name, description, function, parameters)

Add a tool with custom configuration.

```python
agent.add_tool(
    name="calculator",
    description="Performs math calculations",
    function=calc_func,
    parameters={"expression": {"type": "str", "required": True}}
)
```

#### invoke(user_input: str) -> str

Execute the agent with user input.

```python
result = agent.invoke("Your question here")
```

#### add_memory(memory)

Add or update memory instance.

```python
agent.add_memory(ConversationalBufferMemory())
```

#### clear_memory()

Clear conversation history.

```python
agent.clear_memory()
```

#### get_memory_history()

Get conversation history.

```python
history = agent.get_memory_history()
```

## Response Format

The agent returns structured JSON responses:

```json
{
  "Tool call": "calculator",
  "Tool Parameters": {"expression": "25 * 4"},
  "Final Response": "The result is 100"
}
```

## When to Use

**Use Tool Calling Agent when:**

- You need structured, parsable responses
- Tools should be called sequentially with reasoning
- You want clear visibility into tool execution
- Memory/conversation history is important

**Use other agents when:**

- You need parallel tool execution (Multi Reasoning Tool Agent)
- You need iterative reasoning loops (ReAct Agent)
- You need planning and execution phases (Plan-Execute Agent)
- You need deep reasoning before action (Reasoning Agent)

## Error Handling

```python
try:
    result = agent.invoke("Your query")
except ValueError as e:
    print(f"Invalid response format: {e}")
except Exception as e:
    print(f"Execution error: {e}")
```

## Examples

### Weather Assistant

```python
@tool
def get_weather(city: str) -> str:
    """Get current weather"""
    return f"Weather in {city}: Sunny, 72°F"

@tool
def get_forecast(city: str, days: int = 7) -> str:
    """Get weather forecast"""
    return f"{days}-day forecast for {city}"

agent = Create_ToolCalling_Agent(
    llm=llm,
    prompt="You are a helpful weather assistant.",
    verbose=True
)
agent.add_tools(get_weather, get_forecast)

result = agent.invoke("What's the weather in New York and show me the 5-day forecast?")
```

### Research Assistant

```python
@tool
def search_papers(topic: str) -> str:
    """Search academic papers"""
    return f"Found 10 papers about {topic}"

@tool
def summarize_paper(paper_id: str) -> str:
    """Summarize a research paper"""
    return f"Summary of paper {paper_id}"

agent = Create_ToolCalling_Agent(
    llm=llm,
    prompt="You are an academic research assistant.",
    memory=ConversationalBufferMemory()
)
agent.add_tools(search_papers, summarize_paper)

# Multi-turn conversation
agent.invoke("Find papers about machine learning")
agent.invoke("Summarize the first paper")
```

## Notes

- The agent executes one tool at a time (sequential execution)
- Custom prompts should only contain agent personality, not tool instructions
- Tool instructions and response format are added automatically
- Memory is optional but recommended for conversational interactions
- Verbose mode provides detailed execution logs using clean LangChain-style output
