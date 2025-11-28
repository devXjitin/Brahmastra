"""
PSExec Tool - PowerShell Command Execution

A professional-grade tool for executing PowerShell commands with FULL SYSTEM ACCESS.
NO RESTRICTIONS - complete freedom to execute any PowerShell command.

Features:
- Execute ANY PowerShell commands without restrictions
- Full system access (registry, WMI, COM objects, services)
- Audio control (Get-AudioDevice, Set-AudioDevice)
- Process management (Get-Process, Start-Process, Stop-Process)
- File operations (Get-ChildItem, Copy-Item, Remove-Item)
- System information (Get-ComputerInfo, Get-WmiObject)
- Network operations (Invoke-WebRequest, Test-Connection)
- Batch execution with parallel processing
- Capture output and errors
- JSON formatted results

Requires:
- Windows PowerShell 5.1+ or PowerShell 7+

Example:
    >>> from brahmastra.prebuild_autonomous_tool import PSExecTool
    >>> 
    >>> psexec = PSExecTool()
    >>> agent.add_tools(psexec)
"""

from typing import Dict, Optional, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from brahmastra.core import Tool
import subprocess
import json


def execute_powershell_command(
    command: str,
    timeout: int = 30,
    auto_install_modules: bool = True
) -> Dict[str, Any]:
    """
    Execute a single PowerShell command and return results.
    Automatically installs missing modules if needed.
    
    Args:
        command: PowerShell command to execute
        timeout: Maximum execution time in seconds (default: 30)
        auto_install_modules: Auto-install missing modules (default: True)
        
    Returns:
        Dictionary with execution results
    """
    result = {
        "status": "success",
        "command": command[:100] + "..." if len(command) > 100 else command,
        "stdout": "",
        "stderr": "",
        "exit_code": 0,
        "error": None
    }
    
    try:
        # Wrap command to ensure output is captured (Out-String forces text output)
        wrapped_command = f"{command} | Out-String"
        
        # Execute PowerShell command
        process = subprocess.run(
            ["powershell", "-NoProfile", "-Command", wrapped_command],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["exit_code"] = process.returncode
        
        # Check for missing cmdlet/module errors and auto-install
        if process.returncode != 0 and auto_install_modules:
            stderr_lower = process.stderr.lower()
            
            # Detect Get-AudioDevice missing (AudioDeviceCmdlets module)
            if "get-audiodevice" in stderr_lower and "not recognized" in stderr_lower:
                result["stdout"] += "\n[Auto-installing AudioDeviceCmdlets module...]\n"
                
                # Install AudioDeviceCmdlets module
                install_process = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", 
                     "Install-Module -Name AudioDeviceCmdlets -Force -Scope CurrentUser -AllowClobber"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    encoding='utf-8',
                    errors='replace'
                )
                
                if install_process.returncode == 0:
                    result["stdout"] += "[Module installed successfully. Retrying command...]\n"
                    
                    # Retry the original command with output wrapping
                    wrapped_retry = f"{command} | Out-String"
                    retry_process = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", wrapped_retry],
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        encoding='utf-8',
                        errors='replace'
                    )
                    
                    result["stdout"] += retry_process.stdout
                    result["stderr"] = retry_process.stderr
                    result["exit_code"] = retry_process.returncode
                    
                    if retry_process.returncode == 0:
                        result["status"] = "success"
                        result["error"] = None
                    else:
                        result["status"] = "error"
                        result["error"] = f"Command failed after module installation: exit code {retry_process.returncode}"
                else:
                    result["stdout"] += f"[Module installation failed: {install_process.stderr}]\n"
                    result["status"] = "error"
                    result["error"] = f"Failed to install AudioDeviceCmdlets module"
            else:
                result["status"] = "error"
                result["error"] = f"Command exited with code {process.returncode}"
        elif process.returncode != 0:
            result["status"] = "error"
            result["error"] = f"Command exited with code {process.returncode}"
            
    except subprocess.TimeoutExpired:
        result["status"] = "error"
        result["error"] = "Command execution timeout exceeded"
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {str(e)}"
    
    return result


def create_psexec_tool(timeout: int = 30) -> Tool:
    """
    Create a PowerShell command execution tool.
    
    Args:
        timeout: Maximum execution time in seconds (default: 30)
    
    Returns:
        Tool object for PowerShell command execution
    
    Example:
        >>> psexec = create_psexec_tool(timeout=10)
        >>> agent.add_tools(psexec)
    """
    
    def execute_powershell(command: list) -> str:
        """
        Execute PowerShell command(s).
        Always processes commands as a list with parallel execution.
        
        Args:
            command: List of PowerShell command strings (will be joined with newlines)
            
        Returns:
            JSON string with execution results
        """
        # Join all commands with newlines to create a single script
        # This allows multi-line PowerShell scripts to work properly
        script = "\n".join(command)
        
        # Execute the combined script
        result = execute_powershell_command(script, timeout=timeout, auto_install_modules=True)
        
        # Format output
        output = {
            "status": result["status"],
            "total_executions": 1,
            "results": [result]
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    return Tool(
        name="powershell_execute",
        description=(
            "PRIMARY TOOL for ALL Windows system operations. Execute PowerShell commands with FULL SYSTEM ACCESS. "
            "AUTO-INSTALLS missing modules automatically (like AudioDeviceCmdlets for volume control). "
            "ALWAYS use this for: "
            "1) Audio/volume control - IMPORTANT: Use .Device.AudioEndpointVolume.MasterVolumeLevelScalar for volume "
            "   - Get Volume: (Get-AudioDevice -Playback | Where-Object {{ $_.Default -eq $true }}).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100 "
            "   - Set Volume: $vol = (Get-AudioDevice -Playback | Where-Object {{ $_.Default }}).Device.AudioEndpointVolume; $vol.MasterVolumeLevelScalar = 0.75 "
            "   - Note: .Volume property does NOT exist on AudioDevice objects! "
            "2) FILE DOWNLOADS (Invoke-WebRequest, curl, Start-BitsTransfer) "
            "3) System info (Get-ComputerInfo, Get-WmiObject, systeminfo) "
            "4) File listing (Get-ChildItem for directories/files) "
            "5) Processes (Get-Process, Start-Process, Stop-Process, tasklist) "
            "6) Services (Get-Service, Start/Stop-Service) "
            "7) Registry (Get/Set-ItemProperty HKLM:, HKCU:) "
            "8) Network (Test-Connection, Invoke-WebRequest, Get-NetAdapter) "
            "9) Windows features, environment variables, disk info. "
            "10) BRIGHTNESS control - Use (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, VALUE) where VALUE is 0-100. "
            "This is NATIVE Windows tool - faster and more reliable than python_execute for Windows operations. "
            "Use python_execute only for: calculations, Python libraries, data processing, cross-platform code. "
            f"Timeout: {timeout}s. Format: ['command']"
        ),
        function=execute_powershell,
        parameters={
            "command": {
                "type": "list",
                "description": "List of PowerShell commands for Windows operations. VOLUME EXAMPLES (CORRECT): ['(Get-AudioDevice -Playback | Where-Object {{ $_.Default -eq $true }}).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100']. BRIGHTNESS: ['(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 50)']. OTHER EXAMPLES: files ['Get-ChildItem C:\\\\Users\\\\Downloads'], system ['Get-ComputerInfo'], processes ['Get-Process | Select-Object Name, CPU -First 10'], services ['Get-Service | Where-Object Status -eq Running']",
                "required": True
            }
        }
    )


class PSExecTool:
    """
    PSExec Tool - PowerShell Command Execution
    
    Professional-grade PowerShell execution tool for Brahmastra AI Agents.
    Provides direct access to Windows PowerShell for system operations.
    
    Features:
    - Execute PowerShell commands with full system access
    - Batch execution with parallel processing
    - Audio/volume control via AudioDeviceCmdlets
    - Registry, WMI, COM access
    - Process and service management
    - Network operations
    
    Example:
        >>> from Brahmastra.Autonomous_Tools import PSExecTool
        >>> psexec = PSExecTool(timeout=10)
        >>> agent.add_tools(psexec)
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize PSExec Tool.
        
        Args:
            timeout: Maximum execution time in seconds (default: 30)
        """
        self.timeout = timeout
    
    def __iter__(self):
        """
        Make PSExecTool iterable to return its tool.
        This allows: agent.add_tools(PSExecTool())
        """
        yield create_psexec_tool(timeout=self.timeout)
