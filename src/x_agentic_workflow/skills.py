"""Lightweight local skills.

Skills are markdown files with optional YAML-like metadata. Full skill content is
loaded into the system prompt only when the user asks for that skill by name.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    description: str
    content: str
    path: Path


class SkillRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def discover(self) -> list[Skill]:
        skills: list[Skill] = []
        for path in sorted(self.root.rglob("*.md")):
            content = path.read_text(encoding="utf-8")
            name = path.stem
            description = ""
            for line in content.splitlines()[:20]:
                if line.lower().startswith("name:"):
                    name = line.partition(":")[2].strip()
                if line.lower().startswith("description:"):
                    description = line.partition(":")[2].strip()
            skills.append(Skill(name=name, description=description, content=content, path=path))
        return skills

    def matching_prompt(self, user_text: str) -> str:
        wanted = []
        lowered = user_text.lower()
        for skill in self.discover():
            if skill.name.lower() in lowered:
                wanted.append(f"# Skill: {skill.name}\n\n{skill.content}")
        return "\n\n".join(wanted)
