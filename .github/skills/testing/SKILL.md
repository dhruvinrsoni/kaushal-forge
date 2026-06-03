---
name: testing
description: >
  pytest + mypy + ruff testing patterns for Python CLI tools — fixtures,
  parametrize, mocking, type checking, and linting conventions.
metadata:
  version: "1.0.0"
  reasoning_mode: tdd
---

# Testing Python Tools

## Test Structure

```
tests/
  conftest.py         ← Shared fixtures
  test_cli.py         ← CLI entry point tests
  test_core.py        ← Core logic tests
  test_utils.py       ← Utility function tests
```

## Fixtures (`conftest.py`)

```python
import pytest
from pathlib import Path

@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Provides a temporary config directory."""
    config = tmp_path / "config.yaml"
    config.write_text("key: value\n")
    return config

@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear env vars that might affect tests."""
    monkeypatch.delenv("API_KEY", raising=False)
```

## Parametrize Pattern

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("", ""),
    ("123", "123"),
])
def test_transform(input: str, expected: str) -> None:
    assert transform(input) == expected
```

## Mocking

```python
from unittest.mock import patch, MagicMock

def test_api_call() -> None:
    with patch("mypackage.client.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"data": []})
        result = fetch_data("endpoint")
    assert result == []
    mock_get.assert_called_once()
```

## CLI Testing with `subprocess` or `typer`

```python
from subprocess import run, PIPE

def test_cli_help() -> None:
    result = run(["python", "-m", "mypkg.cli", "--help"], stdout=PIPE, stderr=PIPE)
    assert result.returncode == 0
    assert b"Usage" in result.stdout
```

## mypy Tips

- `strict = true` in `pyproject.toml` — enables all strict checks
- Use `# type: ignore[<code>]` (with code) for unavoidable suppressions
- `from __future__ import annotations` for forward references
- `cast()` from `typing` for cases mypy can't infer

## ruff Rules in Use

| Category | Meaning |
|----------|---------|
| `E/F` | pyflakes + pycodestyle (errors + style) |
| `I` | isort (import order) |
| `N` | naming conventions |
| `UP` | pyupgrade (modern Python idioms) |
| `B` | bugbear (common bugs) |
| `SIM` | simplify (redundant code) |

## Commands

| Command | When |
|---------|------|
| `make test` | After every change |
| `make test-cov` | Before committing — verify coverage ≥70% |
| `make lint` | Before committing |
| `make typecheck` | Before committing |
| `make all` | Full pre-commit validation |

## Coverage

Coverage configured in `pyproject.toml`:
```toml
[tool.coverage.report]
fail_under = 70
show_missing = true
```

Run `make test-cov` → opens `htmlcov/index.html` for detailed line-by-line coverage.
