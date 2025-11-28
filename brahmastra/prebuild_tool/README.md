# 🛠️ Brahmastra Pre-built Tools

> Professional-grade, ready-to-use tools for Brahmastra AI agents. Seamlessly integrate powerful capabilities into your AI applications.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Overview](#-overview)
- [Available Tools](#-available-tools)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage Patterns](#-usage-patterns)
- [Tool Reference](#-tool-reference)
- [Contributing](#-contributing)

---

## 🎯 Overview

Pre-built Tools are **agent-friendly utilities** designed for seamless integration with Brahmastra AI agents. Each tool:

- ✅ **Plug & Play**: Add to any agent with `agent.add_tools(tool)`
- ✅ **Iterable Design**: Automatically unpacks multiple capabilities
- ✅ **Consistent API**: All tools follow the same patterns
- ✅ **Well Documented**: Comprehensive documentation and examples
- ✅ **Production Ready**: Robust error handling and retry logic

### Directory Structure

```
prebuild_tool/
├── __init__.py              # Main exports
├── README.md                # This file
├── wikipedia_tool/          # Wikipedia integration
│   ├── __init__.py
│   ├── base.py
│   └── README.md
├── YoutubeSearchTool/       # YouTube Data API integration
│   ├── __init__.py
│   ├── base.py
│   └── README.md
└── YoutubeTranscriptTool/   # YouTube transcript retrieval
    ├── __init__.py
    ├── base.py
    └── README.md
```

---

## 📦 Available Tools

| Tool | Description | Tools Provided | Dependencies |
|------|-------------|----------------|--------------|
| **WikipediaSearchTool** | Search & retrieve Wikipedia articles | 3 tools | `wikipedia` |
| **YoutubeSearchTool** | Search videos, get channel/video info | 3 tools | `google-api-python-client` |
| **YoutubeTranscriptTool** | Get video transcripts & captions | 2 tools | `youtube-transcript-api` |

---

## 🚀 Quick Start

### 1. Wikipedia Tool

Search and retrieve information from Wikipedia with smart disambiguation handling.

```python
from brahmastra.prebuild_tool import WikipediaSearchTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
wiki = WikipediaSearchTool(language="en", max_search_results=5)

# Create agent and add tools
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(wiki)  # Adds 3 tools: search, content, suggest

# Use
result = agent.invoke("What is quantum computing?")
```

**Provides 3 tools:**
- `wikipedia_search` - Search articles and get summaries
- `wikipedia_content` - Get full article content
- `wikipedia_suggest` - Get page title suggestions

**Features:**
- 🌐 200+ language support
- 🎯 Smart disambiguation resolution
- 📊 Relevance scoring
- ⚡ Automatic retry with backoff
- 📈 Usage statistics

[📖 Full Documentation →](wikipedia_tool/README.md)

---

### 2. YouTube Search Tool

Professional YouTube search using the official YouTube Data API v3.

```python
from brahmastra.prebuild_tool import YoutubeSearchTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool (uses YOUTUBE_API_KEY env variable)
youtube = YoutubeSearchTool()
# Or with explicit API key
youtube = YoutubeSearchTool(api_key="your-api-key")

# Create agent and add tools
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(youtube)  # Adds 3 tools: search, channel, video details

# Use
result = agent.invoke("Find Python tutorials from 2024 with >1M views")
```

**Provides 3 tools:**
- `youtube_advanced_search` - Search with 10+ filter options
- `youtube_channel_info` - Get channel stats and recent uploads
- `youtube_video_details` - Get video metadata and statistics

**Features:**
- 🔍 Advanced search filters (duration, date, quality, etc.)
- 📺 Channel analytics (subscribers, views, video count)
- 🎬 Video details (views, likes, comments, duration)
- 📊 Multiple sort options (relevance, date, rating, viewCount)
- 🔄 Automatic fallback to yt-dlp when API unavailable

[📖 Full Documentation →](YoutubeSearchTool/README.md)

---

### 3. YouTube Transcript Tool

Retrieve transcripts and captions from YouTube videos.

```python
from brahmastra.prebuild_tool import YoutubeTranscriptTool
from brahmastra.llm_agent import Create_ReAct_Agent
from brahmastra.llm_provider import GoogleLLM

# Create tool
transcript = YoutubeTranscriptTool(language="en", include_timestamps=True)

# Create agent and add tools
llm = GoogleLLM(model="gemini-2.0-flash")
agent = Create_ReAct_Agent(llm=llm)
agent.add_tools(transcript)  # Adds 2 tools: transcript, languages

# Use
result = agent.invoke("Get the transcript of https://youtube.com/watch?v=dQw4w9WgXcQ")
```

**Provides 2 tools:**
- `youtube_transcript` - Retrieve video transcript with optional timestamps
- `youtube_transcript_languages` - List available transcript languages

**Features:**
- 📝 100+ language support
- ⏱️ Optional timestamps
- 🔄 Auto-generated and manual captions
- 🌐 Translation capabilities
- 📊 Flexible URL/ID input

[📖 Full Documentation →](YoutubeTranscriptTool/README.md)

---

## 📥 Installation

### All Dependencies

```bash
# Core Wikipedia
pip install wikipedia

# YouTube Search (API mode)
pip install google-api-python-client

# YouTube Transcripts
pip install youtube-transcript-api

# Optional: yt-dlp for API fallback
pip install yt-dlp
```

### Individual Tools

```bash
# Wikipedia only
pip install wikipedia

# YouTube Search only
pip install google-api-python-client

# YouTube Transcript only
pip install youtube-transcript-api
```

### API Keys Required

| Tool | API Key | How to Get |
|------|---------|------------|
| YoutubeSearchTool | `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) |

---

## 🔧 Usage Patterns

### Pattern 1: Direct Integration (Recommended)

```python
from brahmastra.prebuild_tool import WikipediaSearchTool

wiki = WikipediaSearchTool()
agent.add_tools(wiki)  # Automatically adds all tool capabilities
```

### Pattern 2: Selective Tools

```python
from brahmastra.prebuild_tool import WikipediaSearchTool

wiki = WikipediaSearchTool()
agent.add_tools(
    wiki.get_search_tool(),   # Only add search
    wiki.get_content_tool()   # Only add content retrieval
)
```

### Pattern 3: Direct Usage (Without Agent)

```python
from brahmastra.prebuild_tool import WikipediaSearchTool

wiki = WikipediaSearchTool()
result = wiki.search("Python programming")
print(result)
```

### Pattern 4: Multiple Tools Together

```python
from brahmastra.prebuild_tool import (
    WikipediaSearchTool,
    YoutubeSearchTool,
    YoutubeTranscriptTool
)

# Create all tools
wiki = WikipediaSearchTool()
youtube = YoutubeSearchTool()
transcript = YoutubeTranscriptTool()

# Add all to agent
agent.add_tools(wiki, youtube, transcript)

# Now agent has 8 tools available!
```

### Pattern 5: With Different Agents

```python
from brahmastra.prebuild_tool import WikipediaSearchTool
from brahmastra.llm_agent import (
    Create_ReAct_Agent,
    Create_MultiReasoningToolAgent,
    Create_ToolCallingAgent
)

wiki = WikipediaSearchTool()

# Works with any agent type
react_agent = Create_ReAct_Agent(llm=llm)
react_agent.add_tools(wiki)

multi_agent = Create_MultiReasoningToolAgent(llm=llm, max_workers=5)
multi_agent.add_tools(wiki)

tool_agent = Create_ToolCallingAgent(llm=llm)
tool_agent.add_tools(wiki)
```

---

## 📚 Tool Reference

### WikipediaSearchTool

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | str | `"en"` | Wikipedia language code |
| `max_search_results` | int | `3` | Max search results |
| `search_chars_max` | int | `4000` | Max chars for summaries |
| `content_chars_max` | int | `10000` | Max chars for full content |
| `smart_disambiguation` | bool | `True` | Auto-resolve ambiguous pages |

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `search(query)` | str | Search Wikipedia |
| `get_content(title)` | str | Get full article |
| `suggest(query)` | str | Get suggestions |
| `get_search_tool()` | Tool | Get search tool |
| `get_content_tool()` | Tool | Get content tool |
| `get_suggest_tool()` | Tool | Get suggest tool |

---

### YoutubeSearchTool

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | env var | YouTube API key |
| `max_results` | int | `5` | Default max results |

**Search Filters:**
| Filter | Values | Description |
|--------|--------|-------------|
| `order` | relevance, date, rating, viewCount, title | Sort order |
| `video_duration` | short (<4min), medium (4-20min), long (>20min) | Duration filter |
| `video_definition` | high, standard | Quality filter |
| `published_after` | ISO 8601 date | Date range start |
| `published_before` | ISO 8601 date | Date range end |
| `safe_search` | none, moderate, strict | Content filter |

---

### YoutubeTranscriptTool

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | str | `"en"` | Preferred language |
| `include_timestamps` | bool | `True` | Include timestamps |
| `max_chars` | int | `50000` | Max characters |

**Supported Input Formats:**
- Full URL: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URL: `https://youtu.be/VIDEO_ID`
- Embed URL: `https://www.youtube.com/embed/VIDEO_ID`
- Video ID: `VIDEO_ID` (11 characters)

---

## 🔜 Coming Soon

### 🔍 Search Tools
- `google_search_tool` - Web search with Google
- `duckduckgo_tool` - Privacy-focused search
- `bing_search_tool` - Bing search integration

### 📰 News & Content
- `news_api_tool` - Latest news articles
- `rss_feed_tool` - RSS feed parser
- `web_scraper_tool` - Web content extraction

### 💾 Data & Storage
- `file_tool` - File operations
- `database_tool` - SQL database queries
- `csv_tool` - CSV processing
- `json_tool` - JSON processing

### 🌐 Web Services
- `weather_tool` - Weather information
- `email_tool` - Email sending
- `translate_tool` - Language translation

---

## 🤝 Contributing

### Adding a New Tool

1. **Create a folder**: `brahmastra/prebuild_tool/your_tool_name/`

2. **Implement base.py**:
```python
from typing import Iterator
from brahmastra.core import Tool

class YourToolName:
    def __init__(self, **config):
        self.config = config
    
    def __iter__(self) -> Iterator[Tool]:
        """Makes tool iterable for agent.add_tools()"""
        yield self.get_tool_1()
        yield self.get_tool_2()
    
    def get_tool_1(self) -> Tool:
        def tool_function(param: str) -> str:
            # Implementation
            return "result"
        
        return Tool(
            name="tool_name",
            description="What this tool does",
            function=tool_function,
            parameters={
                "param": {
                    "type": "string",
                    "description": "Parameter description"
                }
            }
        )
```

3. **Create __init__.py**:
```python
from .base import YourToolName
__all__ = ["YourToolName"]
```

4. **Create README.md** with documentation

5. **Update main __init__.py** to export your tool

---

## 📐 Design Principles

| Principle | Description |
|-----------|-------------|
| **Easy to Use** | Simple `agent.add_tools(tool)` integration |
| **Consistent API** | All tools follow the same patterns |
| **Iterable** | Tools implement `__iter__` for automatic unpacking |
| **Well Documented** | Comprehensive documentation and examples |
| **Robust** | Error handling, retry logic, graceful degradation |
| **Flexible** | Works with or without agents |
| **Modular** | Each tool is independent |

---

## 📄 License

Part of the **Brahmastra Framework** - MIT License

---

**Author:** devxJitin  
**Version:** 1.0.0
