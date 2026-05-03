#!/usr/bin/env python3
"""Lightweight tests for the crawler matching helpers."""

from __future__ import annotations

from crawler import LinkItem, WatchConfig, event_regex, item_matches, normalize_grand_prix


def make_config(grand_prix: str, regex: str = "") -> WatchConfig:
    return WatchConfig(
        url="https://fullraces.com/2026",
        match_all=[],
        match_any=[],
        grand_prix_terms=normalize_grand_prix(grand_prix),
        regex=regex,
        state_file=None,  # type: ignore[arg-type]
        notify_existing=False,
        include_seen=False,
        max_pages=3,
        interval_seconds=900,
        user_agent="test",
    )


def assert_matches(grand_prix: str, title: str) -> None:
    item = LinkItem(title=title, url="https://example.com/video")
    assert item_matches(item, make_config(grand_prix)), f"{grand_prix!r} did not match {title!r}"


def assert_event_matches(event: str, title: str) -> None:
    item = LinkItem(title=title, url="https://example.com/video")
    config = make_config("miami", event_regex(event))
    assert item_matches(item, config), f"{event!r} did not match {title!r}"


def assert_event_does_not_match(event: str, title: str) -> None:
    item = LinkItem(title=title, url="https://example.com/video")
    config = make_config("miami", event_regex(event))
    assert not item_matches(item, config), f"{event!r} unexpectedly matched {title!r}"


def main() -> None:
    assert normalize_grand_prix("japan") == ["japanese grand prix"]
    assert normalize_grand_prix("sao-paulo") == ["sao paulo grand prix", "grande premio de sao paulo"]
    assert normalize_grand_prix("abu-dhabi") == ["abu dhabi grand prix"]

    assert_matches("japan", "RACE - F1 2026 - Japanese Grand Prix Full Race Replay")
    assert_matches("uk", "RACE - F1 2026 - British Grand Prix Full Race Replay")
    assert_matches("sao-paulo", "RACE - F1 2026 - São Paulo Grand Prix Full Race Replay")
    assert_matches("mexico", "RACE - F1 2026 - Mexico City Grand Prix Full Race Replay")
    assert_matches("abu-dhabi", "RACE - F1 2026 - Abu Dhabi Grand Prix Full Race Replay")
    assert_matches("barcelona", "RACE - F1 2026 - Barcelona-Catalunya Grand Prix Full Race Replay")

    assert_event_matches("sprint", "Sprint - F1 2026 - Miami Grand Prix - Full Race Replay")
    assert_event_does_not_match(
        "sprint",
        "Sprint Qualifying - F1 2026 - Miami Grand Prix - Full Race Replay",
    )
    assert_event_matches(
        "sprint-qualifying",
        "Sprint Qualifying - F1 2026 - Miami Grand Prix - Full Race Replay",
    )


if __name__ == "__main__":
    main()
