from __future__ import annotations

from pathlib import Path

import pytest

from f1_race_monitor import WatchConfig, normalize_grand_prix


@pytest.fixture
def watch_config(tmp_path: Path) -> WatchConfig:
    return WatchConfig(
        url="https://fullraces.com/2026",
        match_all=[],
        match_any=[],
        grand_prix_terms=[],
        regex="",
        state_file=tmp_path / "state.json",
        notify_existing=False,
        include_seen=False,
        max_pages=3,
        interval_seconds=900,
        user_agent="test-agent",
    )


def config_for_grand_prix(tmp_path: Path, grand_prix: str, regex: str = "") -> WatchConfig:
    return WatchConfig(
        url="https://fullraces.com/2026",
        match_all=[],
        match_any=[],
        grand_prix_terms=normalize_grand_prix(grand_prix),
        regex=regex,
        state_file=tmp_path / "state.json",
        notify_existing=False,
        include_seen=False,
        max_pages=3,
        interval_seconds=900,
        user_agent="test-agent",
    )
