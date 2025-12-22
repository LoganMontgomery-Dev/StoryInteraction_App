# DOAMMO Narrative Engine

An AI-powered interactive storytelling system for the DOAMMO universe, featuring intelligent lore retrieval, conversation memory, multi-agent orchestration, and context-aware narrative generation.

## Project Status

**Current Phase:** Phase 1 Complete. ALL 9 milestones done ✓
**System Status:** Fully operational web application
**Next Phase:** Phase 2 - LM Studio integration and advanced features

## Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key (Claude)

### Running the Application
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Start the web server
uvicorn api_server:app --reload

# Open in browser
# http://localhost:8000
```

## What's Built

### Phase 1: Complete ✓

- [x] **Milestone 0**: Environment Setup
- [x] **Milestone 1**: Claude API Connection
- [x] **Milestone 2**: Vault Reading
- [x] **Milestone 3**: Lore + Claude Integration
- [x] **Milestone 4**: ChromaDB Semantic Search
- [x] **Milestone 5**: Intelligent Lore-Aware Narratives
- [x] **Milestone 6**: Conversation History + Context Management
- [x] **Milestone 7**: LangGraph Multi-Agent Workflows
- [x] **Milestone 8**: FastAPI REST Backend
- [x] **Milestone 9**: Web Frontend UI

### Features
- 🎯 Intelligent lore retrieval using semantic search
- 🤖 Multi-agent system (Lore Keeper, Narrator, Quality agents)
- 💬 Conversation memory and session management
- 🌐 Beautiful web interface with real-time chat
- 🔌 REST API for programmatic access
- 📚 Read-only vault integration (never modifies your lore)
- 🎨 Modern gradient UI with smooth animations

See [_DOAMMO_Development_Milestones.md](_DOAMMO_Development_Milestones.md) for detailed milestone descriptions.

## Architecture

See [_DOAMMO_AI_System_Overview.md](_DOAMMO_AI_System_Overview.md) for complete technical specification.

### Tech Stack
- **Backend**: FastAPI, LangChain/LangGraph
- **Vector DB**: ChromaDB (local semantic search with all-MiniLM-L6-v2 embeddings)
- **LLM**: Claude Sonnet 4 (Anthropic API)
- **Session Storage**: JSON files (local, gitignored)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templating

## Project Structure

```
DOAMMO_APP/
├── venv/                              # Virtual environment
├── templates/                         # HTML templates
│   └── index.html                    # Web frontend
├── sessions/                          # Conversation sessions (gitignored)
├── chroma_data/                       # ChromaDB vector database (gitignored)
├── api_server.py                      # FastAPI REST backend
├── interactive_multiagent.py          # Interactive multi-agent terminal interface
├── test_*.py                          # Test scripts for each milestone
└── README.md                          # This file
```

## Usage

### Web Interface (Recommended)
1. you have to connect the app to a folder of documents, which would be character bios, storylines, locations, and otherworld building information for the ai to draw on.)
1. Start the server: `uvicorn api_server:app --reload`
2. Open http://localhost:8000
3. Type scenarios and get AI-generated narratives

### Interactive Terminal
```bash
python interactive_multiagent.py
```
Shows detailed output from all three agents (Lore Keeper, Narrator, Quality)

### API Access
Interactive docs at http://localhost:8000/docs

## Next Phase: Phase 2

Planned enhancements:
- Advanced multi-agent features
- UI enhancements (settings panel, themes)
- World state tracking
- Additional specialized agents
- LM Studio integration (local LLM option)
- Switchable backend (Claude vs LM Studio)
- 
## Reference Material

- **SillyTavern**: Cloned locally for UI/UX reference (frontend patterns only)

## License

Private project - All rights reserved
