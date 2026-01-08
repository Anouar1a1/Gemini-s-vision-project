import os
from PIL import Image
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
import io

# --- SETUP ---
load_dotenv()
# Get the API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Please create a .env file and add GEMINI_API_KEY.")

genai.configure(api_key=API_KEY)

# --- FLASK APP ---
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """
    A simple welcome message to confirm the server is running.
    """
    return jsonify({
        "message": "Welcome to the Gemini's Vision API!",
        "usage": "Send a POST request to /analyze with an 'image' file and a 'question' form field."
    })

def analyze_image(image_bytes, user_question, mode="general", history=None):
    """
    Analyzes an image using a conversational chat session with Gemini.

    Args:
        image_bytes: The image data in bytes (only for the first turn).
        user_question: The question from the user.
        mode: The analysis mode (e.g., "general", "street", "kitchen").
        history: The conversation history from previous turns.

    Returns:
        A tuple of (text_response, updated_history).
    """
    print(f"🧠 Gemini is thinking in '{mode}' mode...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        chat = model.start_chat(history=history or [])

        # If this is the first question, we build the detailed system prompt.
        # Otherwise, for follow-ups, we just send the new question.
        if not history:
            if not image_bytes:
                raise ValueError("Image bytes are required for a new conversation.")
            
            img = Image.open(io.BytesIO(image_bytes))
            
            prompts = {
                "street": """IMPORTANT: You are a safety assistant for a visually impaired user who is outdoors.
1.  **Safety First:** Prioritize identifying immediate dangers like moving vehicles, cyclists, traffic lights, crosswalks, uneven pavement, and obstacles on the path.
2.  **Warn Clearly:** If a danger is detected, begin with a clear warning (e.g., \"Warning: Car approaching from the left.\").
3.  **Answer the Question:** After warnings, answer the user's question in the context of being on a street.
""",
                "kitchen": """IMPORTANT: You are a safety assistant for a visually impaired user in a kitchen.
1.  **Safety First:** Prioritize identifying immediate dangers like hot surfaces (stoves, ovens), sharp objects (knives), open flames, and spills on the floor.
2.  **Warn Clearly:** If a danger is detected, begin with a clear warning (e.g., \"Caution: A sharp knife is on the counter to your right.\").
3.  **Answer the Question:** After warnings, answer the user's question in the context of a kitchen environment.
""",
                "general": """IMPORTANT: Your primary role is to be a safety assistant for a visually impaired user.
1.  **Safety First:** Meticulously analyze the image for any potential hazards. This includes, but is not limited to: obstacles on the ground, stairs, or sudden drops.
2.  **Warn Clearly:** If a danger is detected, begin your response with a clear, direct warning.
3.  **Answer the Question:** After issuing any necessary warnings, then proceed to answer the user's question.
"""
            base_prompt = prompts.get(mode, prompts["general"])
            final_prompt = f"{base_prompt}\nUser's question: \"{user_question}\""
            response = chat.send_message([final_prompt, img])
        else:
            # For follow-up questions, the image is already in the history.
            response = chat.send_message(user_question)
        
        # The history includes the model's response, ready for the next turn.
        return response.text, chat.history

    except Exception as e:
        print(f"❌ GEMINI ERROR: {e}")
        # Return a text error and empty history
        return "I could not connect to Gemini or process the image.", []

@app.route('/analyze', methods=['POST'])
def handle_analysis():
    """
    Flask endpoint to handle image analysis requests, supporting conversations.
    Expects a POST request with:
    - 'question': The user's question.
    - 'mode' (optional): The analysis mode.
    - EITHER 'image' (for a new conversation) 
    - OR 'history' (for a follow-up, as a JSON string).
    """
    # --- Input Validation ---
    if 'question' not in request.form:
        return jsonify({"error": "No question provided."}), 400

    question = request.form['question']
    mode = request.form.get('mode', 'general')
    history_str = request.form.get('history')
    history = json.loads(history_str) if history_str else None

    try:
        # Case 1: New conversation (no history provided)
        if not history:
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided for a new conversation."}), 400
            
            image_file = request.files['image']
            image_bytes = image_file.stream.read()
            
            result, updated_history = analyze_image(image_bytes, question, mode, history=None)
            return jsonify({"result": result, "history": updated_history})

        # Case 2: Follow-up conversation (history provided)
        else:
            # Image is not needed as it's in the history
            result, updated_history = analyze_image(None, question, mode, history=history)
            return jsonify({"result": result, "history": updated_history})
        
    except Exception as e:
        print(f"❌ SERVER ERROR: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

def main():
    """
    Runs the Flask application.
    The server will be accessible on your local network.
    """
    print("--- GEMINI VISION API SERVER ---")
    print("--- Ready to receive requests ---")
    # To run on your local network, use host='0.0.0.0'
    # The app will be available at http://<your-ip-address>:5000
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
