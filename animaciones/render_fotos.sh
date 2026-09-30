#!/usr/bin/env bash
# PNG con fondo transparente de cada pieza en el instante FRACCION (def. 0.6) de su duración, a 8K.
# Requiere los .mp4 de render_todo.sh (para conocer la duración de cada pieza).
# Salida: ../exports/png/{oscuro,claro}/<tema>/<Pieza>.png   (fotograma completo)
# Luego: python3 postproceso_fotos.py  -> stickers recortados + hojas de conjunto
# SOLO="ClaseA ClaseB" limita a esas piezas (con FORZAR=1 para rehacerlas).
# Uso: ./render_fotos.sh [oscuro|claro|ambos] [archivo.py ...]   (JOBS=paralelo, RES=7680,4320)
set -uo pipefail
cd "$(dirname "$0")"
TEMAS=${1:-ambos}; shift || true
[ "$TEMAS" = ambos ] && TEMAS="oscuro claro"
ARCHIVOS=${*:-$(ls -1 *.py | grep -v -E '^(code_lib|_)')}
FRACCION=${FRACCION:-0.6}; JOBS=${JOBS:-4}; RES=${RES:-7680,4320}; SALIDA=../exports/png
tareas=()
for t in $TEMAS; do for f in $ARCHIVOS; do
  for c in $(grep -oE '^class\s+\w+\(Pieza\w*\)' "$f" | sed -E 's/class\s+(\w+).*/\1/' | grep -v '^Pieza'); do
    [ -n "${SOLO:-}" ] && [[ " $SOLO " != *" $c "* ]] && continue
    tareas+=("$t $f $c"); done; done; done
echo "${#tareas[@]} fotogramas a $RES"
uno() {
  t=$1; f=$2; c=$3; dest="$SALIDA/$t/${f%.py}"; mkdir -p "$dest"
  [ -f "$dest/$c.png" ] && [ -z "${FORZAR:-}" ] && { echo "= $t/$c"; return; }
  vid="../exports/${f%.py}/oscuro/$c.mp4"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$vid") || { echo "! $t/$c sin video"; return; }
  T=$(python3 -c "print(round($dur*$FRACCION,3))")
  tmp=$(mktemp -d)
  if CODE_FOTO_T=$T CODE_FOTO_SALIDA="$tmp/foto.png" CODE_TEMA=$t manim render -s -t -r $RES --media_dir "$tmp" -o "$c" "$f" "$c" >"$tmp/log" 2>&1; then
    if [ -f "$tmp/foto.png" ]; then mv "$tmp/foto.png" "$dest/$c.png"; echo "+ $t/$c (t=${T}s)"
    else echo "! $t/$c no llegó al instante $T"; fi
  else mkdir -p "$SALIDA/_errores"; cp "$tmp/log" "$SALIDA/_errores/$t-$c.log"; echo "! $t/$c FALLÓ"; fi
  rm -rf "$tmp"
}
export -f uno; export SALIDA RES FORZAR FRACCION
printf '%s\n' "${tareas[@]}" | xargs -P "$JOBS" -L1 bash -c 'uno "$@"' _
