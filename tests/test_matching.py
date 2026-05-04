from __future__ import annotations

from pathlib import Path

import pytest

from grandprix_watcher import LinkItem, event_regex, item_matches, normalize_grand_prix, normalize_search_text
from grandprix_watcher.core import GRAND_PRIX_ALIASES
from tests.conftest import config_for_grand_prix


@pytest.mark.parametrize("alias, terms", sorted(GRAND_PRIX_ALIASES.items()))
def test_all_grand_prix_aliases_match_expected_titles(tmp_path: Path, alias: str, terms: list[str]) -> None:
    config = config_for_grand_prix(tmp_path, alias)

    for term in terms:
        title = f"RACE - F1 2026 - {term.title()} Full Race Replay"
        assert item_matches(LinkItem(title=title, url="https://example.com/video"), config)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("japan", ["japanese grand prix"]),
        ("sao-paulo", ["sao paulo grand prix", "grande premio de sao paulo"]),
        ("abu-dhabi", ["abu dhabi grand prix"]),
        ("unknown-place", ["unknown place grand prix"]),
        ("custom grand prix", ["custom grand prix"]),
    ],
)
def test_normalize_grand_prix(value: str, expected: list[str]) -> None:
    assert normalize_grand_prix(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("São Paulo", "sao paulo"),
        ("abu-dhabi", "abu dhabi"),
        (" Grand   Prix ", "grand prix"),
    ],
)
def test_normalize_search_text(value: str, expected: str) -> None:
    assert normalize_search_text(value) == expected


@pytest.mark.parametrize(
    ("event", "title"),
    [
        ("race", "RACE - F1 2026 - Miami Grand Prix"),
        ("sprint", "Sprint - F1 2026 - Miami Grand Prix"),
        ("qualifying", "Qualifying - F1 2026 - Miami Grand Prix"),
        ("practice", "Practice - F1 2026 - Miami Grand Prix"),
        ("practice", "3rd Practice - F1 2026 - Miami Grand Prix"),
        ("sprint-qualifying", "Sprint Qualifying - F1 2026 - Miami Grand Prix"),
        ("sq", "Sprint Qualifying - F1 2026 - Miami Grand Prix"),
        ("paddock", "Paddock Uncut - F1 2026 - Miami Grand Prix"),
        ("press", "Drivers Press Conference - F1 2026 - Miami Grand Prix"),
    ],
)
def test_event_regex_matches_expected_titles(tmp_path: Path, event: str, title: str) -> None:
    config = config_for_grand_prix(tmp_path, "miami", event_regex(event))
    assert item_matches(LinkItem(title=title, url="https://example.com/video"), config)


def test_sprint_does_not_match_sprint_qualifying(tmp_path: Path) -> None:
    config = config_for_grand_prix(tmp_path, "miami", event_regex("sprint"))
    item = LinkItem(
        title="Sprint Qualifying - F1 2026 - Miami Grand Prix - Full Race Replay",
        url="https://example.com/video",
    )
    assert not item_matches(item, config)


def test_unknown_event_exits() -> None:
    with pytest.raises(SystemExit, match="Unknown event"):
        event_regex("warmup")


def test_match_all_match_any_and_regex(tmp_path: Path) -> None:
    config = config_for_grand_prix(tmp_path, "miami", r"^RACE\s*-")
    config.match_all = ["full race replay"]
    config.match_any = ["sky", "f1tv"]

    matching = LinkItem(
        title="RACE - F1 2026 - Miami Grand Prix - Full Race Replay",
        url="https://example.com/video-f1tv",
    )
    missing_any = LinkItem(
        title="RACE - F1 2026 - Miami Grand Prix - Full Race Replay",
        url="https://example.com/video",
    )
    wrong_event = LinkItem(
        title="Qualifying - F1 2026 - Miami Grand Prix - Full Race Replay",
        url="https://example.com/video-f1tv",
    )

    assert item_matches(matching, config)
    assert not item_matches(missing_any, config)
    assert not item_matches(wrong_event, config)


def test_match_all_missing_returns_false(tmp_path: Path) -> None:
    config = config_for_grand_prix(tmp_path, "miami")
    config.match_all = ["not present"]

    item = LinkItem("RACE - F1 2026 - Miami Grand Prix", "https://example.com/video")

    assert not item_matches(item, config)


def test_grand_prix_missing_returns_false(tmp_path: Path) -> None:
    config = config_for_grand_prix(tmp_path, "miami")

    item = LinkItem("RACE - F1 2026 - Monaco Grand Prix", "https://example.com/video")

    assert not item_matches(item, config)
