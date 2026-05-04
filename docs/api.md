# API Reference

The package exposes a small API for embedding the monitor in another Python program or testing custom matching behavior.

## Common API

```python
from pathlib import Path

from grandprix_watcher import AppConfig, NotifyConfig, WatchConfig, check_once, normalize_grand_prix

watch = WatchConfig(
    url="https://fullraces.com/2026",
    match_all=[],
    match_any=[],
    grand_prix_terms=normalize_grand_prix("japan"),
    regex=r"^RACE\s*-",
    state_file=Path(".crawler_state.json"),
    notify_existing=False,
    include_seen=False,
    max_pages=3,
    interval_seconds=900,
    user_agent="my-monitor/1.0",
)

config = AppConfig(watch=watch, notify=NotifyConfig(methods=["console"], webhook_url=""))
check_once(config)
```

## Public Package API

::: grandprix_watcher
    options:
      members:
        - AppConfig
        - LinkItem
        - NotifyConfig
        - WatchConfig
        - build_config
        - check_once
        - crawl_links
        - event_regex
        - extract_links
        - item_matches
        - load_config
        - load_seen
        - normalize_grand_prix
        - normalize_search_text
        - normalize_text
        - notify
        - save_seen

## Core Module

::: grandprix_watcher.core
