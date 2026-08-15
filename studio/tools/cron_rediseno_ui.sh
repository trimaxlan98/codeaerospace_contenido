#!/usr/bin/env bash
# Lanza una ejecucion del rediseno de UI de ManimStudio en modo headless.
#
# Lo invoca el crontab del usuario a las 09:03 todos los dias:
#   3 9 * * * /home/alanrosasp/Documentos/github/codeaerospace_contenido/studio/tools/cron_rediseno_ui.sh
#
# El prompt vive en cron_rediseno_ui.prompt.md (al lado de este script) y el
# encargo completo en studio/docs/UX-REDISENO-BRIEF.md. Cada ejecucion continua
# por el primer sprint no terminado del tablero de studio/docs/UX-REDISENO.md;
# si el tablero esta completo, no toca nada.
#
# Detalles que importan en cron y no en una terminal:
# - cron arranca con un PATH minimo: node (nvm) y claude se anaden a mano.
# - flock evita que dos ejecuciones se pisen si una tarda mas de un dia.
# - la salida va a un log con fecha; no se rota sola, revisar de vez en cuando.
set -euo pipefail

REPO="/home/alanrosasp/Documentos/github/codeaerospace_contenido"
PROMPT_FILE="$REPO/studio/tools/cron_rediseno_ui.prompt.md"
LOG_DIR="$HOME/.local/state/manimstudio-rediseno"
LOCK="$LOG_DIR/run.lock"

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.18.0/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d_%H%M).log"

# -n: si ya hay una ejecucion viva, esta se salta en vez de encolarse.
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -Is) ya hay una ejecucion en curso, se omite" >>"$LOG_DIR/skipped.log"
  exit 0
fi

cd "$REPO"

{
  echo "=== rediseno UI ManimStudio — $(date -Is) ==="
  claude \
    --dangerously-skip-permissions \
    --model opus \
    --verbose \
    -p "$(cat "$PROMPT_FILE")"
  echo "=== fin — $(date -Is) ==="
} >>"$LOG" 2>&1
