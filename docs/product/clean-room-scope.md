# cat-agentic clean-room scope

`cat-agentic` targets the same product category as terminal AI coding
assistants such as Codex CLI, Gemini CLI, aider, Cline, and Claude-style local
coding assistants.

## Allowed references

- Original Python prototype from `files.zip`.
- Public API documentation for Anthropic, OpenAI-compatible chat completions,
  and MCP.
- General product behavior: CLI/TUI, headless mode, BYOK, tool calling,
  approval sandbox, sessions, skills, hooks, MCP, and multi-agent workflows.
- The SAFe harness in this repository as a development workflow.

## Prohibited references

- Copying or translating leaked source code.
- Copying private prompts, internal state machines, command implementations,
  UI text, constants, or module structures from restricted projects.
- Using restricted code as an implementation blueprint.

## v0.1 scope

- Python package installable with `pipx`.
- `cat-agentic chat` interactive terminal UI.
- `cat-agentic run -p` headless mode.
- Anthropic provider and OpenAI-compatible provider.
- BYOK via environment variables; config stores only provider metadata.
- Sandboxed file, search, and command tools.
- User approval before command execution.
- Session save/resume.
- Skills, hooks, MCP, and multi-agent extension points.
- Textual full-screen terminal UI behind `cat-agentic tui`.

## Later scope

- Full MCP JSON-RPC tool bridge.
- Desktop shell.
- More provider adapters.
- Independent worker processes for multi-agent execution.
