import json

def Tool_Executor(tool_name, tool_parameters, available_tools):
    """
    Execute a tool function with the provided parameters.
    
    Args:
        tool_name: Name of the tool to execute
        tool_parameters: Parameters as dictionary with named keys {"param1": "value1", "param2": "value2"} or "None"
        available_tools: Dictionary of available tools with their functions
        
    Returns:
        Result from tool execution or error message
        
    Example:
        Tool_Executor("calculator", {"expression": "25 * 4"}, tools)
        # Calls: calculator(expression="25 * 4")
    """
    if tool_name not in available_tools:
        return f"Error: Tool '{tool_name}' not found"
    
    tool_function = available_tools[tool_name]["function"]
    
    # Handle no parameters case
    if not tool_parameters or tool_parameters == "None":
        try:
            return tool_function()
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"
    
    # Parse parameters if string
    if isinstance(tool_parameters, str):
        try:
            tool_parameters = json.loads(tool_parameters)
        except json.JSONDecodeError:
            return f"Error: Invalid parameter format. Expected JSON dictionary."
    
    # Execute tool with named parameters
    try:
        if isinstance(tool_parameters, dict) and len(tool_parameters) > 0:
            # Pass all parameters as keyword arguments
            return tool_function(**tool_parameters)
        else:
            # Empty dict or no parameters
            return tool_function()
            
    except TypeError as e:
        # Handle parameter mismatch errors
        return f"Error: Parameter mismatch for tool '{tool_name}'. {str(e)}"
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"