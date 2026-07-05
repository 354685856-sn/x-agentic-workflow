#!/bin/zsh
set -euo pipefail

APP_EXEC="$0"
APP_MACOS_DIR="$(cd "$(dirname "$APP_EXEC")" && pwd)"
APP_CONTENTS_DIR="$(cd "$APP_MACOS_DIR/.." && pwd)"
SOURCE_ROOT="$APP_CONTENTS_DIR/Resources/source"
APP_SUPPORT_DIR="$HOME/Library/Application Support/cat-agentic"
RUN_ROOT="$APP_SUPPORT_DIR/source"
LOG_DIR="$HOME/Library/Logs/cat-agentic"
LOG_FILE="$LOG_DIR/desktop-app.log"

mkdir -p "$LOG_DIR" "$APP_SUPPORT_DIR"

{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting Cat Agentic distribution app"

  if ! command -v python3 >/dev/null 2>&1; then
    osascript -e 'display dialog "python3 is required to run Cat Agentic. Install Python 3, then reopen the app." buttons {"OK"} default button "OK" with icon caution'
    exit 1
  fi

  if [[ ! -d "$SOURCE_ROOT" ]]; then
    osascript -e 'display dialog "The bundled app source is missing. Please download a fresh copy of Cat Agentic." buttons {"OK"} default button "OK" with icon caution'
    exit 1
  fi

  echo "Syncing bundled source to $RUN_ROOT"
  rm -rf "$RUN_ROOT"
  mkdir -p "$RUN_ROOT"
  ditto "$SOURCE_ROOT" "$RUN_ROOT"
  cd "$RUN_ROOT"

  if [[ ! -x ".venv/bin/python" ]]; then
    echo "Creating .venv"
    python3 -m venv .venv
  fi

  if [[ ! -x ".venv/bin/cat-agentic" ]]; then
    echo "Installing local package"
    .venv/bin/python -m pip install -q -e .
  else
    echo "Using existing local package"
  fi

  echo "Launching clean-room desktop UI"
  exec .venv/bin/cat-agentic desktop --host 127.0.0.1 --port 8765
} >>"$LOG_FILE" 2>&1
