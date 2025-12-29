"""
Milestone 4: ChromaDB Setup + Semantic Search
Goal: Embed vault lore into ChromaDB and test semantic search

Prerequisites:
1. ChromaDB installed (pip install chromadb)
2. Vault with lore files in _Lore/ folder
3. Previous milestones working

Run: python test_chromadb_setup.py
"""

import os
from pathlib import Path
import chromadb
from chromadb.config import Settings

def test_chromadb_setup():
    print("=" * 50)
    print("MILESTONE 4: ChromaDB Setup + Semantic Search")
    print("=" * 50)

    # Setup paths
    vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")
    lore_path = vault_path / "_Lore"
    chroma_path = Path("chroma_data")

    print(f"\n[1/6] Initializing ChromaDB...")

    # Create ChromaDB client (persistent storage)
    client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(
            anonymized_telemetry=False  # Disable telemetry for privacy
        )
    )

    # Get or create collection
    # ChromaDB will use a default embedding model (all-MiniLM-L6-v2)
    collection_name = "doammo_lore"

    # Delete existing collection if it exists (for testing)
    try:
        client.delete_collection(name=collection_name)
        print(f"Cleared existing '{collection_name}' collection")
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "DOAMMO universe lore and characters"}
    )

    print(f"OK ChromaDB initialized at: {chroma_path}")

    print(f"\n[2/6] Finding lore files...")

    # Find all markdown files in _Lore folder
    lore_files = list(lore_path.glob("*.md"))

    if not lore_files:
        print("X ERROR: No .md files found in _Lore folder")
        return False

    print(f"OK Found {len(lore_files)} lore files")

    print(f"\n[3/6] Reading and embedding lore files...")

    # Prepare data for embedding
    documents = []  # The actual text content
    metadatas = []  # Metadata about each document
    ids = []        # Unique IDs for each document

    for file in lore_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store the document
            documents.append(content)

            # Store metadata (helpful for filtering and debugging)
            metadatas.append({
                "filename": file.name,
                "filepath": str(file),
                "size": len(content),
                "type": "lore"
            })

            # Use filename as ID (ChromaDB requires unique IDs)
            ids.append(file.stem)  # stem = filename without extension

            print(f"  - Loaded: {file.name} ({len(content)} chars)")

        except Exception as e:
            print(f"  X ERROR reading {file.name}: {e}")

    print(f"\n[4/6] Embedding {len(documents)} documents into ChromaDB...")
    print("This may take a moment as the embedding model processes the text...")

    # Add all documents to ChromaDB
    # ChromaDB will automatically generate embeddings using its default model
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"OK Embedded {len(documents)} documents into ChromaDB")

    print(f"\n[5/6] Testing semantic search...")

    # Test query: search for information about Lyssia
    query = "What vehicles are used for travel?"

    print(f"Query: '{query}'")

    # Perform semantic search
    # n_results=2 means "return the 2 most relevant documents"
    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    print(f"\n[6/6] Search results:")
    print("=" * 50)

    # Results structure:
    # results['documents'][0] = list of matching documents
    # results['metadatas'][0] = list of metadata for matches
    # results['distances'][0] = list of similarity scores (lower = more similar)

    for i, (doc, meta, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"\nResult {i+1}: {meta['filename']}")
        print(f"Relevance score: {distance:.4f} (lower = more relevant)")
        print(f"Preview: {doc[:300]}...")
        print("-" * 50)

    print("\nOK MILESTONE 4 COMPLETE!")
    print(f"ChromaDB successfully embedded {len(documents)} lore files")
    print("Semantic search is working!")
    print(f"\nChromaDB data stored in: {chroma_path}")
    print()

    return True

if __name__ == "__main__":
    test_chromadb_setup()
