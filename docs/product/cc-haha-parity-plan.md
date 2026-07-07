# cc-haha Public Reference Parity Plan

This project uses the public `NanmiCoder/cc-haha` repository and released desktop behavior as a product reference only.

Clean-room boundary:
- Do not copy source files, implementation bodies, prompts, private constants, or text structures.
- Use public screenshots, release notes, README-level behavior, and high-level module structure as acceptance references.
- Implement cat-agentic behavior independently with local tests and browser verification.

Current focus:
1. Settings UI density and navigation parity.
2. Provider management: profiles, presets, default selection, and secret-safe persistence.
3. H5 access: explanatory copy, host/port/keepalive controls, and local backend persistence.
4. MCP settings: list view plus add-service form for stdio, streamable HTTP, and SSE definitions.
5. Agents and memory: browser-style presentation with real local data sources.

Next backlog:
1. Provider connection editing and deletion.
2. MCP server editing, disabling, deletion, and status checks.
3. IM adapter settings with real local pairing state.
4. Plugin page only when plugin backend exists.
5. Computer Use page only after the local capability can be installed and verified.
6. Token usage, Trace, and diagnostics pages backed by local runtime data.
