# Publishing

The package is prepared for PyPI publishing.

## Pre-Release Checklist

1. Update the version in `pyproject.toml`.
2. Confirm package metadata:
   - `authors`
   - `project.urls`
   - license
   - classifiers
3. Run checks:

```bash
just ruff
just test
just docs
just build
just check-dist
```

## Manual Publish

```bash
uv run --extra dev twine upload dist/*
```

## GitHub Release Publish

The publish workflow uses PyPI trusted publishing:

```yaml
uses: pypa/gh-action-pypi-publish@release/v1
```

Release flow:

1. Configure the PyPI project for trusted publishing.
2. Create a GitHub Release.
3. The `publish.yml` workflow builds and publishes the package.

## Install After Publishing

```bash
uv tool install grandprix-watcher
grandprix-watcher --help
```
