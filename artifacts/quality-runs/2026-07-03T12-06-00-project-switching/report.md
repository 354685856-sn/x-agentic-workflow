# Quality Run: v0.8.0 Project Switching

Date: 2026-07-03

Scope: desktop project path switching, recent-project persistence, automatic
post-switch validation, invalid-path rejection, and release packaging checks.

## Commands Run

```bash
.venv/bin/python -m pytest tests/test_desktop.py -q
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src/x_agentic_workflow
.venv/bin/xaw --version
.venv/bin/xaw desktop --help
.venv/bin/xaw smoke-openai-compatible --allow-skip
.venv/bin/xaw desktop --host 127.0.0.1 --port 8767 --no-browser
curl -s -X POST http://127.0.0.1:8767/api/project/switch -H 'content-type: application/json' -d '{"path":"<temporary-project>"}'
.venv/bin/python -m build
.venv/bin/python -m twine check dist/x_agentic_workflow-0.8.0*
```

## Results

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest tests/test_desktop.py -q` | PASS, 11 tests |
| `.venv/bin/python -m pytest` | PASS, 26 tests |
| `.venv/bin/python -m ruff check src tests` | PASS |
| `.venv/bin/python -m mypy src/x_agentic_workflow` | PASS |
| `.venv/bin/xaw --version` | PASS, `0.8.0` |
| `.venv/bin/xaw desktop --help` | PASS |
| `.venv/bin/xaw smoke-openai-compatible --allow-skip` | PASS, skipped because `OPENAI_API_KEY` is absent |
| `xaw desktop --no-browser` + `/api/project/switch` | PASS, switched to a temporary project, returned recent-project state, and re-ran validation |
| `.venv/bin/python -m build` | PASS, built `x_agentic_workflow-0.8.0.tar.gz` and `x_agentic_workflow-0.8.0-py3-none-any.whl` |
| `.venv/bin/python -m twine check dist/x_agentic_workflow-0.8.0*` | PASS |

## API Smoke Result

The `/api/project/switch` response for a temporary README-only project included:

- new `workdir` pointing to the temporary project
- `projectSwitch.ok: true`
- `recentProjects[0].active: true`
- `projectValidation` with `README.md` detected
- git warning because the temporary project was not a git repository

The temporary smoke path was removed from local `~/.x-agentic-workflow/config.json`
after the test so the developer environment was not left with a scratch recent
project.

## Confidence

Medium-high for this scoped feature.

## Scope Risk

Low-to-moderate. Workdir switching is stateful, but the change stays local to
the desktop runtime and does not execute arbitrary project commands.
