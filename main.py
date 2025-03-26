from google import genai
from google.genai import types
from PIL import Image
import pyautogui
import pygetwindow as gw
import win32gui
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Initialize the GenAI client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def capture_screen():
    try:
        pyautogui.hotkey("alt", "tab")
        hwnd = win32gui.GetForegroundWindow()
        target_window_title = win32gui.GetWindowText(hwnd)
        window = gw.getWindowsWithTitle(target_window_title)
        
        if window:
            window = window[0]
            screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            screenshot.save("picture.png")
            st.success("Screenshot captured successfully!")
            return True
        else:
            st.error("Could not capture the active window.")
            return False
    except Exception as e:
        st.error(f"Screenshot failed: {e}")
        return False

def load_and_resize_image(image_input):
    try:
        if isinstance(image_input, str):  # If it's a file path
            img = Image.open(image_input)
        else:  # If it's a file upload object
            img = Image.open(image_input)
        
        aspect_ratio = img.height / img.width
        new_height = int(img.width * aspect_ratio)
        return img.resize((img.width, new_height), Image.Resampling.LANCZOS)
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

def get_genai_response(prompt, image_path):
    try:
        img = load_and_resize_image(image_path)
        if img is None:
            return "Error: Could not process the image."
            
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant with expertise in image analysis.",
            ),
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"

def main():
    # App header
    st.markdown("""
    <div style="background-color:rgb(100, 100, 255);padding:8px">
    <h2 style="color:white;text-align:center;">AI Visual Assistant Multimodal Application with Python & Gemini 2.0 Flash Model</h2>
    </div>
    """, unsafe_allow_html=True)

    # Custom CSS styling
    st.markdown("""
    <style>
        .stFileUploader label {
            font-size: 18px;
        }
        div.stButton > button:first-child {
            background-color: #DD3300;
            color: #eeffee;
        }
    </style>
    """, unsafe_allow_html=True)

    # Image upload section
    st.markdown("<p style='color: purple; font-size: 18px; font-weight: bold;'>Upload Image</p>", unsafe_allow_html=True)
    img_file = st.file_uploader("", type=["jpg", "png"], label_visibility="collapsed")

    if img_file is not None:
        img = load_and_resize_image(img_file)
        if img is not None:
            st.image(img)
            img.save("picture.png")

    # Divider
    st.write("---")

    # Screenshot capture section
    if st.button("Capture Screenshot"):
        if capture_screen():
            img = load_and_resize_image("picture.png")
            if img is not None:
                st.image(img)

    # Query input
    query = st.text_input("**Query**", "", help="Enter your question about the image")

    # Analysis button
    if st.button("Analyze Image"):
        if os.path.exists("picture.png"):
            img = load_and_resize_image("picture.png")
            if img is not None:
                st.image(img)
                results = get_genai_response(query, "picture.png")
                st.success(f'Results: {results}')
        else:
            st.error("No image available. Please upload or capture an image first.")

if __name__ == "__main__":
    main()