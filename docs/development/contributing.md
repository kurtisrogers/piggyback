# Contributing

Thank you for your interest in contributing to Piggyback!

## Development setup

```bash
git clone https://github.com/kurtisrogers/piggyback.git
cd piggyback
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py load_sample_data
```

## Running tests

```bash
pytest
```

## Code style

We use `ruff` for linting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Pull requests

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure `pytest` and `ruff check` pass
5. Submit a pull request

## Reporting issues

Please use [GitHub Issues](https://github.com/kurtisrogers/piggyback/issues) to report bugs or request features.
