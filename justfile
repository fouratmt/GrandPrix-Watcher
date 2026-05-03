set shell := ["zsh", "-cu"]

config := "config.toml"

default:
    @just --list

# Create/update the uv environment with dev dependencies.
sync:
    uv sync --extra dev

# Validate Python syntax.
lint:
    uv run python -B -m py_compile crawler.py src/f1_race_monitor/*.py tests/*.py

# Run the pytest suite with coverage.
test:
    uv run --extra dev pytest

# Run Ruff linting.
ruff:
    uv run --extra dev ruff check .

# Build docs.
docs:
    uv run --extra dev mkdocs build --strict

# Serve docs locally.
docs-serve:
    uv run --extra dev mkdocs serve

# Build docs and open the generated site in the default browser.
docs-open:
    uv run --extra dev mkdocs build --strict
    open site/index.html

# Build wheel and source distribution.
build:
    uv build

# Check built package metadata.
check-dist:
    uv run --extra dev twine check dist/*

# Run one normal check using config.toml.
check config=config:
    uv run f1-monitor --config {{config}}

# Keep polling using config.toml.
watch config=config:
    uv run f1-monitor --config {{config}} --watch

# Run one check and notify/open matches even if they were already seen.
force config=config:
    uv run f1-monitor --config {{config}} --include-seen

# Run one check for an event and Grand Prix location.
for event place config=config:
    uv run f1-monitor --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}}

# Keep polling for an event and Grand Prix location.
watch-for event place config=config:
    uv run f1-monitor --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}} --watch

# Run one event/location check and notify/open even if the match was already seen.
force-for event place config=config:
    uv run f1-monitor --config {{quote(config)}} --grand-prix {{quote(place)}} --event {{quote(event)}} --include-seen

# Send a local Apple Notification Center test notification.
notify-test:
    osascript -e 'display notification "Crawler notification test" with title "New video match" subtitle "Apple Notification Center"'
