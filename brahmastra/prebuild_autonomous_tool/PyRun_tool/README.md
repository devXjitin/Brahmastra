# 🐍 PyRun Tool - Python Code Execution

> Execute Python code dynamically with **full system access** for Brahmastra AI Agents.

⚠️ **Warning:** This tool has unrestricted code execution. Use responsibly.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Security Considerations](#security-considerations)

---

## Overview

PyRun Tool provides Brahmastra AI agents with the ability to execute **any Python code** dynamically. It supports file operations, network requests, subprocess commands, and all standard Python capabilities.

### Key Characteristics

- **Full Python Execution**: No restrictions on code execution
- **All Imports Allowed**: Any Python module can be imported
- **Output Capture**: Captures stdout, stderr, and return values
- **Parallel Execution**: Batch execution with ThreadPoolExecutor
- **Timeout Protection**: Configurable execution timeout

---

## Features

| Feature | Description |
|---------|-------------|
| 🐍 **Unrestricted Execution** | Execute any Python code |
| 📦 **All Imports** | Import any installed module |
| 📊 **Output Capture** | Capture stdout, stderr, return values |
| 🔄 **Parallel Execution** | Run multiple code snippets concurrently |
| ⏱️ **Timeout Protection** | Default 30 seconds, configurable |
| 📝 **JSON Results** | Structured output format |

### Supported Operations

| Category | Examples |
|----------|----------|
| 📁 File System | Read/write files, create directories |
| 🌐 Network | HTTP requests, API calls, web scraping |
| 📊 Data Processing | Pandas, NumPy operations |
| 🔧 System | Subprocess, os operations |
| 🧮 Calculations | Mathematical operations |
| 🤖 ML/AI | Model inference, data analysis |

---

## Installation

```bash
# No additional installation required
# Uses Python 3.7+ standard library

# Optional: Install additional packages for extended capabilities
pip install requests pandas numpy
```

---

## Quick Start

### With Agent

```python
from brahmastra.prebuild_autonomous_tool import PyRunTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
pyrun = PyRunTool()

# Create agent and add tool
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm, verbose=True)
agent.add_tools(pyrun)

# Use agent
result = agent.invoke("Calculate the factorial of 20 using Python")
print(result)
```

### Direct Usage

```python
from brahmastra.prebuild_autonomous_tool.PyRun_tool import create_pyrun_tool

# Create tool with custom settings
tool = create_pyrun_tool(timeout=60, capture_output=True)

# Execute code
code = ["import math", "print(math.factorial(20))"]
result = tool.function(code=code)
print(result)
```

---

## API Reference

### PyRunTool Class

```python
class PyRunTool:
    """
    Python Code Execution Tool
    
    Provides full Python execution capabilities.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        capture_output: bool = True,
        allow_imports: bool = True
    ):
        """
        Initialize PyRun Tool.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
            capture_output: Whether to capture stdout/stderr (default: True)
            allow_imports: Whether to allow import statements (default: True)
        """
```

### Factory Function

```python
def create_pyrun_tool(
    timeout: int = 30,
    capture_output: bool = True,
    allow_imports: bool = True
) -> Tool:
    """
    Create a Python code execution tool.
    
    Args:
        timeout: Maximum execution time in seconds (default: 30)
        capture_output: Whether to capture stdout/stderr (default: True)
        allow_imports: Whether to allow import statements (default: True)
    
    Returns:
        Tool object for Python code execution
    """
```

### Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | list | Yes | List of Python code strings to execute |

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `timeout` | int | `30` | Max execution time in seconds |
| `capture_output` | bool | `True` | Capture stdout/stderr |
| `allow_imports` | bool | `True` | Allow import statements |

### Return Format

```json
{
  "status": "success",
  "total_executions": 1,
  "results": [
    {
      "status": "success",
      "code": "print('Hello World')",
      "stdout": "Hello World\n",
      "stderr": "",
      "return_value": null,
      "error": null
    }
  ]
}
```

### Error Response

```json
{
  "status": "error",
  "total_executions": 1,
  "results": [
    {
      "status": "error",
      "code": "invalid code",
      "stdout": "",
      "stderr": "Traceback...",
      "return_value": null,
      "error": "SyntaxError: invalid syntax"
    }
  ]
}
```

---

## Examples

### Basic Calculations

```python
# Mathematical operations
result = agent.invoke("Calculate 2^100 using Python")
# Executes: print(2**100)

# Factorial
result = agent.invoke("What is the factorial of 50?")
# Executes: import math; print(math.factorial(50))

# Complex calculation
result = agent.invoke("Calculate the first 20 Fibonacci numbers")
# Executes:
# def fib(n):
#     a, b = 0, 1
#     for _ in range(n):
#         yield a
#         a, b = b, a + b
# print(list(fib(20)))
```

### File Operations

```python
# Read file
result = agent.invoke("Read the contents of config.json")
# Executes:
# with open('config.json', 'r') as f:
#     print(f.read())

# Write file
result = agent.invoke("Create a file called output.txt with 'Hello World'")
# Executes:
# with open('output.txt', 'w') as f:
#     f.write('Hello World')
# print('File created successfully')

# List directory
result = agent.invoke("List all Python files in the current directory")
# Executes:
# import glob
# for f in glob.glob('*.py'):
#     print(f)
```

### Network Operations

```python
# HTTP GET request
result = agent.invoke("Fetch data from https://api.github.com")
# Executes:
# import requests
# response = requests.get('https://api.github.com')
# print(response.json())

# Download file
result = agent.invoke("Download https://example.com/file.txt")
# Executes:
# import requests
# response = requests.get('https://example.com/file.txt')
# with open('file.txt', 'wb') as f:
#     f.write(response.content)
# print('Downloaded successfully')
```

### Data Processing

```python
# Pandas operations
result = agent.invoke("Load data.csv and show first 5 rows")
# Executes:
# import pandas as pd
# df = pd.read_csv('data.csv')
# print(df.head())

# Data analysis
result = agent.invoke("Calculate statistics for data.csv")
# Executes:
# import pandas as pd
# df = pd.read_csv('data.csv')
# print(df.describe())

# JSON processing
result = agent.invoke("Parse and pretty-print config.json")
# Executes:
# import json
# with open('config.json') as f:
#     data = json.load(f)
# print(json.dumps(data, indent=2))
```

### System Information

```python
# Platform info
result = agent.invoke("Get system platform information")
# Executes:
# import platform
# print(f"System: {platform.system()}")
# print(f"Release: {platform.release()}")
# print(f"Python: {platform.python_version()}")

# Environment variables
result = agent.invoke("Show PATH environment variable")
# Executes:
# import os
# print(os.environ.get('PATH'))

# Current working directory
result = agent.invoke("What is the current working directory?")
# Executes:
# import os
# print(os.getcwd())
```

### Subprocess Execution

```python
# Run shell command
result = agent.invoke("Run 'dir' command and show output")
# Executes:
# import subprocess
# result = subprocess.run(['cmd', '/c', 'dir'], capture_output=True, text=True)
# print(result.stdout)

# Check Python version
result = agent.invoke("Check installed Python version via command line")
# Executes:
# import subprocess
# result = subprocess.run(['python', '--version'], capture_output=True, text=True)
# print(result.stdout)
```

---

## Parallel Execution

PyRun Tool supports batch execution with parallel processing:

```python
# Multiple code snippets executed in parallel
code_snippets = [
    "import time; time.sleep(1); print('Task 1 done')",
    "import time; time.sleep(1); print('Task 2 done')",
    "import time; time.sleep(1); print('Task 3 done')"
]

# All execute concurrently
result = pyrun_tool.function(code=code_snippets)
```

### Execution Flow

```
Code Snippets → ThreadPoolExecutor → Parallel Execution → Collected Results
      ↓                ↓                    ↓                   ↓
  [code1,         (max 5 workers)      Run concurrently    JSON output
   code2,                                                   with all
   code3]                                                   results
```

---

## Security Considerations

### ⚠️ Risk Level: HIGH

This tool can execute **any Python code**, including:

- File system modifications (read/write/delete)
- Network operations (HTTP requests, sockets)
- System commands (subprocess)
- Module imports (any installed package)
- Environment access

### Best Practices

1. **Always use verbose mode** to review code before execution:
   ```python
   agent = Create_ReAct_Agent(llm=llm, verbose=True)
   ```

2. **Run in isolated environments** (containers, VMs)

3. **Implement code filtering** for production:
   ```python
   # Example: Custom wrapper with filtering
   def safe_pyrun(code):
       blocked = ['os.remove', 'shutil.rmtree', 'subprocess.run']
       for blocked_op in blocked:
           if blocked_op in code:
               return "Operation blocked for safety"
       return pyrun_tool(code)
   ```

4. **Set appropriate timeouts**:
   ```python
   pyrun = PyRunTool(timeout=10)  # 10 second limit
   ```

5. **Monitor execution** and outputs

6. **Limit package availability** if needed:
   ```python
   # Run in virtual environment with limited packages
   ```

---

## Comparison with PSExec

| Aspect | PyRunTool | PSExecTool |
|--------|-----------|------------|
| **Language** | Python | PowerShell |
| **Platform** | Cross-platform | Windows only |
| **Use Case** | Data processing, APIs | System administration |
| **Network** | requests, urllib | Invoke-WebRequest |
| **Files** | open(), pathlib | Get-ChildItem |

### When to Use Which

- **PyRunTool**: Data processing, API calls, cross-platform tasks, calculations
- **PSExecTool**: Windows-specific tasks, system administration, audio control

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import error | Ensure package is installed (`pip install package`) |
| Timeout | Increase timeout parameter or optimize code |
| Permission denied | Check file/directory permissions |
| Unicode errors | Use proper encoding in file operations |

### Debug Mode

```python
# Enable verbose output
agent = Create_ReAct_Agent(llm=llm, verbose=True)

# Or check results directly
import json
result = pyrun_tool.function(code=["print('test')"])
data = json.loads(result)
print(data['results'][0]['stdout'])
print(data['results'][0]['stderr'])
```

---

## License

Part of the **Brahmastra Framework** - MIT License

---

**Author:** devxJitin  
**Version:** 1.0.0
