import socket
from http.server import BaseHTTPRequestHandler

from x_agentic_workflow.desktop import _create_server, render_desktop_html


def test_desktop_html_contains_clean_room_app_shell() -> None:
    html = render_desktop_html()

    assert "x-agentic-workflow" in html
    assert "Local clean-room UI" in html
    assert "New chat" in html
    assert "How can I help you today?" in html
    assert "/api/ask" in html


def test_desktop_server_falls_back_when_preferred_port_is_busy() -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            self.send_response(200)
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        busy_port = sock.getsockname()[1]

        server = _create_server("127.0.0.1", busy_port, Handler)

    try:
        assert server.server_port != busy_port
        assert server.server_port > 0
    finally:
        server.server_close()
