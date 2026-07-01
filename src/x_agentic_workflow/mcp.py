"""MCP configuration placeholder.

The v0.1 runtime records MCP server definitions and exposes them in context.
Full JSON-RPC tool bridging is intentionally isolated behind this module so it
can be implemented without changing the agent loop.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class McpServer:
    name: str
    command: str
    args: list[str]


class McpRegistry:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file

    def list_servers(self) -> list[McpServer]:
        if not self.config_file.exists():
            return []
        data = json.loads(self.config_file.read_text(encoding="utf-8"))
        servers = []
        for name, spec in data.get("servers", {}).items():
            servers.append(
                McpServer(
                    name=name,
                    command=str(spec.get("command", "")),
                    args=[str(arg) for arg in spec.get("args", [])],
                )
            )
        return servers

    def context_summary(self) -> str:
        servers = self.list_servers()
        if not servers:
            return ""
        lines = ["Configured MCP servers:"]
        lines.extend(f"- {s.name}: {s.command} {' '.join(s.args)}".strip() for s in servers)
        return "\n".join(lines)
