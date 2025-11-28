# YouTube Transcript Tool

A comprehensive YouTube transcript retrieval tool for Brahmastra AI agents, providing access to video transcripts and captions from YouTube videos.

## Features

✅ **Two Tools in One**: Transcript retrieval and language listing  
✅ **Easy Integration**: Iterable design - use `agent.add_tools(transcript)` directly  
✅ **Multi-Language Support**: Access transcripts in 100+ languages  
✅ **Auto & Manual Captions**: Supports both auto-generated and human-created transcripts  
✅ **Translation**: Translate transcripts to any language  
✅ **Timestamp Support**: Optional timestamps for each transcript segment  
✅ **Flexible Input**: Accepts YouTube URLs or video IDs  
✅ **Error Handling**: Graceful handling of missing transcripts and errors  
✅ **Character Limits**: Configurable content length to manage context  

## Installation

```bash
pip install youtube-transcript-api
```

## Quick Start

```python
from brahmastra.prebuild_tool.YoutubeTranscriptTool import YoutubeTranscriptTool
from brahmastra.llm_agent.REACT_AGENT import Create_ReAct_Agent
from brahmastra.llm_provider import OpenAI_llm

# Create YouTube Transcript tool
transcript = YoutubeTranscriptTool(language="en", include_timestamps=True)

# Create agent
llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_ReAct_Agent(llm=llm, verbose=True)

# Add both transcript tools directly (simplest way!)
agent.add_tools(transcript)  # Automatically unpacks both tools

# Use the agent
result = agent.invoke("Get the transcript from https://youtube.com/watch?v=dQw4w9WgXcQ")
print(result["final_answer"])
```

## Usage

### Using Both Tools

```python
# Method 1: Direct add (Simplest - Recommended!)
transcript = YoutubeTranscriptTool(language="en")
agent.add_tools(transcript)  # Automatically unpacks both tools

# Method 2: Using __call__
transcript = YoutubeTranscriptTool(language="en")
tools = transcript()  # Returns list of both tools
agent.add_tools(*tools)

# Method 3: Using class method
tools = YoutubeTranscriptTool.create_all_tools(language="en", include_timestamps=True)
agent.add_tools(*tools)

# Method 4: Individual tools
transcript = YoutubeTranscriptTool(language="en")
transcript_tool = transcript.get_transcript_tool()
languages_tool = transcript.get_languages_tool()
agent.add_tools(transcript_tool, languages_tool)
```

### The Two Tools

When you add YoutubeTranscriptTool to an agent, it provides two distinct tools:

1. **`youtube_transcript`**: Retrieve video transcript/captions
   - Parameters: 
     - `video_url_or_id` (str): YouTube URL or video ID
     - `languages` (str, optional): Comma-separated language codes
     - `translate_to` (str, optional): Language to translate to
   - Returns: Formatted transcript with timestamps
   
2. **`youtube_transcript_languages`**: List available transcript languages
   - Parameters: `video_url_or_id` (str)
   - Returns: List of all available manual and auto-generated transcripts

```python
# Example: Agent uses both tools
result = agent.invoke("""
First, check what transcript languages are available for video dQw4w9WgXcQ.
Then, get the English transcript with timestamps.
""")
```

### Direct Usage (Without Agent)

```python
from brahmastra.prebuild_tool.YoutubeTranscriptTool import YoutubeTranscriptTool

# Create tool instance
transcript = YoutubeTranscriptTool(language="en", include_timestamps=True)

# Get transcript directly
result = transcript.get_transcript("dQw4w9WgXcQ")
print(result)

# List available languages
languages = transcript.list_languages("https://youtube.com/watch?v=dQw4w9WgXcQ")
print(languages)

# Get stats
stats = transcript.get_stats()
print(f"Transcripts retrieved: {stats['transcript_requests']}")
```

## Configuration Options

### Language Settings

```python
# Default English
transcript = YoutubeTranscriptTool(language="en")

# Spanish transcripts
transcript = YoutubeTranscriptTool(language="es")

# Change language after creation
transcript.set_language("fr")
```

### Timestamp Control

```python
# With timestamps (default)
transcript = YoutubeTranscriptTool(include_timestamps=True)

# Without timestamps (plain text)
transcript = YoutubeTranscriptTool(include_timestamps=False)
```

### Character Limits

```python
# Default 50,000 characters
transcript = YoutubeTranscriptTool(max_chars=50000)

# Shorter for quick summaries
transcript = YoutubeTranscriptTool(max_chars=10000)

# Longer for detailed analysis
transcript = YoutubeTranscriptTool(max_chars=100000)
```

## Advanced Features

### Multi-Language Retrieval

```python
# Agent will try English first, then Spanish, then French
result = agent.invoke("""
Get the transcript for video dQw4w9WgXcQ in languages: en,es,fr
""")
```

### Translation

```python
# Get Japanese transcript and translate to English
result = agent.invoke("""
Get the transcript for video dQw4w9WgXcQ and translate it to English
""")
```

### Flexible Video ID Input

The tool accepts multiple input formats:
- Full URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URL: `https://youtu.be/dQw4w9WgXcQ`
- Embed URL: `https://www.youtube.com/embed/dQw4w9WgXcQ`
- Video ID only: `dQw4w9WgXcQ`

## Tool Parameters

### youtube_transcript

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| video_url_or_id | str | Yes | YouTube video URL or 11-character video ID |
| languages | str | No | Comma-separated language codes (e.g., "en,es,fr") |
| translate_to | str | No | Language code to translate transcript to |

### youtube_transcript_languages

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| video_url_or_id | str | Yes | YouTube video URL or 11-character video ID |

## Example Use Cases

### 1. Content Analysis

```python
agent.invoke("""
Get the transcript from this Python tutorial video: 
https://youtube.com/watch?v=example123
Then summarize the main topics covered.
""")
```

### 2. Multi-Language Learning

```python
agent.invoke("""
Check what languages are available for video example123.
If Spanish is available, get the Spanish transcript.
""")
```

### 3. Accessibility

```python
agent.invoke("""
Get the English transcript for video example123 without timestamps.
Format it as readable paragraphs for accessibility.
""")
```

### 4. Translation Pipeline

```python
agent.invoke("""
Get the Japanese transcript for video example123.
Then translate it to English for analysis.
""")
```

## Output Format

### Transcript Output

```
🎥 **YouTube Video Transcript**

📹 Video ID: dQw4w9WgXcQ
🔗 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
🌐 Language: en
📝 Segments: 156

──────────────────────────────────────────────────

[00:00] We're no strangers to love
[00:03] You know the rules and so do I
[00:07] A full commitment's what I'm thinking of
...
```

### Languages Output

```
🎥 **Available Transcripts for Video**

📹 Video ID: dQw4w9WgXcQ
🔗 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

📝 **Manual Transcripts** (Human-created):
   • en - English (Translatable: ✓)
   • es - Spanish (Translatable: ✓)

🤖 **Auto-Generated Transcripts**:
   • fr - French (Translatable: ✓)
   • de - German (Translatable: ✓)
   • ja - Japanese (Translatable: ✓)

💡 **Tip**: Use the youtube_transcript tool with the 'languages' parameter to retrieve a transcript in your preferred language.
💡 **Translation**: Translatable transcripts can be translated to any language using the 'translate_to' parameter.
```

## Error Handling

The tool provides informative error messages:

```python
# Transcripts disabled
"❌ Transcripts are disabled for video 'abc123'"

# Video not found
"❌ Video 'abc123' is unavailable or does not exist"

# Language not available
"❌ No transcript found for video 'abc123' in languages: en, fr
📝 Available manual transcripts: es, de
🤖 Available auto-generated: ja, ko
💡 Tip: Use youtube_transcript_languages tool to see all available languages"
```

## Language Codes

Common language codes:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `ja` - Japanese
- `zh` - Chinese
- `ko` - Korean
- `pt` - Portuguese
- `ru` - Russian
- `ar` - Arabic
- `hi` - Hindi
- `it` - Italian

See [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for complete list.

## Statistics

Track usage with the `get_stats()` method:

```python
transcript = YoutubeTranscriptTool()
agent.add_tools(transcript)

# ... use the tools ...

stats = transcript.get_stats()
print(f"Transcript requests: {stats['transcript_requests']}")
print(f"Language queries: {stats['language_queries']}")
```

## Limitations

- **YouTube API Restrictions**: Some videos may have transcripts disabled by the uploader
- **Language Availability**: Not all videos have transcripts in all languages
- **Auto-Generated Quality**: Auto-generated transcripts may contain errors
- **Character Limits**: Long videos may produce very large transcripts (use `max_chars` parameter)
- **Rate Limiting**: Excessive requests may be throttled by YouTube

## Troubleshooting

### "No transcript found"
- Check if the video has captions enabled
- Use `youtube_transcript_languages` tool to see available languages
- Try without specifying a language to get any available transcript

### "Import error"
- Install the package: `pip install youtube-transcript-api`

### "Video unavailable"
- Verify the video ID/URL is correct
- Check if the video is private or deleted
- Try accessing the video directly on YouTube

## Integration with Other Tools

Combine with other Brahmastra tools for powerful workflows:

```python
from brahmastra.prebuild_tool import (
    YoutubeSearchTool,
    YoutubeTranscriptTool,
    WikipediaSearchTool
)

# Search for videos, get transcripts, and cross-reference with Wikipedia
youtube_search = YoutubeSearchTool(api_key="your-key")
youtube_transcript = YoutubeTranscriptTool()
wiki = WikipediaSearchTool()

agent.add_tools(youtube_search, youtube_transcript, wiki)

result = agent.invoke("""
1. Search YouTube for 'Python programming tutorial'
2. Get the transcript of the top result
3. Look up any technical terms mentioned in the transcript on Wikipedia
""")
```

## API Reference

### YoutubeTranscriptTool Class

```python
class YoutubeTranscriptTool:
    def __init__(
        self,
        language: str = "en",
        include_timestamps: bool = True,
        max_chars: int = 50000
    )
    
    def __iter__(self) -> Iterator[Tool]
    def __call__(self) -> List[Tool]
    
    @classmethod
    def create_all_tools(cls, ...) -> List[Tool]
    
    def get_transcript_tool(self) -> Tool
    def get_languages_tool(self) -> Tool
    
    def get_transcript(self, video_url_or_id: str, ...) -> str
    def list_languages(self, video_url_or_id: str) -> str
    
    def get_stats(self) -> Dict
    def set_language(self, language: str) -> str
    
    @property
    def transcript_tool(self) -> Tool
    
    @property
    def languages_tool(self) -> Tool
```

### Function API

```python
# Create individual tools
def create_youtube_transcript_tool(
    language: str = "en",
    include_timestamps: bool = True,
    max_chars: int = 50000
) -> Tool

def create_youtube_transcript_languages_tool() -> Tool
```

## Contributing

Found a bug or have a feature request? Please open an issue on the Brahmastra repository.

## License

This tool is part of the Brahmastra framework and follows the same license.

## Credits

Built with [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) by jdepoix.
