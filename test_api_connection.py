#!/usr/bin/env python3
"""
Gemini API Connection Test Script

This script verifies that the Gemini API key is set up correctly
and can connect to the Google Generative AI service.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    print(f"Loading environment from: {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found.")
    print("Make sure to set up your environment variables!")
    sys.exit(1)

# Check if API key is set
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: No Gemini API key found in environment variables.")
    print("Please set GEMINI_API_KEY in your .env file.")
    sys.exit(1)

print(f"API key found: {api_key[:4]}...{api_key[-4:]} (middle redacted for security)")

try:
    # Try importing and configuring the Gemini API
    print("\nTesting connection to Google Generative AI...")
    import google.generativeai as genai
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Try to access a model
    models = genai.list_models()
    gemini_models = [model.name for model in models if "gemini" in model.name]
    
    print(f"\nAvailable Gemini models:")
    for model in gemini_models:
        print(f"  - {model}")
    
    # Try a simple generation to verify API access
    print("\nTesting API with a simple prompt...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, I'm testing the Gemini API. Please respond with a brief confirmation that the API is working correctly.")
    
    print("\nAPI Response:")
    print("-" * 40)
    print(response.text)
    print("-" * 40)
    
    print("\n✅ API test successful! Your Gemini API key is working correctly.")
    print("\nYou can now run the application with:")
    print("  python main.py")
    
except Exception as e:
    print(f"\n❌ Error connecting to Gemini API: {str(e)}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. No internet connection")
    print("3. API quota exceeded")
    print("4. Missing or incorrect permissions for your API key")
    sys.exit(1)