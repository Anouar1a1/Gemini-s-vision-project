import requests
import json
import os

# The address of our local Flask API server.
# Make sure mobile.py is running in a separate terminal for this to work.
API_URL = "http://127.0.0.1:5000/analyze"

# The image captured by main.py. We'll use it as our sample image.
# In a real mobile app, this would come from the phone's camera.
IMAGE_PATH = "capture.jpg"

def run_phone_simulation():
    """
    Simulates a mobile app client making requests to the API server.
    """
    print("--- Phone App Simulation ---")

    # --- Check if the sample image exists ---
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Sample image '{IMAGE_PATH}' not found.")
        print("Please run main.py and press SPACE to capture an image first.")
        return

    # --- 1. First Turn (New Conversation with an Image) ---
    print("\n1. Asking a new question about the image...")
    
    question1 = "What is in this image?"
    mode1 = "general"
    payload1 = {"question": question1, "mode": mode1}
    
    try:
        with open(IMAGE_PATH, "rb") as image_file:
            files1 = {"image": (IMAGE_PATH, image_file, "image/jpeg")}
            
            # This is where a real mobile app would make its network request.
            response1 = requests.post(API_URL, data=payload1, files=files1)
            response1.raise_for_status()

        data1 = response1.json()
        result1 = data1.get("result")
        history1 = data1.get("history") # Save the history for the follow-up

        print(f"\n🤖 Server Response: '{result1}'")
        print("✅ First turn successful. History has been saved.")

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        print("Could not connect to the local API server. Is mobile.py running?")
        return

    # --- 2. Second Turn (Follow-up Question with History) ---
    if not history1:
        print("\nCould not proceed to follow-up, history is empty.")
        return

    print("\n----------------------------------")
    print("2. Asking a follow-up question...")

    question2 = "What color is the largest object?"
    # In a follow-up, we don't need to send the image again, just the history.
    payload2 = {
        "question": question2,
        "mode": mode1, # Usually the mode would be the same
        "history": json.dumps(history1) # The history must be sent as a JSON string
    }

    try:
        # This is the second network request.
        response2 = requests.post(API_URL, data=payload2)
        response2.raise_for_status()
        
        data2 = response2.json()
        result2 = data2.get("result")
        
        print(f"\n🤖 Server Response: '{result2}'")
        print("✅ Follow-up successful.")

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Error: {e}")
        return

    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    run_phone_simulation()
