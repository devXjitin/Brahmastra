# ⚡ Brahmastra Autonomous Tools

> Professional-grade autonomous tools for Brahmastra AI Agents with real-time system interaction and full system access.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

⚠️ **Warning:** These tools have full system access. Use responsibly in controlled environments.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Available Tools](#-available-tools)
- [Quick Start](#-quick-start)
- [Tool Documentation](#-tool-documentation)
- [Installation](#-installation)
- [Security Notice](#-security-notice)
- [Contributing](#-contributing)

---

## 🎯 Overview

Autonomous Tools are **system-level utilities** designed for real-time interaction with the operating system. Unlike standard tools, these can:

- ✅ **Execute System Commands**: Run PowerShell/Python code directly
- ✅ **Continuous Operation**: Background services that run autonomously
- ✅ **Full System Access**: No restrictions on system operations
- ✅ **LLM Integration**: Optional AI-powered command generation
- ✅ **Real-time Processing**: Immediate execution and response

### Directory Structure

```
prebuild_autonomous_tool/
├── __init__.py                    # Main exports
├── README.md                      # This file
├── speech_recognition_tool/       # Real-time speech-to-text
│   ├── __init__.py
│   ├── base.py
│   └── README.md
├── PSExec_tool/                   # PowerShell command execution
│   ├── __init__.py
│   └── base.py
├── PSGen_tool/                    # LLM-powered PowerShell generation
│   ├── __init__.py
│   └── base.py
└── PyRun_tool/                    # Python code execution
    ├── __init__.py
    └── base.py
```

---

## 📦 Available Tools

| Tool | Description | Requires LLM | Platform |
|------|-------------|--------------|----------|
| **SpeechRecognitionTool** | Real-time speech-to-text with LLM enhancement | Optional | All |
| **PSExecTool** | Execute PowerShell commands with full system access | No | Windows |
| **PSGenTool** | Generate PowerShell from natural language | Yes | Windows |
| **PyRunTool** | Execute Python code dynamically | No | All |

---

## 🚀 Quick Start

### Complete Example

```python
from brahmastra.prebuild_autonomous_tool import (
    SpeechRecognitionTool,
    get_recognized_text,
    PSExecTool,
    PSGenTool,
    PyRunTool
)
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create LLM
llm = GoogleLLM(model="gemini-2.0-flash")

# Create tools
psexec = PSExecTool()           # Execute PowerShell
psgen = PSGenTool(llm=llm)      # Generate PowerShell from NL
pyrun = PyRunTool()             # Execute Python code

# Create agent and add tools
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(psexec, psgen, pyrun)

# Use agent
result = agent.invoke("Get the current system volume level")
```

---

## 📖 Tool Documentation

### 🎤 Speech Recognition Tool

Real-time background speech recognition service with optional LLM enhancement.

**Features:**

- 🎤 Continuous background listening
- 🤖 Optional LLM accuracy enhancement
- 🔇 Configurable silence detection (default: 1.5 seconds)
- 💾 Global variable storage (`RECOGNIZED_TEXT`)
- 🌍 50+ language support
- 🧵 Thread-safe operation

**Quick Start:**

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
from brahmastra.llm_provider import GoogleLLM

# Without LLM (faster, basic accuracy)
speech = SpeechRecognitionTool(auto_start=True)

# With LLM enhancement (slower, better accuracy)
llm = GoogleLLM(model="gemini-2.0-flash")
speech = SpeechRecognitionTool(llm=llm, use_llm=True, auto_start=True)

# Get recognized text
text = get_recognized_text()
# Or
text = speech.get_last_text()

# Stop listening
speech.stop_background_listening()
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | LLM | `None` | LLM instance for text enhancement |
| `language` | str | `"en-US"` | Speech recognition language code |
| `pause_threshold` | float | `1.5` | Seconds of silence before stopping |
| `energy_threshold` | int | `50` | Microphone sensitivity |
| `use_llm` | bool | `True` | Enable LLM enhancement (if LLM provided) |
| `auto_start` | bool | `False` | Start listening on initialization |

**Methods:**

| Method | Description |
|--------|-------------|
| `start_background_listening()` | Start continuous recognition |
| `stop_background_listening()` | Stop recognition |
| `get_last_text()` | Get last recognized text |
| `clear_last_text()` | Clear stored text |
| `get_stats()` | Get usage statistics |

**Architecture:**

```
┌─────────────────────────────────────────────────┐
│              Main Application                    │
│  • Reads RECOGNIZED_TEXT global variable        │
│  • Non-blocking operation                       │
└────────────────────┬────────────────────────────┘
                     │ Thread-safe access
┌────────────────────▼────────────────────────────┐
│         Background Listener Thread               │
│  1. Capture Audio (PyAudio)                     │
│  2. Detect Speech (Voice Activity)              │
│  3. Detect Silence                              │
│  4. Transcribe (Google Speech API)              │
│  5. LLM Enhancement (Optional)                  │
│  6. Update RECOGNIZED_TEXT                      │
└─────────────────────────────────────────────────┘
```

[📖 Full Documentation →](speech_recognition_tool/README.md)

---

### 💻 PSExec Tool - PowerShell Execution

Execute PowerShell commands with **full system access** and no restrictions.

**Features:**

- ⚡ Execute ANY PowerShell command
- 🔧 Auto-install missing modules (e.g., AudioDeviceCmdlets)
- 📊 JSON formatted results
- ⏱️ Configurable timeout
- 🔄 Batch execution support

**Quick Start:**

```python
from brahmastra.prebuild_autonomous_tool import PSExecTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
psexec = PSExecTool()

# Create agent and add tool
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(psexec)

# Agent can now execute any PowerShell command
result = agent.invoke("What is the current CPU usage?")
```

**Provides 1 tool:**

- `powershell_execute` - Execute PowerShell commands

**Capabilities:**

| Category | Examples |
|----------|----------|
| 🎵 Audio Control | `Get-AudioDevice`, volume control |
| 📁 File System | `Get-ChildItem`, `Copy-Item`, `Remove-Item` |
| 🔧 Registry | `Get-ItemProperty`, `Set-ItemProperty` |
| 📊 System Info | `Get-ComputerInfo`, `Get-WmiObject` |
| 🔄 Processes | `Get-Process`, `Start-Process`, `Stop-Process` |
| 🌐 Network | `Invoke-WebRequest`, `Test-Connection` |
| ⚙️ Services | `Get-Service`, `Start-Service`, `Stop-Service` |

**Tool Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | list | List of PowerShell command strings |

**Example Commands:**

```python
# Volume control (auto-installs AudioDeviceCmdlets)
"$dev = (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume; $dev.MasterVolumeLevelScalar * 100"

# System information
"Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory"

# Process list
"Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"

# Download file
"Invoke-WebRequest -Uri 'https://example.com/file.zip' -OutFile 'file.zip'"
```

---

### 🤖 PSGen Tool - PowerShell Generator

Generate PowerShell commands from natural language using LLM.

**Features:**

- 🗣️ Natural language to PowerShell conversion
- 🎯 Context-aware command generation
- ✅ Optimized for output display
- 🧹 Automatic cleanup of LLM response

**Quick Start:**

```python
from brahmastra.prebuild_autonomous_tool import PSGenTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create LLM and tool
llm = GoogleLLM(model="gemini-2.0-flash")
psgen = PSGenTool(llm=llm)

# Create agent and add tool
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(psgen)

# Agent generates and returns PowerShell commands
result = agent.invoke("Generate a command to check system volume")
```

**Provides 1 tool:**

- `powershell_generate` - Generate PowerShell from natural language

**Tool Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `request` | str | Natural language description of desired command |

**Example Requests:**

| Natural Language | Generated Command |
|------------------|-------------------|
| "Check CPU usage" | `Get-Counter '\\Processor(_Total)\\% Processor Time'` |
| "List PDF files in Documents" | `Get-ChildItem -Path "$env:USERPROFILE\Documents" -Filter "*.pdf"` |
| "Get system volume" | `(Get-AudioDevice -Playback \| Where-Object { $_.Default }).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100` |
| "Download file from URL" | `Invoke-WebRequest -Uri "URL" -OutFile "filename"` |

**Note:** Use with `PSExecTool` for a complete solution - PSGen generates commands, PSExec executes them.

---

### 🐍 PyRun Tool - Python Execution

Execute Python code dynamically with **full system access**.

**Features:**

- 🐍 Execute ANY Python code
- 📁 Full file system access
- 🌐 Network operations (HTTP, APIs, web scraping)
- 📊 Capture stdout, stderr, and return values
- 🔄 Parallel batch execution
- ⏱️ Configurable timeout

**Quick Start:**

```python
from brahmastra.prebuild_autonomous_tool import PyRunTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
pyrun = PyRunTool()

# Create agent and add tool
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(pyrun)

# Agent can now execute any Python code
result = agent.invoke("Calculate the factorial of 10 using Python")
```

**Provides 1 tool:**

- `python_execute` - Execute Python code snippets

**Capabilities:**

| Category | Examples |
|----------|----------|
| 📁 File System | Read/write files, create directories |
| 🌐 Network | HTTP requests, API calls, web scraping |
| 📊 Data Processing | Pandas, NumPy operations |
| 🔧 System Commands | subprocess, os operations |
| 🧮 Calculations | Mathematical operations |

**Tool Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | list | List of Python code strings to execute |

**Configuration:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timeout` | int | `30` | Max execution time in seconds |
| `capture_output` | bool | `True` | Capture stdout/stderr |
| `allow_imports` | bool | `True` | Allow import statements |

**Example Code:**

```python
# HTTP request
import requests
response = requests.get('https://api.example.com/data')
print(response.json())

# File operations
with open('output.txt', 'w') as f:
    f.write('Hello World')

# System info
import platform
print(platform.system(), platform.release())
```

---

## 📥 Installation

### Core Dependencies

```bash
# Core Brahmastra
pip install brahmastra
```

### Speech Recognition

```bash
pip install SpeechRecognition pyaudio
```

**Platform-Specific PyAudio Installation:**

```bash
# Windows
pip install pyaudio

# macOS
brew install portaudio
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### LLM Providers (for PSGen and enhanced speech)

```bash
# Google Gemini
pip install google-generativeai

# OpenAI
pip install openai

# Anthropic Claude
pip install anthropic

# Groq
pip install groq

# Ollama (local)
pip install ollama
```

---

## ⚠️ Security Notice

These tools provide **unrestricted system access**:

| Tool | Risk Level | Capabilities |
|------|------------|--------------|
| **PSExecTool** | 🔴 High | Execute ANY PowerShell command |
| **PyRunTool** | 🔴 High | Execute ANY Python code |
| **PSGenTool** | 🟡 Medium | Generates commands from natural language |
| **SpeechRecognitionTool** | 🟢 Low | Microphone access only |

### Best Practices

1. ✅ **Always review agent actions** in verbose mode
2. ✅ **Use in controlled environments** (development, testing)
3. ✅ **Implement safeguards** for production deployments
4. ✅ **Monitor command execution** and outputs
5. ✅ **Limit tool access** based on use case

### Example: Verbose Mode

```python
agent = Create_ReAct_Agent(llm=llm, verbose=True)
agent.add_tools(psexec)

# Now you can see all commands before execution
result = agent.invoke("Show system information")
```

---

## 🤝 Contributing

### Adding a New Autonomous Tool

1. **Create a folder**: `brahmastra/prebuild_autonomous_tool/your_tool_name/`

2. **Implement base.py**:

```python
from brahmastra.core import Tool

def create_your_tool(config: dict) -> Tool:
    """
    Create your autonomous tool.
    
    Args:
        config: Configuration options
    
    Returns:
        Tool object
    """
    def tool_function(param: str) -> str:
        # Implementation with full system access
        return "result"
    
    return Tool(
        name="your_tool_name",
        description="What this tool does",
        function=tool_function,
        parameters={
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        }
    )

class YourTool:
    """Wrapper class for easy integration."""
    
    def __init__(self, **config):
        self.tool = create_your_tool(config)
    
    def __iter__(self):
        yield self.tool
```

3. **Create __init__.py**:

```python
from .base import YourTool, create_your_tool
__all__ = ["YourTool", "create_your_tool"]
```

4. **Update main __init__.py** to export your tool

5. **Add documentation** to this README

---

## 📐 Comparison: Prebuild Tools vs Autonomous Tools

| Aspect | Prebuild Tools | Autonomous Tools |
|--------|----------------|------------------|
| **Purpose** | Information retrieval | System interaction |
| **System Access** | Limited | Full |
| **Example** | Wikipedia search | PowerShell execution |
| **Risk Level** | Low | High |
| **Use Case** | Research, data gathering | Automation, control |

---

## 📄 License

Part of the **Brahmastra Framework** - MIT License

---

**Author:** devxJitin  
**Version:** 1.0.0
