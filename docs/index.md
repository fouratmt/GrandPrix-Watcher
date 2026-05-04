# GrandPrix Watcher

`grandprix-watcher` watches Formula 1 replay listing pages and notifies you when matching videos appear.

It is built for a simple workflow:

1. Choose a listing page, such as `https://fullraces.com/2026`.
2. Choose a Grand Prix and event, such as `miami` and `race`.
3. Run a one-shot check or a polling watcher.
4. Receive a terminal, macOS, browser, desktop, or webhook notification.

The app monitors public links only. It does not download videos and does not bypass site controls.

## Quick Example

```bash
uv sync --extra dev
just for race miami
just watch-for sprint monaco
just force-for race china
```

The installed CLI is also available directly:

```bash
uv run grandprix-watcher --config config.toml --grand-prix japan --event race
```

## Main Concepts

- **Listing page**: the page that contains links to posts.
- **Grand Prix shorthand**: values like `japan`, `uk`, `sao-paulo`, and `abu-dhabi`.
- **Event shorthand**: values like `race`, `sprint`, and `sprint-qualifying`.
- **Seen state**: a JSON file that prevents repeated alerts for the same URL.
- **Notification methods**: `console`, `macos`, `desktop`, `browser`, and `webhook`.

## Documentation

- [Usage](usage.md): day-to-day commands.
- [Configuration](configuration.md): all `config.toml` options.
- [Development](development.md): tests, coverage, docs, and build commands.
- [Publishing](publishing.md): PyPI release process.
- [API Reference](api.md): public Python API and generated reference.
