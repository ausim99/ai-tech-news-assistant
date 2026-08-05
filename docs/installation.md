# Installation (local development)

Nothing in this project *requires* running locally - the pipeline runs in
GitHub Actions and both apps deploy to Vercel. This is for anyone who wants
to develop, test, or debug locally.

## Prerequisites

- Python 3.13 ([`.python-version`](../.python-version) pins it) + [uv](https://docs.astral.sh/uv/)
- Node.js 20+ and npm
- A GitHub personal access token if you want the backend to read real data
  (otherwise it degrades gracefully to empty responses)

## Backend + pipeline

```bash
uv sync                 # installs everything from pyproject.toml / uv.lock
cp .env.example .env    # fill in GITHUB_TOKEN if you want real GitHub API reads
```

Run the test suite:

```bash
uv run pytest -q
uv run ruff check .
uv run black --check .
```

Run the API locally:

```bash
uv run uvicorn backend.main:app --reload --port 8000
curl http://localhost:8000/api/health
```

Run the pipeline itself locally (needs `GROK_API_KEY`, `TELEGRAM_*`,
`GMAIL_*` in `.env` - this will actually call the LLM and send real
messages/emails unless you pass flags):

```bash
uv run python scripts/run_pipeline.py --dry-run          # no commit, no send
uv run python scripts/run_pipeline.py --skip-send         # commit, don't send
uv run python scripts/healthcheck.py
uv run python scripts/cleanup.py --retention-days 90
```

> **Windows note**: if `uv run <tool>` fails with *"An Application Control
> policy has blocked this file"*, that's a local Windows security policy
> blocking the `.exe` shim, not a bug. Run the module form instead:
> `uv run python -m black --check .` / `uv run python -m uvicorn ...`. If it
> also blocks `uv`'s own downloaded interpreter, point uv at a system
> Python: `uv sync --python "C:\Python31x\python.exe"`.

## Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev                        # http://localhost:3000
```

```bash
npm run lint
npm run build
```

## Running both together

Two terminals: `uv run uvicorn backend.main:app --reload --port 8000` in one,
`npm run dev` (inside `frontend/`) in the other, with
`NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in `frontend/.env.local`.

Without a real `GITHUB_TOKEN`/`GITHUB_REPO` pointing at populated data, most
dashboard pages will show their empty/error state - that's expected and is
itself a way to verify the loading/error/empty UI states work.
