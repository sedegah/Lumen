import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


BOOKMARKS_FILE = os.path.join(
    os.path.expanduser("~"), ".lumencli_bookmarks.json"
)


@dataclass
class Bookmark:
    """A single bookmark entry."""
    url: str
    title: str
    added: str = ""

    def to_dict(self) -> dict:
        return {"url": self.url, "title": self.title, "added": self.added}

    @staticmethod
    def from_dict(d: dict) -> "Bookmark":
        return Bookmark(
            url=d.get("url", ""),
            title=d.get("title", ""),
            added=d.get("added", ""),
        )


class BookmarkManager:
    """Manages bookmark storage and retrieval."""

    def __init__(self, filepath: str = BOOKMARKS_FILE):
        self.filepath = filepath
        self._bookmarks: list[Bookmark] = []
        self._load()

    def _load(self):
        """Load bookmarks from disk."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._bookmarks = [Bookmark.from_dict(d) for d in data]
            except (json.JSONDecodeError, KeyError):
                self._bookmarks = []
        else:
            self._bookmarks = []

    def _save(self):
        """Persist bookmarks to disk."""
        data = [b.to_dict() for b in self._bookmarks]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(self, url: str, title: str = "") -> Bookmark:
        """Add a bookmark. Returns the created Bookmark."""
        # Avoid duplicates
        for b in self._bookmarks:
            if b.url == url:
                return b
        bm = Bookmark(
            url=url,
            title=title or url,
            added=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        self._bookmarks.append(bm)
        self._save()
        return bm

    def remove(self, url: str) -> bool:
        """Remove a bookmark by URL. Returns True if found."""
        before = len(self._bookmarks)
        self._bookmarks = [b for b in self._bookmarks if b.url != url]
        if len(self._bookmarks) < before:
            self._save()
            return True
        return False

    def list_all(self) -> list[Bookmark]:
        """Return all bookmarks."""
        return list(self._bookmarks)

    def get(self, number: int) -> Optional[Bookmark]:
        """Get bookmark by 1-based index."""
        idx = number - 1
        if 0 <= idx < len(self._bookmarks):
            return self._bookmarks[idx]
        return None
