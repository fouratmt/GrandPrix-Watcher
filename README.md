# F1 Race Monitor

A runtime dependency-free Python package and CLI that checks a blog/category page for new matching links, then notifies you and can open the matched link in your default browser.

It only monitors public page links and sends notifications. It does not download videos or bypass site controls.

## Quick Start

Edit `config.toml`:

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

Create/update the development environment:

```bash
uv sync --extra dev
```

Run one check:

```bash
just check
```

Keep watching:

```bash
just watch
```

## Just Commands

List commands:

```bash
just
```

Available targets:

- `just sync`: create or update the uv environment with development dependencies.
- `just lint`: validate Python syntax.
- `just test`: run the pytest suite with 100% coverage enforcement.
- `just ruff`: run Ruff linting.
- `just build`: build wheel and source distribution.
- `just docs`: build docs.
- `just docs-serve`: serve docs locally.
- `just docs-open`: build docs and open the generated site.
- `just check-dist`: validate built package metadata.
- `just check`: run one normal check using `config.toml`.
- `just watch`: keep polling using `config.toml`.
- `just force`: run one check and notify/open matches even if they were already seen.
- `just for race miami`: run one check for a specific event and Grand Prix.
- `just watch-for race miami`: keep polling for a specific event and Grand Prix.
- `just force-for race miami`: notify/open a specific event and Grand Prix even if already seen.
- `just notify-test`: send a local Apple Notification Center test notification.

Dynamic examples:

```bash
just for race miami
just for race japan
just for sprint monaco
just watch-for race abu-dhabi
just force-for race miami
```

Supported event names:

- `race`
- `sprint`
- `qualifying`
- `practice`
- `sprint-qualifying`
- `paddock`
- `press`

`sprint` matches the sprint race only. Use `sprint-qualifying` for Sprint Qualifying.

For multi-word locations, use dashes:

```bash
just watch-for race abu-dhabi
just watch-for sprint sao-paulo
```

Some Grand Prix names use adjectives or official city names. The app handles those aliases:

```bash
just for race japan
just watch-for race japan
just for race uk
just for race mexico-city
```

To use another config file, pass it as the last argument:

```bash
just check config.dev.toml
just watch-for race miami config.dev.toml
```

## Seen State

Matches are considered "seen" when their URL is stored in `state_file`, which defaults to `.crawler_state.json`.

This is intentional. Without state, the script would notify and open the same matching post every time it checks the page.

On the first normal run, if `.crawler_state.json` does not exist and `notify_existing = false`, the script saves all current matches as already seen and sends no notification. This prevents old posts from opening immediately when you first start monitoring.

To force visiting matches even after they were seen:

```bash
just force
just force-for race miami
```

Equivalent Python CLI:

```bash
uv run f1-monitor --config config.toml --include-seen
uv run f1-monitor --config config.toml --grand-prix miami --event race --include-seen
```

You can also make this permanent in `config.toml`:

```toml
include_seen = true
```

Be careful with `include_seen = true` in watch mode. If `browser` is enabled, the same link will open on every polling interval.

To completely reset what the script remembers, delete `.crawler_state.json`.

## Watch Behavior

Without `--watch`, the script runs exactly one check and exits whether or not it finds a match.

With `--watch`, the script does not stop when there is a match. It sends the configured notification, opens the link if `browser` is enabled, records the matched URL in the state file, then keeps polling.

## Config Reference

All config lives in `config.toml`.

### `[watch]`

`url`

The page to monitor.

```toml
url = "https://fullraces.com/2026"
```

`match_all`

A list of terms that must all appear in the link title or URL. Matching is case-insensitive.

```toml
match_all = []
```

`grand_prix`

Optional Grand Prix location shorthand. The script turns this into a required Grand Prix title match.

```toml
grand_prix = "miami"
```

For simple locations, `miami` becomes `miami grand prix`. For races with adjective names, city names, or venue shorthand, the app maps common inputs to the expected race title. Examples:

- `japan`, `japanese`, `suzuka` -> `Japanese Grand Prix`
- `australia`, `melbourne` -> `Australian Grand Prix`
- `china`, `shanghai` -> `Chinese Grand Prix`
- `saudi`, `jeddah` -> `Saudi Arabian Grand Prix`
- `canada`, `montreal` -> `Canadian Grand Prix`
- `uk`, `britain`, `silverstone` -> `British Grand Prix`
- `netherlands`, `zandvoort` -> `Dutch Grand Prix`
- `mexico`, `mexico-city` -> `Mexico City Grand Prix`
- `brazil`, `sao-paulo`, `interlagos` -> `São Paulo Grand Prix`
- `usa`, `austin`, `cota` -> `United States Grand Prix`
- `abu-dhabi`, `uae`, `yas-marina` -> `Abu Dhabi Grand Prix`

The 2026 calendar has two Spain rounds. Use `barcelona` or `barcelona-catalunya` for the Barcelona-Catalunya Grand Prix, and `spain`, `spanish`, or `madrid` for the Spanish Grand Prix.

The matcher is accent and punctuation tolerant, so `sao-paulo` can match `São Paulo`.

Supported 2026 Grand Prix shorthands:

| Race title matched | Shorthands |
| --- | --- |
| Australian Grand Prix | `australia`, `australian`, `melbourne`, `albert-park` |
| Chinese Grand Prix | `china`, `chinese`, `shanghai` |
| Japanese Grand Prix | `japan`, `japanese`, `suzuka` |
| Bahrain Grand Prix | `bahrain`, `sakhir` |
| Saudi Arabian Grand Prix | `saudi`, `saudi-arabia`, `saudi-arabian`, `arabia`, `jeddah` |
| Miami Grand Prix | `miami`, `florida` |
| Canadian Grand Prix | `canada`, `canadian`, `montreal` |
| Monaco Grand Prix | `monaco`, `monte-carlo` |
| Barcelona-Catalunya Grand Prix | `barcelona`, `barcelona-catalunya`, `catalunya`, `catalonia` |
| Spanish Grand Prix | `spain`, `spanish`, `madrid` |
| Austrian Grand Prix | `austria`, `austrian`, `spielberg` |
| British Grand Prix | `great-britain`, `britain`, `british`, `uk`, `united-kingdom`, `england`, `silverstone` |
| Belgian Grand Prix | `belgium`, `belgian`, `spa`, `spa-francorchamps` |
| Hungarian Grand Prix | `hungary`, `hungarian`, `budapest`, `hungaroring` |
| Dutch Grand Prix | `netherlands`, `dutch`, `holland`, `zandvoort` |
| Italian Grand Prix | `italy`, `italian`, `monza` |
| Azerbaijan Grand Prix | `azerbaijan`, `baku` |
| Singapore Grand Prix | `singapore` |
| United States Grand Prix | `usa`, `us`, `united-states`, `america`, `austin`, `cota`, `texas` |
| Mexico City Grand Prix | `mexico`, `mexican`, `mexico-city` |
| Sao Paulo Grand Prix | `brazil`, `brazilian`, `sao-paulo`, `interlagos` |
| Las Vegas Grand Prix | `las-vegas`, `vegas`, `nevada` |
| Qatar Grand Prix | `qatar`, `lusail`, `doha` |
| Abu Dhabi Grand Prix | `abu-dhabi`, `uae`, `yas-marina` |

Use `match_all` for extra required terms beyond the Grand Prix name.

`match_any`

A list of terms where at least one must appear in the link title or URL. Matching is case-insensitive.

```toml
match_any = ["race", "sprint"]
```

Leave it empty if you do not need an either/or condition:

```toml
match_any = []
```

`event`

Optional event shorthand. Prefer this over writing event regexes manually.

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

`sprint` only matches the sprint race. It does not match Sprint Qualifying.

`regex`

A lower-level regular expression override that must match the link title or URL. Usually prefer `event`.

```toml
regex = ""
```

For this site, many posts contain the phrase `Full Race Replay`, so `match_all = ["race"]` would also match practice and qualifying posts. Use `event = "race"` to match only the race post.

Leave it empty to disable regex matching:

```toml
regex = ""
```

`notify_existing`

Controls the first run when the state file does not exist yet.

```toml
notify_existing = false
```

When `false`, existing matching posts are saved as already seen and no notification is sent.

When `true`, existing matching posts trigger notifications immediately on the first run.

`include_seen`

Controls whether already-seen matches should notify/open again.

```toml
include_seen = false
```

Keep this `false` for normal monitoring. Set it to `true`, or use `--include-seen`, when you deliberately want to revisit a match.

`state_file`

The JSON file used to remember which matched URLs have already triggered notifications.

```toml
state_file = ".crawler_state.json"
```

`max_pages`

The maximum number of listing pages to crawl from `url`.

```toml
max_pages = 3
```

This matters for older races. For example, after newer Miami and Japan posts are published, China may no longer be on the first `/2026` listing page. With `max_pages = 3`, the script follows pagination links and can still find it.

`interval_seconds`

The delay between checks when running with `--watch`.

```toml
interval_seconds = 900
```

This example checks every 15 minutes. It has no effect for a single run without `--watch`.

`user_agent`

Optional. Overrides the HTTP user agent sent when fetching the page.

```toml
user_agent = "f1-script-crawler/1.0"
```

### `[notify]`

`methods`

The notification methods to use. You can set one method or multiple methods.

```toml
methods = ["macos", "browser"]
```

Supported values:

- `console`: print matches in the terminal.
- `macos`: send a native macOS Notification Center notification using AppleScript.
- `desktop`: use `macos` on macOS, or `notify-send` on Linux.
- `browser`: open the matched link in your default browser.
- `webhook`: send a JSON POST request to `webhook_url`.

Examples:

```toml
methods = ["console"]
methods = ["macos"]
methods = ["macos", "browser"]
methods = ["webhook"]
```

`webhook_url`

The URL used when `methods` includes `webhook`.

```toml
webhook_url = "https://example.com/hook"
```

The script sends JSON like this:

```json
{
  "title": "RACE - F1 2026 - Miami Grand Prix - Full Race Replay - May 3, 2026 - Formula 1",
  "url": "https://fullraces.com/race-f1-2026-miami-grand-prix-full-race-replay-may-3-2026-formula-1"
}
```

## Python CLI

The `just` commands are wrappers around the installed CLI run through `uv`.

Run once:

```bash
uv run f1-monitor --config config.toml
```

Watch:

```bash
uv run f1-monitor --config config.toml --watch
```

Force already-seen matches:

```bash
uv run f1-monitor --config config.toml --include-seen
```

Override event/location from the command line:

```bash
uv run f1-monitor --config config.toml --grand-prix monaco --event race
```

Use Grand Prix shorthand with aliases:

```bash
uv run f1-monitor --config config.toml --grand-prix japan --event race
```

Override notification methods:

```bash
uv run f1-monitor --config config.toml --notify macos --notify browser
```

## Packaging And Release

The project uses a standard `src/` layout and `pyproject.toml`.

Install/sync development dependencies:

```bash
uv sync --extra dev
```

Run checks:

```bash
just sync
just lint
just ruff
just test
```

`just test` enforces 100% coverage.

Build distributions:

```bash
just build
```

Check the build artifacts:

```bash
uv run --extra dev twine check dist/*
```

Install the built wheel locally:

```bash
uv pip install dist/f1_race_monitor-0.1.0-py3-none-any.whl
```

Run the installed CLI:

```bash
f1-monitor --config config.toml
```

Publish to PyPI manually:

```bash
uv run --extra dev twine upload dist/*
```

The repository also includes GitHub Actions:

- `.github/workflows/ci.yml`: lint, test with coverage, build package, check metadata, build docs.
- `.github/workflows/publish.yml`: publish to PyPI on GitHub Release using trusted publishing.

Before publishing, update these fields in `pyproject.toml` if needed:

- `version`
- `authors`
- `project.urls`
- license choice

## API Docs

Docs are ready to build with MkDocs and mkdocstrings.

Build docs locally:

```bash
just docs
```

Serve docs locally:

```bash
just docs-serve
```

Build and open docs:

```bash
just docs-open
```

API docs are configured in:

- `mkdocs.yml`
- `docs/index.md`
- `docs/usage.md`
- `docs/configuration.md`
- `docs/development.md`
- `docs/publishing.md`
- `docs/api.md`
