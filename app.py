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
        if not GEMINI_API_KEY:
            logging.error("Gemini API key not found")
            return None

        prompt = ("give me 10 meme ideas that relatable to pet such as:,"
                   "cat, dog, bird, and fish. about their funny, whimsical, and daily behavior. i want those in positive"
                   "tone and relatable to pet owners. the ideas should be in casual bahasa indonesia. you just"
                   "need to give the ideas, dont suggest any caption, images,"
                    "emojis, etc. be sharp and crisp and punchy don't verbose")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Will raise an exception for HTTP errors
        response_data = response.json()

        if 'error' in response_data:
            logging.error(f"Gemini API error: {response_data['error']}")
            return None

        candidates = response_data.get("candidates", [])
        if not candidates:
            logging.error("No candidates returned from Gemini API")
            return None

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            logging.error("No parts found in Gemini API response")
            return None

        text_response = parts[0].get("text", "").strip()
        if not text_response:
            logging.error("Empty text response from Gemini API")
            return None

        return [idea.strip() for idea in text_response.split("\n") if idea.strip()]

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        logging.exception("Error fetching meme ideas:")
        return None

# Function to generate meme
def generate_meme(prompt):
    try:
        if not SUPER_MEME_API_KEY:
            logging.error("SuperMeme API key not found")
            return None

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
            logging.error("Unauthorized access to SuperMeme API")
            return None

        response.raise_for_status()
        memes = response.json().get("memes", [])
        
        if not memes:
            logging.error("No memes returned from SuperMeme API")
            return None
            
        return memes[:10]  # Return top 10 memes

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        logging.exception("Error generating meme:")
        return None

# Function to download image
def download_image(url):
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.Timeout:
        logging.error("Request timed out while downloading image")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download image: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Failed to download image: {str(e)}")
        return None

[Rest of the code remains exactly the same...]
