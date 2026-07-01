"""Conversation session persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .types import Message


class SessionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, session_id: str) -> Path:
        safe = "".join(ch for ch in session_id if ch.isalnum() or ch in {"-", "_"})
        if not safe:
            raise ValueError("session_id cannot be empty")
        return self.root / f"{safe}.json"

    def new_id(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    def load(self, session_id: str) -> list[Message]:
        path = self.path_for(session_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Message(**item) for item in data.get("messages", [])]

    def save(self, session_id: str, messages: list[Message]) -> None:
        path = self.path_for(session_id)
        payload = {
            "session_id": session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "messages": [asdict(m) for m in messages],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def list_sessions(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))
