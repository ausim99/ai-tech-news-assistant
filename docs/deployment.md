# Deployment

Two Vercel projects from one GitHub repo, plus GitHub Actions running the pipeline. No local server ever needs to run.

## 0. Repo

Already pushed: [github.com/ausim99/ai-tech-news-assistant](https://github.com/ausim99/ai-tech-news-assistant) (branch `main`).

## 1. GitHub Secrets (Settings -> Secrets and variables -> Actions -> Secrets)

| Name | Used by |
|---|---|
| `GROK_API_KEY` | pipeline (research/translate/tutorial/digest) |
| `TELEGRAM_BOT_TOKEN` | pipeline send, healthcheck |
| `TELEGRAM_CHAT_ID` | pipeline send |
| `GMAIL_ADDRESS` | pipeline send, healthcheck |
| `GMAIL_APP_PASSWORD` | pipeline send, healthcheck |
| `GMAIL_TO_ADDRESS` | pipeline send |

## 2. GitHub Variables (Settings -> Secrets and variables -> Actions -> Variables) - optional

| Name | Default if unset |
|---|---|
| `DATA_RETENTION_DAYS` | 90 |

## 3. Backend Vercel project (the API)

Vercel dashboard -> Add New Project -> import this repo.

- **Root Directory**: `.` (repo root - leave as the repo's top level)
- **Framework Preset**: Vercel auto-detects FastAPI from `pyproject.toml`'s `fastapi` dependency + `api/index.py`. Nothing to change.
- **Environment Variables**:

| Name | Value |
|---|---|
| `GITHUB_REPO` | `ausim99/ai-tech-news-assistant` |
| `GITHUB_TOKEN` | a fine-grained GitHub PAT scoped to this repo only, with **Contents: Read**, **Actions: Read and write** |
| `GITHUB_BRANCH` | `main` |
| `ALLOWED_ORIGINS` | `*` for the first deploy - tighten in step 5 once the frontend URL is known |

Deploy. Note the resulting URL, e.g. `https://ai-tech-news-api.vercel.app`. Sanity check:

```bash
curl https://ai-tech-news-api.vercel.app/api/health
# {"status":"ok"}
```

## 4. Frontend Vercel project (the dashboard)

Add New Project again, import the **same repo** a second time.

- **Root Directory**: `frontend`
- **Framework Preset**: Next.js (auto-detected)
- **Environment Variables**:

| Name | Value |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | the backend URL from step 3, e.g. `https://ai-tech-news-api.vercel.app` |

Deploy. Note this URL too, e.g. `https://ai-tech-news-dashboard.vercel.app`.

## 5. Lock down CORS

Back in the **backend** project's env vars, set:

```
ALLOWED_ORIGINS=https://ai-tech-news-dashboard.vercel.app
```

Redeploy the backend (or just trigger a redeploy from the dashboard - no code change needed, env var changes require a redeploy to take effect).

## 6. Enable the pipeline

The 5 workflows in `.github/workflows/` already run on their schedules once the repo is pushed - no extra step. To confirm end-to-end before waiting for 06:00 Asia/Dhaka:

- GitHub -> Actions -> "Manual News Run" -> Run workflow (optionally check `dry_run` for a no-commit test pass first).
- Or from the dashboard: Workflows page -> "Run pipeline".

## Troubleshooting

- **Backend 502s referencing "Not Found"**: `GITHUB_REPO` is wrong, or the PAT doesn't have access to this repo, or no digest/workflow runs exist yet (expected before the first pipeline run).
- **Dashboard shows a CORS error in the browser console**: `ALLOWED_ORIGINS` on the backend doesn't match the frontend's actual URL - check for a trailing slash or `www.` mismatch.
- **`/api/*` requests 404 on the backend**: Vercel's FastAPI auto-detection didn't route the whole app as expected. Fallback fix - add to the root `vercel.json`:
  ```json
  "rewrites": [{ "source": "/(.*)", "destination": "/api/index.py" }]
  ```
