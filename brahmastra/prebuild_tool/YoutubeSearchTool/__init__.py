"""
YouTube Search Tool Module - Official YouTube Data API v3

A pre-built tool for searching and retrieving YouTube videos, channels, and analytics
using Google's official YouTube Data API v3.

Features:
- Advanced video search with 10+ filters
- Channel information and statistics
- Video details with metadata
- Date range filtering
- Duration filtering (short/medium/long)
- Sort by relevance, date, rating, or view count
- HD quality filtering
- Safe search options

Example:
    >>> from brahmastra.prebuild_tool.YoutubeSearchTool import YoutubeSearchTool
    >>> 
    >>> youtube = YoutubeSearchTool()  # Uses YOUTUBE_API_KEY env var
    >>> agent.add_tools(youtube)  # Directly add to agent
"""

from .base import (
    YouTubeSearchTool,
    create_youtube_advanced_search_tool,
    create_youtube_channel_tool,
    create_youtube_video_tool,
    create_youtube_channel_info_tool,
    create_youtube_video_details_tool
)

__all__ = [
    "YouTubeSearchTool",
    "create_youtube_advanced_search_tool",
    "create_youtube_channel_tool",
    "create_youtube_video_tool",
    "create_youtube_channel_info_tool",
    "create_youtube_video_details_tool"
]
