"""Sandboxed local tools."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import RuntimeConfig
from .types import ToolSpec
from .ui import approve


@dataclass
class ToolResult:
    ok: bool
    content: str


def tool_specs() -> list[ToolSpec]:
    return [
        ToolSpec(
            name="read_file",
            description="Read a UTF-8 text file inside the current project.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        ),
        ToolSpec(
            name="write_file",
            description="Create or overwrite a UTF-8 text file inside the current project.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        ),
        ToolSpec(
            name="list_dir",
            description="List files and folders inside the current project.",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        ),
        ToolSpec(
            name="search",
            description="Search project text files for a literal query.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "path": {"type": "string", "default": "."},
                },
                "required": ["query"],
            },
        ),
        ToolSpec(
            name="run_command",
            description="Run a shell command in the project after user approval.",
            input_schema={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        ),
    ]


def resolve_inside(workdir: Path, rel: str) -> Path:
    target = (workdir / rel).resolve()
    if target != workdir and workdir not in target.parents:
        raise ValueError(f"Path escapes project sandbox: {rel}")
    return target


class ToolRegistry:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config

    def dispatch(self, name: str, args: dict[str, object]) -> ToolResult:
        try:
            if name == "read_file":
                return self._read_file(str(args["path"]))
            if name == "write_file":
                return self._write_file(str(args["path"]), str(args["content"]))
            if name == "list_dir":
                return self._list_dir(str(args["path"]))
            if name == "search":
                return self._search(str(args["query"]), str(args.get("path", ".")))
            if name == "run_command":
                return self._run_command(str(args["command"]))
            return ToolResult(False, f"Unknown tool: {name}")
        except Exception as exc:
            return ToolResult(False, f"{type(exc).__name__}: {exc}")

    def _read_file(self, rel: str) -> ToolResult:
        path = resolve_inside(self.config.workdir, rel)
        if not path.is_file():
            return ToolResult(False, f"Not a file: {rel}")
        text = path.read_text(encoding="utf-8", errors="replace")
        return ToolResult(True, _truncate(text, self.config.max_output_chars))

    def _write_file(self, rel: str, content: str) -> ToolResult:
        path = resolve_inside(self.config.workdir, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return ToolResult(True, f"Wrote {len(content)} chars to {rel}")

    def _list_dir(self, rel: str) -> ToolResult:
        path = resolve_inside(self.config.workdir, rel)
        if not path.is_dir():
            return ToolResult(False, f"Not a directory: {rel}")
        entries = [child.name + ("/" if child.is_dir() else "") for child in sorted(path.iterdir())]
        return ToolResult(True, "\n".join(entries) if entries else "(empty)")

    def _search(self, query: str, rel: str) -> ToolResult:
        root = resolve_inside(self.config.workdir, rel)
        if not root.exists():
            return ToolResult(False, f"Path does not exist: {rel}")
        matches: list[str] = []
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
        for path in files:
            if _skip_file(path):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                for idx, line in enumerate(lines, 1):
                    if query in line:
                        shown = path.relative_to(self.config.workdir)
                        matches.append(f"{shown}:{idx}: {line.strip()}")
                        if len(matches) >= 100:
                            return ToolResult(True, "\n".join(matches) + "\n... [truncated]")
            except OSError:
                continue
        return ToolResult(True, "\n".join(matches) if matches else "(no matches)")

    def _run_command(self, command: str) -> ToolResult:
        if self.config.require_command_approval and not approve(
            f"Allow command in {self.config.workdir}: [bold]{command}[/bold]?"
        ):
            return ToolResult(False, "Command declined by user.")
        completed = subprocess.run(
            command,
            cwd=self.config.workdir,
            shell=True,
            text=True,
            capture_output=True,
            timeout=120,
        )
        output = ((completed.stdout or "") + (completed.stderr or "")).strip()
        return ToolResult(
            completed.returncode == 0,
            _truncate(f"exit code {completed.returncode}\n{output}", self.config.max_output_chars),
        )


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "\n... [truncated]"


def _skip_file(path: Path) -> bool:
    ignored = {".git", ".venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache"}
    return any(part in ignored for part in path.parts)
