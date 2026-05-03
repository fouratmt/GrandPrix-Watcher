# Usage

## Install Or Sync

For local development:

```bash
uv sync --extra dev
```

After publishing to PyPI:

```bash
uv tool install f1-race-monitor
```

## One-Shot Checks

Run the configured check:

```bash
just check
```

Run a specific event and Grand Prix:

```bash
just for race miami
just for sprint monaco
just for sprint-qualifying miami
```

The same calls through the CLI:

```bash
uv run f1-monitor --config config.toml --grand-prix miami --event race
uv run f1-monitor --config config.toml --grand-prix monaco --event sprint
```

## Watch Mode

Keep polling:

```bash
just watch
just watch-for race abu-dhabi
```

Watch mode does not stop when a match is found. It notifies, records the URL in state, then keeps polling.

## Force Already-Seen Matches

The app records matched URLs in `.crawler_state.json`. Use force mode when you deliberately want to notify or open the same URL again:

```bash
just force
just force-for race china
```

Equivalent CLI:

```bash
uv run f1-monitor --config config.toml --include-seen
```

Avoid `include_seen = true` in long-running watch mode when `browser` is enabled, because the same link will open repeatedly.

## Notifications

The default local config uses:

```toml
[notify]
methods = ["macos", "browser"]
```

Common combinations:

```bash
uv run f1-monitor --config config.toml --notify console
uv run f1-monitor --config config.toml --notify macos --notify browser
uv run f1-monitor --config config.toml --notify webhook --webhook-url https://example.com/hook
```

## Docs Commands

Build docs:

```bash
just docs
```

Serve docs locally:

```bash
just docs-serve
```

Build and open the generated static docs:

```bash
just docs-open
```
