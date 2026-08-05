# API documentation

Base URL: the backend Vercel project's URL (e.g.
`https://ai-tech-news-api.vercel.app`). All routes are prefixed `/api`.
FastAPI also serves interactive docs at `/docs` (Swagger UI) and
`/openapi.json` for free - this file is the human-readable version.

All endpoints read from the GitHub Contents API live (no cache, no
redeploy needed for fresh data) via `services/github_client.py`. A missing
file (e.g. no digest generated yet) returns `404`, not an error - the
dashboard treats that as an empty state, not a failure.

## `GET /api/health`

Liveness check. `{"status": "ok"}`, always 200.

## `GET /api/news/today`

Today's digest (`data/daily/{YYYY-MM-DD}.json`, Asia/Dhaka date). `404` if
the pipeline hasn't run yet today. Shape: see `Digest` in
`frontend/lib/types.ts` - `top_ai_news`/`top_tech_news` (arrays of
`NewsItem`), `items` (every researched item, for the Categories page),
plus the day's extras (`ai_tip`, `prompt_of_the_day`, etc).

## `GET /api/news/date/{date}`

Same shape as `/today`, for an arbitrary past `date` (`YYYY-MM-DD`).
`400` if the date isn't in that format, `404` if no digest exists for it.

## `GET /api/news/history`

Array of `{date, top_ai_count, top_tech_count}` - the lightweight index
used by the History page's table. `[]` if nothing has run yet.

## `GET /api/news/category/{category}`

Items from *today's* digest matching `category` (case-insensitive), e.g.
`/api/news/category/AI%20Research`. `404` if no digest exists for today.

## `GET /api/workflows`

Recent runs (last 5 each) for all 4 pipeline workflows, keyed by filename:

```json
{
  "pipeline.yml": [{"id": 123, "status": "completed", "conclusion": "success", "run_started_at": "...", "html_url": "..."}],
  "manual-run.yml": [...],
  "healthcheck.yml": [...],
  "cleanup.yml": [...]
}
```

## `POST /api/run`

Dispatches `manual-run.yml`. Body:

```json
{"skip_send": false, "dry_run": false}
```

Returns `{"status": "dispatched"}` immediately - dispatching is fire-and-
forget; poll `/api/workflows` or GitHub Actions to see progress.

## `POST /api/send`

Dispatches `manual-run.yml` with `resend_only: true` - re-sends today's
already-generated digest without regenerating it. No body needed.

## `GET /api/logs`

Array of `{timestamp, status, item_count}` from `data/logs.json` (most
recent 200 runs), oldest first.

## `GET /api/status`

```json
{
  "last_run": {"status": "completed", "conclusion": "success", "started_at": "...", "url": "..."},
  "analytics": {"total_runs_logged": 42, "successful_runs": 40, "success_rate": 0.952, "last_run": {...}, "updated_at": "..."}
}
```

`last_run` reflects the actual latest `pipeline.yml` GitHub Actions run;
`analytics` is computed from `data/logs.json` by `services/storage.py`
after every pipeline run.

## `GET /api/config`

Returns `data/config.json` verbatim - the source list (name, RSS URL or
`null` + status note, category) and the configured schedule strings. Powers
the Sources and Settings pages. Read-only; there's no `PUT`/`PATCH` - see
[faq.md](faq.md) for why and how to actually change it.

## Errors

Every route can return `502` if the GitHub API call itself fails (rate
limited, bad token, etc.) - body is `{"detail": "<message>"}`. CORS is
controlled by the backend's `ALLOWED_ORIGINS` env var; a browser-visible
CORS error almost always means that var doesn't match the dashboard's
actual origin (see [troubleshooting.md](troubleshooting.md)).
