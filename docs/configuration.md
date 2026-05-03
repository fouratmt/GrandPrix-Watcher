# Configuration

All runtime configuration lives in `config.toml`.

```toml
[watch]
url = "https://fullraces.com/2026"
grand_prix = "miami"
match_all = []
match_any = []
event = "race"
regex = ""
notify_existing = false
include_seen = false
state_file = ".crawler_state.json"
max_pages = 3
interval_seconds = 900

[notify]
methods = ["macos", "browser"]
webhook_url = ""
```

## `[watch]`

### `url`

The listing page to monitor.

```toml
url = "https://fullraces.com/2026"
```

### `grand_prix`

Grand Prix shorthand. The app maps common country, city, and venue names to race titles.

```toml
grand_prix = "japan"
```

Examples:

| Input | Matches |
| --- | --- |
| `japan`, `suzuka` | Japanese Grand Prix |
| `china`, `shanghai` | Chinese Grand Prix |
| `uk`, `silverstone` | British Grand Prix |
| `sao-paulo`, `brazil` | Sao Paulo Grand Prix |
| `mexico`, `mexico-city` | Mexico City Grand Prix |
| `abu-dhabi`, `yas-marina` | Abu Dhabi Grand Prix |

The matcher normalizes accents and punctuation, so `sao-paulo` can match titles containing `Sao Paulo` or `São Paulo`.

### `event`

Event shorthand. Prefer this over manually writing `regex`.

```toml
event = "race"
```

Supported values:

- `race`
- `sprint`
- `qualifying`
- `practice`
- `sprint-qualifying`
- `paddock`
- `press`

`sprint` matches only the sprint race. Use `sprint-qualifying` for Sprint Qualifying.

### `match_all`

Additional terms that must all appear in the title or URL.

```toml
match_all = ["f1 2026"]
```

### `match_any`

At least one of these terms must appear in the title or URL.

```toml
match_any = ["sky", "f1tv"]
```

### `regex`

Advanced override for event/title matching.

```toml
regex = "^RACE\\s*-"
```

Leave this empty when using `event`.

### `notify_existing`

Controls first-run behavior when `state_file` does not exist.

```toml
notify_existing = false
```

When `false`, current matches are saved as seen and no notification is sent.

When `true`, current matches notify immediately.

### `include_seen`

Notify or open matches even if their URLs are already in `state_file`.

```toml
include_seen = false
```

Keep this false for normal monitoring.

### `state_file`

JSON file used to remember matched URLs.

```toml
state_file = ".crawler_state.json"
```

Delete this file to reset seen state.

### `max_pages`

Maximum number of listing pages to crawl through pagination links.

```toml
max_pages = 3
```

Older races may move off page 1. Increasing this helps find older posts.

### `interval_seconds`

Polling interval for `--watch`.

```toml
interval_seconds = 900
```

## `[notify]`

### `methods`

Notification methods to run for each new match.

```toml
methods = ["macos", "browser"]
```

Supported values:

- `console`: print to terminal.
- `macos`: use Apple Notification Center via AppleScript.
- `desktop`: macOS notification on macOS, `notify-send` on Linux.
- `browser`: open the URL in the default browser.
- `webhook`: POST JSON to `webhook_url`.

### `webhook_url`

Webhook target used by `webhook`.

```toml
webhook_url = "https://example.com/hook"
```

Payload:

```json
{
  "title": "RACE - F1 2026 - Miami Grand Prix - Full Race Replay - May 3, 2026 - Formula 1",
  "url": "https://fullraces.com/race-f1-2026-miami-grand-prix-full-race-replay-may-3-2026-formula-1"
}
```
