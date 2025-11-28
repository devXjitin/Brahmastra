# LLM Provider Module

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: professional](https://img.shields.io/badge/code%20style-professional-brightgreen.svg)](https://github.com/devxJitin/Brahmastra)

A production-ready collection of LLM provider wrappers with robust error handling, automatic retries, and unified interfaces. Part of the **Brahmastra** framework.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Providers](#supported-providers)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The `llm_provider` module provides a unified, production-ready interface for interacting with multiple Large Language Model providers. Each provider wrapper includes:

- ✅ **Robust error handling** with custom exception hierarchies
- ✅ **Automatic retry logic** with exponential backoff
- ✅ **Request timeout management**
- ✅ **Input validation** for all parameters
- ✅ **Dual interfaces**: Function-based and Class-based APIs
- ✅ **Silent operation**: No logging (by design)
- ✅ **Type hints** for better IDE support

---

## ✨ Features

### 🔒 Production-Ready
- Comprehensive error handling with specific exception types
- Automatic retry mechanism for transient failures
- Configurable timeouts to prevent hanging requests
- Input validation to catch errors early

### 🎨 Flexible Interfaces
- **Function-based API**: Perfect for one-off calls and simple scripts
- **Class-based API**: Ideal for stateful usage with agents and frameworks

### 🛡️ Fault Tolerant
- Exponential backoff for retry attempts
- Defensive response parsing (especially for Google Gemini)
- Graceful handling of API version differences

### 🔇 Clean Output
- No logging by default (per design requirement)
- stderr suppression for noisy libraries (gRPC, TensorFlow, etc.)
- Clean error messages with actionable information

---

## 🚀 Supported Providers

| Provider | Models | Speed | Cost | Privacy |
|----------|--------|-------|------|---------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Fast | $$$ | Cloud |
| **Google Gemini** | Gemini 1.5 Pro/Flash | Fast | $$ | Cloud |
| **Anthropic Claude** | Claude 3 Opus/Sonnet/Haiku | Fast | $$$ | Cloud |
| **Groq** | LLaMA 3, Mixtral, Gemma | Ultra-Fast | $ | Cloud |
| **Ollama** | Any local model | Varies | Free | Local |

### Provider Details

#### 🤖 OpenAI
- **Models**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Best for**: General-purpose tasks, coding, analysis
- **API Key**: Required (OPENAI_API_KEY)

#### 🧠 Google Gemini
- **Models**: gemini-1.5-pro, gemini-1.5-flash, gemini-pro
- **Best for**: Long context, multimodal tasks
- **API Key**: Required (GOOGLE_API_KEY)

#### 🎭 Anthropic Claude
- **Models**: Claude 3 Opus, Sonnet, Haiku
- **Best for**: Safety-critical applications, long documents
- **API Key**: Required (ANTHROPIC_API_KEY)

#### ⚡ Groq
- **Models**: llama3-70b-8192, mixtral-8x7b-32768
- **Best for**: Ultra-fast inference (10-100x faster)
- **API Key**: Required (GROQ_API_KEY)

#### 🏠 Ollama
- **Models**: Any Ollama-supported model (llama2, mistral, codellama, etc.)
- **Best for**: Privacy, local deployment, no API costs
- **Requirements**: Ollama server running locally

---

## 📦 Installation

### Prerequisites
```bash
# Python 3.8 or higher
python --version
```

### Install Provider Dependencies

Choose the providers you need:

```bash
# OpenAI
pip install openai

# Google Gemini
pip install google-generativeai

# Anthropic Claude
pip install anthropic

# Groq
pip install groq

# Ollama (requires Ollama server)
pip install ollama
# Download Ollama: https://ollama.ai/download
```

### Install All Providers
```bash
pip install openai google-generativeai anthropic groq ollama
```

---

## 🚀 Quick Start

### Function-Based API (Simple)

```python
from brahmastra.llm_provider import openai_llm, OpenAILLMError

try:
    response = openai_llm(
        prompt="Explain quantum computing in one sentence",
        model="gpt-4",
        api_key="your-api-key-here",  # or set OPENAI_API_KEY env var
        temperature=0.7,
        max_tokens=100
    )
    print(response)
except OpenAILLMError as e:
    print(f"Error: {e}")
```

### Class-Based API (Stateful)

```python
from brahmastra.llm_provider import OpenAILLM

# Initialize once
llm = OpenAILLM(
    model="gpt-4",
    api_key="your-api-key-here",
    temperature=0.7,
    max_retries=3
)

# Use multiple times
response1 = llm.generate_response("What is Python?")
response2 = llm.generate_response("What is JavaScript?")
```

### Multi-Provider Example

```python
from brahmastra.llm_provider import (
    openai_llm, 
    google_llm, 
    anthropic_llm,
    groq_llm,
    ollama_llm
)

# Compare responses from different providers
prompt = "Explain recursion in simple terms"

providers = {
    "OpenAI": lambda: openai_llm(prompt, model="gpt-4", api_key="..."),
    "Google": lambda: google_llm(prompt, model="gemini-1.5-pro", api_key="..."),
    "Anthropic": lambda: anthropic_llm(prompt, model="claude-3-sonnet-20240229", api_key="..."),
    "Groq": lambda: groq_llm(prompt, model="llama3-70b-8192", api_key="..."),
    "Ollama": lambda: ollama_llm(prompt, model="llama2")
}

for name, func in providers.items():
    try:
        response = func()
        print(f"\n{name}:\n{response}\n{'-'*50}")
    except Exception as e:
        print(f"\n{name}: Error - {e}")
```

---

## 📚 API Reference

### OpenAI Provider

#### Function: `openai_llm()`
```python
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
) -> str
```

**Parameters:**
- `prompt` (str): Input text to send to the model
- `model` (str): Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
- `api_key` (str, optional): API key (defaults to OPENAI_API_KEY env var)
- `max_retries` (int): Number of retry attempts (default: 3)
- `timeout` (float, optional): Request timeout in seconds (default: 30.0)
- `backoff_factor` (float): Exponential backoff multiplier (default: 0.5)
- `temperature` (float, optional): Sampling temperature 0.0-2.0
- `max_tokens` (int, optional): Maximum tokens in response

**Returns:** Generated text string

**Raises:**
- `ValueError`: Invalid parameters
- `OpenAILLMImportError`: Package not installed or API key missing
- `OpenAILLMAPIError`: API request failed after retries
- `OpenAILLMResponseError`: Response parsing failed

#### Class: `OpenAILLM`
```python
class OpenAILLM:
    def __init__(self, model: str, api_key: Optional[str] = None, ...)
    def generate_response(self, prompt: str) -> str
```

**Usage:**
```python
llm = OpenAILLM(model="gpt-4", api_key="sk-...")
response = llm.generate_response("Hello, world!")
```

---

### Google Gemini Provider

#### Function: `google_llm()`
```python
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
) -> str
```

**Additional Parameters:**
- `top_p` (float, optional): Nucleus sampling threshold 0.0-1.0
- `top_k` (int, optional): Top-k sampling parameter
- `max_tokens` (int, optional): Maximum output tokens

#### Class: `GoogleLLM`
```python
llm = GoogleLLM(model="gemini-1.5-pro", api_key="...")
response = llm.generate_response("Explain AI")
```

---

### Anthropic Claude Provider

#### Function: `anthropic_llm()`
```python
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
) -> str
```

**Note:** `max_tokens` is required by Anthropic (default: 4096)

#### Class: `AnthropicLLM`
```python
llm = AnthropicLLM(model="claude-3-opus-20240229", api_key="...")
response = llm.generate_response("Write a poem")
```

---

### Groq Provider

#### Function: `groq_llm()`
```python
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
) -> str
```

**Popular Models:**
- `llama3-70b-8192`: LLaMA 3 70B (8K context)
- `llama3-8b-8192`: LLaMA 3 8B (8K context)
- `mixtral-8x7b-32768`: Mixtral 8x7B (32K context)
- `gemma-7b-it`: Google Gemma 7B Instruct

#### Class: `GroqLLM`
```python
llm = GroqLLM(model="llama3-70b-8192", api_key="...")
response = llm.generate_response("Code review this function")
```

---

### Ollama Provider

#### Function: `ollama_llm()`
```python
def ollama_llm(
    prompt: str,
    model: str,
    base_url: Optional[str] = None,
    *,
    max_retries: int = 3,
    timeout: Optional[float] = 60.0,
    backoff_factor: float = 0.5,
    temperature: Optional[float] = None,
) -> str
```

**Parameters:**
- `base_url` (str, optional): Ollama server URL (defaults to http://localhost:11434)

**Popular Models:**
- `llama2`: Meta LLaMA 2
- `mistral`: Mistral 7B
- `codellama`: Code-specialized LLaMA
- `phi2`: Microsoft Phi-2
- `neural-chat`: Intel Neural Chat

#### Class: `OllamaLLM`
```python
llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")
response = llm.generate_response("Hello!")
```

**Setup Ollama:**
```bash
# 1. Install Ollama (https://ollama.ai/download)

# 2. Start server
ollama serve

# 3. Pull a model
ollama pull llama2

# 4. Use in Python
from brahmastra.llm_provider import ollama_llm
response = ollama_llm("Hello", model="llama2")
```

---

## ⚙️ Configuration

### API Keys

Set API keys via environment variables (recommended):

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AI..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."
export OLLAMA_BASE_URL="http://localhost:11434"  # optional

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:GOOGLE_API_KEY="AI..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:GROQ_API_KEY="gsk_..."
```

Or pass directly in code:
```python
response = openai_llm(prompt="Hello", model="gpt-4", api_key="sk-...")
```

### Retry Configuration

Customize retry behavior:

```python
from brahmastra.llm_provider import openai_llm

response = openai_llm(
    prompt="Hello",
    model="gpt-4",
    api_key="...",
    max_retries=5,        # More retry attempts
    backoff_factor=1.0,   # Longer backoff (1s, 2s, 4s, 8s, 16s)
    timeout=60.0          # Longer timeout (60 seconds)
)
```

**Backoff Formula:** `sleep_time = backoff_factor * (2 ** attempt)`

| Attempt | backoff_factor=0.5 | backoff_factor=1.0 |
|---------|-------------------|-------------------|
| 1       | 0.5s              | 1.0s              |
| 2       | 1.0s              | 2.0s              |
| 3       | 2.0s              | 4.0s              |
| 4       | 4.0s              | 8.0s              |
| 5       | 8.0s              | 16.0s             |

### Generation Parameters

#### Temperature (Creativity)
- **0.0**: Deterministic, focused
- **0.5**: Balanced
- **1.0**: Creative
- **2.0**: Very creative (OpenAI/Groq only)

```python
# Deterministic output (good for code generation)
response = openai_llm(prompt="...", model="gpt-4", temperature=0.0)

# Creative output (good for creative writing)
response = openai_llm(prompt="...", model="gpt-4", temperature=1.5)
```

#### Max Tokens (Length)
```python
# Short response
response = openai_llm(prompt="...", model="gpt-4", max_tokens=100)

# Long response
response = openai_llm(prompt="...", model="gpt-4", max_tokens=2000)
```

---

## 🚨 Error Handling

### Exception Hierarchy

Each provider has a consistent exception hierarchy:

```
ProviderLLMError (base)
├── ProviderLLMImportError (package/key issues)
├── ProviderLLMAPIError (network/API failures)
└── ProviderLLMResponseError (parsing failures)
```

### Catching Specific Errors

```python
from brahmastra.llm_provider import (
    openai_llm,
    OpenAILLMError,
    OpenAILLMImportError,
    OpenAILLMAPIError,
    OpenAILLMResponseError
)

try:
    response = openai_llm(prompt="...", model="gpt-4", api_key="...")
    
except OpenAILLMImportError as e:
    # Package not installed or API key missing
    print(f"Setup error: {e}")
    print("Solution: pip install openai OR set OPENAI_API_KEY")
    
except OpenAILLMAPIError as e:
    # Network or API failure after retries
    print(f"API error: {e}")
    print("Solution: Check internet connection and API status")
    
except OpenAILLMResponseError as e:
    # Response parsing failed
    print(f"Response error: {e}")
    print("Solution: Report this issue")
    
except OpenAILLMError as e:
    # Catch-all for any provider error
    print(f"General error: {e}")
```

### Catching All Provider Errors

```python
from brahmastra.llm_provider import (
    openai_llm, google_llm, anthropic_llm,
    OpenAILLMError, GoogleLLMError, AnthropicLLMError
)

def call_llm_safely(provider_func, *args, **kwargs):
    try:
        return provider_func(*args, **kwargs)
    except (OpenAILLMError, GoogleLLMError, AnthropicLLMError) as e:
        print(f"LLM Error: {type(e).__name__}: {e}")
        return None

# Usage
result = call_llm_safely(openai_llm, prompt="...", model="gpt-4", api_key="...")
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `No API key provided` | Missing API key | Set env var or pass `api_key` parameter |
| `Package not installed` | Provider package missing | `pip install <provider>` |
| `Failed after N attempts` | Network/API issues | Check internet connection, API status |
| `No valid text content` | Unexpected response format | Report issue with details |
| `timeout` | Request took too long | Increase `timeout` parameter |

---

## 🎓 Advanced Usage

### Async/Parallel Calls

For parallel processing with multiple providers:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from brahmastra.llm_provider import openai_llm, google_llm, anthropic_llm

def call_provider(name, func, prompt):
    try:
        response = func(prompt)
        return (name, response, None)
    except Exception as e:
        return (name, None, str(e))

providers = {
    "OpenAI": lambda p: openai_llm(p, model="gpt-4", api_key="..."),
    "Google": lambda p: google_llm(p, model="gemini-1.5-pro", api_key="..."),
    "Anthropic": lambda p: anthropic_llm(p, model="claude-3-sonnet-20240229", api_key="...")
}

prompt = "Explain quantum entanglement"

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(call_provider, name, func, prompt)
        for name, func in providers.items()
    ]
    
    for future in as_completed(futures):
        name, response, error = future.result()
        if error:
            print(f"{name}: Error - {error}")
        else:
            print(f"\n{name}:\n{response}\n{'-'*50}")
```

### Streaming Responses

For streaming (not currently supported, but planned):

```python
# Future implementation
from brahmastra.llm_provider import OpenAILLM

llm = OpenAILLM(model="gpt-4", api_key="...")

for chunk in llm.generate_response_stream("Write a long story"):
    print(chunk, end="", flush=True)
```

### Agent Integration

Use with agent frameworks:

```python
from brahmastra.llm_provider import OpenAILLM

class MyAgent:
    def __init__(self):
        self.llm = OpenAILLM(
            model="gpt-4",
            api_key="...",
            temperature=0.7
        )
    
    def think(self, observation):
        prompt = f"Observation: {observation}\nWhat should I do next?"
        return self.llm.generate_response(prompt)
    
    def act(self, action):
        # Execute action
        pass

# Usage
agent = MyAgent()
thought = agent.think("I see a door")
agent.act(thought)
```

### Custom Retry Logic

Implement custom retry logic:

```python
from brahmastra.llm_provider import openai_llm, OpenAILLMAPIError
import time

def custom_retry_llm(prompt, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return openai_llm(
                prompt=prompt,
                model="gpt-4",
                api_key="...",
                max_retries=1  # Disable internal retry
            )
        except OpenAILLMAPIError as e:
            if attempt == max_attempts - 1:
                raise
            
            # Custom backoff: wait longer each time
            wait_time = (attempt + 1) ** 2  # 1s, 4s, 9s, 16s
            print(f"Attempt {attempt + 1} failed, waiting {wait_time}s...")
            time.sleep(wait_time)
```

### Response Caching

Implement caching to reduce API calls:

```python
from functools import lru_cache
from brahmastra.llm_provider import openai_llm

@lru_cache(maxsize=100)
def cached_llm_call(prompt, model, temperature):
    return openai_llm(
        prompt=prompt,
        model=model,
        api_key="...",
        temperature=temperature
    )

# First call: hits API
response1 = cached_llm_call("What is Python?", "gpt-4", 0.0)

# Second call: returns cached result
response2 = cached_llm_call("What is Python?", "gpt-4", 0.0)
```

---

## ✅ Best Practices

### 1. Use Environment Variables for API Keys
```python
# ✅ Good
import os
api_key = os.environ.get("OPENAI_API_KEY")
response = openai_llm(prompt="...", model="gpt-4", api_key=api_key)

# ❌ Bad (hardcoded key)
response = openai_llm(prompt="...", model="gpt-4", api_key="sk-hardcoded-key")
```

### 2. Always Handle Exceptions
```python
# ✅ Good
try:
    response = openai_llm(prompt="...", model="gpt-4")
except OpenAILLMError as e:
    print(f"Error: {e}")
    response = "Error occurred"

# ❌ Bad (no error handling)
response = openai_llm(prompt="...", model="gpt-4")
```

### 3. Validate Inputs Before Calling
```python
# ✅ Good
def safe_llm_call(prompt, model="gpt-4"):
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    
    return openai_llm(prompt=prompt, model=model)

# ❌ Bad (no validation)
response = openai_llm(prompt="", model="gpt-4")  # Will raise ValueError
```

### 4. Use Appropriate Temperature
```python
# ✅ Good: Low temperature for factual tasks
code_review = openai_llm(prompt="Review this code...", model="gpt-4", temperature=0.2)

# ✅ Good: High temperature for creative tasks
story = openai_llm(prompt="Write a story...", model="gpt-4", temperature=0.9)

# ❌ Bad: High temperature for factual tasks
math_answer = openai_llm(prompt="What is 2+2?", model="gpt-4", temperature=1.5)
```

### 5. Set Reasonable Timeouts
```python
# ✅ Good: Adjust timeout based on expected response time
quick_response = openai_llm(prompt="Hi", model="gpt-4", timeout=10.0)
long_response = openai_llm(prompt="Write an essay...", model="gpt-4", timeout=60.0)

# ❌ Bad: Very short timeout for long tasks
essay = openai_llm(prompt="Write 2000 words...", model="gpt-4", timeout=5.0)
```

### 6. Choose the Right Model
```python
# ✅ Good: Use cheaper models for simple tasks
simple = openai_llm(prompt="Translate to French: Hello", model="gpt-3.5-turbo")

# ✅ Good: Use powerful models for complex tasks
complex = openai_llm(prompt="Analyze this legal document...", model="gpt-4")

# ❌ Bad: Using expensive models for simple tasks
greeting = openai_llm(prompt="Say hi", model="gpt-4")  # Waste of money
```

### 7. Implement Fallback Logic
```python
# ✅ Good: Try multiple providers
def get_response(prompt):
    providers = [
        ("Groq", lambda: groq_llm(prompt, model="llama3-70b-8192", api_key="...")),
        ("OpenAI", lambda: openai_llm(prompt, model="gpt-3.5-turbo", api_key="...")),
    ]
    
    for name, func in providers:
        try:
            return func()
        except Exception as e:
            print(f"{name} failed: {e}")
            continue
    
    raise Exception("All providers failed")
```

### 8. Log API Usage (if needed)
```python
# ✅ Good: Track usage for monitoring
import logging

def tracked_llm_call(prompt, model="gpt-4"):
    logging.info(f"Calling {model} with prompt length: {len(prompt)}")
    start = time.time()
    
    try:
        response = openai_llm(prompt=prompt, model=model)
        duration = time.time() - start
        logging.info(f"Success in {duration:.2f}s, response length: {len(response)}")
        return response
    except Exception as e:
        logging.error(f"Failed: {e}")
        raise
```

---

## 🔧 Troubleshooting

### Issue: "No API key provided"
**Solution:**
```bash
# Set environment variable
export OPENAI_API_KEY="sk-..."

# Or pass directly
response = openai_llm(prompt="...", model="gpt-4", api_key="sk-...")
```

### Issue: "Package not installed"
**Solution:**
```bash
# Install the specific provider
pip install openai          # For OpenAI
pip install google-generativeai  # For Google
pip install anthropic       # For Anthropic
pip install groq            # For Groq
pip install ollama          # For Ollama
```

### Issue: "Request failed after N attempts"
**Solutions:**
1. Check internet connection
2. Verify API key is valid
3. Check provider status page
4. Increase `max_retries` and `timeout`
5. Try a different provider

### Issue: Ollama "Connection refused"
**Solution:**
```bash
# 1. Check if Ollama is running
curl http://localhost:11434

# 2. Start Ollama server
ollama serve

# 3. Verify model is pulled
ollama list
ollama pull llama2  # If not listed
```

### Issue: Google "No text could be extracted"
**Solution:**
This can happen due to:
- Content safety filters blocking response
- SDK version compatibility issues

```python
# Try with different parameters
response = google_llm(
    prompt="...",
    model="gemini-1.5-pro",  # Try different model
    temperature=0.5,  # Lower temperature
    api_key="..."
)
```

### Issue: Rate Limiting
**Solution:**
```python
# Implement rate limiting
import time
from brahmastra.llm_provider import openai_llm

def rate_limited_call(prompt, calls_per_minute=10):
    sleep_time = 60 / calls_per_minute
    response = openai_llm(prompt=prompt, model="gpt-4")
    time.sleep(sleep_time)
    return response
```

### Issue: Timeout Errors
**Solution:**
```python
# Increase timeout for long responses
response = openai_llm(
    prompt="Write a 5000-word essay...",
    model="gpt-4",
    timeout=120.0,  # 2 minutes
    max_tokens=4000
)
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding a New Provider

1. Create `NewProvider_llm.py` following the existing pattern
2. Implement exception classes
3. Implement function-based API
4. Implement class-based API
5. Add comprehensive documentation
6. Update `__init__.py`
7. Update this README

### Code Style Guidelines

- Follow PEP 8
- Use type hints for all parameters
- Add comprehensive docstrings
- Include error handling
- Add inline comments for complex logic
- Use meaningful variable names

### Testing

```bash
# Run tests (when available)
pytest tests/

# Test specific provider
python -c "from brahmastra.llm_provider import openai_llm; print(openai_llm('test', 'gpt-3.5-turbo'))"
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Support

- **Documentation**: [Full API Docs](https://github.com/devxJitin/Brahmastra)
- **Issues**: [GitHub Issues](https://github.com/devxJitin/Brahmastra/issues)
- **Email**: support@brahmastra.com
- **Discord**: [Join our community](https://discord.gg/Brahmastra)

---

## 🙏 Acknowledgments

Built with ❤️ by **devxJitin**

Special thanks to:
- OpenAI for GPT models
- Google for Gemini
- Anthropic for Claude
- Groq for ultra-fast inference
- Ollama for local LLM hosting

---

## 📊 Version History

### v1.0.0 (Current)
- ✅ Initial release
- ✅ Support for 5 major providers
- ✅ Dual API interfaces (function & class)
- ✅ Comprehensive error handling
- ✅ Automatic retry logic
- ✅ Full documentation

---

**Made with 🚀 by devxJitin | Part of the Brahmastra Framework**
