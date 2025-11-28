"""
YouTube Transcript Tool Module

A pre-built tool for retrieving transcripts and captions from YouTube videos.
Based on the youtube-transcript-api Python package.

Features:
- Retrieve video transcripts/captions
- Support for multiple languages
- Auto-generated and manual captions
- Formatted transcript output
- Timestamp support
- Translation capabilities

Example:
    >>> from brahmastra.prebuild_tool.YoutubeTranscriptTool import YoutubeTranscriptTool
    >>> 
    >>> transcript = YoutubeTranscriptTool()
    >>> agent.add_tools(transcript)  # Directly add to agent
"""

from .base import (
    YoutubeTranscriptTool,
    create_youtube_transcript_tool,
    create_youtube_transcript_languages_tool
)

__all__ = [
    "YoutubeTranscriptTool",
    "create_youtube_transcript_tool",
    "create_youtube_transcript_languages_tool"
]

__version__ = "1.0.0"
