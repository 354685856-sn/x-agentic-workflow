from pathlib import Path


def test_macos_app_bundle_launcher_exists_and_is_executable() -> None:
    root = Path(__file__).resolve().parents[1]
    app = root / "apps/macos/Cat Agentic.app"
    plist = app / "Contents/Info.plist"
    launcher = app / "Contents/MacOS/cat-agentic"

    assert plist.is_file()
    assert launcher.is_file()
    assert launcher.stat().st_mode & 0o111

    plist_text = plist.read_text(encoding="utf-8")
    launcher_text = launcher.read_text(encoding="utf-8")

    assert "Cat Agentic" in plist_text
    assert "com.nange.cat-agentic.local" in plist_text
    assert "cat-agentic desktop --host 127.0.0.1 --port 8765" in launcher_text
    assert "pip install -q -e ." in launcher_text
