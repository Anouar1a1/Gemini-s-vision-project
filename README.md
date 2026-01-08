# Gemini Vision Project

A visual assistant application designed for visually impaired users. This tool leverages Google's Gemini 3.0 Flash model to analyze real-time video feed from a camera, identify objects, and detect potential hazards in various environments (General, Street, Kitchen). It provides audio feedback and supports voice interaction for follow-up questions.

## Features

-   **Real-time Image Analysis**: Captures images from a webcam and uses Gemini 3.0 Flash to understand the scene.
-   **Hazard Detection**: Specialized prompts for "Street" and "Kitchen" modes to prioritize safety warnings (e.g., traffic, hot stoves).
-   **Voice Interaction**: Users can ask questions via microphone, and the system responds with synthesized speech (Text-to-Speech).
-   **Follow-up Questions**: Supports conversational context, allowing users to ask more about the previously analyzed image.
-   **Multiple Modes**:
    -   **General**: Standard scene analysis.
    -   **Street**: Focuses on outdoor hazards like cars, crosswalks, and obstacles.
    -   **Kitchen**: Focuses on indoor hazards like sharp objects, heat sources, and spills.

## Architecture

The project consists of two main components:
1.  **Backend (`mobile.py` / `mobile-git-version.py`)**: A Flask API server that handles communication with the Google Gemini API. It processes image and text inputs and manages conversation history.
2.  **Frontend/Client (`main.py` / `main-git-version.py`)**: A desktop application (using OpenCV) that provides the user interface, captures video/audio, and communicates with the backend server.

## Prerequisites

-   Python 3.8+
-   A webcam
-   A microphone
-   [Google Gemini API Key](https://aistudio.google.com/)

## Installation

1.  **Clone the repository** (if applicable) or download the source code.

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the API Key**:
    -   Create a file named `.env` in the project root.
    -   Add your Gemini API key to it:
        ```env
        GEMINI_API_KEY=your_actual_api_key_here
        ```

## Usage

This project provides two sets of files. The `git-version` files are configured to be safe for version control (GitHub) as they strictly require environment variables.

### Option 1: Running the Standard Version
1.  **Start the Backend Server**:
    Open a terminal and run:
    ```bash
    python mobile.py
    ```
    This will start the Flask server on `http://127.0.0.1:5000`.

2.  **Start the Client Application**:
    Open a second terminal and run:
    ```bash
    python main.py
    ```

### Option 2: Running the Git-Safe Version
Use these files if you are sharing your code or want to ensure strict adherence to environment variable security.

1.  **Start the Git Backend Server**:
    Open a terminal and run:
    ```bash
    python mobile-git-version.py
    ```

2.  **Start the Git Client Application**:
    Open a second terminal and run:
    ```bash
    python main-git-version.py
    ```

### Controls (Both Versions)
-   **SPACE**: Capture an image and ask a question (speak into the microphone).
-   **F**: Ask a follow-up question about the last captured image.
-   **1**: Switch to "General" mode.
-   **2**: Switch to "Street" mode.
-   **3**: Switch to "Kitchen" mode.
-   **Q**: Quit the application.

## File Structure

-   `main.py` / `main-git-version.py`: The main client application with OpenCV UI and audio logic.
-   `mobile.py` / `mobile-git-version.py`: The Flask API server acting as the bridge to Gemini.
-   `phone_app_client.py`: A simulation script to test the API without the GUI.
-   `requirements.txt`: Python dependencies.
-   `.env`: Configuration file for the API key (exclude from version control).
-   `sounds/`: Directory containing audio cues (success, warning, thinking).

## Troubleshooting

-   **Camera Error**: Ensure no other application is using the webcam.
-   **Mic Error**: Check your microphone settings in Windows.
-   **API Error**: Verify your API key in `.env` and ensure the backend server is running.
