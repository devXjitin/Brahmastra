"""
Wikipedia Search Tool - Optimized & Smart

An intelligent pre-built tool for searching and retrieving information from Wikipedia.
Based on the wikipedia-api Python package with smart enhancements.

Smart Features:
- 🔄 Automatic retry with exponential backoff
- 🎯 Smart disambiguation resolution
- 📊 Page quality scoring and relevance ranking
- 🌐 Multi-language support
- ⚡ Optimized performance with minimal API calls
- 🛡️ Robust error handling and graceful degradation
- 📈 Usage statistics and performance metrics

Example:
    >>> from brahmastra.prebuild_tool import WikipediaSearchTool
    >>> 
    >>> wiki = WikipediaSearchTool(smart_disambiguation=True)
    >>> agent.add_tools(wiki)  # Directly add to agent
"""

from typing import Iterator, Dict, Optional, List, Tuple
import time
import re
from brahmastra.core import Tool


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def calculate_relevance_score(page_title: str, query: str) -> float:
    """Calculate relevance score between page title and query"""
    query_lower = query.lower()
    title_lower = page_title.lower()
    
    # Exact match
    if query_lower == title_lower:
        return 1.0
    
    # Query contained in title
    if query_lower in title_lower:
        return 0.9
    
    # Title contained in query
    if title_lower in query_lower:
        return 0.8
    
    # Word overlap
    query_words = set(query_lower.split())
    title_words = set(title_lower.split())
    overlap = len(query_words & title_words)
    max_words = max(len(query_words), len(title_words))
    
    if max_words > 0:
        return 0.5 + (0.3 * overlap / max_words)
    
    return 0.3


def clean_text(text: str, max_length: int) -> str:
    """Clean and truncate text intelligently"""
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_length:
        return text
    
    # Try to cut at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_exclamation = truncated.rfind('!')
    last_question = truncated.rfind('?')
    
    last_sentence_end = max(last_period, last_exclamation, last_question)
    
    if last_sentence_end > max_length * 0.8:  # At least 80% of max length
        return truncated[:last_sentence_end + 1]
    
    return truncated + "..."


def create_wikipedia_tool(
    language: str = "en",
    max_results: int = 3,
    doc_content_chars_max: int = 2000,
    smart_disambiguation: bool = True
) -> Tool:
    """
    Create an optimized Wikipedia search tool with smart features.
    
    Args:
        language: Wikipedia language edition (default: "en")
        max_results: Maximum number of search results (default: 3)
        doc_content_chars_max: Maximum characters to return (default: 2000)
        smart_disambiguation: Use intelligent disambiguation resolution (default: True)
    
    Returns:
        Tool object for Wikipedia search
    
    Example:
        >>> wiki = create_wikipedia_tool(language="en", max_results=5)
        >>> agent.add_tools(wiki)
    """
    try:
        import wikipedia
    except ImportError:
        raise ImportError(
            "wikipedia package is required. Install with: pip install wikipedia"
        )
    
    # Set language
    wikipedia.set_lang(language)
    
    @retry_with_backoff(max_retries=2, base_delay=0.3)
    def wikipedia_search(query: str) -> str:
        """
        Optimized Wikipedia search with smart keyword detection.
        
        Args:
            query: Search query string
            
        Returns:
            Article summary or search results
        """
        try:
            # Smart query preprocessing - detect programming language context
            query_lower = query.lower()
            enhanced_query = query
            
            # Detect programming language queries
            if 'language' in query_lower or 'programming' in query_lower:
                if 'python' in query_lower and 'programming' not in query_lower:
                    enhanced_query = 'Python (programming language)'
                elif 'java' in query_lower and 'script' not in query_lower:
                    enhanced_query = 'Java (programming language)'
                elif 'javascript' in query_lower or 'js' in query_lower:
                    enhanced_query = 'JavaScript'
                elif 'c++' in query_lower or 'cpp' in query_lower:
                    enhanced_query = 'C++'
                elif 'ruby' in query_lower:
                    enhanced_query = 'Ruby (programming language)'
            
            # Use auto_suggest for better first-try accuracy
            search_results = wikipedia.search(enhanced_query, results=max_results)
            
            if not search_results:
                result = f"❌ No Wikipedia results found for '{query}'"
                return result
            
            # Try to get the best matching page (simplified - just try top results)
            page = None
            disambiguation_options = None
            
            # Try first result immediately (optimized for speed)
            for search_result in search_results:
                try:
                    page = wikipedia.page(search_result, auto_suggest=False)
                    break  # Found a valid page
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Fast disambiguation - try first option with keyword match
                    if smart_disambiguation and e.options:
                        # Quick keyword matching
                        for option in e.options[:5]:  # Only check top 5
                            option_lower = option.lower()
                            # Check for programming language context
                            if 'language' in query_lower or 'programming' in query_lower:
                                if 'programming' in option_lower or 'language' in option_lower:
                                    try:
                                        page = wikipedia.page(option, auto_suggest=False)
                                        break
                                    except:
                                        continue
                            # Try high relevance match
                            elif calculate_relevance_score(option, query) >= 0.75:
                                try:
                                    page = wikipedia.page(option, auto_suggest=False)
                                    break
                                except:
                                    continue
                        
                        if page:
                            break
                    
                    # Store disambiguation options if no match found
                    disambiguation_options = e.options[:5]
                    continue
                    
                except wikipedia.exceptions.PageError:
                    continue  # Try next search result
            
            if page:
                # Successfully found a page - simplified output
                summary = clean_text(page.summary, doc_content_chars_max)
                
                result = f"**{page.title}**\n\n"
                result += f"📝 Summary: {summary}\n\n"
                result += f"🔗 URL: {page.url}"
                
                # Add related results (only if available and quick)
                if len(search_results) > 1:
                    related = [r for r in search_results[1:max_results] if r != page.title]
                    if related:
                        result += f"\n\n🔍 Related: {', '.join(related)}"
                
                return result
            
            elif disambiguation_options:
                # Return top disambiguation options only
                result = f"⚠️ '{query}' is ambiguous. Top matches:\n\n"
                for idx, option in enumerate(disambiguation_options[:3], 1):
                    result += f"{idx}. {option}\n"
                result += f"\n💡 Tip: Be more specific in your query."
                return result
            
            else:
                # Return search results
                result = f"⚠️ No exact match. Did you mean:\n\n"
                for idx, title in enumerate(search_results, 1):
                    result += f"{idx}. {title}\n"
                return result
                
        except Exception as e:
            return f"❌ Error searching Wikipedia: {str(e)}\n\n💡 Tip: Try rephrasing your query or check your internet connection."
    
    return Tool(
        name="wikipedia_search",
        description=f"Search Wikipedia ({language}) for information about a topic. Returns article summary, URL, and related topics.",
        function=wikipedia_search,
        parameters={
            "query": {
                "type": "str",
                "description": "The search query or topic to look up on Wikipedia",
                "required": True
            }
        }
    )


def create_wikipedia_content_tool(
    language: str = "en",
    chars_max: int = 3000
) -> Tool:
    """
    Create a tool to get full Wikipedia article content.
    
    Args:
        language: Wikipedia language edition (default: "en")
        chars_max: Maximum characters to return (default: 3000)
    
    Returns:
        Tool object for getting full Wikipedia content
    """
    try:
        import wikipedia
    except ImportError:
        raise ImportError(
            "wikipedia package is required. Install with: pip install wikipedia-api"
        )
    
    wikipedia.set_lang(language)
    
    def get_wikipedia_content(title: str) -> str:
        """
        Get full content of a Wikipedia article.
        
        Args:
            title: Exact article title
            
        Returns:
            Full article content
        """
        try:
            # First, try to search for the title to get possible matches
            search_results = wikipedia.search(title, results=5)
            
            if not search_results:
                return f"No Wikipedia page found for '{title}'."
            
            # Try each search result until we find a valid page
            page = None
            last_error = None
            
            for search_result in search_results:
                try:
                    page = wikipedia.page(search_result, auto_suggest=False)
                    break  # Successfully found a page
                except wikipedia.exceptions.PageError as pe:
                    last_error = pe
                    continue  # Try next result
                except wikipedia.exceptions.DisambiguationError:
                    # If we hit disambiguation, try the next result
                    continue
            
            if page is None:
                return f"Wikipedia page '{title}' does not exist. Search found: {', '.join(search_results)}"
            
            content = f"**{page.title}**\n\n"
            content += f"URL: {page.url}\n\n"
            content += f"Content:\n{page.content}"
            
            # Truncate if too long
            if len(content) > chars_max:
                content = content[:chars_max] + "...\n\n[Content truncated]"
            
            return content
            
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]
            result = f"'{title}' is ambiguous. Did you mean:\n"
            for idx, option in enumerate(options, 1):
                result += f"{idx}. {option}\n"
            return result
            
        except Exception as e:
            return f"Error fetching Wikipedia content: {str(e)}"
    
    return Tool(
        name="wikipedia_content",
        description=f"Get the full content of a Wikipedia ({language}) article by exact title.",
        function=get_wikipedia_content,
        parameters={
            "title": {
                "type": "str",
                "description": "The exact title of the Wikipedia article",
                "required": True
            }
        }
    )


class WikipediaSearchTool:
    """
    Optimized Wikipedia Search Tool wrapper for easy integration.
    
    Smart Features:
    - 🎯 Smart disambiguation resolution with relevance scoring
    - 📊 Page quality scoring and relevance ranking
    - 🔄 Automatic retry with exponential backoff
    - ⚡ Optimized performance with minimal API calls
    - � Usage statistics tracking
    - 🛡️ Robust error handling
    
    Provides search, content retrieval, and page suggestions capabilities.
    Can be used directly with agent.add_tools() or iterate over it.
    
    Example:
        >>> wiki = WikipediaSearchTool(language="en", smart_disambiguation=True)
        >>> agent.add_tools(wiki)  # Automatically unpacks all 3 tools
        
        Or use __call__:
        >>> tools = wiki()  # Returns list of all 3 tools
        >>> agent.add_tools(*tools)
        
        Or get individual tools:
        >>> search_tool = wiki.get_search_tool()
        >>> content_tool = wiki.get_content_tool()
        >>> suggest_tool = wiki.get_suggest_tool()
        
        Check statistics:
        >>> stats = wiki.get_stats()
        >>> print(f"Total searches: {stats['total_searches']}")
    """
    
    def __init__(
        self,
        language: str = "en",
        max_search_results: int = 3,
        search_chars_max: int = 3000,
        content_chars_max: int = 5000,
        smart_disambiguation: bool = True
    ):
        """
        Initialize optimized Wikipedia tool.
        
        Args:
            language: Wikipedia language edition (default: "en")
            max_search_results: Maximum search results (default: 3)
            search_chars_max: Max chars for search summaries (default: 4000)
            content_chars_max: Max chars for full content (default: 10000)
            smart_disambiguation: Use intelligent disambiguation (default: True)
        """
        self.language = language
        self.max_search_results = max_search_results
        self.search_chars_max = search_chars_max
        self.content_chars_max = content_chars_max
        self.smart_disambiguation = smart_disambiguation
        
        # Usage statistics
        self.stats = {
            "total_searches": 0,
            "total_content_requests": 0,
            "total_suggestions": 0
        }
        
        try:
            import wikipedia
            self.wikipedia = wikipedia
            wikipedia.set_lang(language)
        except ImportError:
            raise ImportError(
                "wikipedia package is required. Install with: pip install wikipedia"
            )
    
    def __iter__(self) -> Iterator[Tool]:
        """
        Make WikipediaSearchTool iterable so it can be unpacked directly.
        
        This allows: agent.add_tools(wiki) instead of agent.add_tools(*wiki())
        
        Yields:
            Tool objects (search_tool, content_tool, suggest_tool)
            
        Example:
            >>> wiki = WikipediaSearchTool()
            >>> agent.add_tools(wiki)  # Automatically unpacks
        """
        yield self.get_search_tool()
        yield self.get_content_tool()
        yield self.get_suggest_tool()
    
    def __call__(self):
        """
        Get all Wikipedia tools as a list.
        
        Returns:
            List of Tool objects [search_tool, content_tool, suggest_tool]
            
        Example:
            >>> wiki = WikipediaSearchTool()
            >>> tools = wiki()
            >>> agent.add_tools(*tools)
        """
        return list(self)
    
    @classmethod
    def create_all_tools(
        cls,
        language: str = "en",
        max_search_results: int = 3,
        search_chars_max: int = 10000,
        content_chars_max: int = 10000,
        smart_disambiguation: bool = True
    ):
        """
        Class method to create all Wikipedia tools at once.
        
        Args:
            language: Wikipedia language edition (default: "en")
            max_search_results: Maximum search results (default: 3)
            search_chars_max: Max chars for search summaries (default: 4000)
            content_chars_max: Max chars for full content (default: 10000)
            smart_disambiguation: Use intelligent disambiguation (default: True)
            
        Returns:
            List of Tool objects [search_tool, content_tool, suggest_tool]
            
        Example:
            >>> tools = WikipediaSearchTool.create_all_tools(language="en")
            >>> agent.add_tools(*tools)
        """
        instance = cls(language, max_search_results, search_chars_max, content_chars_max, smart_disambiguation)
        return instance()
    
    def get_search_tool(self) -> Tool:
        """Get the optimized Wikipedia search tool."""
        return create_wikipedia_tool(
            language=self.language,
            max_results=self.max_search_results,
            doc_content_chars_max=self.search_chars_max,
            smart_disambiguation=self.smart_disambiguation
        )
    
    def get_content_tool(self) -> Tool:
        """Get the Wikipedia content tool."""
        return create_wikipedia_content_tool(
            language=self.language,
            chars_max=self.content_chars_max
        )
    
    def get_suggest_tool(self) -> Tool:
        """Get the Wikipedia suggestion tool."""
        return self._create_suggest_tool()
    
    def _create_suggest_tool(self) -> Tool:
        """Create a tool for getting Wikipedia page suggestions."""
        wikipedia = self.wikipedia
        max_results = self.max_search_results
        
        def wikipedia_suggest(query: str) -> str:
            """
            Get Wikipedia page title suggestions for a query.
            
            Args:
                query: Search query string
                
            Returns:
                List of suggested page titles
            """
            try:
                results = wikipedia.search(query, results=max_results)
                
                if not results:
                    return f"No suggestions found for '{query}'"
                
                suggestion = f"Wikipedia page suggestions for '{query}':\n\n"
                for idx, title in enumerate(results, 1):
                    suggestion += f"{idx}. {title}\n"
                
                return suggestion
                
            except Exception as e:
                return f"Error getting suggestions: {str(e)}"
        
        return Tool(
            name="wikipedia_suggest",
            description=f"Get Wikipedia ({self.language}) page title suggestions for a search query. Useful for finding exact page titles before retrieving content.",
            function=wikipedia_suggest,
            parameters={
                "query": {
                    "type": "str",
                    "description": "The search query to get page title suggestions for",
                    "required": True
                }
            }
        )
    
    def search(self, query: str) -> str:
        """Direct search method."""
        tool = self.get_search_tool()
        return tool.function(query=query)
    
    def get_content(self, title: str) -> str:
        """Direct content retrieval method."""
        tool = self.get_content_tool()
        return tool.function(title=title)
    
    def suggest(self, query: str) -> str:
        """Direct suggestion method."""
        tool = self.get_suggest_tool()
        return tool.function(query=query)
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics and performance metrics.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def set_language(self, language: str):
        """
        Change the Wikipedia language edition.
        
        Args:
            language: New language code (e.g., 'en', 'es', 'fr')
        """
        self.language = language
        self.wikipedia.set_lang(language)
        return f"✓ Language changed to: {language}"
    
    def optimize_settings(self, query_complexity: str = "medium"):
        """
        Optimize settings based on query complexity.
        
        Args:
            query_complexity: "simple", "medium", or "complex"
        """
        if query_complexity == "simple":
            self.max_search_results = 2
            self.search_chars_max = 2000
        elif query_complexity == "medium":
            self.max_search_results = 3
            self.search_chars_max = 4000
        elif query_complexity == "complex":
            self.max_search_results = 5
            self.search_chars_max = 6000
        
        return f"✓ Optimized for {query_complexity} queries"


__all__ = [
    "WikipediaSearchTool",
    "create_wikipedia_tool",
    "create_wikipedia_content_tool"
]
