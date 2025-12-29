"""
Milestone 5: Intelligent Lore-Aware Narrative Generation
Goal: Automatically find relevant lore and generate context-aware narratives

Prerequisites:
1. ChromaDB working (Milestone 4)
2. Claude API working (Milestone 1)
3. Lore embedded in ChromaDB

How it works:
- User provides a scenario
- ChromaDB finds the most relevant lore
- Claude generates narrative using that lore as context
- No manual lore selection needed!

Run: python test_intelligent_narrative.py
"""

import os
from pathlib import Path
import chromadb
from chromadb.config import Settings
from anthropic import Anthropic

def test_intelligent_narrative():
    print("=" * 50)
    print("MILESTONE 5: Intelligent Lore-Aware Narratives")
    print("=" * 50)

    # Setup
    chroma_path = Path("chroma_data")

    print(f"\n[1/7] Loading API key...")

    # Load API key
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

    print(f"\n[2/7] Connecting to ChromaDB...")

    # Connect to existing ChromaDB
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get the existing collection
    try:
        collection = client.get_collection(name="doammo_lore")
        print(f"OK Connected to ChromaDB collection")
    except Exception as e:
        print(f"X ERROR: ChromaDB collection not found. Run test_chromadb_setup.py first!")
        return False

    print(f"\n[3/7] Creating test scenario...")

    # User's scenario - this time it mentions a creature!
    user_scenario = "I'm exploring the desert ruins when I encounter a massive, tentacled creature emerging from the sand. What happens?"

    print(f"Scenario: {user_scenario}")

    print(f"\n[4/7] Searching ChromaDB for relevant lore...")

    # Search for the most relevant lore for this scenario
    # We'll get top 3 most relevant documents
    search_results = collection.query(
        query_texts=[user_scenario],
        n_results=3  # Get top 3 most relevant lore pieces
    )

    # Display what ChromaDB found
    print(f"\nChromaDB found {len(search_results['documents'][0])} relevant lore documents:")
    for i, (meta, distance) in enumerate(zip(
        search_results['metadatas'][0],
        search_results['distances'][0]
    )):
        print(f"  {i+1}. {meta['filename']} (relevance: {distance:.4f})")

    print(f"\n[5/7] Building context from retrieved lore...")

    # Combine the top results into context for Claude
    lore_context = ""
    for i, doc in enumerate(search_results['documents'][0]):
        filename = search_results['metadatas'][0][i]['filename']
        # Limit each doc to 1500 chars to manage context size
        lore_context += f"\n--- From {filename} ---\n{doc[:1500]}\n"

    print(f"OK Built context from {len(search_results['documents'][0])} documents")
    print(f"Total context size: {len(lore_context)} characters")

    print(f"\n[6/7] Generating narrative with Claude...")

    # Build the prompt with automatically retrieved lore
    prompt = f"""You are a narrative generator for the DOAMMO universe.

RELEVANT LORE CONTEXT (use this to stay consistent with the world):
{lore_context}

USER SCENARIO:
{user_scenario}

Generate an engaging narrative response (2-3 paragraphs) that:
- Uses specific details from the lore context above
- Stays consistent with the DOAMMO universe
- Is descriptive and immersive
- Advances the scenario in an interesting way
"""

    # Send to Claude
    try:
        anthropic_client = Anthropic(api_key=api_key)

        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        narrative = message.content[0].text

        print("OK Claude generated narrative")

        print(f"\n[7/7] Generated Narrative:")
        print("=" * 50)
        print(narrative)
        print("=" * 50)

        print("\n" + "=" * 50)
        print("MILESTONE 5 COMPLETE!")
        print("=" * 50)
        print("\nWhat just happened:")
        print("1. You provided a scenario about a creature in the desert")
        print("2. ChromaDB automatically found the 3 most relevant lore documents")
        print("3. Claude used that lore to generate a consistent narrative")
        print("4. NO manual lore selection needed!")
        print(f"\nLore used: {', '.join([m['filename'] for m in search_results['metadatas'][0]])}")
        print(f"Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        print()

        return True

    except Exception as e:
        print(f"X ERROR: {e}")
        return False

if __name__ == "__main__":
    test_intelligent_narrative()
