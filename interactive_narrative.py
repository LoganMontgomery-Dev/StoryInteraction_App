"""
Interactive DOAMMO Narrative Engine
A simple terminal interface to interact with your lore-aware AI narrator

Run: python interactive_narrative.py
Type scenarios and get AI-generated narratives back!
Type 'quit' or 'exit' to stop
"""

import os
from pathlib import Path
import chromadb
from chromadb.config import Settings
from anthropic import Anthropic

class DOAMMONarrator:
    def __init__(self):
        self.chroma_path = Path("chroma_data")
        self.api_key = None
        self.chroma_client = None
        self.collection = None
        self.anthropic_client = None

    def setup(self):
        """Initialize all components"""
        print("=" * 60)
        print("DOAMMO Interactive Narrative Engine")
        print("=" * 60)

        # Load API key
        print("\nInitializing...")
        env_path = ".env"

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ANTHROPIC_API_KEY='):
                        self.api_key = line.strip().split('=', 1)[1]
                        break

        if not self.api_key:
            print("ERROR: API key not found in .env")
            return False

        # Connect to ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.chroma_path),
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.chroma_client.get_collection(name="doammo_lore")
            print(f"OK Connected to lore database ({self.collection.count()} documents)")
        except Exception as e:
            print(f"ERROR: Could not connect to ChromaDB. Run test_chromadb_setup.py first!")
            return False

        # Setup Claude client
        self.anthropic_client = Anthropic(api_key=self.api_key)
        print("OK Connected to Claude AI")

        return True

    def generate_narrative(self, user_input):
        """Generate a narrative based on user input"""

        # Step 1: Find relevant lore
        print("\nSearching lore database...")
        search_results = self.collection.query(
            query_texts=[user_input],
            n_results=3
        )

        # Show what lore was found
        lore_files = [m['filename'] for m in search_results['metadatas'][0]]
        print(f"Using lore from: {', '.join(lore_files)}")

        # Step 2: Build context
        lore_context = ""
        for i, doc in enumerate(search_results['documents'][0]):
            filename = search_results['metadatas'][0][i]['filename']
            lore_context += f"\n--- From {filename} ---\n{doc[:1500]}\n"

        # Step 3: Create prompt
        prompt = f"""You are a narrative generator for the DOAMMO universe.

RELEVANT LORE CONTEXT (use this to stay consistent):
{lore_context}

USER INPUT:
{user_input}

Generate an engaging narrative response (2-3 paragraphs) that:
- Uses specific details from the lore context
- Stays consistent with the DOAMMO universe
- Is descriptive and immersive
- Responds naturally to what the user described
"""

        # Step 4: Generate with Claude
        print("Generating narrative...\n")

        message = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def run(self):
        """Main interactive loop"""
        if not self.setup():
            return

        print("\n" + "=" * 60)
        print("Ready! Type your scenario and press Enter.")
        print("Type 'quit' or 'exit' to stop.")
        print("=" * 60)

        while True:
            print("\n" + "-" * 60)
            user_input = input("\nYour scenario: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not user_input:
                print("Please enter a scenario!")
                continue

            try:
                # Generate narrative
                narrative = self.generate_narrative(user_input)

                # Display result
                print("\n" + "=" * 60)
                print("NARRATIVE:")
                print("=" * 60)
                print(narrative)
                print("=" * 60)

            except Exception as e:
                print(f"\nERROR: {e}")
                print("Please try again.")

if __name__ == "__main__":
    narrator = DOAMMONarrator()
    narrator.run()
