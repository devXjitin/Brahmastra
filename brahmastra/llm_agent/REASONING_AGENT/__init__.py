"""
Reasoning Agent Module

Provides an advanced AI agent framework with step-by-step reasoning capabilities.
Designed for complex problem solving requiring transparent thinking processes.

Main Components:
- Create_Reasoning_Agent: The main agent class for reasoning tasks
- Optimized for reasoning models (OpenAI o1, o3, DeepSeek-R1)
- Shows transparent reasoning steps
- Verbose mode with colored terminal output

Note: This agent does NOT support tool calling. Use TOOL_CALLING_AGENT for tool usage.

Example:
    >>> from brahmastra.llm_agent.REASONING_AGENT import Create_Reasoning_Agent
    >>> from brahmastra.llm_provider import OpenAI_llm
    >>> 
    >>> llm = OpenAI_llm(model="o1-preview", api_key="your-key")
    >>> agent = Create_Reasoning_Agent(llm=llm, verbose=True, show_reasoning=True)
    >>> 
    >>> result = agent.invoke("What is 17 × 23 + 45 × 12?")
    >>> print(result["final_answer"])
"""

from .base import Create_Reasoning_Agent

__all__ = ["Create_Reasoning_Agent"]

__version__ = "1.0.0"
