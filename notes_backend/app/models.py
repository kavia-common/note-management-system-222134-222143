from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# PUBLIC_INTERFACE
@dataclass
class Note:
    """A simple Note model used for JSON-serializable storage."""
    id: str
    title: str
    content: str
    created_at: float
    updated_at: float
    tags: List[str] = field(default_factory=list)

    # PUBLIC_INTERFACE
    def to_dict(self) -> Dict:
        """Return a JSON-serializable dict representation of the Note."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Note":
        """Create a Note from a dict."""
        return Note(
            id=str(data["id"]),
            title=str(data.get("title", "")),
            content=str(data.get("content", "")),
            created_at=float(data.get("created_at", time.time())),
            updated_at=float(data.get("updated_at", time.time())),
            tags=list(data.get("tags", [])),
        )


class NoteStorage:
    """Thread-safe in-memory storage with optional JSON file persistence."""

    def __init__(self, persist_path: Optional[Path] = None) -> None:
        self._lock = threading.RLock()
        self._notes: Dict[str, Note] = {}
        self._persist_path = persist_path
        if self._persist_path:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_from_file()

    def _load_from_file(self) -> None:
        with self._lock:
            if not self._persist_path or not self._persist_path.exists():
                return
            try:
                raw = self._persist_path.read_text(encoding="utf-8")
                if not raw.strip():
                    return
                data = json.loads(raw)
                self._notes = {str(n["id"]): Note.from_dict(n) for n in data}
            except (OSError, json.JSONDecodeError):
                # If file is corrupt or unreadable, start fresh but do not crash
                self._notes = {}

    def _save_to_file(self) -> None:
        if not self._persist_path:
            return
        with self._lock:
            try:
                data = [n.to_dict() for n in self._notes.values()]
                tmp_path = self._persist_path.with_suffix(".tmp")
                tmp_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
                tmp_path.replace(self._persist_path)
            except OSError:
                # Don't crash API on persistence errors
                pass

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return a list of all notes."""
        with self._lock:
            return list(self._notes.values())

    # PUBLIC_INTERFACE
    def get_note(self, note_id: str) -> Optional[Note]:
        """Return a note by id, or None if not found."""
        with self._lock:
            return self._notes.get(str(note_id))

    # PUBLIC_INTERFACE
    def create_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> Note:
        """Create and persist a new note, returning the created Note."""
        now = time.time()
        # very simple id: epoch-ms string; keeps it opaque and unique enough for demo
        note_id = str(int(now * 1000))
        note = Note(
            id=note_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
            tags=list(tags or []),
        )
        with self._lock:
            self._notes[note_id] = note
            self._save_to_file()
            return note

    # PUBLIC_INTERFACE
    def update_note(
        self, note_id: str, title: Optional[str] = None, content: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> Optional[Note]:
        """Update a note fields; returns updated Note or None if not found."""
        with self._lock:
            note = self._notes.get(str(note_id))
            if not note:
                return None
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            if tags is not None:
                note.tags = list(tags)
            note.updated_at = time.time()
            self._save_to_file()
            return note

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: str) -> bool:
        """Delete a note; returns True if deleted, False if not found."""
        with self._lock:
            removed = self._notes.pop(str(note_id), None)
            if removed is None:
                return False
            self._save_to_file()
            return True


# Create a default storage instance with file-based persistence in a local data directory.
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "notes.json"
storage = NoteStorage(persist_path=DEFAULT_DATA_PATH)
