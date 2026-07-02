"""Clean-room local browser UI for x-agentic-workflow."""
# ruff: noqa: E501

import errno
import json
import socket
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast

from .agent import Agent
from .config import RuntimeConfig
from .sessions import SessionStore


def run_desktop(
    config: RuntimeConfig | None = None,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    """Start the clean-room browser UI server."""

    runtime_config = config or RuntimeConfig.load(workdir=Path.cwd())
    app = DesktopApp(runtime_config)
    server = _create_server(host, port, _handler_for(app))
    url = f"http://{host}:{server.server_port}"
    if open_browser:
        threading.Timer(0.2, lambda: webbrowser.open(url)).start()
    print(f"x-agentic-workflow desktop UI running at {url}", flush=True)  # noqa: T201
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _create_server(
    host: str,
    port: int,
    handler: type[BaseHTTPRequestHandler],
) -> ThreadingHTTPServer:
    if port != 0 and _port_has_listener(host, port):
        return ThreadingHTTPServer((host, 0), handler)
    try:
        return ThreadingHTTPServer((host, port), handler)
    except OSError as exc:
        if exc.errno != errno.EADDRINUSE or port == 0:
            raise
        return ThreadingHTTPServer((host, 0), handler)


def _port_has_listener(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


class DesktopApp:
    """Small HTTP facade over the existing CLI agent runtime."""

    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.sessions = SessionStore(config.sessions_dir)
        self.agent = Agent(config)
        self.messages: list[dict[str, str]] = []

    def state(self) -> dict[str, Any]:
        return {
            "provider": self.config.provider.name,
            "model": self.config.provider.model,
            "apiKeyPresent": bool(self.config.api_key),
            "workdir": str(self.config.workdir),
            "sessionId": self.agent.session_id,
            "sessions": list(reversed(self.sessions.list_sessions()[-8:])),
            "messages": self.messages[-30:],
        }

    def new_chat(self) -> dict[str, Any]:
        self.agent = Agent(self.config)
        self.messages = []
        return self.state()

    def open_session(self, session_id: str) -> dict[str, Any]:
        self.agent = Agent(self.config, session_id=session_id)
        self.messages = [
            {"role": message.role, "content": message.content}
            for message in self.agent.messages
            if message.role in {"user", "assistant"}
        ]
        return self.state()

    def ask(self, prompt: str) -> dict[str, Any]:
        text = prompt.strip()
        if not text:
            return self.state()
        self.messages.append({"role": "user", "content": text})
        try:
            answer = self.agent.run_once(text)
        except Exception as exc:  # noqa: BLE001 - API errors are rendered in the UI
            answer = f"{type(exc).__name__}: {exc}"
            self.messages.append({"role": "error", "content": answer})
            return self.state()
        if answer:
            self.messages.append({"role": "assistant", "content": answer})
        return self.state()


def _handler_for(app: DesktopApp) -> type[BaseHTTPRequestHandler]:
    class DesktopHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
            if self.path in {"/", "/index.html"}:
                self._send_html(render_desktop_html())
                return
            if self.path == "/api/state":
                self._send_json(app.state())
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
            payload = self._read_json()
            if self.path == "/api/new":
                self._send_json(app.new_chat())
                return
            if self.path == "/api/open":
                self._send_json(app.open_session(str(payload.get("sessionId", ""))))
                return
            if self.path == "/api/ask":
                self._send_json(app.ask(str(payload.get("prompt", ""))))
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length", "0"))
            if length <= 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return cast(dict[str, Any], json.loads(raw or "{}"))

        def _send_html(self, html: str) -> None:
            data = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return DesktopHandler


def render_desktop_html() -> str:
    """Return the clean-room desktop UI shell."""

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>x-agentic-workflow</title>
  <style>
    :root {
      --ink: #242321;
      --muted: #7c7973;
      --line: #ece9e3;
      --soft: #f7f5f1;
      --panel: #ffffff;
      --accent: #d97757;
      --shadow: 0 18px 55px rgba(34, 31, 28, .10);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: #fff; }
    .app { min-height: 100vh; display: grid; grid-template-columns: 310px 1fr; }
    aside {
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, #fbfaf7, #f8f6f2);
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .traffic { display: flex; gap: 10px; align-items: center; height: 26px; }
    .dot { width: 13px; height: 13px; border-radius: 99px; display: inline-block; }
    .red { background: #ff5f57; } .yellow { background: #febc2e; } .green { background: #28c840; }
    .tabs { display: grid; grid-template-columns: repeat(3, 1fr); padding: 4px; gap: 4px; background: #eeece8; border-radius: 12px; }
    .tab { border: 0; background: transparent; border-radius: 9px; padding: 9px 8px; color: #8a867f; font-size: 15px; cursor: pointer; }
    .tab.active { color: var(--ink); background: white; box-shadow: 0 1px 4px rgba(0,0,0,.12); font-weight: 650; }
    nav { display: grid; gap: 8px; }
    .nav-item, .recent-item, .profile, .update {
      border: 0;
      width: 100%;
      text-align: left;
      background: transparent;
      color: #403e3a;
      border-radius: 12px;
      padding: 9px 10px;
      font-size: 16px;
      cursor: pointer;
    }
    .nav-item:hover, .recent-item:hover { background: #efede8; }
    .section-title { color: #9a968f; font-size: 14px; margin: 18px 2px 4px; }
    .recents { flex: 1; overflow: auto; }
    .recent-item { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .update { background: white; border: 1px solid var(--line); box-shadow: 0 8px 25px rgba(0,0,0,.07); color: var(--muted); }
    .profile { border-top: 1px solid var(--line); border-radius: 0; padding-top: 16px; color: var(--muted); }
    main { position: relative; display: flex; flex-direction: column; min-width: 0; }
    .topbar { height: 58px; display: flex; justify-content: flex-end; align-items: center; padding: 0 28px; color: var(--muted); }
    .ghost { font-size: 24px; }
    .stage { flex: 1; display: flex; align-items: center; justify-content: center; padding: 28px; }
    .hero { width: min(880px, 100%); margin-top: -40px; }
    .greeting { text-align: center; font-family: Georgia, "Times New Roman", serif; font-size: clamp(42px, 6vw, 68px); line-height: 1.05; margin-bottom: 38px; color: #35322e; }
    .burst { color: var(--accent); font-family: ui-sans-serif, system-ui; margin-right: 16px; }
    .composer {
      background: white;
      border: 1px solid #e8e4de;
      border-radius: 28px;
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .notice { display: flex; gap: 12px; align-items: center; justify-content: space-between; padding: 16px 22px 10px; font-weight: 700; }
    .notice small { color: var(--muted); font-weight: 500; }
    textarea {
      width: 100%;
      min-height: 132px;
      resize: vertical;
      border: 0;
      outline: 0;
      padding: 20px 26px;
      font: inherit;
      font-size: 20px;
      color: var(--ink);
    }
    textarea::placeholder { color: #99958e; }
    .composer-footer { display: flex; align-items: center; justify-content: space-between; padding: 12px 22px 18px; }
    .round, .send {
      border: 1px solid var(--line);
      background: white;
      border-radius: 999px;
      min-width: 40px;
      height: 40px;
      padding: 0 14px;
      font-size: 16px;
      cursor: pointer;
    }
    .send { background: var(--ink); color: white; border-color: var(--ink); }
    .model { display: flex; gap: 12px; align-items: center; color: var(--muted); }
    .chips { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin-top: 26px; }
    .chip { border: 1px solid var(--line); background: white; border-radius: 13px; padding: 10px 16px; box-shadow: 0 3px 10px rgba(0,0,0,.05); font-size: 16px; }
    .messages { margin-top: 22px; display: grid; gap: 10px; max-height: 240px; overflow: auto; }
    .msg { border-radius: 16px; padding: 12px 14px; line-height: 1.45; white-space: pre-wrap; }
    .msg.user { background: var(--soft); justify-self: end; max-width: 78%; }
    .msg.assistant { background: white; border: 1px solid var(--line); }
    .msg.error { background: #fff1ef; color: #a23122; border: 1px solid #ffd4cc; }
    @media (max-width: 860px) {
      .app { grid-template-columns: 1fr; }
      aside { display: none; }
      .stage { padding: 18px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="traffic"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span></div>
      <div class="tabs"><button class="tab active">💬 Chat</button><button class="tab">☑ Cowork</button><button class="tab">⌘ Code</button></div>
      <nav>
        <button class="nav-item" id="newChat">＋ New chat</button>
        <button class="nav-item">▱ Projects</button>
        <button class="nav-item">◇ Artifacts</button>
        <button class="nav-item">▣ Customize</button>
      </nav>
      <div class="recents">
        <div class="section-title">Recents</div>
        <div id="recents"></div>
      </div>
      <button class="update">◌ Local clean-room UI</button>
      <div class="profile">● sn · local BYOK</div>
    </aside>
    <main>
      <div class="topbar"><span class="ghost">◌</span></div>
      <section class="stage">
        <div class="hero">
          <div class="greeting"><span class="burst">✳</span><span id="greeting">Good afternoon, sn</span></div>
          <div class="composer">
            <div class="notice"><span id="status">x-agentic-workflow is ready.</span><small id="workdir"></small></div>
            <textarea id="prompt" placeholder="How can I help you today?"></textarea>
            <div class="composer-footer">
              <button class="round">＋</button>
              <div class="model"><span id="model">model</span><button class="send" id="send">Send</button></div>
            </div>
          </div>
          <div class="chips">
            <button class="chip">✎ Write</button><button class="chip">▱ Learn</button><button class="chip">⌘ Code</button><button class="chip">☕ Life stuff</button><button class="chip">◇ XAW choice</button>
          </div>
          <div class="messages" id="messages"></div>
        </div>
      </section>
    </main>
  </div>
  <script>
    const $ = (id) => document.getElementById(id);
    async function api(path, body) {
      const res = await fetch(path, { method: body ? 'POST' : 'GET', headers: {'content-type': 'application/json'}, body: body ? JSON.stringify(body) : undefined });
      return await res.json();
    }
    function render(state) {
      $('status').textContent = state.apiKeyPresent ? 'x-agentic-workflow is ready.' : 'API key missing. Set your BYOK environment variable to run prompts.';
      $('workdir').textContent = state.workdir.split('/').slice(-2).join('/');
      $('model').textContent = state.model;
      $('recents').innerHTML = state.sessions.map(s => `<button class="recent-item" data-session="${s}">${s}</button>`).join('') || '<div class="section-title">No sessions yet</div>';
      $('messages').innerHTML = state.messages.map(m => `<div class="msg ${m.role}">${escapeHtml(m.content)}</div>`).join('');
      document.querySelectorAll('[data-session]').forEach(btn => btn.onclick = async () => render(await api('/api/open', {sessionId: btn.dataset.session})));
    }
    function escapeHtml(text) {
      return text.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
    }
    async function send() {
      const prompt = $('prompt').value.trim();
      if (!prompt) return;
      $('prompt').value = '';
      $('status').textContent = 'Running...';
      render(await api('/api/ask', {prompt}));
    }
    $('send').onclick = send;
    $('prompt').addEventListener('keydown', e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send(); });
    $('newChat').onclick = async () => render(await api('/api/new', {}));
    api('/api/state').then(render);
  </script>
</body>
</html>"""
