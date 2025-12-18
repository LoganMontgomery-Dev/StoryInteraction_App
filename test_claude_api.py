"""
Milestone 1 (Claude Version): Test Claude API Connection
Goal: Verify Python can call Claude API and get responses

Prerequisites:
1. Anthropic package installed (pip install anthropic)
2. API key in .env file

Run: python test_claude_api.py
"""

import os
from anthropic import Anthropic

def test_claude_api():
    print("=" * 50)
    print("MILESTONE 1: Testing Claude API Connection")
    print("=" * 50)

    # Load API key from .env file
    # Read the .env file manually (simple approach for now)
    env_path = ".env"
    api_key = None

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                    break

    if not api_key or api_key == "paste-your-key-here":
        print("✗ ERROR: API key not found in .env file")
        print("Please make sure your .env file has:")
        print("ANTHROPIC_API_KEY=sk-ant-...")
        return False

    print(f"\n[1/3] API key found: {api_key[:20]}...")
    print("[2/3] Connecting to Claude API...")

    try:
        # Create Anthropic client
        client = Anthropic(api_key=api_key)

        # Send a simple test message
        print("[3/3] Sending test message: 'Say hello in a creative way'")

        message = client.messages.create(
            model="claude-sonnet-4-20250514",  # Claude Sonnet 4 (great for creative writing)
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say hello in a creative way"}
            ]
        )

        print("\n" + "=" * 50)
        print("Claude's Response:")
        print("=" * 50)
        print(message.content[0].text)
        print("=" * 50)

        print("\n✓ MILESTONE 1 COMPLETE!")
        print("Claude API connection working successfully.")
        print(f"Model used: {message.model}")
        print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        print()
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Is your API key correct?")
        print("2. Do you have credits/subscription active?")
        print("3. Check https://console.anthropic.com/")
        print()
        return False

if __name__ == "__main__":
    test_claude_api()
