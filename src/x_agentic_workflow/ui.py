"""Terminal UI helpers."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()


def user_prompt() -> str:
    return Prompt.ask("[bold green]you[/bold green]")


def assistant(text: str) -> None:
    if text.strip():
        console.print(Panel(text, title="agent", border_style="blue"))


def stream_text(text: str) -> None:
    console.print(text, end="")


def tool_call(name: str, args: dict[str, object]) -> None:
    console.print(f"[yellow]tool[/yellow] {name} [dim]{args}[/dim]")


def tool_result(text: str) -> None:
    preview = text if len(text) <= 800 else text[:800] + "…"
    console.print(f"[dim]{preview}[/dim]")


def error(text: str) -> None:
    console.print(f"[red]error[/red] {text}")


def approve(prompt: str) -> bool:
    return Confirm.ask(prompt, default=False)
