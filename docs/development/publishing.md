# Publishing to PyPI

The package is published as **[pypiggybackm](https://pypi.org/project/pypiggybackm/)** on PyPI.

## Automated publishing

Releases are published via GitHub Actions (`.github/workflows/publish.yml`) using [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC — no API tokens in secrets).

### Triggers

| Event | When it runs |
|-------|----------------|
| GitHub Release published | Create a release on GitHub |
| Tag push `v*` | e.g. `git tag v0.1.1 && git push origin v0.1.1` |
| Manual | Actions → Publish to PyPI → Run workflow |

### One-time PyPI setup

1. On [pypi.org](https://pypi.org), open the **pypiggybackm** project → **Publishing** → **Add a new publisher**
2. Configure the trusted publisher:
   - **PyPI Project Name:** `pypiggybackm`
   - **Owner:** `kurtisrogers`
   - **Repository name:** `piggyback`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi` (optional but recommended)
3. On GitHub, create an environment named `pypi` under **Settings → Environments** (can add approval rules if desired)

### Release checklist

1. Bump `version` in `pyproject.toml`
2. Commit and merge to `main`
3. Create a GitHub Release (or push a `v*` tag)
4. Workflow builds sdist + wheel and publishes to PyPI

### Local build (verify before release)

```bash
pip install build
python -m build
twine check dist/*
```

Install locally:

```bash
pip install dist/pypiggybackm-*.whl
```
