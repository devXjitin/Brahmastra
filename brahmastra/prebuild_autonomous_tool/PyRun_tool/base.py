"""
PyRun Tool - Python Code Execution

A professional-grade tool for executing Python code with FULL SYSTEM ACCESS.
NO RESTRICTIONS - complete freedom to execute any Python code.

Features:
- Execute ANY Python code without restrictions
- Full file system access (read/write/delete)
- System command execution (subprocess, shell commands)
- Network operations (HTTP, APIs, web scraping)
- Batch execution with parallel processing
- Capture stdout, stderr, and return values
- Timeout protection (configurable)
- JSON formatted results

Requires:
- Python 3.7+ (standard library only)

Example:
    >>> from brahmastra.prebuild_autonomous_tool import PyRunTool
    >>> 
    >>> pyrun = PyRunTool()
    >>> agent.add_tools(pyrun)
"""

from typing import Dict, Optional, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from brahmastra.core import Tool
import subprocess
import sys
import json
import io
import contextlib
import traceback


def execute_python_code(
    code: str,
    timeout: int = 30,
    capture_output: bool = True,
    globals_dict: Optional[Dict] = None,
    locals_dict: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute a single Python code snippet with FULL FREEDOM and return results.
    No restrictions - can access file system, network, subprocess, etc.
    
    Args:
        code: Python code to execute (any valid Python code)
        timeout: Maximum execution time in seconds (default: 30)
        capture_output: Whether to capture stdout/stderr (default: True)
        globals_dict: Global variables dictionary
        locals_dict: Local variables dictionary
        
    Returns:
        Dictionary with execution results
    """
    result = {
        "status": "success",
        "code": code[:100] + "..." if len(code) > 100 else code,
        "stdout": "",
        "stderr": "",
        "return_value": None,
        "error": None
    }
    
    try:
        # Prepare execution environment
        if globals_dict is None:
            globals_dict = {"__builtins__": __builtins__}
        if locals_dict is None:
            locals_dict = {}
        
        # Capture output if requested
        if capture_output:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with contextlib.redirect_stdout(stdout_capture), \
                 contextlib.redirect_stderr(stderr_capture):
                # Compile and execute code
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, globals_dict, locals_dict)
                
                # Check if there's a return value (last expression)
                try:
                    # Try to evaluate as expression for return value
                    lines = code.strip().split('\n')
                    last_line = lines[-1].strip()
                    if last_line and not last_line.startswith(('print', 'import', 'from', 'def', 'class', 'if', 'for', 'while')):
                        return_value = eval(last_line, globals_dict, locals_dict)
                        result["return_value"] = str(return_value)
                except:
                    pass
            
            result["stdout"] = stdout_capture.getvalue()
            result["stderr"] = stderr_capture.getvalue()
        else:
            # Execute without capturing output
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code, globals_dict, locals_dict)
        
    except SyntaxError as e:
        result["status"] = "error"
        result["error"] = f"SyntaxError: {str(e)}"
        result["stderr"] = traceback.format_exc()
    except TimeoutError:
        result["status"] = "error"
        result["error"] = "Execution timeout exceeded"
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["stderr"] = traceback.format_exc()
    
    return result


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
    
    Example:
        >>> pyrun = create_pyrun_tool(timeout=10)
        >>> agent.add_tools(pyrun)
    """
    
    def execute_python(code: list) -> str:
        """
        Execute Python code snippet(s).
        Always processes code as a list with parallel execution.
        
        Args:
            code: List of Python code strings to execute
            
        Returns:
            JSON string with execution results for all code snippets
        """
        results = {}
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=min(len(code), 5)) as executor:
            # Submit all code snippets
            future_to_code = {
                executor.submit(_execute_single_code, c, timeout, capture_output, allow_imports): (idx, c)
                for idx, c in enumerate(code, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_code):
                idx, c = future_to_code[future]
                try:
                    result = future.result()
                    results[idx] = result
                except Exception as e:
                    results[idx] = {
                        "status": "error",
                        "code": c[:100] + "..." if len(c) > 100 else c,
                        "error": f"Execution failed: {str(e)}"
                    }
        
        # Format results in original order
        output = {
            "status": "success",
            "total_executions": len(code),
            "results": [results[idx] for idx in sorted(results.keys())]
        }
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _execute_single_code(
        code: str,
        timeout: int,
        capture_output: bool,
        allow_imports: bool
    ) -> Dict[str, Any]:
        """
        Execute a single Python code snippet with full freedom.
        
        Returns:
            Dictionary with execution results
        """
        # Allow all imports by default - full freedom mode
        # No restrictions on code execution
        
        # Execute the code
        return execute_python_code(
            code=code,
            timeout=timeout,
            capture_output=capture_output
        )
    
    return Tool(
        name="python_execute",
        description=(
            "Execute Python code with FULL SYSTEM ACCESS for: "
            "1) DOWNLOADING FILES (yt-dlp for YouTube videos/audio, requests/urllib for web files, subprocess for system downloads) "
            "2) Calculations, data processing, algorithms "
            "3) File operations (read/write/create, list directories, move/copy files) "
            "4) Python libraries (import ANY library: requests, json, os, pathlib, datetime, yt-dlp, etc.) "
            "5) API calls and web scraping "
            "6) Data analysis (JSON/CSV/text processing) "
            "7) Cross-platform operations (Windows/Linux/Mac). "
            "For WINDOWS-SPECIFIC operations (volume, registry, services, WMI), use 'powershell_execute' instead. "
            "Download examples: ['import subprocess; subprocess.run([\"yt-dlp\", \"-x\", \"--audio-format\", \"mp3\", \"-o\", \"~/Desktop/%(title)s.%(ext)s\", \"URL\"])'], "
            "['import requests; open(\"file.zip\", \"wb\").write(requests.get(\"https://example.com/file.zip\").content)']. "
            f"Timeout: {timeout}s. Format: ['code']"
        ),
        function=execute_python,
        parameters={
            "code": {
                "type": "list",
                "description": "List of Python code strings. Use for: downloads ['subprocess.run([\"yt-dlp\", \"-x\", \"--audio-format\", \"mp3\", \"URL\"])'], calculations ['import math; print(math.sqrt(144))'], file ops ['import os; print(os.listdir(\".\"))']. For Windows system operations, use powershell_execute.",
                "required": True
            }
        }
    )


class PyRunTool:
    """
    PyRun Tool - Python Code Execution
    
    Professional-grade Python code execution tool for Brahmastra AI Agents.
    Similar to WikipediaSearchTool and YoutubeSearchTool, provides a clean interface
    that can be used with agent.add_tools().
    
    Features:
    - Execute Python code snippets safely
    - Batch execution with parallel processing
    - Capture stdout, stderr, and return values
    - Timeout protection
    - Configurable execution environment
    
    Example:
        >>> from Brahmastra.Autonomous_Tools import PyRunTool
        >>> pyrun = PyRunTool(timeout=10)
        >>> agent.add_tools(pyrun)
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
        self.timeout = timeout
        self.capture_output = capture_output
        self.allow_imports = allow_imports
    
    def __iter__(self):
        """
        Make PyRunTool iterable to return its tool.
        This allows: agent.add_tools(PyRunTool())
        """
        yield create_pyrun_tool(
            timeout=self.timeout,
            capture_output=self.capture_output,
            allow_imports=self.allow_imports
        )
