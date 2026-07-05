"""Command line entrypoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

from . import __version__
from .agent import Agent
from .config import ProviderConfig, RuntimeConfig
from .providers import build_provider
from .sessions import SessionStore
from .tools import tool_specs
from .types import Message
from .ui import assistant, console, error

app = typer.Typer(help="cat-agentic terminal agent")


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool,
        typer.Option("--version", help="Show version.", is_eager=True),
    ] = False,
) -> None:
    if version:
        console.print(__version__)
        raise typer.Exit()


@app.command()
def init(
    provider: str = typer.Option("anthropic", help="anthropic or openai-compatible"),
    model: str = typer.Option("claude-3-5-sonnet-latest", help="Model name"),
    base_url: str | None = typer.Option(None, help="OpenAI-compatible base URL"),
    api_key_env: str | None = typer.Option(None, help="Environment variable holding API key"),
) -> None:
    """Create a local config file without storing secrets."""
    key_env = api_key_env or (
        "OPENAI_API_KEY" if provider == "openai-compatible" else "ANTHROPIC_API_KEY"
    )
    config = RuntimeConfig(
        provider=ProviderConfig(
            name=provider,  # type: ignore[arg-type]
            model=model,
            base_url=base_url,
            api_key_env=key_env,
        )
    )
    config.save()
    assistant(f"Wrote {config.config_file}. Put your key in {key_env}, not in the config file.")


@app.command()
def chat(
    session: str | None = typer.Option(None, help="Session id to resume"),
    cwd: Path | None = typer.Option(None, help="Project directory"),
) -> None:
    """Start the interactive terminal UI."""
    config = RuntimeConfig.load(workdir=cwd or Path.cwd())
    raise typer.Exit(Agent(config, session_id=session).run_interactive())


@app.command()
def run(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt to run once"),
    cwd: Path | None = typer.Option(None, help="Project directory"),
    session: str | None = typer.Option(None, help="Session id to resume"),
) -> None:
    """Run one prompt and print the final answer."""
    config = RuntimeConfig.load(workdir=cwd or Path.cwd())
    try:
        text = Agent(config, session_id=session).run_once(prompt)
    except Exception as exc:
        error(str(exc))
        raise typer.Exit(1) from exc
    if text:
        console.print(text)


@app.command()
def tui() -> None:
    """Start the full-screen Textual terminal UI."""
    from .tui import XawTuiApp

    XawTuiApp().run()


@app.command()
def desktop(
    host: str = typer.Option("127.0.0.1", help="Host for the local clean-room UI server"),
    port: int = typer.Option(8765, help="Port for the local clean-room UI server"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not open the browser"),
) -> None:
    """Start the clean-room browser desktop UI."""
    from .desktop import run_desktop

    run_desktop(host=host, port=port, open_browser=not no_browser)


@app.command("sessions")
def sessions_cmd() -> None:
    """List saved sessions."""
    config = RuntimeConfig.load()
    store = SessionStore(config.sessions_dir)
    table = Table("session")
    for session_id in store.list_sessions():
        table.add_row(session_id)
    console.print(table)


@app.command()
def doctor() -> None:
    """Check local runtime readiness."""
    config = RuntimeConfig.load()
    table = Table("check", "value")
    table.add_row("provider", config.provider.name)
    table.add_row("model", config.provider.model)
    table.add_row("base_url", config.provider.base_url or "(default)")
    table.add_row("api_key_env", config.provider.api_key_env)
    table.add_row("api_key_present", "yes" if os.environ.get(config.provider.api_key_env) else "no")
    table.add_row("workdir", str(config.workdir))
    table.add_row("sessions_dir", str(config.sessions_dir))
    console.print(table)


@app.command()
def smoke_openai_compatible(
    allow_skip: bool = typer.Option(
        False,
        "--allow-skip",
        help="Exit 0 with SKIPPED when OPENAI_API_KEY is unavailable.",
    ),
    base_url: str | None = typer.Option(None, help="OpenAI-compatible base URL"),
    model: str = typer.Option("gpt-4.1-mini", help="Model name for the smoke call"),
) -> None:
    """Run a minimal OpenAI-compatible provider smoke check."""
    if not os.environ.get("OPENAI_API_KEY"):
        message = "SKIPPED: OPENAI_API_KEY is not set."
        if allow_skip:
            console.print(message)
            return
        error(message)
        raise typer.Exit(2)

    config = RuntimeConfig(
        provider=ProviderConfig(
            name="openai-compatible",
            model=model,
            base_url=base_url,
            api_key_env="OPENAI_API_KEY",
        )
    )
    provider = build_provider(config)
    response = provider.complete(
        [
            Message(role="system", content="Reply with exactly: ok"),
            Message(role="user", content="smoke"),
        ],
        tool_specs(),
    )
    console.print(response.text or "OK")


if __name__ == "__main__":
    app()
