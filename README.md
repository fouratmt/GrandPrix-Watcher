# GrandPrix Watcher

GrandPrix Watcher is a small Python CLI that watches a public replay/blog listing page, finds matching Formula 1 posts, notifies you, and can open the matched link in your browser.

It monitors links only. It does not download videos or bypass site controls.

## Use From Source

These steps assume a fresh machine.

### 1. Install The Command Line Tools

On macOS, install the Apple command line tools first if `git` is missing:

```bash
xcode-select --install
```

Install these tools:

- `git`: clones the source code.
- `uv`: installs Python if needed and manages the project environment.
- `just`: runs the project commands without memorizing long CLI flags.

With Homebrew:

```bash
brew install git uv just
```

If Homebrew itself is missing, install it from [brew.sh](https://brew.sh/), then run the command above.

Check that the tools are available:

```bash
git --version
uv --version
just --version
```

### 2. Get The Source Code

```bash
git clone https://github.com/fouratmt/GrandPrix-Watcher.git
cd grandprix-watcher
```

If you already have the repository, just `cd` into it.

### 3. Install The Project Environment

```bash
just sync
```

That creates or updates the `uv` environment. You do not need to create a virtualenv manually.

If `just` is not installed yet, the equivalent command is:

```bash
uv sync --extra dev
```

### 4. Create Your Config

```bash
cp config.example.toml config.toml
```

Open `config.toml` and set what you want to watch:

```toml
[watch]
url = "https://fullraces.com/2026"
grand_prix = "miami"
event = "race"
max_pages = 3
interval_seconds = 900

[notify]
methods = ["macos", "browser"]
```

This example looks for the Miami Grand Prix race, sends a native macOS notification, and opens the matched link in your default browser.

### 5. Run It Once

```bash
just check
```

Important first-run behavior: by default, existing matches are marked as seen and do not notify. This avoids opening old posts the first time you run the app.

To notify/open matching links even if they were already seen:

```bash
just force
```

### 6. Keep Watching

```bash
just watch
```

In watch mode, the app keeps running. It does not stop after a match. It notifies, opens the link if configured, records the URL as seen, then checks again after `interval_seconds`.

## Commands Users Actually Need

| Task | Command |
| --- | --- |
| Install/update the local environment | `just sync` |
| Run one check from `config.toml` | `just check` |
| Keep watching from `config.toml` | `just watch` |
| Force already-seen matches to notify/open again | `just force` |
| Run one race/event directly | `just for race miami` |
| Watch one race/event directly | `just watch-for race miami` |
| Force one race/event even if already seen | `just force-for race miami` |
| Test Apple Notification Center | `just notify-test` |
| Show every available command | `just` |

Examples:

```bash
just for race miami
just for sprint monaco
just for race japan
just watch-for race abu-dhabi
just force-for race china
```

For multi-word Grand Prix names, use dashes:

```bash
just for race mexico-city
just watch-for sprint sao-paulo
```

## Events And Grand Prix Names

Supported event values:

- `race`
- `sprint`
- `qualifying`
- `practice`
- `sprint-qualifying`
- `paddock`
- `press`

`sprint` matches the sprint race only. Use `sprint-qualifying` for Sprint Qualifying.

Grand Prix matching accepts country, city, venue, and adjective shorthands. For example:

| Input | Matches |
| --- | --- |
| `japan`, `japanese`, `suzuka` | Japanese Grand Prix |
| `china`, `chinese`, `shanghai` | Chinese Grand Prix |
| `uk`, `britain`, `silverstone` | British Grand Prix |
| `usa`, `austin`, `cota` | United States Grand Prix |
| `mexico`, `mexico-city` | Mexico City Grand Prix |
| `brazil`, `sao-paulo`, `interlagos` | Sao Paulo Grand Prix |
| `abu-dhabi`, `uae`, `yas-marina` | Abu Dhabi Grand Prix |

The full list is documented in [docs/configuration.md](docs/configuration.md).

## Seen State

GrandPrix Watcher stores matched URLs in `.crawler_state.json` by default.

That file prevents the same post from notifying and opening again on every run.

Use this when you deliberately want to revisit matches:

```bash
just force
just force-for race miami
```

Or set this in `config.toml`:

```toml
include_seen = true
```

Be careful with `include_seen = true` in watch mode. If `browser` notifications are enabled, the same link can open on every polling interval.

To fully reset the seen state, delete `.crawler_state.json`.

## Config Reference

Runtime config lives in `config.toml`.

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

| Config | Meaning |
| --- | --- |
| `watch.url` | Listing page to monitor. |
| `watch.grand_prix` | Race shorthand, such as `miami`, `japan`, `china`, `sao-paulo`, or `abu-dhabi`. |
| `watch.event` | Event shorthand, such as `race`, `sprint`, or `qualifying`. |
| `watch.match_all` | Extra terms that must all appear in the title or URL. |
| `watch.match_any` | Optional terms where at least one must appear. |
| `watch.regex` | Advanced regex filter. Usually leave empty and use `event`. |
| `watch.notify_existing` | Notify matches found on the first run instead of marking them seen silently. |
| `watch.include_seen` | Notify/open matches even if they are already in the state file. |
| `watch.state_file` | JSON file that stores seen URLs. |
| `watch.max_pages` | Number of paginated listing pages to crawl. Increase this for older posts. |
| `watch.interval_seconds` | Delay between checks in `just watch` / `--watch` mode. |
| `notify.methods` | Notification methods: `console`, `macos`, `desktop`, `browser`, `webhook`. |
| `notify.webhook_url` | URL used when `webhook` is enabled. |

Full config documentation is in [docs/configuration.md](docs/configuration.md).

## Running Without Just

The `just` commands are wrappers around the Python CLI. These are equivalent:

```bash
uv run grandprix-watcher --config config.toml
uv run grandprix-watcher --config config.toml --watch
uv run grandprix-watcher --config config.toml --include-seen
uv run grandprix-watcher --config config.toml --grand-prix miami --event race
uv run grandprix-watcher --config config.toml --grand-prix miami --event race --watch
```

## Maintainer Commands

These are mostly for development, CI, docs, and packaging:

| Task | Command |
| --- | --- |
| Syntax check | `just lint` |
| Ruff linting | `just ruff` |
| Tests with enforced 100% coverage | `just test` |
| Build MkDocs site | `just docs` |
| Serve docs locally | `just docs-serve` |
| Build and open docs | `just docs-open` |
| Build wheel and source distribution | `just build` |
| Validate package metadata | `just check-dist` |
| Remove generated caches/build/docs output | `just clean` |

Package artifacts are written to `dist/`.

## Documentation

Build the docs:

```bash
just docs
```

Open the docs site:

```bash
just docs-open
```

The MkDocs source files live in `docs/`, and API docs are generated from the `grandprix_watcher` package.
