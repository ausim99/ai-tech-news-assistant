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

**Is WhatsApp required?** No - `agents/whatsapp.py` and
`services/notify/whatsapp.py` are called unless `--skip-send`, but nothing
else depends on WhatsApp succeeding. If you don't have Meta Cloud API
credentials, leave the `WHATSAPP_*` secrets unset; the send will fail and
log a warning-level error for that channel, but Telegram delivery and
everything else still completes. To fully disable it, remove the
`await whatsapp_agent.send_digest(digest)` line in
`scripts/run_pipeline.py`.

**Can I use a different WhatsApp provider (Twilio, etc.)?**
`services/notify/whatsapp.py` implements the `NotifyProvider` protocol
(`services/notify/base.py`) - `async def send(text: str) -> None`. Swap the
module's internals for a different provider's API call and nothing else in
the codebase changes; `agents/whatsapp.py` only calls `send()`.

**Why isn't Settings/prompt-editing writable from the dashboard?** It's
read-only by design for now - making it writable means committing changes
back to `data/config.json` (or `prompts/*.py`) via the GitHub Contents API
from the backend, which is a real feature (auth, validation, conflict
handling) not yet built rather than something faked to look complete.
`GET /api/config` exists; there's no `PUT`.

**What does "API Usage" actually track?** Pipeline run reliability
(`data/analytics.json`: runs logged, success rate, last run) - not
per-provider (Grok/Telegram/WhatsApp) API call counts or cost. That metering
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
