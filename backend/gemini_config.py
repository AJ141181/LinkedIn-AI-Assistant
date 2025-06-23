# backend/gemini_config.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load the environment variable from .env
load_dotenv()

# Set up Gemini API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# ✅ Define the Gemini Pro model instance
model = genai.GenerativeModel("models/gemini-1.5-pro")

# ✅ Explicit export
__all__ = ["model"]
