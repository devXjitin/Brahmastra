"""
Pre-built Tools for Brahmastra

Collection of ready-to-use tools for AI agents, similar to LangChain's tools.

Available Tools:
- WikipediaSearchTool: Search and retrieve Wikipedia articles
- YoutubeSearchTool: Search YouTube videos using official API
- YoutubeTranscriptTool: Retrieve transcripts and captions from YouTube videos

Example:
    >>> from brahmastra.prebuild_tool import WikipediaSearchTool, YoutubeSearchTool, YoutubeTranscriptTool
    >>> from brahmastra.llm_agent.REACT_AGENT import Create_ReAct_Agent
    >>> 
    >>> # Create Wikipedia tool
    >>> wiki = WikipediaSearchTool(language="en", max_search_results=5)
    >>> 
    >>> # Create YouTube Search tool
    >>> youtube = YoutubeSearchTool()  # Uses YOUTUBE_API_KEY env var
    >>> 
    >>> # Create YouTube Transcript tool
    >>> transcript = YoutubeTranscriptTool(language="en")
    >>> 
    >>> # Create agent and add tools
    >>> agent = Create_ReAct_Agent(llm=your_llm, verbose=True)
    >>> agent.add_tools(wiki, youtube, transcript)  # Directly add all tools
    >>> 
    >>> # Use the agent
    >>> result = agent.invoke("Tell me about Python programming language")
"""

from .wikipedia_tool import (
    WikipediaSearchTool,
    create_wikipedia_tool,
    create_wikipedia_content_tool
)


from .YoutubeSearchTool import (
    YouTubeSearchTool as YoutubeSearchTool,
    create_youtube_advanced_search_tool,
    create_youtube_channel_tool,
    create_youtube_video_tool,
    create_youtube_channel_info_tool,
    create_youtube_video_details_tool
)

from .YoutubeTranscriptTool import (
    YoutubeTranscriptTool,
    create_youtube_transcript_tool,
    create_youtube_transcript_languages_tool
)

__all__ = [
    "WikipediaSearchTool",
    "create_wikipedia_tool",
    "create_wikipedia_content_tool",
    "YoutubeSearchTool",
    "create_youtube_advanced_search_tool",
    "create_youtube_channel_tool",
    "create_youtube_video_tool",
    "create_youtube_channel_info_tool",
    "create_youtube_video_details_tool",
    "YoutubeTranscriptTool",
    "create_youtube_transcript_tool",
    "create_youtube_transcript_languages_tool"
]

__version__ = "1.0.0"
