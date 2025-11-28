# YouTube Search Tool - Official YouTube Data API v3

**Professional-grade YouTube search and analytics for Brahmastra AI Agents**

A pre-built tool using Google's official YouTube Data API v3, providing comprehensive search capabilities with advanced filters, channel analytics, and video details.

---

## Features

### 🔍 Advanced Video Search
- **10+ Filter Options**: Duration, date range, quality, order, safe search
- **Multiple Sort Options**: Relevance, date, rating, view count, title
- **Rich Metadata**: Views, likes, duration, thumbnails, descriptions
- **Content Types**: Videos, channels, playlists

### 📺 Channel Analytics
- **Statistics**: Subscriber count, video count, total views
- **Recent Uploads**: Latest 5 videos from channel
- **Handle Support**: Works with @username or channel ID
- **Country & Creation Date**: Full channel metadata

### 🎬 Video Details
- **Statistics**: Views, likes, comments
- **Metadata**: Duration, tags, description, channel info
- **Publication Date**: Upload timestamp

---

## Quick Start

### Prerequisites

1. **Get YouTube Data API v3 Key**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create/select a project
   - Enable "YouTube Data API v3"
   - Create credentials (API Key)

2. **Install Dependencies**:
   ```bash
   pip install google-api-python-client
   ```

3. **Set Environment Variable** (Optional if passing API key directly):

   ```powershell
   # PowerShell
   $env:YOUTUBE_API_KEY = "your-api-key-here"
   ```

### API Key Configuration

You have two options to provide your YouTube API key:

**Option 1: Environment Variable** (Recommended)
```python
youtube = YoutubeSearchTool()  # Reads from YOUTUBE_API_KEY env variable
```

**Option 2: Direct Parameter**
```python
youtube = YoutubeSearchTool(api_key="your-api-key-here")
```

### Basic Usage

```python
from brahmastra.prebuild_tool import YoutubeSearchTool
from brahmastra.llm_agent import ReActAgent
from brahmastra.llm_provider import GoogleLLM

# Create YouTube tool (Option 1: Use environment variable)
youtube = YoutubeSearchTool()  # Uses YOUTUBE_API_KEY env variable

# Or create with API key directly (Option 2: Pass API key)
youtube = YoutubeSearchTool(api_key="your-api-key-here")

# Create agent
llm = GoogleLLM(model="gemini-2.0-flash-exp")
agent = ReActAgent(llm=llm)

# Add tools (automatically adds all 3 tools)
agent.add_tools(youtube)

# Run query
response = agent.run("Find Python tutorials from 2024")
print(response)
```

---

## Available Tools

The `YoutubeSearchTool` provides 3 tools:

### 1. `youtube_advanced_search`

Advanced YouTube search with comprehensive filters.

**Parameters**:

- `query` (required) - Search query string
- `max_results` (1-50) - Maximum results (default: 5)
- `order` - Sort: 'relevance', 'date', 'rating', 'viewCount', 'title'
- `video_duration` - Filter: 'short' (<4min), 'medium' (4-20min), 'long' (>20min)
- `published_after` - ISO 8601 date (e.g., '2024-01-01T00:00:00Z')
- `published_before` - ISO 8601 date
- `channel_id` - Search within specific channel
- `video_type` - Type: 'video', 'channel', 'playlist'
- `video_definition` - Quality: 'high' (HD), 'standard'
- `safe_search` - Filter: 'none', 'moderate', 'strict'

### 2. `youtube_channel_info`
Get detailed channel information and statistics.

**Parameters**:
- `channel_id` (required) - Channel ID (UCxxxx) or handle (@username)

### 3. `youtube_video_details`
Get comprehensive video information.

**Parameters**:
- `video_id` (required) - Video ID (11 characters from URL)

---

## Example Usage

### Advanced Search with Filters

```python
# Find recent Python tutorials
response = agent.run("""
Find Python programming tutorials:
- Published after 2024-01-01
- Duration: long (>20 minutes)
- Quality: high definition
- Order by view count
- Limit to 3 results
""")
```

### Channel Analysis

```python
# Get channel statistics
response = agent.run("Get details about @Fireship channel")
```

### Video Details

```python
# Get video information
response = agent.run("Get details for video ID: dQw4w9WgXcQ")
```

---

## API Quota Management

YouTube Data API v3 has quota limits:
- **Default quota**: 10,000 units/day
- **Search**: 100 units per query
- **Video details**: 1 unit per query
- **Channel info**: 1 unit per query

**Tips**:
- Cache results when possible
- Use specific queries to reduce re-searches
- Monitor usage in Google Cloud Console

---

## Comparison: Official API vs yt-dlp

| Feature | YouTube API | yt-dlp Tool |
|---------|-------------|-------------|
| API Key Required | ✅ Yes | ❌ No |
| Quota Limits | ✅ 10k/day | ❌ Unlimited |
| Date Range Filter | ✅ Yes | ❌ No |
| Duration Filter | ✅ Yes | ❌ No |
| Order By Options | ✅ 5 options | ⚠️ Relevance only |
| Quality Filter | ✅ Yes | ❌ No |
| Channel Analytics | ✅ Full stats | ⚠️ Basic |
| Real-time Stats | ✅ Yes | ⚠️ Basic |

**Use YouTube API when**: Need advanced filters, real-time statistics, professional applications

**Use yt-dlp when**: Quick prototyping, no API key available, unlimited queries needed

---

## Troubleshooting

### "YouTube API key required"
Set the `YOUTUBE_API_KEY` environment variable:
```powershell
$env:YOUTUBE_API_KEY = "your-key"
```

### "quotaExceeded"
You've exceeded the daily 10,000 quota. Wait until next day or request quota increase.

### "API key not valid"
- Verify key in Google Cloud Console
- Enable "YouTube Data API v3"
- Regenerate key if needed

---

## Statistics Tracking

Track tool usage:

```python
# Option 1: Using environment variable
youtube = YoutubeSearchTool()

# Option 2: Passing API key directly
youtube = YoutubeSearchTool(api_key="your-api-key-here")

agent.add_tools(youtube)

# Run queries
agent.run("Find Python tutorials")
agent.run("Get @Fireship channel info")

# Check usage
stats = youtube.get_stats()
print(f"Searches: {stats['searches']}")
print(f"Channel lookups: {stats['channel_lookups']}")
print(f"Video lookups: {stats['video_lookups']}")
```

---

## License

MIT License - Part of Brahmastra Framework

---

**Made with ❤️ for the Brahmastra AI Agent Framework**
