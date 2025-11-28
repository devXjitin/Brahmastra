"""
Speech Recognition Tool with Gemini Enhancement
================================================

Real-time speech-to-text with LLM accuracy enhancement.

Example:
    >>> from brahmastra.prebuild_autonomous_tool.speech_recognition_tool import SpeechRecognitionTool
    >>> 
    >>> speech = SpeechRecognitionTool(gemini_api_key="your_api_key")
    >>> agent.add_tools(speech)
"""

from .base import SpeechRecognitionTool, create_speech_recognition_tool, RECOGNIZED_TEXT

__all__ = [
    "SpeechRecognitionTool",
    "create_speech_recognition_tool",
    "RECOGNIZED_TEXT"
]
