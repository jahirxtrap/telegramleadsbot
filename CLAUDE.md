# CLAUDE.md — TelegramLeadsBot

Inbound Telegram bot that captures leads into Google Sheets, assisted by Cerebras.
Backend only — FastAPI + Python 3.11, deployed on Render. No frontend, no database.

The core (response envelope, config pattern, security middleware, Dockerized deploy)
was lifted from the `backstube-web` backend skeleton.

---

## Architecture

```
Telegram  ──webhook──>  POST /api/telegram/webhook  ──>  services/leads.handle_message
                                                              │
                                          ┌───────────────────┼────────────────────┐
                                          ▼                    ▼                    ▼
                                  services/cerebras      services/sheets      services/telegram
                                  (qualify + reply)      (append row via       (sendMessage back
                                                          Apps Script web app)   to the lead)
```

- **Webhook, not polling.** Telegram pushes updates; we ack `200` fast and process
  in a `BackgroundTasks` job so Telegram never retries.
- **Sheets is the only datastore.** Persistence happens through a deployed Apps
  Script web app (`apps_script/Code.gs`) — no Postgres.
- **Cerebras** runs the OpenAI-compatible Chat Completions API to qualify each
  lead and draft a reply.

## Project Structure

```
telegramleadsbot/
├── main.py                  # FastAPI app: middleware, error handlers, router auto-discovery, catch-all 404
├── run.py                   # Uvicorn launcher (honors $PORT, $WEB_CONCURRENCY)
├── pyproject.toml           # Dependencies
├── Dockerfile               # Image build
├── render.yaml              # Render web service + env var declarations
├── .env.example             # Template — copy to .env and fill for local dev
├── core/
│   ├── config.py            # Reads all config from env vars (.env auto-loaded for local dev)
│   ├── responses.py         # api_response() — THE response envelope
│   └── rate_limit.py        # slowapi limiter (configured, not globally enforced)
├── middleware/
│   ├── error_handler.py     # Routes every error through api_response()
│   └── security.py          # Security headers + 25MB request size limit
├── routers/
│   ├── health.py            # GET /api/health
│   └── telegram.py          # POST /api/telegram/webhook (secret-verified)
├── schemas/
│   ├── telegram.py          # Pydantic models for the Telegram Update subset we read
│   └── lead.py              # Lead — maps 1:1 to a spreadsheet row
├── services/
│   ├── telegram.py          # Bot API client (sendMessage, setWebhook, ...)
│   ├── sheets.py            # POST a lead to the Apps Script web app
│   ├── cerebras.py          # chat() / chat_json() over the Cerebras API
│   └── leads.py             # Orchestration: message -> qualify -> store -> reply
├── scripts/
│   └── set_webhook.py       # CLI to register/inspect/delete the Telegram webhook
└── apps_script/
    └── Code.gs              # Google Apps Script doPost — paste into the Sheet's script editor
```

## API Response Envelope

Every JSON endpoint returns `core.responses.api_response()`. Never return a raw dict.

```json
{ "success": true, "status": 200, "message": "OK", "data": { } }
```

`data` is omitted when `None`. Messages are **English**. Errors flow through the
handlers in `middleware/error_handler.py`.

## Configuration

All config lives in **environment variables** — no `ctes.py`, no templating layer.
`core/config.py` reads them via `os.environ`, auto-loading a root `.env` (python-dotenv)
for local dev. On Render the vars are injected by the platform, so `.env` is absent.

### Environment Variables

| Var | Example | Notes |
|---|---|---|
| `BACKEND_URL` | `https://telegramleadsbot.onrender.com` | Public URL; used to build the webhook URL |
| `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | From @BotFather |
| `TELEGRAM_WEBHOOK_SECRET` | random hex | Echoed by Telegram in `X-Telegram-Bot-Api-Secret-Token` |
| `SHEETS_WEBAPP_URL` | `https://script.google.com/.../exec` | Deployed Apps Script web app |
| `SHEETS_SHARED_SECRET` | random hex | Must match the Apps Script `SHARED_SECRET` property |
| `CEREBRAS_API_KEY` | `csk-...` | From https://cloud.cerebras.ai |
| `CEREBRAS_BASE_URL` | `https://api.cerebras.ai/v1` | OpenAI-compatible base |
| `CEREBRAS_MODEL` | `llama3.1-8b` | Must be a model id available on your account (GET /v1/models). Lighter models 429 far less on the free tier. |

## Local Development

```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows bash
pip install -e .
cp .env.example .env          # fill in the values
python run.py                 # http://localhost:8000 (reload on)
```

For local webhook testing, expose port 8000 (e.g. ngrok), set `BACKEND_URL` to the
public URL, then `python scripts/set_webhook.py set`.

## Deploy (Render)

1. Push the repo; create a **Docker web service** from `render.yaml` (or point Render at the Dockerfile).
2. Fill the `sync: false` env vars in the Render dashboard. `TELEGRAM_WEBHOOK_SECRET` is auto-generated.
3. After the first deploy, set `BACKEND_URL` to the service URL and redeploy.
4. Register the webhook once: `python scripts/set_webhook.py set` (locally, with the same env)
   or call Telegram's `setWebhook` with the `/api/telegram/webhook` URL and the secret token.

## Google Sheets setup

See the header comment in `apps_script/Code.gs`. In short: paste the script into the
Sheet's Apps Script editor, add `SHARED_SECRET` to Script Properties, deploy as a web
app ("Execute as: Me", "Who has access: Anyone"), and copy the `/exec` URL into
`SHEETS_WEBAPP_URL`. The column order in `Code.gs` mirrors `schemas/lead.py`.

## Conventions

1. **Routers stay thin** — validate input, call a service, return `api_response()`.
2. **Business logic lives in `services/`.** New integrations get their own module there.
3. **Everything the API emits is English** (messages, keys, paths).
4. **No secrets in the repo.** Secrets come from env vars / a gitignored `.env`; `core/config.py` only holds dev fallbacks.
5. **Imports at the top of the file**, never inline; never fully-qualified class names inline.

---

## Persistent Memory (engram)

**Engram project name**: `telegramleadsbot`. Pass `project: "telegramleadsbot"` explicitly
in every `mem_search` / `mem_save` / `mem_context` call (auto-detection is unreliable).

At session start, call `mem_context` / `mem_search` with keywords from the user's message
before responding. Save proactively (decisions, bug fixes, gotchas, conventions). Write all
engram observations in **English**; respond to the user in **Spanish**. Before closing a task,
call `mem_session_summary` (Goal, Discoveries, Accomplished, Next Steps, Relevant Files).
