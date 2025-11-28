"""
Speech Recognition Tool - Background Speech Recognition Service
================================================================

A professional-grade background service for real-time speech recognition.
Uses speech_recognition library with optional LLM enhancement for accuracy.

Features:
- Background continuous speech recognition
- Optional LLM integration for accuracy enhancement (OpenAI, Gemini, Claude, etc.)
- Auto-stop on configurable silence detection
- Global variable storage for recognized text
- Thread-safe operation
- High accuracy with LLM correction

Requires:
- speech_recognition (pip install SpeechRecognition)
- pyaudio (pip install pyaudio)
- Optional: Any LLM provider (OpenAI, Gemini, Claude, Groq, Ollama)

Example Usage:
    >>> from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
    >>> from brahmastra.llm_provider import GoogleLLM
    >>> 
    >>> # Without LLM (faster)
    >>> speech = SpeechRecognitionTool()
    >>> speech.start_background_listening()
    >>> 
    >>> # Check recognized text
    >>> text = speech.get_last_text()
    >>> # Or use helper function
    >>> text = get_recognized_text()
    >>> 
    >>> speech.stop_background_listening()
    >>>
    >>> # With LLM enhancement (more accurate)
    >>> llm = GoogleLLM(api_key="your_key", model="gemini-2.0-flash-lite")
    >>> speech = SpeechRecognitionTool(llm=llm, use_llm=True)
    >>> speech.start_background_listening()
"""

from typing import Optional, Dict, Any
import threading
import time

# Global variable to store the final recognized text
RECOGNIZED_TEXT = ""
_recognition_lock = threading.Lock()


class SpeechRecognitionTool:
    """
    Background Speech Recognition Service with Optional LLM Enhancement.
    
    This service provides continuous speech recognition in a background thread
    with optional LLM-based accuracy enhancement.
    
    Features:
    - Background continuous speech recognition
    - Optional LLM integration for text accuracy improvement
    - Configurable silence detection (default 1.5 seconds)
    - Thread-safe global variable storage
    - Real-time processing without queues
    - Preserves original language (no translation)
    
    Args:
        llm: Optional LLM instance from brahmastra.llm_provider
        language: Language code for speech recognition (default: "en-US")
        pause_threshold: Seconds of silence before stopping (default: 1.5)
        energy_threshold: Microphone sensitivity (default: 300)
        use_llm: Enable LLM enhancement (default: True if llm provided)
        auto_start: Auto-start background listening (default: False)
    
    Example:
        >>> from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
        >>> 
        >>> # Without LLM (faster)
        >>> speech = SpeechRecognitionTool()
        >>> speech.start_background_listening()
        >>> text = get_recognized_text()
        >>> 
        >>> # With LLM enhancement
        >>> from brahmastra.llm_provider import GoogleLLM
        >>> llm = GoogleLLM(api_key="key", model="gemini-2.0-flash-lite")
        >>> speech = SpeechRecognitionTool(llm=llm, use_llm=True)
        >>> speech.start_background_listening()
    """
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        language: str = "en-US",
        pause_threshold: float = 1.5,
        energy_threshold: int = 50,
        use_llm: bool = True,
        auto_start: bool = False
    ):
        """Initialize the Speech Recognition Tool."""
        self.llm = llm
        self.language = language
        self.pause_threshold = pause_threshold
        self.energy_threshold = energy_threshold
        self.use_llm = use_llm and llm is not None
        
        # Background listening state
        self._listening_thread = None
        self._is_listening = False
        self._stop_listening = threading.Event()
        
        # Statistics
        self.stats = {
            "total_recognitions": 0,
            "successful_recognitions": 0,
            "llm_enhancements": 0,
            "errors": 0
        }
        
        # Validate dependencies
        self._validate_dependencies()
        
        # Auto-start if requested
        if auto_start:
            self.start_background_listening()
    
    def _validate_dependencies(self):
        """Validate that required packages are installed."""
        try:
            import speech_recognition
        except ImportError:
            raise ImportError(
                "speech_recognition is required. Install with: pip install SpeechRecognition pyaudio"
            )
    
    def _enhance_with_llm(self, text: str) -> str:
        """
        Enhance recognized text using LLM for improved accuracy.
        Preserves original language (no translation).
        
        Args:
            text: Raw recognized text
            
        Returns:
            Enhanced text (or original if LLM fails)
        """
        if not self.use_llm or not text or not self.llm:
            return text
        
        try:
            # Create concise enhancement prompt for faster processing
            prompt = f"""You are a speech understanding assistant.

Your job is to interpret what the speaker most likely intended to say, even if the transcription is incomplete, noisy, or partially incorrect.

RULES:
1. Use context, tone, and wording to infer meaning.
2. Keep the SAME language as the input (Hindi, English, or Hinglish mix – preserve it exactly).
3. Preserve Hindi or Hinglish words exactly as spoken – do not replace or translate.
4. Fix grammar, punctuation, and abbreviations while maintaining the original language.
5. Rephrase incomplete or unclear phrases into coherent sentences in the SAME language.
6. Replace "gym"/"gem" with "JIM" only when referring to the assistant.
7. Preserve the user’s tone (casual, formal, emotional) while improving clarity.
8. If meaning cannot be reasonably inferred, output only the portion that is clear.
9. Output only the final cleaned sentence, with no notes, explanations, or prefixes.

Input: {text}
Output:
"""
            
            # Get LLM response using generate_response method
            if hasattr(self.llm, 'generate_response'):
                enhanced_text = self.llm.generate_response(prompt)
            elif hasattr(self.llm, '__call__'):
                enhanced_text = self.llm(prompt)
            else:
                raise AttributeError("LLM must have generate_response method or be callable")
            
            enhanced_text = enhanced_text.strip()
            
            # Safety check: If LLM made it much longer or empty, use original
            if not enhanced_text or len(enhanced_text) > len(text) * 2:
                return text
            
            self.stats["llm_enhancements"] += 1
            return enhanced_text
            
        except Exception as e:
            # If LLM fails, return original text
            return text
    
    def _background_listener(self):
        """
        Background thread that continuously listens for speech.
        Processes audio in real-time and updates global RECOGNIZED_TEXT variable.
        """
        global RECOGNIZED_TEXT
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = self.pause_threshold  # Pause after speech
        recognizer.energy_threshold = self.energy_threshold
        recognizer.dynamic_energy_threshold = True  # Auto-adjust to ambient noise
        recognizer.phrase_threshold = 0.3  # Min seconds of speaking before it's considered a phrase
        recognizer.non_speaking_duration = 0.5  # Seconds of non-speaking before a phrase is complete
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while not self._stop_listening.is_set():
                try:
                    # Listen for speech
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
                    
                    # Process immediately (REAL-TIME - no queue!)
                    try:
                        recognized_text = recognizer.recognize_google(audio, language=self.language)  # type: ignore
                        
                        # Enhance with LLM if enabled (silently - no display)
                        if self.use_llm and recognized_text:
                            final_text = self._enhance_with_llm(recognized_text)
                        else:
                            final_text = recognized_text
                        
                        # Update global variable immediately
                        with _recognition_lock:
                            RECOGNIZED_TEXT = final_text
                        
                        self.stats["total_recognitions"] += 1
                        self.stats["successful_recognitions"] += 1
                        
                    except sr.UnknownValueError:
                        pass  # Could not understand audio
                    except sr.RequestError:
                        self.stats["errors"] += 1
                
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    if not self._stop_listening.is_set():
                        self.stats["errors"] += 1
                    time.sleep(0.1)
    
    def start_background_listening(self):
        """
        Start continuous background speech recognition.
        
        Returns:
            Status message
        """
        if self._is_listening:
            return "Already listening in background"
        
        self._stop_listening.clear()
        self._is_listening = True
        
        # Start single listener thread (captures AND processes - REAL-TIME!)
        self._listening_thread = threading.Thread(target=self._background_listener, daemon=True)
        self._listening_thread.start()
        
        return "Started real-time background listening"
    
    def stop_background_listening(self):
        """
        Stop background speech recognition.
        
        Returns:
            Status message
        """
        if not self._is_listening:
            return "Not currently listening"
        
        self._stop_listening.set()
        self._is_listening = False
        
        if self._listening_thread:
            self._listening_thread.join(timeout=2)
            
        return "Stopped background listening"
    
    def get_last_text(self) -> str:
        """
        Get the last recognized text from global variable.
        
        Returns:
            Last recognized text
        """
        global RECOGNIZED_TEXT
        with _recognition_lock:
            return RECOGNIZED_TEXT
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()
    
    def clear_last_text(self):
        """Clear the global recognized text variable."""
        global RECOGNIZED_TEXT
        with _recognition_lock:
            RECOGNIZED_TEXT = ""
        return "Last recognized text cleared"


def create_speech_recognition_tool(
    llm: Optional[Any] = None,
    language: str = "en-US",
    pause_threshold: float = 1.5,
    use_llm: bool = True,
    auto_start: bool = False
) -> SpeechRecognitionTool:
    """
    Create a speech recognition service with optional LLM enhancement.
    
    Args:
        llm: Optional LLM instance from brahmastra.llm_provider
        language: Language code (default: "en-US")
        pause_threshold: Silence duration before stopping (default: 1.5s)
        use_llm: Enable LLM enhancement (default: True)
        auto_start: Auto-start background listening (default: False)
    
    Returns:
        SpeechRecognitionTool instance
    
    Example:
        >>> from brahmastra.llm_provider import GoogleLLM
        >>> llm = GoogleLLM(api_key="key", model="gemini-2.0-flash-lite")
        >>> speech = create_speech_recognition_tool(llm=llm)
        >>> speech.start_background_listening()
    """
    return SpeechRecognitionTool(
        llm=llm,
        language=language,
        pause_threshold=pause_threshold,
        use_llm=use_llm,
        auto_start=auto_start
    )


__all__ = [
    "SpeechRecognitionTool",
    "create_speech_recognition_tool",
    "RECOGNIZED_TEXT"
]
