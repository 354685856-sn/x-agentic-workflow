# Clean-room product and delivery lessons

Last updated: 2026-07-02

This note captures public product and release lessons from terminal AI coding
assistant products without copying, translating, or deriving implementation from
restricted source code.

## Source boundary

Allowed inputs:

- Public README capability descriptions.
- Public GitHub Release notes.
- Public screenshots and installation notes.
- Public issue titles or release-linked problem summaries.

Not allowed:

- Cloning or downloading repositories known to be based on leaked source code.
- Reading source files, internal module structure, prompts, constants, state
  machines, or implementation details from those repositories.
- Recreating implementation from leaked-source-derived code.

## Public product lessons to absorb

### 1. Desktop runtime choice is a product decision

Public release notes for `cc-haha` v0.4.0 describe a migration from Tauri to
Electron because system WebViews created different macOS and Windows behavior.
The explicit tradeoff was larger packages in exchange for a more consistent
Chromium rendering layer.

XAW decision:

- Keep `xaw desktop` as the lightweight clean-room local browser UI now.
- For a full customer desktop shell, evaluate Electron/Chromium first if
  cross-platform UI consistency becomes more important than package size.
- Do not assume a native WebView shell will behave the same across macOS,
  Windows, and Linux.

### 2. Customer distribution needs release engineering, not only UI

The public release notes repeatedly call out macOS DMG, Windows installer,
Linux AppImage/deb, signing, Gatekeeper, SmartScreen, and update metadata.

XAW decision:

- Maintain a staged delivery path:
  1. GitHub clone/download + repository `.app`.
  2. Preview DMG with bundled source.
  3. Signed and notarized macOS DMG.
  4. Cross-platform installers.
  5. Auto-update metadata.
- Every customer-facing release must verify first launch on a clean account,
  not only local developer startup.

### 3. Provider compatibility fails in slow and proxied environments

Public notes from v0.4.2 and v0.4.4 highlight slow third-party providers,
provider proxy behavior, loopback proxy bypass, connectivity checks, fallback
status, and trace redaction.

XAW decision:

- Add a provider settings page before advanced desktop features.
- Add provider connectivity checks for:
  - default cloud APIs;
  - OpenAI-compatible third-party APIs;
  - loopback/local providers;
  - proxied environments.
- Model calls need explicit timeout policy:
  - connect timeout;
  - first-token or first-byte timeout;
  - long-running healthy stream timeout;
  - user-visible fallback state.
- Provider traces must redact API keys, headers, MCP secrets, and env values.

### 4. Trace and activity views become required debugging surfaces

Public notes describe trace fixes for tool-call timing, live updates, aborted
API calls, pending calls, model/tool/session timing, and plugin/Skill usage.

XAW decision:

- Extend v0.3 Tool Timeline into a real Trace panel.
- Track at minimum:
  - request start/end;
  - provider/model;
  - tool name;
  - duration;
  - ok/error;
  - redacted metadata.
- Add “copy diagnostic bundle” later, with secrets removed by default.

### 5. Background tasks and session prewarm are high-risk

Public releases mention background task drawers, Goal continuation, session
prewarm races, history-session prewarm mistakes, and task notifications leaking
back into transcript/model context.

XAW decision:

- Do not add complex background agent continuation until session state is
  explicit.
- Separate:
  - user transcript;
  - model context;
  - internal task notifications;
  - UI-only activity logs.
- Background task UI should show status without automatically injecting task
  notifications into the model context.

### 6. Remote H5/mobile access needs persistence and lifecycle design

Public notes mention fixed H5 token/port, QR/bookmark survival after restart,
mobile keyboard/safe-area fixes, disconnect grace periods, and not killing a
running CLI too aggressively when a phone sleeps.

XAW decision:

- Treat mobile remote access as a separate feature phase.
- Persist token and port intentionally.
- Add disconnect grace period.
- Keep LAN/public access rules stricter than local loopback browser preview.
- Test iPhone Safari/Chrome keyboard and safe-area behavior before release.

### 7. Version alignment should be mechanically checked

Public release notes call out keeping desktop package version, Git tag, and
release notes aligned.

XAW decision:

- Add release checks for:
  - `pyproject.toml` version;
  - `src/x_agentic_workflow/__init__.py`;
  - Git tag;
  - GitHub Release title/body;
  - DMG filename;
  - docs release target.
- Avoid manually composing shell commands with unescaped backticks in release
  notes.

### 8. Real smoke matrix beats unit tests alone

Public release notes list smoke targets such as provider connectivity, slow
stream, background task drawer, trace deletion, MCP secrets redaction, native
browser preview, Windows window drag, macOS signed DMG first launch, and update
metadata.

XAW decision:

- Keep unit/lint/type/build gates.
- Add customer-flow smoke gates:
  - open `.app`;
  - start desktop UI;
  - configure provider;
  - run provider connectivity check;
  - open a project;
  - send a prompt;
  - inspect diff/tool timeline;
  - quit/reopen and resume session.

## Clean-room roadmap impact

Recommended next milestones:

1. v0.5 preview distribution:
   - build preview DMG;
   - document unsigned preview behavior;
   - test first launch from mounted DMG.
2. v0.6 provider setup:
   - UI settings page;
   - local secret entry;
   - connectivity checks;
   - redacted trace.
3. v0.7 project/workspace:
   - project selector;
   - workdir switching;
   - session list per project;
   - diff and file-change panel.
4. v0.8 production macOS:
   - Developer ID signing;
   - notarization;
   - stapling;
   - clean Mac smoke.
5. v0.9 remote/mobile:
   - H5 access token;
   - persistent port;
   - QR or copy link;
   - mobile UI QA.

