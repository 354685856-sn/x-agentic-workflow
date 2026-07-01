"""Local multi-agent planning primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AgentRole:
    name: str
    instructions: str


DEFAULT_ROLES = [
    AgentRole("architect", "Focus on boundaries, risk, and design consistency."),
    AgentRole("implementer", "Focus on small, verifiable code changes."),
    AgentRole("reviewer", "Focus on regressions, security, and launch readiness."),
]


def role_prompt() -> str:
    lines = ["Available local agent roles for task decomposition:"]
    lines.extend(f"- {role.name}: {role.instructions}" for role in DEFAULT_ROLES)
    return "\n".join(lines)
