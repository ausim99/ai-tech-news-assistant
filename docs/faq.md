# FAQ

**Why Bangla?** Built for a Bangladeshi audience - the digest runs on
Asia/Dhaka time (06:00 daily) and every summary/tutorial/tip is generated
in natural Bangla, not machine-literal translation (see
`prompts/translate.py`).

**How do I add a new RSS source?** Add an entry to `data/sources` in
`data/config.json`: `{"name": "...", "rss_url": "https://...", "category":
"AI"}`. No code change needed - `agents/trend.py` reads the list at runtime.
It'll be picked up on the next pipeline run.

**How do I change the schedule?** Edit the `cron:` line in the relevant
workflow file (`.github/workflows/pipeline.yml`,
`healthcheck.yml`, or `cleanup.yml`) and update the matching entry in
`data/config.json`'s `schedule` block (informational only - the workflow's
own cron is what actually controls timing). GitHub Actions cron is always
UTC.

**Is Gmail required?** Not architecturally, but note that delivery failures
aren't swallowed - `agents/telegram.py` and `agents/gmail.py` both propagate
send errors uncaught, so a missing/invalid `GMAIL_*` secret fails the whole
run (by design: silent delivery failure is worse than a visible one). To
actually make it optional, either pass `--skip-send` to skip both channels,
or wrap the `await gmail_agent.send_digest(digest)` call in
`scripts/run_pipeline.py` in a try/except if you want Gmail failures
specifically to be non-fatal.

**Can I use a different email/SMTP provider?**
`services/notify/gmail.py` isn't behind the `NotifyProvider` protocol
(`services/notify/base.py`) as-is, since email's subject+body shape doesn't
match the single-string `send(text)` contract Telegram uses - but the split
is clean: swap `services/notify/gmail.py`'s internals (SMTP host/port/auth)
for another provider and nothing in `agents/gmail.py` or
`scripts/run_pipeline.py` changes.

**Why isn't Settings/prompt-editing writable from the dashboard?** It's
read-only by design for now - making it writable means committing changes
back to `data/config.json` (or `prompts/*.py`) via the GitHub Contents API
from the backend, which is a real feature (auth, validation, conflict
handling) not yet built rather than something faked to look complete.
`GET /api/config` exists; there's no `PUT`.

**What does "API Usage" actually track?** Pipeline run reliability
(`data/analytics.json`: runs logged, success rate, last run) - not
per-provider (Grok/Telegram/Gmail) API call counts or cost. That metering
isn't implemented; the page says so rather than showing invented numbers.

**Why 96 hours for "recent," not 24?** See
[architecture.md](architecture.md#why-this-shape) - some real sources post
every few days, not daily, and the digest ranks by importance rather than
strictly by recency, so a wider window doesn't hurt relevance.

**How much does this cost to run?** GitHub Actions (public repo): free.
Vercel (both projects, this traffic level): free tier. Ongoing cost is
Grok API usage (a handful of LLM calls per collected item, daily) - scales
with how many sources/items you configure and `max_tutorial_items` in
`data/config.json`.

**Can I run this for a different language/region?** Yes - swap the
`Asia/Dhaka` timezone (`services/storage.py`, `backend/routers/news.py`,
`agents/digest.py`) and rewrite the Bangla-specific instructions in
`prompts/translate.py`/`prompts/tutorial.py`/`prompts/digest.py`. Everything
else (collection, research, delivery) is language-agnostic.
