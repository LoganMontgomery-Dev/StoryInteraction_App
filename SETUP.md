# DOAMMO Narrative Engine - Setup Guide

Complete installation and setup instructions for the DOAMMO interactive storytelling system.

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Anthropic API Key** - [Get API Key](https://console.anthropic.com/)

### Check Your Python Version

```bash
python --version
# Should show Python 3.10.x or higher
```

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/LoganMontgomery-Dev/StoryInteraction_App.git
cd StoryInteraction_App
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- FastAPI (web framework)
- Anthropic SDK (Claude API)
- ChromaDB (vector database)
- LangGraph (multi-agent workflows)
- And all other dependencies

**Note:** Installation may take 2-5 minutes depending on your internet connection.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Or on Windows:
copy .env.example .env
```

Edit `.env` and add your configuration:

```env
# Required: Your Anthropic API Key
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Vault path (if you have a custom Obsidian vault)
VAULT_PATH=C:/path/to/your/vault

# Optional: Server configuration
HOST=localhost
PORT=8000
DEBUG=true
```

**Getting your Anthropic API Key:**
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy and paste it into your `.env` file

### 5. Initialize ChromaDB (First Time Only)

The vector database will be initialized automatically on first run, but you can verify it:

```bash
python test_chromadb_setup.py
```

This creates the `chroma_data/` directory and sets up the embedding system.

---

## Running the Application

### Start the Server

```bash
python api_server.py
```

You should see output like:
```
Initializing DOAMMO Narrative Engine API...
✓ ChromaDB collection initialized
✓ Claude API client configured
✓ LangGraph workflow compiled
INFO:     Uvicorn running on http://localhost:8000
```

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

You should see the DOAMMO narrative interface with:
- Chat panel (center)
- Lore viewer (right)
- Wiki management (top bar)

---

## Verifying Installation

### Test the API

```bash
# In a new terminal (keep the server running)
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### Test Components Individually

**Test Claude API connection:**
```bash
python test_claude_api.py
```

**Test ChromaDB:**
```bash
python test_chromadb_setup.py
```

**Test the full workflow:**
```bash
python test_intelligent_narrative.py
```

---

## Project Structure

After installation, your directory should look like this:

```
StoryInteraction_App/
├── venv/                      # Virtual environment (created)
├── chroma_data/               # Vector database (created on first run)
├── user_data/                 # User wikis and sessions (created on use)
├── sessions/                  # Legacy sessions (if any)
│
├── api_server.py              # Main application entry point
├── wiki_manager.py            # Wiki CRUD operations
├── interactive_narrative.py   # Interactive testing script
├── interactive_multiagent.py  # Multi-agent testing script
│
├── static/                    # Frontend assets
│   ├── css/
│   ├── js/
│   └── header-landscape.png
│
├── templates/                 # HTML templates
│   └── index.html
│
├── test_*.py                  # Test scripts
├── requirements.txt           # Dependencies
├── .env                       # Your configuration (created)
├── .env.example              # Configuration template
└── README.md                  # Project documentation
```

---

## Common Issues & Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Verify `.env` file exists in project root
2. Check that `ANTHROPIC_API_KEY` is set correctly
3. Restart the server after editing `.env`

### Issue: Server won't start / Port already in use

**Solution:**
```bash
# Check if something is using port 8000
# Windows:
netstat -ano | findstr :8000

# macOS/Linux:
lsof -i :8000

# Change port in .env:
PORT=8080
```

### Issue: ChromaDB errors

**Solution:**
```bash
# Delete and recreate ChromaDB
rm -rf chroma_data/  # or: rmdir /s chroma_data on Windows
python test_chromadb_setup.py
```

### Issue: Virtual environment won't activate (Windows)

**Solution:**
```powershell
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again:
venv\Scripts\activate
```

### Issue: Slow API responses

**Possible causes:**
1. First request after startup is slower (ChromaDB initialization)
2. Network latency to Anthropic API
3. Large vault being processed

**Solution:**
- Wait for full initialization
- Check your internet connection
- Reduce vault size if testing

---

## Development Setup

If you plan to modify the code:

### Install Development Tools (Optional)

```bash
pip install pytest black flake8
```

### Run Tests

```bash
# Run all tests
pytest

# Run specific test
python test_api.py
```

### Code Formatting

```bash
# Format code with black
black api_server.py wiki_manager.py
```

---

## Usage Workflow

### 1. Create a Wiki

1. Click "Create New Wiki" in the top bar
2. Enter wiki name and description
3. Wiki folder structure is created automatically

### 2. Start a Conversation

1. Type your narrative prompt in the chat input
2. Press Enter or click Send
3. AI generates a response using lore from your vault

### 3. Save Sessions

1. Enable "Auto-Sync" to automatically save after each turn
2. Or manually click "Save to Wiki"
3. Sessions are stored in `user_data/{user}/wikis/{wiki_name}/sessions/`

### 4. Browse Sessions

1. Click "Browse Sessions" in the top bar
2. Select a previous session to load
3. Continue from where you left off

### 5. Manage Wiki Pages

1. Click "New Page" in the lore viewer
2. Choose category (Characters, Locations, Items, Events)
3. Write in Markdown format
4. Pages appear in the lore viewer automatically

---

## Next Steps

### Explore Example Scripts

**Interactive Narrative (Simple):**
```bash
python interactive_narrative.py
```
Basic narrative generation with lore retrieval.

**Multi-Agent Workflow:**
```bash
python interactive_multiagent.py
```
Full LangGraph agent pipeline with consistency checking.

### Connect Your Obsidian Vault (Optional)

1. Set `VAULT_PATH` in `.env` to your vault location
2. Restart the server
3. Your vault lore will be available for semantic search

### Customize System Prompts

Edit the system prompts in `api_server.py` to change:
- Narrative style
- Character behavior
- Story pacing
- Tone and genre

---

## Updating the Application

### Pull Latest Changes

```bash
# Activate virtual environment first
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Restart the server
python api_server.py
```

---

## Uninstalling

To completely remove the application:

```bash
# Deactivate virtual environment
deactivate

# Delete project directory
cd ..
rm -rf StoryInteraction_App  # or: rmdir /s StoryInteraction_App on Windows
```

**Note:** This will delete all wikis and sessions. Back up `user_data/` if needed.

---

## Getting Help

**Issues or bugs:** [GitHub Issues](https://github.com/LoganMontgomery-Dev/StoryInteraction_App/issues)

**Documentation:** See [README.md](README.md) for feature overview

**API Documentation:** Visit `http://localhost:8000/docs` when server is running (FastAPI auto-generated docs)

---

## System Requirements

**Minimum:**
- Python 3.10+
- 4GB RAM
- 500MB disk space
- Internet connection (for Anthropic API)

**Recommended:**
- Python 3.11+
- 8GB RAM
- 2GB disk space (for larger vaults and wikis)
- Stable internet connection

---

## Security Notes

- **Never commit `.env` to git** - It contains your API key
- `.env` is already in `.gitignore`
- Keep your Anthropic API key private
- The application runs locally - your data stays on your machine
- Only API requests are sent to Anthropic (text prompts and responses)

---

## FAQ

**Q: Do I need an Obsidian vault to use this?**
A: No, the wiki system works standalone. An Obsidian vault is optional for additional lore.

**Q: Can I use a different LLM?**
A: Currently only Claude (Anthropic) is supported. LM Studio support is planned for future updates.

**Q: Where is my data stored?**
A: All data is local in `user_data/`, `chroma_data/`, and `sessions/` folders.

**Q: Can I run this on a server for friends?**
A: Yes, but you'll need to configure CORS and host settings. For local network access, set `HOST=0.0.0.0` in `.env`.

---

**Setup complete!** You're ready to create interactive narratives with DOAMMO.

Enjoy your storytelling adventures! 🎲📖
