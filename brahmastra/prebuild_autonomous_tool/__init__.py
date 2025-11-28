"""
Prebuilt Autonomous Tools for Brahmastra AI Agents
==================================================

Collection of autonomous tools that run continuously and interact with 
the system in real-time. These tools operate independently in background
threads, enabling seamless integration with AI agents.

Available Tools:
----------------
- SpeechRecognitionTool: Real-time speech-to-text with optional LLM enhancement
  - Supports multiple languages
  - Background listening mode
  - Optional Gemini/OpenAI accuracy enhancement

- PSExecTool: PowerShell command execution with full system access
  - Execute any PowerShell command
  - Capture stdout/stderr output
  - System administration capabilities

- PSGenTool: Intelligent PowerShell command generator using LLM
  - Natural language to PowerShell conversion
  - Context-aware command generation
  - Requires LLM instance

- PyRunTool: Python code execution with full system access
  - Execute Python code dynamically
  - Capture output and errors
  - Full Python runtime capabilities

Helper Functions:
-----------------
- get_recognized_text(): Get the current recognized text from global variable
- create_speech_recognition_tool(): Factory function to create speech tool
- create_psexec_tool(): Factory function to create PSExec tool
- create_pyrun_tool(): Factory function to create PyRun tool

Example:
--------
    >>> from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
    >>> from brahmastra.prebuild_autonomous_tool import PSExecTool, PSGenTool, PyRunTool
    >>> from brahmastra.llm_provider import GoogleLLM
    >>> 
    >>> # Create with LLM enhancement
    >>> llm = GoogleLLM(model="gemini-2.0-flash")
    >>> speech = SpeechRecognitionTool(llm=llm, auto_start=True)
    >>> psgen = PSGenTool(llm=llm)
    >>> 
    >>> # Create execution tools
    >>> psexec = PSExecTool()
    >>> pyrun = PyRunTool()

Author: devxJitin
Version: 1.0.0
License: MIT
"""

from .speech_recognition_tool import (
    SpeechRecognitionTool,
    create_speech_recognition_tool,
)
from .speech_recognition_tool import base as _speech_base

from .PSExec_tool import (
    PSExecTool,
    create_psexec_tool,
)

from .PSGen_tool import (
    PSGenTool,
    generate_powershell_command,
    clean_generated_command,
)

from .PyRun_tool import (
    PyRunTool,
    create_pyrun_tool,
)


def get_recognized_text() -> str:
    """
    Get the last recognized speech text from the global variable.
    
    Returns:
        str: The last recognized text, or empty string if none
        
    Example:
        >>> from brahmastra.prebuild_autonomous_tool import get_recognized_text
        >>> text = get_recognized_text()
        >>> print(text)
    """
    return _speech_base.RECOGNIZED_TEXT


__version__ = "1.0.0"
__author__ = "devxJitin"

__all__ = [
    # Speech Recognition
    "SpeechRecognitionTool",
    "create_speech_recognition_tool",
    "get_recognized_text",
    # PSExec Tool
    "PSExecTool",
    "create_psexec_tool",
    # PSGen Tool
    "PSGenTool",
    "generate_powershell_command",
    "clean_generated_command",
    # PyRun Tool
    "PyRunTool",
    "create_pyrun_tool",
]
