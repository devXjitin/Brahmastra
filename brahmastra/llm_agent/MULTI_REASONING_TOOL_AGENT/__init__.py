"""
Multi Tool Agent Module

Agent that executes multiple tools simultaneously for efficiency.

Key Features:
- Parallel tool execution for independent tasks
- Batch parameter execution for the same tool
- Sequential execution when dependencies exist
- Error handling per tool call

Use Cases:
1. Parallel Independent Calls:
   - Search Google, Wikipedia, and News simultaneously
   - Fetch data from multiple APIs at once
   - Process multiple independent queries

2. Batch Parameter Calls:
   - Search multiple keywords with same tool
   - Process multiple files with same function
   - Query multiple databases with same parameters

Example:
    >>> from brahmastra.llm_agent import Create_MultiToolAgent
    >>> from brahmastra.llm_provider import OpenAI_llm
    >>> from brahmastra.core import tool
    >>> 
    >>> llm = OpenAI_llm(model="gpt-4", api_key="your-key")
    >>> agent = Create_MultiToolAgent(llm=llm, max_workers=5, verbose=True)
    >>> 
    >>> @tool
    >>> def google_search(query: str, num_results: int = 5):
    >>>     '''Search Google for information'''
    >>>     return f"Results for {query}"
    >>> 
    >>> agent.add_tools(google_search)
    >>> 
    >>> # Agent will execute tools accordingly
    >>> result = agent.invoke("Search for 'Python AI', 'Machine Learning', and 'Neural Networks'")
"""

from .base import Create_MultiToolAgent

__all__ = ["Create_MultiToolAgent"]

__version__ = "1.0.0"
