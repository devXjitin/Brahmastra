"""
Google Gemini LLM Provider Module
==================================

A production-ready wrapper around Google's Generative AI client with comprehensive
error handling, automatic retries with exponential backoff, and flexible response parsing.

This module provides two interfaces for interacting with Gemini models:
    1. Function-based API: `google_llm()` for stateless one-off calls
    2. Class-based API: `GoogleLLM` for stateful usage with agents

Key Features:
-------------
- Robust error handling with custom exception hierarchy
- Automatic retry mechanism with configurable exponential backoff
- Request timeout management
- Flexible response parsing (handles multiple SDK versions)
- Input validation for all parameters
- Support for all Gemini models (Pro, Flash, Ultra)
- Advanced generation parameters (temperature, top_p, top_k)
- Silent operation (no logging per design requirement)
- Comprehensive stderr suppression for gRPC warnings

Supported Models:
-----------------
- Gemini 1.5 Pro (gemini-1.5-pro, gemini-1.5-pro-latest)
- Gemini 1.5 Flash (gemini-1.5-flash, gemini-1.5-flash-latest)
- Gemini Pro (gemini-pro)
- Gemini Pro Vision (gemini-pro-vision)

Configuration:
--------------
API key can be provided via:
    - Direct parameter: api_key="your-key"
    - Environment variable: GOOGLE_API_KEY

Example Usage:
--------------
    Function-based:
        >>> from brahmastra.llm_provider import google_llm, GoogleLLMError
        >>> try:
        ...     response = google_llm(
        ...         prompt="Explain Python in one sentence",
        ...         model="gemini-1.5-pro",
        ...         api_key="your-api-key-here",
        ...         temperature=0.7,
        ...         max_tokens=100
        ...     )
        ...     print(response)
        ... except GoogleLLMError as e:
        ...     print(f"Error: {e}")
    
    Class-based:
        >>> from brahmastra.llm_provider import GoogleLLM
        >>> llm = GoogleLLM(model="gemini-1.5-pro", api_key="your-key")
        >>> response = llm.generate_response("What is Python?")
        >>> print(response)

Technical Notes:
----------------
- Handles multiple google.generativeai SDK versions and response formats
- Uses defensive response parsing with fallback strategies
- Automatically suppresses gRPC ALTS warnings during import

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
# Suppress verbose logging from gRPC and underlying libraries
# Google's generativeai uses gRPC which can produce verbose ALTS warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'          # Suppress gRPC verbose logs
os.environ['GLOG_minloglevel'] = '2'            # Suppress Google logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'        # Suppress TensorFlow logs

# Suppress Python warnings from gRPC modules
warnings.filterwarnings('ignore', category=UserWarning, module='.*grpc.*')

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
# Import Google generativeai client at module level for better performance
# Handle multiple packaging strategies (google.generativeai vs google.genai)
_GOOGLE_GENAI_AVAILABLE = False
genai_module = None
try:
    with suppress_stderr():
        try:
            # Preferred: standard packaging
            import google.generativeai as genai_module  # type: ignore
            _GOOGLE_GENAI_AVAILABLE = True
        except Exception:
            # Fallback: alternate or older packaging structure
            from google import genai as genai_module  # type: ignore
            _GOOGLE_GENAI_AVAILABLE = True
except Exception:
    _GOOGLE_GENAI_AVAILABLE = False
    genai_module = None


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================
class GoogleLLMError(Exception):
    """
    Base exception class for all Google Gemini LLM-related errors.
    
    All custom exceptions in this module inherit from this class,
    allowing users to catch any module-specific error with a single
    except clause.
    """


class GoogleLLMImportError(GoogleLLMError):
    """
    Raised when the Google generative AI client library cannot be imported or initialized.
    
    Common causes:
        - google-generativeai package not installed (pip install google-generativeai)
        - Missing or invalid API key
        - Client initialization failure
        - Incompatible SDK version
    """


class GoogleLLMAPIError(GoogleLLMError):
    """
    Raised when the API request fails after all retry attempts.
    
    Common causes:
        - Network connectivity issues
        - API service unavailable
        - Rate limiting or quota exceeded
        - Invalid model name or parameters
        - Authentication failures
    """


class GoogleLLMResponseError(GoogleLLMError):
    """
    Raised when the API response cannot be interpreted or is malformed.
    
    Common causes:
        - Empty response from API
        - Missing expected fields in response structure
        - Unexpected response format from SDK version
        - Content safety filters blocked the response
    """


def _extract_text_from_response(resp: Any) -> Optional[str]:
    """
    Extract generated text from Google API response using defensive parsing.
    
    The Google generativeai SDK has evolved across versions, resulting in
    different response object structures. This function implements multiple
    extraction strategies to ensure compatibility across SDK versions.
    
    Extraction Strategies (in order):
        1. Direct .text attribute (most common for recent SDKs)
        2. candidates[0].content.parts[0].text (structured format)
        3. Dict-based extraction for JSON-like responses
        4. Fallback patterns for legacy response formats
    
    Args:
        resp: Response object from Google Gemini API (can be object, dict, or other)
    
    Returns:
        Extracted text string if found, None if extraction fails
    
    Implementation Notes:
        - All extraction attempts are wrapped in try-except for fault tolerance
        - Validates extracted text is non-empty string before returning
        - Handles both callable and property-based .text attributes
    """
    # ========================================================================
    # Early Exit for None
    # ========================================================================
    if resp is None:
        return None

    # ========================================================================
    # Strategy 1: Direct .text Attribute
    # ========================================================================
    # Most recent SDK versions provide a direct .text attribute or property
    try:
        text = getattr(resp, "text", None)
        if text is not None:
            # Handle both callable properties and direct attributes
            if callable(text):
                text = text()
            if isinstance(text, str) and text.strip():
                return text
    except Exception:
        pass  # Fail silently, try next strategy

    # ========================================================================
    # Strategy 2: Structured Candidates Format
    # ========================================================================
    # Newer APIs structure responses as: response.candidates[0].content.parts[0].text
    candidates = getattr(resp, "candidates", None)
    if candidates and isinstance(candidates, (list, tuple)) and len(candidates) > 0:
        first_candidate = candidates[0]
        
        # Try nested structure: candidate.content.parts[0].text
        content = getattr(first_candidate, "content", None)
        if content:
            # Extract from parts array
            parts = getattr(content, "parts", None)
            if parts and isinstance(parts, (list, tuple)) and len(parts) > 0:
                first_part = parts[0]
                part_text = getattr(first_part, "text", None)
                if isinstance(part_text, str) and part_text.strip():
                    return part_text
            
            # Try direct text in content object
            content_text = getattr(content, "text", None)
            if isinstance(content_text, str) and content_text.strip():
                return content_text
        
        # Try direct text in candidate (legacy format)
        candidate_text = getattr(first_candidate, "text", None)
        if isinstance(candidate_text, str) and candidate_text.strip():
            return candidate_text

    # ========================================================================
    # Strategy 3: Dictionary-Based Responses
    # ========================================================================
    # Handle JSON-like dict responses from different SDK versions
    try:
        if isinstance(resp, dict):
            # Try nested dict structure: candidates[0].content.parts[0].text
            candidates = resp.get("candidates")
            if candidates and isinstance(candidates, (list, tuple)) and len(candidates) > 0:
                first = candidates[0]
                if isinstance(first, dict):
                    # Extract from deeply nested structure
                    content = first.get("content")
                    if isinstance(content, dict):
                        parts = content.get("parts")
                        if isinstance(parts, (list, tuple)) and len(parts) > 0:
                            part = parts[0]
                            if isinstance(part, dict):
                                text = part.get("text")
                                if isinstance(text, str) and text.strip():
                                    return text
                    
                    # Try simpler dict structures
                    cont = first.get("content") or first.get("text")
                    if isinstance(cont, str) and cont.strip():
                        return cont
            
            # Try top-level 'text' field (simplest format)
            cont = resp.get("text")
            if isinstance(cont, str) and cont.strip():
                return cont
    except Exception:
        # Fail silently - all extraction strategies exhausted
        pass

    # No valid text found in any format
    return None


def google_llm(
    prompt: str,
    model: str,
    api_key: Optional[str] = None,
    *,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    max_tokens: Optional[int] = None,
    max_retries: int = 3,
    timeout: Optional[float] = 30.0,
    backoff_factor: float = 0.5,
) -> str:
    """Call a Google generative model and return the generated text.

    Args:
        prompt: The prompt / input text to send to the model. Must be non-empty.
        model: Model identifier (e.g. "gemini-pro" or other supported model name).
        api_key: API key to use. If omitted, the function will try the
            environment variable ``GOOGLE_API_KEY``.
        temperature: Controls randomness (0.0-2.0). Higher = more random.
        top_p: Nucleus sampling threshold (0.0-1.0). Alternative to temperature.
        top_k: Top-k sampling. Limits to k most likely tokens.
        max_tokens: Maximum tokens to generate (max_output_tokens).
        max_retries: Number of attempts to make on transient failures.
        timeout: Optional timeout (seconds) to pass to the underlying client.
        backoff_factor: Base factor for exponential backoff between retries.

    Returns:
        The generated text from the model.

    Raises:
        ValueError: If required arguments are missing or invalid.
        GoogleLLMImportError: If the Google client is not installed.
        GoogleLLMAPIError: If all retry attempts fail.
        GoogleLLMResponseError: If a response is returned but contains no text.
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
    if top_p is not None and not (0.0 <= top_p <= 1.0):
        raise ValueError("top_p must be between 0.0 and 1.0")
    if top_k is not None and top_k < 1:
        raise ValueError("top_k must be >= 1")
    if max_tokens is not None and max_tokens < 1:
        raise ValueError("max_tokens must be >= 1")

    # ========================================================================
    # Build Generation Configuration
    # ========================================================================
    # Construct generation config dict from provided parameters
    generation_config = {}
    if temperature is not None:
        generation_config["temperature"] = temperature
    if top_p is not None:
        generation_config["top_p"] = top_p
    if top_k is not None:
        generation_config["top_k"] = top_k
    if max_tokens is not None:
        # Google uses 'max_output_tokens' instead of 'max_tokens'
        generation_config["max_output_tokens"] = max_tokens

    # ========================================================================
    # API Key Configuration
    # ========================================================================
    # Try provided key first, fallback to environment variable
    api_key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise GoogleLLMImportError(
            "No API key provided and environment variable GOOGLE_API_KEY is not set"
        )

    # ========================================================================
    # Client Availability Check
    # ========================================================================
    # Verify google-generativeai package was imported successfully
    if not _GOOGLE_GENAI_AVAILABLE or genai_module is None:
        raise GoogleLLMImportError(
            "Failed to import or initialize google.generativeai client"
        )

    # ========================================================================
    # Client Configuration
    # ========================================================================
    # Use the module-level imported genai
    genai = genai_module
    client = None
    
    # Google's SDK has multiple initialization patterns across versions:
    # 1. genai.configure(api_key=...) + GenerativeModel (common pattern)
    # 2. Client(api_key=...) + client.models.generate_content (wrapper pattern)
    # We attempt both to maximize compatibility
    
    # Try configure() pattern (no return value, sets global state)
    try:
        with suppress_stderr():
            cfg = getattr(genai, "configure", None)
            if callable(cfg):
                cfg(api_key=api_key)
    except Exception:
        pass  # Non-fatal: some SDK versions don't require configure

    # Try Client() pattern (returns client object)
    try:
        with suppress_stderr():
            ClientCls = getattr(genai, "Client", None)
            if callable(ClientCls):
                try:
                    client = ClientCls(api_key=api_key)
                except TypeError:
                    # Some Client constructors have different signatures
                    client = ClientCls()
    except Exception:
        pass  # Non-fatal: GenerativeModel pattern may still work

    # ========================================================================
    # Retry Loop with Exponential Backoff
    # ========================================================================
    last_exc: Optional[BaseException] = None

    for attempt in range(1, max_retries + 1):
        try:
            # ================================================================
            # Multi-Strategy API Call
            # ================================================================
            # Google's SDK has evolved with different calling patterns.
            # We try multiple strategies to maximize compatibility.
            # All API calls wrapped in stderr suppression to hide gRPC warnings.
            
            with suppress_stderr():
                # ------------------------------------------------------------
                # Strategy 1: Client-based API (client.models.generate_content)
                # ------------------------------------------------------------
                if client is not None:
                    models_attr = getattr(client, "models", None)
                    gen_fn = getattr(models_attr, "generate_content", None) if models_attr else None
                    if callable(gen_fn):
                        resp = gen_fn(model=model, contents=prompt, timeout=timeout)
                        text = _extract_text_from_response(resp)
                        if text:
                            return text

                # ------------------------------------------------------------
                # Strategy 2: GenerativeModel Class (preferred modern approach)
                # ------------------------------------------------------------
                GenerativeModel = getattr(genai, "GenerativeModel", None)
                if callable(GenerativeModel):
                    try:
                        # Initialize model with optional generation config
                        if generation_config:
                            model_obj = GenerativeModel(model, generation_config=generation_config)
                        else:
                            model_obj = GenerativeModel(model)
                        
                        # Call generate_content method
                        gen_fn = getattr(model_obj, "generate_content", None)
                        if callable(gen_fn):
                            # Note: GenerativeModel.generate_content doesn't support timeout parameter
                            resp = gen_fn(prompt)
                            text = _extract_text_from_response(resp)
                            if text:
                                return text
                    except Exception:
                        pass  # Fall through to next strategy

                # ------------------------------------------------------------
                # Strategy 3: Top-level Convenience Functions (legacy)
                # ------------------------------------------------------------
                for helper_name in ("generate_text", "generate", "model_generate"):
                    helper = getattr(genai, helper_name, None)
                    if callable(helper):
                        try:
                            resp = helper(model=model, prompt=prompt, timeout=timeout)
                            text = _extract_text_from_response(resp)
                            if text:
                                return text
                        except Exception:
                            pass  # Try next helper

            # ================================================================
            # No Valid Response Extracted
            # ================================================================
            # If all strategies failed to extract text, raise error for retry
            raise GoogleLLMResponseError("No text could be extracted from the API response")

        except Exception as exc:
            # ================================================================
            # Error Handling and Retry Logic
            # ================================================================
            last_exc = exc
            if attempt == max_retries:
                # All retries exhausted
                raise GoogleLLMAPIError(
                    f"Google LLM request failed after {max_retries} attempts: {exc}"
                ) from exc

            # ================================================================
            # Exponential Backoff
            # ================================================================
            # Calculate sleep duration: backoff_factor * 2^(attempt-1)
            sleep_for = backoff_factor * (2 ** (attempt - 1))
            time.sleep(sleep_for)

    # Fallback error if loop exits without returning
    raise GoogleLLMAPIError("Google LLM request failed") from last_exc


class GoogleLLM:
    """
    Class-based wrapper for Google Gemini LLM with generate_response method.
    
    This class wraps the google_llm function to provide a stateful interface
    suitable for use with agents and other systems that expect an object
    with a generate_response(prompt) method.
    
    Example:
        >>> llm = GoogleLLM(model="gemini-1.5-pro", api_key="your-key")
        >>> response = llm.generate_response("What is Python?")
        >>> print(response)
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        *,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        timeout: Optional[float] = 30.0,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize Google Gemini LLM wrapper.
        
        Args:
            model: Model identifier (e.g. "gemini-1.5-pro", "gemini-pro")
            api_key: API key (optional if GOOGLE_API_KEY env var is set)
            temperature: Controls randomness (0.0-2.0)
            top_p: Nucleus sampling threshold (0.0-1.0)
            top_k: Top-k sampling
            max_tokens: Maximum tokens to generate
            max_retries: Number of retry attempts on failure
            timeout: Request timeout in seconds
            backoff_factor: Exponential backoff factor for retries
        """
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.timeout = timeout
        self.backoff_factor = backoff_factor
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the Google Gemini model.
        
        Args:
            prompt: The input prompt text
            
        Returns:
            Generated response text
            
        Raises:
            ValueError: If prompt is invalid
            GoogleLLMImportError: If Google client not available
            GoogleLLMAPIError: If API request fails
            GoogleLLMResponseError: If response is invalid
        """
        return google_llm(
            prompt=prompt,
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            max_tokens=self.max_tokens,
            max_retries=self.max_retries,
            timeout=self.timeout,
            backoff_factor=self.backoff_factor,
        )


__all__ = [
    "google_llm",
    "GoogleLLM",
    "GoogleLLMError",
    "GoogleLLMAPIError",
    "GoogleLLMImportError",
    "GoogleLLMResponseError",
]