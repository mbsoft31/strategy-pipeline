# OpenRouter Integration Guide

## ✅ Setup Complete!

Your system is now configured to use **OpenRouter** instead of direct OpenAI API.

---

## What is OpenRouter?

OpenRouter provides access to multiple LLM providers (OpenAI, Anthropic, Google, Meta, etc.) through a single unified API that's OpenAI-compatible.

**Benefits:**
- ✅ Single API key for many models
- ✅ Pay-per-use pricing (no subscriptions needed)
- ✅ Free models available
- ✅ No credit card declined issues
- ✅ Works with existing OpenAI code

---

## Configuration

Your `.env` is now set up with:

```env
LLM__PROVIDER=openai
LLM__OPENAI_API_KEY=sk-or-v1-... (your OpenRouter key)
LLM__OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM__OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Available Models on OpenRouter

### Free Models (No cost!)
```env
LLM__OPENAI_MODEL=google/gemini-flash-1.5-8b
# or
LLM__OPENAI_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### Low-Cost Models (Recommended)
```env
LLM__OPENAI_MODEL=openai/gpt-4o-mini  # ~$0.15/1M tokens
LLM__OPENAI_MODEL=anthropic/claude-3-haiku  # ~$0.25/1M tokens
LLM__OPENAI_MODEL=google/gemini-pro-1.5  # ~$0.35/1M tokens
```

### Premium Models
```env
LLM__OPENAI_MODEL=openai/gpt-4o  # ~$2.50/1M tokens
LLM__OPENAI_MODEL=anthropic/claude-3.5-sonnet  # ~$3.00/1M tokens
```

**See all models:** https://openrouter.ai/models

---

## How to Test

### 1. Simple Test
```bash
python test_openrouter.py
```

### 2. Orchestrator Agent Test
```bash
python test_orchestrator.py
```

### 3. Full Demo
```bash
python demo_autonomous_agent.py
```

---

## Troubleshooting

### Issue: "Authentication failed"
**Solution:** Check your API key at https://openrouter.ai/keys

### Issue: "Model not found"
**Solution:** Use full model name with provider prefix:
```env
# ✅ Correct
LLM__OPENAI_MODEL=openai/gpt-4o-mini

# ❌ Wrong
LLM__OPENAI_MODEL=gpt-4o-mini
```

### Issue: "Rate limit"
**Solution:** OpenRouter has generous limits. If you hit them:
1. Add credits at https://openrouter.ai/credits
2. Or use a free model temporarily

### Issue: "Too expensive"
**Solution:** Switch to a cheaper or free model:
```env
# Free option
LLM__OPENAI_MODEL=google/gemini-flash-1.5-8b

# Cheap option  
LLM__OPENAI_MODEL=openai/gpt-4o-mini
```

---

## Cost Estimation

For the autonomous research agent:

**Per Research Question:**
- Input: ~500 tokens (prompts)
- Output: ~200 tokens (strategy)
- **Total: ~700 tokens per question**

**With gpt-4o-mini ($0.15/1M input, $0.60/1M output):**
- Input cost: ~$0.000075
- Output cost: ~$0.00012
- **Total: ~$0.0002 per question** (1/5th of a cent!)

**100 research questions = $0.02** 🎉

---

## Model Recommendations

### For Research (Best Quality/Cost)
```env
LLM__OPENAI_MODEL=openai/gpt-4o-mini
```
- Great performance
- Very cheap
- Fast responses

### For Testing (Free!)
```env
LLM__OPENAI_MODEL=google/gemini-flash-1.5-8b
```
- Completely free
- Good enough for testing
- No costs

### For Production (Best Quality)
```env
LLM__OPENAI_MODEL=anthropic/claude-3.5-sonnet
```
- Best reasoning
- Most accurate
- Higher cost

---

## Code Changes Made

### 1. Updated `src/config.py`
Added `openai_base_url` field to support custom API endpoints.

### 2. Updated `src/services/llm_provider.py`
Modified `OpenAIProvider.__init__()` to use custom base_url when provided.

### 3. Updated `.env`
Configured for OpenRouter with your API key.

**No other code changes needed!** The OpenAI Python SDK is compatible with OpenRouter.

---

## Next Steps

1. **Test it works:**
   ```bash
   python test_openrouter.py
   ```

2. **Try the autonomous agent:**
   ```bash
   python demo_autonomous_agent.py
   ```

3. **Choose your model:**
   - Start with `openai/gpt-4o-mini` (cheap, good quality)
   - Try `google/gemini-flash-1.5-8b` if you want zero cost
   - Upgrade to `claude-3.5-sonnet` if you need best quality

4. **Monitor usage:**
   - Check dashboard: https://openrouter.ai/activity
   - View costs in real-time
   - Set budget limits if needed

---

## Why This is Better

**Before (Direct OpenAI):**
- ❌ Need credit card
- ❌ Your card was declined
- ❌ Locked to one provider
- ❌ Higher costs

**After (OpenRouter):**
- ✅ Works with your existing API key
- ✅ Multiple providers available
- ✅ Free models available
- ✅ Pay-per-use (no subscription)
- ✅ Often cheaper than direct API

---

## Support

**OpenRouter Docs:** https://openrouter.ai/docs  
**Model Prices:** https://openrouter.ai/models  
**Your Dashboard:** https://openrouter.ai/activity

**Questions?** The integration is complete and should work out of the box!

---

**Status:** ✅ OpenRouter integration complete!  
**Ready to use:** Run `python demo_autonomous_agent.py` 🚀

