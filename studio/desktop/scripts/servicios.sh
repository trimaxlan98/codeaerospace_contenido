#!/usr/bin/env bash
# servicios.sh — runner + backend de ManimStudio para la app de escritorio.
#
# Es studio/dev.sh sin Vite y sin --reload: la interfaz ya compilada
# (studio/frontend/dist) la sirve la propia app, que ademas hace de proxy de
# /api. Se usa igual en Linux y dentro de WSL2 (Windows), que es por lo que
# vive como script de bash y no dentro de Electron.
#
#   servicios.sh run     primer plano; Ctrl-C (o `stop`) para los dos
#   servicios.sh stop    detiene lo que dejo corriendo un `run` anterior
#   servicios.sh check   verifica requisitos sin arrancar nada
#
# Requisitos: los mismos que dev.sh (studio/backend/.env, studio/backend/venv
# e imagen `docker compose build manim`).

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO"
RUN_DIR="$REPO/.run/desktop"
PIDFILE="$RUN_DIR/servicios.pid"
API_PORT="${CODE_STUDIO_API_PORT:-3002}"

check() {
  local ok=0
  [[ -f studio/backend/.env ]] || { echo "FALTA studio/backend/.env (copiar de .env.example)"; ok=1; }
  [[ -x studio/backend/venv/bin/python ]] || { echo "FALTA studio/backend/venv"; ok=1; }
  command -v docker >/dev/null || { echo "FALTA docker"; ok=1; }
  if command -v docker >/dev/null && ! docker image inspect codeaerospace_contenido-manim >/dev/null 2>&1; then
    echo "FALTA la imagen de render (docker compose build manim)"; ok=1
  fi
  [[ $ok == 0 ]] && echo "OK"
  return $ok
}

stop() {
  [[ -f "$PIDFILE" ]] || { echo "no hay servicios registrados"; return 0; }
  local pid; pid="$(cat "$PIDFILE")"
  # El pid registrado es el del propio `run`, lider de su grupo de procesos:
  # matar el grupo se lleva runner y uvicorn aunque el padre ya no exista.
  kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  rm -f "$PIDFILE"
  echo "servicios detenidos"
}

run() {
  check >/dev/null || { check; exit 1; }
  # El hash bcrypt lleva '$': el .env usa comillas simples (ver dev.sh).
  set -a; . studio/backend/.env; set +a
  export MS_WORKSPACE="$REPO"
  mkdir -p "$(dirname "$MS_RUNNER_SOCKET")" "$RUN_DIR" render_jobs pending_primitives

  # Si quedo un `run` de una sesion anterior, se para antes: dos runners
  # pelearian por el mismo socket.
  [[ -f "$PIDFILE" ]] && stop >/dev/null
  echo $$ > "$PIDFILE"

  local pids=()
  cleanup() {
    kill "${pids[@]}" 2>/dev/null || true
    wait 2>/dev/null || true
    [[ "$(cat "$PIDFILE" 2>/dev/null)" == "$$" ]] && rm -f "$PIDFILE"
  }
  trap cleanup EXIT
  trap 'exit 0' INT TERM

  # Sustitucion de procesos y no tuberia: con `a | sed &`, $! seria el pid
  # de sed y el cleanup dejaria vivo al proceso de verdad.
  studio/backend/venv/bin/python -u studio/runner/manim_runner.py \
      > >(sed -u 's/^/[runner] /') 2>&1 &
  pids+=($!)
  (cd studio/backend && exec ../../studio/backend/venv/bin/uvicorn app.main:app \
      --host 127.0.0.1 --port "$API_PORT" --workers 1) \
      > >(sed -u 's/^/[backend] /') 2>&1 &
  pids+=($!)

  echo "[servicios] runner + backend en 127.0.0.1:$API_PORT (pid $$)"
  wait
}

case "${1:-run}" in
  run) run ;;
  stop) stop ;;
  check) check ;;
  *) echo "uso: $0 run|stop|check" >&2; exit 2 ;;
esac
