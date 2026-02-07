"""
Script to test Google Gemini API Key connection.
"""
import os
import sys
from pathlib import Path

# Add src to path to use project modules if needed, but we'll keep this simple and standalone
# to strictly test the API connection.

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai is not installed.")
    print("Run: pip install google-generativeai")
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
        genai.configure(api_key=api_key)
        
        print("Listing available models...")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    print(f" - {m.name}")
        except Exception as e:
             print(f"⚠️ Failed to list models: {e}")

        # Try models seen in the list
        models_to_try = ["gemini-2.0-flash-lite", "gemini-flash-latest", "gemini-2.5-flash"]
        
        for model_name in models_to_try:
            print(f"\nAttempting with model: {model_name}...")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello! Are you working?")
                
                print(f"\n✅ Success! Gemini responded using {model_name}:")
                print(f"Response: {response.text}")
                return # Exit on success
            except Exception as e:
                print(f"⚠️ Failed with {model_name}: {e}")
                
        print("\n❌ All models failed.")

    except Exception as e:
        print("\n❌ Connection Failed!")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_connection()
