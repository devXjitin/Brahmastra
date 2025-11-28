# 🔱 Brahmastra

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Version-1.0.0-orange.svg" alt="Version">
  <img src="https://img.shields.io/badge/Author-devxJitin-purple.svg" alt="Author">
</p>

<p align="center">
  <strong>A powerful AI Agent framework for building intelligent, multi-modal AI agents with ease.</strong>
</p>

---

## 🚀 Overview

**Brahmastra** is a comprehensive Python framework designed to simplify the creation of AI agents. It provides:

- 🤖 **Multiple Agent Types** - ReAct, Multi-Tool, Tool-Calling, and Reasoning agents
- 🔧 **Pre-built Tools** - YouTube, Wikipedia, Speech Recognition, PowerShell execution
- 🧠 **LLM Providers** - Google Gemini, OpenAI, Anthropic, Groq, Ollama
- ⚡ **Parallel Execution** - Execute multiple tools simultaneously
- 🎯 **Easy Integration** - Simple decorator-based tool creation

---

## 📦 Installation

```bash
pip install brahmastra
```

### Dependencies

```bash
# Core (included)
pip install brahmastra

# For specific LLM providers
pip install google-generativeai  # Google Gemini
pip install openai               # OpenAI
pip install anthropic            # Anthropic Claude
pip install groq                 # Groq
pip install ollama               # Ollama (local)

# For specific tools
pip install wikipedia            # Wikipedia tool
pip install google-api-python-client  # YouTube API
pip install youtube-transcript-api    # YouTube transcripts
pip install SpeechRecognition pyaudio # Speech recognition
```

---

## 🏃 Quick Start

### Basic Example

```python
from brahmastra.llm_provider import GoogleLLM
from brahmastra.llm_agent import Create_MultiToolAgent
from brahmastra.prebuild_tool import WikipediaSearchTool, YoutubeSearchTool
from brahmastra.core import tool

# Create LLM
llm = GoogleLLM(model="gemini-2.0-flash")

# Create tools
wikipedia = WikipediaSearchTool()
youtube = YoutubeSearchTool(api_key="your-youtube-api-key")

# Custom tool using decorator
@tool
def calculator(expression: str) -> str:
    """Performs mathematical calculations."""
    return str(eval(expression))

# Create agent
agent = Create_MultiToolAgent(llm=llm, verbose=True)
agent.add_tools(wikipedia, youtube, calculator)

# Run query
result = agent.invoke("What is the capital of France and calculate 25 * 4?")
print(result)
```

### Advanced Example with Autonomous Tools

```python
from brahmastra.llm_provider import GoogleLLM
from brahmastra.llm_agent import Create_MultiToolAgent
from brahmastra.prebuild_autonomous_tool import PSExecTool, PSGenTool, PyRunTool

# Create LLM
llm = GoogleLLM(model="gemini-2.0-flash")

# Create autonomous tools
psexec = PSExecTool()           # Execute PowerShell commands
psgen = PSGenTool(llm=llm)      # Generate PowerShell from natural language
pyrun = PyRunTool()             # Execute Python code

# Create agent
agent = Create_MultiToolAgent(llm=llm, verbose=True)
agent.add_tools(psexec, psgen, pyrun)

# Run system tasks
result = agent.invoke("Check system information and list all running processes")
```

---

## 📁 Project Structure

```
brahmastra/
├── core/                    # Core components (Tool, decorators)
├── llm_provider/            # LLM integrations (Google, OpenAI, etc.)
├── llm_agent/               # Agent implementations
│   ├── REACT_AGENT/         # ReAct reasoning agent
│   ├── MULTI_REASONING_TOOL_AGENT/  # Multi-tool parallel agent
│   ├── TOOL_CALLING_AGENT/  # Simple tool calling agent
│   └── REASONING_AGENT/     # Pure reasoning agent
├── prebuild_tool/           # Pre-built tools
│   ├── wikipedia_tool/      # Wikipedia search
│   ├── YoutubeSearchTool/   # YouTube search
│   └── YoutubeTranscriptTool/  # YouTube transcripts
├── prebuild_autonomous_tool/  # Autonomous system tools
│   ├── speech_recognition_tool/  # Speech-to-text
│   ├── PSExec_tool/         # PowerShell execution
│   ├── PSGen_tool/          # PowerShell generation
│   └── PyRun_tool/          # Python execution
└── utils/                   # Utilities (logger, executor)
```

---

## 🤖 Available Agents

| Agent | Description | Best For |
|-------|-------------|----------|
| `Create_MultiToolAgent` | Executes multiple tools in parallel | Complex queries requiring multiple tools |
| `Create_ReAct_Agent` | Reasoning + Acting loop | Step-by-step problem solving |
| `Create_ToolCalling_Agent` | Simple tool invocation | Single tool operations |
| `Create_Reasoning_Agent` | Pure reasoning without tools | Complex logical reasoning |

---

## 🔧 Available Tools

### Pre-built Tools
- **WikipediaSearchTool** - Search and retrieve Wikipedia articles
- **YoutubeSearchTool** - Search YouTube videos via API
- **YoutubeTranscriptTool** - Get video transcripts/captions

### Autonomous Tools
- **SpeechRecognitionTool** - Real-time speech-to-text
- **PSExecTool** - Execute PowerShell commands
- **PSGenTool** - Generate PowerShell from natural language
- **PyRunTool** - Execute Python code dynamically

---

## 🧠 Supported LLM Providers

| Provider | Models | Class |
|----------|--------|-------|
| Google | Gemini 2.0, 1.5 Pro/Flash | `GoogleLLM` |
| OpenAI | GPT-4, GPT-3.5 | `OpenAILLM` |
| Anthropic | Claude 3 Opus/Sonnet | `AnthropicLLM` |
| Groq | Llama, Mixtral | `GroqLLM` |
| Ollama | Local models | `OllamaLLM` |

---

## 🛠️ Creating Custom Tools

```python
from brahmastra.core import tool, Tool

# Method 1: Using decorator (recommended)
@tool
def my_custom_tool(query: str, limit: int = 10) -> str:
    """Description of what the tool does."""
    # Your implementation
    return result

# Method 2: Using Tool class directly
my_tool = Tool(
    name="my_tool",
    description="What this tool does",
    function=my_function,
    parameters={
        "query": {"type": "str", "description": "Search query", "required": True}
    }
)

# Add to agent
agent.add_tools(my_custom_tool, my_tool)
```

---

## 📚 Documentation

- [Core Module](brahmastra/core/README.md) - Tool system and decorators
- [LLM Providers](brahmastra/llm_provider/README.md) - LLM integrations
- [LLM Agents](brahmastra/llm_agent/README.md) - Agent implementations
- [Pre-built Tools](brahmastra/prebuild_tool/README.md) - Ready-to-use tools
- [Autonomous Tools](brahmastra/prebuild_autonomous_tool/README.md) - System tools

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**devxJitin**

---

<p align="center">
  <strong>Built with ❤️ for the AI community</strong>
</p>
