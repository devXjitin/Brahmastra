# Speech Recognition Tool

## Overview

The Speech Recognition Tool is a professional-grade background service that provides continuous, real-time speech recognition with optional LLM-based text enhancement. Unlike traditional speech-to-text tools that require manual triggering, this service runs autonomously in a background thread, continuously listening and transcribing speech into a globally accessible variable.

**Key Characteristics:**

- **Background Service**: Runs independently in a daemon thread
- **Autonomous Operation**: No manual intervention required after starting
- **Real-time Processing**: Immediate transcription without queuing delays
- **Thread-Safe**: Safe for concurrent access from multiple threads
- **LLM-Enhanced**: Optional AI-powered text correction and improvement
- **Language Agnostic**: Preserves original language without translation

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [LLM Enhancement](#llm-enhancement)
- [Global Variable Access](#global-variable-access)
- [Performance Tuning](#performance-tuning)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [License](#license)

## Core Concepts

### What is a Background Speech Service?

This tool operates as a **background service** rather than a traditional function-call tool:

1. **Continuous Operation**: Once started, it runs indefinitely until explicitly stopped
2. **Non-Blocking**: Doesn't block your main application thread
3. **Global State**: Stores recognized text in a thread-safe global variable
4. **Event-Driven**: Automatically triggers transcription on speech detection

### How It Differs from Traditional Speech Recognition

| Traditional Approach | This Tool |
|---------------------|-----------|
| Call function → wait → get result | Start once → continuously updates global variable |
| Blocking operation | Non-blocking background thread |
| Manual triggering required | Automatic speech detection |
| One-time transcription | Continuous listening |
| Function return value | Global variable access |

### Use Cases

**Perfect For:**

- Voice-controlled applications
- Real-time transcription systems
- Voice assistants and chatbots
- Accessibility tools
- Hands-free data entry
- Voice command interfaces
- Live captioning systems

**Not Suitable For:**

- One-time audio file transcription (use direct API instead)
- Batch processing of audio files
- Non-real-time applications

## Architecture

### System Design

```design
┌─────────────────────────────────────────────────────────┐
│                    Main Application                     │
│  ┌────────────────────────────────────────────────┐     │
│  │  Your Code                                     │     │
│  │  • Reads RECOGNIZED_TEXT                       │     │
│  │  • Processes user commands                     │     │
│  │  • Non-blocking operation                      │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↕ (Thread-safe access)
┌─────────────────────────────────────────────────────────┐
│            Background Speech Listener Thread            │
│  ┌────────────────────────────────────────────────┐     │
│  │  1. Capture Audio (PyAudio)                    │     │
│  │       ↓                                        │     │
│  │  2. Detect Speech (VAD - Voice Activity)       │     │
│  │       ↓                                        │     │
│  │  3. Detect Silence (Configurable threshold)    │     │
│  │       ↓                                        │     │
│  │  4. Transcribe (Google Speech API)             │     │
│  │       ↓                                        │     │
│  │  5. LLM Enhancement (Optional)                 │     │
│  │       ↓                                        │     │
│  │  6. Update RECOGNIZED_TEXT (Thread-safe)       │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↕ (Audio input)
                    ┌─────────────┐
                    │  Microphone │
                    └─────────────┘
```

### Threading Model

- **Main Thread**: Your application logic
- **Listener Thread**: Background daemon thread that captures and processes audio
- **Thread Synchronization**: Uses `threading.Lock` for safe global variable access
- **Daemon Mode**: Automatically terminates when main program exits

### Data Flow

1. **Audio Capture**: Continuous microphone input via PyAudio
2. **Voice Activity Detection**: Automatically detects when speech starts
3. **Silence Detection**: Monitors for pause (default: 1.5 seconds)
4. **Transcription**: Sends audio to Google Speech Recognition API
5. **LLM Enhancement** (Optional): Improves accuracy via LLM
6. **Storage**: Updates thread-safe global variable `RECOGNIZED_TEXT`
7. **Access**: Application reads variable anytime via `get_last_text()` or `get_recognized_text()`

## Features

### Core Features

- **Background Listening**: Continuous speech recognition in background thread
- **Real-time Processing**: Immediate transcription without queuing delays  
- **Auto-stop Detection**: Configurable silence detection (default: 1.5 seconds)
- **Global Variable Storage**: Thread-safe storage in `RECOGNIZED_TEXT`
- **Language Preservation**: Maintains original language (no automatic translation)
- **Ambient Noise Adaptation**: Automatically adjusts to environment

### Optional Features

- **LLM Enhancement**: AI-powered text correction and improvement
- **Multi-LLM Support**: Works with OpenAI, Gemini, Claude, Groq, Ollama
- **Statistics Tracking**: Monitor recognitions, errors, and enhancements
- **Auto-start**: Begin listening on instantiation
- **Multi-language Support**: 50+ languages supported

### Technical Features

- **Thread-safe Operations**: Safe concurrent access
- **Error Recovery**: Graceful handling of recognition failures
- **Dynamic Energy Threshold**: Auto-adjusts to ambient noise
- **Configurable Parameters**: Customize sensitivity and timing
- **Memory Efficient**: Lightweight background operation

## Installation

```bash
pip install SpeechRecognition pyaudio
```

Plus any LLM provider you want to use:

```bash
# For Gemini
pip install google-generativeai

# For OpenAI
pip install openai

# For Claude
pip install anthropic

# For Groq
pip install groq

# For Ollama (local)
pip install ollama
```

### Platform-Specific Notes

**Windows:**

```bash
pip install pyaudio
```

**macOS:**

```bash
brew install portaudio
pip install pyaudio
```

**Linux:**

```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## Quick Start

### Without LLM (Fastest)

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text

# Create and start service
speech = SpeechRecognitionTool()
speech.start_background_listening()

# Access recognized text anytime
text = get_recognized_text()
print(text)

# Stop when done
speech.stop_background_listening()
```

### With LLM Enhancement (More Accurate)

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool
from brahmastra.llm_provider import GoogleLLM

# Create LLM
llm = GoogleLLM(api_key="your_key", model="gemini-2.0-flash-lite")

# Create service with LLM
speech = SpeechRecognitionTool(llm=llm, use_llm=True)
speech.start_background_listening()

# Get LLM-enhanced text
text = speech.get_last_text()
```

## Detailed Usage

### Basic Configuration

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool

speech = SpeechRecognitionTool(
    llm=None,                    # Optional: LLM instance for enhancement
    language="en-US",            # Language code for recognition
    pause_threshold=1.5,         # Seconds of silence to detect end of speech
    energy_threshold=300,        # Microphone sensitivity (lower = more sensitive)
    use_llm=True,               # Enable LLM enhancement (requires llm)
    auto_start=False            # Auto-start background listening
)
```

### Multi-LLM Support

This tool works with any LLM provider from the Brahmastra framework:

```python
from brahmastra.llm_provider import (
    GoogleLLM,      # Google Gemini
    OpenAILLM,      # OpenAI GPT
    AnthropicLLM,   # Anthropic Claude
    GroqLLM,        # Groq (fastest)
    OllamaLLM       # Ollama (local, offline)
)

# Example with Groq (recommended for speed)
llm = GroqLLM(api_key="your_key", model="llama3-70b-8192")
speech = SpeechRecognitionTool(llm=llm)

# Example with Ollama (no API key needed)
llm = OllamaLLM(model="llama2")
speech = SpeechRecognitionTool(llm=llm)
```

### Multi-Language Support

```python
# Hindi
speech_hi = SpeechRecognitionTool(language="hi-IN")

# Spanish  
speech_es = SpeechRecognitionTool(language="es-ES")

# French
speech_fr = SpeechRecognitionTool(language="fr-FR")

# Hinglish (Hindi + English mix) - Use Hindi language code
speech_hinglish = SpeechRecognitionTool(language="hi-IN")
```

### Auto-Start Configuration

```python
# Start listening immediately upon creation
speech = SpeechRecognitionTool(
    language="en-US",
    auto_start=True  # Begins listening automatically
)

# Already listening! No need to call start_background_listening()
text = speech.get_last_text()
```

## Configuration

### Configuration Parameters Explained

#### `llm` (Any, Optional)

LLM instance for text enhancement. Pass any Brahmastra LLM provider.

- **Default**: `None` (no enhancement)
- **Options**: GoogleLLM, OpenAILLM, AnthropicLLM, GroqLLM, OllamaLLM
- **Performance Impact**: Adds 100-500ms latency per recognition
- **Recommendation**: Use GroqLLM for best speed/accuracy balance

```python
from brahmastra.llm_provider import GroqLLM
llm = GroqLLM(api_key="key", model="llama3-70b-8192")
```

#### `language` (str)

Language code for speech recognition. Follows ISO 639-1 + ISO 3166-1 format.

- **Default**: `"en-US"`
- **Examples**: `"hi-IN"` (Hindi), `"es-ES"` (Spanish), `"fr-FR"` (French)
- **50+ languages supported** by Google Speech API
- **Mixed languages**: Use primary language code (e.g., `"hi-IN"` for Hinglish)

#### `pause_threshold` (float)

Seconds of silence before considering speech complete.

- **Default**: `1.5`
- **Range**: `0.5` - `3.0`
- **Lower values**: Faster response, may cut off sentences
- **Higher values**: More complete sentences, slower response
- **Recommendation**: `1.5` for conversations, `0.8` for commands

```python
# Fast commands
speech = SpeechRecognitionTool(pause_threshold=0.8)

# Long sentences
speech = SpeechRecognitionTool(pause_threshold=2.5)
```

#### `energy_threshold` (int)

Microphone sensitivity level. Higher = less sensitive.

- **Default**: `300`
- **Range**: `100` - `4000`
- **Quiet environment**: `100-300`
- **Noisy environment**: `500-1000`
- **Very noisy**: `1000-4000`
- **Auto-adjustment**: Dynamically adapts to ambient noise

```python
# Quiet room
speech = SpeechRecognitionTool(energy_threshold=200)

# Noisy office
speech = SpeechRecognitionTool(energy_threshold=800)
```

#### `use_llm` (bool)

Enable or disable LLM enhancement.

- **Default**: `True` (if llm provided)
- **When True**: Sends text to LLM for correction
- **When False**: Uses raw Google Speech API output
- **Performance**: False = 10x faster, True = more accurate

```python
# Maximum speed (no LLM)
speech = SpeechRecognitionTool(llm=llm, use_llm=False)

# Maximum accuracy (with LLM)
speech = SpeechRecognitionTool(llm=llm, use_llm=True)
```

#### `auto_start` (bool)

Automatically start background listening on instantiation.

- **Default**: `False`
- **When True**: Starts listening immediately  
- **When False**: Must call `start_background_listening()` manually

```python
# Auto-start
speech = SpeechRecognitionTool(auto_start=True)
# Already listening!

# Manual start
speech = SpeechRecognitionTool(auto_start=False)
speech.start_background_listening()  # Must call this
```

## API Reference

### Class: `SpeechRecognitionTool`

Main class for background speech recognition service.

#### Methods

##### `start_background_listening()`

Start continuous background speech recognition in a daemon thread.

**Parameters**: None

**Returns**: `str` - Status message ("Started real-time background listening")

**Thread-Safe**: Yes

**Example**:

```python
speech = SpeechRecognitionTool()
status = speech.start_background_listening()
print(status)  # "Started real-time background listening"
```

##### `stop_background_listening()`

Stop the background speech recognition thread.

**Parameters**: None

**Returns**: `str` - Status message ("Stopped background listening" or "Not currently listening")

**Thread-Safe**: Yes

**Cleanup**: Waits up to 2 seconds for thread to terminate

**Example**:

```python
status = speech.stop_background_listening()
print(status)  # "Stopped background listening"
```

##### `get_last_text()`

Get the last recognized text from the thread-safe global variable.

**Parameters**: None

**Returns**: `str` - Last recognized text (empty string if none)

**Thread-Safe**: Yes

**Note**: Returns current value without clearing it

**Example**:

```python
text = speech.get_last_text()
if text:
    print(f"Recognized: {text}")
```

##### `get_stats()`

Get usage statistics dictionary.

**Parameters**: None

**Returns**: `dict` - Statistics dictionary with keys:

- `total_recognitions` (int): Total recognition attempts
- `successful_recognitions` (int): Successful recognitions
- `llm_enhancements` (int): Number of LLM enhancements applied
- `errors` (int): Number of errors encountered

**Thread-Safe**: Yes

**Example**:

```python
stats = speech.get_stats()
print(f"Success rate: {stats['successful_recognitions']}/{stats['total_recognitions']}")
print(f"LLM enhancements: {stats['llm_enhancements']}")
print(f"Errors: {stats['errors']}")
```

##### `clear_last_text()`

Clear the global recognized text variable.

**Parameters**: None

**Returns**: `str` - Status message ("Last recognized text cleared")

**Thread-Safe**: Yes

**Use Case**: Clear text after processing to detect new input

**Example**:

```python
text = speech.get_last_text()
process(text)
speech.clear_last_text()  # Ready for next input
```

### Helper Function: `get_recognized_text()`

Global helper function to access recognized text.

**Import**:

```python
from brahmastra.prebuild_autonomous_tool import get_recognized_text
```

**Parameters**: None

**Returns**: `str` - Current value of `RECOGNIZED_TEXT` global variable

**Thread-Safe**: Yes

**Advantage**: Simpler than accessing module attribute directly

**Example**:

```python
from brahmastra.prebuild_autonomous_tool import get_recognized_text

while True:
    text = get_recognized_text()
    if text:
        print(f"User said: {text}")
    time.sleep(0.5)
```

### Factory Function: `create_speech_recognition_tool()`

Factory function to create SpeechRecognitionTool instance.

**Import**:

```python
from brahmastra.prebuild_autonomous_tool import create_speech_recognition_tool
```

**Parameters**:

- `llm` (Any, optional): LLM instance
- `language` (str): Language code (default: "en-US")
- `pause_threshold` (float): Silence duration (default: 1.5)
- `use_llm` (bool): Enable LLM (default: True)
- `auto_start` (bool): Auto-start listening (default: False)

**Returns**: `SpeechRecognitionTool` instance

**Example**:

```python
speech = create_speech_recognition_tool(
    llm=my_llm,
    language="hi-IN",
    auto_start=True
)
```

## LLM Enhancement

### How LLM Enhancement Works

When enabled, the LLM enhancement feature:

1. **Receives raw text** from Google Speech API
2. **Sends to LLM** with specialized prompt
3. **LLM improves**:
   - Fixes grammar and punctuation
   - Corrects misheard words based on context
   - Maintains original language (no translation)
   - Preserves user's intent and tone
4. **Returns enhanced text** to global variable
5. **Fallback**: If LLM fails, uses original text

### LLM Enhancement Prompt

The tool uses this prompt strategy:

```text
You are a speech understanding assistant.

Your job is to interpret what the speaker most likely intended to say,
even if the transcription is incomplete, noisy, or partially incorrect.

RULES:
1. Use context, tone, and wording to infer meaning.
2. Keep the SAME language as the input (preserve it exactly).
3. Preserve Hindi or Hinglish words exactly as spoken.
4. Fix grammar, punctuation, and abbreviations.
5. Rephrase incomplete phrases into coherent sentences.
6. Replace "gym"/"gem" with "JIM" only when referring to assistant.
7. Preserve user's tone while improving clarity.
8. If meaning cannot be inferred, output only clear portion.
9. Output only the final cleaned sentence, no explanations.

Input: {recognized_text}
Output:
```

### Performance Considerations

| Mode | Speed | Accuracy | Use Case |
|------|-------|----------|----------|
| **No LLM** | ~100ms | Good | Commands, fast response needed |
| **LLM** | ~300-800ms | Excellent | Conversations, accuracy critical |
| **LLM (Groq)** | ~200-400ms | Excellent | Best balance |
| **LLM (Local)** | ~500-2000ms | Good | Offline, privacy critical |

### Choosing an LLM Provider

#### Groq (Recommended for Most Cases)

```python
from brahmastra.llm_provider import GroqLLM
llm = GroqLLM(api_key="key", model="llama3-70b-8192")
speech = SpeechRecognitionTool(llm=llm)
```

- **Speed**: Fastest cloud LLM (~200-400ms)
- **Accuracy**: Excellent
- **Cost**: Very low
- **Best for**: Production applications

#### Google Gemini**

```python
from brahmastra.llm_provider import GoogleLLM
llm = GoogleLLM(api_key="key", model="gemini-2.0-flash-lite")
speech = SpeechRecognitionTool(llm=llm)
```

- **Speed**: Fast (~300-500ms)
- **Accuracy**: Excellent
- **Multi-language**: Best for Hindi/Hinglish
- **Best for**: Multi-language applications

#### Ollama (Local)

```python
from brahmastra.llm_provider import OllamaLLM
llm = OllamaLLM(model="llama2")
speech = SpeechRecognitionTool(llm=llm)
```

- **Speed**: Slower (~500-2000ms, depends on hardware)
- **Accuracy**: Good
- **Offline**: Works without internet
- **Privacy**: Data never leaves your machine
- **Best for**: Privacy-sensitive applications

## Global Variable Access

### The `RECOGNIZED_TEXT` Global Variable

The tool stores recognized text in a module-level global variable:

```python
from brahmastra.prebuild_autonomous_tool.speech_recognition_tool import RECOGNIZED_TEXT
```

**Characteristics**:

- **Thread-Safe**: Protected by `threading.Lock`
- **Mutable**: Updates continuously as speech is recognized
- **Persistent**: Retains value until cleared or overwritten
- **Global Scope**: Accessible from any module

### Access Methods

**Method 1: Direct Access** (Not Recommended)

```python
from brahmastra.prebuild_autonomous_tool.speech_recognition_tool import RECOGNIZED_TEXT

# This won't work as expected due to Python's import behavior
print(RECOGNIZED_TEXT)  # Shows value at import time, not current
```

**Method 2: Via get_last_text()** (Recommended)

```python
speech = SpeechRecognitionTool()
speech.start_background_listening()

text = speech.get_last_text()  # Gets current value
```

**Method 3: Via Helper Function** (Most Convenient)

```python
from brahmastra.prebuild_autonomous_tool import get_recognized_text

text = get_recognized_text()  # Gets current value
```

### Why Global Variable?

**Advantages**:

- **Simple Access**: Read from anywhere in your code
- **Non-Blocking**: Main thread doesn't wait for recognition
- **Real-Time**: Always contains latest recognized text
- **Multiple Readers**: Multiple threads can read simultaneously

**Alternative Approaches** (Not Used):

- ❌ Callback functions: More complex integration
- ❌ Queue: Adds latency and complexity
- ❌ Return values: Requires blocking calls

## Performance Tuning

### Optimization Strategies

#### For Maximum Speed

```python
speech = SpeechRecognitionTool(
    llm=None,                # No LLM processing
    use_llm=False,           # Disable enhancement
    pause_threshold=0.8,     # Quick response
    energy_threshold=400     # Reduce false positives
)
```

**Expected latency**: ~100-200ms per recognition

#### For Maximum Accuracy

```python
from brahmastra.llm_provider import GroqLLM

llm = GroqLLM(api_key="key", model="llama3-70b-8192")
speech = SpeechRecognitionTool(
    llm=llm,
    use_llm=True,            # Enable enhancement
    pause_threshold=1.5,     # Complete sentences
    energy_threshold=300     # Capture all speech
)
```

**Expected latency**: ~400-600ms per recognition

#### Balanced Configuration

```python
from brahmastra.llm_provider import GroqLLM

llm = GroqLLM(api_key="key", model="llama3-8b-8192")  # Smaller model
speech = SpeechRecognitionTool(
    llm=llm,
    use_llm=True,
    pause_threshold=1.2,
    energy_threshold=350
)
```

**Expected latency**: ~250-400ms per recognition

### Performance Metrics

| Component | Latency | Notes |
|-----------|---------|-------|
| Voice Activity Detection | ~10ms | Continuous monitoring |
| Silence Detection | 0.8-2.5s | Configurable (pause_threshold) |
| Audio Capture | ~20-50ms | Depends on phrase length |
| Google Speech API | ~100-300ms | Network dependent |
| LLM Enhancement (Groq) | ~200-400ms | Fastest cloud option |
| LLM Enhancement (Gemini) | ~300-500ms | Good balance |
| LLM Enhancement (Ollama) | ~500-2000ms | Hardware dependent |
| **Total (No LLM)** | **~150-400ms** | **Fast mode** |
| **Total (With LLM)** | **~400-900ms** | **Accurate mode** |

### Troubleshooting Performance

**Problem**: Recognition is too slow

**Solutions**:

1. Disable LLM: `use_llm=False`
2. Use Groq instead of other LLMs
3. Reduce `pause_threshold` to 0.8-1.0
4. Check network latency to Google Speech API
5. Use smaller LLM model

**Problem**: Too many false positives

**Solutions**:

1. Increase `energy_threshold` (try 500-800)
2. Increase `pause_threshold` to 1.5-2.0
3. Reduce ambient noise in environment

**Problem**: Misses speech

**Solutions**:

1. Decrease `energy_threshold` (try 100-250)
2. Speak louder or closer to microphone
3. Check microphone settings in OS

## Examples

### Example 1: Simple Voice Command System

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
import time

# Create and start
speech = SpeechRecognitionTool(pause_threshold=0.8)  # Quick response
speech.start_background_listening()

print("Listening for commands...")

while True:
    text = get_recognized_text()
    
    if text:
        text_lower = text.lower()
        
        if "hello" in text_lower:
            print("Hello! How can I help you?")
        elif "goodbye" in text_lower or "exit" in text_lower:
            print("Goodbye!")
            break
        elif "time" in text_lower:
            print(f"Current time is: {time.strftime('%H:%M:%S')}")
        else:
            print(f"You said: {text}")
        
        speech.clear_last_text()  # Clear for next command
    
    time.sleep(0.3)

speech.stop_background_listening()
```

### Example 2: Voice-Controlled Chatbot

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool
from brahmastra.llm_provider import OpenAILLM
import time

# Create speech recognition with LLM
speech_llm = GroqLLM(api_key="speech_key", model="llama3-70b-8192")
speech = SpeechRecognitionTool(llm=speech_llm, use_llm=True)
speech.start_background_listening()

# Create chatbot LLM
chatbot_llm = OpenAILLM(api_key="openai_key", model="gpt-4")

print("Voice chatbot ready! Speak now...")

while True:
    user_input = speech.get_last_text()
    
    if user_input:
        print(f"You: {user_input}")
        
        # Send to chatbot
        response = chatbot_llm.generate_response(user_input)
        print(f"Bot: {response}")
        
        speech.clear_last_text()
        
        if "goodbye" in user_input.lower():
            break
    
    time.sleep(0.5)

speech.stop_background_listening()
```

### Example 3: Multi-Language Support

```python
from brahmastra.prebuild_autonomous_tool import create_speech_recognition_tool
from brahmastra.llm_provider import GoogleLLM

# Gemini works best with multiple languages
llm = GoogleLLM(api_key="key", model="gemini-2.0-flash-lite")

# Hindi/Hinglish recognition
speech_hi = create_speech_recognition_tool(
    llm=llm,
    language="hi-IN",
    auto_start=True
)

print("बोलिए... (Speak in Hindi or Hinglish)")

import time
for _ in range(10):
    text = speech_hi.get_last_text()
    if text:
        print(f"Recognized: {text}")
        speech_hi.clear_last_text()
    time.sleep(1)

speech_hi.stop_background_listening()
```

### Example 4: Statistics Monitoring

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool
import time

speech = SpeechRecognitionTool()
speech.start_background_listening()

# Run for 60 seconds
start_time = time.time()
while time.time() - start_time < 60:
    text = speech.get_last_text()
    if text:
        print(f"Recognized: {text}")
        speech.clear_last_text()
    time.sleep(0.5)

# Show statistics
stats = speech.get_stats()
print("\n=== Statistics ===")
print(f"Total recognitions: {stats['total_recognitions']}")
print(f"Successful: {stats['successful_recognitions']}")
print(f"LLM enhancements: {stats['llm_enhancements']}")
print(f"Errors: {stats['errors']}")
print(f"Success rate: {stats['successful_recognitions']/max(stats['total_recognitions'],1)*100:.1f}%")

speech.stop_background_listening()
```

### Example 5: Continuous Transcription

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool
import time

speech = SpeechRecognitionTool(
    pause_threshold=2.0,  # Longer sentences
    auto_start=True
)

transcript = []

print("Start speaking... (Press Ctrl+C to stop)")

try:
    while True:
        text = speech.get_last_text()
        if text and (not transcript or text != transcript[-1]):
            transcript.append(text)
            print(f"[{len(transcript)}] {text}")
            speech.clear_last_text()
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\n\n=== Full Transcript ===")
    for i, line in enumerate(transcript, 1):
        print(f"{i}. {line}")

speech.stop_background_listening()
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Microphone Not Detected

**Symptoms**: `OSError: No Default Input Device Available`

**Solutions**:

1. Check microphone is connected
2. Set microphone as default in OS settings
3. Grant microphone permissions to Python
4. Test microphone with other applications
5. Install/reinstall PyAudio: `pip install --upgrade pyaudio`

#### Issue: Poor Recognition Accuracy

**Symptoms**: Incorrect transcriptions, missed words

**Solutions**:

1. Enable LLM enhancement: `use_llm=True`
2. Speak clearly and at moderate pace
3. Reduce background noise
4. Adjust microphone position (6-12 inches from mouth)
5. Increase `energy_threshold` if too many false positives
6. Decrease `energy_threshold` if missing speech
7. Use correct language code for your language

#### Issue: High Latency / Slow Response

**Symptoms**: Delay between speech and recognition

**Solutions**:

1. Disable LLM: `use_llm=False` (10x faster)
2. Use Groq LLM if accuracy needed (fastest cloud LLM)
3. Reduce `pause_threshold` to 0.8-1.0
4. Check internet connection speed
5. Use local Ollama for offline operation

#### Issue: Cuts Off Sentences

**Symptoms**: Recognition stops mid-sentence

**Solutions**:

1. Increase `pause_threshold` to 2.0-2.5
2. Speak without long pauses
3. Reduce `energy_threshold` if too sensitive

#### Issue: Python Crashes on Start

**Symptoms**: Segmentation fault or crash when starting

**Solutions**:

1. Reinstall PyAudio: `pip uninstall pyaudio && pip install pyaudio`
2. On Linux: `sudo apt-get install portaudio19-dev python3-pyaudio`
3. On macOS: `brew install portaudio`
4. Check microphone permissions
5. Try different Python version (3.8-3.11 recommended)

#### Issue: Network Errors

**Symptoms**: `RequestError: recognition connection failed`

**Solutions**:

1. Check internet connection
2. Google Speech API may be temporarily down
3. Firewall may be blocking requests
4. Use VPN if geo-restricted

#### Issue: Global Variable Not Updating

**Symptoms**: `get_last_text()` returns empty or old value

**Solutions**:

1. Ensure `start_background_listening()` was called
2. Check if service is still running
3. Verify microphone is working
4. Speak clearly and wait for `pause_threshold` duration
5. Check `get_stats()` for errors

#### Issue: Memory Usage Increases Over Time

**Symptoms**: High memory usage after long runtime

**Solutions**:

1. This is normal for long-running services
2. Restart service periodically: `stop_background_listening()` → `start_background_listening()`
3. Call `clear_last_text()` regularly
4. Limit LLM usage for very high-frequency applications

## Best Practices

### Do's

✅ **Use `get_recognized_text()` helper** instead of direct RECOGNIZED_TEXT access

```python
from brahmastra.prebuild_autonomous_tool import get_recognized_text
text = get_recognized_text()  # Correct
```

✅ **Clear text after processing** to detect new input

```python
text = speech.get_last_text()
if text:
    process(text)
    speech.clear_last_text()  # Clear for next input
```

✅ **Stop service when done** to free resources

```python
speech.stop_background_listening()
```

✅ **Handle exceptions** for production applications

```python
try:
    speech = SpeechRecognitionTool()
    speech.start_background_listening()
except ImportError:
    print("Please install: pip install SpeechRecognition pyaudio")
except OSError:
    print("Microphone not found. Please connect a microphone.")
```

✅ **Use appropriate pause_threshold** for your use case

- Commands: `0.8-1.0` seconds
- Conversations: `1.5-2.0` seconds
- Long sentences: `2.0-2.5` seconds

✅ **Monitor statistics** in production

```python
stats = speech.get_stats()
if stats['errors'] > stats['successful_recognitions'] * 0.1:
    logger.warning("High error rate in speech recognition")
```

### Don'ts

❌ **Don't access RECOGNIZED_TEXT directly**

```python
# Wrong - won't get updated value
from brahmastra.prebuild_autonomous_tool.speech_recognition_tool import RECOGNIZED_TEXT
print(RECOGNIZED_TEXT)  # Incorrect

# Correct
text = get_recognized_text()
```

❌ **Don't run multiple instances** on same microphone

```python
# Wrong - conflicts
speech1 = SpeechRecognitionTool()
speech2 = SpeechRecognitionTool()
speech1.start_background_listening()
speech2.start_background_listening()  # ERROR: Microphone already in use
```

❌ **Don't use in CPU-intensive tight loops**

```python
# Wrong - too frequent
while True:
    text = get_recognized_text()  # No sleep!
    
# Correct - add sleep
while True:
    text = get_recognized_text()
    time.sleep(0.3)  # Give CPU time for other tasks
```

❌ **Don't forget to handle empty strings**

```python
# Wrong
text = get_recognized_text()
process_command(text)  # May process empty string

# Correct
text = get_recognized_text()
if text:  # Check if not empty
    process_command(text)
```

❌ **Don't use for file transcription**

```python
# Wrong use case
with open("audio.wav", "rb") as f:
    # This tool is for real-time microphone, not files
    
# Correct approach for files:
# Use google.cloud.speech or other file-based APIs
```

### Production Recommendations

#### **Logging**: Add logging for debugging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

speech = SpeechRecognitionTool()
speech.start_background_listening()
logger.info("Speech recognition service started")
```

#### **Error Recovery**: Implement retry logic

```python
def start_with_retry(speech, max_retries=3):
    for attempt in range(max_retries):
        try:
            return speech.start_background_listening()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### **Graceful Shutdown**: Handle signals

```python
import signal
import sys

def signal_handler(sig, frame):
    print("\nStopping speech recognition...")
    speech.stop_background_listening()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

#### **Configuration Files**: Externalize configuration

```python
import json

with open("config.json") as f:
    config = json.load(f)

speech = SpeechRecognitionTool(
    language=config["language"],
    pause_threshold=config["pause_threshold"],
    energy_threshold=config["energy_threshold"]
)
```

#### **Health Checks**: Monitor service health

```python
def is_healthy(speech):
    stats = speech.get_stats()
    error_rate = stats['errors'] / max(stats['total_recognitions'], 1)
    return error_rate < 0.2  # Less than 20% error rate

if not is_healthy(speech):
    logger.warning("Restarting speech service due to high error rate")
    speech.stop_background_listening()
    speech.start_background_listening()
```

## Supported Languages

### Complete Language List

| Language | Code | LLM Support |
|----------|------|-------------|
| Afrikaans | `af-ZA` | Good |
| Arabic | `ar-SA` | Excellent |
| Bengali | `bn-IN` | Good |
| Chinese (Simplified) | `zh-CN` | Excellent |
| Chinese (Traditional) | `zh-TW` | Excellent |
| Czech | `cs-CZ` | Good |
| Danish | `da-DK` | Good |
| Dutch | `nl-NL` | Excellent |
| English (US) | `en-US` | Excellent |
| English (UK) | `en-GB` | Excellent |
| English (Australia) | `en-AU` | Excellent |
| English (India) | `en-IN` | Excellent |
| Finnish | `fi-FI` | Good |
| French | `fr-FR` | Excellent |
| German | `de-DE` | Excellent |
| Greek | `el-GR` | Good |
| Hindi | `hi-IN` | Excellent |
| Hungarian | `hu-HU` | Good |
| Indonesian | `id-ID` | Good |
| Italian | `it-IT` | Excellent |
| Japanese | `ja-JP` | Excellent |
| Korean | `ko-KR` | Excellent |
| Malay | `ms-MY` | Good |
| Norwegian | `no-NO` | Good |
| Polish | `pl-PL` | Good |
| Portuguese (Brazil) | `pt-BR` | Excellent |
| Portuguese (Portugal) | `pt-PT` | Excellent |
| Romanian | `ro-RO` | Good |
| Russian | `ru-RU` | Excellent |
| Spanish (Spain) | `es-ES` | Excellent |
| Spanish (Mexico) | `es-MX` | Excellent |
| Swedish | `sv-SE` | Good |
| Tamil | `ta-IN` | Good |
| Telugu | `te-IN` | Good |
| Thai | `th-TH` | Good |
| Turkish | `tr-TR` | Good |
| Ukrainian | `uk-UA` | Good |
| Vietnamese | `vi-VN` | Good |

**LLM Support Legend**:

- **Excellent**: Gemini/GPT handles very well
- **Good**: Supported but may need fine-tuning

### Mixed Languages (Code-Switching)

The tool handles mixed languages (e.g., Hinglish, Spanglish):

```python
# Hinglish (Hindi + English)
speech = SpeechRecognitionTool(language="hi-IN")
# Recognizes: "Main market jaa raha hoon to buy vegetables"

# Spanglish (Spanish + English)
speech = SpeechRecognitionTool(language="es-MX")
# Recognizes: "Voy al store para comprar milk"
```

**Recommendation**: Use the primary language code, LLM will preserve the mix.

## License

MIT License

Copyright (c) 2025 Brahmastra Framework

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

### **Part of the Brahmastra AI Agent Framework**

For more information, visit: [Brahmastra Documentation](https://github.com/devxJitin/brahmastra)

```python
from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool
from brahmastra.llm_provider import GoogleLLM  # or OpenAILLM, AnthropicLLM, etc.

# Create LLM instance
llm = GoogleLLM(api_key="your_api_key", model="gemini-2.0-flash-lite")

# Create tool with LLM enhancement
speech = SpeechRecognitionTool(
    llm=llm,
    language="en-US",
    pause_threshold=1.5,
    use_llm=True
)

# Start background listening
speech.start_background_listening()

# Get enhanced text
text = speech.get_last_text()

# Stop listening
speech.stop_background_listening()
```

### Using Different LLMs

```python
# With OpenAI GPT
from brahmastra.llm_provider import OpenAILLM
llm = OpenAILLM(api_key="your_key", model="gpt-3.5-turbo")
speech = SpeechRecognitionTool(llm=llm)

# With Anthropic Claude
from brahmastra.llm_provider import AnthropicLLM
llm = AnthropicLLM(api_key="your_key", model="claude-3-sonnet-20240229")
speech = SpeechRecognitionTool(llm=llm)

# With Groq (fast inference)
from brahmastra.llm_provider import GroqLLM
llm = GroqLLM(api_key="your_key", model="llama3-70b-8192")
speech = SpeechRecognitionTool(llm=llm)

# With Ollama (local, no API key needed)
from brahmastra.llm_provider import OllamaLLM
llm = OllamaLLM(model="llama2")
speech = SpeechRecognitionTool(llm=llm)
```

### Accessing Global Variable

```python
# Direct access to global variable
from brahmastra.prebuild_autonomous_tool.speech_recognition_tool import RECOGNIZED_TEXT
print(RECOGNIZED_TEXT)

# Or use helper function
from brahmastra.prebuild_autonomous_tool import get_recognized_text
text = get_recognized_text()
```

### Configuration Options

```python
speech = SpeechRecognitionTool(
    llm=None,                    # Optional: LLM instance for enhancement
    language="en-US",            # Language code
    pause_threshold=1.5,         # Seconds of silence to detect end of speech
    energy_threshold=300,        # Microphone sensitivity
    use_llm=True,               # Enable LLM enhancement (if llm provided)
    auto_start=False            # Auto-start background listening
)
```
