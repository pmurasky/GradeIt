# AI Provider Fallback System

## Overview

GradeIt now supports **automatic fallback between multiple AI providers**. When one provider hits its quota limit, the system automatically switches to the next available provider.

## Supported Providers

1. **Google Gemini** (`gemini-flash-latest` or `gemini-2.0-flash`)
   - Free tier: 1,500 requests per day
   - Get API key: https://aistudio.google.com/app/apikey

2. **Anthropic Claude** (`claude-3-5-sonnet-20241022`)
   - Free tier: $5 credit for new users
   - Get API key: https://console.anthropic.com/

3. **OpenAI GPT** (`gpt-4o-mini`)
   - Free tier: $5 credit for new users
   - Get API key: https://platform.openai.com/api-keys

## Configuration

### Step 1: Get API Keys

Sign up for at least one (preferably all three) AI providers and get your API keys.

### Step 2: Update `config.properties`

```properties
# Fallback providers (comma-separated, in order of preference)
ai_providers_fallback=gemini,anthropic,openai

# Add your API keys
gemini_api_key=YOUR_GEMINI_KEY_HERE
anthropic_api_key=YOUR_ANTHROPIC_KEY_HERE
openai_api_key=YOUR_OPENAI_KEY_HERE
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## How It Works

1. **Automatic Detection**: The system tries each provider in the order specified in `ai_providers_fallback`
2. **Quota Detection**: When a provider returns a quota/rate limit error (429, RESOURCE_EXHAUSTED, etc.), it automatically tries the next provider
3. **Seamless Switching**: You'll see messages like:
   ```
   ⚠️  Quota limit hit for GeminiClient, trying next provider...
   ✓ Switched to AnthropicClient
   ```
4. **No Manual Intervention**: The grading continues automatically with the next provider

## Example Scenarios

### Scenario 1: Gemini Quota Exhausted
```
Processing student1...
⚠️  Quota limit hit for GeminiClient, trying next provider...
✓ Switched to AnthropicClient
  ✓ Report appended to: Assignment1_Feedback.md
```

### Scenario 2: Multiple Providers Exhausted
```
Processing student5...
⚠️  Quota limit hit for GeminiClient, trying next provider...
⚠️  Quota limit hit for AnthropicClient, trying next provider...
✓ Switched to OpenAIClient
  ✓ Report appended to: Assignment1_Feedback.md
```

### Scenario 3: All Providers Exhausted
```
Processing student10...
⚠️  Quota limit hit for GeminiClient, trying next provider...
⚠️  Quota limit hit for AnthropicClient, trying next provider...
⚠️  Quota limit hit for OpenAIClient, trying next provider...
  ✗ Error grading student10: All AI providers failed
```

## Provider Order Strategy

**Recommended order**: `gemini,anthropic,openai`

- **Gemini**: Fastest and free tier is generous (1,500/day)
- **Anthropic**: High quality, good for complex grading
- **OpenAI**: Reliable fallback, widely available

You can customize the order based on your preferences and quota limits.

## Cost Considerations

### Free Tier Limits (Approximate)

- **Gemini**: 1,500 requests/day (free)
- **Anthropic**: ~100-200 requests with $5 credit
- **OpenAI**: ~500-1000 requests with $5 credit (gpt-4o-mini)

### Maximizing Free Usage

1. Start with Gemini (largest free tier)
2. Use Anthropic/OpenAI when Gemini quota is exhausted
3. Wait for daily quota reset (usually midnight UTC)

## Troubleshooting

### "Skipping provider: API_KEY not found"

This is normal if you haven't set up all providers. The system will skip providers without API keys and use the ones you've configured.

### All Providers Failing

1. Check your API keys are valid
2. Verify you haven't exhausted all quotas
3. Check your internet connection
4. Review provider status pages

## Single Provider Mode

If you prefer to use only one provider (no fallback), you can:

1. Set only one API key in config.properties
2. Or modify `ai_providers_fallback` to include only one provider:
   ```properties
   ai_providers_fallback=anthropic
   ```

## Advanced Configuration

### Custom Models

You can specify different models for each provider:

```properties
gemini_model=gemini-2.0-flash
anthropic_model=claude-3-5-sonnet-20241022
openai_model=gpt-4o-mini
```

### Provider-Specific Settings

Each provider has its own strengths:

- **Gemini**: Fast, good for bulk grading
- **Claude (Anthropic)**: Best for detailed code analysis
- **GPT (OpenAI)**: Balanced performance and quality

Choose your fallback order based on your priorities.
