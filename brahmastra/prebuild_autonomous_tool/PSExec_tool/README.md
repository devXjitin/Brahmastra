# 💻 PSExec Tool - PowerShell Command Execution

> Execute PowerShell commands with **full system access** for Brahmastra AI Agents.

⚠️ **Warning:** This tool has unrestricted system access. Use responsibly.

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

PSExec Tool provides Brahmastra AI agents with the ability to execute **any PowerShell command** on Windows systems. It includes automatic module installation, timeout protection, and JSON-formatted output.

### Key Characteristics

- **Full System Access**: No restrictions on command execution
- **Auto-Install Modules**: Automatically installs missing PowerShell modules
- **JSON Output**: Results returned in structured JSON format
- **Timeout Protection**: Configurable execution timeout
- **Error Handling**: Comprehensive error capture and reporting

---

## Features

| Feature | Description |
|---------|-------------|
| ⚡ **Unrestricted Execution** | Execute any PowerShell command |
| 🔧 **Auto-Install** | Missing modules installed automatically |
| 📊 **JSON Results** | Structured output with status, stdout, stderr |
| ⏱️ **Timeout Protection** | Default 30 seconds, configurable |
| 🔄 **Batch Execution** | Execute multiple commands |

### Supported Operations

| Category | Examples |
|----------|----------|
| 🎵 Audio | `Get-AudioDevice`, volume control |
| 📁 File System | `Get-ChildItem`, `Copy-Item`, `Remove-Item` |
| 🔧 Registry | `Get-ItemProperty`, `Set-ItemProperty` |
| 📊 System Info | `Get-ComputerInfo`, `Get-WmiObject` |
| 🔄 Processes | `Get-Process`, `Start-Process`, `Stop-Process` |
| 🌐 Network | `Invoke-WebRequest`, `Test-Connection` |
| ⚙️ Services | `Get-Service`, `Start-Service`, `Stop-Service` |

---

## Installation

```bash
# No additional installation required
# Uses Windows PowerShell 5.1+ (pre-installed on Windows)
```

For audio control features:

```powershell
# AudioDeviceCmdlets module (auto-installed by tool)
Install-Module -Name AudioDeviceCmdlets -Force -Scope CurrentUser
```

---

## Quick Start

### With Agent

```python
from brahmastra.prebuild_autonomous_tool import PSExecTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
psexec = PSExecTool()

# Create agent and add tool
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm, verbose=True)
agent.add_tools(psexec)

# Use agent
result = agent.invoke("Get the current CPU usage")
print(result)
```

### Direct Usage

```python
from brahmastra.prebuild_autonomous_tool.PSExec_tool import create_psexec_tool

# Create tool with custom timeout
tool = create_psexec_tool(timeout=60)

# Execute command
result = tool.function(command=["Get-Process | Select-Object -First 5"])
print(result)
```

---

## API Reference

### PSExecTool Class

```python
class PSExecTool:
    """
    PowerShell Command Execution Tool
    
    Provides full system access for executing PowerShell commands.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize PSExec Tool.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
        """
```

### Factory Function

```python
def create_psexec_tool(timeout: int = 30) -> Tool:
    """
    Create a PowerShell command execution tool.
    
    Args:
        timeout: Maximum execution time in seconds (default: 30)
    
    Returns:
        Tool object for PowerShell command execution
    """
```

### Tool Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | list | Yes | List of PowerShell command strings |

### Return Format

```json
{
  "status": "success",
  "total_executions": 1,
  "results": [
    {
      "status": "success",
      "command": "Get-Process | Select-Object -First 5",
      "stdout": "...",
      "stderr": "",
      "exit_code": 0,
      "error": null
    }
  ]
}
```

---

## Examples

### System Information

```python
# Get computer info
result = agent.invoke("Get detailed system information")
# Executes: Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory
```

### Volume Control

```python
# Get current volume
result = agent.invoke("What is the current system volume?")
# Executes: (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100

# Set volume to 50%
result = agent.invoke("Set the system volume to 50%")
# Executes: $vol = (Get-AudioDevice -Playback | Where-Object { $_.Default }).Device.AudioEndpointVolume; $vol.MasterVolumeLevelScalar = 0.5
```

### File Operations

```python
# List files
result = agent.invoke("List all PDF files in my Documents folder")
# Executes: Get-ChildItem -Path "$env:USERPROFILE\Documents" -Filter "*.pdf" -Recurse

# Get file info
result = agent.invoke("Show details of config.json file")
# Executes: Get-Item "config.json" | Select-Object Name, Length, LastWriteTime
```

### Network Operations

```python
# Download file
result = agent.invoke("Download https://example.com/file.zip")
# Executes: Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"

# Test connection
result = agent.invoke("Check if google.com is reachable")
# Executes: Test-Connection -ComputerName google.com -Count 2
```

### Process Management

```python
# List top processes
result = agent.invoke("Show top 10 processes by CPU usage")
# Executes: Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet

# Start application
result = agent.invoke("Open Notepad")
# Executes: Start-Process notepad
```

### Service Management

```python
# List running services
result = agent.invoke("Show all running services")
# Executes: Get-Service | Where-Object { $_.Status -eq 'Running' }

# Check specific service
result = agent.invoke("Is the Windows Update service running?")
# Executes: Get-Service -Name wuauserv
```

---

## Security Considerations

### ⚠️ Risk Level: HIGH

This tool can execute **any PowerShell command**, including:

- System modifications
- File deletion
- Registry changes
- Service control
- Network operations

### Best Practices

1. **Always use verbose mode** to review commands before execution:
   ```python
   agent = Create_ReAct_Agent(llm=llm, verbose=True)
   ```

2. **Run in controlled environments** during development

3. **Implement command filtering** for production:
   ```python
   # Example: Custom wrapper with filtering
   def safe_psexec(command):
       blocked = ['Remove-Item', 'Stop-Service', 'Set-ItemProperty']
       for blocked_cmd in blocked:
           if blocked_cmd.lower() in command.lower():
               return "Command blocked for safety"
       return psexec_tool(command)
   ```

4. **Monitor execution logs** for suspicious activity

5. **Use least privilege principle** - run with minimal required permissions

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Command not recognized" | Module may need installation (usually auto-installed) |
| Timeout errors | Increase timeout parameter |
| Permission denied | Run with appropriate privileges |
| Unicode errors | Output includes proper encoding handling |

### Debug Mode

```python
# Enable verbose output to see exact commands
agent = Create_ReAct_Agent(llm=llm, verbose=True)
```

---

## License

Part of the **Brahmastra Framework** - MIT License

---

**Author:** devxJitin  
**Version:** 1.0.0
