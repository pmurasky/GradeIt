# Multi-Provider AI Fallback System - Setup Guide

## 🎯 What We've Built

Your GradeIt system now has **automatic fallback between 3 AI providers**:
1. **Google Gemini** (currently configured)
2. **Anthropic Claude** (ready to add)
3. **OpenAI GPT** (ready to add)

When Gemini hits its quota limit, the system will automatically switch to Claude, then to OpenAI if needed.

## 📋 Quick Setup Steps

### Step 1: Install OpenAI Package

Since your system uses an externally-managed Python environment, you'll need to install the openai package. Choose one of these methods:

**Option A: Using pipx (Recommended)**
```bash
pipx install openai
```

**Option B: Using --break-system-packages (if you know what you're doing)**
```bash
pip install --break-system-packages openai>=1.0.0
```

**Option C: Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Get Additional API Keys

#### For Anthropic Claude:
1. Go to https://console.anthropic.com/
2. Sign up (you get $5 free credit)
3. Create an API key
4. Add to `config.properties`:
   ```properties
   anthropic_api_key=sk-ant-xxxxxxxxxxxxx
   ```

#### For OpenAI:
1. Go to https://platform.openai.com/api-keys
2. Sign up (you get $5 free credit)
3. Create an API key
4. Add to `config.properties`:
   ```properties
   openai_api_key=sk-xxxxxxxxxxxxx
   ```

### Step 3: Test the System

Run your grading command as usual:
```bash
python -m gradeit.cli grade -a Assignment1 -s Solution1
```

## 🔄 How the Fallback Works

### Current Behavior (Gemini Only)
```
Processing student1...
AI Error calling Gemini: 429 RESOURCE_EXHAUSTED
  ✗ Error grading student1
```

### New Behavior (With Fallback)
```
Processing student1...
⚠️  Quota limit hit for GeminiClient, trying next provider...
✓ Switched to AnthropicClient
  ✓ Report appended to: Assignment1_Feedback.md

Processing student2...
  ✓ Report appended to: Assignment1_Feedback.md
(continues using AnthropicClient)
```

## 📊 Provider Comparison

| Provider | Free Tier | Speed | Quality | Best For |
|----------|-----------|-------|---------|----------|
| **Gemini** | 1,500/day | ⚡⚡⚡ | ⭐⭐⭐ | Bulk grading |
| **Claude** | $5 credit | ⚡⚡ | ⭐⭐⭐⭐⭐ | Detailed analysis |
| **OpenAI** | $5 credit | ⚡⚡ | ⭐⭐⭐⭐ | Balanced |

## 🎛️ Configuration Options

### Current Configuration (config.properties)
```properties
# Fallback order (tries in this order)
ai_providers_fallback=gemini,anthropic,openai

# Gemini (currently working)
gemini_api_key=AIzaSyBjGS9Fra_uB7QB1pOMyR_xuLN3XmKcC8Q
gemini_model=gemini-flash-latest

# Anthropic (add your key)
anthropic_api_key=
anthropic_model=claude-3-5-sonnet-20241022

# OpenAI (add your key)
openai_api_key=
openai_model=gpt-4o-mini
```

### Customize Fallback Order

You can change the order based on your preferences:

**Option 1: Start with Claude (highest quality)**
```properties
ai_providers_fallback=anthropic,gemini,openai
```

**Option 2: Use only two providers**
```properties
ai_providers_fallback=gemini,anthropic
```

**Option 3: Use only one provider (no fallback)**
```properties
ai_providers_fallback=gemini
```

## 💡 Immediate Solution for Your Current Issue

Since Gemini hit the quota limit, here's what to do RIGHT NOW:

### Quick Fix: Switch to Anthropic

1. **Get Anthropic API key** (takes 2 minutes):
   - Visit: https://console.anthropic.com/
   - Sign up with email
   - Go to "API Keys" → "Create Key"
   - Copy the key (starts with `sk-ant-`)

2. **Update config.properties**:
   ```properties
   anthropic_api_key=sk-ant-YOUR_KEY_HERE
   ```

3. **Run grading again**:
   ```bash
   python -m gradeit.cli grade -a YourAssignment -s YourSolution
   ```

The system will automatically skip Gemini and use Claude!

## 🔍 Monitoring Usage

### Check Which Provider is Being Used

Watch the console output:
```
✓ Switched to AnthropicClient  ← You'll see this when it switches
```

### Providers Being Skipped

If a provider doesn't have an API key:
```
Skipping openai: OPENAI_API_KEY not found  ← This is normal
```

## 📝 Files Modified

1. ✅ `requirements.txt` - Added OpenAI package
2. ✅ `src/gradeit/ai_clients.py` - Added OpenAI client and fallback logic
3. ✅ `src/gradeit/cli.py` - Updated to use fallback client
4. ✅ `config.properties` - Added multi-provider configuration
5. ✅ `AI_PROVIDER_FALLBACK.md` - Detailed documentation
6. ✅ `SETUP_GUIDE.md` - This file

## 🚀 Next Steps

1. **Immediate**: Get an Anthropic API key to continue grading
2. **Soon**: Get an OpenAI API key as a third fallback
3. **Optional**: Install openai package when convenient
4. **Monitor**: Watch your quota usage across providers

## ❓ FAQ

**Q: Do I need all three providers?**
A: No! You can use just one or two. The system will skip providers without API keys.

**Q: What happens if all providers fail?**
A: The system will show an error message and continue to the next student.

**Q: Can I use different models?**
A: Yes! Edit the `*_model` settings in config.properties.

**Q: Is this more expensive?**
A: No! You're using free tiers. It actually saves money by spreading load across providers.

**Q: Will my existing grades be affected?**
A: No! The fallback system only affects new grading operations.

## 📞 Support

For more details, see:
- `AI_PROVIDER_FALLBACK.md` - Complete fallback system documentation
- `README.md` - General GradeIt documentation
