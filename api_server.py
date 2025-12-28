"""
Milestone 8: FastAPI REST Backend
DOAMMO Narrative Engine API

Run: uvicorn api_server:app --reload
Access: http://localhost:8000/docs
"""

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager

import chromadb
from chromadb.config import Settings
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from typing import TypedDict
import json

from wiki_manager import WikiManager

# ============================================================================
# Pydantic Models for API
# ============================================================================

class NarrativeRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None

class NarrativeResponse(BaseModel):
    narrative: str
    lore_used: List[str]
    quality_check: str
    session_id: str
    timestamp: str

class SessionResponse(BaseModel):
    session_id: str
    message_count: int
    created: str
    updated: str

class HealthResponse(BaseModel):
    status: str
    lore_documents: int
    model: str

# ============================================================================
# LangGraph State and Agents
# ============================================================================

class NarrativeState(TypedDict):
    user_input: str
    session_id: str
    relevant_lore: list
    lore_context: str
    narrative: str
    quality_check: str
    final_output: str

class ConversationManager:
    """Manages conversation history"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.session_file = self.sessions_dir / f"api_{session_id}.json"
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

    def add_message(self, role: str, content: str):
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.conversation_history.append(message)
        self.save_session()

    def get_recent_context(self, max_messages: int = 6) -> str:
        recent = self.conversation_history[-max_messages:] if len(self.conversation_history) > max_messages else self.conversation_history
        context = ""
        for msg in recent:
            role = "You" if msg['role'] == 'user' else "AI"
            context += f"{role}: {msg['content']}\n\n"
        return context

    def get_metadata(self):
        return {
            'session_id': self.session_id,
            'message_count': len(self.conversation_history),
            'created': self.conversation_history[0]['timestamp'] if self.conversation_history else datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

class LoreKeeperAgent:
    def __init__(self, chroma_collection):
        self.collection = chroma_collection

    def __call__(self, state: NarrativeState) -> NarrativeState:
        search_results = self.collection.query(
            query_texts=[state["user_input"]],
            n_results=3
        )

        lore_files = [m['filename'] for m in search_results['metadatas'][0]]

        lore_context = ""
        for i, doc in enumerate(search_results['documents'][0]):
            filename = search_results['metadatas'][0][i]['filename']
            lore_context += f"\n--- {filename} ---\n{doc[:1200]}\n"

        state["relevant_lore"] = lore_files
        state["lore_context"] = lore_context
        return state

class NarratorAgent:
    def __init__(self, llm, conv_managers: dict):
        self.llm = llm
        self.conv_managers = conv_managers

    def __call__(self, state: NarrativeState) -> NarrativeState:
        session_id = state["session_id"]
        conv_manager = self.conv_managers.get(session_id)

        recent_context = conv_manager.get_recent_context() if conv_manager else ""

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

        response = self.llm.invoke(prompt)
        state["narrative"] = response.content
        return state

class QualityAgent:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: NarrativeState) -> NarrativeState:
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
- "NEEDS REVISION: [issues]" if there are problems
"""

        response = self.llm.invoke(prompt)
        state["quality_check"] = response.content
        state["final_output"] = state["narrative"]
        return state

# ============================================================================
# Global State
# ============================================================================

chroma_collection = None
llm = None
workflow_app = None
conv_managers = {}
wiki_manager = None

# ============================================================================
# Lifespan Context Manager (must be defined before app initialization)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize system on startup and cleanup on shutdown"""
    global chroma_collection, llm, workflow_app, wiki_manager

    print("Initializing DOAMMO Narrative Engine API...")

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
        raise RuntimeError("API key not found in .env file")

    # Connect to ChromaDB
    chroma_path = Path("chroma_data")
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False)
    )
    chroma_collection = client.get_collection(name="doammo_lore")
    print(f"Connected to lore database ({chroma_collection.count()} documents)")

    # Initialize LLM
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=api_key,
        max_tokens=600
    )

    # Create agents
    lore_keeper = LoreKeeperAgent(chroma_collection)
    narrator = NarratorAgent(llm, conv_managers)
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
    workflow_app = workflow.compile()

    # Initialize Wiki Manager
    wiki_manager = WikiManager()
    print(f"Wiki Manager initialized (user_data directory)")

    print("API ready!")

    yield  # Server runs here

    # Cleanup (runs on shutdown)
    print("Shutting down...")

# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="DOAMMO Narrative Engine API",
    description="AI-powered interactive storytelling for the DOAMMO universe",
    version="1.0.0",
    lifespan=lifespan
)

# Set up templates for HTML frontend
templates = Jinja2Templates(directory="templates")

# Add CORS middleware to allow web frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the web frontend"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api", response_model=dict)
async def api_root():
    """API root - basic info"""
    return {
        "name": "DOAMMO Narrative Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running and connected to all services"""
    if not chroma_collection:
        raise HTTPException(status_code=503, detail="ChromaDB not initialized")

    return HealthResponse(
        status="healthy",
        lore_documents=chroma_collection.count(),
        model="claude-sonnet-4-20250514"
    )

@app.post("/narrative", response_model=NarrativeResponse)
async def generate_narrative(request: NarrativeRequest):
    """Generate a narrative based on user input"""

    # Generate or use existing session ID
    session_id = request.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    # Get or create conversation manager
    if session_id not in conv_managers:
        conv_managers[session_id] = ConversationManager(session_id)

    conv_manager = conv_managers[session_id]

    # Add user input to conversation history
    conv_manager.add_message('user', request.user_input)

    # Run through workflow
    initial_state = {
        "user_input": request.user_input,
        "session_id": session_id,
        "relevant_lore": [],
        "lore_context": "",
        "narrative": "",
        "quality_check": "",
        "final_output": ""
    }

    try:
        result = workflow_app.invoke(initial_state)

        # Add AI response to conversation history
        conv_manager.add_message('assistant', result["final_output"])

        return NarrativeResponse(
            narrative=result["final_output"],
            lore_used=result["relevant_lore"],
            quality_check=result["quality_check"],
            session_id=session_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get information about a conversation session"""

    session_file = Path("sessions") / f"api_{session_id}.json"

    if not session_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    with open(session_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return SessionResponse(
        session_id=data['session_id'],
        message_count=len(data['history']),
        created=data['created'],
        updated=data['updated']
    )

@app.get("/sessions", response_model=List[str])
async def list_sessions():
    """List all available session IDs"""
    sessions_dir = Path("sessions")

    if not sessions_dir.exists():
        return []

    session_files = list(sessions_dir.glob("api_*.json"))
    session_ids = [f.stem.replace("api_", "") for f in session_files]

    return session_ids

@app.post("/session/{session_id}/undo")
async def undo_last_turn(session_id: str):
    """Remove the last user message and AI response from session"""
    if session_id not in conv_managers:
        raise HTTPException(status_code=404, detail="Session not found")

    conv_manager = conv_managers[session_id]

    if len(conv_manager.conversation_history) < 2:
        return {"success": False, "message": "Not enough messages to undo"}

    # Remove last 2 messages (AI response, then user message)
    conv_manager.conversation_history = conv_manager.conversation_history[:-2]
    conv_manager.save_session()

    return {
        "success": True,
        "message_count": len(conv_manager.conversation_history),
        "message": "Last turn removed successfully"
    }

@app.post("/session/{session_id}/edit")
async def edit_message(session_id: str, edit_data: dict):
    """Edit a message in the conversation history"""
    if session_id not in conv_managers:
        raise HTTPException(status_code=404, detail="Session not found")

    conv_manager = conv_managers[session_id]
    message_index = edit_data.get("message_index")
    new_content = edit_data.get("new_content")

    if message_index is None or new_content is None:
        raise HTTPException(status_code=400, detail="Missing message_index or new_content")

    if message_index >= len(conv_manager.conversation_history) or message_index < 0:
        raise HTTPException(status_code=400, detail="Invalid message index")

    # Update the message content
    conv_manager.conversation_history[message_index]["content"] = new_content
    conv_manager.conversation_history[message_index]["edited"] = datetime.now().isoformat()
    conv_manager.save_session()

    return {
        "success": True,
        "message": "Message edited successfully"
    }

@app.get("/session/{session_id}/export")
async def export_session(session_id: str):
    """Export conversation as text file"""
    if session_id not in conv_managers:
        raise HTTPException(status_code=404, detail="Session not found")

    conv_manager = conv_managers[session_id]

    if not conv_manager.conversation_history:
        raise HTTPException(status_code=400, detail="No messages to export")

    # Format conversation as readable text
    text = f"DOAMMO Story Export\n"
    text += f"Session ID: {session_id}\n"

    # Get timestamps
    metadata = conv_manager.get_metadata()
    text += f"Created: {metadata['created']}\n"
    text += f"Updated: {metadata['updated']}\n"
    text += f"Total Messages: {metadata['message_count']}\n"
    text += f"\n{'='*60}\n\n"

    for msg in conv_manager.conversation_history:
        role = "You" if msg['role'] == 'user' else "AI Narrator"
        text += f"{role}:\n{msg['content']}\n\n"
        text += f"{'-'*60}\n\n"

    return Response(
        content=text,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=DOAMMO_Story_{session_id}.txt"
        }
    )

# ============================================================================
# Wiki API Endpoints
# ============================================================================

@app.post("/wiki/create")
async def create_wiki(data: dict):
    """Create a new story wiki"""
    wiki_name = data.get("name")
    description = data.get("description", "")

    if not wiki_name:
        raise HTTPException(status_code=400, detail="Wiki name is required")

    try:
        metadata = wiki_manager.create_wiki(wiki_name, description)
        return {
            "success": True,
            "wiki": metadata
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wiki/list")
async def list_wikis():
    """List all available wikis"""
    wikis = wiki_manager.list_wikis()
    return {
        "success": True,
        "wikis": wikis
    }

@app.get("/wiki/{wiki_name}")
async def get_wiki(wiki_name: str):
    """Get wiki metadata and sessions list"""
    try:
        metadata = wiki_manager.get_wiki_metadata(wiki_name)
        sessions = wiki_manager.load_wiki_sessions(wiki_name)
        pages = wiki_manager.list_wiki_pages(wiki_name)

        return {
            "success": True,
            "metadata": metadata,
            "sessions": sessions,
            "pages": pages
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/wiki/{wiki_name}/save_session")
async def save_session_to_wiki(wiki_name: str, data: dict):
    """Save current session to wiki"""
    session_id = data.get("session_id")

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    if session_id not in conv_managers:
        raise HTTPException(status_code=404, detail="Session not found")

    conv_manager = conv_managers[session_id]

    try:
        wiki_manager.save_session_to_wiki(
            wiki_name,
            session_id,
            conv_manager.conversation_history
        )
        return {
            "success": True,
            "message": f"Session saved to wiki '{wiki_name}'"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/wiki/{wiki_name}/session/{session_id}")
async def load_session_from_wiki(wiki_name: str, session_id: str):
    """Load a session from a wiki"""
    try:
        conversation = wiki_manager.load_session_from_wiki(wiki_name, session_id)
        return {
            "success": True,
            "conversation": conversation
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/wiki/{wiki_name}/page/{category}/{page_name}")
async def read_wiki_page(wiki_name: str, category: str, page_name: str):
    """Read a wiki page"""
    try:
        content = wiki_manager.read_wiki_page(wiki_name, category, page_name)
        return {
            "success": True,
            "content": content
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/wiki/{wiki_name}/page/{category}/{page_name}")
async def write_wiki_page(wiki_name: str, category: str, page_name: str, data: dict):
    """Create or update a wiki page"""
    content = data.get("content")

    if content is None:
        raise HTTPException(status_code=400, detail="Content is required")

    try:
        wiki_manager.write_wiki_page(wiki_name, category, page_name, content)
        return {
            "success": True,
            "message": f"Page '{page_name}' saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/wiki/{wiki_name}/page/{category}/{page_name}")
async def delete_wiki_page(wiki_name: str, category: str, page_name: str):
    """Delete a wiki page"""
    try:
        wiki_manager.delete_wiki_page(wiki_name, category, page_name)
        return {
            "success": True,
            "message": f"Page '{page_name}' deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (must be last to not interfere with API routes)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
