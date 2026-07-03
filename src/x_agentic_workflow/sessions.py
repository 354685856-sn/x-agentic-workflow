"""Conversation session persistence."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
        data = self.load_payload(session_id)
        return [Message(**item) for item in data.get("messages", [])]

    def load_payload(self, session_id: str) -> dict[str, Any]:
        path = self.path_for(session_id)
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data

    def save(self, session_id: str, messages: list[Message]) -> None:
        path = self.path_for(session_id)
        payload = self.load_payload(session_id)
        payload.update(
            {
                "session_id": session_id,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "messages": [asdict(m) for m in messages],
            }
        )
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def load_file_changes(self, session_id: str) -> list[dict[str, Any]]:
        data = self.load_payload(session_id)
        changes = data.get("file_changes", [])
        if not isinstance(changes, list):
            return []
        return [change for change in changes if isinstance(change, dict)]

    def save_file_changes(self, session_id: str, changes: list[dict[str, Any]]) -> None:
        path = self.path_for(session_id)
        payload = {
            **self.load_payload(session_id),
            "session_id": session_id,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "file_changes": changes,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def list_sessions(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))
