"""
PSGen Tool - PowerShell Command Generator

An intelligent tool that uses LLM to generate PowerShell commands based on natural language requests.
The generated commands are optimized for execution and output display.

Features:
- Generate PowerShell commands from natural language
- LLM-powered command generation
- Ensures commands produce visible output
- Optimized for Windows PowerShell 5.1+ and PowerShell 7+
- Returns ready-to-execute PowerShell commands

Example:
    >>> from brahmastra.prebuild_autonomous_tool import PSGenTool
    >>> from brahmastra.llm_provider import GoogleLLM
    >>> 
    >>> llm = GoogleLLM(api_key="your-key")
    >>> psgen = PSGenTool(llm=llm)
    >>> agent.add_tools(psgen)
"""

from typing import Dict, Any
import re
from brahmastra.core import Tool


PSGEN_PROMPT = """You are a PowerShell command generator. Generate a PowerShell command based on the user's request.

RULES:
1. Return ONLY the raw PowerShell command - NO explanations, NO markdown, NO code blocks, NO backticks
2. The command must be ready to execute directly in PowerShell
3. Ensure commands produce visible output when appropriate
4. Use proper PowerShell syntax

COMMON PATTERNS:

Volume Control (requires AudioDeviceCmdlets module):
- Get volume: (Get-AudioDevice -Playback | Where-Object {{ $_.Default }}).Device.AudioEndpointVolume.MasterVolumeLevelScalar * 100
- Set volume to 50%: $dev = (Get-AudioDevice -Playback | Where-Object {{ $_.Default }}).Device.AudioEndpointVolume; $dev.MasterVolumeLevelScalar = 0.5; Write-Host "Volume set to 50%"
- Decrease by 20%: $dev = (Get-AudioDevice -Playback | Where-Object {{ $_.Default }}).Device.AudioEndpointVolume; $current = $dev.MasterVolumeLevelScalar; $dev.MasterVolumeLevelScalar = [Math]::Max(0, $current - 0.2); Write-Host "Volume decreased"
- Increase by 20%: $dev = (Get-AudioDevice -Playback | Where-Object {{ $_.Default }}).Device.AudioEndpointVolume; $current = $dev.MasterVolumeLevelScalar; $dev.MasterVolumeLevelScalar = [Math]::Min(1, $current + 0.2); Write-Host "Volume increased"

System Info:
- CPU: Get-Counter '\\Processor(_Total)\\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue
- Memory: Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory
- Disk: Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free
- Processes: Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet

File Operations:
- List files: Get-ChildItem -Path "C:\\Users" -Recurse -File
- Search: Get-ChildItem -Path "C:\\" -Filter "*.txt" -Recurse -ErrorAction SilentlyContinue
- File info: Get-Item "C:\\path\\to\\file" | Select-Object Name, Length, LastWriteTime

Network:
- IP info: Get-NetIPAddress | Where-Object {{ $_.AddressFamily -eq 'IPv4' }}
- Test connection: Test-Connection -ComputerName google.com -Count 2
- Download: Invoke-WebRequest -Uri "URL" -OutFile "filename"

Services:
- List running: Get-Service | Where-Object {{ $_.Status -eq 'Running' }}
- Start/Stop: Start-Service -Name "ServiceName" / Stop-Service -Name "ServiceName"

Remember: Output ONLY the command, nothing else.

User Request: {user_request}"""


def generate_powershell_command(llm, request: str) -> Dict[str, Any]:
    """
    Generate a PowerShell command using LLM based on natural language request.
    
    Args:
        llm: LLM instance with generate_response method
        request: Natural language description of what the command should do
        
    Returns:
        Dictionary with generated command and status
    """
    result = {
        "status": "success",
        "request": request,
        "command": "",
        "error": None
    }
    
    try:
        # Generate prompt
        prompt = PSGEN_PROMPT.format(user_request=request)
        
        # Get LLM response
        command = llm.generate_response(prompt)
        
        # Clean up the response thoroughly
        command = clean_generated_command(command)
        
        result["command"] = command
        
        if not command:
            result["status"] = "error"
            result["error"] = "LLM generated empty command"
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Error generating command: {str(e)}"
    
    return result


def clean_generated_command(command: str) -> str:
    """
    Clean up LLM-generated command by removing markdown, explanations, etc.
    
    Args:
        command: Raw LLM output
        
    Returns:
        Clean PowerShell command ready for execution
    """
    if not command:
        return ""
    
    command = command.strip()
    
    # Remove markdown code blocks (various formats)
    code_block_patterns = [
        r'```powershell\s*([\s\S]*?)\s*```',
        r'```ps1\s*([\s\S]*?)\s*```',
        r'```ps\s*([\s\S]*?)\s*```',
        r'```shell\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
    ]
    
    for pattern in code_block_patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            command = match.group(1).strip()
            break
    
    # Remove inline backticks
    if command.startswith('`') and command.endswith('`'):
        command = command[1:-1].strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        'command:', 'powershell:', 'ps:', 'cmd:', 
        'here is the command:', 'the command is:',
        'here\'s the command:', 'execute:',
    ]
    command_lower = command.lower()
    for prefix in prefixes_to_remove:
        if command_lower.startswith(prefix):
            command = command[len(prefix):].strip()
            command_lower = command.lower()
    
    # Remove trailing explanations (lines starting with common explanation patterns)
    lines = command.split('\n')
    clean_lines = []
    for line in lines:
        line_stripped = line.strip().lower()
        # Stop if we hit explanation text
        if any(line_stripped.startswith(p) for p in [
            'this command', 'this will', 'note:', 'explanation:',
            'the above', '#', '//', 'this script', 'output:'
        ]):
            break
        if line.strip():  # Keep non-empty lines
            clean_lines.append(line)
    
    command = '\n'.join(clean_lines).strip()
    
    # Remove any remaining backticks at start/end
    command = command.strip('`').strip()
    
    return command


class PSGenTool:
    """
    PowerShell Command Generator Tool
    
    Generates PowerShell commands from natural language using an LLM.
    
    Example:
        >>> from Brahmastra.Autonomous_Tools import PSGenTool
        >>> psgen = PSGenTool(llm=llm)
        >>> agent.add_tools(psgen)
    """
    
    def __init__(self, llm):
        """
        Initialize PSGen Tool with an LLM.
        
        Args:
            llm: LLM instance with generate_response method
        """
        self.llm = llm
        self.tool = Tool(
            name="powershell_generate",
            description="Generate PowerShell commands from natural language. Use this to create PowerShell commands for system operations, audio control, file management, and more. Returns a ready-to-execute PowerShell command.",
            parameters={
                "request": {
                    "type": "str",
                    "description": "Natural language description of the PowerShell command to generate",
                    "required": True
                }
            },
            function=self._generate_command
        )
    
    def _generate_command(self, request: str) -> str:
        """Internal method to generate PowerShell command."""
        result = generate_powershell_command(self.llm, request)
        
        if result["status"] == "error":
            return f"Error: {result['error']}"
        
        return f"Generated PowerShell Command:\n{result['command']}\n\nYou can now execute this command using the powershell_execute tool."
    
    def __iter__(self):
        """Make the tool iterable for add_tools() method."""
        yield self.tool
