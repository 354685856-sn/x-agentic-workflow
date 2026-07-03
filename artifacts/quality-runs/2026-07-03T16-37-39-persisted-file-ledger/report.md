# v0.11.0 Persisted File Ledger Quality Run

Date: 2026-07-03

## Scope

- Persist desktop file-change ledger metadata in session JSON.
- Restore file-change ledger when opening a saved desktop session.
- Add selected diff state and `/api/diff/select` for multi-file diff review.
- Preserve compatibility with old session JSON payloads.

## Commands

```bash
.venv/bin/python -m pytest tests/test_desktop.py -q
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src/x_agentic_workflow
.venv/bin/xaw --version
.venv/bin/xaw desktop --help
.venv/bin/xaw smoke-openai-compatible --allow-skip
.venv/bin/python -m build
.venv/bin/python -m twine check dist/x_agentic_workflow-0.11.0*
```

## Results

- `tests/test_desktop.py`: passed, 18 tests.
- Full pytest suite: passed, 33 tests.
- Ruff: passed.
- Mypy: passed.
- `.venv/bin/xaw --version`: `0.11.0`.
- `.venv/bin/xaw desktop --help`: passed.
- `.venv/bin/xaw smoke-openai-compatible --allow-skip`: skipped safely because
  `OPENAI_API_KEY` is not set.
- Build: passed, generated `x_agentic_workflow-0.11.0.tar.gz` and
  `x_agentic_workflow-0.11.0-py3-none-any.whl`.
- Twine check: passed for both v0.11.0 artifacts.

## Evidence Notes

- `SessionStore.load()` remains message-focused for existing CLI/TUI callers.
- `SessionStore.save()` now preserves existing metadata such as `file_changes`.
- Desktop state exposes `selectedDiff`, `selectedDiffIndex`, and keeps
  `latestDiff` as a compatibility alias for the selected diff.

## Confidence

Medium-high.

## Scope Risk

Low-to-moderate. The persistence format is additive and older session JSON files
without `file_changes` are covered by tests.
