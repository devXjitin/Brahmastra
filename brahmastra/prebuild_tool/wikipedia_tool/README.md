# Wikipedia Tool

A comprehensive Wikipedia integration tool for Brahmastra AI agents, providing search, content retrieval, and page suggestions from Wikipedia.

## Features

✅ **Three Tools in One**: Search, full content, and page suggestions  
✅ **Easy Integration**: Iterable design - use `agent.add_tools(wiki)` directly  
✅ **Smart Search**: Intelligently finds relevant Wikipedia articles  
✅ **Robust Page Retrieval**: Handles title variations and case-sensitivity issues  
✅ **Disambiguation Handling**: Provides options when query is ambiguous  
✅ **Summary & Full Content**: Get quick summaries or detailed articles  
✅ **URL Inclusion**: Returns article URLs for reference  
✅ **Related Topics**: Suggests related Wikipedia pages  
✅ **Multi-Language**: Supports all Wikipedia language editions (200+ languages)  
✅ **Error Handling**: Graceful handling of missing pages and errors  
✅ **Character Limits**: Configurable content length to manage context  

## Installation

```bash
pip install wikipedia
```

## Quick Start

```python
from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool
from brahmastra.llm_agent.REACT_AGENT import Create_ReAct_Agent
from brahmastra.llm_provider import OpenAI_llm

# Create Wikipedia tool
wiki = WikipediaSearchTool(language="en", max_search_results=5)

# Create agent
llm = OpenAI_llm(model="gpt-4", api_key="your-key")
agent = Create_ReAct_Agent(llm=llm, verbose=True)

# Add all 3 Wikipedia tools directly (simplest way!)
agent.add_tools(wiki)  # Automatically unpacks all 3 tools

# Use the agent
result = agent.invoke("What is Python programming language?")
print(result["final_answer"])
```

## Usage

### Using All Three Tools

```python
# Method 1: Direct add (Simplest - Recommended!)
wiki = WikipediaSearchTool(language="en")
agent.add_tools(wiki)  # Automatically unpacks all 3 tools

# Method 2: Using __call__
wiki = WikipediaSearchTool(language="en")
tools = wiki()  # Returns list of all 3 tools
agent.add_tools(*tools)

# Method 3: Using class method
tools = WikipediaSearchTool.create_all_tools(language="en", max_search_results=5)
agent.add_tools(*tools)

# Method 4: Individual tools
wiki = WikipediaSearchTool(language="en")
search_tool = wiki.get_search_tool()
content_tool = wiki.get_content_tool()
suggest_tool = wiki.get_suggest_tool()
agent.add_tools(search_tool, content_tool, suggest_tool)
```

### The Three Tools

When you add WikipediaSearchTool to an agent, it provides three distinct tools:

1. **`wikipedia_search`**: Search Wikipedia and get article summaries
   - Parameters: `query` (str)
   - Returns: Article summary, URL, and related topics
2. **`wikipedia_content`**: Get full content of a Wikipedia article
   - Parameters: `title` (str)
   - Returns: Complete article content (truncated to character limit)
3. **`wikipedia_suggest`**: Get page title suggestions for a query
   - Parameters: `query` (str)
   - Returns: List of suggested Wikipedia page titles

```python
# Example: Agent uses all three tools
result = agent.invoke("""
First, suggest pages for 'Machine Learning'.
Then search for the most relevant one.
Finally, get the full content of that article.
""")
```

### Direct Usage (Without Agent)

```python
from brahmastra.prebuild_tool import WikipediaSearchTool

wiki = WikipediaSearchTool()

# Direct search
result = wiki.search("Artificial Intelligence")
print(result)

# Get full content
content = wiki.get_content("Artificial Intelligence")
print(content)

# Get suggestions
suggestions = wiki.suggest("Python")
print(suggestions)
```

### Factory Functions

```python
from brahmastra.prebuild_tool.wikipedia_tool import (
    create_wikipedia_tool, 
    create_wikipedia_content_tool,
    create_wikipedia_suggest_tool
)

# Create search tool with custom settings
search_tool = create_wikipedia_tool(
    language="en",
    max_results=5,
    doc_content_chars_max=5000
)

# Create content tool
content_tool = create_wikipedia_content_tool(
    language="en",
    chars_max=15000
)

# Create suggest tool
suggest_tool = create_wikipedia_suggest_tool(
    language="en",
    max_results=10
)

# Add to agent
agent.add_tools(search_tool, content_tool, suggest_tool)
```

## Configuration

### Multi-Language Support

```python
# Search in different languages
wiki_en = WikipediaSearchTool(language="en")  # English
wiki_es = WikipediaSearchTool(language="es")  # Spanish
wiki_fr = WikipediaSearchTool(language="fr")  # French
wiki_de = WikipediaSearchTool(language="de")  # German
wiki_ja = WikipediaSearchTool(language="ja")  # Japanese

# Use with agent
result = wiki_es.search("Inteligencia Artificial")
```

### Parameters

**WikipediaSearchTool Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | str | `"en"` | Wikipedia language edition (e.g., "en", "es", "fr", "de", "ja") |
| `max_search_results` | int | `3` | Maximum number of search results to return |
| `search_chars_max` | int | `4000` | Max characters for search result summaries |
| `content_chars_max` | int | `10000` | Max characters for full article content |

### Methods

**WikipediaSearchTool Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `__iter__()` | Iterator[Tool] | Makes WikipediaSearchTool iterable - allows `agent.add_tools(wiki)` |
| `__call__()` | List[Tool] | Returns list of all 3 tools (search, content, suggest) |
| `get_search_tool()` | Tool | Returns Tool for searching Wikipedia |
| `get_content_tool()` | Tool | Returns Tool for getting full article content |
| `get_suggest_tool()` | Tool | Returns Tool for getting page suggestions |
| `search(query)` | str | Direct search without agent |
| `get_content(title)` | str | Direct content retrieval without agent |
| `suggest(query)` | str | Direct suggestions without agent |

**Class Method:**

- `create_all_tools(language, max_search_results, search_chars_max, content_chars_max)`: Create all tools using class method

## Advanced Features

### Robust Page Retrieval

The Wikipedia tool now includes intelligent page retrieval that handles common issues:

```python
# These all work correctly now, even with case variations:
wiki.search("Machine Learning")  # ✓ Works
wiki.search("machine learning")  # ✓ Works
wiki.search("MACHINE LEARNING")  # ✓ Works

# The tool tries multiple search results until finding a valid page
# This solves the Wikipedia API's strict title matching requirement
```

**How it works:**

1. Searches Wikipedia for the query
2. Gets multiple potential page titles
3. Tries each result sequentially with `auto_suggest=False`
4. Returns the first successfully retrieved page
5. Handles disambiguation and missing pages gracefully

### Use Cases

1. **Research Assistant**: Search for information and get detailed articles
2. **Fact Checking**: Verify information against Wikipedia
3. **Content Generation**: Get background information for content creation
4. **Education**: Learn about topics from reliable source
5. **Multi-Source Research**: Combine with other search tools

## Examples

### Example 1: Basic Search with ReAct Agent

```python
from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool
from brahmastra.llm_agent.REACT_AGENT import Create_ReAct_Agent
from brahmastra.llm_provider import Google_llm

wiki = WikipediaSearchTool(language="en")
llm = Google_llm(model="gemini-2.0-flash-exp")
agent = Create_ReAct_Agent(llm=llm, verbose=True)

agent.add_tools(wiki)

result = agent.invoke("What is Quantum Computing?")
print(result["final_answer"])
```

### Example 2: Parallel Searches with Multi Reasoning Tool Agent

```python
from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool
from brahmastra.llm_agent import Create_MultiReasoningToolAgent
from brahmastra.llm_provider import OpenAI_llm

wiki = WikipediaSearchTool(max_search_results=5)
llm = OpenAI_llm(model="gpt-4")
agent = Create_MultiReasoningToolAgent(llm=llm, max_workers=10, verbose=True)

agent.add_tools(wiki)

# Agent automatically executes searches in parallel
result = agent.invoke("""
Search Wikipedia for:
1. Artificial Intelligence
2. Machine Learning  
3. Deep Learning
4. Neural Networks
5. Natural Language Processing

Summarize the key differences between them.
""")
```

### Example 3: Sequential Deep Dive

```python
from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool
from brahmastra.llm_agent import Create_MultiReasoningToolAgent
from brahmastra.llm_provider import Google_llm

wiki = WikipediaSearchTool()
llm = Google_llm(model="gemini-2.0-flash-exp")
agent = Create_MultiReasoningToolAgent(llm=llm)

agent.add_tools(wiki)

result = agent.invoke("""
1. Get page suggestions for 'Transformer Architecture'
2. Search for the most relevant page
3. Get the full content of that page
4. Summarize the key concepts
""")
```

### Example 4: Multi-Language Research

```python
from brahmastra.prebuild_tool.wikipedia_tool import WikipediaSearchTool

# Create tools for different languages
wiki_en = WikipediaSearchTool(language="en")
wiki_es = WikipediaSearchTool(language="es")
wiki_fr = WikipediaSearchTool(language="fr")

# Search in English
en_result = wiki_en.search("Artificial Intelligence")

# Search in Spanish
es_result = wiki_es.search("Inteligencia Artificial")

# Search in French
fr_result = wiki_fr.search("Intelligence Artificielle")
```

## Error Handling

The tool handles common errors gracefully:

```python
wiki = WikipediaSearchTool()

# Page doesn't exist
result = wiki.search("asdfjkl123nonexistent")
# Returns: "No Wikipedia results found for 'asdfjkl123nonexistent'"

# Ambiguous query (disambiguation)
result = wiki.search("Python")
# Returns: List of disambiguation options:
# 'Python' is ambiguous. Did you mean:
# 1. Python (programming language)
# 2. Python (genus)
# 3. Burmese python
# ...

# Title case variations (now handled automatically!)
result = wiki.search("Machine Learning")  # ✓ Works
result = wiki.search("machine learning")  # ✓ Also works
result = wiki.search("MACHINE LEARNING")  # ✓ Still works

# Empty query
result = wiki.search("")
# Returns: Helpful error message
```

## Technical Details

### Architecture

```text
wikipedia_tool/
├── base.py           # Main implementation
├── __init__.py       # Exports
└── README.md         # This file
```

### Dependencies

- `wikipedia`: Python wrapper for Wikipedia API
- Required: `pip install wikipedia`

### Tool Schemas

**wikipedia_search Tool:**

```python
{
    "name": "wikipedia_search",
    "description": "Search Wikipedia and get article summaries",
    "parameters": {
        "query": {
            "type": "str",
            "description": "Search query for Wikipedia",
            "required": True
        }
    }
}
```

**wikipedia_content Tool:**

```python
{
    "name": "wikipedia_content",
    "description": "Get full content of a Wikipedia article",
    "parameters": {
        "title": {
            "type": "str",
            "description": "Exact title of the Wikipedia article",
            "required": True
        }
    }
}
```

**wikipedia_suggest Tool:**

```python
{
    "name": "wikipedia_suggest",
    "description": "Get Wikipedia page title suggestions",
    "parameters": {
        "query": {
            "type": "str",
            "description": "Query to get suggestions for",
            "required": True
        }
    }
}
```

## Troubleshooting

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'wikipedia'"

```bash
# Solution: Install the wikipedia package
pip install wikipedia
```

#### Issue: "PageError: Page does not exist"

- This is now automatically handled by trying multiple search results
- If it still occurs, the page genuinely doesn't exist on Wikipedia
- Try using `wikipedia_suggest` first to find the correct title

#### Issue: Disambiguation errors

- The tool automatically returns disambiguation options
- Use the exact title from the suggestions with `wikipedia_content`

#### Issue: Content too long

- Adjust `search_chars_max` or `content_chars_max` parameters
- Default limits prevent context overflow in LLM prompts

## Performance Tips

1. **Use Multi Reasoning Tool Agent for parallel searches**: When searching multiple topics, the Multi Reasoning Tool Agent executes them concurrently
2. **Adjust character limits**: Lower limits = faster responses and less token usage
3. **Use suggest before content**: Get the exact title first to avoid page errors
4. **Language-specific instances**: Create separate instances for different languages rather than changing language per call

## Changelog

### Version 1.1.0 (Current)

- ✨ **New**: Robust page retrieval with automatic fallback through search results
- ✨ **New**: Handles title case variations automatically
- 🐛 **Fixed**: "Machine Learning" and similar queries now work correctly
- 🐛 **Fixed**: Case-sensitivity issues with Wikipedia page titles
- 📝 **Improved**: Better error messages and handling

### Version 1.0.0

- Initial release with three tools: search, content, suggest
- Multi-language support
- Iterable design for easy agent integration

---

## License

Part of the Brahmastra package. See main package license for details.
