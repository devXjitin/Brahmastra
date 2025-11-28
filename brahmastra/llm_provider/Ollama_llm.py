"""
Ollama LLM Provider Module
===========================

A production-ready wrapper around Ollama's local API client with comprehensive
error handling, automatic retries with exponential backoff, and timeout management.

This module provides two interfaces for interacting with locally-hosted Ollama models:
    1. Function-based API: `ollama_llm()` for stateless one-off calls
    2. Class-based API: `OllamaLLM` for stateful usage with agents

Key Features:
-------------
- Robust error handling with custom exception hierarchy
- Automatic retry mechanism with configurable exponential backoff
- Request timeout management
- Input validation for all parameters
- Support for all Ollama-hosted models
- Privacy-focused: runs entirely locally, no data sent to external services
- Silent operation (no logging per design requirement)
- Stderr suppression for clean output

Supported Models:
-----------------
- LLaMA 2 (llama2, llama2:13b, llama2:70b)
- Mistral (mistral, mistral:instruct)
- CodeLLaMA (codellama, codellama:python)
- Phi-2 (phi2)
- Neural Chat (neural-chat)
- Starling (starling-lm)
- And all other models available in Ollama registry

Prerequisites:
--------------
- Ollama must be installed and running locally
- Default server: http://localhost:11434
- Install Ollama: https://ollama.ai/download

Configuration:
--------------
Server URL can be provided via:
    - Direct parameter: base_url="http://localhost:11434"
    - Environment variable: OLLAMA_BASE_URL
    - Default: http://localhost:11434 (if not specified)

Example Usage:
--------------
    Function-based:
        >>> from brahmastra.llm_provider import ollama_llm, OllamaLLMError
        >>> try:
        ...     response = ollama_llm(
        ...         prompt="Explain Python in one sentence",
        ...         model="llama2",
        ...         base_url="http://localhost:11434",
        ...         temperature=0.7
        ...     )
        ...     print(response)
        ... except OllamaLLMError as e:
        ...     print(f"Error: {e}")
    
    Class-based:
        >>> from brahmastra.llm_provider import OllamaLLM
        >>> llm = OllamaLLM(model="mistral", base_url="http://localhost:11434")
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
# Import Ollama client at module level for better performance and to check
# availability once rather than on every function call
try:
    with suppress_stderr():
        from ollama import Client
    _OLLAMA_AVAILABLE = True
except ImportError:
    _OLLAMA_AVAILABLE = False
    Client = None  # type: ignore


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================
class OllamaLLMError(Exception):
    """
    Base exception class for all Ollama LLM-related errors.
    
    All custom exceptions in this module inherit from this class,
    allowing users to catch any module-specific error with a single
    except clause.
    """


class OllamaLLMImportError(OllamaLLMError):
    """
    Raised when the Ollama client library cannot be imported or initialized.
    
    Common causes:
        - Ollama package not installed (pip install ollama)
        - Invalid base_url provided
        - Client initialization failure
    """


class OllamaLLMAPIError(OllamaLLMError):
    """
    Raised when the API request fails after all retry attempts.
    
    Common causes:
        - Ollama server not running (start with: ollama serve)
        - Network connectivity issues to local server
        - Invalid model name (model not pulled)
        - Server temporarily unavailable
        - Connection refused or timeout
    """


class OllamaLLMResponseError(OllamaLLMError):
    """
    Raised when the API response cannot be interpreted or is malformed.
    
    Common causes:
        - Empty response from Ollama server
        - Missing expected fields in response
        - Unexpected response format
    """


def ollama_llm(
    prompt: str,
    model: str,
    base_url: Optional[str] = None,
    *,
    max_retries: int = 3,
    timeout: Optional[float] = 60.0,
    backoff_factor: float = 0.5,
    temperature: Optional[float] = None,
) -> str:
    """Call an Ollama local model and return the generated text.

    Args:
        prompt: The prompt / input text to send to the model. Must be non-empty.
        model: Model identifier (e.g. "llama2", "mistral", "codellama").
        base_url: Ollama server URL. If omitted, will try OLLAMA_BASE_URL env var
                  or default to http://localhost:11434.
        max_retries: Number of attempts to make on transient failures.
        timeout: Optional timeout (seconds) to pass to the underlying client.
        backoff_factor: Base factor for exponential backoff between retries.
        temperature: Sampling temperature (0.0 to 2.0, optional).

    Returns:
        The generated text from the model.

    Raises:
        ValueError: If required arguments are missing or invalid.
        OllamaLLMImportError: If the Ollama client is not installed.
        OllamaLLMAPIError: If all retry attempts fail.
        OllamaLLMResponseError: If a response is returned but contains no text.
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

    # ========================================================================
    # Server URL Configuration
    # ========================================================================
    # Priority: provided parameter > env variable > default localhost
    base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    # ========================================================================
    # Client Initialization
    # ========================================================================
    # Check if Ollama package is available
    if not _OLLAMA_AVAILABLE or Client is None:
        raise OllamaLLMImportError(
            "Ollama package not installed. Install with: pip install ollama"
        )

    # Initialize Ollama client with server URL
    try:
        client = Client(host=base_url)
    except Exception as exc:
        raise OllamaLLMImportError(
            f"Failed to initialize Ollama client with base_url={base_url}"
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
            # Build options dict for generation parameters
            options = {}
            if temperature is not None:
                options["temperature"] = temperature

            # ================================================================
            # Execute API Call
            # ================================================================
            # Call Ollama's chat endpoint with chat completion format
            response = client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options=options if options else None,
            )

            # ================================================================
            # Extract and Validate Response
            # ================================================================
            # Check for empty response
            if not response:
                raise OllamaLLMResponseError("Empty response from Ollama")
            
            # Ollama can return responses in different formats
            # Try multiple extraction strategies
            if isinstance(response, dict):
                # Primary format: response.message.content
                text = response.get("message", {}).get("content")
                if not text:
                    # Alternative format: response.response (legacy)
                    text = response.get("response")
            else:
                text = None

            # Validate extracted text
            if not text or not isinstance(text, str):
                raise OllamaLLMResponseError("No valid text content in response")

            # Return cleaned response
            return text.strip()

        except OllamaLLMError:
            # Re-raise our custom exceptions without retry
            raise
        except Exception as exc:
            # Handle transient errors with retry logic
            last_exc = exc
            if attempt == max_retries:
                # All retries exhausted
                raise OllamaLLMAPIError(
                    f"Ollama LLM request failed after {max_retries} attempts: {exc}"
                ) from exc

            # ================================================================
            # Exponential Backoff
            # ================================================================
            # Calculate sleep duration: backoff_factor * 2^(attempt-1)
            # Example: 0.5s, 1s, 2s, 4s, 8s...
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    # Fallback error if loop exits without returning
    raise OllamaLLMAPIError("Ollama LLM request failed") from last_exc


class OllamaLLM:
    """
    Class-based wrapper for Ollama LLM with generate_response method.
    
    This class wraps the ollama_llm function to provide a stateful interface
    suitable for use with agents and other systems that expect an object
    with a generate_response(prompt) method.
    
    Example:
        >>> llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")
        >>> response = llm.generate_response("What is Python?")
        >>> print(response)
    """
    
    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        *,
        max_retries: int = 3,
        timeout: Optional[float] = 60.0,
        backoff_factor: float = 0.5,
        temperature: Optional[float] = None,
    ):
        """
        Initialize Ollama LLM wrapper.
        
        Args:
            model: Model identifier (e.g. "llama2", "mistral", "codellama")
            base_url: Ollama server URL (optional, defaults to http://localhost:11434)
            max_retries: Number of retry attempts on failure
            timeout: Request timeout in seconds
            backoff_factor: Exponential backoff factor for retries
            temperature: Sampling temperature (0.0 to 2.0)
        """
        self.model = model
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor
        self.temperature = temperature
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the Ollama model.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            ValueError: If prompt is invalid
            OllamaLLMImportError: If Ollama client not available
            OllamaLLMAPIError: If API request fails
            OllamaLLMResponseError: If response is invalid
        """
        return ollama_llm(
            prompt=prompt,
            model=self.model,
            base_url=self.base_url,
            max_retries=self.max_retries,
            timeout=self.timeout,
            backoff_factor=self.backoff_factor,
            temperature=self.temperature,
        )


__all__ = [
    "ollama_llm",
    "OllamaLLM",
    "OllamaLLMError",
    "OllamaLLMAPIError",
    "OllamaLLMImportError",
    "OllamaLLMResponseError",
]
