"""
DOAMMO Wiki Manager
Handles wiki creation, storage, and retrieval for story sessions
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class WikiManager:
    """Manages story wikis with sessions and markdown pages"""

    def __init__(self, user_data_dir: str = "user_data", default_user: str = "default_user"):
        self.user_data_dir = Path(user_data_dir)
        self.default_user = default_user
        self.user_dir = self.user_data_dir / default_user
        self.wikis_dir = self.user_dir / "wikis"
        self.chats_dir = self.user_dir / "chats"

        # Ensure directories exist
        self.wikis_dir.mkdir(parents=True, exist_ok=True)
        self.chats_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Wiki Creation & Setup
    # ========================================================================

    def create_wiki(self, wiki_name: str, description: str = "") -> Dict:
        """Create a new wiki with folder structure and templates"""
        # Sanitize wiki name for filesystem
        safe_name = self._sanitize_name(wiki_name)
        wiki_path = self.wikis_dir / safe_name

        if wiki_path.exists():
            raise ValueError(f"Wiki '{wiki_name}' already exists")

        # Create directory structure
        wiki_path.mkdir(parents=True, exist_ok=True)
        (wiki_path / "sessions").mkdir(exist_ok=True)
        (wiki_path / "pages" / "characters").mkdir(parents=True, exist_ok=True)
        (wiki_path / "pages" / "locations").mkdir(parents=True, exist_ok=True)
        (wiki_path / "pages" / "items").mkdir(parents=True, exist_ok=True)
        (wiki_path / "pages" / "events").mkdir(parents=True, exist_ok=True)

        # Create metadata
        metadata = {
            "name": wiki_name,
            "safe_name": safe_name,
            "description": description,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "sessions": []
        }

        metadata_path = wiki_path / "wiki_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        # Create template examples
        self._create_template_examples(wiki_path)

        return metadata

    def _create_template_examples(self, wiki_path: Path):
        """Create example template files in the wiki"""
        templates = {
            "pages/characters/_template.md": """# {Character Name}

## Overview
Brief description

## Appearance
Physical description

## Personality
Key traits and behaviors

## Background
History and origin

## Relationships
- **{Name}**: {Relationship}

## Notes
Additional information
""",
            "pages/locations/_template.md": """# {Location Name}

## Description
What it looks like

## Notable Features
Key elements or landmarks

## Inhabitants
Who lives here or frequents this place

## Connections
Paths to other locations

## History
Background of this place

## Notes
""",
            "pages/items/_template.md": """# {Item Name}

## Description
Physical appearance

## Properties
Capabilities or effects

## Origin
Where it came from

## Current Status
Who has it, where it is

## Notes
""",
            "pages/events/_template.md": """# {Event Name}

## When
Time/date/session

## What Happened
Summary of the event

## Participants
Who was involved

## Consequences
Outcomes and impacts

## Notes
"""
        }

        for relative_path, content in templates.items():
            file_path = wiki_path / relative_path
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    # ========================================================================
    # Wiki Listing & Retrieval
    # ========================================================================

    def list_wikis(self) -> List[Dict]:
        """List all available wikis"""
        wikis = []

        if not self.wikis_dir.exists():
            return wikis

        for wiki_dir in self.wikis_dir.iterdir():
            if wiki_dir.is_dir():
                metadata_path = wiki_dir / "wiki_metadata.json"
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        wikis.append(metadata)

        # Sort by updated date (most recent first)
        wikis.sort(key=lambda x: x.get('updated', ''), reverse=True)
        return wikis

    def get_wiki_metadata(self, wiki_name: str) -> Dict:
        """Get metadata for a specific wiki"""
        safe_name = self._sanitize_name(wiki_name)
        metadata_path = self.wikis_dir / safe_name / "wiki_metadata.json"

        if not metadata_path.exists():
            raise ValueError(f"Wiki '{wiki_name}' not found")

        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # ========================================================================
    # Session Management
    # ========================================================================

    def save_session_to_wiki(self, wiki_name: str, session_id: str, conversation_history: List[Dict]):
        """Save a conversation session to a wiki"""
        safe_name = self._sanitize_name(wiki_name)
        wiki_path = self.wikis_dir / safe_name

        if not wiki_path.exists():
            raise ValueError(f"Wiki '{wiki_name}' not found")

        # Save session file
        session_path = wiki_path / "sessions" / f"{session_id}.json"
        session_data = {
            "session_id": session_id,
            "saved": datetime.now().isoformat(),
            "conversation": conversation_history
        }

        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)

        # Update wiki metadata
        metadata = self.get_wiki_metadata(wiki_name)
        if session_id not in metadata['sessions']:
            metadata['sessions'].append(session_id)
        metadata['updated'] = datetime.now().isoformat()

        metadata_path = wiki_path / "wiki_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def load_wiki_sessions(self, wiki_name: str) -> List[Dict]:
        """Load all sessions from a wiki"""
        safe_name = self._sanitize_name(wiki_name)
        sessions_dir = self.wikis_dir / safe_name / "sessions"

        if not sessions_dir.exists():
            return []

        sessions = []
        for session_file in sessions_dir.glob("*.json"):
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                sessions.append({
                    "session_id": session_data['session_id'],
                    "saved": session_data['saved'],
                    "message_count": len(session_data['conversation'])
                })

        sessions.sort(key=lambda x: x['saved'], reverse=True)
        return sessions

    def load_session_from_wiki(self, wiki_name: str, session_id: str) -> List[Dict]:
        """Load a specific session's conversation history"""
        safe_name = self._sanitize_name(wiki_name)
        session_path = self.wikis_dir / safe_name / "sessions" / f"{session_id}.json"

        if not session_path.exists():
            raise ValueError(f"Session '{session_id}' not found in wiki '{wiki_name}'")

        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
            return session_data['conversation']

    # ========================================================================
    # Wiki Pages Management
    # ========================================================================

    def list_wiki_pages(self, wiki_name: str, category: Optional[str] = None) -> Dict[str, List[str]]:
        """List all pages in a wiki, optionally filtered by category"""
        safe_name = self._sanitize_name(wiki_name)
        pages_dir = self.wikis_dir / safe_name / "pages"

        if not pages_dir.exists():
            return {}

        pages = {}
        categories = [category] if category else ["characters", "locations", "items", "events"]

        for cat in categories:
            cat_dir = pages_dir / cat
            if cat_dir.exists():
                pages[cat] = [
                    f.stem for f in cat_dir.glob("*.md")
                ]

        return pages

    def read_wiki_page(self, wiki_name: str, category: str, page_name: str) -> str:
        """Read a wiki page's content"""
        safe_name = self._sanitize_name(wiki_name)
        safe_page = self._sanitize_name(page_name)
        page_path = self.wikis_dir / safe_name / "pages" / category / f"{safe_page}.md"

        if not page_path.exists():
            raise ValueError(f"Page '{page_name}' not found in category '{category}'")

        with open(page_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_wiki_page(self, wiki_name: str, category: str, page_name: str, content: str):
        """Write or update a wiki page"""
        safe_name = self._sanitize_name(wiki_name)
        safe_page = self._sanitize_name(page_name)
        page_path = self.wikis_dir / safe_name / "pages" / category / f"{safe_page}.md"

        # Ensure category directory exists
        page_path.parent.mkdir(parents=True, exist_ok=True)

        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Update wiki metadata timestamp
        metadata = self.get_wiki_metadata(wiki_name)
        metadata['updated'] = datetime.now().isoformat()

        metadata_path = self.wikis_dir / safe_name / "wiki_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def delete_wiki_page(self, wiki_name: str, category: str, page_name: str):
        """Delete a wiki page"""
        safe_name = self._sanitize_name(wiki_name)
        safe_page = self._sanitize_name(page_name)
        page_path = self.wikis_dir / safe_name / "pages" / category / f"{safe_page}.md"

        if page_path.exists():
            page_path.unlink()

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _sanitize_name(self, name: str) -> str:
        """Convert name to filesystem-safe format"""
        # Replace spaces with underscores, remove special characters
        safe = name.replace(" ", "_")
        safe = "".join(c for c in safe if c.isalnum() or c in "_-")
        return safe.lower()
