#!/usr/bin/env bash
# Produce la familia de cursos "Algebra lineal" en modo headless, orquestada por Fable.
#
# Crontab del usuario (una sola noche, con reintentos cada 4 h por si una corrida
# muere por cuota o error; flock evita que se pisen):
#   0 1,5,9,13,17 19 8 * /home/alanrosasp/Documentos/github/codeaerospace_contenido/studio/tools/cron_algebra_lineal.sh
#
# El prompt vive en cron_algebra_lineal.prompt.md. Cada corrida lee el tablero de
# docs/plan_contenido/curso-20-algebra-lineal.md y continua por el primer paso
# no terminado; si todo esta en produccion, solo verifica e informa.
#
# Trabaja en un git worktree aparte (../codeaerospace_contenido-algebra) para no
# estorbar al cron de UI de las 09:03 que usa el checkout principal.
set -euo pipefail

REPO="/home/alanrosasp/Documentos/github/codeaerospace_contenido"
PROMPT_FILE="$REPO/studio/tools/cron_algebra_lineal.prompt.md"
LOG_DIR="$HOME/.local/state/manimstudio-algebra"
LOCK="$LOG_DIR/run.lock"

export PATH="$HOME/.local/bin:$HOME/.nvm/versions/node/v24.18.0/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y-%m-%d_%H%M).log"

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -Is) ya hay una ejecucion en curso, se omite" >>"$LOG_DIR/skipped.log"
  exit 0
fi

# El cwd es el checkout principal para que Claude cargue la memoria y la skill
# del proyecto; el prompt manda hacer todo el trabajo de archivos en el worktree.
cd "$REPO"

{
  echo "=== Algebra lineal — $(date -Is) ==="
  claude \
    --dangerously-skip-permissions \
    --model claude-fable-5 \
    --verbose \
    -p "$(cat "$PROMPT_FILE")"
  echo "=== fin — $(date -Is) ==="
} >>"$LOG" 2>&1
