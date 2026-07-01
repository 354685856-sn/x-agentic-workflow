from typer.testing import CliRunner

from x_agentic_workflow.cli import app


def test_tui_app_is_textual_app() -> None:
    from textual.app import App

    from x_agentic_workflow.tui import XawTuiApp

    assert issubclass(XawTuiApp, App)
    assert "submit" in {binding.action for binding in XawTuiApp.BINDINGS}


def test_openai_compatible_smoke_can_skip_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runner = CliRunner()

    result = runner.invoke(app, ["smoke-openai-compatible", "--allow-skip"])

    assert result.exit_code == 0
    assert "SKIPPED" in result.output
