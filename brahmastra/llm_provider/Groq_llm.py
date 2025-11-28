"""
Groq LLM Provider Module
=========================

A production-ready wrapper around Groq's high-performance API client with comprehensive
error handling, automatic retries with exponential backoff, and timeout management.

This module provides two interfaces for interacting with Groq's ultra-fast inference models:
    1. Function-based API: `groq_llm()` for stateless one-off calls
    2. Class-based API: `GroqLLM` for stateful usage with agents

Key Features:
-------------
- Robust error handling with custom exception hierarchy
- Automatic retry mechanism with configurable exponential backoff
- Request timeout management
- Input validation for all parameters
- Support for Groq's ultra-fast inference models
- Silent operation (no logging per design requirement)
- Stderr suppression for clean output

Supported Models:
-----------------
- LLaMA 3 (llama3-70b-8192, llama3-8b-8192)
- Mixtral (mixtral-8x7b-32768)
- Gemma (gemma-7b-it, gemma2-9b-it)
- And other Groq-supported models

Performance:
------------
Groq provides industry-leading inference speed with their LPU™ Inference Engine,
delivering 10-100x faster responses compared to traditional GPU-based inference.

Configuration:
--------------
API key can be provided via:
    - Direct parameter: api_key="your-key"
    - Environment variable: GROQ_API_KEY

Example Usage:
--------------
    Function-based:
        >>> from brahmastra.llm_provider import groq_llm, GroqLLMError
        >>> try:
        ...     response = groq_llm(
        ...         prompt="Explain Python in one sentence",
        ...         model="llama3-70b-8192",
        ...         api_key="your-api-key-here",
        ...         temperature=0.5
        ...     )
        ...     print(response)
        ... except GroqLLMError as e:
        ...     print(f"Error: {e}")
    
    Class-based:
        >>> from brahmastra.llm_provider import GroqLLM
        >>> llm = GroqLLM(model="mixtral-8x7b-32768", api_key="your-key")
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

# Suppress gRPC and other warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Suppress Python warnings
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
# Import Groq client at module level for better performance and to check
# availability once rather than on every function call
try:
    with suppress_stderr():
        from groq import Groq
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False
    Groq = None  # type: ignore


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================
class GroqLLMError(Exception):
    """
    Base exception class for all Groq LLM-related errors.
    
    All custom exceptions in this module inherit from this class,
    allowing users to catch any module-specific error with a single
    except clause.
    """


class GroqLLMImportError(GroqLLMError):
    """
    Raised when the Groq client library cannot be imported or initialized.
    
    Common causes:
        - Groq package not installed (pip install groq)
        - Missing or invalid API key
        - Client initialization failure
    """


class GroqLLMAPIError(GroqLLMError):
    """
    Raised when the API request fails after all retry attempts.
    
    Common causes:
        - Network connectivity issues
        - API service unavailable
        - Rate limiting or quota exceeded
        - Invalid model name or parameters
        - Groq service temporarily overloaded
    """


class GroqLLMResponseError(GroqLLMError):
    """
    Raised when the API response cannot be interpreted or is malformed.
    
    Common causes:
        - Empty response from API
        - Missing expected fields in response
        - Unexpected response format
    """


def groq_llm(
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
    """Call a Groq model and return the generated text.

    Args:
        prompt: The prompt / input text to send to the model. Must be non-empty.
        model: Model identifier (e.g. "llama3-70b-8192", "mixtral-8x7b-32768").
        api_key: API key to use. If omitted, will try GROQ_API_KEY env var.
        max_retries: Number of attempts to make on transient failures.
        timeout: Optional timeout (seconds) to pass to the underlying client.
        backoff_factor: Base factor for exponential backoff between retries.
        temperature: Sampling temperature (0.0 to 2.0, optional).
        max_tokens: Maximum tokens in response (optional).

    Returns:
        The generated text from the model.

    Raises:
        ValueError: If required arguments are missing or invalid.
        GroqLLMImportError: If the Groq client is not installed.
        GroqLLMAPIError: If all retry attempts fail.
        GroqLLMResponseError: If a response is returned but contains no text.
    """

    # Basic validation
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be a non-empty string")
    if not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError("max_retries must be an integer >= 1")
    if temperature is not None and not (0.0 <= temperature <= 2.0):
        raise ValueError("temperature must be between 0.0 and 2.0")
    if max_tokens is not None and max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise GroqLLMImportError(
            "No API key provided and environment variable GROQ_API_KEY is not set"
        )

    # Check if Groq client is available
    if not _GROQ_AVAILABLE or Groq is None:
        raise GroqLLMImportError(
            "Groq package not installed. Install with: pip install groq"
        )

    # Initialize client
    try:
        client = Groq(api_key=api_key, timeout=timeout)
    except Exception as exc:
        raise GroqLLMImportError(
            "Failed to initialize Groq client"
        ) from exc

    last_exc: Optional[BaseException] = None

    for attempt in range(1, max_retries + 1):
        try:
            # Prepare kwargs
            kwargs: dict = {"model": model, "messages": [{"role": "user", "content": prompt}]}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            # Make API request
            response = client.chat.completions.create(**kwargs)

            # Extract text
            if not response.choices:
                raise GroqLLMResponseError("No choices in response")
            
            text = response.choices[0].message.content
            if not text or not isinstance(text, str):
                raise GroqLLMResponseError("No valid text content in response")

            return text.strip()

        except GroqLLMError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt == max_retries:
                raise GroqLLMAPIError(
                    f"Groq LLM request failed after {max_retries} attempts: {exc}"
                ) from exc

            # Backoff before next retry
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    raise GroqLLMAPIError("Groq LLM request failed") from last_exc


class GroqLLM:
    """
    Class-based wrapper for Groq LLM with generate_response method.
    
    This class wraps the groq_llm function to provide a stateful interface
    suitable for use with agents and other systems that expect an object
    with a generate_response(prompt) method.
    
    Example:
        >>> llm = GroqLLM(model="llama3-70b-8192", api_key="your-key")
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
        Initialize Groq LLM wrapper.
        
        Args:
            model: Model identifier (e.g. "llama3-70b-8192", "mixtral-8x7b-32768")
            api_key: API key (optional if GROQ_API_KEY env var is set)
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
        Generate a response from the Groq model.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            ValueError: If prompt is invalid
            GroqLLMImportError: If Groq client not available
            GroqLLMAPIError: If API request fails
            GroqLLMResponseError: If response is invalid
        """
        return groq_llm(
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
    "groq_llm",
    "GroqLLM",
    "GroqLLMError",
    "GroqLLMAPIError",
    "GroqLLMImportError",
    "GroqLLMResponseError",
]
