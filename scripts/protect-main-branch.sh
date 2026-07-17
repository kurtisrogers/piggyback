#!/usr/bin/env bash
# Apply branch protection rules to main.
# Requires a GitHub token with admin:repo or repo admin permissions.
set -euo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
BRANCH="${2:-main}"

echo "Applying branch protection to ${REPO}@${BRANCH}..."

gh api \
  --method PUT \
  "repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "Pre-commit"},
      {"context": "Test (Python 3.12, Django 5.1)"},
      {"context": "BDD / Playwright E2E"},
      {"context": "Docs"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "Branch protection applied."
