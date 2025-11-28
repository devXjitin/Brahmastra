# 🎯 Brahmastra Core Module

The core module provides the fundamental building blocks for creating tools in the Brahmastra framework.

## 📦 Components

### Tool Class

The `Tool` class represents a callable tool with metadata that can be used by AI agents.

```python
from brahmastra.core import Tool

# Create a tool manually
my_tool = Tool(
    name="my_tool",
    description="Description of what this tool does",
    function=my_function,
    parameters={
        "query": {
            "type": "str",
            "description": "The search query",
            "required": True
        },
        "limit": {
            "type": "int",
            "description": "Maximum results",
            "required": False
        }
    }
)
```

### @tool Decorator

The `@tool` decorator provides an easy way to create tools from functions:

```python
from brahmastra.core import tool

@tool
def calculator(expression: str) -> str:
    """
    Performs mathematical calculations on expressions.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        The result of the calculation
    """
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# The decorator automatically extracts:
# - name: from function name
# - description: from docstring
# - parameters: from type hints
```

## ✨ Features

- **Automatic Parameter Extraction** - Type hints are automatically converted to tool parameters
- **Docstring Parsing** - Function docstrings become tool descriptions
- **Type Validation** - Parameters are validated based on type hints
- **Flexible Definition** - Use decorator or class-based approach

## 📝 Parameter Types

Supported parameter types:

| Python Type | Tool Type | Example |
|-------------|-----------|---------|
| `str` | `str` | `query: str` |
| `int` | `int` | `limit: int = 10` |
| `float` | `float` | `temperature: float = 0.7` |
| `bool` | `bool` | `verbose: bool = False` |
| `list` | `list` | `items: list` |
| `dict` | `dict` | `config: dict` |
| `Optional[T]` | `T` (optional) | `name: Optional[str] = None` |

## 🔧 Advanced Usage

### Custom Parameter Descriptions

```python
from brahmastra.core import Tool

def search(query: str, max_results: int = 10) -> str:
    """Search for items."""
    return f"Searching for {query}, limit {max_results}"

my_tool = Tool(
    name="advanced_search",
    description="Advanced search with custom parameters",
    function=search,
    parameters={
        "query": {
            "type": "str",
            "description": "The search query string",
            "required": True
        },
        "max_results": {
            "type": "int",
            "description": "Maximum number of results (1-100)",
            "required": False
        }
    }
)
```

### Tool with Complex Return Types

```python
from brahmastra.core import tool
import json

@tool
def get_weather(city: str, units: str = "celsius") -> str:
    """
    Get weather information for a city.
    
    Args:
        city: City name
        units: Temperature units (celsius/fahrenheit)
    
    Returns:
        JSON formatted weather data
    """
    # Your implementation
    weather_data = {
        "city": city,
        "temperature": 25,
        "units": units,
        "condition": "Sunny"
    }
    return json.dumps(weather_data, indent=2)
```

## 📚 API Reference

### Tool Class

```python
Tool(
    name: str,                    # Tool name (used by agents)
    description: str,             # What the tool does
    function: Callable,           # The actual function to call
    parameters: Dict[str, Dict]   # Parameter definitions
)
```

### @tool Decorator

```python
@tool
def function_name(param1: type, param2: type = default) -> return_type:
    """Docstring becomes description."""
    pass
```

---

**Author:** devxJitin  
**Version:** 1.0.0  
**Part of the Brahmastra Framework**
