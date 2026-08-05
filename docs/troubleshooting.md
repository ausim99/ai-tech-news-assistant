# Troubleshooting

## Pipeline / GitHub Actions

**A workflow run failed and I got a Telegram alert with a link.** Click the
link (it's the exact run). Most failures are one of: a Grok API error
(check `GROK_API_KEY` is set and has quota), a Telegram/Gmail send
failure (see below), or `git push` rejected because something else pushed
to `main` in between (rare, given the `news-pipeline` concurrency group
queues `pipeline.yml` and `manual-run.yml` against each other).

**"no items collected from any source, aborting"** in the logs - every
configured RSS source failed or returned nothing. Run
`scripts/healthcheck.py` manually to see which feeds are down. A handful of
sources going down doesn't stop the pipeline (see `agents/trend.py` - a
single dead feed just contributes 0 items); this message only fires if
*all* of them fail.

**A specific source never contributes items.** Check `data/config.json` -
Anthropic, Meta AI, xAI, and YouTube ship with `rss_url: null` because they
have no stable official RSS feed (verified when this was built; check
again, they may add one). Microsoft AI's official feed
(`blogs.microsoft.com/ai/feed/`) returned `410 Gone` as of 2026-08 and was
disabled the same way. If a source you'd expect to see never appears, check
its `status`/`note` fields in `data/config.json` before assuming a code bug.

**Reddit's `.rss` feed times out.** Reddit is known to throttle/block
requests from cloud and datacenter IP ranges (including GitHub Actions
runners) more aggressively than residential networks. This is expected to
be flaky; the pipeline degrades gracefully (logs a warning, continues with
0 items from that source) rather than failing the run.

**Gmail/Telegram send fails.** Telegram: check the bot token is still
valid and the bot hasn't been removed from the target chat. Gmail: App
Passwords require 2-Step Verification enabled on the account, and stop
working if the account's password or 2FA settings change - regenerate at
[myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
if `smtplib.SMTPAuthenticationError` shows up in the logs.

## Dashboard / backend

**Every page shows an error or stays empty.** Check `GET /api/health` on
the backend URL directly. If that 200s but everything else 502s, the
backend's `GITHUB_REPO`/`GITHUB_TOKEN` env vars are likely wrong or the PAT
lacks `Contents: Read` on this repo.

**CORS error in the browser console.** The backend's `ALLOWED_ORIGINS` env
var doesn't match the dashboard's actual deployed origin exactly (scheme,
host, and any trailing slash all matter). See
[deployment.md](deployment.md) step 5.

**"No digest generated for today yet" even though it's afternoon.** The
pipeline runs at 06:00 Asia/Dhaka - if it's before that in Dhaka time, this
is expected. If it's well after, check `GET /api/workflows` (or the
Workflows page) for whether `pipeline.yml` actually ran and succeeded.

**`/api/*` 404s on the backend even though the function deployed.** Vercel's
FastAPI auto-detection didn't route the whole app as a single Function.
Fallback: add an explicit rewrite to the root `vercel.json` -
`{"rewrites": [{"source": "/(.*)", "destination": "/api/index.py"}]}`.

## Local development (Windows)

**"An Application Control policy has blocked this file" running `uv run
<tool>`.** A local Windows security policy (WDAC/AppLocker) blocking a
`.exe` shim (seen with `black.exe`, `uvicorn.exe`) or occasionally uv's own
downloaded interpreter. Fixes, in order of preference:

1. Run the module form instead of the shim: `uv run python -m black
   --check .`, `uv run python -m uvicorn backend.main:app`.
2. If it's blocking uv's downloaded CPython entirely, point uv at a system-
   installed Python that the policy already trusts:
   `uv sync --python "C:\Python31x\python.exe"`.
3. If neither works, re-run `uv sync` once more - a corrupted partial
   download of the interpreter has been observed to trigger this
   transiently and clear up on a fresh download.

**`zoneinfo.ZoneInfoNotFoundError: No time zone found with key Asia/Dhaka`.**
Windows doesn't ship a tz database; the fix is already in
`pyproject.toml` (the `tzdata` dependency) - make sure you ran `uv sync`
after pulling the latest lockfile.

## Getting more detail

- Backend errors: check the Vercel project's Function logs.
- Pipeline errors: the failed GitHub Actions run's step output has the full
  Python traceback (loguru logs to stderr, which Actions captures).
- Frontend errors: browser devtools console - `app/error.tsx` catches
  render errors but logs the underlying error to the console first.
