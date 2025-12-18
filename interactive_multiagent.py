"""
Interactive Multi-Agent Narrative System
Combines LangGraph agents with conversation history for detailed interactive sessions

Run: python interactive_multiagent.py
"""

import os
from pathlib import Path
from typing import TypedDict
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
import chromadb
from chromadb.config import Settings
import json
from datetime import datetime

# Define the state that flows through the workflow
class NarrativeState(TypedDict):
    """State that gets passed between agents"""
    user_input: str
    relevant_lore: list[str]
    lore_context: str
    narrative: str
    quality_check: str
    final_output: str


class ConversationManager:
    """Manages conversation history"""

    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.session_file = self.sessions_dir / f"multiagent_{self.session_id}.json"
        self.conversation_history = []
        self.load_session()

    def load_session(self):
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.conversation_history = data.get('history', [])

    def save_session(self):
        data = {
            'session_id': self.session_id,
            'created': self.conversation_history[0]['timestamp'] if self.conversation_history else datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'history': self.conversation_history
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, role, content):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self.save_session()

    def get_recent_context(self, max_messages=6):
        """Get recent conversation for context"""
        recent = self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history

        context = ""
        for msg in recent:
            role = "You" if msg['role'] == 'user' else "AI"
            context += f"{role}: {msg['content']}\n\n"
        return context


class LoreKeeperAgent:
    """Agent responsible for finding relevant lore"""

    def __init__(self, chroma_collection):
        self.collection = chroma_collection

    def __call__(self, state: NarrativeState) -> NarrativeState:
        print("\n" + "=" * 60)
        print("[LORE KEEPER AGENT]")
        print("=" * 60)
        print("Searching for relevant lore...")

        user_input = state["user_input"]

        # Search ChromaDB for relevant lore
        search_results = self.collection.query(
            query_texts=[user_input],
            n_results=3
        )

        # Get the lore files found
        lore_files = [m['filename'] for m in search_results['metadatas'][0]]
        print(f"\nFound {len(lore_files)} relevant lore documents:")
        for i, filename in enumerate(lore_files, 1):
            distance = search_results['distances'][0][i-1]
            print(f"  {i}. {filename} (relevance score: {distance:.4f})")

        # Build lore context
        lore_context = ""
        for i, doc in enumerate(search_results['documents'][0]):
            filename = search_results['metadatas'][0][i]['filename']
            preview = doc[:1200]
            lore_context += f"\n--- {filename} ---\n{preview}\n"
            print(f"\n  Preview from {filename}:")
            print(f"  {doc[:150]}...")

        # Update state
        state["relevant_lore"] = lore_files
        state["lore_context"] = lore_context

        return state


class NarratorAgent:
    """Agent responsible for generating narrative"""

    def __init__(self, llm, conv_manager):
        self.llm = llm
        self.conv_manager = conv_manager

    def __call__(self, state: NarrativeState) -> NarrativeState:
        print("\n" + "=" * 60)
        print("[NARRATOR AGENT]")
        print("=" * 60)
        print("Generating narrative using lore and conversation context...")

        # Get conversation context
        recent_context = self.conv_manager.get_recent_context()

        # Build prompt
        prompt = f"""You are the Narrator for the DOAMMO universe.

RELEVANT LORE:
{state['lore_context']}

RECENT CONVERSATION CONTEXT:
{recent_context}

CURRENT USER INPUT:
{state['user_input']}

Generate an engaging narrative response (2-3 paragraphs) that:
- Uses specific details from the lore
- Stays consistent with the DOAMMO universe
- References and builds on the recent conversation context
- Is descriptive and immersive
- Responds naturally to the user's current input
"""

        # Generate narrative
        response = self.llm.invoke(prompt)
        narrative = response.content

        print(f"\nGenerated narrative ({len(narrative)} characters):")
        print("-" * 60)
        print(narrative)
        print("-" * 60)

        # Update state
        state["narrative"] = narrative

        return state


class QualityAgent:
    """Agent responsible for checking narrative quality and lore consistency"""

    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: NarrativeState) -> NarrativeState:
        print("\n" + "=" * 60)
        print("[QUALITY AGENT]")
        print("=" * 60)
        print("Reviewing narrative for lore consistency and quality...")

        # Build prompt
        prompt = f"""You are the Quality Keeper for the DOAMMO universe.

LORE CONTEXT:
{state['lore_context']}

GENERATED NARRATIVE:
{state['narrative']}

Review the narrative and check:
1. Does it contradict any lore?
2. Does it use appropriate DOAMMO universe terminology?
3. Is it engaging and well-written?
4. Does it maintain narrative consistency?

Respond with either:
- "APPROVED: [brief positive comment]" if it's good
- "NEEDS REVISION: [specific issues]" if there are problems

Be specific about what works or what needs improvement.
"""

        # Get quality check
        response = self.llm.invoke(prompt)
        quality_check = response.content

        print(f"\nQuality review:")
        print("-" * 60)
        print(quality_check)
        print("-" * 60)

        # Update state
        state["quality_check"] = quality_check
        state["final_output"] = state["narrative"]

        return state


def main():
    print("=" * 60)
    print("DOAMMO INTERACTIVE MULTI-AGENT NARRATIVE SYSTEM")
    print("=" * 60)

    # Setup
    print("\nInitializing system...")

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
        print("ERROR: API key not found in .env")
        return

    # Connect to ChromaDB
    chroma_path = Path("chroma_data")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(name="doammo_lore")
    print(f"Connected to lore database ({collection.count()} documents)")

    # Initialize conversation manager
    conv_manager = ConversationManager()
    print(f"Session: {conv_manager.session_id}")

    # Initialize LLM
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=600
    )

    # Create agents
    lore_keeper = LoreKeeperAgent(collection)
    narrator = NarratorAgent(llm, conv_manager)
    quality = QualityAgent(llm)

    # Build workflow
    workflow = StateGraph(NarrativeState)
    workflow.add_node("lore_keeper", lore_keeper)
    workflow.add_node("narrator", narrator)
    workflow.add_node("quality", quality)
    workflow.set_entry_point("lore_keeper")
    workflow.add_edge("lore_keeper", "narrator")
    workflow.add_edge("narrator", "quality")
    workflow.add_edge("quality", END)
    app = workflow.compile()

    print("\nSystem ready!")
    print("\n" + "=" * 60)
    print("Type your narrative input and press Enter.")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # Interactive loop
    while True:
        print("\n" + ">" * 60)
        user_input = input("\nYour input: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\nSession saved to: {conv_manager.session_file}")
            print("Goodbye!")
            break

        if not user_input:
            print("Please enter something!")
            continue

        try:
            # Add user message to history
            conv_manager.add_message('user', user_input)

            # Run through workflow
            initial_state = {
                "user_input": user_input,
                "relevant_lore": [],
                "lore_context": "",
                "narrative": "",
                "quality_check": "",
                "final_output": ""
            }

            result = app.invoke(initial_state)

            # Add AI response to history
            conv_manager.add_message('assistant', result["final_output"])

            print("\n" + "=" * 60)
            print("[FINAL NARRATIVE]")
            print("=" * 60)
            print(result["final_output"])
            print("=" * 60)

        except Exception as e:
            print(f"\nERROR: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
