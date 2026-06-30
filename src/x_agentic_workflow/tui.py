"""Full-screen Textual interface for x-agentic-workflow."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from .agent import Agent
from .config import RuntimeConfig


class XawTuiApp(App[None]):
    """A compact full-screen terminal UI backed by the same Agent runtime."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #workspace {
        height: 1fr;
    }

    #sidebar {
        width: 32;
        padding: 1;
        background: $surface;
        border-right: solid $primary;
    }

    #transcript {
        height: 1fr;
        padding: 1;
    }

    #composer {
        height: 3;
        padding: 0 1;
        border-top: solid $primary;
    }

    #prompt {
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "submit", "Submit"),
        Binding("ctrl+r", "reset", "Reset"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(
        self,
        config: RuntimeConfig | None = None,
        agent: Agent | None = None,
        session_id: str | None = None,
    ) -> None:
        super().__init__()
        self.config = config or RuntimeConfig.load(workdir=Path.cwd())
        self.agent = agent or Agent(self.config, session_id=session_id)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="workspace"):
            with Vertical(id="sidebar"):
                yield Static("x-agentic-workflow", id="brand")
                yield Static(f"provider: {self.config.provider.name}")
                yield Static(f"model: {self.config.provider.model}")
                yield Static(f"workdir: {self.config.workdir}")
                yield Static("Ctrl+S submit · Ctrl+R reset · Ctrl+Q quit")
            yield RichLog(id="transcript", wrap=True, markup=True)
        with Horizontal(id="composer"):
            yield Input(placeholder="Ask x-agentic-workflow…", id="prompt")
            yield Button("Send", id="send", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#transcript", RichLog)
        log.write(f"[bold blue]session[/bold blue] {self.agent.session_id}")
        self.query_one("#prompt", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send":
            self._submit(self.query_one("#prompt", Input).value)

    def action_submit(self) -> None:
        self._submit(self.query_one("#prompt", Input).value)

    def action_reset(self) -> None:
        self.query_one("#transcript", RichLog).clear()
        self.agent.messages = [self.agent.messages[0]]
        self.agent.sessions.save(self.agent.session_id, self.agent.messages)

    def _submit(self, text: str) -> None:
        prompt = text.strip()
        if not prompt:
            return
        prompt_box = self.query_one("#prompt", Input)
        transcript = self.query_one("#transcript", RichLog)
        prompt_box.value = ""
        transcript.write(f"[bold green]you[/bold green] {prompt}")
        try:
            answer = self.agent.run_once(prompt)
        except Exception as exc:  # noqa: BLE001 - render provider/tool failures in UI
            transcript.write(f"[bold red]error[/bold red] {type(exc).__name__}: {exc}")
            return
        if answer:
            transcript.write(f"[bold blue]agent[/bold blue] {answer}")
