"""
Milestone 7: LangGraph Multi-Agent Workflows
Goal: Create specialized AI agents that work together

Prerequisites:
1. LangGraph installed
2. All previous milestones working

This implements a multi-agent system with:
- Lore Keeper Agent: Finds relevant lore
- Narrator Agent: Generates narrative text
- Quality Agent: Ensures consistency with lore

Run: python test_langgraph_agents.py
"""

import os
from pathlib import Path
from typing import TypedDict, Annotated
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
import chromadb
from chromadb.config import Settings

# Define the state that flows through the workflow
class NarrativeState(TypedDict):
    """State that gets passed between agents"""
    user_input: str
    relevant_lore: list[str]
    lore_context: str
    narrative: str
    quality_check: str
    final_output: str


class LoreKeeperAgent:
    """Agent responsible for finding relevant lore"""

    def __init__(self, chroma_collection):
        self.collection = chroma_collection

    def __call__(self, state: NarrativeState) -> NarrativeState:
        """Find relevant lore for the user's input"""
        print("\n[Lore Keeper Agent] Searching for relevant lore...")

        user_input = state["user_input"]

        # Search ChromaDB for relevant lore
        search_results = self.collection.query(
            query_texts=[user_input],
            n_results=3
        )

        # Get the lore files found
        lore_files = [m['filename'] for m in search_results['metadatas'][0]]
        print(f"  Found: {', '.join(lore_files)}")

        # Build lore context
        lore_context = ""
        for i, doc in enumerate(search_results['documents'][0]):
            filename = search_results['metadatas'][0][i]['filename']
            lore_context += f"\n--- {filename} ---\n{doc[:1200]}\n"

        # Update state
        state["relevant_lore"] = lore_files
        state["lore_context"] = lore_context

        return state


class NarratorAgent:
    """Agent responsible for generating narrative"""

    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: NarrativeState) -> NarrativeState:
        """Generate narrative using the lore context"""
        print("\n[Narrator Agent] Generating narrative...")

        # Build prompt
        prompt = f"""You are the Narrator for the DOAMMO universe.

RELEVANT LORE:
{state['lore_context']}

USER INPUT:
{state['user_input']}

Generate an engaging narrative response (2-3 paragraphs) that:
- Uses specific details from the lore
- Stays consistent with the DOAMMO universe
- Is descriptive and immersive
- Responds naturally to the user's input
"""

        # Generate narrative
        response = self.llm.invoke(prompt)
        narrative = response.content

        print(f"  Generated {len(narrative)} characters")

        # Update state
        state["narrative"] = narrative

        return state


class QualityAgent:
    """Agent responsible for checking narrative quality and lore consistency"""

    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: NarrativeState) -> NarrativeState:
        """Check if the narrative is consistent with lore"""
        print("\n[Quality Agent] Checking narrative quality...")

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

Respond with either:
- "APPROVED: [brief comment]" if it's good
- "NEEDS REVISION: [specific issues]" if there are problems
"""

        # Get quality check
        response = self.llm.invoke(prompt)
        quality_check = response.content

        print(f"  Result: {quality_check[:100]}...")

        # Update state
        state["quality_check"] = quality_check

        # For now, always approve (in a full system, you'd loop back if rejected)
        state["final_output"] = state["narrative"]

        return state


def test_langgraph_agents():
    print("=" * 60)
    print("MILESTONE 7: LangGraph Multi-Agent System")
    print("=" * 60)

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

    print("\n[3/5] Initializing LLM and agents...")

    # Initialize Claude LLM for LangChain
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=500
    )

    # Create agents
    lore_keeper = LoreKeeperAgent(collection)
    narrator = NarratorAgent(llm)
    quality = QualityAgent(llm)

    print("OK Agents initialized")

    print("\n[4/5] Building LangGraph workflow...")

    # Create workflow graph
    workflow = StateGraph(NarrativeState)

    # Add nodes (agents)
    workflow.add_node("lore_keeper", lore_keeper)
    workflow.add_node("narrator", narrator)
    workflow.add_node("quality", quality)

    # Define the workflow
    workflow.set_entry_point("lore_keeper")  # Start with lore search
    workflow.add_edge("lore_keeper", "narrator")  # Then generate narrative
    workflow.add_edge("narrator", "quality")  # Then check quality
    workflow.add_edge("quality", END)  # Then finish

    # Compile the graph
    app = workflow.compile()

    print("OK Workflow compiled")

    print("\n[5/5] Running test scenario through multi-agent workflow...")
    print("=" * 60)

    # Test scenario
    user_input = "I discover a hidden chamber in the megastructure. What's inside?"

    print(f"\nUser Input: {user_input}")
    print("\n" + "-" * 60)

    # Run through the workflow
    initial_state = {
        "user_input": user_input,
        "relevant_lore": [],
        "lore_context": "",
        "narrative": "",
        "quality_check": "",
        "final_output": ""
    }

    result = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL NARRATIVE:")
    print("=" * 60)
    print(result["final_output"])
    print("=" * 60)

    print("\n" + "=" * 60)
    print("MILESTONE 7 COMPLETE!")
    print("=" * 60)
    print("\nMulti-agent workflow successfully orchestrated!")
    print(f"\nWorkflow steps:")
    print(f"  1. Lore Keeper found: {', '.join(result['relevant_lore'])}")
    print(f"  2. Narrator generated narrative")
    print(f"  3. Quality Agent reviewed: {result['quality_check'][:80]}...")
    print(f"\nThis demonstrates agent specialization and orchestration.")
    print()

    return True

if __name__ == "__main__":
    test_langgraph_agents()
