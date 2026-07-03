# v0.13.0 Text Attachments Quality Run

Date: 2026-07-03

## Scope

- Make composer `+` select real text files.
- Add removable attachment chips.
- Enforce client and server attachment limits.
- Prevent stale asynchronous file-read callbacks.
- Keep raw attachment bodies out of restored transcript UI.

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
.venv/bin/python -m twine check dist/x_agentic_workflow-0.13.0*
```

## Results

- Targeted desktop tests: passed, 21 tests.
- Full pytest suite: passed, 36 tests.
- Ruff: passed.
- Mypy: passed.
- Browser attachment smoke: selected `notes.md`, rendered its chip, and removed
  it successfully without writing a fixture file.
- `.venv/bin/xaw --version`: `0.13.0`.
- `.venv/bin/xaw desktop --help`: passed.
- `.venv/bin/xaw smoke-openai-compatible --allow-skip`: skipped safely because
  `OPENAI_API_KEY` is not set.
- Build: passed, generated `x_agentic_workflow-0.13.0.tar.gz` and
  `x_agentic_workflow-0.13.0-py3-none-any.whl`.
- Twine check: passed for both v0.13.0 artifacts.

## Evidence Notes

- Server validates actual UTF-8 content byte size instead of trusting browser
  metadata.
- Session restore reconstructs attachment-name display from persisted context
  while hiding raw file bodies.
- Attachment async epoch is invalidated on send, new chat, session open, and
  project switch.

## Confidence

Medium-high.

## Scope Risk

Moderate. The feature adds user-controlled text context and asynchronous browser
reads, bounded by explicit limits and regression tests.
