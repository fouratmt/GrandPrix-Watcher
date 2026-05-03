from __future__ import annotations

import argparse
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from f1_race_monitor import LinkItem, NotifyConfig, build_config, load_config, notify
from f1_race_monitor.core import (
    as_string_list,
    fetch_html,
    notify_browser,
    notify_desktop,
    notify_macos,
    notify_webhook,
)


def make_args(**overrides: object) -> argparse.Namespace:
    defaults = {
        "config": "missing.toml",
        "url": None,
        "match_all": None,
        "match_any": None,
        "regex": None,
        "grand_prix": None,
        "event": None,
        "state_file": None,
        "max_pages": None,
        "notify": None,
        "webhook_url": None,
        "notify_existing": False,
        "include_seen": False,
        "interval": None,
        "watch": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_load_config_missing_file(tmp_path: Path) -> None:
    assert load_config(tmp_path / "missing.toml") == {}


def test_build_config_requires_url() -> None:
    with pytest.raises(SystemExit, match="Missing page URL"):
        build_config(make_args())


def test_as_string_list_rejects_invalid_type() -> None:
    with pytest.raises(TypeError, match="Expected string or list"):
        as_string_list(1)


def test_build_config_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
        [watch]
        url = "https://fullraces.com/2026"
        grand_prix = "china"
        event = "race"
        state_file = "state.json"
        notify_existing = true
        include_seen = true
        max_pages = 5
        interval_seconds = 30

        [notify]
        methods = ["console", "browser"]
        webhook_url = "https://example.com/hook"
        """,
        encoding="utf-8",
    )

    config = build_config(make_args(config=str(config_file)))

    assert config.watch.url == "https://fullraces.com/2026"
    assert config.watch.grand_prix_terms == ["chinese grand prix"]
    assert config.watch.regex == r"^RACE\s*-"
    assert config.watch.notify_existing is True
    assert config.watch.include_seen is True
    assert config.watch.max_pages == 5
    assert config.watch.interval_seconds == 30
    assert config.notify.methods == ["console", "browser"]
    assert config.notify.webhook_url == "https://example.com/hook"


def test_build_config_cli_overrides_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
        [watch]
        url = "https://fullraces.com/2026"
        grand_prix = "miami"

        [notify]
        methods = ["console"]
        """,
        encoding="utf-8",
    )

    config = build_config(
        make_args(
            config=str(config_file),
            grand_prix="japan",
            event="sprint",
            notify=["browser"],
            url="https://example.com/listing",
            max_pages=2,
        )
    )

    assert config.watch.url == "https://example.com/listing"
    assert config.watch.grand_prix_terms == ["japanese grand prix"]
    assert config.watch.regex == r"^Sprint\s*-"
    assert config.watch.max_pages == 2
    assert config.notify.methods == ["browser"]


def test_notify_dispatch(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    calls = []
    item = LinkItem("RACE - F1 2026 - Miami Grand Prix", "https://example.com/video")

    monkeypatch.setattr("f1_race_monitor.core.notify_console", lambda item: calls.append("console"))
    monkeypatch.setattr("f1_race_monitor.core.notify_macos", lambda item: calls.append("macos"))
    monkeypatch.setattr("f1_race_monitor.core.notify_browser", lambda item: calls.append("browser"))
    monkeypatch.setattr(
        "f1_race_monitor.core.notify_webhook",
        lambda item, url: calls.append(("webhook", url)),
    )

    notify(
        item,
        NotifyConfig(methods=["console", "macos", "browser", "webhook", "unknown"], webhook_url="hook"),
    )

    assert calls == ["console", "macos", "browser", ("webhook", "hook")]


def test_notify_macos_uses_osascript(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    calls = []
    item = LinkItem("Title", "https://example.com/video")

    monkeypatch.setattr("f1_race_monitor.core.platform.system", lambda: "Darwin")
    monkeypatch.setattr("f1_race_monitor.core.shutil.which", lambda command: "/usr/bin/osascript")
    monkeypatch.setattr("f1_race_monitor.core.subprocess.run", lambda args, check: calls.append(args))

    notify_macos(item)

    assert calls
    assert calls[0][0] == "osascript"


def test_notify_desktop_linux_uses_notify_send(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    calls = []
    item = LinkItem("Title", "https://example.com/video")

    monkeypatch.setattr("f1_race_monitor.core.platform.system", lambda: "Linux")
    monkeypatch.setattr("f1_race_monitor.core.shutil.which", lambda command: "/usr/bin/notify-send")
    monkeypatch.setattr("f1_race_monitor.core.subprocess.run", lambda args, check: calls.append(args))

    notify_desktop(item)

    assert calls == [["notify-send", "New video match", "Title\nhttps://example.com/video"]]


def test_notify_browser(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    calls = []
    item = LinkItem("Title", "https://example.com/video")

    monkeypatch.setattr(
        "f1_race_monitor.core.webbrowser.open",
        lambda url, new: calls.append((url, new)) or True,
    )

    notify_browser(item)

    assert calls == [(item.url, 2)]


def test_notify_webhook(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    requests = []
    item = LinkItem("Title", "https://example.com/video")

    class FakeResponse:
        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"ok"

    def fake_urlopen(request, timeout):  # type: ignore[no-untyped-def]
        requests.append((request.full_url, request.data, timeout))
        return FakeResponse()

    monkeypatch.setattr("f1_race_monitor.core.urllib.request.urlopen", fake_urlopen)

    notify_webhook(item, "https://example.com/hook")

    assert requests[0][0] == "https://example.com/hook"
    assert b'"title": "Title"' in requests[0][1]


def test_fetch_html_success(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    class Headers:
        def get_content_charset(self) -> str:
            return "utf-8"

    class FakeResponse:
        headers = Headers()

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return b"ok"

    monkeypatch.setattr(
        "f1_race_monitor.core.urllib.request.urlopen",
        lambda request, timeout: FakeResponse(),
    )

    assert fetch_html("https://example.com", "agent") == "ok"


def test_fetch_html_http_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def raise_http_error(request, timeout):  # type: ignore[no-untyped-def]
        raise HTTPError(request.full_url, 500, "server error", hdrs=None, fp=None)

    monkeypatch.setattr("f1_race_monitor.core.urllib.request.urlopen", raise_http_error)

    with pytest.raises(RuntimeError, match="HTTP 500"):
        fetch_html("https://example.com", "agent")


def test_fetch_html_url_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    def raise_url_error(request, timeout):  # type: ignore[no-untyped-def]
        raise URLError("offline")

    monkeypatch.setattr("f1_race_monitor.core.urllib.request.urlopen", raise_url_error)

    with pytest.raises(RuntimeError, match="Could not fetch"):
        fetch_html("https://example.com", "agent")
