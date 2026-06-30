"""Configuration loading for x-agentic-workflow."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

ProviderName = Literal["anthropic", "openai-compatible"]

DEFAULT_CONFIG_DIR = Path.home() / ".x-agentic-workflow"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


@dataclass
class ProviderConfig:
    name: ProviderName = "anthropic"
    model: str = "claude-3-5-sonnet-latest"
    base_url: str | None = None
    api_key_env: str = "ANTHROPIC_API_KEY"


@dataclass
class RuntimeConfig:
    provider: ProviderConfig = field(default_factory=ProviderConfig)
    max_tokens: int = 4096
    temperature: float = 0.2
    workdir: Path = field(default_factory=lambda: Path.cwd().resolve())
    config_file: Path = DEFAULT_CONFIG_FILE
    max_output_chars: int = 20_000
    require_command_approval: bool = True
    sessions_dir: Path = field(default_factory=lambda: DEFAULT_CONFIG_DIR / "sessions")
    skills_dir: Path = field(default_factory=lambda: DEFAULT_CONFIG_DIR / "skills")
    hooks_dir: Path = field(default_factory=lambda: DEFAULT_CONFIG_DIR / "hooks")
    mcp_config_file: Path = field(default_factory=lambda: DEFAULT_CONFIG_DIR / "mcp.json")

    @property
    def api_key(self) -> str:
        return os.environ.get(self.provider.api_key_env, "").strip()

    @classmethod
    def load(cls, config_file: Path | None = None, workdir: Path | None = None) -> RuntimeConfig:
        load_dotenv(Path.cwd() / ".env")
        path = config_file or DEFAULT_CONFIG_FILE
        data: dict[str, Any] = {}
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))

        provider_data = data.get("provider", {})
        provider = ProviderConfig(
            name=provider_data.get("name", os.environ.get("XAW_PROVIDER", "anthropic")),
            model=provider_data.get(
                "model",
                os.environ.get("XAW_MODEL", "claude-3-5-sonnet-latest"),
            ),
            base_url=provider_data.get("base_url", os.environ.get("XAW_BASE_URL") or None),
            api_key_env=provider_data.get(
                "api_key_env",
                "OPENAI_API_KEY"
                if os.environ.get("XAW_PROVIDER") == "openai-compatible"
                else "ANTHROPIC_API_KEY",
            ),
        )
        return cls(
            provider=provider,
            max_tokens=int(data.get("max_tokens", os.environ.get("XAW_MAX_TOKENS", 4096))),
            temperature=float(data.get("temperature", os.environ.get("XAW_TEMPERATURE", 0.2))),
            workdir=(workdir or Path.cwd()).resolve(),
            config_file=path,
            max_output_chars=int(data.get("max_output_chars", 20_000)),
            require_command_approval=bool(data.get("require_command_approval", True)),
        )

    def validate_for_model_call(self) -> None:
        if self.provider.name not in {"anthropic", "openai-compatible"}:
            raise ValueError(f"Unsupported provider: {self.provider.name}")
        if not self.api_key:
            raise ValueError(
                f"{self.provider.api_key_env} is not set. Run `xaw init` or export the key."
            )

    def save(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "provider": {
                "name": self.provider.name,
                "model": self.provider.model,
                "base_url": self.provider.base_url,
                "api_key_env": self.provider.api_key_env,
            },
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_output_chars": self.max_output_chars,
            "require_command_approval": self.require_command_approval,
        }
        self.config_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
