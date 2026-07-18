# Publishing to PyPI

The package is published as **[pypiggyback](https://pypi.org/project/pypiggyback/)** on PyPI.

## Automated publishing

Releases are published via GitHub Actions (`.github/workflows/publish.yml`).

### Triggers

| Event | When it runs |
|-------|----------------|
| GitHub Release published | Create a release on GitHub |
| Tag push `v*` | e.g. `git tag v0.1.1 && git push origin v0.1.1` |
| Manual | Actions → Publish to PyPI → Run workflow |

## Authentication (choose one)

### Option A — API token (simplest)

1. On [pypi.org](https://pypi.org), go to **Account settings → API tokens**
2. Create a token scoped to the **pypiggyback** project (or whole account for first upload)
3. On GitHub: **Settings → Secrets and variables → Actions** → add `PYPI_API_TOKEN`

The workflow uses this token when the secret is set.

### Option B — Trusted publishing (OIDC, no secrets)

1. On [pypi.org](https://pypi.org), open **pypiggyback** → **Publishing** → **Add a new trusted publisher**
2. Configure **exactly**:

| Field | Value |
|-------|-------|
| PyPI Project Name | `pypiggyback` |
| Owner | `kurtisrogers` |
| Repository name | `piggyback` |
| Workflow name | `publish.yml` |
| Environment name | *(leave blank)* |

3. Do **not** create a GitHub `pypi` environment unless you also set the same name on PyPI

If `PYPI_API_TOKEN` is **not** set, the workflow falls back to trusted publishing.

### Troubleshooting `invalid-publisher`

If publish fails with *"valid token, but no corresponding publisher"*, the PyPI trusted publisher does not match the workflow. Common causes:

- Trusted publisher not added on the **pypiggyback** project
- **Environment name** set on PyPI but not in the workflow (or vice versa) — leave blank on both sides
- Wrong workflow filename — must be `publish.yml`, not `Publish to PyPI`
- Publisher added to a different PyPI project (e.g. old name)

Claims from a failed run (for debugging):

```
repository: kurtisrogers/piggyback
workflow: publish.yml
```

Either fix the trusted publisher to match, or add `PYPI_API_TOKEN` and re-run.

## Release checklist

1. Bump `version` in `pyproject.toml`
2. Commit and merge to `main`
3. Create a GitHub Release (or push a `v*` tag)
4. Workflow builds sdist + wheel and publishes to PyPI

## Local build (verify before release)

```bash
pip install build twine
python -m build
twine check dist/*
```

Install locally:

```bash
pip install dist/pypiggyback-*.whl
```
