# DOAMMO Development Milestones

**Building in Chunks: Start Simple, Add Incrementally**

Core philosophy: Start with the simplest possible thing that works, validate it, then add one feature at a time. Each milestone should take 1-3 hours and produce something testable immediately.

---

## Phase 1: Foundation (First Session - ~12 hours total)

### ✅ Milestone 0: Environment Setup
**Time**: 30 minutes  
**Goal**: Development environment ready

```bash
# Create project
mkdir doammo-narrative-engine
cd doammo-narrative-engine

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install minimal dependencies
pip install openai
```

**Validation**: `python --version` and `pip list` work

---

### ✅ Milestone 1: Talk to LM Studio
**Time**: 1 hour  
**Goal**: Python can call LM Studio and get responses

**Create**: `test_lm_studio.py`
```python
import openai

# Point to LM Studio
client = openai.OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

# Test call
response = client.chat.completions.create(
    model="local-model",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response.choices[0].message.content)
```

**Run**: 
```bash
# Terminal 1: Start LM Studio, load model, start server
# Terminal 2:
python test_lm_studio.py
```

**Validation**: Prints "Hello!" or similar response

**Why this first**: Proves LM Studio works before building anything else. If this fails, nothing else will work.

---

### ✅ Milestone 2: Read Your Vault
**Time**: 30 minutes  
**Goal**: Python can read a lore file

**Create**: `test_vault_read.py`
```python
from pathlib import Path

vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")

# Read one character file
lyssia_file = vault_path / "Characters" / "Lyssia.md"

with open(lyssia_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Read {len(content)} characters")
print(content[:500])  # First 500 chars
```

**Validation**: Prints Lyssia's character content

---

### ✅ Milestone 3: LM Studio + Lore = Response
**Time**: 1 hour  
**Goal**: LLM responds using injected lore

**Create**: `test_lore_injection.py`
```python
import openai
from pathlib import Path

# Read lore
vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")
lyssia_file = vault_path / "Characters" / "Lyssia.md"
with open(lyssia_file, 'r', encoding='utf-8') as f:
    lyssia_lore = f.read()

# Call LM Studio with lore
client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

user_input = "Lyssia and I approach an old gate. What does she do?"

prompt = f"""LORE:
{lyssia_lore[:1000]}

USER ACTION:
{user_input}

Generate narrative response:"""

response = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)

print(response.choices[0].message.content)
```

**Validation**: Response mentions Lyssia and is consistent with her character

**Why this matters**: This is the **core loop** of your system. Everything else is just making this better.

---

### ✅ Milestone 4: Simple Interactive Loop
**Time**: 30 minutes  
**Goal**: Can have a conversation

**Create**: `simple_game.py`
```python
import openai
from pathlib import Path

# Setup
vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")
client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

# Load lore once
with open(vault_path / "Characters" / "Lyssia.md", 'r') as f:
    lyssia_lore = f.read()[:1000]

print("=== DOAMMO Prototype ===")
print("Type 'quit' to exit\n")

history = []

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ['quit', 'exit']:
        break
    
    # Build prompt with history
    prompt = f"LORE:\n{lyssia_lore}\n\nCONVERSATION:\n"
    for turn in history[-3:]:  # Last 3 turns
        prompt += f"{turn}\n"
    prompt += f"USER: {user_input}\nAI:"
    
    response = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": prompt}]
    )
    
    ai_response = response.choices[0].message.content
    print(f"\n{ai_response}\n")
    
    history.append(f"USER: {user_input}")
    history.append(f"AI: {ai_response}")
```

**Run**: `python simple_game.py`

**Validation**: Can have multi-turn conversation, Lyssia stays in character

**🎉 Milestone achieved**: You have a **working narrative engine**. Crude, but functional.

---

### ✅ Milestone 5: Install ChromaDB
**Time**: 1 hour  
**Goal**: Semantic search works

```bash
pip install chromadb
```

**Create**: `test_chromadb.py`
```python
import chromadb
from pathlib import Path

# Initialize
client = chromadb.Client()
collection = client.create_collection("test_lore")

# Add some lore
vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")

# Add Lyssia
with open(vault_path / "Characters" / "Lyssia.md", 'r') as f:
    collection.add(
        documents=[f.read()],
        ids=["lyssia"],
        metadatas=[{"type": "character"}]
    )

# Search
results = collection.query(
    query_texts=["distrustful military veteran"],
    n_results=1
)

print("Found:", results['ids'])
print(results['documents'][0][:200])
```

**Validation**: Search returns Lyssia's document

---

### ✅ Milestone 6: Multi-File Semantic Search
**Time**: 1-2 hours  
**Goal**: Search across entire vault

**Create**: `embed_vault.py`
```python
import chromadb
from pathlib import Path

client = chromadb.Client()
collection = client.get_or_create_collection("doammo_lore")

vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")

# Find all markdown files
md_files = list(vault_path.rglob("*.md"))
print(f"Found {len(md_files)} files")

for file_path in md_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add to ChromaDB
        file_id = str(file_path.relative_to(vault_path))
        collection.add(
            documents=[content],
            ids=[file_id],
            metadatas=[{"path": file_id}]
        )
        print(f"✓ {file_id}")
    except Exception as e:
        print(f"✗ {file_path}: {e}")

print("\nDone! Testing search...")

# Test search
results = collection.query(
    query_texts=["desert vehicle"],
    n_results=3
)

for doc_id in results['ids'][0]:
    print(f"- {doc_id}")
```

**Run**: `python embed_vault.py` (takes 1-2 minutes)

**Validation**: Can search for concepts and get relevant documents

---

### ✅ Milestone 7: Combine ChromaDB + LLM
**Time**: 1 hour  
**Goal**: LLM uses automatically retrieved lore

**Create**: `smart_game.py`
```python
import openai
import chromadb
from pathlib import Path

# Setup
client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
chroma = chromadb.Client()
collection = chroma.get_collection("doammo_lore")

print("=== DOAMMO Smart Prototype ===\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ['quit', 'exit']:
        break
    
    # Search for relevant lore
    lore_results = collection.query(
        query_texts=[user_input],
        n_results=2
    )
    
    # Build context
    context = "RELEVANT LORE:\n"
    for doc in lore_results['documents'][0]:
        context += f"\n{doc[:500]}\n---\n"
    
    context += f"\nUSER ACTION: {user_input}\nGenerate narrative:"
    
    # Generate
    response = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": context}]
    )
    
    print(f"\n{response.choices[0].message.content}\n")
```

**Validation**: Mentions relevant lore even if not explicitly referenced

**Example**:
- Input: "We find a vehicle"
- ChromaDB finds vehicle docs
- LLM mentions specific vehicles from your lore

**🎉 Milestone achieved**: **RAG (Retrieval-Augmented Generation) works!**

---

### ✅ Milestone 8: Add FastAPI
**Time**: 2 hours  
**Goal**: Backend server running

```bash
pip install fastapi uvicorn
```

**Create**: `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import chromadb

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup
llm_client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
chroma = chromadb.Client()
collection = chroma.get_collection("doammo_lore")

class NarrativeRequest(BaseModel):
    user_input: str

@app.post("/api/narrative")
async def generate_narrative(request: NarrativeRequest):
    # Search lore
    lore_results = collection.query(
        query_texts=[request.user_input],
        n_results=2
    )
    
    # Build prompt
    context = "LORE:\n"
    for doc in lore_results['documents'][0]:
        context += f"{doc[:500]}\n---\n"
    context += f"\nUSER: {request.user_input}\nAI:"
    
    # Generate
    response = llm_client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": context}]
    )
    
    return {
        "narrative": response.choices[0].message.content,
        "lore_used": lore_results['ids'][0]
    }

@app.get("/")
async def root():
    return {"status": "DOAMMO backend running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)
```

**Run**: `python backend/main.py`

**Test in browser**: `http://localhost:5000` - should see status message

**Test API**: 
```bash
curl -X POST http://localhost:5000/api/narrative \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I approach the gate"}'
```

**Validation**: Returns JSON with narrative

**🎉 Milestone achieved**: **Backend API works!**

---

### ✅ Milestone 9: Simple Frontend
**Time**: 2 hours  
**Goal**: Can chat through browser

**Create**: `frontend/index.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>DOAMMO</title>
    <style>
        body {
            font-family: system-ui;
            max-width: 800px;
            margin: 50px auto;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }
        #messages {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #444;
            padding: 10px;
            margin-bottom: 10px;
            background: #2d2d2d;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user { background: #3a5a7a; }
        .ai { background: #2d4a2d; }
        #input { 
            width: 80%; 
            padding: 10px;
            background: #2d2d2d;
            border: 1px solid #444;
            color: #e0e0e0;
        }
        button {
            padding: 10px 20px;
            background: #4a90e2;
            border: none;
            color: white;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>DOAMMO</h1>
    <div id="messages"></div>
    <input id="input" placeholder="What do you do?" />
    <button onclick="send()">Send</button>

    <script>
        async function send() {
            const input = document.getElementById('input');
            const messages = document.getElementById('messages');
            const text = input.value.trim();
            if (!text) return;

            // Show user message
            messages.innerHTML += `<div class="message user">${text}</div>`;
            input.value = '';
            messages.scrollTop = messages.scrollHeight;

            // Call backend
            const response = await fetch('http://localhost:5000/api/narrative', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_input: text})
            });

            const data = await response.json();

            // Show AI response
            messages.innerHTML += `<div class="message ai">${data.narrative}</div>`;
            messages.scrollTop = messages.scrollHeight;
        }

        document.getElementById('input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
```

**Run**:
```bash
# Terminal 1: Backend
python backend/main.py

# Terminal 2: Frontend
cd frontend
python -m http.server 8000
```

**Open browser**: `http://localhost:8000`

**Validation**: Can chat through browser, see responses

**🎉 Milestone achieved**: **Full working prototype!**

---

## Progress Summary

| # | Milestone | Time | Cumulative | Status |
|---|-----------|------|------------|--------|
| 0 | Environment Setup | 30m | 30m | ⬜ |
| 1 | LM Studio Connection | 1h | 1.5h | ⬜ |
| 2 | Vault Reading | 30m | 2h | ⬜ |
| 3 | Lore + LLM | 1h | 3h | ⬜ |
| 4 | Interactive Loop | 30m | 3.5h | ⬜ |
| 5 | ChromaDB Setup | 1h | 4.5h | ⬜ |
| 6 | Embed Vault | 2h | 6.5h | ⬜ |
| 7 | Smart Retrieval | 1h | 7.5h | ⬜ |
| 8 | FastAPI Backend | 2h | 9.5h | ⬜ |
| 9 | Web Frontend | 2h | 11.5h | ⬜ |

**After ~12 hours**: Working web app with semantic lore retrieval!

---

## Phase 2: Advanced Features (Future Milestones)

### Milestone 10: SQLite State Persistence
**Time**: 3 hours  
**Goal**: State persists between sessions

- Add SQLAlchemy + SQLite database
- Create sessions table
- Store conversation history
- Load previous sessions

### Milestone 11: First Agent
**Time**: 2 hours  
**Goal**: Structured agent system begins

- Create base agent class
- Implement input analyzer
- Extract entities/intent from user input

### Milestone 12: Multi-Agent Pipeline
**Time**: 4 hours  
**Goal**: Multiple agents working together

- Install LangChain/LangGraph
- Create simple 3-agent workflow (Analyzer → Retriever → Generator)
- Test orchestration

### Milestone 13: Consistency Checking
**Time**: 3 hours  
**Goal**: AI validates its own output

- Implement consistency checker agent
- Add regeneration loop
- Test with deliberately bad examples

### Milestone 14: State Management System
**Time**: 4 hours  
**Goal**: Game state tracks and updates

- Define JSON state structure
- Implement state updater agent
- Add frontend state display panel

### Milestone 15: Network Access for Friends
**Time**: 1 hour  
**Goal**: Friends can connect on local network

- Add `--network` command line flag
- Test connection from another device on WiFi
- Verify multi-user sessions work

---

## Troubleshooting Guide

### LM Studio Not Responding
**Symptoms**: Connection refused, timeout errors

**Solutions**:
1. Verify LM Studio server is running (green indicator)
2. Test in browser: `http://localhost:1234/v1/models`
3. Reload model in LM Studio
4. Check firewall isn't blocking port 1234

---

### ChromaDB Errors
**Symptoms**: Collection not found, embedding errors

**Solutions**:
1. Delete `chroma_data/` folder and re-run `embed_vault.py`
2. Check file encodings are UTF-8 (not UTF-16 or other)
3. Verify vault path is correct
4. Try embedding just one file first to isolate issues

---

### Import Errors
**Symptoms**: `ModuleNotFoundError`

**Solutions**:
1. Activate virtual environment: `source venv/bin/activate`
2. Install missing package: `pip install <package-name>`
3. Verify you're in project directory
4. Check `pip list` to see installed packages

---

### Frontend Not Loading
**Symptoms**: Blank page, CORS errors

**Solutions**:
1. Verify CORS is enabled in FastAPI
2. Check backend is running on port 5000
3. Open browser console (F12) for specific errors
4. Try accessing backend directly: `http://localhost:5000`

---

### Lore Not Being Used
**Symptoms**: Responses ignore vault content

**Solutions**:
1. Verify vault was embedded: check `chroma_data/` exists
2. Test ChromaDB search separately with `test_chromadb.py`
3. Print retrieved documents to see what's being found
4. Check file paths in ChromaDB match actual files

---

## Development Best Practices

### Work Incrementally
- Complete one milestone before starting next
- Don't skip ahead - each builds on previous
- Test thoroughly at each step

### Test Immediately
- Run code after every change
- Don't accumulate untested code
- Fix issues as they appear

### Commit Often
```bash
git add .
git commit -m "Milestone X: [description]"
```
- Commit after each working milestone
- Easy to roll back if something breaks
- Track your progress

### Stay Simple
- Resist urge to add features before basics work
- One feature at a time
- If something breaks, you know what caused it

### Take Breaks
- Step away if stuck for >30 minutes
- Fresh perspective helps
- Sleep on complex problems

---

## Key Principle

**Each milestone gives you something working to test.**

Don't think about the final product. Focus on getting Milestone 1 working tonight. Then Milestone 2 tomorrow. Build momentum with quick wins.

The goal isn't to build everything - it's to build something that works, then make it better.

---

## Next Steps

1. ⭐ Start with Milestone 1 (LM Studio connection test)
2. Work through Milestones 2-9 in order
3. After Milestone 9, reassess and plan Phase 2
4. Adjust milestones based on what you learn

**You've got this. Start simple. Build incrementally. Test constantly.**

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run scripts
python test_lm_studio.py
python embed_vault.py
python simple_game.py
python backend/main.py

# Start frontend
cd frontend
python -m http.server 8000

# Test API
curl -X POST http://localhost:5000/api/narrative \
  -H "Content-Type: application/json" \
  -d '{"user_input": "test message"}'
```
