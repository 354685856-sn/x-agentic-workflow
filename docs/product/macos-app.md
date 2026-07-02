# macOS double-click app

This repository includes a clean-room local macOS app launcher:

```text
apps/macos/X Agentic Workflow.app
```

After cloning or downloading the repository on macOS, a user can double-click
that app bundle to launch the browser desktop UI.

## What the app does

- Locates the repository root relative to the `.app` bundle.
- Creates `.venv` if it does not exist.
- Installs the local package with `pip install -e .`.
- Starts:

```bash
xaw desktop --host 127.0.0.1 --port 8765
```

- Opens the clean-room local UI in the default browser.
- If port `8765` is already in use, `xaw desktop` falls back to an available
  local port and opens that URL.

## Logs

Runtime logs are written to:

```text
~/Library/Logs/x-agentic-workflow/desktop-app.log
```

## Customer notes

- Python 3 must be available on the customer's Mac.
- API keys are not bundled or stored in the app. Users still bring their own
  keys through environment variables or future in-app settings.
- This launcher is suitable for GitHub download / developer preview use.
- For public distribution, build a signed and notarized `.dmg` or `.pkg`.
