"""
Quick test to verify OpenRouter integration works.
"""
from src.services.llm_provider import get_llm_provider

print("Testing OpenRouter integration...")
print()

try:
    # Get provider
    llm = get_llm_provider()
    print(f"✅ LLM Provider initialized: {type(llm).__name__}")
    print()

    # Test a simple generation
    print("Sending test request to OpenRouter...")
    response = llm.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say 'Hello from OpenRouter!' and nothing else."
    )

    print(f"✅ Response received: {response}")
    print()
    print("🎉 OpenRouter is working!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

