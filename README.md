# DOAMMO Narrative Engine

An AI-powered interactive storytelling system for the DOAMMO universe, featuring intelligent lore retrieval, conversation memory, multi-agent orchestration, context-aware narrative generation, and a complete wiki management system.

## Project Status

**Current Phase:** Phase 2 In Progress - Wiki System Complete ✓
**System Status:** Fully operational web application with wiki management
**Next Feature:** Lore Keeper AI System (auto-updating wiki from conversations)

## Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key (Claude)

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn langchain-anthropic chromadb langgraph python-dotenv

# Set up API key in .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Running the Application
```bash
# Start the web server
python api_server.py

# Open in browser
# http://localhost:8000
```

## Features

### Phase 1: Core Engine ✓
- 🎯 **Intelligent Lore Retrieval** - Semantic search using ChromaDB
- 🤖 **Multi-Agent System** - Lore Keeper, Narrator, and Quality agents
- 💬 **Conversation Memory** - Session management and history
- 🌐 **Web Interface** - Beautiful UI with real-time chat
- 🔌 **REST API** - Full programmatic access
- 📚 **Vault Integration** - Read-only lore access (never modifies your files)

### Phase 2: Wiki System ✓
- 📖 **Wiki Management** - Create and manage multiple story wikis
- 💾 **Session Storage** - Save conversations to wikis for later reference
- 📝 **Page Editor** - Create, edit, and delete wiki pages with markdown
- 📂 **Category Organization** - Characters, Locations, Items, Events
- 🔄 **Auto-Sync** - Optional automatic wiki saving after each AI response
- 📜 **Session Browser** - View and load previous sessions from wikis
- 🏗️ **Template System** - Pre-formatted templates for different page types
- 📁 **Multi-Wiki Support** - Multiple wikis per user with folder structure

### Wiki System Architecture

**File Structure:**
```
user_data/
└── {username}/
    └── wikis/
        └── {wiki_name}/
            ├── wiki_metadata.json
            ├── sessions/
            │   └── {session_id}.json
            └── pages/
                ├── characters/
                ├── locations/
                ├── items/
                └── events/
```

**API Endpoints:**
- `POST /wiki/create` - Create new wiki
- `GET /wiki/list` - List all wikis
- `GET /wiki/{name}` - Get wiki details
- `POST /wiki/{name}/save_session` - Save conversation to wiki
- `GET /wiki/{name}/session/{id}` - Load session from wiki
- `GET /wiki/{name}/page/{category}/{name}` - Read wiki page
- `POST /wiki/{name}/page/{category}/{name}` - Create/update page
- `DELETE /wiki/{name}/page/{category}/{name}` - Delete page

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

### Phase 2: Wiki System Complete ✓
- [x] **Backend Integration** - WikiManager class for file operations
- [x] **Session Management** - Save/load conversations from wikis
- [x] **Page Editor** - Full CRUD operations for wiki pages
- [x] **Session Browser** - View and restore previous sessions
- [x] **Auto-Sync Toggle** - Automatic wiki saving option
- [x] **Template System** - Pre-formatted page templates

## Tech Stack

- **Backend**: FastAPI, LangChain/LangGraph
- **Vector DB**: ChromaDB (local semantic search with all-MiniLM-L6-v2 embeddings)
- **LLM**: Claude Sonnet 4 (Anthropic API)
- **Wiki Storage**: Local file system (JSON + Markdown)
- **Session Storage**: JSON files (gitignored)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templating, Lucide icons

## Project Structure

```


```

## Usage

### Web Interface (Recommended)

1. **Connect to your lore vault** - Point the app to a folder containing your world-building documents (character bios, storylines, locations, etc.)
2. **Start the server**: `python api_server.py`
3. **Open browser**: http://localhost:8000
4. **Create a wiki**: Click "Save to Wiki" to create your first story wiki
5. **Start chatting**: Type scenarios and get AI-generated narratives
6. **Manage wikis**: Use "Open Wiki" to browse, load sessions, and edit pages

### Wiki Workflow

1. **Create Wiki** - Save your first conversation to create a new wiki
2. **Auto-Sync** - Toggle auto-sync to automatically save after each AI response
3. **Edit Pages** - Click edit buttons to modify wiki pages or create new ones
4. **Browse Sessions** - View all saved sessions and load them back into chat
5. **Organize Lore** - Categorize pages as Characters, Locations, Items, or Events

### Interactive Terminal
```bash
python interactive_multiagent.py
```
Shows detailed output from all three agents (Lore Keeper, Narrator, Quality)

### API Access
Interactive docs at http://localhost:8000/docs

## Next Feature: Lore Keeper AI System

The next major feature will be an AI-powered system that automatically watches conversations and updates the wiki:

**Planned Features:**
- **AI-Powered Entity Detection** - Automatically detect characters, locations, items, and events
- **Confidence Scoring** - Assign confidence scores to detected entities 
- **Auto-Update Wiki** - Create and update wiki pages based on conversations
- **Configurable System Prompt** - Customize what the Lore Keeper focuses on
- **Threshold Controls** - Only write lore if confidence > threshold
- **Verbosity Settings** - Control how much detail to write
- **Toggle Modes** - Ask before writing vs fully automatic

## License

Private project - All rights reserved
