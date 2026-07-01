from typer.testing import CliRunner

from x_agentic_workflow.cli import app


def test_tui_app_is_textual_app() -> None:
    from textual.app import App

    from x_agentic_workflow.tui import XawTuiApp

    assert issubclass(XawTuiApp, App)
    assert "submit" in {binding.action for binding in XawTuiApp.BINDINGS}
    assert {"doctor", "approval_panel", "clear"}.issubset(
        {binding.action for binding in XawTuiApp.BINDINGS}
    )
    assert {"next_session", "previous_session", "open_session"}.issubset(
        {binding.action for binding in XawTuiApp.BINDINGS}
    )


def test_tui_panel_renderers_include_hybrid_sections(tmp_path) -> None:
    from x_agentic_workflow.tui import (
        TuiPanelState,
        _render_approval,
        _render_extensions,
        _render_help,
        _render_sessions,
        _render_status,
        _render_tools,
    )

    state = TuiPanelState(
        provider="openai-compatible",
        model="gpt-4.1",
        api_key_present=True,
        session_id="20260701-000000",
        workdir=tmp_path,
        sessions=("20260701-000000",),
        skills_count=2,
        hooks_count=1,
        mcp_servers_count=3,
        tools=("read_file", "run_command"),
        approval_required=True,
        selected_session_id="20260701-000000",
        timeline=("→ write_file {'path': 'x.txt'}", "← write_file ok: Wrote x.txt"),
        latest_diff="--- a/x.txt\n+++ b/x.txt\n@@\n-old\n+new",
        mode="Review",
    )

    assert "provider: openai-compatible" in _render_status(state)
    assert "active:" in _render_sessions(state)
    assert "mcp servers: 3" in _render_extensions(state)
    assert "run_command" in _render_tools(state)
    assert "command approval: enabled" in _render_approval(state)
    from x_agentic_workflow.tui import _render_diff, _render_timeline

    assert "Tool Timeline" in _render_timeline(state)
    assert "write_file" in _render_timeline(state)
    assert "Diff Viewer" in _render_diff(state)
    assert "+new" in _render_diff(state)
    assert "Ctrl+D doctor" in _render_help()
    assert "Ctrl+O open session" in _render_help()


def test_openai_compatible_smoke_can_skip_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runner = CliRunner()

    result = runner.invoke(app, ["smoke-openai-compatible", "--allow-skip"])

    assert result.exit_code == 0
    assert "SKIPPED" in result.output
