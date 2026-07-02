# Legal open-source reference map

Last updated: 2026-07-02

This document converts legal, public open-source references into XAW product
requirements. It is not a source-code porting plan. Use it to guide clean-room
design and implementation.

## Clean-room rule

Allowed:

- Read normal open-source projects with clear public licenses.
- Learn product patterns, architecture tradeoffs, CLI behavior, docs, and tests.
- Implement original Python code with XAW's own modules, prompts, data models,
  and UI.

Not allowed:

- Use leaked-source-derived code as a reference.
- Translate modules or state machines from restricted projects.
- Copy prompts, constants, UI text, or internal implementation structure from
  restricted projects.

## Reference matrix

| Reference | Public lesson | XAW implementation direction |
| --- | --- | --- |
| OpenAI Codex CLI | Terminal-first local coding agent, approval/sandbox boundaries, app/CLI split | Keep CLI/TUI first-class; make desktop UI a shell over the same runtime, not a separate product |
| Google Gemini CLI | ReAct loop, built-in tools, MCP, provider/config-oriented terminal UX | Add explicit provider settings, config validation, MCP status, and model diagnostics |
| aider | Git-native editing workflow, visible diffs, undo/commit flow | Add file-change ledger, diff review, undo checkpoint, optional git commit command |
| Cline | Plan/Act mode, terminal command approval, real-time command output, MCP extension UX | Add mode switch, command approval queue, live command logs, MCP tool inventory |
| OpenHands | Sandbox/session/runtime separation, long-running environment issues, live preview | Separate project workspace, sandbox policy, task session, and UI state; add runtime health checks |
| Electron + React official guidance | Cross-platform UI consistency with Chromium; larger bundle and higher security responsibility | Use Electron only when browser UI is stable; enforce secure defaults: no remote Node integration, context isolation, strict IPC |
| cc-haha public README/Release notes only | Product/distribution lessons: DMG, signing, slow providers, proxy, trace, H5, background tasks | Absorb release lessons without reading source; keep these as roadmap and checklist inputs |

## XAW architecture principles from these references

### 1. One runtime, multiple surfaces

Surfaces:

- `xaw chat`
- `xaw run`
- `xaw tui`
- `xaw desktop`
- future Electron/React shell
- future H5/mobile remote shell

All surfaces should call the same Python runtime:

- provider adapters;
- agent loop;
- tools;
- session store;
- sandbox policy;
- Skills/Hooks/MCP registry;
- trace/event stream.

Avoid duplicating agent logic in UI code.

### 2. Trace before autonomy

Before adding multi-agent or background continuation, the user must be able to
see:

- what provider/model was called;
- what tool ran;
- what file changed;
- what command ran;
- what was approved/denied;
- how long each step took;
- what error occurred;
- what secrets were redacted.

### 3. Git-native safety

Borrow the product pattern from git-native tools, but implement our own:

- show dirty status before edits;
- save file-change metadata;
- show unified diff;
- add undo/checkpoint later;
- add commit helper later;
- never auto-commit without explicit user action.

### 4. Sandboxing is a product feature

Sandbox policy must be visible to the user:

- allowed workspace;
- blocked path escapes;
- command approval status;
- network/proxy state;
- future container/process sandbox health.

For the next milestones, keep the Python project-directory sandbox simple and
well-tested before adding Docker or remote sandboxes.

### 5. Provider setup is a first-run flow

Customer users should not need shell exports. The desktop UI needs:

- provider selector;
- base URL;
- model;
- API key entry;
- connection test;
- redacted storage/logging;
- import from env as an advanced option.

### 6. Desktop packaging should be staged

Current:

- repository `.app`;
- preview DMG with bundled source.

Next:

- signed app;
- notarized DMG;
- clean user smoke;
- update metadata.

Future:

- Electron shell if the browser UI proves valuable and needs a true native
  shell.

## Implementation milestones

### v0.5 Preview distribution

- Build preview DMG.
- Verify mounted DMG first launch.
- Document unsigned preview behavior.
- Add release checklist gates.

### v0.6 Provider settings

- Settings panel in clean-room UI.
- Save provider metadata.
- API key secure entry plan.
- Connectivity check.
- Redacted provider trace.

### v0.7 Project and diff workspace

- Project selector.
- Recent projects.
- Session list per project.
- File-change ledger.
- Diff viewer in desktop UI.

### v0.8 Approval and trace center

- Command approval queue.
- Live command logs.
- Trace panel.
- Diagnostic bundle with secret masking.

### v0.9 Desktop shell decision

- Evaluate staying with browser UI vs adding Electron.
- If Electron is chosen, build a minimal shell around the Python local server
  using secure Electron settings.

