"""
Tool System - Professional-Grade Tool Management
=================================================

A modern, independent tool system with decorators and automatic parameter 
extraction from function signatures. Designed for seamless integration with 
AI agents and multi-agent systems in the brahmastra.

Features:
    ✨ Clean decorator syntax (@tool)
    🔍 Automatic parameter extraction from type hints
    📝 Smart docstring parsing for descriptions
    🎯 Type-safe parameter validation
    🔄 Flexible tool definition (decorator or direct instantiation)
    🚀 Zero-boilerplate tool creation
    🔧 Framework-agnostic design
    
Architecture:
    - Tool: Core class representing a callable tool with metadata
    - @tool: Decorator for automatic tool creation from functions
    - Parameter introspection via Python's inspect module
    - Type hint support for automatic schema generation

Example:
    >>> from brahmastra.core import tool
    >>> 
    >>> @tool
    >>> def calculator(expression: str) -> str:
    ...     '''Performs mathematical calculations.'''
    ...     return str(eval(expression))
    >>> 
    >>> # Add to agent
    >>> agent.add_tools(calculator)
    >>> 
    >>> # Direct call
    >>> result = calculator("2 + 2")

Author: devxJitin
Version: 1.0.0
License: MIT
"""

import inspect
import re
from typing import Callable, Optional, Dict, Any, List, Union, get_type_hints, get_origin, get_args
from functools import wraps


# ============================================================================
# Type Utilities
# ============================================================================

def _convert_type_to_string(param_type: Any) -> str:
    """
    Convert Python type hints to string representation for tool schema.
    
    Supports basic types, Optional, Union, List, Dict, and custom types.
    
    Args:
        param_type: Python type hint to convert
        
    Returns:
        String representation of the type (e.g., "str", "int", "list", "dict")
        
    Examples:
        >>> _convert_type_to_string(str)
        'str'
        >>> _convert_type_to_string(Optional[int])
        'int'
        >>> _convert_type_to_string(List[str])
        'list'
    """
    # Handle None/Any
    if param_type is None or param_type == Any:
        return "any"
    
    # Handle string representations
    if isinstance(param_type, str):
        return param_type.lower()
    
    # Get origin for generic types (List, Dict, Optional, Union)
    origin = get_origin(param_type)
    
    # Handle Optional (which is Union[X, None])
    if origin is Union:
        args = get_args(param_type)
        # Filter out NoneType
        non_none_args = [arg for arg in args if arg is not type(None)]
        if non_none_args:
            return _convert_type_to_string(non_none_args[0])
        return "any"
    
    # Handle List, Dict, etc.
    if origin is list or origin is List:
        return "list"
    if origin is dict or origin is Dict:
        return "dict"
    if origin is tuple or origin is tuple:
        return "tuple"
    if origin is set or origin is set:
        return "set"
    
    # Handle basic types
    type_map = {
        str: "str",
        int: "int",
        float: "float",
        bool: "bool",
        list: "list",
        dict: "dict",
        tuple: "tuple",
        set: "set",
        bytes: "bytes",
    }
    
    return type_map.get(param_type, "str")  # Default to string


def _extract_param_descriptions_from_docstring(func: Callable) -> Dict[str, str]:
    """
    Extract parameter descriptions from function docstring.
    
    Supports Google-style, NumPy-style, and reStructuredText docstrings.
    
    Args:
        func: Function to extract parameter descriptions from
        
    Returns:
        Dictionary mapping parameter names to their descriptions
        
    Examples:
        Google-style:
            Args:
                query (str): The search query to execute
                limit (int): Maximum number of results
                
        NumPy-style:
            Parameters
            ----------
            query : str
                The search query to execute
            limit : int
                Maximum number of results
    """
    docstring = func.__doc__ or ""
    param_descriptions = {}
    
    # Try Google/Sphinx style: "Args:" or "Arguments:" or "Parameters:"
    args_pattern = r'(?:Args?|Arguments?|Parameters?):\s*\n((?:\s+\w+.*\n?)+)'
    args_match = re.search(args_pattern, docstring, re.IGNORECASE)
    
    if args_match:
        args_section = args_match.group(1)
        
        # Match: param_name (type): description or param_name: description
        param_pattern = r'\s+(\w+)\s*(?:\([^)]+\))?\s*:\s*(.+?)(?=\n\s+\w+\s*(?:\([^)]+\))?\s*:|$)'
        
        for match in re.finditer(param_pattern, args_section, re.DOTALL):
            param_name = match.group(1)
            description = re.sub(r'\s+', ' ', match.group(2)).strip()
            param_descriptions[param_name] = description
    
    # Try NumPy style
    if not param_descriptions:
        numpy_pattern = r'Parameters\s*\n\s*-+\s*\n((?:.*\n?)+?)(?:\n\s*(?:Returns|Yields|Raises|See Also|Notes|Examples)|\Z)'
        numpy_match = re.search(numpy_pattern, docstring, re.IGNORECASE)
        
        if numpy_match:
            params_section = numpy_match.group(1)
            # Match: param_name : type\n    description
            param_pattern = r'(\w+)\s*:\s*[^\n]+\n\s+(.+?)(?=\n\w+\s*:|$)'
            
            for match in re.finditer(param_pattern, params_section, re.DOTALL):
                param_name = match.group(1)
                description = re.sub(r'\s+', ' ', match.group(2)).strip()
                param_descriptions[param_name] = description
    
    return param_descriptions


# ============================================================================
# Tool Decorator
# ============================================================================

def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    return_direct: bool = False
) -> Union['Tool', Callable[..., 'Tool']]:
    """
    Decorator to convert a function into a Tool with automatic metadata extraction.
    
    This decorator intelligently extracts:
        - Tool name from function name
        - Description from docstring
        - Parameters with types from function signature
        - Parameter descriptions from docstring Args section
        - Required/optional status from default values
    
    Args:
        func: Function to convert to a tool (when used as @tool)
        name: Optional custom tool name (defaults to function name)
        description: Optional custom description (defaults to docstring)
        return_direct: Whether the tool returns final answer directly to user
    
    Returns:
        Tool instance with complete metadata
        
    Examples:
        Basic usage:
            >>> @tool
            >>> def calculator(expression: str) -> str:
            ...     '''Performs mathematical calculations on expressions.'''
            ...     return str(eval(expression))
        
        With custom metadata:
            >>> @tool(name="web_search", description="Search the internet")
            >>> def search(query: str, limit: int = 10) -> str:
            ...     '''Search for information.
            ...     
            ...     Args:
            ...         query: The search query to execute
            ...         limit: Maximum number of results to return
            ...     '''
            ...     return f"Found {limit} results for {query}"
        
        With complex types:
            >>> @tool
            >>> def process_data(
            ...     items: List[str],
            ...     config: Optional[Dict[str, Any]] = None
            ... ) -> Dict[str, Any]:
            ...     '''Process a list of items with optional configuration.'''
            ...     return {"processed": len(items)}
    
    Note:
        Type hints are required for proper parameter extraction.
        Without type hints, parameters default to 'str' type.
    """
    def decorator(f: Callable) -> 'Tool':
        # Extract tool metadata
        tool_name = name or f.__name__
        tool_description = description or (f.__doc__ or "No description provided").strip()
        
        # Get first line of docstring if multi-line
        if '\n' in tool_description:
            tool_description = tool_description.split('\n')[0].strip()
        
        # Extract parameter information
        sig = inspect.signature(f)
        type_hints = get_type_hints(f)
        param_descriptions = _extract_param_descriptions_from_docstring(f)
        
        parameters = {}
        for param_name, param in sig.parameters.items():
            # Skip *args, **kwargs
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            
            # Get type from hints
            param_type = type_hints.get(param_name, Any)
            type_str = _convert_type_to_string(param_type)
            
            # Check if required (no default value)
            required = param.default == inspect.Parameter.empty
            
            # Get description from docstring or generate default
            param_desc = param_descriptions.get(
                param_name,
                f"The {param_name} parameter"
            )
            
            parameters[param_name] = {
                "type": type_str,
                "description": param_desc,
                "required": required
            }
        
        return Tool(
            name=tool_name,
            description=tool_description,
            function=f,
            parameters=parameters,
            return_direct=return_direct
        )
    
    # Handle both @tool and @tool() or @tool(name="...", description="...")
    if func is not None:
        # Used as @tool (without parentheses)
        return decorator(func)
    else:
        # Used as @tool() or @tool(name="...")
        return decorator




# ============================================================================
# Tool Class
# ============================================================================

class Tool:
    """
    Represents a callable tool with complete metadata and schema.
    
    A Tool wraps a Python function with structured metadata that enables:
        - Automatic documentation generation
        - Parameter validation
        - Schema-based invocation by AI agents
        - Direct or indirect execution
    
    Attributes:
        name (str): Unique identifier for the tool
        description (str): Human-readable description of functionality
        function (Callable): The actual Python function to execute
        parameters (Dict): Schema defining input parameters with types and descriptions
        return_direct (bool): Whether tool output goes directly to user
    
    Examples:
        Direct instantiation:
            >>> def multiply(a: int, b: int) -> int:
            ...     return a * b
            >>> 
            >>> tool = Tool(
            ...     name="multiply",
            ...     description="Multiply two numbers",
            ...     function=multiply,
            ...     parameters={
            ...         "a": {"type": "int", "description": "First number", "required": True},
            ...         "b": {"type": "int", "description": "Second number", "required": True}
            ...     }
            ... )
        
        Via decorator (recommended):
            >>> @tool
            >>> def multiply(a: int, b: int) -> int:
            ...     '''Multiply two numbers together.'''
            ...     return a * b
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None,
        return_direct: bool = False
    ):
        """
        Initialize a Tool instance.
        
        Args:
            name: Unique tool name (used as identifier by agents)
            description: Clear description of what the tool does
            function: The callable Python function to execute
            parameters: Parameter schema dict mapping param names to their metadata.
                Each parameter should have: type, description, required
            return_direct: If True, tool output is returned directly to user.
                If False, output goes back to the agent for further processing
        
        Raises:
            ValueError: If name is empty or function is not callable
        """
        if not name or not isinstance(name, str):
            raise ValueError("Tool name must be a non-empty string")
        
        if not callable(function):
            raise ValueError("Tool function must be callable")
        
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters or {}
        self.return_direct = return_direct
    
    def run(self, *args, **kwargs) -> Any:
        """
        Execute the tool's function with provided arguments.
        
        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        
        Returns:
            Result of the function execution
        
        Raises:
            Any exception raised by the underlying function
        
        Example:
            >>> tool = Tool("add", "Add numbers", lambda a, b: a + b)
            >>> result = tool.run(5, 3)
            >>> print(result)  # 8
        """
        return self.function(*args, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tool to dictionary representation.
        
        Useful for serialization, logging, or passing to external systems.
        Note: The function itself is included but may not be serializable.
        
        Returns:
            Dictionary containing tool metadata
        
        Example:
            >>> tool_dict = tool.to_dict()
            >>> print(tool_dict.keys())
            dict_keys(['name', 'description', 'function', 'parameters', 'return_direct'])
        """
        return {
            "name": self.name,
            "description": self.description,
            "function": self.function,
            "parameters": self.parameters,
            "return_direct": self.return_direct
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool's schema without the function reference.
        
        Useful for generating API documentation or passing schema to LLMs.
        
        Returns:
            Dictionary with tool metadata excluding the function object
        
        Example:
            >>> schema = tool.get_schema()
            >>> # Safe to JSON serialize or send to LLM
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "return_direct": self.return_direct
        }
    
    def validate_parameters(self, **kwargs) -> List[str]:
        """
        Validate provided parameters against the tool's schema.
        
        Args:
            **kwargs: Parameters to validate
        
        Returns:
            List of error messages (empty if valid)
        
        Example:
            >>> errors = tool.validate_parameters(query="test", limit=10)
            >>> if errors:
            ...     print("Validation errors:", errors)
        """
        errors = []
        
        # Check required parameters
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False):
                if param_name not in kwargs:
                    errors.append(f"Missing required parameter: {param_name}")
        
        # Check for unexpected parameters
        valid_params = set(self.parameters.keys())
        provided_params = set(kwargs.keys())
        unexpected = provided_params - valid_params
        
        if unexpected:
            errors.append(f"Unexpected parameters: {', '.join(unexpected)}")
        
        return errors
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Allow tool to be called directly like a function.
        
        Example:
            >>> result = tool(arg1="value", arg2=123)
        """
        return self.run(*args, **kwargs)
    
    def __repr__(self) -> str:
        """String representation of the tool."""
        params = list(self.parameters.keys())
        return f"Tool(name='{self.name}', parameters={params})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        param_count = len(self.parameters)
        return f"Tool '{self.name}': {self.description} ({param_count} parameters)"


# ============================================================================
# Exports
# ============================================================================

__all__ = ["Tool", "tool"]
