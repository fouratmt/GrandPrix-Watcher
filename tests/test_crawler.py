from __future__ import annotations

from pathlib import Path

from f1_race_monitor import (
    AppConfig,
    LinkItem,
    NotifyConfig,
    WatchConfig,
    check_once,
    crawl_links,
    extract_links,
)
from f1_race_monitor.core import is_pagination_link, load_seen, save_seen


def test_extract_links_deduplicates_and_resolves_urls() -> None:
    html = """
    <a href="/race">RACE - F1 2026 - Miami Grand Prix</a>
    <a href="/race">RACE - F1 2026 - Miami Grand Prix</a>
    <a href="">Empty</a>
    """

    links = extract_links(html, "https://fullraces.com/2026")

    assert links == [
        LinkItem(
            title="RACE - F1 2026 - Miami Grand Prix",
            url="https://fullraces.com/race",
        )
    ]


def test_is_pagination_link() -> None:
    assert is_pagination_link(LinkItem("2", "https://fullraces.com/2026/2"), "https://fullraces.com/2026")
    assert is_pagination_link(LinkItem("»", "https://fullraces.com/2026/2"), "https://fullraces.com/2026")
    assert not is_pagination_link(LinkItem("Watch", "https://fullraces.com/race"), "https://fullraces.com/2026")
    assert not is_pagination_link(LinkItem("2", "https://example.com/2026/2"), "https://fullraces.com/2026")


def test_crawl_links_follows_pagination(monkeypatch, watch_config: WatchConfig) -> None:  # type: ignore[no-untyped-def]
    pages = {
        "https://fullraces.com/2026": """
            <a href="/race-miami">RACE - F1 2026 - Miami Grand Prix</a>
            <a href="/2026/2">2</a>
        """,
        "https://fullraces.com/2026/2": """
            <a href="/race-china">RACE - F1 2026 - Chinese Grand Prix</a>
        """,
    }

    def fake_fetch(url: str, user_agent: str) -> str:
        return pages[url]

    monkeypatch.setattr("f1_race_monitor.core.fetch_html", fake_fetch)

    links = crawl_links(watch_config)

    assert [link.title for link in links] == [
        "RACE - F1 2026 - Miami Grand Prix",
        "2",
        "RACE - F1 2026 - Chinese Grand Prix",
    ]


def test_crawl_links_respects_max_pages(monkeypatch, watch_config: WatchConfig) -> None:  # type: ignore[no-untyped-def]
    watch_config.max_pages = 1
    pages = {
        "https://fullraces.com/2026": """
            <a href="/race-miami">RACE - F1 2026 - Miami Grand Prix</a>
            <a href="/2026/2">2</a>
        """,
        "https://fullraces.com/2026/2": """
            <a href="/race-china">RACE - F1 2026 - Chinese Grand Prix</a>
        """,
    }

    monkeypatch.setattr("f1_race_monitor.core.fetch_html", lambda url, user_agent: pages[url])

    assert [link.title for link in crawl_links(watch_config)] == ["RACE - F1 2026 - Miami Grand Prix", "2"]


def test_seen_state_round_trip(tmp_path: Path) -> None:
    state_file = tmp_path / "nested" / "state.json"

    assert load_seen(state_file) == set()
    save_seen(state_file, {"https://example.com/a"})

    assert load_seen(state_file) == {"https://example.com/a"}


def test_check_once_initializes_state_without_notifying(monkeypatch, watch_config: WatchConfig) -> None:  # type: ignore[no-untyped-def]
    item = LinkItem("RACE - F1 2026 - Miami Grand Prix", "https://example.com/miami")
    notified = []
    watch_config.grand_prix_terms = ["miami grand prix"]
    app_config = AppConfig(watch=watch_config, notify=NotifyConfig(methods=["console"], webhook_url=""))

    monkeypatch.setattr("f1_race_monitor.core.crawl_links", lambda config: [item])
    monkeypatch.setattr("f1_race_monitor.core.notify", lambda item, config: notified.append(item))

    assert check_once(app_config) == 0
    assert notified == []
    assert load_seen(watch_config.state_file) == {item.url}


def test_check_once_notifies_new_matches(monkeypatch, watch_config: WatchConfig) -> None:  # type: ignore[no-untyped-def]
    item = LinkItem("RACE - F1 2026 - Miami Grand Prix", "https://example.com/miami")
    notified = []
    watch_config.notify_existing = True
    watch_config.grand_prix_terms = ["miami grand prix"]
    app_config = AppConfig(watch=watch_config, notify=NotifyConfig(methods=["console"], webhook_url=""))

    monkeypatch.setattr("f1_race_monitor.core.crawl_links", lambda config: [item])
    monkeypatch.setattr("f1_race_monitor.core.notify", lambda item, config: notified.append(item))

    assert check_once(app_config) == 1
    assert notified == [item]
    assert load_seen(watch_config.state_file) == {item.url}


def test_check_once_include_seen_notifies_existing(monkeypatch, watch_config: WatchConfig) -> None:  # type: ignore[no-untyped-def]
    item = LinkItem("RACE - F1 2026 - Miami Grand Prix", "https://example.com/miami")
    notified = []
    watch_config.include_seen = True
    watch_config.grand_prix_terms = ["miami grand prix"]
    save_seen(watch_config.state_file, {item.url})
    app_config = AppConfig(watch=watch_config, notify=NotifyConfig(methods=["console"], webhook_url=""))

    monkeypatch.setattr("f1_race_monitor.core.crawl_links", lambda config: [item])
    monkeypatch.setattr("f1_race_monitor.core.notify", lambda item, config: notified.append(item))

    assert check_once(app_config) == 1
    assert notified == [item]
