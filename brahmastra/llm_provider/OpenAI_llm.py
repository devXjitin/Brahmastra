"""
OpenAI LLM Provider Module
===========================

A production-ready wrapper around OpenAI's API client with comprehensive error handling,
automatic retries with exponential backoff, and timeout management.

This module provides two interfaces for interacting with OpenAI models:
    1. Function-based API: `openai_llm()` for stateless one-off calls
    2. Class-based API: `OpenAILLM` for stateful usage with agents

Key Features:
-------------
- Robust error handling with custom exception hierarchy
- Automatic retry mechanism with configurable exponential backoff
- Request timeout management
- Input validation for all parameters
- Support for chat models (GPT-4, GPT-3.5-turbo, etc.)
- Silent operation (no logging per design requirement)
- Stderr suppression for clean output

Supported Models:
-----------------
- GPT-4 (gpt-4, gpt-4-turbo-preview)
- GPT-3.5 (gpt-3.5-turbo, gpt-3.5-turbo-16k)
- And all other OpenAI chat completion models

Configuration:
--------------
API key can be provided via:
    - Direct parameter: api_key="your-key"
    - Environment variable: OPENAI_API_KEY

Example Usage:
--------------
    Function-based:
        >>> from brahmastra.llm_provider import openai_llm, OpenAILLMError
        >>> try:
        ...     response = openai_llm(
        ...         prompt="Explain Python in one sentence",
        ...         model="gpt-4",
        ...         api_key="your-api-key-here",
        ...         temperature=0.7,
        ...         max_tokens=100
        ...     )
        ...     print(response)
        ... except OpenAILLMError as e:
        ...     print(f"Error: {e}")
    
    Class-based:
        >>> from brahmastra.llm_provider import OpenAILLM
        >>> llm = OpenAILLM(model="gpt-4", api_key="your-key", temperature=0.7)
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
    """
    Context manager to temporarily suppress stderr output.
    
    This function uses low-level file descriptor redirection to completely
    suppress stderr output from underlying libraries that may produce
    unwanted warnings or debug messages.
    
    Implementation:
        1. Saves the current stderr file descriptor
        2. Redirects stderr to /dev/null at OS level
        3. Redirects Python's sys.stderr to a StringIO buffer
        4. Restores original stderr on exit
    
    Usage:
        >>> with suppress_stderr():
        ...     # Code that produces stderr output
        ...     import_noisy_library()
    
    Note:
        All stderr suppression is temporary and automatically restored
        when exiting the context manager, even if an exception occurs.
    """
    import io
    
    # Save original stderr references
    original_stderr = sys.stderr
    original_stderr_fd = None
    
    try:
        # Save the original file descriptor (stderr is typically fd=2)
        try:
            original_stderr_fd = os.dup(2)
        except:
            pass  # Fail silently if fd operations not supported
        
        # Redirect stderr to devnull at the OS level
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, 2)
            os.close(devnull)
        except:
            pass  # Fail silently if redirection not supported
        
        # Also redirect Python's sys.stderr to a buffer
        sys.stderr = io.StringIO()
        
        yield
        
    finally:
        # Restore stderr to original state
        try:
            if original_stderr_fd is not None:
                os.dup2(original_stderr_fd, 2)
                os.close(original_stderr_fd)
        except:
            pass  # Fail silently during restoration
        
        sys.stderr = original_stderr

# ============================================================================
# Module-Level Client Import
# ============================================================================
# Import OpenAI client at module level for better performance and to check
# availability once rather than on every function call
try:
    with suppress_stderr():
        from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================
class OpenAILLMError(Exception):
    """
    Base exception class for all OpenAI LLM-related errors.
    
    All custom exceptions in this module inherit from this class,
    allowing users to catch any module-specific error with a single
    except clause.
    """


class OpenAILLMImportError(OpenAILLMError):
    """
    Raised when the OpenAI client library cannot be imported or initialized.
    
    Common causes:
        - OpenAI package not installed (pip install openai)
        - Missing or invalid API key
        - Client initialization failure
    """


class OpenAILLMAPIError(OpenAILLMError):
    """
    Raised when the API request fails after all retry attempts.
    
    Common causes:
        - Network connectivity issues
        - API service unavailable
        - Rate limiting or quota exceeded
        - Invalid model name or parameters
    """


class OpenAILLMResponseError(OpenAILLMError):
    """
    Raised when the API response cannot be interpreted or is malformed.
    
    Common causes:
        - Empty response from API
        - Missing expected fields in response
        - Unexpected response format
    """


def openai_llm(
    prompt: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    max_retries: int = 3,
    timeout: Optional[float] = 30.0,
    backoff_factor: float = 0.5,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> str:
    """Call an OpenAI model and return the generated text.

    Args:
        prompt: The prompt / input text to send to the model. Must be non-empty.
        model: Model identifier (e.g. "gpt-4", "gpt-3.5-turbo").
        api_key: API key to use. If omitted, will try OPENAI_API_KEY env var.
        max_retries: Number of attempts to make on transient failures.
        timeout: Optional timeout (seconds) to pass to the underlying client.
        backoff_factor: Base factor for exponential backoff between retries.
        temperature: Sampling temperature (0.0 to 2.0, optional).
        max_tokens: Maximum tokens in response (optional).

    Returns:
        The generated text from the model.

    Raises:
        ValueError: If required arguments are missing or invalid.
        OpenAILLMImportError: If the OpenAI client is not installed.
        OpenAILLMAPIError: If all retry attempts fail.
        OpenAILLMResponseError: If a response is returned but contains no text.
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
    
    # Validate generation parameters
    if temperature is not None and not (0.0 <= temperature <= 2.0):
        raise ValueError("temperature must be between 0.0 and 2.0")
    if max_tokens is not None and max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    # ========================================================================
    # API Key Configuration
    # ========================================================================
    # Try provided key first, fallback to environment variable
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise OpenAILLMImportError(
            "No API key provided and environment variable OPENAI_API_KEY is not set"
        )

    # ========================================================================
    # Client Initialization
    # ========================================================================
    # Check if OpenAI package is available
    if not _OPENAI_AVAILABLE or OpenAI is None:
        raise OpenAILLMImportError(
            "OpenAI package not installed. Install with: pip install openai"
        )

    # Initialize OpenAI client with timeout
    try:
        client = OpenAI(api_key=api_key, timeout=timeout)
    except Exception as exc:
        raise OpenAILLMImportError(
            "Failed to initialize OpenAI client"
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
            # Build request parameters with chat completion format
            kwargs: dict = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Add optional parameters if provided
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            # ================================================================
            # Execute API Call
            # ================================================================
            response = client.chat.completions.create(**kwargs)

            # ================================================================
            # Extract and Validate Response
            # ================================================================
            # Check if response contains choices
            if not response.choices:
                raise OpenAILLMResponseError("No choices in response")
            
            # Extract text content from first choice
            text = response.choices[0].message.content
            if not text or not isinstance(text, str):
                raise OpenAILLMResponseError("No valid text content in response")

            # Return cleaned response
            return text.strip()

        except OpenAILLMError:
            # Re-raise our custom exceptions without retry
            raise
        except Exception as exc:
            # Handle transient errors with retry logic
            last_exc = exc
            if attempt == max_retries:
                # All retries exhausted
                raise OpenAILLMAPIError(
                    f"OpenAI LLM request failed after {max_retries} attempts: {exc}"
                ) from exc

            # ================================================================
            # Exponential Backoff
            # ================================================================
            # Calculate sleep duration: backoff_factor * 2^(attempt-1)
            # Example: 0.5s, 1s, 2s, 4s, 8s...
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    # Fallback error if loop exits without returning
    raise OpenAILLMAPIError("OpenAI LLM request failed") from last_exc


class OpenAILLM:
    """
    Class-based wrapper for OpenAI LLM with generate_response method.
    
    This class wraps the openai_llm function to provide a stateful interface
    suitable for use with agents and other systems that expect an object
    with a generate_response(prompt) method.
    
    Example:
        >>> llm = OpenAILLM(model="gpt-4", api_key="your-key", temperature=0.7)
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
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize OpenAI LLM wrapper.
        
        Args:
            model: Model identifier (e.g. "gpt-4", "gpt-3.5-turbo")
            api_key: API key (optional if OPENAI_API_KEY env var is set)
            max_retries: Number of retry attempts on failure
            timeout: Request timeout in seconds
            backoff_factor: Exponential backoff factor for retries
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
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
        Generate a response from the OpenAI model.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            ValueError: If prompt is invalid
            OpenAILLMImportError: If OpenAI client not available
            OpenAILLMAPIError: If API request fails
            OpenAILLMResponseError: If response is invalid
        """
        return openai_llm(
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
    "openai_llm",
    "OpenAILLM",
    "OpenAILLMError",
    "OpenAILLMAPIError",
    "OpenAILLMImportError",
    "OpenAILLMResponseError",
]
