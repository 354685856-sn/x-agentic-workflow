from pathlib import Path

from x_agentic_workflow.config import RuntimeConfig
from x_agentic_workflow.tools import ToolRegistry, resolve_inside


def test_resolve_inside_blocks_path_escape(tmp_path: Path) -> None:
    try:
        resolve_inside(tmp_path, "../outside")
    except ValueError as exc:
        assert "escapes" in str(exc)
    else:
        raise AssertionError("path escape was allowed")


def test_file_tools_are_sandboxed_to_workdir(tmp_path: Path) -> None:
    config = RuntimeConfig(workdir=tmp_path)
    tools = ToolRegistry(config)

    write = tools.dispatch("write_file", {"path": "hello.txt", "content": "hello"})
    read = tools.dispatch("read_file", {"path": "hello.txt"})
    listing = tools.dispatch("list_dir", {"path": "."})

    assert write.ok
    assert read.content == "hello"
    assert "hello.txt" in listing.content


def test_search_returns_matches(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha\nbeta\n", encoding="utf-8")
    config = RuntimeConfig(workdir=tmp_path)

    result = ToolRegistry(config).dispatch("search", {"query": "beta"})

    assert result.ok
    assert "a.txt:2" in result.content


def test_write_file_returns_diff_metadata_for_existing_file(tmp_path: Path) -> None:
    (tmp_path / "hello.txt").write_text("old\n", encoding="utf-8")
    config = RuntimeConfig(workdir=tmp_path)

    result = ToolRegistry(config).dispatch(
        "write_file", {"path": "hello.txt", "content": "new\n"}
    )

    assert result.ok
    assert result.metadata["operation"] == "write_file"
    assert result.metadata["path"] == "hello.txt"
    assert result.metadata["existed"] is True
    assert "-old" in str(result.metadata["diff"])
    assert "+new" in str(result.metadata["diff"])
