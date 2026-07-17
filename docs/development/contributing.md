# Contributing

Thank you for your interest in contributing to Piggyback!

## Development setup

```bash
git clone https://github.com/kurtisrogers/piggyback.git
cd piggyback
pip install -e ".[dev]"
pre-commit install
playwright install chromium
cd example
python manage.py migrate
python manage.py load_sample_data --fixture
```

## Fixtures

Sample catalog data ships as a Django fixture:

```bash
python manage.py load_sample_data --fixture
# equivalent to:
python manage.py loaddata sample_data
```

The programmatic loader remains available without `--fixture`.

## Running tests

### Unit tests

```bash
PYTHONPATH=src:example pytest tests/ --ignore=tests/bdd
```

### BDD / Playwright E2E

Gherkin features live in `tests/bdd/features/`:

```bash
playwright install chromium
DJANGO_ALLOW_ASYNC_UNSAFE=true PYTHONPATH=src:example pytest tests/bdd -v
```

Scenarios cover the home page, card catalog, authentication, and the system-user API.

### Everything

```bash
DJANGO_ALLOW_ASYNC_UNSAFE=true PYTHONPATH=src:example pytest
```

## Pre-commit

Hooks run ruff, formatting, and JSON/YAML checks:

```bash
pre-commit install        # once per clone
pre-commit run --all-files
```

A `pre-push` hook also runs fast unit tests.

## Code style

We use `ruff` for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Pull requests

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality (unit + BDD where relevant)
4. Ensure `pre-commit run --all-files` and `pytest` pass
5. Submit a pull request

## Reporting issues

Please use [GitHub Issues](https://github.com/kurtisrogers/piggyback/issues) to report bugs or request features.
