import os
import google.generativeai as genai
from dotenv import load_dotenv  # Import dotenv to load .env file

# Load environment variables from .env file
load_dotenv()

# Access the API key securely
api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API
genai.configure(api_key=api_key)

# Verify if the API key is loaded properly
if api_key:
    print("API key loaded successfully!")
else:
    print("Error: API key not found!")
