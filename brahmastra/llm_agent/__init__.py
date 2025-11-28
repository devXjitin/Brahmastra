"""
Brahmastra LLM Agent Module

A collection of advanced AI agents for different use cases.

Agents:
- Create_ToolCalling_Agent: Agent that can call tools to perform actions
- Create_Reasoning_Agent: Agent for complex step-by-step reasoning
- Create_ReAct_Agent: Agent combining reasoning and tool execution
- Create_MultiToolAgent: Agent that executes multiple tools simultaneously
- Create_AdvancedMultiToolAgent: Advanced agent with sophisticated reasoning and strategic planning

Each agent is optimized for specific types of tasks.
"""

from .TOOL_CALLING_AGENT import Create_ToolCalling_Agent
from .REASONING_AGENT import Create_Reasoning_Agent
from .REACT_AGENT import Create_ReAct_Agent
from .MULTI_REASONING_TOOL_AGENT import Create_MultiToolAgent

__all__ = [
    "Create_ToolCalling_Agent",
    "Create_Reasoning_Agent",
    "Create_ReAct_Agent",
    "Create_MultiToolAgent"
]

__version__ = "1.0.0"
