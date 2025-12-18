# DOAMMO Narrative Engine

An AI-powered interactive storytelling system for the DOAMMO universe, featuring multi-agent orchestration, semantic lore retrieval, and local LLM inference.

## Project Status

**Current Phase:** Foundation Setup
**Last Milestone:** Environment Setup (Milestone 0) ✓

## Quick Start

### Prerequisites
- Python 3.10+
- LM Studio installed and running
- Obsidian vault with DOAMMO lore at `C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault`

### Setup
```bash
# Activate virtual environment
.\venv\Scripts\activate

# Test LM Studio connection (Milestone 1)
python test_lm_studio.py
```

## Development Milestones

### Phase 1: Foundation (Current)

- [x] **Milestone 0**: Environment Setup (30m)
  - Virtual environment created
  - OpenAI package installed
  - Git repository initialized

- [ ] **Milestone 1**: LM Studio Connection (1h)
  - Test connection to LM Studio
  - Verify model inference works
  - **Next:** Run `python test_lm_studio.py`

- [ ] **Milestone 2**: Vault Reading (30m)
- [ ] **Milestone 3**: Lore + LLM Integration (1h)
- [ ] **Milestone 4**: Simple Interactive Loop (30m)
- [ ] **Milestone 5**: ChromaDB Setup (1h)
- [ ] **Milestone 6**: Multi-File Semantic Search (2h)
- [ ] **Milestone 7**: Smart Retrieval (1h)
- [ ] **Milestone 8**: FastAPI Backend (2h)
- [ ] **Milestone 9**: Web Frontend (2h)

See [_DOAMMO_Development_Milestones.md](_DOAMMO_Development_Milestones.md) for detailed milestone descriptions.

## Architecture

See [_DOAMMO_AI_System_Overview.md](_DOAMMO_AI_System_Overview.md) for complete technical specification.

### Tech Stack
- **Backend**: FastAPI, SQLAlchemy, LangChain/LangGraph
- **Vector DB**: ChromaDB (local semantic search)
- **LLM**: LM Studio (localhost:1234)
- **Database**: SQLite → PostgreSQL migration path
- **Frontend**: HTML/CSS/JavaScript (SillyTavern UI patterns)

## Project Structure

```
DOAMMO_APP/
├── venv/                           # Virtual environment
├── SillyTavern/                    # Reference only (gitignored)
├── test_lm_studio.py              # Milestone 1 test
├── _DOAMMO_AI_System_Overview.md  # Technical spec
├── _DOAMMO_Development_Milestones.md  # Milestone tracking
└── README.md                       # This file
```

## Next Steps

1. **Ensure LM Studio is running:**
   - Open LM Studio
   - Load a model (recommended: 7B-13B parameter range)
   - Start the server (should show localhost:1234)

2. **Run Milestone 1 test:**
   ```bash
   python test_lm_studio.py
   ```

3. **If successful, proceed to Milestone 2** (Vault reading)

## Reference Material

- **SillyTavern**: Cloned locally for UI/UX reference (frontend patterns only)
- **Obsidian Vault**: `C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault`

## Development Philosophy

- Start simple, build incrementally
- Test after every change
- Complete one milestone before moving to next
- Local-first, cloud-optional architecture
- Hobby project with commercial migration path

## License

Private project - All rights reserved
