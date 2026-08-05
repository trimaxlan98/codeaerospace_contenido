#!/usr/bin/env bash
# dev.sh — levanta ManimStudio en un clon local (runner + backend + vite).
#
# El despliegue real es systemd + nginx (ver studio/deploy/). Esto es solo para
# desarrollo: los tres procesos corren como el usuario actual y el socket del
# runner vive en el repo, no en /run/manimstudio.
#
# Requisitos previos (una sola vez):
#   studio/backend/.env                      (copiar de .env.example)
#   studio/backend/venv                      virtualenv -q venv && venv/bin/pip install -r requirements.txt
#   studio/frontend/node_modules             npm ci
#   imagen de render                         docker compose build manim

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

[[ -f studio/backend/.env ]] || { echo "falta studio/backend/.env"; exit 1; }
[[ -x studio/backend/venv/bin/python ]] || { echo "falta studio/backend/venv"; exit 1; }

# El hash bcrypt lleva '$': las variables del .env deben ir entre comillas
# simples o `source` las expandiria y el login fallaria con 401.
set -a; . studio/backend/.env; set +a
export MS_WORKSPACE="$REPO"

mkdir -p "$(dirname "$MS_RUNNER_SOCKET")" render_jobs pending_primitives

pids=()
cleanup() { kill "${pids[@]}" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

studio/backend/venv/bin/python studio/runner/manim_runner.py & pids+=($!)
(cd studio/backend && exec ../../studio/backend/venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 --port 3002 --workers 1 --reload) & pids+=($!)
(cd studio/frontend && exec npx vite --host 127.0.0.1 --port 5173) & pids+=($!)

echo "ManimStudio dev  ->  http://127.0.0.1:5173   (Ctrl-C para parar los 3)"
wait
