# Publishing to PyPI

The package is published as **[pypiggyback](https://pypi.org/project/pypiggyback/)** on PyPI.

## Automated publishing

Releases are published via GitHub Actions (`.github/workflows/workflow.yml`).

### Triggers

| Event | When it runs |
|-------|----------------|
| GitHub Release published | Create a release on GitHub |
| Tag push `v*` | e.g. `git tag v0.1.1 && git push origin v0.1.1` |
| Manual | Actions → Publish to PyPI → Run workflow |

## Authentication (choose one)

### Option A — API token (recommended if OIDC fails)

1. On [pypi.org](https://pypi.org), go to **Account settings → API tokens**
2. Create a token scoped to the **pypiggyback** project (or whole account for first upload)
3. On GitHub: **Settings → Secrets and variables → Actions** → add `PYPI_API_TOKEN`

When this secret is set, the workflow uses token auth and skips trusted publishing.

### Option B — Trusted publishing (OIDC, no secrets)

1. Go to [pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
2. Add a **pending publisher** (or edit the existing one) with these **exact** values:

| Field | Value |
|-------|-------|
| PyPI Project Name | `pypiggyback` |
| Owner | `kurtisrogers` |
| Repository name | `piggyback` |
| Workflow name | `workflow.yml` |
| Environment name | *(leave blank)* |

!!! warning "Repository name is case-sensitive"
    GitHub sends `kurtisrogers/piggyback` (all lowercase). If PyPI shows `Piggyback` with a capital **P**, trusted publishing will fail with `invalid-publisher`. Remove the pending publisher and re-add it with lowercase `piggyback`.

## Troubleshooting `invalid-publisher`

If publish fails with *"valid token, but no corresponding publisher"*, compare your PyPI config to the GitHub OIDC claims:

```
repository: kurtisrogers/piggyback
workflow: workflow.yml
environment: (none)
```

**Fastest fix:** add `PYPI_API_TOKEN` in GitHub repo secrets and re-run.

**OIDC fix:** edit the pending publisher on PyPI so the repository is `piggyback` (not `Piggyback`).

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
