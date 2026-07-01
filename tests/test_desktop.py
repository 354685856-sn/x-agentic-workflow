from x_agentic_workflow.desktop import render_desktop_html


def test_desktop_html_contains_clean_room_app_shell() -> None:
    html = render_desktop_html()

    assert "x-agentic-workflow" in html
    assert "Local clean-room UI" in html
    assert "New chat" in html
    assert "How can I help you today?" in html
    assert "/api/ask" in html
