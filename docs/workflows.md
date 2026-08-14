# Workflow documentation

## `.github/workflows/pipeline.yml`

**Trigger**: cron `0 0 * * *` (00:00 UTC = 06:00 Asia/Dhaka) + `workflow_dispatch`.
**Permissions**: `contents: write`.
**Concurrency**: group `news-pipeline`, queued not cancelled - so a manual
run triggered at the same moment as the scheduled run waits its turn instead
of racing on the `git push`.

Runs `.github/actions/run-pipeline` with default inputs (send + commit both
on), then posts a Telegram alert via `notify-failure` if any step failed.

## `.github/workflows/manual-run.yml`

**Trigger**: `workflow_dispatch` only, with 3 boolean inputs:

| Input | Default | Effect |
|---|---|---|
| `skip_send` | `false` | Runs the full pipeline but doesn't call Telegram/Gmail |
| `dry_run` | `false` | Doesn't write `data/*.json` or commit - pure test run |
| `resend_only` | `false` | Skips collect/research/translate/tutorial/digest entirely; re-sends today's *already-generated* digest |

Same concurrency group as `pipeline.yml`. This is what the dashboard's
"Run pipeline" and "Resend" buttons dispatch via
`POST /api/run` and `POST /api/send` (see [api.md](api.md)).

## `.github/workflows/healthcheck.yml`

**Trigger**: cron `0 * * * *` (hourly) + `workflow_dispatch`.
**Permissions**: `contents: read` (doesn't write anything).

Runs `scripts/healthcheck.py`, which checks RSS source reachability, a
`getMe` call to confirm the Telegram bot token is valid, and an SMTP login
to confirm the Gmail App Password is valid. Exits non-zero (triggering the
failure alert) only if Telegram or Gmail fails, or more than half of RSS
sources are unreachable - a single dead feed doesn't page anyone.

## `.github/workflows/cleanup.yml`

**Trigger**: cron `0 3 * * 0` (Sunday 03:00 UTC) + `workflow_dispatch`.
**Permissions**: `contents: write`.

Runs `scripts/cleanup.py --retention-days ${{ vars.DATA_RETENTION_DAYS }}`
(default 90), deleting `data/daily/*.json` files older than the cutoff.
`data/history.json`'s lightweight per-day index is kept forever - only the
full digest payloads get rotated.

## `.github/workflows/token-reminder.yml`

**Trigger**: cron `30 0 * * *` (00:30 UTC, right after the daily pipeline) +
`workflow_dispatch`.
**Permissions**: `contents: write` (persists `data/linkedin_token.json`).

Runs `scripts/notify_token_expiry.py`, which tracks the LinkedIn access
token's age (its ~60-day lifetime has no refresh token). Once the token is
inside its final 7 days it sends a Telegram + Gmail reminder **every day**
until the token is rotated - rotation is detected via a SHA-256 hash of the
token value stored in `data/linkedin_token.json`. The `commit-data` action
persists the state so the daily reminder doesn't re-fire every run.

## `.github/workflows/ci.yml`

**Trigger**: push or PR against `main`. Two independent jobs:

- **backend**: `ruff check .`, `black --check .`, `pytest -q`
- **frontend**: `npm run lint`, `npm run build`

Doesn't touch `data/` or send anything - pure validation, runs on every
push/PR regardless of the daily schedule.

## Composite actions (`.github/actions/`)

| Action | Does |
|---|---|
| `setup-env` | `astral-sh/setup-uv` + `uv sync --locked` (repo must already be checked out) |
| `run-pipeline` | `setup-env` + run `scripts/run_pipeline.py` with flags built from inputs + `commit-data` (skipped if `dry-run`) |
| `commit-data` | `git add data/`, commit with a given message, push - no-ops cleanly if nothing changed |
| `notify-failure` | Posts a Telegram message (via `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` from job-level `env:`) - used by every workflow's `if: failure()` step |

These exist because 4 workflow files would otherwise duplicate the same
checkout -> setup -> run -> commit steps; each workflow file itself is just
a trigger + a couple of `uses:` lines.
