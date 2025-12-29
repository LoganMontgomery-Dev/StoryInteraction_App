"""
Milestone 3: Lore + Claude = Narrative
Goal: Claude responds using injected lore from your vault

Prerequisites:
1. Claude API working (Milestone 1)
2. Vault reading working (Milestone 2)
3. API key in .env

Run: python test_lore_injection.py
"""

import os
from pathlib import Path
from anthropic import Anthropic

def test_lore_injection():
    print("=" * 50)
    print("MILESTONE 3: Lore + Claude = Narrative")
    print("=" * 50)

    # Setup paths
    vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")
    lore_path = vault_path / "_Lore"
    lyssia_file = lore_path / "Char_Aeth_Lyssia.md"

    print(f"\n[1/5] Loading API key...")

    # Load API key from .env
    env_path = ".env"
    api_key = None

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                    break

    if not api_key:
        print("X ERROR: API key not found in .env")
        return False

    print(f"OK API key loaded: {api_key[:20]}...")

    print(f"\n[2/5] Reading Lyssia's lore...")

    try:
        with open(lyssia_file, 'r', encoding='utf-8') as f:
            lyssia_lore = f.read()

        print(f"OK Loaded {len(lyssia_lore)} characters of lore")

    except Exception as e:
        print(f"X ERROR reading lore file: {e}")
        return False

    print(f"\n[3/5] Creating scenario...")

    # User's action/scenario
    user_input = "Lyssia and I approach an ancient gate in the desert. What does she do?"

    print(f"Scenario: {user_input}")

    print(f"\n[4/5] Sending to Claude with lore context...")

    # Build the prompt with lore
    prompt = f"""You are a narrative generator for the DOAMMO universe.

LORE CONTEXT (use this to stay consistent):
{lyssia_lore[:1500]}

USER SCENARIO:
{user_input}

Generate a narrative response (2-3 paragraphs) that:
- Uses details from the lore
- Stays in character for Lyssia
- Is engaging and descriptive
"""

    try:
        client = Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        narrative = message.content[0].text

        print("OK Received narrative response")

        print(f"\n[5/5] Claude's Narrative:")
        print("=" * 50)
        print(narrative)
        print("=" * 50)

        print("\nOK MILESTONE 3 COMPLETE!")
        print("Claude successfully generated narrative using your lore!")
        print(f"Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        print()

        return True

    except Exception as e:
        print(f"X ERROR: {e}")
        return False

if __name__ == "__main__":
    test_lore_injection()
