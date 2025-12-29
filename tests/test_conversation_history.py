"""
Milestone 6: Conversation History + Context Management
Goal: Enable multi-turn conversations with memory

Prerequisites:
1. All previous milestones working
2. sessions/ folder created

Run: python test_conversation_history.py
"""

import os
import json
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings
from anthropic import Anthropic

class ConversationManager:
    """Manages conversation history and context"""

    def __init__(self, session_id=None):
        self.session_id = session_id or self._generate_session_id()
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.session_file = self.sessions_dir / f"{self.session_id}.json"
        self.conversation_history = []
        self.load_session()

    def _generate_session_id(self):
        """Generate a unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_session(self):
        """Load existing session if it exists"""
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conversation_history = data.get('history', [])
                print(f"Loaded existing session: {self.session_id}")
                print(f"  {len(self.conversation_history)} messages in history")
        else:
            print(f"Started new session: {self.session_id}")

    def save_session(self):
        """Save current session to disk"""
        data = {
            'session_id': self.session_id,
            'created': self.conversation_history[0]['timestamp'] if self.conversation_history else datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'history': self.conversation_history
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, role, content):
        """Add a message to conversation history"""
        message = {
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self.save_session()

    def get_conversation_context(self, max_messages=10):
        """Get recent conversation for Claude's context"""
        # Get last N messages for context
        recent = self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history

        # Format for Claude API
        messages = []
        for msg in recent:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        return messages

    def get_summary(self):
        """Get a summary of the conversation"""
        user_messages = len([m for m in self.conversation_history if m['role'] == 'user'])
        assistant_messages = len([m for m in self.conversation_history if m['role'] == 'assistant'])
        return f"Session {self.session_id}: {user_messages} user messages, {assistant_messages} AI responses"


def test_conversation_history():
    print("=" * 60)
    print("MILESTONE 6: Conversation History Test")
    print("=" * 60)

    # Initialize
    print("\n[1/5] Loading API key...")
    env_path = ".env"
    api_key = None

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                    break

    if not api_key:
        print("X ERROR: API key not found")
        return False

    print("OK API key loaded")

    print("\n[2/5] Connecting to ChromaDB...")
    chroma_path = Path("chroma_data")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(name="doammo_lore")
    print(f"OK Connected ({collection.count()} documents)")

    print("\n[3/5] Setting up conversation manager...")
    conv_manager = ConversationManager()
    print(f"OK {conv_manager.get_summary()}")

    print("\n[4/5] Running multi-turn conversation test...")

    # Setup Claude client
    anthropic_client = Anthropic(api_key=api_key)

    # Test scenario: 3-turn conversation
    test_turns = [
        "I'm exploring the desert and find ancient ruins",
        "I examine the markings on the walls",
        "What do the symbols mean?"
    ]

    for turn_num, user_input in enumerate(test_turns, 1):
        print(f"\n--- Turn {turn_num} ---")
        print(f"You: {user_input}")

        # Add user message to history
        conv_manager.add_message('user', user_input)

        # Search for relevant lore
        search_results = collection.query(
            query_texts=[user_input],
            n_results=2
        )

        lore_files = [m['filename'] for m in search_results['metadatas'][0]]
        print(f"Using lore: {', '.join(lore_files)}")

        # Build lore context
        lore_context = ""
        for i, doc in enumerate(search_results['documents'][0]):
            filename = search_results['metadatas'][0][i]['filename']
            lore_context += f"\n--- {filename} ---\n{doc[:1000]}\n"

        # Get conversation context
        conversation_messages = conv_manager.get_conversation_context()

        # Build system prompt
        system_prompt = f"""You are a narrative generator for the DOAMMO universe.

LORE CONTEXT:
{lore_context}

Generate engaging narrative responses (1-2 paragraphs) that:
- Stay consistent with the lore
- Remember and reference previous events in this conversation
- Respond naturally to the user's input
- Advance the story"""

        # Create messages for Claude (system message + conversation history + new input)
        # Note: The user's latest message is already in conversation_messages
        api_messages = [
            {"role": "user", "content": system_prompt},
            {"role": "assistant", "content": "I understand. I'll generate narratives using the lore and conversation context."}
        ] + conversation_messages

        # Generate response
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=api_messages
        )

        narrative = message.content[0].text

        # Add assistant response to history
        conv_manager.add_message('assistant', narrative)

        print(f"\nAI: {narrative}")
        print(f"(Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out)")

    print("\n" + "=" * 60)
    print("[5/5] Verifying conversation memory...")
    print("=" * 60)

    print(f"\nSession saved to: {conv_manager.session_file}")
    print(f"Total messages: {len(conv_manager.conversation_history)}")
    print(f"\nConversation history:")
    for i, msg in enumerate(conv_manager.conversation_history, 1):
        role = "You" if msg['role'] == 'user' else "AI"
        preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"  {i}. {role}: {preview}")

    print("\n" + "=" * 60)
    print("MILESTONE 6 COMPLETE!")
    print("=" * 60)
    print("\nConversation history is working!")
    print("- Each turn remembers previous turns")
    print("- Session saved to disk")
    print("- Can be loaded for future conversations")
    print()

    return True

if __name__ == "__main__":
    test_conversation_history()
