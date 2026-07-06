---
name: manimstudio
description: Use when working on ManimStudio (studio/ in this repo, prod at coderesearch.space) — rendering Manim scenes, its FastAPI backend, the Docker runner, the React frontend, the Vertex AI assistant, deploying, running tests, or E2E testing the authenticated API.
---

# ManimStudio

Private single-user web console to render Manim Community scenes at **https://coderesearch.space**.
Lives in `studio/`. Full docs: `studio/docs/README.md` and `studio/docs/AUDITORIA.md`.

## Architecture (who talks to whom)

```
navegador ─HTTPS→ nginx ├─ /      → estático  studio/frontend/dist  (React+Vite+CodeMirror)
                        └─ /api/   → 127.0.0.1:3002  backend FastAPI (usuario manimstudio, sin privilegios)
                                       cola en memoria: 1 render a la vez · SQLite WAL studio/backend/manimstudio.db
                                       Vertex AI (único módulo con salida a red)
                                       ↓ socket unix /run/manimstudio/runner.sock (0660 root:manimstudio)
                                   manim-runner (root, 4 comandos: render/cancel/thumbnail/stats/ping)
                                       ↓ docker compose run  (network_mode:none, --user manimstudio, --rm, timeout duro)
```

Two systemd services:
- **`manimstudio-backend.service`** — uvicorn `app.main:app` on `127.0.0.1:3002`, user `manimstudio`, **1 worker** (queue + SSE bus live in process memory — do NOT add workers without moving them out first).
- **`manimstudio-runner.service`** — the ONLY process with Docker access (root). Restart after editing `studio/runner/manim_runner.py`.

## Deploy

| Change | How to deploy |
|--------|---------------|
| Frontend (`studio/frontend/src`) | `cd studio/frontend && node_modules/.bin/vite build` — **that IS the deploy** (nginx serves `dist/` from disk). Verify: `curl -s https://coderesearch.space \| grep -o 'index-[a-z0-9]*\.js'`. Routes are relative `/api` — no URL baked in. |
| Backend (`studio/backend/app`) | `sudo systemctl restart manimstudio-backend.service` |
| Runner (`studio/runner`) | `sudo systemctl restart manimstudio-runner.service` (root) |

There is **no Docker container for the frontend**. The global `deploy-frontend` skill targets another project (finanzas-app) — it does NOT apply here.

## Tests

```bash
cd studio/backend && venv/bin/pytest -q      # 81 tests; the runner does NOT run in tests
```
Tests reload `app*` modules per `tmp_path` (see `conftest.py`); the AI assistant is disabled unless a test creates the key and mocks `_call_model`. Tests that read a job's `scene.py` from disk must tolerate `FileNotFoundError` when the job is already `error` (the worker deletes the job dir on failure — a real race, not a flake).

## E2E against the running API (no password needed)

The admin password only exists as a hash. Sign a session cookie with `MS_SECRET_KEY` from `/etc/manimstudio/env` (moved out of the repo tree so render containers can't read it; the systemd unit reads `EnvironmentFile` from there):

```python
from itsdangerous import TimestampSigner
cookie = TimestampSigner(SECRET, salt="manimstudio-session").sign(f"{user}:{hex}").decode()
# send as cookie `ms_session` to http://127.0.0.1:3002
```

## Non-obvious gotchas

- **`lifespan` shutdown is unreliable in prod.** With a Monitor open (SSE `/api/events`), uvicorn hangs draining on SIGTERM and systemd SIGKILLs at 90 s (`TimeoutStopUSec`) before the shutdown hook runs. So the metrics ring buffer is snapshotted **periodically** (`_metrics_loop`, ~120 s, `MS_METRICS_SNAPSHOT_INTERVAL`), not only at exit. Any other shutdown logic (`db.close`, etc.) suffers the same — don't rely on it.
- **Render containers run as uid `manimstudio`** (`--user` + `HOME=/tmp`, constant `RUN_AS_ARGS` in `manim_runner.py`). If root-owned files reappear in `render_jobs/`, that flag was reverted and the backend can't delete `media/`.
- **AI assistant is a feature-flag by file existence:** `/etc/manimstudio/gcp-key.json` (640, `root:manimstudio`, GCP project `codeaerospace-tech`). No file → app works, AI UI hidden. Only Gemini 2.5 in `us-central1`.
- **Fable 5 primitives (Admin → Experimentación) is a feature-flag by env var:** `MS_ANTHROPIC_API_KEY` in `/etc/manimstudio/env`. Without it, `/api/primitives` returns 503 and the UI shows "no configurado". Proposals stage in `pending_primitives/` (gitignored); approved ones land in `studio/content/manim_extensions/` (git).
- **The render container mounts the repo read-only** (`.:/workspace:ro`, `cap_drop: ALL`, rootfs `read_only`); only `render_jobs/<job_id>/` is mounted rw per invocation from `manim_runner.py`. If renders start failing with write errors, check the `-v job_mount` flag wasn't reverted.
- **OpenGL headless renders work** (Mesa/EGL in the image) but require `--write_to_movie` — without it the OpenGL renderer exits 0 writing no video. The UI pipeline still uses Cairo by default.
- **`JobManager.storage_usage()` is cached** (TTL 15 s), invalidated in `_finish` and `delete_job`; it does not walk the FS on every `GET /api/jobs`.
- Config is env vars with prefix `MS_` (`studio/backend/app/config.py`); required: `MS_ADMIN_USER`, `MS_ADMIN_PASSWORD_HASH`, `MS_SECRET_KEY`.

## Hard rules

- **NEVER commit** `.env`, `gcp-key.json`, `render_jobs/`, `pending_primitives/`, `manimstudio.db*`, or `metrics_history.json*` (all gitignored — keep it that way).
- One **atomic commit per sprint**; commit subject lines **sin acentos**.
