import os
import cv2
import speech_recognition as sr
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
from langdetect import detect
from playsound import playsound  # Windows native player
from dotenv import load_dotenv
import requests
import json

# Load variables from .env file
load_dotenv()

# --- SETUP ---
# Get the API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please create a .env file and add GEMINI_API_KEY.")

genai.configure(api_key=API_KEY)
recognizer = sr.Recognizer()

# --- Audio Cue Functions ---
def play_sound(sound_file):
    """Helper function to play a sound file from the 'sounds' directory."""
    sound_path = os.path.join("sounds", sound_file)
    try:
        if os.path.exists(sound_path):
            playsound(sound_path, block=False) # block=False lets the sound play in the background
        else:
            # This print is for the developer.
            print(f"[Audio Cue] Hint: Add a sound file at '{sound_path}'")
    except Exception as e:
        print(f"❌ Error playing sound {sound_path}: {e}")

def play_thinking_sound():
    """Plays a sound to indicate the AI is processing."""
    # Recommendation: A short, subtle processing sound (e.g., thinking.mp3)
    play_sound("thinking.mp3") 

def play_success_sound():
    """Plays a sound to indicate a successful response."""
    # Recommendation: A clear, positive chime (e.g., success.mp3)
    play_sound("success.mp3")

def play_warning_sound():
    """Plays a sound to indicate a safety warning."""
    # Recommendation: A sharp, urgent but not alarming beep (e.g., warning.mp3)
    play_sound("warning.mp3")

def speak(text):
    if not text: return

    # Play a warning sound if the response contains a safety alert.
    text_lower = text.lower()
    if text_lower.startswith("warning:") or text_lower.startswith("caution:") or text_lower.startswith("danger:"):
        play_warning_sound()

    print(f"🗣️ Speaking: {text}")
    
    try:
        # Detect Language
        lang = detect(text) if len(text.split()) > 1 else 'en'
        
        # Generate MP3
        filename = "response.mp3"
        # Remove old file if it exists (Windows locks files sometimes)
        if os.path.exists(filename):
            os.remove(filename)
            
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        
        # Play Sound (Native Windows)
        playsound(filename)
        
    except Exception as e:
        print(f"❌ Audio Error: {e}")

def listen_to_user():
    print("👂 Listening... (Speak now!)")
    try:
        with sr.Microphone() as source: 
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("   -> Speak NOW!")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            
            # List of languages to try in order
            languages = ["ar-MA", "fr-FR", "en-US"]
            
            for lang in languages:
                try:
                    text = recognizer.recognize_google(audio, language=lang)
                    print(f"✅ Detected ({lang}): {text}")
                    return text
                except sr.UnknownValueError:
                    # This means speech was heard but not understood
                    continue # Try the next language
                except sr.RequestError as e:
                    # This means there was an issue with the API request
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    return "" # Stop trying
            
            # If the loop finishes without returning, nothing was recognized
            print("Could not understand audio")
            return ""

    except Exception as e:
        print(f"⚠️ Mic Error: {e}")
        return ""

def analyze_image(image_path, user_question, mode="general", history=None):
    """
    Analyzes an image by sending a request to the local Flask API server.

    Args:
        image_path: The path to the image file (only for the first turn).
        user_question: The question from the user.
        mode: The analysis mode (e.g., "general", "street", "kitchen").
        history: The conversation history object from a previous turn.

    Returns:
        A tuple of (text_response, updated_history).
    """
    API_URL = "http://127.0.0.1:5000/analyze"
    print(f"📡 Sending request to local API in '{mode}' mode...")

    payload = {
        "question": user_question,
        "mode": mode
    }
    files = {}

    try:
        # If there's no history, it's a new conversation with an image.
        if not history:
            if not image_path or not os.path.exists(image_path):
                raise ValueError("Image path is required for a new conversation.")
            # The 'files' dictionary is used by requests to send multipart/form-data
            files["image"] = (image_path, open(image_path, "rb"), "image/jpeg")
        # If there is history, it's a follow-up. Send the history as a JSON string.
        else:
            payload["history"] = json.dumps(history)

        response = requests.post(API_URL, data=payload, files=files)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)

        # Close the file if it was opened
        if "image" in files:
            files["image"][1].close()

        # Parse the JSON response from the server
        data = response.json()
        return data.get("result", "No result found."), data.get("history", [])

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        error_message = "Could not connect to the local API server. Is mobile.py running?"
        speak(error_message)
        return error_message, history # Return old history on error
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}", history

def main():
    # Windows Camera Index:
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("❌ Camera Error: Could not open video stream.")
        return

    # --- State Management ---
    modes = {'1': "general", '2': "street", '3': "kitchen"}
    current_mode_key = '1'
    chat_history = None # To store the conversation history for the current image

    print("--- GEMINI VISION WINDOWS READY ---")
    speak("System Ready.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # --- UI Display ---
        mode_name = modes[current_mode_key].upper()
        cv2.putText(frame, f"MODE: {mode_name} (1,2,3)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SPACE: New Question", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "F: Follow-up Question", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Q: Quit", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Gemini Vision", frame)
        
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        
        # --- Mode Selection ---
        key_char = chr(key)
        if key_char in modes:
            if current_mode_key != key_char:
                current_mode_key = key_char
                new_mode_name = modes[current_mode_key]
                print(f"🔄 Mode changed to: {new_mode_name}")
                speak(f"Mode changed to {new_mode_name}")
                chat_history = None # Reset history on mode change
                speak("History cleared.")

        elif key == 32: # SPACE BAR for new question
            print("\n--- NEW QUESTION ---")
            chat_history = None 
            cv2.imwrite("capture.jpg", frame)
            question = listen_to_user()
            
            if question:
                play_thinking_sound()
                result, history = analyze_image("capture.jpg", question, mode=modes[current_mode_key])
                play_success_sound()
                chat_history = history 
                print(f"🤖 Gemini: {result}")
                speak(result)
            else:
                print("🤷 No question heard.")
                speak("I didn't hear a question.")

        elif key == ord('f'): # 'F' for follow-up
            if not chat_history:
                print("❌ No active conversation. Press SPACE to start a new one.")
                speak("Please start a new conversation first by pressing the space bar.")
                continue
            
            print("\n--- FOLLOW-UP QUESTION ---")
            question = listen_to_user()

            if question:
                play_thinking_sound()
                result, history = analyze_image(None, question, mode=modes[current_mode_key], history=chat_history)
                play_success_sound()
                chat_history = history 
                print(f"🤖 Gemini: {result}")
                speak(result)
            else:
                print("🤷 No question heard for follow-up.")
                speak("I didn't hear a follow-up question.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
