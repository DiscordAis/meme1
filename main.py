import streamlit as st
import requests
import os
import logging
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
SUPER_MEME_API_KEY = os.getenv("SUPER_MEME_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Function to get meme ideas
def get_meme_idea():
    try:
        prompt = ("give me 10 meme ideas that relatable to pet such as:,"
         "cat, dog, bird, and fish. about their funny, whimsical, and daily behavior. i want those in positive"
         "tone and relatable to pet owners. the ideas should be in casual bahasa indonesia. you just"
          "need to give the ideas, dont suggest any caption, images,"
          "emojis, etc. be sharp and crisp and punchy don't verbose ALSO don't give the number like 1,2 for 10 sentence also * too")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            return None

        candidates = response_data.get("candidates", [])
        if not candidates:
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return None

        text_response = parts[0].get("text", "").strip()
        if not text_response:
            return None

        return [idea.strip() for idea in text_response.split("\n") if idea.strip()]

    except Exception as e:
        logging.exception("Error fetching meme ideas:")
        return None

# Function to generate meme
def generate_meme(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {SUPER_MEME_API_KEY}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            "https://app.supermeme.ai/api/v2/meme/image",
            json={"text": prompt},
            headers=headers,
        )

        if response.status_code == 401:
            return None

        response.raise_for_status()
        memes = response.json().get("memes", [])
        return memes[:10]  # Return top 10 memes

    except Exception as e:
        logging.exception("Error generating meme:")
        return None

# Function to download image
def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        logging.error(f"Failed to download image: {e}")
        return None

# Enhanced styling
st.markdown(
    """
    <style>
    .stButton > button {
        background-color: #0096FF !important;  /* Blue */
        color: white !important;
        border: none !important;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #ADD8E6 !important;  /* Light Blue */
        border-color: transparent !important;
    }
    .stButton > button:focus {
        box-shadow: none !important;
        border-color: transparent !important;
    }
    .stButton > button:active {
        background-color: #ADD8E6 !important;
        border-color: transparent !important;
    }
    .meme-image {
        cursor: pointer;
        transition: transform 0.2s;
    }
    .meme-image:hover {
        transform: scale(1.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit app setup
st.title("AI Meme Generator")
st.markdown("Transform your ideas into hilarious memes with AI!")

# Initialize session state
if "meme_text" not in st.session_state:
    st.session_state["meme_text"] = ""
if "generated_memes" not in st.session_state:
    st.session_state["generated_memes"] = None
if "selected_image" not in st.session_state:
    st.session_state["selected_image"] = None
if "show_modal" not in st.session_state:
    st.session_state["show_modal"] = False
if "meme_ideas" not in st.session_state:
    st.session_state["meme_ideas"] = []

# Function to handle image selection
def view_full_image(url):
    st.session_state["selected_image"] = url
    st.session_state["show_modal"] = True
    st.rerun()

# Function to close modal
def close_modal():
    st.session_state["show_modal"] = False
    st.session_state["selected_image"] = None
    st.rerun()

# Callback for idea selection
def select_idea(idea):
    st.session_state["meme_text"] = idea

# Input field for meme idea
meme_text = st.text_area(
    "Describe your meme idea...",
    value=st.session_state["meme_text"],
    max_chars=300,
    height=100,
    key="meme_input",
)
st.write(f"Character count: {len(meme_text)}/300")

# Create two columns for buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Generate Meme", key="generate_button"):
        if meme_text.strip():
            memes = generate_meme(meme_text.strip())
            if memes:
                st.session_state["generated_memes"] = memes
            else:
                st.error("Failed to generate memes. Try again.")
        else:
            st.error("Please enter a meme idea.")

with col2:
    if st.button("Get Meme Ideas", key="ideas_button"):
        ideas = get_meme_idea()
        if ideas:
            st.session_state["meme_ideas"] = ideas
        else:
            st.error("Failed to get meme ideas. Try again.")

# Display meme ideas
if st.session_state["meme_ideas"]:
    st.write("Choose a meme idea:")
    cols = st.columns(2)
    for idx, idea in enumerate(st.session_state["meme_ideas"]):
        with cols[idx % 2]:
            if st.button(idea, key=f"idea_{idx}", use_container_width=True, on_click=select_idea, args=(idea,)):
                pass

# Display generated memes
if not st.session_state["show_modal"]:
    if st.session_state["generated_memes"]:
        for idx, url in enumerate(st.session_state["generated_memes"]):
            st.image(url, use_container_width=True, output_format="PNG")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("View Full Size", key=f"view_{idx}", use_container_width=True):
                    view_full_image(url)

# Modal for selected image
if st.session_state["show_modal"]:
    st.image(st.session_state["selected_image"], use_container_width=True)
    image_data = download_image(st.session_state["selected_image"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Back", use_container_width=True):
            close_modal()

    with col2:
        if image_data:
            st.download_button(
                label="Download Meme",
                data=image_data,
                file_name="meme.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.error("Failed to fetch image for download.")
