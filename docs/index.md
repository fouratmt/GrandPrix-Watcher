# F1 Race Monitor

`f1-race-monitor` monitors Formula 1 replay listing pages and sends notifications when matching links appear.

## Install

```bash
pip install f1-race-monitor
```

## Run

```bash
f1-monitor --config config.toml
f1-monitor --config config.toml --watch
f1-monitor --config config.toml --grand-prix japan --event race
```

## Build Docs

```bash
uv sync --extra dev
uv run mkdocs build --strict
```
