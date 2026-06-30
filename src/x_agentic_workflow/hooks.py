"""Simple hook runner for lifecycle automation."""

from __future__ import annotations

import subprocess
from pathlib import Path


class HookRunner:
    def __init__(self, root: Path, enabled: bool = True) -> None:
        self.root = root
        self.enabled = enabled
        self.root.mkdir(parents=True, exist_ok=True)

    def run(self, event: str, cwd: Path) -> list[str]:
        if not self.enabled:
            return []
        event_dir = self.root / event
        if not event_dir.exists():
            return []
        outputs: list[str] = []
        for script in sorted(event_dir.iterdir()):
            if not script.is_file():
                continue
            result = subprocess.run(
                [str(script)],
                cwd=cwd,
                text=True,
                capture_output=True,
                timeout=30,
            )
            out = ((result.stdout or "") + (result.stderr or "")).strip()
            outputs.append(f"{script.name}: exit {result.returncode}\n{out}")
        return outputs
