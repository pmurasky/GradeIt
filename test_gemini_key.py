"""
Script to test Google Gemini API Key connection.
"""
import os
import sys
from pathlib import Path

# Add src to path to use project modules if needed, but we'll keep this simple and standalone
# to strictly test the API connection.

try:
    from google import genai
except ImportError:
    print("Error: google-genai is not installed.")
    print("Run: pip install google-genai")
    sys.exit(1)

def load_api_key():
    """Load API key from config.properties or env."""
    config_path = Path("config.properties")
    api_key = None
    
    if config_path.exists():
        with open(config_path, "r") as f:
            for line in f:
                if line.strip().startswith("gemini_api_key"):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        api_key = parts[1].strip()
                        break
    
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        
    return api_key

def test_connection():
    api_key = load_api_key()
    
    if not api_key:
        print("❌ Error: Could not find 'gemini_api_key' in config.properties or GEMINI_API_KEY env var.")
        return

    print(f"Testing API Key: {api_key[:5]}...{api_key[-4:]}")
    
    try:
        client = genai.Client(api_key=api_key)
        
        print("Listing available models...")
        try:
            models = client.models.list()
            print("Available models:")
            for model in models:
                print(f" - {model.name}")
        except Exception as e:
             print(f"⚠️ Failed to list models: {e}")

        # Test with a working model (gemini-2.0-flash or gemini-1.5-flash are commonly available)
        models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        
        for model_name in models_to_try:
            print(f"\nTesting with model: {model_name}...")
            
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents="Hello! Are you working?"
                )
                
                print(f"\n✅ Success! Gemini responded using {model_name}:")
                print(f"Response: {response.text}")
                return  # Exit on first success
            except Exception as e:
                print(f"⚠️ Failed with {model_name}: {e}")
        
        print("\n❌ All tested models failed.")

    except Exception as e:
        print("\n❌ Connection Failed!")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_connection()
