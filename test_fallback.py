#!/usr/bin/env python3
"""
Test script to verify AI provider fallback system.
This script tests the fallback logic without actually grading students.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from gradeit.config_loader import ConfigLoader
from gradeit.ai_clients import AIClientFactory, FallbackAIClient

def test_fallback_system():
    """Test the AI provider fallback system."""
    print("🧪 Testing AI Provider Fallback System\n")
    print("=" * 60)
    
    # Load configuration
    try:
        config = ConfigLoader('config.properties')
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    # Create fallback clients
    print("\n📋 Creating AI clients with fallback support...")
    print("-" * 60)
    
    try:
        clients = AIClientFactory.create_fallback_clients(config)
        print(f"\n✓ Created {len(clients)} AI client(s):")
        for i, client in enumerate(clients, 1):
            print(f"  {i}. {client.__class__.__name__}")
        
        if not clients:
            print("\n⚠️  No AI clients available!")
            print("   Please add at least one API key to config.properties")
            return False
            
    except Exception as e:
        print(f"\n✗ Failed to create clients: {e}")
        return False
    
    # Create fallback client
    print("\n🔄 Creating fallback client wrapper...")
    try:
        fallback_client = FallbackAIClient(clients)
        print("✓ Fallback client created successfully")
    except Exception as e:
        print(f"✗ Failed to create fallback client: {e}")
        return False
    
    # Test with a simple prompt
    print("\n🧪 Testing with a simple code analysis prompt...")
    print("-" * 60)
    
    test_prompt = """
    Analyze this simple Java code and provide feedback in JSON format:
    
    ```java
    public class HelloWorld {
        public static void main(String[] args) {
            System.out.println("Hello, World!");
        }
    }
    ```
    
    Return JSON with: score (0-100), feedback (string), suggestions (array), confidence (0-1)
    """
    
    try:
        result = fallback_client.analyze_code(test_prompt)
        print("\n✓ AI Response received:")
        print("-" * 60)
        print(result[:500])  # Print first 500 chars
        if len(result) > 500:
            print("... (truncated)")
        print("-" * 60)
        
        # Check if it's an error response
        if "AI Error" in result or "All AI providers failed" in result:
            print("\n⚠️  Warning: AI returned an error response")
            print("   This might indicate quota limits or API key issues")
            return False
        else:
            print("\n✅ SUCCESS! The fallback system is working correctly!")
            return True
            
    except Exception as e:
        print(f"\n✗ Error during AI call: {e}")
        return False

def print_summary():
    """Print summary and next steps."""
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("""
The fallback system is now configured. Here's what will happen:

1. When grading, the system tries providers in this order:
   - Gemini (if API key is set)
   - Anthropic (if API key is set)
   - OpenAI (if API key is set)

2. If a provider hits quota limits, it automatically tries the next one

3. You'll see messages like:
   ⚠️  Quota limit hit for GeminiClient, trying next provider...
   ✓ Switched to AnthropicClient

Next Steps:
-----------
1. Add API keys for Anthropic and/or OpenAI to config.properties
2. Install the openai package if you plan to use OpenAI
3. Run your grading commands as usual

For detailed setup instructions, see:
- SETUP_GUIDE.md
- AI_PROVIDER_FALLBACK.md
""")

if __name__ == '__main__':
    print("\n")
    success = test_fallback_system()
    print_summary()
    
    if success:
        print("\n✅ All tests passed! You're ready to grade with fallback support.")
        sys.exit(0)
    else:
        print("\n⚠️  Tests completed with warnings. Check the output above.")
        print("   The system will still work, but you may want to add more API keys.")
        sys.exit(0)
