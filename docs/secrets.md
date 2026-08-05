# GitHub Secrets & Variables Guide

Set at **Settings -> Secrets and variables -> Actions** on
[github.com/ausim99/ai-tech-news-assistant](https://github.com/ausim99/ai-tech-news-assistant).
Never commit any of these values - they're read only from `secrets.*` /
`vars.*` in the workflow YAML and from environment variables in Python.

## Secrets (Repository secrets tab)

| Secret | Where to get it |
|---|---|
| `GROK_API_KEY` | [console.x.ai](https://console.x.ai) -> API Keys -> Create key. Used by `services/llm.py` for research/translate/tutorial/digest. |
| `TELEGRAM_BOT_TOKEN` | Message [@BotFather](https://t.me/BotFather) on Telegram -> `/newbot` -> follow prompts -> it gives you a token like `123456:ABC-DEF...`. |
| `TELEGRAM_CHAT_ID` | Add your new bot to the target chat (or message it directly for a DM), then call `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `message.chat.id` from the response. For a channel, it's usually negative (e.g. `-100123456789`). |
| `GMAIL_ADDRESS` | The Gmail address the digest sends from. Needs 2-Step Verification enabled on this account. |
| `GMAIL_APP_PASSWORD` | [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) -> generate a 16-character App Password (requires 2-Step Verification to be enabled first). Not your regular Gmail password. |
| `GMAIL_TO_ADDRESS` | The recipient address the daily digest email gets sent to. |

## Variables (Repository variables tab) - optional, all have defaults

| Variable | Default | Used by |
|---|---|---|
| `DATA_RETENTION_DAYS` | `90` | `cleanup.yml` - how many days of `data/daily/*.json` to keep |

## Vercel project environment variables

These live in each **Vercel project's** own Settings -> Environment
Variables, not in GitHub. See [deployment.md](deployment.md) for the full
list per project (`GITHUB_REPO`, `GITHUB_TOKEN`, `GITHUB_BRANCH`,
`ALLOWED_ORIGINS` on the backend; `NEXT_PUBLIC_API_BASE_URL` on the
frontend).

The `GITHUB_TOKEN` used by the **Vercel backend** is a *separate* credential
from anything in GitHub Secrets above - it's a fine-grained PAT
(github.com -> Settings -> Developer settings -> Fine-grained tokens),
scoped to only this repo, with **Contents: Read-only** and
**Actions: Read and write** permissions. It's what lets the dashboard read
`data/*.json` and dispatch `manual-run.yml`.

## Masking

GitHub Actions automatically masks any string matching a registered secret's
value in logs (replaced with `***`), regardless of how it's used (env var,
inline in a `run:` step, etc.) - see `.github/actions/notify-failure` for an
example that safely interpolates `TELEGRAM_BOT_TOKEN` into a URL.
