# Development

The project uses:

- `uv` for environment and command execution.
- `pytest` and `pytest-cov` for tests and coverage.
- `ruff` for linting.
- `mkdocs` and `mkdocstrings` for docs.
- `hatchling` through `pyproject.toml` for package builds.

## Setup

```bash
uv sync --extra dev
```

## Test And Coverage

```bash
just test
```

The coverage threshold is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = "--cov=f1_race_monitor --cov-report=term-missing --cov-report=xml --cov-fail-under=100"
```

## Lint

```bash
just lint
just ruff
```

`just lint` checks Python syntax. `just ruff` runs style and quality checks.

## Build

```bash
just build
just check-dist
```

Build artifacts are written to `dist/`.

Clean generated artifacts:

```bash
just clean
```

`just clean` removes caches, coverage output, package build artifacts, and the generated docs site. It does not remove `.venv`, `uv.lock`, config files, or `.crawler_state.json`.

## Documentation

```bash
just docs
just docs-serve
just docs-open
```

The generated static site is written to `site/`.

## CI

GitHub Actions are configured in:

- `.github/workflows/ci.yml`
- `.github/workflows/publish.yml`

CI runs linting, tests with coverage, package build checks, and docs build checks.
