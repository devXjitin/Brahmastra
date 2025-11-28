"""
Anthropic Claude LLM Provider Module
=====================================

A production-ready wrapper around Anthropic's Claude API client with comprehensive
error handling, automatic retries with exponential backoff, and timeout management.

This module provides two interfaces for interacting with Claude models:
    1. Function-based API: `anthropic_llm()` for stateless one-off calls
    2. Class-based API: `AnthropicLLM` for stateful usage with agents

Key Features:
-------------
- Robust error handling with custom exception hierarchy
- Automatic retry mechanism with configurable exponential backoff
- Request timeout management
- Input validation for all parameters
- Support for all Claude 3 models (Opus, Sonnet, Haiku)
- Silent operation (no logging per design requirement)
- Stderr suppression for clean output

Supported Models:
-----------------
- Claude 3 Opus (claude-3-opus-20240229)
- Claude 3 Sonnet (claude-3-sonnet-20240229, claude-3-5-sonnet-20240620)
- Claude 3 Haiku (claude-3-haiku-20240307)
- Legacy Claude models (claude-2.1, claude-2.0, claude-instant-1.2)

Configuration:
--------------
API key can be provided via:
    - Direct parameter: api_key="your-key"
    - Environment variable: ANTHROPIC_API_KEY

Example Usage:
--------------
    Function-based:
        >>> from brahmastra.llm_provider import anthropic_llm, AnthropicLLMError
        >>> try:
        ...     response = anthropic_llm(
        ...         prompt="Explain Python in one sentence",
        ...         model="claude-3-opus-20240229",
        ...         api_key="your-api-key-here",
        ...         temperature=0.7,
        ...         max_tokens=1000
        ...     )
        ...     print(response)
        ... except AnthropicLLMError as e:
        ...     print(f"Error: {e}")
    
    Class-based:
        >>> from brahmastra.llm_provider import AnthropicLLM
        >>> llm = AnthropicLLM(model="claude-3-sonnet-20240229", api_key="your-key")
        >>> response = llm.generate_response("What is Python?")
        >>> print(response)

Author: devxJitin
Version: 1.0.0
"""

from typing import Optional, Any
import os
import time
import warnings
import sys
from contextlib import contextmanager

# ============================================================================
# Environment Configuration
# ============================================================================
# Suppress verbose logging from underlying libraries to maintain clean output
os.environ['GRPC_VERBOSITY'] = 'ERROR'          # Suppress gRPC verbose logs
os.environ['GLOG_minloglevel'] = '2'            # Suppress Google logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'        # Suppress TensorFlow logs

# Suppress Python warning categories
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

@contextmanager
def suppress_stderr():
    """Temporarily suppress stderr output using low-level file descriptor redirection."""
    import io
    
    # Save original stderr
    original_stderr = sys.stderr
    original_stderr_fd = None
    
    try:
        # Save the original file descriptor
        try:
            original_stderr_fd = os.dup(2)
        except:
            pass
        
        # Redirect stderr to devnull
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 2)
            os.close(devnull)
        except:
            pass
        
        # Also redirect Python's sys.stderr
        sys.stderr = io.StringIO()
        
        yield
        
    finally:
        # Restore stderr
        try:
            if original_stderr_fd is not None:
                os.dup2(original_stderr_fd, 2)
                os.close(original_stderr_fd)
        except:
            pass
        
        sys.stderr = original_stderr

# ============================================================================
# Module-Level Client Import
# ============================================================================
# Import Anthropic client at module level for better performance and to check
# availability once rather than on every function call
try:
    with suppress_stderr():
        from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    Anthropic = None  # type: ignore


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================
class AnthropicLLMError(Exception):
    """
    Base exception class for all Anthropic Claude LLM-related errors.
    
    All custom exceptions in this module inherit from this class,
    allowing users to catch any module-specific error with a single
    except clause.
    """


class AnthropicLLMImportError(AnthropicLLMError):
    """
    Raised when the Anthropic client library cannot be imported or initialized.
    
    Common causes:
        - Anthropic package not installed (pip install anthropic)
        - Missing or invalid API key
        - Client initialization failure
    """


class AnthropicLLMAPIError(AnthropicLLMError):
    """
    Raised when the API request fails after all retry attempts.
    
    Common causes:
        - Network connectivity issues
        - API service unavailable
        - Rate limiting or quota exceeded
        - Invalid model name or parameters
        - Overloaded API errors
    """


class AnthropicLLMResponseError(AnthropicLLMError):
    """
    Raised when the API response cannot be interpreted or is malformed.
    
    Common causes:
        - Empty response from API
        - Missing content blocks in response
        - Unexpected response format
    """


def anthropic_llm(
    prompt: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    max_retries: int = 3,
    timeout: Optional[float] = 30.0,
    backoff_factor: float = 0.5,
    temperature: Optional[float] = None,
    max_tokens: int = 4096,
) -> str:
    """Call an Anthropic Claude model and return the generated text.

    Args:
        prompt: The prompt / input text to send to the model. Must be non-empty.
        model: Model identifier (e.g. "claude-3-opus-20240229", "claude-3-sonnet-20240229").
        api_key: API key to use. If omitted, will try ANTHROPIC_API_KEY env var.
        max_retries: Number of attempts to make on transient failures.
        timeout: Optional timeout (seconds) to pass to the underlying client.
        backoff_factor: Base factor for exponential backoff between retries.
        temperature: Sampling temperature (0.0 to 1.0, optional).
        max_tokens: Maximum tokens in response (default: 4096, required by Anthropic).

    Returns:
        The generated text from the model.

    Raises:
        ValueError: If required arguments are missing or invalid.
        AnthropicLLMImportError: If the Anthropic client is not installed.
        AnthropicLLMAPIError: If all retry attempts fail.
        AnthropicLLMResponseError: If a response is returned but contains no text.
    """

    # ========================================================================
    # Input Validation
    # ========================================================================
    # Validate prompt
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    
    # Validate model identifier
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be a non-empty string")
    
    # Validate retry configuration
    if not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError("max_retries must be an integer >= 1")
    
    # Validate generation parameters (Claude uses 0.0-1.0 range for temperature)
    if temperature is not None and not (0.0 <= temperature <= 1.0):
        raise ValueError("temperature must be between 0.0 and 1.0")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    # ========================================================================
    # API Key Configuration
    # ========================================================================
    # Try provided key first, fallback to environment variable
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AnthropicLLMImportError(
            "No API key provided and environment variable ANTHROPIC_API_KEY is not set"
        )

    # ========================================================================
    # Client Initialization
    # ========================================================================
    # Check if Anthropic package is available
    if not _ANTHROPIC_AVAILABLE or Anthropic is None:
        raise AnthropicLLMImportError(
            "Anthropic package not installed. Install with: pip install anthropic"
        )

    # Initialize Anthropic client with timeout
    try:
        client = Anthropic(api_key=api_key, timeout=timeout)
    except Exception as exc:
        raise AnthropicLLMImportError(
            "Failed to initialize Anthropic client"
        ) from exc

    # ========================================================================
    # Retry Loop with Exponential Backoff
    # ========================================================================
    last_exc: Optional[BaseException] = None

    for attempt in range(1, max_retries + 1):
        try:
            # ================================================================
            # Prepare API Request
            # ================================================================
            # Build request parameters (max_tokens is required by Anthropic)
            kwargs: dict = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Add optional parameters if provided
            if temperature is not None:
                kwargs["temperature"] = temperature

            # ================================================================
            # Execute API Call
            # ================================================================
            response = client.messages.create(**kwargs)

            # ================================================================
            # Extract and Validate Response
            # ================================================================
            # Check if response contains content
            if not response.content:
                raise AnthropicLLMResponseError("No content in response")
            
            # Claude responses can contain multiple content blocks
            # Extract and concatenate all text blocks
            text_parts = []
            for block in response.content:
                if hasattr(block, 'text'):
                    text_parts.append(block.text)
            
            # Verify we extracted at least some text
            if not text_parts:
                raise AnthropicLLMResponseError("No text content in response")

            # Combine all text parts and return cleaned response
            return "".join(text_parts).strip()

        except AnthropicLLMError:
            # Re-raise our custom exceptions without retry
            raise
        except Exception as exc:
            # Handle transient errors with retry logic
            last_exc = exc
            if attempt == max_retries:
                # All retries exhausted
                raise AnthropicLLMAPIError(
                    f"Anthropic LLM request failed after {max_retries} attempts: {exc}"
                ) from exc

            # ================================================================
            # Exponential Backoff
            # ================================================================
            # Calculate sleep duration: backoff_factor * 2^(attempt-1)
            # Example: 0.5s, 1s, 2s, 4s, 8s...
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    # Fallback error if loop exits without returning
    raise AnthropicLLMAPIError("Anthropic LLM request failed") from last_exc


class AnthropicLLM:
    """
    Class-based wrapper for Anthropic Claude LLM with generate_response method.
    
    This class wraps the anthropic_llm function to provide a stateful interface
    suitable for use with agents and other systems that expect an object
    with a generate_response(prompt) method.
    
    Example:
        >>> llm = AnthropicLLM(model="claude-3-sonnet-20240229", api_key="your-key")
        >>> response = llm.generate_response("What is Python?")
        >>> print(response)
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        *,
        max_retries: int = 3,
        timeout: Optional[float] = 30.0,
        backoff_factor: float = 0.5,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
    ):
        """
        Initialize Anthropic Claude LLM wrapper.
        
        Args:
            model: Model identifier (e.g. "claude-3-opus-20240229", "claude-3-sonnet-20240229")
            api_key: API key (optional if ANTHROPIC_API_KEY env var is set)
            max_retries: Number of retry attempts on failure
            timeout: Request timeout in seconds
            backoff_factor: Exponential backoff factor for retries
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response (required by Anthropic)
        """
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the Anthropic Claude model.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            ValueError: If prompt is invalid
            AnthropicLLMImportError: If Anthropic client not available
            AnthropicLLMAPIError: If API request fails
            AnthropicLLMResponseError: If response is invalid
        """
        return anthropic_llm(
            prompt=prompt,
            model=self.model,
            api_key=self.api_key,
            max_retries=self.max_retries,
            timeout=self.timeout,
            backoff_factor=self.backoff_factor,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )


__all__ = [
    "anthropic_llm",
    "AnthropicLLM",
    "AnthropicLLMError",
    "AnthropicLLMAPIError",
    "AnthropicLLMImportError",
    "AnthropicLLMResponseError",
]
