# v0.14.0 Provider Status UX Quality Run

Date: 2026-07-03

## Scope

- Render the actual saved provider configuration.
- Preserve unsaved provider form drafts.
- Block duplicate provider save/test submissions.
- Remove inactive provider controls and sample cards.

## Commands

```bash
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src/x_agentic_workflow
.venv/bin/xaw --version
.venv/bin/xaw desktop --help
.venv/bin/xaw smoke-openai-compatible --allow-skip
.venv/bin/python -m build
.venv/bin/python -m twine check dist/x_agentic_workflow-0.14.0*
```

## Results

- Targeted desktop tests: passed, 21 tests.
- Full pytest suite: passed, 36 tests.
- Ruff: passed.
- Mypy: passed.
- Browser smoke:
  - provider model draft survived chat/settings transitions.
  - dirty status displayed `未保存更改`.
  - two immediate save clicks produced one intercepted request.
  - successful save returned status to saved.
- `.venv/bin/xaw --version`: `0.14.0`.
- `.venv/bin/xaw desktop --help`: passed.
- `.venv/bin/xaw smoke-openai-compatible --allow-skip`: skipped safely because
  `OPENAI_API_KEY` is not set.
- Build: passed, generated `x_agentic_workflow-0.14.0.tar.gz` and
  `x_agentic_workflow-0.14.0-py3-none-any.whl`.
- Twine check: passed for both v0.14.0 artifacts.

## Evidence Notes

- Form values only resync from server state when clean or after successful save.
- Save/test buttons share one in-flight guard.
- Saved provider card is derived from runtime state instead of hardcoded samples.

## Confidence

Medium-high.

## Scope Risk

Low-to-moderate. Provider request contracts and secret storage remain unchanged.
