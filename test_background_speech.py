"""
Speech Recognition Tool - Background Listening Test
===================================================

Test the background autonomous speech recognition feature.
"""

from brahmastra.prebuild_autonomous_tool import SpeechRecognitionTool, get_recognized_text
from brahmastra.llm_provider import GoogleLLM
import time

# Create LLM
llm = GoogleLLM(api_key="AIzaSyCsJ5cmln2krNCgB3kq7rjmeHfzfA4zU20", model="gemini-2.0-flash-lite")

# Create speech tool with auto-start
print("🎤 JIM Virtual Assistant - Speech Recognition Active")
print("=" * 60)
print("Speak naturally in any language...")
print("Press Ctrl+C to stop\n")

speech = SpeechRecognitionTool(llm=llm, use_llm=False, auto_start=True, pause_threshold=1)

try:
    last_text = ""
    while True:
        
        # Use helper function to get current recognized text
        current_text = get_recognized_text()
        if current_text and current_text != last_text:
            print(f"✓ {current_text}")
            last_text = current_text
            
            # Exit if user says "stop"
            if "stop" in current_text.lower():
                break

except KeyboardInterrupt:
    print("\n\n🛑 Stopping...")
finally:
    speech.stop_background_listening()
    print("✅ Done!")
