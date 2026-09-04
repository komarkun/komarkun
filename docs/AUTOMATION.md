# Automation

The README has two blocks that a script keeps current. Everything else is
hand-written.

## What updates automatically

| Block | Markers in `README.md` | Source |
|-------|------------------------|--------|
| Engineering status | `<!-- STATUS:START -->` … `<!-- STATUS:END -->` | `scripts/status.config.json` + current UTC time |
| Recent public activity | `<!-- ACTIVITY:START -->` … `<!-- ACTIVITY:END -->` | `https://api.github.com/users/<user>/events/public` |

The script (`scripts/render_readme.py`) only ever reads **public** data. It sends
no credentials, contacts no private host, and touches nothing outside these two
marker pairs.

## How it runs

`.github/workflows/profile-status.yml`:

- **daily** at 06:17 UTC (`schedule`)
- on demand from the Actions tab (`workflow_dispatch`)
- on **push to `main`** that changes `scripts/**` or the workflow file

Steps: check out → set up Python 3.12 → `python scripts/render_readme.py` →
commit `README.md` only if it changed. The commit is made by
`github-actions[bot]` with `[skip ci]` in the message so it doesn't trigger
itself. The job needs `contents: write`, which is declared in the workflow.

## The status config

`scripts/status.config.json`:

```json
{
  "github_user": "komarkun",
  "role": "DevOps Engineer -> Platform Engineering",
  "focus": ["Infra", "Cloud", "K8s", "CI/CD", "GitOps", "Observability"],
  "building": ["bucket-explorer", "cert-watch"],
  "operating": ["K3s", "ArgoCD (GitOps)", "Prometheus + Grafana", "Cloudflare"],
  "learning": ["Kubernetes operators", "internal developer platforms"]
}
```

Edit any list, commit, and the next run (or a manual dispatch) re-renders the
panel and refreshes the `updated` timestamp. Keep entries short — the panel is
56 columns wide and long lines will wrap on mobile.

## The activity block

`render_activity()` pulls the public events feed and keeps up to six lines,
de-duplicated per `(date, repo, event type)`. It reports pushes (with a real
commit count), pull requests (opened / closed / merged), releases, tag and repo
creation, and issues opened or closed. Branch-creation noise and empty pushes
are dropped.

If the API call fails or is rate-limited, the function returns `None` and the
existing block is left exactly as it was — the README never falls back to an
error string. Unauthenticated GitHub API calls are limited to 60/hour per IP;
one run per day is far under that, so no token is required.

## Run it locally

```bash
python scripts/render_readme.py
git diff README.md
```

Standard library only — no `pip install`, Python 3.10+.

## Turn it off

Delete `.github/workflows/profile-status.yml` (or disable it in the Actions
tab). The two blocks then just keep whatever text they last had; they are
ordinary Markdown and can be edited by hand.
