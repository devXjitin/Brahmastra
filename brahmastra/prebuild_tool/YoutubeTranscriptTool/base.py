"""
YouTube Transcript Tool - YouTube Transcript API

A professional-grade tool for retrieving video transcripts and captions from YouTube.
Based on the youtube-transcript-api Python package.

Features:
- 📝 Retrieve video transcripts/captions
- 🌐 Multi-language support
- 🔄 Auto-generated and manual captions
- ⏱️ Timestamp support
- 🔤 Translation capabilities
- 📊 Available languages listing
- 🎯 Formatted output options

Requires:
- youtube-transcript-api package
- Install with: pip install youtube-transcript-api

Example:
    >>> from brahmastra.prebuild_tool import YoutubeTranscriptTool
    >>> 
    >>> transcript = YoutubeTranscriptTool()
    >>> agent.add_tools(transcript)
"""

from typing import Dict, Optional, List, Iterator
from brahmastra.core import Tool
import re


def extract_video_id(url_or_id: str) -> str:
    """
    Extract YouTube video ID from URL or return ID if already extracted.
    
    Args:
        url_or_id: YouTube URL or video ID
        
    Returns:
        Video ID string
    """
    # If it's already an ID (11 characters, alphanumeric + _ -)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's an ID
    return url_or_id


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS or MM:SS format.
    
    Args:
        seconds: Timestamp in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def create_youtube_transcript_tool(
    language: str = "en",
    include_timestamps: bool = True,
    max_chars: int = 50000
) -> Tool:
    """
    Create a tool to retrieve YouTube video transcripts.
    
    Args:
        language: Preferred language code (default: "en")
        include_timestamps: Include timestamps in output (default: True)
        max_chars: Maximum characters to return (default: 50000)
    
    Returns:
        Tool object for retrieving YouTube transcripts
    
    Example:
        >>> transcript_tool = create_youtube_transcript_tool(language="en")
        >>> agent.add_tools(transcript_tool)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable
        )
    except ImportError:
        raise ImportError(
            "youtube-transcript-api is required. "
            "Install with: pip install youtube-transcript-api"
        )
    
    def get_youtube_transcript(
        video_url_or_id: str,
        languages: Optional[str] = None,
        translate_to: Optional[str] = None
    ) -> str:
        """
        Retrieve transcript/captions from a YouTube video.
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            languages: Comma-separated language codes (e.g., "en,es,fr"). Defaults to tool's language setting.
            translate_to: Translate transcript to this language code (optional)
            
        Returns:
            Formatted transcript with timestamps
        """
        try:
            # Extract video ID
            video_id = extract_video_id(video_url_or_id)
            
            # Prepare language preferences
            if languages:
                lang_list = [lang.strip() for lang in languages.split(',')]
            else:
                lang_list = [language]
            
            # Get transcript
            try:
                # Create API instance
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)
                
                # Try to find transcript in preferred languages
                transcript = None
                found_lang = None
                
                # Try manual transcripts first
                for lang in lang_list:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        found_lang = lang
                        break
                    except NoTranscriptFound:
                        continue
                
                # If no manual transcript, try generated
                if not transcript:
                    try:
                        transcript = transcript_list.find_generated_transcript(lang_list)
                        found_lang = transcript.language_code
                    except NoTranscriptFound:
                        pass
                
                # If still no transcript, get any available
                if not transcript:
                    available = transcript_list._manually_created_transcripts or transcript_list._generated_transcripts
                    if available:
                        transcript = list(available.values())[0]
                        found_lang = transcript.language_code
                    else:
                        return f"❌ No transcripts available for video '{video_id}'"
                
                # Translate if requested
                if translate_to and translate_to != found_lang:
                    try:
                        transcript = transcript.translate(translate_to)
                        found_lang = translate_to
                    except Exception as e:
                        return f"⚠️ Translation to '{translate_to}' failed: {str(e)}\n\nUsing original transcript in '{found_lang}'..."
                
                # Fetch transcript data
                transcript_data = transcript.fetch()
                
                # Format output
                output = f"🎥 **YouTube Video Transcript**\n\n"
                output += f"📹 Video ID: {video_id}\n"
                output += f"🔗 URL: https://www.youtube.com/watch?v={video_id}\n"
                output += f"🌐 Language: {found_lang}\n"
                output += f"📝 Segments: {len(transcript_data)}\n\n"
                output += "─" * 50 + "\n\n"
                
                # Add transcript content
                full_text = ""
                for entry in transcript_data:
                    text = entry.text.strip()
                    
                    if include_timestamps:
                        timestamp = format_timestamp(entry.start)
                        full_text += f"[{timestamp}] {text}\n"
                    else:
                        full_text += f"{text} "
                
                # Truncate if too long
                if len(full_text) > max_chars:
                    full_text = full_text[:max_chars] + "\n\n... (transcript truncated)"
                    output += f"⚠️ Note: Transcript truncated to {max_chars} characters\n\n"
                
                output += full_text
                
                return output
                
            except TranscriptsDisabled:
                return f"❌ Transcripts are disabled for video '{video_id}'"
                
            except NoTranscriptFound:
                return f"❌ No transcript found for video '{video_id}' in languages: {', '.join(lang_list)}\n\n💡 Tip: Use youtube_transcript_languages tool to see all available languages"
                    
            except VideoUnavailable:
                return f"❌ Video '{video_id}' is unavailable or does not exist"
                
        except Exception as e:
            return f"❌ Error retrieving transcript: {str(e)}\n\n💡 Tip: Check the video ID/URL and try again"
    
    return Tool(
        name="youtube_transcript",
        description=(
            f"Retrieve transcript/captions from YouTube videos. "
            f"Supports multiple languages, auto-generated and manual captions. "
            f"Can translate transcripts to different languages. "
            f"Default language: {language}. Returns formatted transcript with timestamps."
        ),
        function=get_youtube_transcript,
        parameters={
            "video_url_or_id": {
                "type": "str",
                "description": "YouTube video URL (e.g., https://youtube.com/watch?v=VIDEO_ID) or video ID (11 characters)",
                "required": True
            },
            "languages": {
                "type": "str",
                "description": f"Comma-separated language codes (e.g., 'en,es,fr'). Defaults to '{language}' if not specified",
                "required": False
            },
            "translate_to": {
                "type": "str",
                "description": "Translate transcript to this language code (e.g., 'en', 'es', 'fr'). Optional.",
                "required": False
            }
        }
    )


def create_youtube_transcript_languages_tool() -> Tool:
    """
    Create a tool to list available transcript languages for a video.
    
    Returns:
        Tool object for listing available transcript languages
    
    Example:
        >>> languages_tool = create_youtube_transcript_languages_tool()
        >>> agent.add_tools(languages_tool)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            VideoUnavailable
        )
    except ImportError:
        raise ImportError(
            "youtube-transcript-api is required. "
            "Install with: pip install youtube-transcript-api"
        )
    
    def list_transcript_languages(video_url_or_id: str) -> str:
        """
        List all available transcript languages for a YouTube video.
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            
        Returns:
            List of available languages with details
        """
        try:
            # Extract video ID
            video_id = extract_video_id(video_url_or_id)
            
            # Get transcript list
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            
            output = f"🎥 **Available Transcripts for Video**\n\n"
            output += f"📹 Video ID: {video_id}\n"
            output += f"🔗 URL: https://www.youtube.com/watch?v={video_id}\n\n"
            
            # Manual transcripts
            manual_transcripts = transcript_list._manually_created_transcripts
            if manual_transcripts:
                output += "📝 **Manual Transcripts** (Human-created):\n"
                for lang_code, transcript in manual_transcripts.items():
                    lang_name = transcript.language
                    translatable = "✓" if transcript.is_translatable else "✗"
                    output += f"   • {lang_code} - {lang_name} (Translatable: {translatable})\n"
                output += "\n"
            
            # Generated transcripts
            generated_transcripts = transcript_list._generated_transcripts
            if generated_transcripts:
                output += "🤖 **Auto-Generated Transcripts**:\n"
                for lang_code, transcript in generated_transcripts.items():
                    lang_name = transcript.language
                    translatable = "✓" if transcript.is_translatable else "✗"
                    output += f"   • {lang_code} - {lang_name} (Translatable: {translatable})\n"
                output += "\n"
            
            if not manual_transcripts and not generated_transcripts:
                output += "❌ No transcripts available for this video\n"
            else:
                output += "💡 **Tip**: Use the youtube_transcript tool with the 'languages' parameter to retrieve a transcript in your preferred language.\n"
                output += "💡 **Translation**: Translatable transcripts can be translated to any language using the 'translate_to' parameter.\n"
            
            return output
            
        except TranscriptsDisabled:
            video_id = extract_video_id(video_url_or_id)
            return f"❌ Transcripts are disabled for video '{video_id}'"
            
        except VideoUnavailable:
            video_id = extract_video_id(video_url_or_id)
            return f"❌ Video '{video_id}' is unavailable or does not exist"
            
        except Exception as e:
            return f"❌ Error listing transcript languages: {str(e)}"
    
    return Tool(
        name="youtube_transcript_languages",
        description="List all available transcript languages for a YouTube video. Shows manual (human-created) and auto-generated transcripts with translation availability.",
        function=list_transcript_languages,
        parameters={
            "video_url_or_id": {
                "type": "str",
                "description": "YouTube video URL (e.g., https://youtube.com/watch?v=VIDEO_ID) or video ID (11 characters)",
                "required": True
            }
        }
    )


class YoutubeTranscriptTool:
    """
    YouTube Transcript Tool - YouTube Transcript API
    
    Professional-grade YouTube transcript retrieval tool for Brahmastra AI Agents.
    Similar to WikipediaSearchTool and YoutubeSearchTool, provides multiple sub-tools
    that can be used with agent.add_tools().
    
    Provides 2 specialized tools:
    1. youtube_transcript - Retrieve video transcripts with language support
    2. youtube_transcript_languages - List available transcript languages
    
    Features:
    - 📝 Retrieve video transcripts/captions
    - 🌐 Multi-language support
    - 🔄 Auto-generated and manual captions
    - ⏱️ Timestamp support
    - 🔤 Translation capabilities
    - 📊 Available languages listing
    
    Examples:
        >>> # Basic usage
        >>> transcript = YoutubeTranscriptTool()
        >>> agent.add_tools(transcript)
        
        >>> # Custom language preference
        >>> transcript = YoutubeTranscriptTool(language="es", include_timestamps=True)
        >>> agent.add_tools(transcript)
        
        >>> # Get statistics
        >>> stats = transcript.get_stats()
        >>> print(f"Transcripts retrieved: {stats['transcript_requests']}")
    """
    
    def __init__(
        self,
        language: str = "en",
        include_timestamps: bool = True,
        max_chars: int = 50000
    ):
        """
        Initialize YouTube Transcript Tool.
        
        Args:
            language: Preferred language code (default: "en")
            include_timestamps: Include timestamps in output (default: True)
            max_chars: Maximum characters to return (default: 50000)
        
        Example:
            >>> # Default settings
            >>> transcript = YoutubeTranscriptTool()
            
            >>> # Custom settings
            >>> transcript = YoutubeTranscriptTool(
            ...     language="es",
            ...     include_timestamps=False,
            ...     max_chars=20000
            ... )
        """
        self.language = language
        self.include_timestamps = include_timestamps
        self.max_chars = max_chars
        
        # Usage statistics
        self.stats = {
            'transcript_requests': 0,
            'language_queries': 0
        }
        
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            self._api = YouTubeTranscriptApi
        except ImportError:
            raise ImportError(
                "youtube-transcript-api is required. "
                "Install with: pip install youtube-transcript-api"
            )
        
        # Create tools
        self._transcript_tool = create_youtube_transcript_tool(
            language=self.language,
            include_timestamps=self.include_timestamps,
            max_chars=self.max_chars
        )
        self._languages_tool = create_youtube_transcript_languages_tool()
        
        # Wrap functions to track statistics
        self._wrap_with_stats()
    
    def _wrap_with_stats(self):
        """Wrap tool functions with statistics tracking."""
        original_transcript_func = self._transcript_tool.function
        original_languages_func = self._languages_tool.function
        
        def transcript_wrapper(*args, **kwargs):
            self.stats['transcript_requests'] += 1
            return original_transcript_func(*args, **kwargs)
        
        def languages_wrapper(*args, **kwargs):
            self.stats['language_queries'] += 1
            return original_languages_func(*args, **kwargs)
        
        self._transcript_tool.function = transcript_wrapper
        self._languages_tool.function = languages_wrapper
    
    def __iter__(self) -> Iterator[Tool]:
        """
        Make YoutubeTranscriptTool iterable so it can be unpacked directly.
        
        This allows: agent.add_tools(transcript) instead of agent.add_tools(*transcript())
        
        Yields:
            Tool objects (transcript_tool, languages_tool)
            
        Example:
            >>> transcript = YoutubeTranscriptTool()
            >>> agent.add_tools(transcript)  # Automatically unpacks
        """
        yield self._transcript_tool
        yield self._languages_tool
    
    def __call__(self):
        """
        Get all YouTube transcript tools as a list.
        
        Returns:
            List of Tool objects [transcript_tool, languages_tool]
            
        Example:
            >>> transcript = YoutubeTranscriptTool()
            >>> tools = transcript()
            >>> agent.add_tools(*tools)
        """
        return list(self)
    
    @classmethod
    def create_all_tools(
        cls,
        language: str = "en",
        include_timestamps: bool = True,
        max_chars: int = 50000
    ):
        """
        Class method to create all YouTube transcript tools at once.
        
        Args:
            language: Preferred language code (default: "en")
            include_timestamps: Include timestamps in output (default: True)
            max_chars: Maximum characters to return (default: 50000)
            
        Returns:
            List of Tool objects [transcript_tool, languages_tool]
            
        Example:
            >>> tools = YoutubeTranscriptTool.create_all_tools(language="en")
            >>> agent.add_tools(*tools)
        """
        instance = cls(language, include_timestamps, max_chars)
        return instance()
    
    def get_transcript_tool(self) -> Tool:
        """Get the YouTube transcript retrieval tool."""
        return self._transcript_tool
    
    def get_languages_tool(self) -> Tool:
        """Get the transcript languages listing tool."""
        return self._languages_tool
    
    def get_transcript(
        self,
        video_url_or_id: str,
        languages: Optional[str] = None,
        translate_to: Optional[str] = None
    ) -> str:
        """
        Direct method to retrieve transcript.
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            languages: Comma-separated language codes (optional)
            translate_to: Translate to this language (optional)
            
        Returns:
            Formatted transcript
        """
        return self._transcript_tool.function(
            video_url_or_id=video_url_or_id,
            languages=languages,
            translate_to=translate_to
        )
    
    def list_languages(self, video_url_or_id: str) -> str:
        """
        Direct method to list available transcript languages.
        
        Args:
            video_url_or_id: YouTube video URL or video ID
            
        Returns:
            List of available languages
        """
        return self._languages_tool.function(video_url_or_id=video_url_or_id)
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def set_language(self, language: str):
        """
        Change the default language preference.
        
        Args:
            language: New language code (e.g., 'en', 'es', 'fr')
        """
        self.language = language
        # Recreate transcript tool with new language
        self._transcript_tool = create_youtube_transcript_tool(
            language=self.language,
            include_timestamps=self.include_timestamps,
            max_chars=self.max_chars
        )
        self._wrap_with_stats()
        return f"✓ Language changed to: {language}"
    
    @property
    def transcript_tool(self) -> Tool:
        """Get transcript retrieval tool."""
        return self._transcript_tool
    
    @property
    def languages_tool(self) -> Tool:
        """Get languages listing tool."""
        return self._languages_tool


__all__ = [
    "YoutubeTranscriptTool",
    "create_youtube_transcript_tool",
    "create_youtube_transcript_languages_tool"
]
