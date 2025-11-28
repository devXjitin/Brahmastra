"""
ReAct Agent Module (Reasoning + Acting)

Provides an advanced AI agent framework that combines reasoning and tool execution.
This agent thinks through problems step-by-step while taking actions using tools.

Main Components:
- Create_ReAct_Agent: The main agent class combining reasoning and acting
- Iterative Think-Act-Observe loop
- Memory integration support (optional)
- Custom prompt support for agent introduction
- Verbose mode with colored terminal output

Based on the ReAct paradigm: "ReAct: Synergizing Reasoning and Acting in Language Models"

Example:
    >>> from brahmastra.llm_agent.REACT_AGENT import Create_ReAct_Agent
    >>> from brahmastra.llm_provider import OpenAI_llm
    >>> from brahmastra.core import tool
    >>> 
    >>> llm = OpenAI_llm(model="gpt-4", api_key="your-key")
    >>> agent = Create_ReAct_Agent(llm=llm, verbose=True)
    >>> 
    >>> @tool
    >>> def search(query: str):
    >>>     '''Search the internet'''
    >>>     return f"Results for {query}"
    >>> 
    >>> agent.add_tools(search)
    >>> result = agent.invoke("Search for Python tutorials and tell me about them")
"""

from .base import Create_ReAct_Agent

__all__ = ["Create_ReAct_Agent"]

__version__ = "1.0.0"
