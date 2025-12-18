[[_DOAMMO_Development_Milestones]]
# DOAMMO Interactive Narrative AI System - Implementation Guide

Note: there mnay be a SillyTavern folder somewhere in the project, if so, that is simply for reference. dont alter anything in the SillyTavern, think ofit as "read only".
 

## Project Overview

An intelligent, locally-operated narrative assistant serving as both AI Dungeon Master and creative writing tool for the DOAMMO universe. The system orchestrates multiple specialized AI agents to maintain strict lore consistency while generating dynamic, engaging narratives through semantic search and multi-agent verification.

**Primary Use Cases**:
- Interactive storytelling sessions (user as player, AI as DM/narrator)
- Creative writing assistance with automatic lore consistency checking
- Character interaction simulation with deep personality modeling
- Collaborative D&D-style sessions with friends on local network

**Project Philosophy**: Hobby-first with pragmatic choices. Build locally, make it work well, add complexity only when needed. Future commercial migration possible but not driving current decisions.

---

## Technology Stack

### Backend
**FastAPI** (Python web framework)
- Modern async support for agent orchestration
- Automatic API documentation (OpenAPI/Swagger)
- Type hints with Pydantic validation
- Easy network access for friends (`--network` flag)
- Cloud migration path if needed later

**SQLAlchemy** (Database ORM)
- Abstraction over SQLite (now) and PostgreSQL (if commercial later)
- One line change to migrate databases
- Handles sessions, state, conversation history

**LangChain + LangGraph** (AI orchestration)
- LangChain: LLM connections, embeddings, prompts, tools
- LangGraph: Multi-agent workflow with conditional branching and loops
- Built for complex agentic systems with regeneration logic

**ChromaDB** (Vector database)
- Local-first, file-based semantic search
- Embeds lore documents for "magical compass" retrieval
- No server required, completely private

### Frontend
**HTML/CSS/JavaScript** (Pure web stack)
- Reference: SillyTavern codebase for UI patterns
- Works in browser (localhost or network)
- Can wrap with Electron/Tauri later for desktop app

**SillyTavern as Template**:
- Clone repo locally for reference
- Extract: character cards, world info patterns, chat UI, settings
- Adapt: simplified versions tailored to DOAMMO
- Skip: Node.js backend, complex extensions, features not needed

### Data Storage
**SQLite** (Primary database)
- Zero-setup file-based database
- Handles sessions, state, user data, conversation history
- Migrates to PostgreSQL easily if needed

**Local Filesystem** (Lore storage)
- Obsidian vault: `C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault`
- Markdown files for all lore
- ChromaDB indexes these files
- Git-compatible for version control

**ChromaDB Storage** (Vector embeddings)
- `./chroma_data/` directory
- Embedded representations of vault documents
- Persists between sessions

### LLM Backend
**LM Studio** (Local AI inference)
- Already installed and familiar
- OpenAI-compatible API at `localhost:1234`
- Runs Llama, Mistral, or other local models
- Network-accessible for friends' connections

---

## Architecture Overview

### Request Flow
```
User Input (Frontend)
    ↓ HTTP POST
FastAPI Endpoint
    ↓
LangGraph Orchestrator
    ↓
┌─────────────────────────────────────┐
│  Sequential Agent Pipeline:         │
│  1. Input Analyzer                  │
│  2. Lore Retriever (ChromaDB)       │
│  3. Continuity Agent                │
│  4. Drama/Pacing Agent              │
│  5. Narrative Generator (LM Studio) │
│  6. Consistency Checker             │
│      ↓                              │
│  [Pass] → State Updater             │
│  [Fail] → Loop back to Generator    │
└─────────────────────────────────────┘
    ↓
State Saved (SQLite)
    ↓
Response (JSON)
    ↓ HTTP Response
Frontend Displays Narrative
```

### Directory Structure
```
doammo-narrative-engine/
├── backend/
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Configuration management
│   ├── database/
│   │   ├── db.py                   # SQLite connection & models
│   │   ├── models.py               # SQLAlchemy models
│   │   └── migrations/             # Schema changes (if needed)
│   ├── agents/
│   │   ├── base_agent.py           # Abstract base class
│   │   ├── input_analyzer.py      # Extract entities/intent
│   │   ├── lore_retriever.py      # ChromaDB semantic search
│   │   ├── continuity_agent.py    # Track narrative flow
│   │   ├── drama_pacing.py        # Suggest narrative beats
│   │   ├── generator.py           # Main LLM call
│   │   ├── consistency_checker.py # Validate against lore
│   │   └── state_updater.py       # Extract state changes
│   ├── workflow/
│   │   └── narrative_graph.py     # LangGraph orchestration
│   ├── services/
│   │   ├── llm_client.py          # LM Studio connection
│   │   ├── chroma_client.py       # ChromaDB wrapper
│   │   ├── vault_reader.py        # Read Obsidian files
│   │   └── context_builder.py     # Assemble prompts
│   └── api/
│       └── routes.py               # API endpoints
├── frontend/
│   ├── index.html                  # Main page
│   ├── css/
│   │   └── styles.css              # Styling (adapted from SillyTavern)
│   ├── js/
│   │   ├── app.js                  # Main application logic
│   │   ├── api.js                  # Backend communication
│   │   ├── chat.js                 # Chat UI (from SillyTavern pattern)
│   │   ├── characters.js           # Character management
│   │   └── state.js                # State visualization
│   └── assets/
│       ├── images/                 # Character avatars, locations
│       └── audio/                  # Background music (optional)
├── vault/                          # Symlink to Obsidian vault
├── chroma_data/                    # ChromaDB storage
├── doammo.db                       # SQLite database
├── requirements.txt                # Python dependencies
├── .env                            # Configuration (gitignored)
└── README.md                       # Setup instructions
```

---

## Database Schema

### SQLite Tables

**sessions** (User sessions)
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    vault_id TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON  -- Additional session info
);
```

**game_state** (Current state per session)
```sql
CREATE TABLE game_state (
    session_id TEXT PRIMARY KEY,
    state JSON NOT NULL,  -- Complete game state as JSON
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

**conversation_history** (Turn-by-turn history)
```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    user_input TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    state_snapshot JSON,  -- State at this turn
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

**lore_metadata** (Track vault documents)
```sql
CREATE TABLE lore_metadata (
    file_path TEXT PRIMARY KEY,
    category TEXT,
    last_modified TIMESTAMP,
    embedding_status TEXT,  -- 'pending', 'embedded', 'error'
    checksum TEXT  -- MD5 hash to detect changes
);
```

### State JSON Structure
```json
{
  "characters": {
    "lyssia": {
      "mood": "cautious",
      "trust_sundy": 73,
      "location": "desert_gate_approach",
      "health": 85,
      "inventory": ["sidearm", "canteen", "map"],
      "active_modifiers": ["high_stress"]
    }
  },
  "world": {
    "location": "desert_gate",
    "time_of_day": "dusk",
    "weather": "clear",
    "gates": {
      "gate_alpha": "locked"
    }
  },
  "quest_flags": {
    "discovered_tracks": true,
    "met_patrol": false
  },
  "narrative_state": {
    "tension_level": "medium",
    "last_major_event": "approached_gate",
    "unresolved_threads": ["need_keycard", "low_fuel"]
  },
  "turn_count": 15
}
```

---

## Configuration Management

**config.py**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server
    host: str = "localhost"
    port: int = 5000
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///doammo.db"
    
    # Vault
    vault_path: str = "C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault"
    
    # ChromaDB
    chroma_path: str = "./chroma_data"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LM Studio
    lm_studio_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "local-model"
    
    # Agent settings
    max_regeneration_attempts: int = 3
    consistency_threshold: float = 0.85
    
    # Network mode
    allow_network_access: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**.env** (user-specific, gitignored)
```
DEBUG=true
VAULT_PATH=C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault
ALLOW_NETWORK_ACCESS=false
```

---

## Backend Implementation

### 1. FastAPI Application (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import argparse
from config import settings
from api.routes import router
from database.db import init_database

app = FastAPI(
    title="DOAMMO Narrative Engine",
    description="AI-powered interactive storytelling system",
    version="0.1.0"
)

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include API routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    init_database()
    # Initialize ChromaDB
    from services.chroma_client import init_chroma
    init_chroma()

@app.get("/")
async def root():
    """Serve frontend"""
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--network', action='store_true',
                       help='Allow network access (for friends)')
    args = parser.parse_args()
    
    host = "0.0.0.0" if args.network else "localhost"
    
    uvicorn.run(
        app,
        host=host,
        port=settings.port,
        log_level="info"
    )
```

### 2. Database Models (database/models.py)

```python
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True)
    user_name = Column(String, nullable=False)
    vault_id = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

class GameState(Base):
    __tablename__ = "game_state"
    
    session_id = Column(String, ForeignKey("sessions.session_id"), primary_key=True)
    state = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    user_input = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    state_snapshot = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class LoreMetadata(Base):
    __tablename__ = "lore_metadata"
    
    file_path = Column(String, primary_key=True)
    category = Column(String)
    last_modified = Column(DateTime)
    embedding_status = Column(String, default="pending")
    checksum = Column(String)
```

### 3. Database Connection (database/db.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DBSession
from contextlib import contextmanager
from config import settings
from .models import Base

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # SQLite specific
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db() -> DBSession:
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. LM Studio Client (services/llm_client.py)

```python
import aiohttp
import json
from typing import Optional, Dict, Any
from config import settings

class LMStudioClient:
    """Wrapper for LM Studio API calls"""
    
    def __init__(self):
        self.base_url = settings.lm_studio_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate text from LM Studio"""
        await self._ensure_session()
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": settings.lm_studio_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload
        ) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]
    
    async def close(self):
        if self.session:
            await self.session.close()

# Singleton instance
llm_client = LMStudioClient()
```

### 5. ChromaDB Client (services/chroma_client.py)

```python
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict
from config import settings

class ChromaClient:
    """Wrapper for ChromaDB operations"""
    
    def __init__(self):
        self.client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_path,
            anonymized_telemetry=False
        ))
        self.collections = {}
    
    def get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """Add documents to collection"""
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5
    ) -> List[Dict]:
        """Semantic search in collection"""
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        return formatted

# Singleton instance
chroma_client = ChromaClient()

def init_chroma():
    """Initialize ChromaDB on startup"""
    # Ensure collections exist
    chroma_client.get_or_create_collection("characters")
    chroma_client.get_or_create_collection("locations")
    chroma_client.get_or_create_collection("history")
    chroma_client.get_or_create_collection("technology")
```

### 6. Vault Reader (services/vault_reader.py)

```python
import os
from pathlib import Path
from typing import List, Dict
import hashlib
from config import settings

class VaultReader:
    """Read and manage Obsidian vault files"""
    
    def __init__(self):
        self.vault_path = Path(settings.vault_path)
    
    def list_files(self, category: str = None) -> List[Path]:
        """List all markdown files in vault or category"""
        if category:
            search_path = self.vault_path / category
        else:
            search_path = self.vault_path
        
        return list(search_path.rglob("*.md"))
    
    def read_file(self, file_path: str) -> str:
        """Read markdown file content"""
        full_path = self.vault_path / file_path
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_file_checksum(self, file_path: str) -> str:
        """Get MD5 checksum of file"""
        content = self.read_file(file_path)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_category_from_path(self, file_path: Path) -> str:
        """Extract category from file path"""
        relative = file_path.relative_to(self.vault_path)
        if len(relative.parts) > 1:
            return relative.parts[0]
        return "root"

vault_reader = VaultReader()
```

### 7. LangGraph Orchestrator (workflow/narrative_graph.py)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from agents import (
    input_analyzer,
    lore_retriever,
    continuity_agent,
    drama_pacing,
    generator,
    consistency_checker,
    state_updater
)

class NarrativeState(TypedDict):
    """State passed between agents"""
    # Input
    session_id: str
    user_input: str
    
    # Analysis
    entities: list
    intent: str
    keywords: list
    
    # Lore
    lore_documents: list
    
    # Context
    continuity_notes: dict
    pacing_suggestion: str
    
    # Generation
    narrative: str
    
    # Validation
    consistency_score: float
    issues: list
    regeneration_count: int
    
    # Output
    state_changes: dict

def should_regenerate(state: NarrativeState) -> str:
    """Decide if narrative should be regenerated"""
    if state["consistency_score"] > 0.85:
        return "finalize"
    elif state["regeneration_count"] < 3:
        return "regenerate"
    else:
        return "finalize"  # Give up after 3 attempts

# Build workflow graph
workflow = StateGraph(NarrativeState)

# Add nodes
workflow.add_node("analyze", input_analyzer.analyze)
workflow.add_node("retrieve_lore", lore_retriever.retrieve)
workflow.add_node("check_continuity", continuity_agent.check)
workflow.add_node("suggest_pacing", drama_pacing.suggest)
workflow.add_node("generate", generator.generate)
workflow.add_node("check_consistency", consistency_checker.check)
workflow.add_node("update_state", state_updater.update)

# Define edges
workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "retrieve_lore")
workflow.add_edge("retrieve_lore", "check_continuity")
workflow.add_edge("check_continuity", "suggest_pacing")
workflow.add_edge("suggest_pacing", "generate")
workflow.add_edge("generate", "check_consistency")

# Conditional edge for regeneration
workflow.add_conditional_edges(
    "check_consistency",
    should_regenerate,
    {
        "regenerate": "generate",
        "finalize": "update_state"
    }
)

workflow.add_edge("update_state", END)

# Compile graph
narrative_graph = workflow.compile()
```

### 8. API Routes (api/routes.py)

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from workflow.narrative_graph import narrative_graph
from database.db import get_db
from database.models import Session, GameState, ConversationHistory
from sqlalchemy.orm import Session as DBSession
import uuid

router = APIRouter()

class NarrativeRequest(BaseModel):
    session_id: Optional[str] = None
    user_name: str
    user_input: str

class NarrativeResponse(BaseModel):
    session_id: str
    narrative: str
    state: dict
    turn_number: int

@router.post("/narrative", response_model=NarrativeResponse)
async def generate_narrative(
    request: NarrativeRequest,
    db: DBSession = Depends(get_db)
):
    """Main endpoint for narrative generation"""
    
    # Get or create session
    if request.session_id:
        session = db.query(Session).filter(
            Session.session_id == request.session_id
        ).first()
        if not session:
            raise HTTPException(404, "Session not found")
    else:
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            user_name=request.user_name
        )
        db.add(session)
        db.commit()
    
    # Load current state
    game_state = db.query(GameState).filter(
        GameState.session_id == session.session_id
    ).first()
    
    if not game_state:
        # Initialize new state
        initial_state = {
            "characters": {},
            "world": {},
            "quest_flags": {},
            "narrative_state": {},
            "turn_count": 0
        }
        game_state = GameState(
            session_id=session.session_id,
            state=initial_state
        )
        db.add(game_state)
    
    # Get turn number
    turn_number = game_state.state.get("turn_count", 0) + 1
    
    # Run narrative graph
    result = await narrative_graph.ainvoke({
        "session_id": session.session_id,
        "user_input": request.user_input,
        "regeneration_count": 0
    })
    
    # Update state
    updated_state = {**game_state.state, **result["state_changes"]}
    updated_state["turn_count"] = turn_number
    game_state.state = updated_state
    
    # Save conversation history
    history_entry = ConversationHistory(
        session_id=session.session_id,
        turn_number=turn_number,
        user_input=request.user_input,
        ai_response=result["narrative"],
        state_snapshot=updated_state
    )
    db.add(history_entry)
    db.commit()
    
    return NarrativeResponse(
        session_id=session.session_id,
        narrative=result["narrative"],
        state=updated_state,
        turn_number=turn_number
    )

@router.get("/sessions/{session_id}/history")
async def get_history(
    session_id: str,
    limit: int = 10,
    db: DBSession = Depends(get_db)
):
    """Get conversation history for session"""
    history = db.query(ConversationHistory).filter(
        ConversationHistory.session_id == session_id
    ).order_by(
        ConversationHistory.turn_number.desc()
    ).limit(limit).all()
    
    return [
        {
            "turn": h.turn_number,
            "user": h.user_input,
            "ai": h.ai_response,
            "timestamp": h.timestamp
        }
        for h in reversed(history)
    ]
```

---

## Agent Implementations

### Base Agent (agents/base_agent.py)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process state and return updates"""
        pass
    
    def log_info(self, message: str):
        self.logger.info(message)
    
    def log_error(self, message: str):
        self.logger.error(message)
```

### Input Analyzer (agents/input_analyzer.py)

```python
from .base_agent import BaseAgent
from services.llm_client import llm_client
import json

class InputAnalyzer(BaseAgent):
    """Analyzes user input to extract entities, intent, and keywords"""
    
    async def analyze(self, state: dict) -> dict:
        """Extract structured information from user input"""
        
        prompt = f"""Analyze this user input for a narrative game:
"{state['user_input']}"

Extract:
1. Entities mentioned (characters, locations, items)
2. User intent (action, question, dialogue, etc.)
3. Keywords for lore search

Return JSON only:
{{
  "entities": ["entity1", "entity2"],
  "intent": "action|question|dialogue",
  "keywords": ["keyword1", "keyword2"]
}}"""
        
        response = await llm_client.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=200
        )
        
        # Parse JSON
        try:
            analysis = json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback to simple extraction
            analysis = {
                "entities": [],
                "intent": "action",
                "keywords": state['user_input'].lower().split()[:5]
            }
        
        self.log_info(f"Analyzed input: {analysis}")
        
        state.update(analysis)
        return state

input_analyzer = InputAnalyzer()
```

### Lore Retriever (agents/lore_retriever.py)

```python
from .base_agent import BaseAgent
from services.chroma_client import chroma_client

class LoreRetriever(BaseAgent):
    """Retrieves relevant lore from ChromaDB"""
    
    async def retrieve(self, state: dict) -> dict:
        """Search ChromaDB for relevant lore"""
        
        # Build search query from entities and keywords
        search_terms = state.get('entities', []) + state.get('keywords', [])
        query = " ".join(search_terms)
        
        # Search each category
        results = {
            'characters': [],
            'locations': [],
            'history': []
        }
        
        for category in results.keys():
            search_results = chroma_client.search(
                collection_name=category,
                query=query,
                n_results=3
            )
            results[category] = search_results
        
        self.log_info(f"Retrieved {sum(len(v) for v in results.values())} lore documents")
        
        state['lore_documents'] = results
        return state

lore_retriever = LoreRetriever()
```

### Generator (agents/generator.py)

```python
from .base_agent import BaseAgent
from services.llm_client import llm_client

class Generator(BaseAgent):
    """Generates narrative response"""
    
    def _build_context(self, state: dict) -> str:
        """Assemble context from all agent outputs"""
        lore = state.get('lore_documents', {})
        continuity = state.get('continuity_notes', {})
        pacing = state.get('pacing_suggestion', '')
        
        context = "=== LORE CONTEXT ===\n"
        for category, docs in lore.items():
            if docs:
                context += f"\n{category.upper()}:\n"
                for doc in docs[:2]:  # Top 2 per category
                    context += f"- {doc['document'][:500]}\n"
        
        context += f"\n=== CONTINUITY ===\n{continuity}\n"
        context += f"\n=== PACING ===\n{pacing}\n"
        context += f"\n=== USER ACTION ===\n{state['user_input']}\n"
        
        return context
    
    async def generate(self, state: dict) -> dict:
        """Generate narrative response"""
        
        context = self._build_context(state)
        
        system_prompt = """You are a narrative generator for the DOAMMO universe.
Write engaging, lore-consistent narrative in third-person past tense.
Stay consistent with provided lore and continuity notes.
Follow pacing suggestions to maintain dramatic tension."""
        
        narrative = await llm_client.generate(
            system=system_prompt,
            prompt=context,
            temperature=0.8,
            max_tokens=500
        )
        
        state['narrative'] = narrative.strip()
        self.log_info(f"Generated {len(narrative)} characters")
        
        return state

generator = Generator()
```

### Consistency Checker (agents/consistency_checker.py)

```python
from .base_agent import BaseAgent
from services.llm_client import llm_client
import json

class ConsistencyChecker(BaseAgent):
    """Validates narrative against lore"""
    
    async def check(self, state: dict) -> dict:
        """Check narrative for consistency issues"""
        
        narrative = state.get('narrative', '')
        lore_summary = self._summarize_lore(state.get('lore_documents', {}))
        
        prompt = f"""Check this narrative for consistency with established lore:

NARRATIVE:
{narrative}

LORE:
{lore_summary}

Return JSON:
{{
  "consistency_score": 0.0-1.0,
  "issues": ["issue1", "issue2"] or []
}}"""
        
        response = await llm_client.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=300
        )
        
        try:
            result = json.loads(response.strip())
            consistency_score = result.get('consistency_score', 0.9)
            issues = result.get('issues', [])
        except json.JSONDecodeError:
            # Assume pass if can't parse
            consistency_score = 0.9
            issues = []
        
        state['consistency_score'] = consistency_score
        state['issues'] = issues
        state['regeneration_count'] = state.get('regeneration_count', 0) + 1
        
        self.log_info(f"Consistency: {consistency_score:.2f}, Issues: {len(issues)}")
        
        return state
    
    def _summarize_lore(self, lore_docs: dict) -> str:
        """Create brief summary of key lore points"""
        summary = []
        for category, docs in lore_docs.items():
            for doc in docs[:1]:  # Just top doc per category
                summary.append(doc['document'][:200])
        return "\n".join(summary)

consistency_checker = ConsistencyChecker()
```

---

## Frontend Implementation

### Reference SillyTavern Structure

**Clone and study**:
```bash
git clone https://github.com/SillyTavern/SillyTavern.git
cd SillyTavern/public
```

**Key files to reference**:
- `index.html` - Overall page layout
- `css/st-main.css` - Styling patterns
- `scripts/world-info.js` - World info management
- `scripts/characters.js` - Character handling
- `scripts/chat.js` - Message rendering

**Adapt, don't copy**:
- Extract UI patterns (chat bubbles, input forms, settings panels)
- Simplify for DOAMMO needs (remove features not used)
- Rewrite to match your backend API

### HTML Structure (frontend/index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOAMMO Narrative Engine</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div id="app">
        <!-- Header -->
        <header>
            <h1>DOAMMO</h1>
            <div class="session-info">
                <span id="session-id">Session: New</span>
                <span id="user-name">User: Local</span>
            </div>
        </header>

        <!-- Main Container -->
        <div class="main-container">
            <!-- Sidebar (optional - for state/character info) -->
            <aside id="sidebar">
                <h3>Current State</h3>
                <div id="state-display"></div>
            </aside>

            <!-- Chat Area -->
            <main id="chat-container">
                <div id="messages"></div>
                
                <!-- Input Area -->
                <div id="input-area">
                    <textarea 
                        id="user-input" 
                        placeholder="What do you do?"
                        rows="3"
                    ></textarea>
                    <button id="send-btn">Send</button>
                </div>
            </main>
        </div>
    </div>

    <!-- Scripts -->
    <script src="js/api.js"></script>
    <script src="js/chat.js"></script>
    <script src="js/state.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### Main Application Logic (frontend/js/app.js)

```javascript
// Global state
let currentSession = {
    sessionId: null,
    userName: 'Local User',
    state: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Load saved session if exists
    const saved = localStorage.getItem('doammo_session');
    if (saved) {
        currentSession = JSON.parse(saved);
        updateSessionDisplay();
    }
}

function setupEventListeners() {
    const sendBtn = document.getElementById('send-btn');
    const inputArea = document.getElementById('user-input');
    
    sendBtn.addEventListener('click', handleSendMessage);
    
    inputArea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
}

async function handleSendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    addMessage(message, 'user');
    input.value = '';
    
    // Show loading
    showLoading();
    
    try {
        // Call backend
        const response = await API.sendMessage({
            session_id: currentSession.sessionId,
            user_name: currentSession.userName,
            user_input: message
        });
        
        // Update session
        currentSession.sessionId = response.session_id;
        currentSession.state = response.state;
        
        // Display AI response
        addMessage(response.narrative, 'ai');
        
        // Update state display
        updateStateDisplay(response.state);
        
        // Save session
        localStorage.setItem('doammo_session', JSON.stringify(currentSession));
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('Error connecting to backend. Is the server running?', 'system');
    } finally {
        hideLoading();
    }
}

function addMessage(text, type) {
    const container = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = text;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showLoading() {
    const container = document.getElementById('messages');
    const loader = document.createElement('div');
    loader.id = 'loading';
    loader.className = 'message message-system';
    loader.textContent = 'Generating...';
    container.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('loading');
    if (loader) loader.remove();
}

function updateStateDisplay(state) {
    const display = document.getElementById('state-display');
    // Simplified state display
    display.innerHTML = `
        <div class="state-item">Turn: ${state.turn_count}</div>
        <div class="state-item">Location: ${state.world?.location || 'Unknown'}</div>
    `;
}

function updateSessionDisplay() {
    document.getElementById('session-id').textContent = 
        `Session: ${currentSession.sessionId?.substring(0, 8) || 'New'}`;
    document.getElementById('user-name').textContent = 
        `User: ${currentSession.userName}`;
}
```

### API Communication (frontend/js/api.js)

```javascript
const API = {
    baseURL: window.location.origin + '/api',
    
    async sendMessage(data) {
        const response = await fetch(`${this.baseURL}/narrative`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    },
    
    async getHistory(sessionId, limit = 10) {
        const response = await fetch(
            `${this.baseURL}/sessions/${sessionId}/history?limit=${limit}`
        );
        return await response.json();
    }
};
```

### Basic Styling (frontend/css/styles.css)

```css
/* Reference SillyTavern's st-main.css for inspiration */
/* Simplified version for DOAMMO */

:root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent: #4a90e2;
    --user-msg: #3a5a7a;
    --ai-msg: #2d4a2d;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    height: 100vh;
    overflow: hidden;
}

#app {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

header {
    background: var(--bg-secondary);
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--accent);
}

.main-container {
    display: flex;
    flex: 1;
    overflow: hidden;
}

#sidebar {
    width: 250px;
    background: var(--bg-secondary);
    padding: 1rem;
    overflow-y: auto;
    border-right: 1px solid #444;
}

#chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

#messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
}

.message {
    margin: 1rem 0;
    padding: 1rem;
    border-radius: 8px;
    max-width: 80%;
}

.message-user {
    background: var(--user-msg);
    margin-left: auto;
}

.message-ai {
    background: var(--ai-msg);
    margin-right: auto;
}

.message-system {
    background: var(--bg-secondary);
    text-align: center;
    font-style: italic;
    max-width: 100%;
}

#input-area {
    padding: 1rem;
    background: var(--bg-secondary);
    display: flex;
    gap: 0.5rem;
    border-top: 1px solid #444;
}

#user-input {
    flex: 1;
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid #444;
    border-radius: 4px;
    padding: 0.5rem;
    font-family: inherit;
    resize: none;
}

#send-btn {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 2rem;
    cursor: pointer;
    font-weight: bold;
}

#send-btn:hover {
    opacity: 0.8;
}
```

---

## Embedding Pipeline

### Initial Vault Embedding (scripts/embed_vault.py)

```python
"""
One-time script to embed all vault documents into ChromaDB
Run: python scripts/embed_vault.py
"""

from services.vault_reader import vault_reader
from services.chroma_client import chroma_client, init_chroma
from database.db import init_database, get_db
from database.models import LoreMetadata
from tqdm import tqdm

def embed_vault():
    """Embed all vault documents"""
    init_database()
    init_chroma()
    
    print("Scanning vault...")
    files = vault_reader.list_files()
    print(f"Found {len(files)} markdown files")
    
    with get_db() as db:
        for file_path in tqdm(files, desc="Embedding"):
            relative_path = str(file_path.relative_to(vault_reader.vault_path))
            category = vault_reader.get_category_from_path(file_path)
            
            # Read content
            try:
                content = vault_reader.read_file(relative_path)
                checksum = vault_reader.get_file_checksum(relative_path)
            except Exception as e:
                print(f"Error reading {relative_path}: {e}")
                continue
            
            # Add to ChromaDB
            collection = category.lower()
            if collection not in ['characters', 'locations', 'history', 'technology']:
                collection = 'general'
            
            try:
                chroma_client.add_documents(
                    collection_name=collection,
                    documents=[content],
                    metadatas=[{
                        'file_path': relative_path,
                        'category': category
                    }],
                    ids=[relative_path]
                )
                
                # Update metadata
                metadata = db.query(LoreMetadata).filter(
                    LoreMetadata.file_path == relative_path
                ).first()
                
                if metadata:
                    metadata.embedding_status = 'embedded'
                    metadata.checksum = checksum
                else:
                    metadata = LoreMetadata(
                        file_path=relative_path,
                        category=category,
                        embedding_status='embedded',
                        checksum=checksum
                    )
                    db.add(metadata)
                
                db.commit()
                
            except Exception as e:
                print(f"Error embedding {relative_path}: {e}")
    
    print("Embedding complete!")

if __name__ == "__main__":
    embed_vault()
```

---

## Development Phases

### Phase 1: Foundation (Days 1-3)
**Goal**: Backend runs, connects to LM Studio, basic API works

**Tasks**:
1. Set up project structure
2. Install dependencies: `pip install fastapi uvicorn sqlalchemy chromadb langchain langgraph`
3. Implement `config.py`, `database/db.py`, `database/models.py`
4. Create basic FastAPI app in `main.py`
5. Implement `services/llm_client.py` - test connection to LM Studio
6. Run server: `python main.py` - verify http://localhost:5000

**Validation**: Can call LM Studio through your backend

---

### Phase 2: ChromaDB Integration (Days 4-5)
**Goal**: Vault embedded, semantic search works

**Tasks**:
1. Implement `services/chroma_client.py`
2. Implement `services/vault_reader.py`
3. Create `scripts/embed_vault.py`
4. Run embedding: `python scripts/embed_vault.py`
5. Test searches in Python REPL

**Validation**: Can retrieve relevant lore from queries

---

### Phase 3: Simple Agent Pipeline (Days 6-9)
**Goal**: Basic narrative generation without loops

**Tasks**:
1. Implement `agents/base_agent.py`
2. Implement `agents/input_analyzer.py`
3. Implement `agents/lore_retriever.py`
4. Implement `agents/generator.py`
5. Create simple linear workflow (no LangGraph yet)
6. Implement `api/routes.py` - `/api/narrative` endpoint
7. Test with curl or Postman

**Validation**: POST to API returns narrative based on lore

---

### Phase 4: Frontend Basic (Days 10-12)
**Goal**: Can chat through web interface

**Tasks**:
1. Clone SillyTavern for reference: `git clone https://github.com/SillyTavern/SillyTavern.git`
2. Study `SillyTavern/public/index.html` and `scripts/chat.js`
3. Create `frontend/index.html` - simplified layout
4. Implement `frontend/js/api.js` - backend communication
5. Implement `frontend/js/app.js` - basic chat logic
6. Implement `frontend/css/styles.css` - adapt SillyTavern styling
7. Test in browser

**Validation**: Can send messages and see responses in browser

---

### Phase 5: LangGraph + Consistency Loop (Days 13-16)
**Goal**: Multi-agent with regeneration

**Tasks**:
1. Implement remaining agents: `continuity_agent.py`, `drama_pacing.py`, `consistency_checker.py`, `state_updater.py`
2. Create `workflow/narrative_graph.py` with LangGraph
3. Add conditional edge for consistency checking
4. Update API route to use LangGraph workflow
5. Test regeneration logic

**Validation**: Inconsistent outputs trigger regeneration

---

### Phase 6: State Management (Days 17-19)
**Goal**: Game state persists and updates

**Tasks**:
1. Define state JSON structure
2. Implement state loading/saving in API
3. Implement `agents/state_updater.py` to extract changes
4. Create frontend state display panel
5. Test state changes across multiple turns

**Validation**: State updates correctly, persists between sessions

---

### Phase 7: Polish & Features (Days 20-25)
**Goal**: Production-ready for personal use

**Tasks**:
1. Add conversation history endpoint
2. Implement session management (create new, load existing)
3. Add basic error handling
4. Improve UI (loading indicators, better styling)
5. Add `--network` flag for friend access
6. Write README with setup instructions
7. Test with friends

**Validation**: Friends can connect and play

---

### Phase 8: Optional Enhancements (Ongoing)
**Goal**: Advanced features as desired

**Tasks**:
- Character personality matrices
- Relationship tracking
- Image display system
- Background music
- Ink integration for branching
- Character-specific fonts
- Advanced state visualization

---

## Dependencies

**requirements.txt**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
chromadb==0.4.18
langchain==0.1.0
langgraph==0.0.20
aiohttp==3.9.1
python-multipart==0.0.6
```

**Install**:
```bash
pip install -r requirements.txt
```

---

## Running the Application

**Local (just you)**:
```bash
# Terminal 1: Start LM Studio, load model, start server

# Terminal 2: Start backend
python main.py

# Browser: http://localhost:5000
```

**Network (with friends)**:
```bash
# Terminal 1: LM Studio running

# Terminal 2: Start backend with network access
python main.py --network

# Tell friends: http://YOUR_IP:5000
# (Find IP: ipconfig on Windows, ifconfig on Mac/Linux)
```

**First time setup**:
```bash
# 1. Embed vault
python scripts/embed_vault.py

# 2. Start app
python main.py
```

---

## Testing Approach

### Manual Testing Checklist
- [ ] Backend starts without errors
- [ ] LM Studio connection works
- [ ] ChromaDB search returns relevant results
- [ ] API endpoint returns narrative
- [ ] Frontend loads in browser
- [ ] Can send message and receive response
- [ ] State persists between refreshes
- [ ] Consistency checker triggers on bad output
- [ ] Works on network for friends

### Unit Tests (Optional)
```python
# tests/test_agents.py
def test_input_analyzer():
    state = {"user_input": "I approach the gate with Lyssia"}
    result = input_analyzer.analyze(state)
    assert "entities" in result
    assert "gate" in result["keywords"]
```

---

## Troubleshooting

### LM Studio Connection Issues
**Problem**: "Connection refused" to localhost:1234
**Solution**: 
1. Verify LM Studio is running
2. Check server is started in LM Studio
3. Verify URL in config: `http://localhost:1234/v1`

### ChromaDB Errors
**Problem**: "Collection not found"
**Solution**: Run `python scripts/embed_vault.py`

### Frontend Not Loading
**Problem**: Blank page or 404
**Solution**: 
1. Check `frontend/` files exist
2. Verify FastAPI mounts static files correctly
3. Check browser console for errors

### Network Access Not Working
**Problem**: Friends can't connect
**Solution**:
1. Use `--network` flag when starting
2. Verify firewall allows port 5000
3. Give friends your local IP (not localhost)
4. Both on same WiFi network

---

## Future Migration to Commercial (If Needed)

**When you decide to commercialize (Year 2-3)**:

### Database Migration
```python
# Change one line in config.py:
database_url = "postgresql://user:pass@host/doammo"
# SQLAlchemy handles the rest
```
**Time**: 1 hour + hosting setup

### Vector Database Migration
```python
# Replace ChromaDB with Qdrant
from qdrant_client import QdrantClient
client = QdrantClient(url="https://your-cluster.qdrant.io")
# Rewrite search queries (similar API)
```
**Time**: 2-3 days

### File Storage Migration
```python
# Add S3 storage class
class S3VaultStorage:
    def read_file(self, path):
        return s3.get_object(Bucket=bucket, Key=path)
```
**Time**: 2-3 days

### Add Authentication
```python
# Add FastAPI security
from fastapi.security import HTTPBearer
# Add user table, JWT tokens
```
**Time**: 1 week

### Add Payments
```python
# Integrate Stripe
# Add subscription management
```
**Time**: 1 week

**Total migration time**: 2-4 weeks, not 6 months

---

## Alternative: Considered & Rejected

### PostgreSQL (Instead using SQLite)
**Why rejected**: Overkill for hobby, adds Docker/setup complexity
**Migration**: One line change if needed later

### Qdrant (Instead using ChromaDB)
**Why rejected**: ChromaDB simpler for local use
**Migration**: 2-3 days to rewrite queries if needed

### SillyTavern Backend (Instead building custom)
**Why rejected**: Node.js, wrong architecture for multi-agent
**Alternative**: Use frontend only as reference

### Ink Scripting (Deferred)
**Why deferred**: Add complexity, implement after core works
**Timeline**: Phase 8 optional enhancement

### Cloud Deployment (Deferred)
**Why deferred**: Local-first priority
**Timeline**: Only if commercializing in future

---

## Success Criteria

**Phase 1-4 Complete**: Basic system works
- Can chat with AI locally
- Lore retrieval working
- Narratives are coherent

**Phase 5-6 Complete**: Production ready for hobby
- Consistency checking works
- State management functional
- Friends can connect on network

**Phase 7 Complete**: Polished experience
- UI looks good
- Error handling graceful
- Fun to use

**Phase 8**: Advanced features as desired

---

## Quick Start Commands

```bash
# Setup
git clone YOUR_REPO
cd doammo-narrative-engine
pip install -r requirements.txt
python scripts/embed_vault.py

# Development
python main.py

# With friends
python main.py --network

# Browser
open http://localhost:5000
```

---

## Notes for AI-Assisted Development

When using Claude or another AI to build this:

1. **Start with backend foundation** (Phase 1-3) - most critical
2. **Reference SillyTavern** for frontend patterns, not backend
3. **Keep it simple** - don't over-engineer for hypothetical commercial use
4. **Test incrementally** - verify each phase works before moving on
5. **Use SQLite** - PostgreSQL is unnecessary complexity now
6. **ChromaDB is fine** - don't migrate to Qdrant unless commercializing
7. **Focus on fun** - this is a hobby project, make it enjoyable to use

**This document provides complete specification for building DOAMMO system. All architectural decisions made, all patterns specified. Ready for implementation.**
