# 🤖 PSGen Tool - PowerShell Command Generator

> Generate PowerShell commands from natural language using LLM for Brahmastra AI Agents.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Integration with PSExec](#integration-with-psexec)
- [Best Practices](#best-practices)

---

## Overview

PSGen Tool uses Large Language Models (LLMs) to convert natural language requests into ready-to-execute PowerShell commands. This enables agents to understand user intent and generate appropriate system commands.

### Key Characteristics

- **Natural Language Input**: Describe what you want in plain English
- **LLM-Powered**: Uses any Brahmastra LLM provider
- **Clean Output**: Returns only the command, no explanations
- **Optimized Prompts**: Pre-configured for common operations
- **Auto-Cleanup**: Removes markdown, backticks, and formatting

---

## Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language** | Convert plain English to PowerShell |
| 🤖 **Multi-LLM Support** | Works with Gemini, OpenAI, Claude, Groq, Ollama |
| 🧹 **Auto-Cleanup** | Removes formatting from LLM output |
| 🎯 **Optimized Prompts** | Pre-built patterns for common tasks |
| ✅ **Ready-to-Execute** | Commands work directly in PowerShell |

### Supported Request Types

| Category | Example Requests |
|----------|------------------|
| 🎵 Audio | "Check volume", "Set volume to 50%" |
| 📊 System | "Show CPU usage", "Memory status" |
| 📁 Files | "List PDFs in Documents", "Find large files" |
| 🌐 Network | "Test internet connection", "Download file" |
| 🔧 Services | "Check if Bluetooth is running" |

---

## Installation

```bash
# Install LLM provider
pip install google-generativeai  # For Gemini
# or
pip install openai              # For OpenAI
# or
pip install anthropic           # For Claude
```

---

## Quick Start

### With Agent

```python
from brahmastra.prebuild_autonomous_tool import PSGenTool, PSExecTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create LLM
llm = GoogleLLM(model="gemini-2.0-flash")

# Create tools
psgen = PSGenTool(llm=llm)
psexec = PSExecTool()  # To execute generated commands

# Create agent
agent = Create_ReAct_Agent(llm=llm, verbose=True)
agent.add_tools(psgen, psexec)

# Generate and execute
result = agent.invoke("Generate a command to check CPU usage, then execute it")
```

### Direct Usage

```python
from brahmastra.prebuild_autonomous_tool.PSGen_tool import PSGenTool
from brahmastra.llm_provider import GoogleLLM

# Create LLM and tool
llm = GoogleLLM(model="gemini-2.0-flash")
psgen = PSGenTool(llm=llm)

# Generate command
result = psgen.tool.function(request="Check current disk space")
print(result)
# Output: {"status": "success", "command": "Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free"}
```

---

## API Reference

### PSGenTool Class

```python
class PSGenTool:
    """
    PowerShell Command Generator Tool
    
    Uses LLM to convert natural language to PowerShell commands.
    """
    
    def __init__(self, llm):
        """
        Initialize PSGen Tool.
        
        Args:
            llm: LLM instance with generate_response method
        """
```

### Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `request` | str | Yes | Natural language description of desired command |

### Return Format

```json
{
  "status": "success",
  "request": "Check CPU usage",
  "command": "Get-Counter '\\Processor(_Total)\\% Processor Time'",
  "error": null
}
```

### Error Response

```json
{
  "status": "error",
  "request": "Invalid request",
  "command": "",
  "error": "Error generating command: ..."
}
```

---

## Examples

### Volume Control

```python
# Get current volume
result = psgen.tool.function(request="Get the current system volume level")
# Generated: (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100

# Set volume
result = psgen.tool.function(request="Set volume to 75%")
# Generated: $dev = (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume; $dev.MasterVolumeLevelScalar = 0.75; Write-Host "Volume set to 75%"

# Decrease volume
result = psgen.tool.function(request="Lower the volume by 20%")
# Generated: $dev = (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume; $current = $dev.MasterVolumeLevelScalar; $dev.MasterVolumeLevelScalar = [Math]::Max(0, $current - 0.2)
```

### System Information

```python
# CPU usage
result = psgen.tool.function(request="Show current CPU usage percentage")
# Generated: Get-Counter '\Processor(_Total)\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue

# Memory info
result = psgen.tool.function(request="How much memory is available?")
# Generated: Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory

# Disk space
result = psgen.tool.function(request="Show disk space on all drives")
# Generated: Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free
```

### File Operations

```python
# Find files
result = psgen.tool.function(request="Find all MP3 files in my Music folder")
# Generated: Get-ChildItem -Path "$env:USERPROFILE\Music" -Filter "*.mp3" -Recurse

# Large files
result = psgen.tool.function(request="Find files larger than 1GB on C drive")
# Generated: Get-ChildItem -Path "C:\" -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1GB } | Select-Object FullName, @{N='SizeGB';E={[math]::Round($_.Length/1GB,2)}}
```

### Network Operations

```python
# Connectivity test
result = psgen.tool.function(request="Check if I can reach google.com")
# Generated: Test-Connection -ComputerName google.com -Count 2

# IP information
result = psgen.tool.function(request="Show my IP addresses")
# Generated: Get-NetIPAddress | Where-Object { $_.AddressFamily -eq 'IPv4' }

# Download file
result = psgen.tool.function(request="Download a file from https://example.com/file.zip")
# Generated: Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"
```

### Process Management

```python
# Top processes
result = psgen.tool.function(request="Show top 10 processes using most CPU")
# Generated: Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet

# Find process
result = psgen.tool.function(request="Check if Chrome is running")
# Generated: Get-Process -Name chrome -ErrorAction SilentlyContinue | Select-Object Name, CPU, WorkingSet
```

---

## Integration with PSExec

PSGen generates commands, PSExec executes them. Use together for complete automation:

```python
from brahmastra.prebuild_autonomous_tool import PSGenTool, PSExecTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

llm = GoogleLLM(model="gemini-2.0-flash")

# Create both tools
psgen = PSGenTool(llm=llm)
psexec = PSExecTool()

# Agent with both tools
agent = Create_ReAct_Agent(llm=llm, verbose=True)
agent.add_tools(psgen, psexec)

# Now agent can:
# 1. Generate command with PSGen
# 2. Execute it with PSExec
result = agent.invoke("Check how much disk space I have left")
```

### Workflow

```
User Request → PSGen (generate) → PSExec (execute) → Result
     ↓              ↓                    ↓            ↓
"Check CPU"   "Get-Counter..."    Execute PS    "CPU: 45%"
```

---

## Command Cleanup

PSGen automatically cleans LLM responses:

| Input (LLM Output) | Cleaned Output |
|--------------------|----------------|
| `` `Get-Process` `` | `Get-Process` |
| `\`\`\`powershell\nGet-Process\n\`\`\`` | `Get-Process` |
| `Command: Get-Process` | `Get-Process` |
| `Here's the command:\nGet-Process` | `Get-Process` |

---

## Pre-built Prompt Patterns

PSGen includes optimized patterns for common tasks:

```python
# Volume control patterns
"(Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100"

# System info patterns
"Get-Counter '\\Processor(_Total)\\% Processor Time'"
"Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory"

# File operation patterns
"Get-ChildItem -Path 'C:\\Users' -Recurse -File"
"Get-Item 'C:\\path\\to\\file' | Select-Object Name, Length, LastWriteTime"

# Network patterns
"Test-Connection -ComputerName google.com -Count 2"
"Invoke-WebRequest -Uri 'URL' -OutFile 'filename'"
```

---

## Best Practices

### 1. Be Specific

```python
# Good - specific request
result = psgen.tool.function(request="List all .log files larger than 10MB in C:\\Logs")

# Less ideal - vague request
result = psgen.tool.function(request="Find some log files")
```

### 2. Use with PSExec

```python
# Generate then execute for complete automation
agent.add_tools(psgen, psexec)
```

### 3. Review Generated Commands

```python
# Use verbose mode to see generated commands
agent = Create_ReAct_Agent(llm=llm, verbose=True)
```

### 4. Handle Errors

```python
import json

result = psgen.tool.function(request="...")
data = json.loads(result)

if data["status"] == "error":
    print(f"Error: {data['error']}")
else:
    print(f"Command: {data['command']}")
```

---

## Supported LLM Providers

| Provider | Example |
|----------|---------|
| Google Gemini | `GoogleLLM(model="gemini-2.0-flash")` |
| OpenAI | `OpenAILLM(model="gpt-4")` |
| Anthropic Claude | `AnthropicLLM(model="claude-3-opus")` |
| Groq | `GroqLLM(model="mixtral-8x7b")` |
| Ollama | `OllamaLLM(model="llama3")` |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty command generated | Request may be too vague - be more specific |
| Incorrect command | Try rephrasing the request |
| LLM timeout | Increase timeout or use faster model |
| Markdown in output | Should be auto-cleaned; report if persists |

---

## License

Part of the **Brahmastra Framework** - MIT License

---

**Author:** devxJitin  
**Version:** 1.0.0
