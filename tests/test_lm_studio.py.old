"""
Milestone 1: Test LM Studio Connection
Goal: Verify Python can call LM Studio and get responses

Prerequisites:
1. LM Studio is running
2. A model is loaded
3. Server is started (localhost:1234)

Run: python test_lm_studio.py
"""

import openai

def test_lm_studio():
    print("=" * 50)
    print("MILESTONE 1: Testing LM Studio Connection")
    print("=" * 50)

    # Point to LM Studio
    client = openai.OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    print("\n[1/3] Connecting to LM Studio at localhost:1234...")

    try:
        # Test call
        print("[2/3] Sending test message: 'Say hello'")
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=50
        )

        print("[3/3] ✓ Response received!")
        print("\n" + "=" * 50)
        print("LM Studio Response:")
        print("=" * 50)
        print(response.choices[0].message.content)
        print("=" * 50)

        print("\n✓ MILESTONE 1 COMPLETE!")
        print("LM Studio connection working successfully.\n")
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nTroubleshooting:")
        print("1. Is LM Studio running?")
        print("2. Is a model loaded?")
        print("3. Is the server started? (green indicator in LM Studio)")
        print("4. Try accessing http://localhost:1234/v1/models in browser")
        print()
        return False

if __name__ == "__main__":
    test_lm_studio()
