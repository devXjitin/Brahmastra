"""
YouTube Search Tool - Hybrid API + yt-dlp (Best of Both Worlds)

A professional-grade tool that prioritizes YouTube Data API v3 for search,
with automatic fallback to yt-dlp when API is unavailable or fails.

Features:
- 🔑 Primary: YouTube Data API v3 (when available)
- 🔄 Fallback: yt-dlp (when API unavailable/fails)
- 🎯 Advanced search filters (duration, date, order, quality, etc.)
- 📊 Complete video metadata (views, likes, comments, duration)
- 📺 Channel information and statistics
- ⚡ Optimal performance with smart fallback

Requires:
- yt-dlp (pip install yt-dlp) - Required
- google-api-python-client (optional) - For API mode

API Setup (Optional but Recommended):
- Set YOUTUBE_API_KEY environment variable
- Get key from: https://console.cloud.google.com/

Example:
    >>> from youtube_tool import YouTubeSearchTool
    >>> 
    >>> youtube = YouTubeSearchTool()  # Auto-detects API key
    >>> agent.add_tools(youtube)
"""

from typing import Dict, Optional, List, Iterator
from brahmastra.core import Tool
from datetime import datetime
import subprocess
import json
import os


def format_number(num) -> str:
    """Format large numbers to readable format."""
    if not num:
        return "0"
    
    try:
        num = int(num)
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    except:
        return str(num)


def format_duration(seconds) -> str:
    """Format duration in seconds to readable format."""
    if not seconds:
        return "Unknown"
    
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    except:
        return str(seconds)


def format_duration_iso(duration: str) -> str:
    """Convert ISO 8601 duration to readable format (for API responses)."""
    import re
    
    if not duration:
        return "Unknown"
    
    # Parse ISO 8601 duration (PT#H#M#S)
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        elif minutes > 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"0:{seconds:02d}"
    return duration


def create_youtube_advanced_search_tool(api_key: Optional[str] = None) -> Tool:
    """
    Create an advanced YouTube search tool with hybrid API + yt-dlp approach.
    Tries YouTube Data API v3 first (if available), falls back to yt-dlp.
    
    Args:
        api_key: YouTube Data API v3 key (optional). If not provided, 
                reads from YOUTUBE_API_KEY environment variable.
                If no API key, uses yt-dlp directly.
    
    Returns:
        Tool object for advanced YouTube search
    
    Examples:
        >>> # With API key (recommended)
        >>> youtube = create_youtube_advanced_search_tool(api_key="AIza...")
        >>> agent.add_tools(youtube)
        
        >>> # Without API key (uses yt-dlp)
        >>> youtube = create_youtube_advanced_search_tool()
        >>> agent.add_tools(youtube)
    """
    # Check if API is available
    api_key = api_key or os.getenv('YOUTUBE_API_KEY')
    has_api = False
    
    if api_key:
        try:
            from googleapiclient.discovery import build
            has_api = True
        except ImportError:
            has_api = False
    
    # Check if yt-dlp is available (fallback)
    try:
        import yt_dlp
    except ImportError:
        if not has_api:
            raise ImportError(
                "Either google-api-python-client OR yt-dlp is required.\n"
                "Install with: pip install google-api-python-client\n"
                "Or: pip install yt-dlp"
            )
    
    def youtube_advanced_search(
        query: str,
        max_results: int = 5,
        order: str = "relevance",
        video_duration: Optional[str] = None,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        channel_id: Optional[str] = None,
        video_type: str = "video",
        video_definition: Optional[str] = None,
        safe_search: str = "none",
        region: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Advanced YouTube search - tries API first, falls back to yt-dlp.
        
        Args:
            query: Search query string
            max_results: Maximum results (1-50, default: 5)
            order: Sort order - 'relevance', 'date', 'rating', 'viewCount' (API) or 'views' (yt-dlp)
            video_duration: Duration filter - 'short' (<4min), 'medium' (4-20min), 'long' (>20min)
            published_after: ISO 8601 date (e.g., '2024-01-01T00:00:00Z')
            published_before: ISO 8601 date
            channel_id: Search within specific channel (channel ID like UCxxxx or @handle)
            video_type: Type - 'video', 'channel', 'playlist'
            video_definition: Quality - 'high' (HD), 'standard'
            safe_search: Filter - 'none', 'moderate', 'strict'
            region: Region code (e.g., 'US', 'GB', 'IN')
            language: Language code (e.g., 'en', 'es', 'hi')
            
        Returns:
            Formatted search results with detailed metadata
        """
        
        # Try API first (if available)
        if has_api and api_key:
            try:
                from googleapiclient.discovery import build
                youtube = build('youtube', 'v3', developerKey=api_key)
                
                # Prepare search parameters
                search_params = {
                    'q': query,
                    'part': 'snippet',
                    'maxResults': min(max_results, 50),
                    'order': order if order in ['relevance', 'date', 'rating', 'viewCount', 'title'] else 'relevance',
                    'type': video_type,
                    'safeSearch': safe_search
                }
                
                # Add optional filters
                if video_duration:
                    search_params['videoDuration'] = video_duration
                if published_after:
                    search_params['publishedAfter'] = published_after
                if published_before:
                    search_params['publishedBefore'] = published_before
                if channel_id and not channel_id.startswith('@'):
                    search_params['channelId'] = channel_id
                if video_definition:
                    search_params['videoDefinition'] = video_definition
                if region:
                    search_params['regionCode'] = region
                if language:
                    search_params['relevanceLanguage'] = language
                
                # Execute search
                search_response = youtube.search().list(**search_params).execute()
                
                if not search_response.get('items'):
                    return f"❌ No results found for '{query}'"
                
                items = search_response['items']
                
                # Get video IDs for detailed stats
                video_ids = [item['id']['videoId'] for item in items if item['id']['kind'] == 'youtube#video']
                
                # Get video statistics
                video_stats = {}
                if video_ids:
                    stats_response = youtube.videos().list(
                        part='statistics,contentDetails',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for video in stats_response.get('items', []):
                        video_stats[video['id']] = {
                            'views': video['statistics'].get('viewCount', '0'),
                            'likes': video['statistics'].get('likeCount', '0'),
                            'comments': video['statistics'].get('commentCount', '0'),
                            'duration': video['contentDetails'].get('duration', 'PT0S')
                        }
                
                # Format output
                output = f"🎥 **YouTube Advanced Search Results** (via API)\n\n"
                output += f"Query: '{query}'\n"
                output += f"Results: {len(items)}\n\n"
                
                for idx, item in enumerate(items, 1):
                    snippet = item['snippet']
                    title = snippet['title']
                    channel = snippet['channelTitle']
                    description = snippet['description'][:150] + "..." if len(snippet['description']) > 150 else snippet['description']
                    published = snippet['publishedAt'][:10]
                    
                    if item['id']['kind'] == 'youtube#video':
                        video_id = item['id']['videoId']
                        link = f"https://www.youtube.com/watch?v={video_id}"
                        
                        stats = video_stats.get(video_id, {})
                        views = format_number(stats.get('views', 0))
                        likes = format_number(stats.get('likes', 0))
                        duration = format_duration_iso(stats.get('duration', 'PT0S'))
                        comments = format_number(stats.get('comments', 0))
                        
                        output += f"**{idx}. {title}**\n"
                        output += f"   📺 Channel: {channel}\n"
                        output += f"   ⏱️  Duration: {duration}\n"
                        output += f"   👁️  Views: {views}\n"
                        output += f"   👍 Likes: {likes}\n"
                        if comments != "0":
                            output += f"   💬 Comments: {comments}\n"
                        output += f"   📅 Published: {published}\n"
                        output += f"   📝 {description}\n"
                        output += f"   🔗 {link}\n\n"
                
                return output.strip()
                
            except Exception as api_error:
                # API failed, fall back to yt-dlp
                # Common failures: quota exceeded, invalid API key, network error
                pass
        
        # Fallback to yt-dlp (when API unavailable or failed)
        try:
            import yt_dlp
            # Build search query with channel filter if specified
            if channel_id:
                if channel_id.startswith('@'):
                    query = f"{query} site:youtube.com/{channel_id}"
                elif channel_id.startswith('UC'):
                    query = f"{query} site:youtube.com/channel/{channel_id}"
            
            # Build search prefix based on order
            search_prefix = "ytsearch"
            if order == "date":
                search_prefix = "ytsearchdate"
            
            search_query = f"{search_prefix}{max_results}:{query}"
            
            # Configure yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
                'format': 'best',
                'ignoreerrors': True,
            }
            
            # Add region/language if specified
            if region:
                ydl_opts['geo_bypass_country'] = region
            
            # Build match filter for advanced filtering
            match_filters = []
            
            # Duration filter
            if video_duration == "short":
                match_filters.append("duration < 240")  # < 4 minutes
            elif video_duration == "medium":
                match_filters.append("duration >= 240 & duration <= 1200")  # 4-20 minutes
            elif video_duration == "long":
                match_filters.append("duration > 1200")  # > 20 minutes
            
            # Date filters
            if published_after:
                try:
                    # Convert to timestamp
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(published_after.replace('Z', '+00:00'))
                    timestamp = int(date_obj.timestamp())
                    match_filters.append(f"timestamp >= {timestamp}")
                except:
                    pass
            
            if published_before:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(published_before.replace('Z', '+00:00'))
                    timestamp = int(date_obj.timestamp())
                    match_filters.append(f"timestamp <= {timestamp}")
                except:
                    pass
            
            # Video definition (quality) filter
            if video_definition == "high":
                match_filters.append("height >= 720")
            elif video_definition == "standard":
                match_filters.append("height < 720")
            
            # Apply match filters
            if match_filters:
                ydl_opts['match_filter'] = yt_dlp.utils.match_filter_func(' & '.join(match_filters))  # type: ignore
            
            # Execute search
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                try:
                    info = ydl.extract_info(search_query, download=False)
                except Exception as e:
                    return f"❌ Search error: {str(e)}"
                
                if not info or 'entries' not in info:
                    return f"❌ No results found for '{query}'"
                
                entries = [e for e in info['entries'] if e is not None]  # type: ignore
                
                if not entries:
                    return f"❌ No results found for '{query}'"
                
                # Format output
                output = f"🎥 **YouTube Advanced Search Results** (via yt-dlp)\n\n"
                output += f"Query: '{query}'\n"
                
                # Show active filters
                filters_active = []
                if order != "relevance":
                    filters_active.append(f"order={order}")
                if video_duration:
                    filters_active.append(f"duration={video_duration}")
                if published_after:
                    filters_active.append(f"after={published_after}")
                if published_before:
                    filters_active.append(f"before={published_before}")
                if channel_id:
                    filters_active.append(f"channel={channel_id}")
                if video_definition:
                    filters_active.append(f"quality={video_definition}")
                if region:
                    filters_active.append(f"region={region}")
                
                if filters_active:
                    output += f"Filters: {', '.join(filters_active)}\n"
                
                output += f"Results: {len(entries)}\n\n"
                
                for idx, video in enumerate(entries, 1):
                    title = video.get('title', 'Unknown')
                    channel = video.get('uploader', video.get('channel', 'Unknown'))
                    channel_id_result = video.get('channel_id', '')
                    video_id = video.get('id', '')
                    duration = format_duration(video.get('duration', 0))
                    views = format_number(video.get('view_count', 0))
                    likes = format_number(video.get('like_count', 0))
                    comments = format_number(video.get('comment_count', 0))
                    upload_date = video.get('upload_date', 'Unknown')
                    description = video.get('description', '')
                    resolution = video.get('height', 0)
                    
                    # Format upload date
                    if upload_date and upload_date != 'Unknown':
                        try:
                            upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        except:
                            pass
                    
                    # Truncate description
                    if description and len(description) > 150:
                        description = description[:150] + "..."
                    
                    # Quality indicator
                    quality = "HD" if resolution >= 720 else "SD" if resolution > 0 else "Unknown"
                    
                    output += f"**{idx}. {title}**\n"
                    output += f"   📺 Channel: {channel}\n"
                    output += f"   ⏱️  Duration: {duration}\n"
                    output += f"   👁️  Views: {views}\n"
                    output += f"   👍 Likes: {likes}\n"
                    
                    if comments != "0":
                        output += f"   💬 Comments: {comments}\n"
                    
                    output += f"   📅 Published: {upload_date}\n"
                    output += f"   🎬 Quality: {quality}\n"
                    
                    if description:
                        output += f"   📝 {description}\n"
                    
                    output += f"   🔗 https://www.youtube.com/watch?v={video_id}\n\n"
                
                return output.strip()
                
        except Exception as e:
            return f"❌ Error: {str(e)}\n\n💡 Tip: Make sure yt-dlp is installed and updated: pip install -U yt-dlp"
    
    return Tool(
        name="youtube_advanced_search",
        description=(
            "Advanced YouTube search with hybrid approach: uses YouTube Data API v3 (if available) "
            "for fast, reliable results, or falls back to yt-dlp (no API key required). "
            "Supports comprehensive filters: order (relevance/date/rating/viewCount/views), "
            "duration (short/medium/long), date range (published_after/before), "
            "channel filter, quality (high/standard), region, language, safe_search. "
            "Returns complete metadata: title, channel, views, likes, comments, duration, quality, description."
        ),
        function=youtube_advanced_search,
        parameters={
            "query": {
                "type": "str",
                "description": "Search query string",
                "required": True
            },
            "max_results": {
                "type": "int",
                "description": "Maximum results (1-50, default: 5)",
                "required": False
            },
            "order": {
                "type": "str",
                "description": "Sort order: 'relevance', 'date', 'views', 'rating' (default: relevance)",
                "required": False
            },
            "video_duration": {
                "type": "str",
                "description": "Duration filter: 'short' (<4min), 'medium' (4-20min), 'long' (>20min)",
                "required": False
            },
            "published_after": {
                "type": "str",
                "description": "ISO 8601 date (e.g., '2024-01-01' or '2024-01-01T00:00:00Z') - videos published after this date",
                "required": False
            },
            "published_before": {
                "type": "str",
                "description": "ISO 8601 date - videos published before this date",
                "required": False
            },
            "channel_id": {
                "type": "str",
                "description": "Search within specific channel (channel ID like UCxxxxxx or @handle)",
                "required": False
            },
            "video_type": {
                "type": "str",
                "description": "Type: 'video', 'channel', 'playlist' (default: video)",
                "required": False
            },
            "video_definition": {
                "type": "str",
                "description": "Quality filter: 'high' (HD/720p+), 'standard' (<720p), 'any'",
                "required": False
            },
            "safe_search": {
                "type": "str",
                "description": "Filter: 'none', 'moderate', 'strict' (default: none)",
                "required": False
            },
            "region": {
                "type": "str",
                "description": "Region code for localized results (e.g., 'US', 'GB', 'IN', 'JP')",
                "required": False
            },
            "language": {
                "type": "str",
                "description": "Language code for localized results (e.g., 'en', 'es', 'hi', 'ja')",
                "required": False
            }
        }
    )


def create_youtube_channel_tool() -> Tool:
    """
    Create a tool to get YouTube channel information using yt-dlp.
    
    Returns:
        Tool for channel information retrieval
    
    Examples:
        >>> channel_tool = create_youtube_channel_tool()
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required")
    
    def get_channel_info(channel_identifier: str) -> str:
        """
        Get detailed YouTube channel information using yt-dlp.
        
        Args:
            channel_identifier: Channel @handle, channel ID, or full URL
            
        Returns:
            Channel information with statistics and recent uploads
        """
        try:
            # Build channel URL
            if channel_identifier.startswith('http'):
                url = channel_identifier
            elif channel_identifier.startswith('@'):
                url = f"https://www.youtube.com/{channel_identifier}"
            elif channel_identifier.startswith('UC'):
                url = f"https://www.youtube.com/channel/{channel_identifier}"
            else:
                url = f"https://www.youtube.com/@{channel_identifier}"
            
            # Get channel info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return f"❌ Channel '{channel_identifier}' not found"
                
                channel_name = info.get('uploader', info.get('channel', 'Unknown'))
                channel_id = info.get('channel_id', info.get('uploader_id', 'Unknown'))
                subscriber_count = format_number(info.get('channel_follower_count', 0))
                description = info.get('description', 'No description available')
                
                # Truncate description
                if len(description) > 300:
                    description = description[:300] + "..."
                
                output = f"📺 **Channel Information**\n\n"
                output += f"**{channel_name}**\n\n"
                output += f"👥 Subscribers: {subscriber_count}\n"
                output += f"🆔 Channel ID: {channel_id}\n\n"
                output += f"📝 Description:\n{description}\n\n"
                
                # Get recent uploads
                entries = info.get('entries', [])
                if entries:
                    output += f"📌 **Recent Uploads** (showing up to 5):\n\n"
                    for idx, video in enumerate(entries[:5], 1):
                        if video:
                            video_title = video.get('title', 'Unknown')
                            video_id = video.get('id', '')
                            output += f"{idx}. {video_title}\n"
                            output += f"   🔗 https://www.youtube.com/watch?v={video_id}\n"
                
                output += f"\n🔗 Channel: {url}\n"
                
                return output
                
        except Exception as e:
            return f"❌ Error getting channel info: {str(e)}"
    
    return Tool(
        name="youtube_channel_info",
        description="Get YouTube channel information using yt-dlp. Accepts @handle, channel ID (UCxxxx), or full URL. Returns subscriber count, description, and recent uploads.",
        function=get_channel_info,
        parameters={
            "channel_identifier": {
                "type": "str",
                "description": "Channel @handle, channel ID (UCxxxx), or full YouTube URL",
                "required": True
            }
        }
    )


def create_youtube_video_tool() -> Tool:
    """
    Create a tool to get YouTube video information using yt-dlp.
    
    Returns:
        Tool for video details retrieval
    
    Examples:
        >>> video_tool = create_youtube_video_tool()
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required")
    
    def get_video_details(video_url_or_id: str) -> str:
        """
        Get detailed YouTube video information using yt-dlp.
        
        Args:
            video_url_or_id: Full YouTube URL or video ID
            
        Returns:
            Complete video information with statistics
        """
        try:
            # Build URL if only ID provided
            if not video_url_or_id.startswith('http'):
                url = f"https://www.youtube.com/watch?v={video_url_or_id}"
            else:
                url = video_url_or_id
            
            # Get video info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return f"❌ Video not found or unavailable"
                
                title = info.get('title', 'Unknown')
                channel = info.get('uploader', info.get('channel', 'Unknown'))
                channel_id = info.get('channel_id', 'Unknown')
                video_id = info.get('id', '')
                duration = format_duration(info.get('duration', 0))
                views = format_number(info.get('view_count', 0))
                likes = format_number(info.get('like_count', 0))
                comments = format_number(info.get('comment_count', 0))
                upload_date = info.get('upload_date', 'Unknown')
                description = info.get('description', 'No description')
                tags = info.get('tags', [])
                categories = info.get('categories', [])
                
                # Format upload date
                if upload_date and upload_date != 'Unknown':
                    try:
                        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                    except:
                        pass
                
                # Truncate description
                if len(description) > 500:
                    description = description[:500] + "..."
                
                output = f"🎥 **Video Details**\n\n"
                output += f"**{title}**\n\n"
                output += f"📺 Channel: {channel}\n"
                output += f"🆔 Channel ID: {channel_id}\n"
                output += f"⏱️  Duration: {duration}\n"
                output += f"👁️  Views: {views}\n"
                output += f"👍 Likes: {likes}\n"
                output += f"💬 Comments: {comments}\n"
                output += f"📅 Published: {upload_date}\n"
                
                if categories:
                    output += f"🏷️  Category: {categories[0]}\n"
                
                output += f"\n📝 Description:\n{description}\n"
                
                if tags:
                    tags_str = ', '.join(tags[:10])
                    output += f"\n🏷️  Tags: {tags_str}\n"
                
                output += f"\n🔗 {url}\n"
                
                return output
                
        except Exception as e:
            return f"❌ Error getting video details: {str(e)}"
    
    return Tool(
        name="youtube_video_details",
        description="Get complete YouTube video information using yt-dlp. Accepts full URL or video ID. Returns title, channel, duration, views, likes, comments, description, and tags.",
        function=get_video_details,
        parameters={
            "video_url_or_id": {
                "type": "str",
                "description": "Full YouTube URL or 11-character video ID",
                "required": True
            }
        }
    )


def create_youtube_playlist_tool() -> Tool:
    """
    Create a tool to get YouTube playlist information using yt-dlp.
    
    Returns:
        Tool for playlist information retrieval
    
    Examples:
        >>> playlist_tool = create_youtube_playlist_tool()
    """
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp is required")
    
    def get_playlist_info(playlist_url_or_id: str, max_videos: int = 10) -> str:
        """
        Get YouTube playlist information using yt-dlp.
        
        Args:
            playlist_url_or_id: Full playlist URL or playlist ID
            max_videos: Maximum number of videos to show (default: 10)
            
        Returns:
            Playlist information with video list
        """
        try:
            # Build URL if only ID provided
            if not playlist_url_or_id.startswith('http'):
                url = f"https://www.youtube.com/playlist?list={playlist_url_or_id}"
            else:
                url = playlist_url_or_id
            
            # Get playlist info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return f"❌ Playlist not found or unavailable"
                
                title = info.get('title', 'Unknown Playlist')
                uploader = info.get('uploader', info.get('channel', 'Unknown'))
                playlist_id = info.get('id', '')
                description = info.get('description', 'No description')
                entries = info.get('entries', [])
                video_count = len(entries)
                
                # Truncate description
                if description and len(description) > 200:
                    description = description[:200] + "..."
                
                output = f"📚 **Playlist Information**\n\n"
                output += f"**{title}**\n\n"
                output += f"📺 Channel: {uploader}\n"
                output += f"🎬 Total Videos: {video_count}\n"
                output += f"🆔 Playlist ID: {playlist_id}\n\n"
                
                if description:
                    output += f"📝 Description: {description}\n\n"
                
                if entries:
                    output += f"📌 **Videos** (showing {min(max_videos, video_count)} of {video_count}):\n\n"
                    for idx, video in enumerate(entries[:max_videos], 1):
                        if video:
                            video_title = video.get('title', 'Unknown')
                            video_id = video.get('id', '')
                            video_duration = format_duration(video.get('duration', 0))
                            
                            output += f"{idx}. {video_title}\n"
                            output += f"   ⏱️  {video_duration}\n"
                            output += f"   🔗 https://www.youtube.com/watch?v={video_id}\n"
                
                output += f"\n🔗 Playlist: {url}\n"
                
                return output
                
        except Exception as e:
            return f"❌ Error getting playlist info: {str(e)}"
    
    return Tool(
        name="youtube_playlist_info",
        description="Get YouTube playlist information using yt-dlp. Accepts full URL or playlist ID. Returns title, channel, video count, and list of videos with durations.",
        function=get_playlist_info,
        parameters={
            "playlist_url_or_id": {
                "type": "str",
                "description": "Full playlist URL or playlist ID",
                "required": True
            },
            "max_videos": {
                "type": "int",
                "description": "Maximum number of videos to show (default: 10)",
                "required": False
            }
        }
    )


class YouTubeSearchTool:
    """
    YouTube Search Tool - Hybrid API + yt-dlp (Best of Both Worlds)
    
    Professional-grade YouTube search tool that prioritizes API (when available),
    with automatic fallback to yt-dlp for maximum reliability.
    
    Provides 4 professional-grade tools:
    1. youtube_advanced_search - Advanced search (API first, yt-dlp fallback)
    2. youtube_channel_info - Channel information and statistics (yt-dlp)
    3. youtube_video_details - Complete video information (yt-dlp)
    4. youtube_playlist_info - Playlist information and video list (yt-dlp)
    
    Examples:
        >>> # With API key (recommended for search)
        >>> youtube = YouTubeSearchTool(api_key="AIza...")
        >>> agent.add_tools(youtube)
        
        >>> # Without API key (uses yt-dlp)
        >>> youtube = YouTubeSearchTool()
        >>> agent.add_tools(youtube)
        
        >>> # Or unpack individual tools
        >>> search, channel, video, playlist = YouTubeSearchTool()
        >>> agent.add_tools([search, channel, video])
        
        >>> # Get statistics
        >>> stats = youtube.get_stats()
        >>> print(f"Searches: {stats['searches']}")
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube Search Tool with optional API key.
        
        Args:
            api_key: YouTube Data API v3 key (optional). If provided,
                    search will use API first, then fallback to yt-dlp.
                    If not provided, reads from YOUTUBE_API_KEY env var
                    or uses yt-dlp directly.
        
        Examples:
            >>> # With API key (recommended)
            >>> youtube = YouTubeSearchTool(api_key="AIza...")
            
            >>> # Without API key (uses yt-dlp)
            >>> youtube = YouTubeSearchTool()
            >>> agent.add_tools(youtube)
        """
        try:
            import yt_dlp
        except ImportError:
            raise ImportError(
                "yt-dlp is required. Install with: pip install yt-dlp"
            )
        
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        
        self.stats = {
            'searches': 0,
            'channel_lookups': 0,
            'video_lookups': 0,
            'playlist_lookups': 0
        }
        
        # Create tools (search supports API, others use yt-dlp)
        self._search_tool = create_youtube_advanced_search_tool(self.api_key)
        self._channel_tool = create_youtube_channel_tool()
        self._video_tool = create_youtube_video_tool()
        self._playlist_tool = create_youtube_playlist_tool()
        
        # Wrap functions to track statistics
        self._wrap_with_stats()
    
    def _wrap_with_stats(self):
        """Wrap tool functions with statistics tracking."""
        original_search = self._search_tool.function
        original_channel = self._channel_tool.function
        original_video = self._video_tool.function
        original_playlist = self._playlist_tool.function
        
        def search_wrapper(*args, **kwargs):
            self.stats['searches'] += 1
            return original_search(*args, **kwargs)
        
        def channel_wrapper(*args, **kwargs):
            self.stats['channel_lookups'] += 1
            return original_channel(*args, **kwargs)
        
        def video_wrapper(*args, **kwargs):
            self.stats['video_lookups'] += 1
            return original_video(*args, **kwargs)
        
        def playlist_wrapper(*args, **kwargs):
            self.stats['playlist_lookups'] += 1
            return original_playlist(*args, **kwargs)
        
        self._search_tool.function = search_wrapper
        self._channel_tool.function = channel_wrapper
        self._video_tool.function = video_wrapper
        self._playlist_tool.function = playlist_wrapper
    
    def __iter__(self) -> Iterator[Tool]:
        """Allow unpacking: search, channel, video, playlist = YouTubeSearchTool()"""
        return iter([self._search_tool, self._channel_tool, self._video_tool, self._playlist_tool])
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        return self.stats.copy()
    
    @property
    def search_tool(self) -> Tool:
        """Get search tool."""
        return self._search_tool
    
    @property
    def channel_tool(self) -> Tool:
        """Get channel info tool."""
        return self._channel_tool
    
    @property
    def video_tool(self) -> Tool:
        """Get video details tool."""
        return self._video_tool
    
    @property
    def playlist_tool(self) -> Tool:
        """Get playlist info tool."""
        return self._playlist_tool


def create_youtube_channel_info_tool() -> Tool:
    """
    Create a tool to get YouTube channel information (alias for create_youtube_channel_tool).
    
    Returns:
        Tool for channel information retrieval
    
    Examples:
        >>> channel_tool = create_youtube_channel_info_tool()
    """
    return create_youtube_channel_tool()


def create_youtube_video_details_tool() -> Tool:
    """
    Create a tool to get YouTube video details (alias for create_youtube_video_tool).
    
    Returns:
        Tool for video details retrieval
    
    Examples:
        >>> video_tool = create_youtube_video_details_tool()
    """
    return create_youtube_video_tool()


__all__ = [
    "YouTubeSearchTool",
    "create_youtube_advanced_search_tool",
    "create_youtube_channel_tool",
    "create_youtube_video_tool",
    "create_youtube_playlist_tool",
    "create_youtube_channel_info_tool",
    "create_youtube_video_details_tool"
]