# Branch protection for `main`

The cloud agent token cannot set branch protection rules on this repository (requires admin permissions). Apply these settings manually as a repo admin.

## Option 1: Script (recommended)

```bash
gh auth login   # as a repo admin
bash scripts/protect-main-branch.sh
```

## Option 2: GitHub UI

In **Settings → Branches → Branch protection rules** for `main`:

| Setting | Value |
|---------|-------|
| Require pull request before merging | ✅ (1 approval) |
| Require status checks | ✅ |
| Required checks | `Pre-commit`, `Test (Python 3.12, Django 5.1)`, `BDD / Playwright E2E`, `Docs` |
| Require branches up to date | ✅ |
| Include administrators | ✅ |
| Allow force pushes | ❌ |
| Allow deletions | ❌ |

## Option 3: GitHub Actions workflow

The workflow `.github/workflows/branch-protection.yml` attempts to apply rules on push to `main` when run with a token that has `administration: write`. It may require a personal access token or organization admin PAT stored as a secret.

## Required CI checks

After merging PR #1, these jobs must pass before `main` can be updated:

1. **Pre-commit** — ruff, formatting, file hygiene
2. **Test** — pytest unit suite (matrix)
3. **BDD / Playwright E2E** — Gherkin browser scenarios
4. **Docs** — MkDocs build
