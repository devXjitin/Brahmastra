"""
Wikipedia Tool Module

A pre-built tool for searching and retrieving information from Wikipedia.
Based on the wikipedia-api Python package.

Features:
- Search Wikipedia articles
- Get article summaries
- Get full article content
- Get article URL
- Handle disambiguation pages
- Multi-language support

Example:
    >>> from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool
    >>> 
    >>> wiki = WikipediaSearchTool()
    >>> agent.add_tools(wiki)  # Directly add to agent
"""

from .base import (
    WikipediaSearchTool,
    create_wikipedia_tool,
    create_wikipedia_content_tool
)

__all__ = [
    "WikipediaSearchTool",
    "create_wikipedia_tool",
    "create_wikipedia_content_tool"
]

__version__ = "1.0.0"
